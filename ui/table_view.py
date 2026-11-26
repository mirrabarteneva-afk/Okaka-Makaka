from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtCore import QSize
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from pathlib import Path
from moduls.max_value import max_value
from moduls.min_value import min_value
from moduls.sr_values import sr_value
from moduls.get_table import get_table_data, make_diverging_lut
from moduls.create_document import create_file, create_file_table
import numpy as np
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
    QCheckBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox, 
    QMessageBox
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

        self.add_btn = QPushButton('+')
        self.add_btn.setToolTip('Добавить строку в таблицу')
        self.add_btn.clicked.connect(self.add_row)
        config_layout.addWidget(self.add_btn)

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

        self.save_table_button = QPushButton('Сохранить таблицу как ...')
        self.save_table_button.clicked.connect(self.save_table)
        save_layout.addWidget(self.save_table_button)

        self.save_all = QPushButton('Сохранить всё как ...')
        self.save_all.clicked.connect(self.save_document)
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

    def draw_table(self, header, row, delim):
        self.delim = delim
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
        self.sr_menu.clear()
        self.count_menu.clear()

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

    def data_sortes(self, col):
        num_sorted = []
        all_values = []

        headers = [self.table_result.horizontalHeaderItem(i).text() for i in range(self.table_result.columnCount())]
        if col:
            column = headers.index(col)
            print(column)
            
        else:
            return
        
        for row in range(self.table_result.rowCount()):
            item = self.table_result.item(row, column)
            if item is not None:
                text = item.text()
                all_values.append(text)
                try:
                    num = float(item.text())
                    num_sorted.append(num)

                except ValueError:
                    pass   

        return num_sorted, all_values

    def sort(self, menu_column=None, column=None):
        if column is None:
            action = self.sender()
            action.blockSignals(True)
            menu = action.parent()
            name = action.text()

            num_sorted, all_values = self.data_sortes(name)

        else:
            menu = menu_column
            num_sorted, all_values = self.data_sortes(column)
            print(num_sorted, all_values)
            name = column
            
        try:
            if menu is self.max_menu or menu == 'max':
                max_num = max_value(num_sorted)
                self.result.append(f'Максимальное значение в колонке {name} - {max_num:.2f}')
            
            if menu is self.min_menu or menu == 'min':
                min_num = min_value(num_sorted)
                self.result.append(f'Минимальное значение в колонке {name} - {min_num:.2f}')   

            if menu is self.sr_menu or menu == 'sr':
                if num_sorted:
                    sr_number = sr_value(num_sorted)
                    self.result.append(f'Среднее значение в колонке {name} - {sr_number:.2f}')
                else:
                    raise ValueError

            if menu is self.count_menu or menu == 'len':
                number = len(all_values)
                self.result.append(f'Количество элементов в колонке {name} - {number}')

        except TypeError:
            if menu is self.max_menu or menu == 'max':
                max_num = max([len(a) for a in all_values])
                self.result.append(f'Максимальное значение в колонке {name} - {max_num}')

            if menu is self.min_menu or menu == 'min':
                min_num = min([len(a) for a in all_values])
                self.result.append(f'Минимальное значение в колонке {name} - {min_num}')

            if menu is self.sr_menu or menu == 'sr':
                num_sorted = [len(atribut) for atribut in all_values]
                sr_number = sum(num_sorted) / len(num_sorted)
                self.result.append(f'Среднея длина значения в колонке {name} - {sr_number}')


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

        exporter = ImageExporter(self.graph.plotItem)
        p = exporter.parameters()
        p['width'] = 1920
        p['height'] = 1080

        exporter.export(file)

    def save_table(self):
        file, filter = QFileDialog.getSaveFileName(
            self,
            'Сохранить',
            '',
            'CSV (*.csv);; SQLite базы (*.db *.sqlite);;Все файлы (*)'
        )

        path = Path(file)
        suffix = path.suffix.lower()

        if suffix == '.db' or suffix == '.sqlite':
            create_file_table(table_widget=self.table_result, path_for_document=path, format=suffix, table_name=self.delim)

        create_file_table(table_widget=self.table_result, path_for_document=path, format=suffix)

        

    def save_document(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить',
            '',
            'DOCX (*.docx)'
        )

        text = self.result.toPlainText()
        table = self.table_result

        create_file(table, path_for_document=file, text=text)

    def draw_graph(self):
        selected = []
        for i in range(self.checkboxes.count()):
            widget = self.checkboxes.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                selected.append(widget.text())
        if not selected:
            return

        headers = [self.table_result.horizontalHeaderItem(i).text()
                   for i in range(self.table_result.columnCount())]
        data = get_table_data(self.table_result, headers, selected)

        self.graph.clear()
        self.graph.setTitle(None)
        self.graph.invertY(False)
        self.graph.showAxis('right', False)
        for axis in (self.graph.getAxis('bottom'), self.graph.getAxis('left'),
                     self.graph.getAxis('right')):
            axis.setLabel(None)
            axis.setTicks(None)
        if self.graph.plotItem.legend is not None:
            self.graph.plotItem.legend.clear()

        if self.scatter.isChecked() and data.shape[1] >= 2:
            x, y = data[:, 0], data[:, 1]
            mask = ~np.isnan(x) & ~np.isnan(y)
            self.graph.plot(x[mask], y[mask], pen=None,
                            symbol='o', symbolSize=8, symbolBrush=(31, 119, 180, 180))
            self.graph.setLabel('bottom', selected[0])
            self.graph.setLabel('left', selected[1])
            self.graph.setTitle('Точечная диаграмма')

        elif self.bubble.isChecked() and data.shape[1] >= 3:
            x, y, v = data[:, 0], data[:, 1], data[:, 2]
            mask = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(v)
            x, y, v = x[mask], y[mask], v[mask]
            if x.size == 0:
                return
            v_max = max(abs(v).max(), 1e-9)
            sizes = 10 + 40 * np.abs(v) / v_max

            c_lo = np.array([30, 144, 255], dtype=float)
            c_hi = np.array([178, 34, 34], dtype=float)
            t = np.abs(v) / v_max
            rgb = (c_lo + (c_hi - c_lo) * t[:, None]).astype(int)
            brushes = [pg.mkBrush(int(r), int(g), int(b), 160) for r, g, b in rgb]

            scatter = pg.ScatterPlotItem(
                x=x, y=y, size=sizes, brush=brushes, pen=None,
                hoverable=True,
                tip=lambda s, pos: f'{selected[2]}: {s.data()[2]:.2f}',
            )
            self.graph.addItem(scatter)
            self.graph.setLabel('bottom', selected[0])
            self.graph.setLabel('left', selected[1])
            self.graph.setTitle('Пузырьковая диаграмма')

        elif self.line.isChecked():
            if self.graph.plotItem.legend is None:
                self.graph.addLegend(offset=(10, 10))
            for k, name in enumerate(selected):
                y = data[:, k]
                mask = ~np.isnan(y)
                pen = pg.mkPen(pg.intColor(k, hues=9), width=2)
                self.graph.plot(np.arange(len(y))[mask], y[mask], pen=pen,
                                symbol='o', symbolSize=5, name=name)
            self.graph.setLabel('bottom', 'Номер строки')
            self.graph.setTitle('Линейный график')

        elif self.temp_map.isChecked() and data.shape[1] >= 2:
            clean = data[~np.isnan(data).any(axis=1)]
            if clean.shape[0] < 2:
                self.graph.setTitle('Мало строк без пропусков')
                return
            corr = np.corrcoef(clean, rowvar=False)

            self.graph.invertY(True)

            img = pg.ImageItem(corr.T)
            img.setLookupTable(make_diverging_lut(256))
            img.setLevels((-1, 1))
            self.graph.addItem(img)

            ticks = [(i + 0.5, name) for i, name in enumerate(selected)]
            self.graph.getAxis('bottom').setTicks([ticks])
            self.graph.getAxis('left').setTicks([ticks])
            self.graph.showAxis('right')
            self.graph.getAxis('right').setTicks([ticks])
            self.graph.getAxis('right').setWidth(90)
            self.graph.setTitle('Корреляции (Пирсон)')

            try:
                cm = pg.colormap.get('RdBu', source='matplotlib')
                bar = pg.ColorBarItem(values=(-1, 1), colorMap=cm)
                bar.setImageItem(img, insert_in=self.graph)
            except Exception:
                pass

            for i in range(len(selected)):
                for j in range(len(selected)):
                    text = pg.TextItem(f'{corr[i, j]:.2f}', anchor=(0.5, 0.5))
                    if abs(corr[i, j]) > 0.6:
                        text.setColor('w')
                    text.setPos(j + 0.5, i + 0.5)
                    self.graph.addItem(text)


    def add_row(self):
        cols = self.table_result.columnCount()
        if cols == 0:
            QMessageBox.warning(self, 'Нет данных', 'Сначала откройте файл с таблицей')
            return

        dialog = QDialog(self)
        dialog.setWindowTitle('Новая строка')
        form = QFormLayout(dialog)
        edits = []
        for i in range(cols):
            name = self.table_result.horizontalHeaderItem(i).text()
            edit = QLineEdit()
            edit.setPlaceholderText(f'значение: {name}')
            form.addRow(name + ':', edit)
            edits.append(edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        row = self.table_result.rowCount()
        self.table_result.setRowCount(row + 1)
        for j, edit in enumerate(edits):
            self.table_result.setItem(row, j, QTableWidgetItem(edit.text()))
