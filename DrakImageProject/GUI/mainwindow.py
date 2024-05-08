from matplotlib.pyplot import imread, imsave, get_cmap
from skimage import restoration

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QProgressBar, QFileDialog, QMessageBox, QMainWindow, qApp


from Ui_mainwindow import Ui_MainWindow
from about import AboutWindow
from illuMap import IlluMapWindow
from setting import SettingWindow
from utli import ImgFigure, WorkThread


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setupUi(self)

        # -------setupUi------------
        self.originImgFigure = ImgFigure()
        self.enhancedImgFigure = ImgFigure()

        self.originImgLayout = QHBoxLayout(self.originBox)
        self.enhancedImgLayout = QHBoxLayout(self.enhancedBox)
        self.originImgLayout.addWidget(self.originImgFigure)
        self.enhancedImgLayout.addWidget(self.enhancedImgFigure)

        self.statusBar.showMessage("Please select file")
        self.progressBar = QProgressBar()
        self.statusBar.addPermanentWidget(self.progressBar)
        # self.progressBar.setVisible(False)

        self.showProgressBarAct.triggered['bool'].connect(
            self.progressBar.setVisible)

        self.showToolBarAct.setChecked(True)
        self.showProgressBarAct.setChecked(True)
        # -------setupUi------------

        self.alpha = 1
        self.gamma = 0.7
        self.weigh = 1

        self.settingWindow = SettingWindow()
        self.settingWindow.changeParameterSignal.connect(self.changeParameter)

        self._illuMapWindowFlag = False

        with open("./resource/config/.history", 'r') as fp:
            self.action1 = self.recentOpenMenu.addAction(fp.readline())
            self.action1.triggered.connect(
                lambda: self.openImage(self.action1.text()))
            self.action2 = self.recentOpenMenu.addAction(fp.readline())
            self.action2.triggered.connect(
                lambda: self.openImage(self.action2.text()))
            self.action3 = self.recentOpenMenu.addAction(fp.readline())
            self.action3.triggered.connect(
                lambda: self.openImage(self.action3.text()))

    @pyqtSlot()
    def on_openAct_triggered(self):
        # imgPath = "./data/13.jpg"
        imgPath = QFileDialog.getOpenFileName(
            self, "Please select a picture", "/", "All Files (*)")[0]
        self.openImage(imgPath)

    def openImage(self, imgPath):
        self.imgPath = imgPath.strip()
        if imgPath != '':
            self.originImg = imread(self.imgPath)
            self.originImgFigure.axes.imshow(self.originImg)
            self.originImgFigure.draw()
            self.statusBar.showMessage("current image path: " + self.imgPath)

            self.historyFile()
            self.progressBar.setValue(0)
            self.enhanceAct.setEnabled(True)
        else:
            QMessageBox.warning(self, "hint", "Please select a picture again")

    def historyFile(self):
        with open("./resource/config/.history", 'r+') as fp:
            history = fp.readlines()
            history = self.imgPath + '\n' + history[0] + history[1]
            fp.seek(0, 0)
            fp.truncate()
            fp.write(history)

    def changeParameter(self, alpha, gamma, weigh):
        self.alpha = alpha
        self.gamma = gamma
        self.weigh = weigh

    @pyqtSlot()
    def on_enhanceAct_triggered(self):
        self.progressBar.setValue(0)
        # self.progressBar.setVisible(True)
        self.workThread = WorkThread(
            self.imgPath, self.progressBar, self.alpha, self.gamma)
        self.workThread.start()
        self.workThread.finishSignal.connect(self.on_workThread_finishSignal)

    def on_workThread_finishSignal(self, T, R):
        self.T = T
        self.R = R
        self.statusBar.showMessage("current image path: " + self.imgPath + "   Image enhancement succeeded")
        # self.imgFigure.T_axes.imshow(self.T, )
        self.enhancedImgFigure.axes.imshow(self.R)

        self.progressBar.setValue(self.progressBar.maximum())
        # self.progressBar.setVisible(False)

        self.enhancedImgFigure.draw()
        self.saveAct.setEnabled(True)
        self.saveAsAct.setEnabled(True)
        self.saveIlluMapAct.setEnabled(True)
        self.denoiseAct.setEnabled(True)
        self.illuMapAct.setEnabled(True)

    @pyqtSlot()
    def on_saveAsAct_triggered(self):
        savePath = QFileDialog.getSaveFileName(
            self, "Please select a save location", "/", "BMPFormat (*.bmp);;JPGFormat  (*.jpg)")[0]
        if savePath != '':
            imsave(savePath, self.R)
            QMessageBox.about(self, "hint", "Saved successfully")
        else:
            QMessageBox.warning(self, "hint", "Please reselect the save location")

    @pyqtSlot()
    def on_saveAct_triggered(self):
        savePath = self.imgPath
        imsave(savePath, self.R)
        QMessageBox.about(self, "hint", "Saved successfully")

    @pyqtSlot()
    def on_clearAct_triggered(self):
        self.originImgFigure.axes.cla()
        self.originImgFigure.draw()
        self.enhancedImgFigure.axes.cla()
        self.enhancedImgFigure.draw()

        self.enhanceAct.setEnabled(False)
        self.saveIlluMapAct.setEnabled(False)
        self.saveAsAct.setEnabled(False)
        self.saveAct.setEnabled(False)
        self.denoiseAct.setEnabled(False)

    @pyqtSlot()
    def on_quitAct_triggered(self):
        qApp.quit()

    @pyqtSlot()
    def on_denoiseAct_triggered(self):
        self.R = restoration.denoise_tv_bregman(self.R, self.weigh)
        self.enhancedImgFigure.axes.imshow(self.R)
        self.enhancedImgFigure.draw()
        QMessageBox.about(self, "hint", "Denoising successful")

    @pyqtSlot()
    def on_saveIlluMapAct_triggered(self):
        savePath = QFileDialog.getSaveFileName(
            self, "Please select a save location", "/", "BMP (*.bmp);;JPG (*.jpg)")[0]
        if savePath != '':
            if self._illuMapWindowFlag == True:
                color = self.illuMapWindow.colorComboBox.currentText()
                color = self.illuMapWindow.colorMap[color]
                imsave(savePath, self.T, cmap=get_cmap(color))
            else:
                imsave(savePath, self.T, cmap=get_cmap('OrRd_r'))
            QMessageBox.about(self, "hint", "Saved successfully")
        else:
            QMessageBox.warning(self, "hint", "Please reselect the save location")

        # -------------其他界面-------------

    @pyqtSlot()
    def on_aboutAct_triggered(self):
        self.aboutWindow = AboutWindow()
        self.aboutWindow.show()

    @pyqtSlot()
    def on_illuMapAct_triggered(self):
        self.illuMapWindow = IlluMapWindow()
        self._illuMapWindowFlag = True
        self.illuMapWindow.saveIlluMapBtn.clicked.connect(
            self.on_saveIlluMapAct_triggered)
        self.illuMapWindow.confirmBtn.clicked.connect(
            self.on_confirmBtn_triggered)
        self.illuMapWindow.figure.axes.imshow(self.T, cmap=get_cmap('OrRd_r'))
        self.illuMapWindow.figure.draw()
        self.illuMapWindow.show()

    def on_confirmBtn_triggered(self):
        color = self.illuMapWindow.colorComboBox.currentText()
        color = self.illuMapWindow.colorMap[color]
        self.illuMapWindow.figure.axes.imshow(self.T, cmap=get_cmap(color))
        self.illuMapWindow.figure.draw()

    @pyqtSlot()
    def on_settingAct_triggered(self):
        self.settingWindow.smoothnessSlider.setValue(
            int(401 - 100 * self.alpha))
        self.settingWindow.brightnessSlider.setValue(int(100 * self.gamma))
        self.settingWindow.denosieSlider.setValue(int(100*self.weigh))
        self.settingWindow.show()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
