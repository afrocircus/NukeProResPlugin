__author__ = 'natasha'

import sys
import PySide.QtGui as QtGui
import ftrackUtils
from PySide.QtCore import Signal
import os
os.environ['USERNAME'] = 'Natasha'


class BrowserDialog(QtGui.QDialog):

    winClosed = Signal(str)

    def __init__(self, taskPath, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.taskPath = taskPath
        viewerBox = QtGui.QGroupBox('Ftrack')
        self.layout().addWidget(viewerBox)
        vLayout = QtGui.QVBoxLayout()
        viewerBox.setLayout(vLayout)

        projList = QtGui.QListWidget()
        self.createProjList(projList)
        projList.itemClicked.connect(self.projItemClicked)
        self.taskList = QtGui.QListWidget()
        self.taskList.itemClicked.connect(self.taskItemClicked)
        hLayout1 = QtGui.QHBoxLayout()
        hLayout1.addWidget(projList)
        hLayout1.addWidget(self.taskList)
        vLayout.addLayout(hLayout1)
        self.pathEdit = QtGui.QLineEdit()
        vLayout.addWidget(self.pathEdit)

        self.setButton = QtGui.QPushButton('Set')
        self.setButton.setDisabled(True)
        cancelButton = QtGui.QPushButton('Cancel')
        self.setButton.clicked.connect(self.setTaskPath)
        cancelButton.clicked.connect(self.closeWindow)
        hLayout2 = QtGui.QHBoxLayout()
        hLayout2.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        hLayout2.addWidget(self.setButton)
        hLayout2.addWidget(cancelButton)
        vLayout.addLayout(hLayout2)
        self.projPath = ''
        if not self.taskPath == '':
            self.pathEdit.setText(self.taskPath)
            self.createTaskList(self.taskPath)
            self.setProjPath()


    def createProjList(self, projList):
        projects = ftrackUtils.getAllProjectNames()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("PNG/home.png"))
        for project in projects:
            item = QtGui.QListWidgetItem(icon, project)
            projList.addItem(item)

    def projItemClicked(self, item):
        self.projPath = ''
        self.pathEdit.setText(str(item.text()))
        self.createTaskList(str(item.text()))

    def isAllTasks(self):
        for type, name in self.childList:
            if not type == 'task':
                return False
        return True

    def setProjPath(self):
        if self.isAllTasks():
            self.setButton.setDisabled(False)
            if self.projPath == '':
                tmpPath = str(self.pathEdit.text())
                self.projPath = tmpPath.split(' / ')[0]
                for p in tmpPath.split(' / ')[1:-1]:
                    self.projPath = '%s / %s' % (self.projPath, p)

    def taskItemClicked(self, item):
        pathtext = str(self.pathEdit.text())
        projPath = '%s / %s' % (pathtext, str(item.text()))
        if self.isAllTasks():
            if self.projPath == '':
                self.projPath = str(self.pathEdit.text())
            projPath = '%s / %s' % (self.projPath, str(item.text()))
            self.setButton.setDisabled(False)
        self.pathEdit.setText(projPath)
        self.createTaskList(projPath)

    def createTaskList(self, projPath):
        self.childList = ftrackUtils.getAllChildren(projPath)
        self.taskList.clear()
        for type, name in self.childList:
            if type == 'assetbuild':
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("PNG/box.png"))
                item = QtGui.QListWidgetItem(icon, name)
            elif type == 'task':
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("PNG/signup.png"))
                item = QtGui.QListWidgetItem(icon, name)
            elif type == 'sequence':
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("PNG/movie.png"))
                item = QtGui.QListWidgetItem(icon, name)
            else:
                item = QtGui.QListWidgetItem(name)
            self.taskList.addItem(item)

    def setTaskPath(self):
        self.winClosed.emit(self.getTaskPath())
        self.close()

    def getTaskPath(self):
        return str(self.pathEdit.text())

    def closeWindow(self):
        self.close()


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
        self.assetDrop.setMinimumWidth(100)
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

    def setPath(self, newPath):
        self.taskEdit.setText(newPath)
        assetList = ftrackUtils.getAllAssets(newPath)
        self.assetDrop.addItems(assetList)

    def openBrowserDialog(self):
        taskpath = str(self.taskEdit.text())
        self.gui = BrowserDialog(taskpath, parent=self)
        self.gui.show()
        self.gui.winClosed.connect(self.setPath)


def main():
    app = QtGui.QApplication(sys.argv)
    gui = MovieUploadWidget()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()