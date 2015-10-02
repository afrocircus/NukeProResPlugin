__author__ = 'Natasha'

import subprocess
import threading
import os
import re
import nuke
import utils
import ftrackUtils
import PySide.QtGui as QtGui
from widgets import FileBrowseWidget
from ftrackUpload import MovieUploadWidget


class NukeProResWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QGridLayout())
        self.setMinimumSize(320,200)
        tabWidget = QtGui.QTabWidget()
        frameBox = QtGui.QWidget()
        viewerBox = QtGui.QGroupBox('')
        viewerBox.setMaximumSize(500, 150)
        vLayout = QtGui.QVBoxLayout()
        basedir, infile = ftrackUtils.getInputFilePath(os.environ['FTRACK_SHOTID'])
        outfile = ftrackUtils.getOutputFilePath(basedir, infile)
        self.inputWidget = FileBrowseWidget("Input Image File  ", infile, outfile)
        self.inputWidget.addOpenFileDialogEvent()
        self.outputWidget = FileBrowseWidget("Output Movie File", outfile, outfile)
        self.outputWidget.addSaveFileDialogEvent()
        # Set trigger to change output path when input file is selected.
        self.inputWidget.fileEdit.textChanged.connect(self.outputWidget.setFilePath)
        # Set trigger to change label when input file is selected.
        self.inputWidget.fileEdit.textChanged.connect(self.setSlugLabel)
        vLayout.addWidget(self.inputWidget)
        vLayout.addWidget(self.outputWidget)
        viewerBox.setLayout(vLayout)
        frameLayout = QtGui.QVBoxLayout()
        frameBox.setLayout(frameLayout)
        frameLayout.addWidget(viewerBox)

        movieWidget = MovieUploadWidget()
        self.outputWidget.fileEdit.textChanged.connect(movieWidget.setMoviePath)

        # Setup the slug checkbox
        hLayout = QtGui.QHBoxLayout()
        self.slugBox = QtGui.QCheckBox('Slug')
        hLayout.addWidget(self.slugBox)
        self.slugBox.stateChanged.connect(self.showSlugOptions)
        vLayout.addLayout(hLayout)
        vLayout.addItem(QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

        # Setup the slug options and set visibility to False.
        self.slugFrameBox = QtGui.QGroupBox('Slug Options')
        frameLayout.addWidget(self.slugFrameBox)
        hslugLayout = QtGui.QGridLayout()
        self.slugFrameBox.setLayout(hslugLayout)
        hslugLayout.addWidget(QtGui.QLabel('Slug Label'),0,0)
        self.slugTextBox = QtGui.QLineEdit('Customize Slug Label')
        hslugLayout.addWidget(self.slugTextBox,0,1)
        self.slugFrameBox.setVisible(False)

        hLayout2 = QtGui.QHBoxLayout()
        createButton = QtGui.QPushButton('Create Movie')
        createButton.clicked.connect(self.createMovie)
        hLayout2.addWidget(createButton)
        hLayout2.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        frameLayout.addLayout(hLayout2)
        frameLayout.addItem(QtGui.QSpacerItem(10,10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))

        tabWidget.addTab(frameBox, 'ProRes Options')
        tabWidget.addTab(movieWidget, 'Ftrack Upload Options')
        self.layout().addWidget(tabWidget)

    def showSlugOptions(self, state):
        '''
        Sets visibilty of slug options based on state of slug check box.
        Resizes the window appropriately.
        :param state: State of the slug check box.
        '''
        if state == 2:
            self.slugFrameBox.setVisible(True)
        else:
            self.slugFrameBox.setVisible(False)

    def setSlugLabel(self, filename):
        '''
        Sets the slug label based on input file name.
        :param filename: Name of the input file
        '''
        inputFolder = os.path.dirname(str(filename))
        imageExt = str(filename).split('.')[-1]
        shotName, firstFrame,lastFrame, date, firstFrameStr = utils.getShotInfo(str(inputFolder), str(imageExt))
        label = 'Quarks %s %s Frame#' % (date, shotName)
        self.slugTextBox.setText(label)

    def createMovie(self):
        inputFile = self.inputWidget.getFilePath()
        outputFile = str(self.outputWidget.getFilePath())

        slugChoice = self.slugBox.checkState()
        if 'Select' in inputFile or 'Select' in outputFile or inputFile == '' or outputFile == '':
            nuke.message("Please select input and output folder")
            return

        inputFolder = os.path.dirname(str(inputFile))
        imageExt = str(inputFile).split('.')[-1]
        if not outputFile.endswith('.mov'):
            outputFile = '%s.mov' % outputFile

        shotName, firstFrame, lastFrame, date, firstFrameStr = utils.getShotInfo(inputFolder, imageExt)

        if slugChoice == 2:
            tmpDir = '%s\\tmp' % os.environ['TEMP']
            if not os.path.exists(tmpDir):
                os.mkdir(tmpDir)

            task = nuke.ProgressTask("Slug Creation")
            task.setMessage("Creating slug files")
            slugResult = utils.generateSlugImages(tmpDir, self.slugTextBox.text(), firstFrame,
                                                  lastFrame, date, firstFrameStr, task)
            if slugResult != 0:
                nuke.message("Error while creating slug images!")
                return
            slugMovResult = utils.generateSlugMovie(tmpDir, firstFrame, firstFrameStr)
            if slugMovResult != 0:
                nuke.message("Error while creating slug movie!")
                return
            finalMovCmd = utils.generateFileMovie(inputFolder, tmpDir, outputFile, firstFrame,
                                                shotName, imageExt, lastFrame, firstFrameStr)
        else:
            finalMovCmd = utils.generateFileMovieNoSlug(inputFolder, outputFile, firstFrame,
                                                  shotName, imageExt, lastFrame, firstFrameStr)
        threading.Thread( None, self.movieProgress, args=[finalMovCmd]).start()

        #if os.path.exists('%s/imageSeq' % os.environ['TEMP']):
         #   shutil.rmtree('%s/imageSeq' % os.environ['TEMP'])

    def movieProgress(self, finalMovCmd):
        task = nuke.ProgressTask("Movie Conversion")
        task.setMessage("Encoding files")
        task.setProgress(0)
        p = subprocess.Popen(finalMovCmd, shell=True, bufsize=64, stderr=subprocess.PIPE)
        self.updateProgressBar(p, task)

    def updateProgressBar(self, process, task):
        while True:
            chatter = process.stderr.read(1024)
            durationRes = re.search(r"Duration:\s(?P<duration>\S+)", chatter)
            if durationRes:
                durationList = durationRes.groupdict()['duration'][:-1].split(':')
                duration = int(durationList[0])*3600 + int(durationList[1])*60 + float(durationList[2])
            result = re.search(r'\stime=(?P<time>\S+)', chatter)
            if result:
                elapsed_time = result.groupdict()['time'].split(':')
                secs = int(elapsed_time[0])*3600 + int(elapsed_time[1])*60 + float(elapsed_time[2])
                curValue = 10
                outOf = 100-curValue
                progress = secs/duration * outOf
                QtGui.QApplication.processEvents()
                task.setProgress(int(progress+curValue))
            if not chatter:
                break
