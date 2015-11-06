__author__ = 'Natasha'

import ftrack
import os
import shlex
import subprocess
import json
from datetime import datetime

def getInputFilePath(shotid):
    baseDir = 'P:\\'
    shot = ftrack.Shot(id=shotid)
    shotName = '%s_%s' % (shot.getSequence().getName(), shot.getName())
    hierarchy = reversed(shot.getParents())
    imgDir = baseDir

    for p in hierarchy:
        if isinstance(p, ftrack.Project):
            pname = p.getName()
            if pname == 'willowstr':
                pname = 'ds_willowStreet'
            imgDir = os.path.join(imgDir, pname)
            imgDir = os.path.join(imgDir, 'shots')
        else:
            imgDir = os.path.join(imgDir, p.getName())

    baseDir = os.path.join(imgDir, shotName)
    inputFile = ''
    imgDir = os.path.join(baseDir, 'img\\comp')
    if os.path.exists(imgDir):
        verDirs = [d for d in os.listdir(imgDir) if os.path.isdir(os.path.join(imgDir, d))]
        if verDirs:
            imgDir = os.path.join(imgDir, verDirs[-1])
            files = [f for f in os.listdir(imgDir) if os.path.isfile(os.path.join(imgDir, f))]
            if files:
                inputFile = files[0]
    return imgDir, inputFile

def getOutputFilePath(shotid, taskid, inBaseDir):
    baseDir = 'P:\\'
    shot = ftrack.Shot(id=shotid)
    pname = shot.getProject().getName()
    if pname == 'willowstr':
        pname = 'ds_willowStreet'
    baseDir = os.path.join(baseDir, pname)
    today = datetime.today()
    day = str(today.day)
    if len(day) == 1:
        day = '0%s' % day
    datefolder = '%s-%s-%s' % (today.year, today.month, day)
    baseDir = os.path.join(baseDir, 'production\\approvals')
    baseDir = os.path.join(baseDir, datefolder)
    if not os.path.exists(baseDir):
        os.mkdir(baseDir)
    sq = shot.getSequence().getName()
    task = ftrack.Task(taskid).getName()
    ver = inBaseDir.split('\\')[-1]
    filename = '%s_%s_%s_%s.mov' % (sq, shot.getName(), task, ver)
    outputFile = os.path.join(baseDir, filename)
    outputFile = outputFile.replace(' ', '_')
    return outputFile

def getTaskPath(taskid):
    task = ftrack.Shot(id=taskid)
    taskName = task.getName()
    hierarchy = reversed(task.getParents())
    taskPath = ''
    for parent in hierarchy:
        taskPath = taskPath + parent.getName() + ' / '
    taskPath = taskPath + taskName
    return taskPath

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

def getTask(projPath):
    parent = getNode(projPath)
    taskName = projPath.split(' / ')[-1]
    task = parent
    for tasks in parent.getTasks():
        if tasks.getName() == taskName:
            task = tasks
    return task

def isTask(taskPath):
    task = getTask(taskPath)
    if task.get('objecttypename') == 'Task':
        return True
    else:
        return False

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

def getAllStatuses(projPath):
    projectName = projPath.split(' / ')[0]
    project = getProject(projectName)
    task = getTask(projPath)
    taskType = task.getType()
    statuses = project.getTaskStatuses(taskType)
    return statuses

def getStatusList(projPath):
    statuses = getAllStatuses(projPath)
    statusList = [status.getName() for status in statuses]
    return statusList

def getCurrentStatus(projPath):
    task = getTask(projPath)
    status = task.getStatus()
    return status.getName()

def convertMp4Files(inputFile, outfilemp4):
    mp4cmd = 'ffmpeg -y -i "%s" -ac 2 -b:v 2000k -c:a aac -c:v libx264 ' \
             '-pix_fmt yuv420p -g 30 -vf scale="trunc((a*oh)/2)*2:720" ' \
             '-b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 "%s"' % (inputFile, outfilemp4)
    args = shlex.split(mp4cmd)
    result = subprocess.call(args, shell=True)
    return result

def convertWebmFiles(inputFile, outfilewebm):
    webmcmd = 'ffmpeg -y -i "%s" -qscale:a 6 -g 30 -ac 2 -c:a libvorbis ' \
              '-c:v libvpx -pix_fmt yuv420p -b:v 2000k -vf scale="trunc((a*oh)/2)*2:720" ' \
              '-crf 5 -qmin 0 -qmax 50 -f webm "%s"' % (inputFile, outfilewebm)
    args = shlex.split(webmcmd)
    result = subprocess.call(args, shell=True)
    return result

def createThumbnail(inputFile, outputFile):
    cmd = 'ffmpeg -y -i "%s" -vf  "thumbnail,scale=640:360" -frames:v 1 "%s"' % (inputFile, outputFile)
    args = shlex.split(cmd)
    result = subprocess.call(args, shell=True)
    return result

def getAsset(filePath, assetName):
    parent = getNode(filePath)
    assets = parent.getAssets()
    asset = ''
    for each in assets:
        if each.getName() == assetName:
            asset = each
            break
    if asset == '':
        asset = parent.createAsset(name=assetName,
                                   assetType='ftrack_generic_type')
    return asset

def createAttachment(version, name, outfile, framein, frameout, framerate):
    baseAttachmentUrl = '/attachment/getAttachment?attachmentid={0}'
    attachment = version.createAttachment(outfile)
    component = version.createComponent(name=name, path=baseAttachmentUrl.format(attachment.getId()))
    metadata = json.dumps({
        'frameIn' : framein,
        'frameOut' : frameout,
        'frameRate' : framerate
    })
    component.setMeta(key='ftr_meta', value=metadata)


def createAndPublishVersion(filePath, comment, asset, outfilemp4, outfilewebm, thumbnail, framein, frameout, framerate):
    task = getTask(filePath)
    version = asset.createVersion(comment=comment, taskid=task.getId())
    createAttachment(version, 'ftrackreview-mp4', outfilemp4, framein, frameout, framerate)
    createAttachment(version, 'ftrackreview-webm', outfilewebm, framein, frameout, framerate)
    if os.path.exists(thumbnail):
        attachment = version.createAttachment(thumbnail)
        version.setThumbnail(attachment)
    version.publish()

def getStatus(projPath, statusName):
    statuses = getAllStatuses(projPath)
    status = ''
    for status in statuses:
        if status.getName() == statusName:
            break
    return status

def setTaskStatus(filePath, statusName):
    task = getTask(filePath)
    status = getStatus(filePath, statusName)
    task.setStatus(status)

def getProjectFromShot(id):
    shot = ftrack.Shot(id=id)
    return shot.getProject().getName()
