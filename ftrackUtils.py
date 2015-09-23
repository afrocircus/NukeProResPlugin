__author__ = 'Natasha'

import ftrack
import os


def getInputFilePath(shotid):
    baseDir = 'P:\\'
    shot = ftrack.Shot(id=shotid)
    shotName = shot.getName()
    hierarchy = reversed(shot.getParents())
    imgDir = baseDir

    for p in hierarchy:
        if isinstance(p, ftrack.Project):
            imgDir = os.path.join(imgDir, p.getName())
            imgDir = os.path.join(imgDir, 'shots')
        else:
            imgDir = os.path.join(imgDir, p.getName())

    baseDir = os.path.join(imgDir, shotName)
    imgDir = os.path.join(baseDir, 'img\\comp')
    verDirs = [d for d in os.listdir(imgDir) if os.path.isdir(os.path.join(imgDir, d))]
    imgDir = os.path.join(imgDir, verDirs[-1])
    files = [f for f in os.listdir(imgDir) if os.path.isfile(os.path.join(imgDir, f))]

    inputFile = os.path.join(imgDir, files[0])
    return baseDir, inputFile

def getOutputFilePath(baseDir, inputFile):
    movDir = os.path.join(baseDir, 'mov')
    if not os.path.exists(movDir):
        os.mkdir(movDir)
    filename = inputFile.split('\\')[-1]
    outputFile = os.path.join(movDir, filename.split('.')[0])
    outputFile = '%s.mov' % outputFile
    return outputFile
