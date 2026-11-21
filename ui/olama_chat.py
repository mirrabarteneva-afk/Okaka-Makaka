from PyQt6.QtGui import QAction
from moduls.ollama import script_run
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QMenu,
    QPushButton,
    QMenuBar,
    QLineEdit,
    QScrollArea,
)


class Olama_panel(QWidget):
    def __init__(self):
        super().__init__()
        self.status = False
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll.setWidget(self.scroll_content)

        self.chat = QVBoxLayout()
        self.input_line = QHBoxLayout()

        self.chat_window = QTextBrowser(self)
        self.chat_window.setPlaceholderText('Запустите Ollama на своём устройстве и пользуйтесь ей в этом чате!')
        self.chat_window.setOpenExternalLinks(True)
        self.chat.addWidget(self.chat_window)

        self.input_message = QLineEdit(self)
        self.input_message.setPlaceholderText('Введите текст . . .')
        self.input_message.returnPressed.connect(self.enter_pressed)
        self.input_line.addWidget(self.input_message)
        self.chat.addLayout(self.input_line)

        self.model_check = QPushButton('Выбрать модель')
        self.input_line.addWidget(self.model_check)
        self.chat.addLayout(self.input_line)

        self.menu_check = QMenu(self)
        self.menu_check.addActions([QAction('v1', self), QAction('v2', self)])
        self.model_check.setMenu(self.menu_check)

        self.setLayout(self.chat)

    def _add_message(self, text, is_user):
        if is_user:
            bubble = (
                '<td width="70%" align="right"'
                ' style="background-color:#3a3410; color:#FFD700;'
                ' padding:8px 12px; border:1px solid #B8860B;'
                ' border-radius:5px; font-size:14px;">'
                f'<b>Вы:</b> {text}</td>'
            )
            row = f'<td width="30%"></td>{bubble}'
        else:
            bubble = (
                '<td width="70%" align="left"'
                ' style="background-color:#2e2e2e; color:#FFFFFF;'
                ' padding:8px 12px; border:1px solid #4a4a4a;'
                ' border-radius:5px; font-size:14px;">'
                f'<b>Ваша модель:</b> {text}</td>'
            )
            row = f'{bubble}<td width="30%"></td>'

        self.chat_window.append(
            '<table width="100%" cellspacing="0" cellpadding="0">'
            f'<tr>{row}</tr></table>'
        )
        self.chat_window.append('<p style="margin:6px 0px;"></p>')

    def enter_pressed(self):
        text_request = self.input_message.text()
        if not text_request:
            return

        self._add_message(text_request, is_user=True)
        self.input_message.clear()

        text = script_run(text_request)
        self._add_message(text, is_user=False)
