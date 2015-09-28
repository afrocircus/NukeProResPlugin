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

def getAllProjectNames():
    projects = ftrack.getProjects()
    projList = [proj.getName() for proj in projects]
    projList.sort()
    return projList

def getProject(projName):
    for project in ftrack.getProjects():
        if project.getName() == projName:
            break;
    return project

def getNode(nodePath):
    nodes = nodePath.split(' / ')
    parent = getProject(nodes[0])
    nodes = nodes[1:]
    if nodes:
        for node in nodes:
            for child in parent.getChildren():
                if child.getName() == node:
                    parent = child
                    break
    return parent

def getAllChildren(projPath):
    parent = getNode(projPath)
    children = parent.getChildren()
    complete = False
    if not children:
        children = parent.getTasks()
    childList = []
    for child in children:
        if child.getName() == 'Asset builds' or child.get('objecttypename') == 'Asset Build':
            childList.append(('assetbuild', child.getName()))
        elif child.get('objecttypename') == 'Episode':
            childList.append(('episode', child.getName()))
        elif child.get('objecttypename') == 'Sequence':
            childList.append(('sequence', child.getName()))
        elif child.get('objecttypename') == 'Shot':
            childList.append(('shot', child.getName()))
        else:
            childList.append(('task', child.getName()))
    return childList

def getAllAssets(projPath):
    parent = getNode(projPath)
    assets = parent.getAssets()
    assetList = [asset.getName() for asset in assets]
    return assetList
