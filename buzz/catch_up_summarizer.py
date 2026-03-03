import logging
from typing import Optional

from openai import OpenAI
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable


DEFAULT_CATCH_UP_PROMPT = (
    "You are summarizing a live lecture transcript for someone who just rejoined. "
    "The transcript may be partial, noisy, or repetitive. Respond in plain text using this structure:\n"
    "Summary: <one sentence>\n"
    "Key points:\n"
    "- <3 to 6 bullets>\n"
    "Current section: <definition, derivation, example, recap, discussion, or unknown>\n"
    "Keywords:\n"
    "- <5 to 10 terms>\n"
    "Confidence: <high, medium, or low> and note uncertainty if the transcript is incomplete."
)


class CatchUpSummaryJob(QRunnable):
    class Signals(QObject):
        success = pyqtSignal(str)
        failed = pyqtSignal(str)

    def __init__(
        self,
        transcript: str,
        model: str,
        prompt: str,
        api_key: str,
        base_url: str = "",
    ):
        super().__init__()
        self.transcript = transcript
        self.model = model
        self.prompt = prompt
        self.api_key = api_key
        self.base_url = base_url
        self.signals = self.Signals()

    def run(self):
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url if self.base_url else None,
                timeout=30.0,
                max_retries=0,
            )
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.transcript},
                ],
                timeout=30.0,
            )
        except Exception as exc:
            logging.error("Catch up summary failed: %s", exc)
            self.signals.failed.emit(str(exc))
            return

        content: Optional[str] = None
        if completion and completion.choices and completion.choices[0].message:
            content = completion.choices[0].message.content

        if content:
            self.signals.success.emit(content)
            return

        logging.error("Catch up summary returned no content: %s", completion)
        self.signals.failed.emit("The model returned an empty summary.")
