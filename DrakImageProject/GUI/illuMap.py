from Ui_illuMap import Ui_Form
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from utli import ImgFigure


class IlluMapWindow(QWidget, Ui_Form):
    def __init__(self):
        super(IlluMapWindow, self).__init__()
        self.setupUi(self)

        self.figure = ImgFigure()
        self.layout = QHBoxLayout(self.groupBox)
        self.layout.addWidget(self.figure)

        self.colorMap = {'red and yellow': 'OrRd_r',
                         'grey': 'Greys',
                         'red powder': 'RdPu',
                         'blue green': 'GnBu',
                         'yellow green blue': 'YlGnBu',
                         'pink blue': 'PuBu'}


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = IlluMapWindow()
    window.show()
    sys.exit(app.exec())
