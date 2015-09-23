__author__ = 'natasha'

import sys
import PySide.QtGui as QtGui


class BrowserDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        viewerBox = QtGui.QGroupBox('Ftrack')
        self.layout().addWidget(viewerBox)



class MovieUploadWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        viewerBox = QtGui.QGroupBox('File Options')
        viewerBox.setMaximumSize(500,200)
        gLayout = QtGui.QGridLayout()
        viewerBox.setLayout(gLayout)
        self.layout().addWidget(viewerBox)
        gLayout.addWidget(QtGui.QLabel('Link To:'))
        self.taskEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.taskEdit, 0, 1)
        self.browseButton = QtGui.QPushButton('Browse')
        self.browseButton.clicked.connect(self.openBrowserDialog)
        gLayout.addWidget(self.browseButton, 0, 2)

        gLayout.addWidget(QtGui.QLabel('Assets:'), 1, 0)
        hlayout = QtGui.QHBoxLayout()
        self.assetDrop = QtGui.QComboBox()
        self.assetDrop.addItem('new')
        hlayout.addWidget(self.assetDrop)
        hlayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        gLayout.addLayout(hlayout, 1, 1)

        gLayout.addWidget(QtGui.QLabel('Asset Name:'), 2, 0)
        self.assetEdit = QtGui.QLineEdit()
        gLayout.addWidget(self.assetEdit)

        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(QtGui.QLabel('Comment'))
        vLayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        gLayout.addLayout(vLayout, 3, 0)
        self.commentBox = QtGui.QTextEdit()
        gLayout.addWidget(self.commentBox, 3, 1)


    def openBrowserDialog(self):
        gui = BrowserDialog(parent=self)
        gui.show()


def main():
    app = QtGui.QApplication(sys.argv)
    gui = MovieUploadWidget()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()