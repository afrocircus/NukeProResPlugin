__author__ = 'natasha'

import PySide.QtGui as QtGui
import ftrackUtils
from PySide.QtCore import Signal
# import os, sys
# os.environ['USERNAME'] = 'Natasha'

iconPath = 'P:\\dev\\ftrack-connect-package\\resource\\ftrack_connect_nuke\\nuke_path\\NukeProResPlugin'

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
        icon.addPixmap(QtGui.QPixmap("%s\\PNG\\home.png" % iconPath))
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
                icon.addPixmap(QtGui.QPixmap("%s\\PNG\\box.png" % iconPath))
                item = QtGui.QListWidgetItem(icon, name)
            elif type == 'task':
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("%s\\PNG\\signup.png" % iconPath))
                item = QtGui.QListWidgetItem(icon, name)
            elif type == 'sequence':
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("%s\\PNG\\movie.png" % iconPath))
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
        self.layout().addWidget(QtGui.QLabel('Link To:'))
        self.taskEdit = QtGui.QLineEdit()
        self.taskEdit.setReadOnly(True)
        self.layout().addWidget(self.taskEdit, 0, 1)
        self.taskEdit.textChanged.connect(self.updateAssetDrop)
        self.browseButton = QtGui.QPushButton('Browse')
        self.browseButton.clicked.connect(self.openBrowserDialog)
        self.layout().addWidget(self.browseButton, 0, 2)

        self.layout().addWidget(QtGui.QLabel('Assets:'), 1, 0)
        hlayout = QtGui.QHBoxLayout()
        self.assetDrop = QtGui.QComboBox()
        self.assetDrop.addItem('Select')
        self.assetDrop.addItem('new')
        self.assetDrop.setMinimumWidth(100)
        self.assetDrop.activated[str].connect(self.assetSelected)
        hlayout.addWidget(self.assetDrop)
        hlayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.layout().addLayout(hlayout, 1, 1)

        self.layout().addWidget(QtGui.QLabel('Asset Name:'), 2, 0)
        self.assetEdit = QtGui.QLineEdit()
        self.assetEdit.setDisabled(True)
        self.layout().addWidget(self.assetEdit)

        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(QtGui.QLabel('Comment'))
        vLayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        self.layout().addLayout(vLayout, 3, 0)
        self.commentBox = QtGui.QTextEdit()
        self.layout().addWidget(self.commentBox, 3, 1)

        self.layout().addWidget(QtGui.QLabel('Status:'), 4, 0)
        hlayout1 = QtGui.QHBoxLayout()
        self.statusDrop = QtGui.QComboBox()
        self.statusDrop.setMinimumWidth(100)
        hlayout1.addWidget(self.statusDrop)
        hlayout1.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.layout().addLayout(hlayout1, 4, 1)

        self.uploadButton = QtGui.QPushButton('Upload')
        self.uploadButton.setDisabled(True)
        self.layout().addWidget(self.uploadButton, 5, 0)
        self.layout().addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding), 6, 0)

    def setPath(self, newPath):
        self.taskEdit.setText(newPath)

    def assetSelected(self, assetName):
        if assetName == 'Select':
            self.assetEdit.setDisabled(True)
            self.uploadButton.setEnabled(False)
        elif assetName == 'new' :
            self.assetEdit.setDisabled(False)
            self.assetEdit.textChanged.connect(self.enableUploadButton)
        else:
            self.assetEdit.setDisabled(True)
            self.enableUploadButton()

    def updateAssetDrop(self):
        newPath = str(self.taskEdit.text())
        self.assetDrop.clear()
        self.assetDrop.addItem('Select')
        self.assetDrop.addItem('new')
        self.assetEdit.setDisabled(False)
        assetList = ftrackUtils.getAllAssets(newPath)
        self.assetDrop.addItems(assetList)
        self.updateStatusDrop(newPath)

    def updateStatusDrop(self, projectPath):
        statusList = ftrackUtils.getAllStatuses(projectPath)
        self.statusDrop.clear()
        self.statusDrop.addItems(statusList)
        currentStatus = ftrackUtils.getCurrentStatus(projectPath)
        self.statusDrop.setCurrentIndex(statusList.index(currentStatus))

    def openBrowserDialog(self):
        taskpath = str(self.taskEdit.text())
        self.gui = BrowserDialog(taskpath, parent=self)
        self.gui.show()
        self.gui.winClosed.connect(self.setPath)

    def enableUploadButton(self):
        self.uploadButton.setEnabled(True)


'''def main():
    app = QtGui.QApplication(sys.argv)
    gui = MovieUploadWidget()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()'''