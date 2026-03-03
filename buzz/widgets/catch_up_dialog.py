from typing import Optional

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from buzz.locale import _


class CatchUpDialog(QDialog):
    def __init__(self, summary_text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.summary_text = summary_text.strip()
        self.setWindowTitle(_("Catch up"))
        self.setMinimumSize(520, 420)

        lines = [line.strip() for line in self.summary_text.splitlines() if line.strip()]
        headline = lines[0] if lines else _("No summary available.")

        layout = QVBoxLayout(self)

        self.headline_label = QLabel(headline, self)
        font = self.headline_label.font()
        font.setPointSize(max(font.pointSize() + 2, 12))
        font.setBold(True)
        self.headline_label.setFont(font)
        self.headline_label.setWordWrap(True)
        layout.addWidget(self.headline_label)

        self.summary_text_box = QPlainTextEdit(self)
        self.summary_text_box.setReadOnly(True)
        self.summary_text_box.setPlainText(self.summary_text)
        layout.addWidget(self.summary_text_box)

        actions_layout = QHBoxLayout()
        self.copy_button = QPushButton(_("Copy"), self)
        self.copy_button.clicked.connect(self.on_copy_clicked)
        actions_layout.addWidget(self.copy_button)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        button_box.rejected.connect(self.reject)
        actions_layout.addWidget(button_box)
        layout.addLayout(actions_layout)

    def on_copy_clicked(self):
        app = QApplication.instance()
        if app is None:
            QMessageBox.warning(self, "", _("Clipboard is unavailable right now."))
            return

        clipboard = app.clipboard()
        if clipboard is None:
            QMessageBox.warning(self, "", _("Clipboard is unavailable right now."))
            return

        clipboard.setText(self.summary_text)
        self.copy_button.setText(_("Copied!"))
