from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt
from pathlib import Path
from moduls.open_csv import get_headers
from moduls.open_db import get_headers_column
from moduls.table_create_csv import csv_table_create
from moduls.table_create_db import db_table_create

from ui.table_view import Main_panel
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QCheckBox,
    QComboBox,
    QPushButton,
    QLabel,
    QGridLayout,
    QFileDialog,
    QLineEdit,
)


class Leftpanel(QWidget):
    def __init__(self, assets_path, data_view: Main_panel):
        super().__init__()
        self.assets_path = assets_path
        self.data_view = data_view
        self.status = True
        self.conditions = []
        self.headers = []
        self.rows = []
        self.checkboxes = {}
        self.count = 1
        self.path = ''
        self.img_path = self.assets_path / "assets" / "monkey_logo.jpeg"
        self.img_clear = self.assets_path / "assets" / "clear.png"
        self.initUI()

    def initUI(self):
        self.scroll  = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.scroll_content = QWidget()
        
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(10)
        self.grid.setContentsMargins(5, 5, 5, 5)

        self.scroll.setWidget(self.scroll_content)

        main_layout = QVBoxLayout()

        self.condition_data = QVBoxLayout()
        sort_layout = QHBoxLayout()
        sort_layout_default = QVBoxLayout() 
        request_layout = QHBoxLayout()
        title_layout = QHBoxLayout()
        open_layout = QHBoxLayout()
        presets_layout_1 = QVBoxLayout()
        presets_layout_2 = QHBoxLayout()
        presets_layout_3 = QHBoxLayout()
        presets_layout_4 = QHBoxLayout()

        pixmap = QPixmap(str(self.img_path))

        size = 64
        pixmap = pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.logo = QLabel()
        self.logo.setPixmap(pixmap)
        self.logo.setFixedSize(size, size)
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setObjectName("logo_avatar")
        title_layout.addWidget(self.logo)

        self.title = QLabel("Окака Макака", self)
        self.title.setObjectName("title")
        title_layout.addWidget(self.title)
        
        request_layout.addLayout(title_layout)

        self.open_file = QPushButton('Открыть файл', self)
        self.open_file.clicked.connect(self.open_file_diolog)
        open_layout.addWidget(self.open_file)

        self.clear_button = QPushButton()
        self.clear_button.setFixedSize(40, 40)
        self.clear_button.setObjectName('clear_btn')
        self.clear_button.setIcon(QIcon(str(self.img_clear)))
        self.clear_button.setIconSize(QSize(24, 24))
        self.clear_button.clicked.connect(self.clear)
        
        self.get_delim = QLineEdit(self)
        self.get_delim.setPlaceholderText('Укажите разделитель или название таблицы...')
        open_layout.addWidget(self.get_delim)
        open_layout.addWidget(self.clear_button)

        self.errors_message = QLabel(self)

        self.text_parametrs = QLabel('Сортировка', self)
        presets_layout_1.addWidget(self.text_parametrs)

        self.columns_change_2 = QComboBox(self)
        self.columns_change_2.addItem('Нет')
        self.columns_change_2.setToolTip('Колонка по которой будем сортировать')
        sort_layout.addWidget(self.columns_change_2)

        self.change_operations = QComboBox(self)
        self.change_operations.setToolTip('Операции выбора')
        self.change_operations.addItems(['=', '<', '>', '<=', '>=', 'Диапазон вкл', 'Диапазон не вкл', 'В тексте', 'Пусто', 'Не пусто'])
        sort_layout.addWidget(self.change_operations)

        self.input_parametr = QLineEdit(self)
        self.input_parametr.setPlaceholderText('Введите значения сортировки ...')
        sort_layout.addWidget(self.input_parametr)

        self.add_condition = QPushButton('+', self)
        self.add_condition.clicked.connect(self.add_condition_func)
        sort_layout.addWidget(self.add_condition)

        self.button_start = QPushButton('Вывести', self)
        self.button_start.clicked.connect(self.start)

        sort_layout_default.addLayout(sort_layout)
        sort_layout_default.addLayout(self.condition_data)
        presets_layout_1.addLayout(presets_layout_2)
        presets_layout_1.addLayout(sort_layout_default)
        presets_layout_1.addLayout(presets_layout_3)
        presets_layout_1.addLayout(presets_layout_4)
        presets_layout_1.addWidget(self.button_start)
        main_layout.addLayout(request_layout)
        main_layout.addLayout(open_layout)
        main_layout.addWidget(self.scroll)
        main_layout.addWidget(self.errors_message)
        main_layout.addLayout(presets_layout_1)
        self.setLayout(main_layout)

    def open_file_diolog(self):
        table_name = self.get_delim.text()
        self.errors_message.setText('')
        if not table_name:
            self.errors_message.setText('Вы должны указать разделитель или имя таблицы!')
            return
        try:
            file, _ = QFileDialog.getOpenFileName(
                self,
                'Выберете файл c данными для Окаки Макаки',
                '',
                'CSV файлы (*.csv);;SQLite базы (*.db *.sqlite);;Все файлы (*)'
            )

            if file:
                path = Path(file)
                self.path = path
                suffix = path.suffix.lower()

                if suffix == '.csv':
                    delim = self.get_delim.text() 
                    headers = get_headers(path, delim)
                    self.columns_change_2.addItems(headers)
                    self.render_checkboxes(headers)
                    self.add_condition_func(headers)

                elif suffix == '.db':
                    table_name = self.get_delim.text()
                    if not table_name:
                        self.errors_message.setText('Вы не указали таблицу!')
                        return

                    headers = get_headers_column(path, table_name)                    
                    self.columns_change_2.addItems(headers)
                    self.render_checkboxes(headers)
                    self.add_condition_func(headers)
            return None 
        except TypeError:
            return


    def render_checkboxes(self, headers):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not headers:
            self.errors_message.setText('Ничего не найдено! Окака Макака на хочет работать!')
            if hasattr(self, 'checkboxes'):
                self.checkboxes.clear()
            return

        if not hasattr(self, 'checkboxes'):
            self.checkboxes = {}
        else:
            self.checkboxes.clear()

        for i, col_name in enumerate(headers):
            self.headers.append(col_name)
            cb = QCheckBox(col_name)
            cb.setObjectName(f'cb_{col_name}')

            self.checkboxes[str(col_name)] = cb
            self.grid.addWidget(cb)
            
        self.data_view.draw_checboxes(self.headers)
        if not self.checkboxes:
            self.errors_message('Запрос был некорректен!')


    def add_condition_func(self):
            headers = [self.columns_change_2.itemText(i) for i in range(self.columns_change_2.count())]
            row_widget = QWidget()
            row_layout = QHBoxLayout()

            logic_combo = QComboBox()
            logic_combo.addItems(['AND', 'OR'])
            row_layout.addWidget(logic_combo)

            column_combo = QComboBox()
            column_combo.addItems(headers)
            row_layout.addWidget(column_combo)

            operator_combo = QComboBox()
            operator_combo.addItems(['=', '<', '>', '<=', '>=', 'Диапазон', 'В', 'В тексте', 'Пусто', 'Не пусто'])
            row_layout.addWidget(operator_combo)

            input_edit = QLineEdit()
            row_layout.addWidget(input_edit)

            button_delete = QPushButton('-', self)

            controls = (logic_combo, column_combo, operator_combo, input_edit)

            def row_clear():
                if controls in self.rows:
                    self.rows.remove(controls)

                while row_layout.count():
                    item = row_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

                self.condition_data.removeWidget(row_widget)
                row_widget.deleteLater()            

            button_delete.clicked.connect(row_clear)
            row_layout.addWidget(button_delete)

            row_widget.setLayout(row_layout)
            self.condition_data.addWidget(row_widget)
            self.rows.append(controls)

    def clear(self):
        self.get_delim.setText('')
        self.errors_message.setText('')
        self.input_parametr.setText('')
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.columns_change_2.clear()
        self.columns_change_2.addItem('Нет')
        
        while self.condition_data.count():
            item = self.condition_data.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def start(self):
        conditions =[]
        check = [name for name, active in self.checkboxes.items() if active.isChecked()]
        delim = self.get_delim.text()
        path = self.path

        if self.columns_change_2.currentText() != 'Нет':
            conditions = [
                (self.columns_change_2.currentText(),
                self.change_operations.currentText(),
                self.input_parametr.text())
            ]

        for logic_combo, column_combo, operator_combo, input_edit in self.rows:
            conditions.append(logic_combo.currentText())
            conditions.append(
                (column_combo.currentText(), operator_combo.currentText(), input_edit.text())
            )

        if path.suffix.lower() == '.csv':
            try:
                self.errors_message.clear()
                headers, row = csv_table_create(check, path, delim, conditions)
                self.data_view.draw_table(headers, row)
                    
            except ValueError:
                self.errors_message.setText('Проблемы с типизацией!')
                return

            except TypeError:
                self.errors_message.setText('Проверьте, что вы корректно ввели условие')
                return

        if path.suffix.lower() == '.db':
            headers, row = db_table_create(check, path, delim)
            self.data_view.draw_table(headers, row)


    def get_headers(self):
        delim = self.get_delim.text()
        return (self.headers, self.path, delim)