from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import QSize
import pyqtgraph as pg

from moduls.max_value import max_value
from moduls.min_value import min_value
from moduls.sr_values import sr_valye

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QMenu,
    QPushButton,
    QRadioButton,
    QLabel,
    QFileDialog,
    QCheckBox
)


class Main_panel(QWidget):
    def __init__(self, assets_path):
        super().__init__()
        self.max_actions = []
        self.image_clear = assets_path / 'assets' / 'clear.png'
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        config_layout = QHBoxLayout()
        save_layout = QHBoxLayout()
        self.tabs = QTabWidget()

        self.tab_1 = QWidget()
        main_layout_table = QVBoxLayout(self.tab_1)

        self.table_result = QTableWidget(self)
        main_layout_table.addWidget(self.table_result)

        self.max_btn = QPushButton('Вывести максимальное по ...')
        self.max_menu = QMenu(self)
        self.max_btn.setMenu(self.max_menu)
        config_layout.addWidget(self.max_btn)

        self.min_btn = QPushButton('Вывести минимальное по ...')
        self.min_menu = QMenu(self)
        self.min_btn.setMenu(self.min_menu)
        config_layout.addWidget(self.min_btn)

        self.sr_btn = QPushButton('Вывести среднее по ...')
        self.sr_menu = QMenu(self)
        self.sr_btn.setMenu(self.sr_menu)
        config_layout.addWidget(self.sr_btn)

        self.count_btn = QPushButton('Вывести количество ...')
        self.count_menu = QMenu(self)
        self.count_btn.setMenu(self.count_menu)
        config_layout.addWidget(self.count_btn)

        self.save_table = QPushButton('Сохранить таблицу как ...')
        save_layout.addWidget(self.save_table)

        self.save_all = QPushButton('Сохранить всё как ...')
        save_layout.addWidget(self.save_all)
    
        self.clear_button = QPushButton()
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setIcon(QIcon(str(self.image_clear)))
        self.clear_button.setIconSize(QSize(32, 32))
        self.clear_button.clicked.connect(self.result_clear)
        config_layout.addWidget(self.clear_button)
        main_layout_table.addLayout(config_layout)
        main_layout_table.addLayout(save_layout)

        self.result = QTextBrowser(self)
        self.result.setPlaceholderText('Пока что пусто ...')
        main_layout_table.addWidget(self.result)

        self.tab_2 = QWidget()
        main_layout_graphic = QVBoxLayout()
        setting_graph = QHBoxLayout()
        self.checkboxes = QHBoxLayout()
        buttons = QHBoxLayout()

        self.graph = pg.PlotWidget(self)
        self.graph.showGrid(x=True, y=True)
        main_layout_graphic.addWidget(self.graph)
        
        self.graph_type = QLabel('Настройки графика', self)
        main_layout_graphic.addWidget(self.graph_type)
        
        self.scatter = QRadioButton('Точечная диаграмма', self)
        setting_graph.addWidget(self.scatter)

        self.bubble = QRadioButton('Пузырьковая диаграмма', self)
        setting_graph.addWidget(self.bubble)

        self.line = QRadioButton('Линейный график', self)
        setting_graph.addWidget(self.line)

        self.temp_map = QRadioButton('Тепловая карта корреляций', self)
        setting_graph.addWidget(self.temp_map)

        self.draw_graph_button = QPushButton('Нарисовать', self)
        self.draw_graph_button.clicked.connect(self.draw_graph)
        buttons.addWidget(self.draw_graph_button)

        self.save_button = QPushButton('Сохранить как ...')
        self.save_button.clicked.connect(self.save)        
        buttons.addWidget(self.save_button)

        main_layout_graphic.addLayout(setting_graph)
        main_layout_graphic.addLayout(self.checkboxes)
        main_layout_graphic.addLayout(buttons)
        self.tab_2.setLayout(main_layout_graphic)

        self.tabs.addTab(self.tab_1, 'Данные')
        self.tabs.addTab(self.tab_2, 'График')
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def draw_table(self, header, row):
        self.table_result.clearContents()
        self.result.clear()
        self.table_result.setColumnCount(len(header))
        self.table_result.setHorizontalHeaderLabels(header)
        self.table_result.setRowCount(len(row))
        for i, elem in enumerate(row):
            for j, val in enumerate(elem):
                self.table_result.setItem(i, j, QTableWidgetItem(str(val)))
                
        self.filters_table(header)

    def draw_checboxes(self, checboxes):
        for ch in checboxes:
            ch = QCheckBox(ch, self)
            self.checkboxes.addWidget(ch)

    def filters_table(self, header):
        self.max_menu.clear()
        self.min_menu.clear()

        for ch in header:
            ch = QAction(ch, self.max_menu)
            ch.setCheckable(True)
            ch.setChecked(False)
            ch.toggled.connect(self.sort)
            self.max_menu.addAction(ch)
            self.max_actions.append(ch)

        for ch in header:
            ch = QAction(ch, self.min_menu)
            ch.setCheckable(True)
            ch.setChecked(False)
            ch.toggled.connect(self.sort)           
            self.min_menu.addAction(ch)

        for ch in header:
            ch = QAction(ch, self.sr_menu)
            ch.setCheckable(True)
            ch.setChecked(False)
            ch.toggled.connect(self.sort)
            self.sr_menu.addAction(ch)

        for ch in header:
            ch = QAction(ch, self.count_menu)
            ch.setCheckable(True)
            ch.setChecked(False)
            ch.toggled.connect(self.sort)
            self.count_menu.addAction(ch)

    def sort(self):
        action = self.sender()
        action.blockSignals(True)
        menu = action.parent()
        name = action.text()
        num_sorted = []
        all_values = []

        headers = [self.table_result.horizontalHeaderItem(i).text() for i in range(self.table_result.columnCount())]

        if headers:
            col = headers.index(name)

            for row in range(self.table_result.rowCount()):
                item = self.table_result.item(row, col)
                if item is not None:
                    text = item.text()
                    all_values.append(text)
                    try:
                        num = float(item.text())
                        num_sorted.append(num)

                    except ValueError:
                        pass       
            try:
                if menu is self.max_menu:
                    max_num = max_value(num_sorted)
                    self.result.append(f'Максимальное значение в колонке {name} - {max_num:.2f}')
            
                if menu is self.min_menu:
                    min_num = min_value(num_sorted)
                    self.result.append(f'Минимальное значение в колонке {name} - {min_num:.2f}')   

                if menu is self.sr_menu:
                    if num_sorted:
                        sr_number = sr_valye(num_sorted)
                        self.result.append(f'Среднее значение в колонке {name} - {sr_number:.2f}')
                    else:
                        raise ValueError

                if menu is self.count_menu:
                    number = len(all_values)
                    self.result.append(f'Количество элементов в колонке {name} - {number}')

            except ValueError:
                if menu is self.max_menu:
                    max_num = max([len(a) for a in all_values])
                    self.result.append(f'Максимальное значение в колонке {name} - {max_num}')

                if menu is self.min_menu:
                    min_num = min([len(a) for a in all_values])
                    self.result.append(f'Минимальное значение в колонке {name} - {min_num}')

                if menu is self.sr_menu:
                    num_sorted = [len(atribut) for atribut in all_values]
                    sr_number = sum(num_sorted) / len(num_sorted)
                    self.result.append(f'Среднея длина значения в колонке {name} - {sr_number:.2f}')
        else:
            return

    def result_clear(self):
        self.result.clear()


    def save(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранение',
            '',
            'PNG изображения (*.png);;JPEG (*.jpeg *.jpg);;Все файлы (*)'
        )

        if not file:
            return

        exporter = pg.exporters.ImageExporter(self.graph.plotItem)
        p = exporter.parameters()
        p['width'] = 1920
        p['height'] = 1080

        exporter.export(file)

    def save_table(self):
        file, filter = QFileDialog.getSaveFileName(
            self,
            'Сохранить',
            '',
            'CSV (*.csv);;TSV (*.tsv);;PARQUET (*parquet);;FEATHER (*feather);;XLSX (*xlsx)'
        )


    def save_all(self):
        pass

    def draw_graph(self):
        header = [name for name, ch in self.checkboxes if ch.isChecked()]
        print(header)