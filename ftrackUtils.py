__author__ = 'Natasha'

import ftrack
import ftrack_api
import os
import shlex
import subprocess
import json
from datetime import datetime


session = ftrack_api.Session(
    server_url='http://192.168.0.105',
    api_key='36d3599c-86bf-11e5-954c-0015170f7389',
    api_user='Natasha'
)


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
    item = session.query('Task where id is %s' % taskid).one()
    taskPath = ''
    while True:
        taskPath = item['name'] + taskPath
        item = item['parent']
        if not item:
            break
        taskPath = ' / ' + taskPath
    return taskPath


def getAllProjectNames():
    projects = session.query('Project').all()
    projList = [proj['name'] for proj in projects]
    projList.sort()
    return projList


def getProject(projName):
    project = session.query('Project where name is "%s"' % projName).one()
    return project


def getNode(nodePath):
    nodes = nodePath.split(' / ')
    parent = getProject(nodes[0])
    nodes = nodes[1:]
    if nodes:
        for node in nodes:
            for child in parent['children']:
                if child['name'] == node:
                    parent = child
                    break
    return parent


def getTask(projPath):
    parent = getNode(projPath)
    taskName = projPath.split(' / ')[-1]
    task = session.query('Task where parent.id is %s and name is %s' % (parent['parent']['id'], taskName)).one()
    return task


def isTask(taskPath):
    task = getTask(taskPath)
    if task['object_type']['name'] == 'Task':
        return True
    else:
        return False


def getAllChildren(projPath):
    parent = getNode(projPath)
    children = parent['children']
    childList = []
    for child in children:
        if child['name'] == 'Asset builds' or child['object_type']['name'] == 'Asset Build':
            childList.append(('assetbuild', child['name']))
        elif child['object_type']['name'] == 'Episode':
            childList.append(('episode', child['name']))
        elif child['object_type']['name'] == 'Sequence':
            childList.append(('sequence', child['name']))
        elif child['object_type']['name'] == 'Shot':
            childList.append(('shot', child['name']))
        else:
            childList.append(('task', child['name']))
    return childList


def getAllAssets(projPath):
    parent = getNode(projPath)
    assets = session.query('Asset where parent.name is "%s"' % parent['parent']['name'])
    assetList = [asset['name'] for asset in assets]
    return assetList


def getAllStatuses(projPath):
    projectName = projPath.split(' / ')[0]
    project = getProject(projectName)
    task = getTask(projPath)
    projectSchema = project['project_schema']
    statuses = projectSchema.get_statuses('Task', task['type']['id'])
    return statuses


def getStatusList(projPath):
    statuses = getAllStatuses(projPath)
    statusList = [status['name'] for status in statuses]
    return statusList


def getCurrentStatus(projPath):
    task = getTask(projPath)
    status = task['status']['name']
    return status


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
    task = getTask(filePath)
    assetType = session.query('AssetType where name is Upload').one()
    try:
        asset = session.query('Asset where name is "%s" and parent.name is "%s"' %
                              (assetName, task['parent']['name'])).one()
    except:
        asset = session.create('Asset', {
            'name': assetName,
            'parent': task['parent'],
            'type': assetType
        })
        session.commit()
    return asset


def createAttachment(version, name, outfile, framein, frameout, framerate):
    server_location = session.query('Location where name is "ftrack.server"').one()
    component = version.create_component(
        path=outfile,
        data={
            'name': name
        },
        location=server_location
    )
    component['metadata']['ftr_meta'] = json.dumps({
        'frameIn': framein,
        'frameOut': frameout,
        'frameRate': framerate
    })
    component.session.commit()


def createAndPublishVersion(filePath, comment, asset, outfilemp4, outfilewebm, thumbnail, framein, frameout, framerate):
    task = getTask(filePath)
    status = task['status']
    version = session.create('AssetVersion', {
        'asset': asset,
        'status': status,
        'comment': comment,
        'task': task
    })
    createAttachment(version, 'ftrackreview-mp4', outfilemp4, framein, frameout, framerate)
    createAttachment(version, 'ftrackreview-webm', outfilewebm, framein, frameout, framerate)
    session.commit()
    if os.path.exists(thumbnail):
        attachThumbnail(thumbnail, task, asset, version)
    return version


def attachThumbnail(thumbnail, task, asset, version):
    # Currently, it is not possible to set thumbnails using new API
    # This is a workaround using the old API.
    task_old_api = ftrack.Task(id=task['id'])
    asset_old_api = ftrack.Asset(id=asset['id'])
    for vers in asset_old_api.getVersions():
        if vers.getId() == version['id']:
            version_old_api = vers
            attachment = version_old_api.createThumbnail(thumbnail)
            task_old_api.setThumbnail(attachment)
            break


def getStatus(statusName):
    status = session.query('Status where name is "%s"'  % statusName).one()
    return status


def setTaskStatus(filePath, version, statusName):
    task = getTask(filePath)
    status = getStatus(statusName)
    task['status'] = status
    version['status'] = status
    session.commit()


def getProjectFromShot(id):
    shot = session.query('Shot where id is %s' % id).one()
    return shot['name']
