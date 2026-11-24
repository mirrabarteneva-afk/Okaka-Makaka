from PyQt6.QtGui import QAction
from itertools import chain, zip_longest
from moduls.ollama import script_run
from moduls.table_create_csv import csv_table_create
from ui.table_view import Main_panel
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QMenu,
    QPushButton,
    QWidgetAction,
    QToolBar,
    QLineEdit,
    QScrollArea,
)


class Olama_panel(QWidget):
    def __init__(self, left_panel, data_view: Main_panel):
        super().__init__()
        self.status = False
        self.left_panel = left_panel
        self.data_view = data_view
        self.model = None,
        self.url = None,
        self.initUI()

    def initUI(self):
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll.setWidget(self.scroll_content)

        self.chat = QVBoxLayout()
        self.input_line = QHBoxLayout()
        self.model_layout = QVBoxLayout()

        self.chat_window = QTextBrowser(self)
        self.chat_window.setPlaceholderText('Запустите Ollama на своём устройстве и пользуйтесь ей в этом чате!')
        self.chat_window.setOpenExternalLinks(True)
        self.chat.addWidget(self.chat_window)

        self.input_message = QLineEdit(self)
        self.input_message.setPlaceholderText('Введите текст . . .')
        self.input_message.returnPressed.connect(self.enter_pressed)
        self.input_line.addWidget(self.input_message)
        self.chat.addLayout(self.input_line)

        self.model_settings = QPushButton('Выбрать модель')

        def open_menu():
            menu = QMenu(self)

            model_version = QLineEdit()
            model_version.setPlaceholderText('Ваша моделью. По умолчанию qwen2.5:3b (Рекомендовано).')
            action_version = QWidgetAction(menu)
            action_version.setDefaultWidget(model_version)
            menu.addAction(action_version)        
            model_version.returnPressed.connect(menu.close)

            model_url = QLineEdit()
            model_url.setPlaceholderText('Url вашей модели. По умолчанию (http://localhost:11434/api/generate).')
            action_url = QWidgetAction(menu)
            action_url.setDefaultWidget(model_url)
            menu.addAction(action_url)        
            model_url.returnPressed.connect(menu.close)

            menu.addSeparator()

            def collect():
                model = model_version.text()
                url = model_url.text()

                return model, url

            ok_action = menu.addAction('Ok')
            ok_action.triggered.connect(collect)
            
            menu.exec(self.model_settings.mapToGlobal(self.model_settings.rect().bottomLeft()))

            self.model, self.url = collect()

            
        self.model_settings.clicked.connect(open_menu)
        self.input_line.addWidget(self.model_settings)
        self.chat.addLayout(self.input_line)


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
        self.columns = self.left_panel.get_headers()
        print(self.url)

        self.response = script_run(text_request, data_columns=self.columns[0], url=self.url, model=self.model)
        self._add_message(self.response, is_user=False)

        parse = []

        response = self.response.strip('[').strip(']')
        response = tuple(response.split(', '))

        if len(response) > 1:
            if 'AND' in response or 'OR' in response:
                cond = [x for x in response if x == 'AND' or x == 'OR']
                values = [x for x in response if x != 'AND' and x != 'OR']

                it = iter(values)
                values = list(zip(it, it, it))

                parse = [x for x in chain.from_iterable(zip_longest(cond, values)) if x is not None]
                
            else:
                parse = [response]

        else:
            response = tuple(self.response.split(': '))
            print(response)
            self.data_view.sort(menu_column=response[0], column=response[1])

        if parse:
            headers, row  = csv_table_create(columns=self.columns[0], path=self.columns[1], delim=self.columns[2], conditions=parse)
            self.data_view.draw_table(headers, row)

        #action_ok = self.menu.addAction('Ok')
        #action_ok.triggered.connect(self.)

        #btn = self.sender()
        #rect = self.toolBar().connect(self.c)
        #self.menu.exec(self.mapToGlobal())