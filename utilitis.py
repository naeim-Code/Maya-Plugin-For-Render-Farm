import os
import shutil
import maya.cmds as cmds
import glob
import sys
import subprocess
import locale
import webbrowser
import re as regex 
import farmWin 

import SceneFiles 

try:
    import hashlib
except:
    pass

class FileInfo:

    def __init__(self, serverPath, localPath, fileSize = -1, toCopy = True):
        self.serverPath = serverPath
        self.localPath = localPath
        if not os.path.exists(self.localPath):
            self.localPath = cmds.workspace(expandName=self.localPath)
        self.fileSize = fileSize
        self.toCopy = toCopy
        if self.fileSize == -1:
            try:
                self.fileSize = os.stat(self.localPath).st_size
            except:
                pass


class FileNodeAttributes:
    __slots__ = ['node_name',
     'available_nodes_list',
     'attribute_name',
     'all_options',
     'special_case']

    def __init__(self, node_name, available_nodes_list, attribute_name, all_options = True, special_case = False):
        self.node_name = node_name
        self.available_nodes_list = available_nodes_list
        self.attribute_name = attribute_name
        self.all_options = all_options
        self.special_case = special_case


def appendFileInfo(vecFiles, serverPath, localPath, fileSize = -1, toCopy = True):
    found = False
    for f in vecFiles:
        if f.serverPath == serverPath:
            found = True
            break

    if not found:
        vecFiles.append(FileInfo(serverPath, localPath, fileSize=fileSize, toCopy=toCopy))


def copyFolder(srcFolder, destFolder, vecFiles, subPath):
    if not existsFile(os.path.join(destFolder, os.path.basename(srcFolder))):
        os.makedirs(os.path.join(destFolder, os.path.basename(srcFolder)))
    entries = os.listdir(srcFolder)
    for f in entries:
        if f[0:1] == '.':
            continue
        if isDir(os.path.join(srcFolder, f)):
            copyFolder(os.path.join(srcFolder, f), os.path.join(destFolder, os.path.basename(srcFolder)), vecFiles, subPath + '/' + f)
        else:
            appendFileInfo(vecFiles, subPath + '/' + f, os.path.join(srcFolder, f))


def mstr(st):
    s = ''
    try:
        s = str(st)
    except:
        s = st

    return s


def existsFile(file_path):
    if file_path:
        workspace_filepath = cmds.workspace(expandName=file_path)
        if os.path.exists(file_path) or os.path.exists(workspace_filepath):
            return True
    return False


def myFileSize(fname):
    if fname:
        if os.path.exists(fname):
            return os.path.getsize(fname)
        f = cmds.workspace(expandName=fname)
        if os.path.exists(f) and not isDir(f):
            return os.path.getsize(f)
    return -1


def copyFile(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    if not os.path.exists(os.path.join(dst, os.path.basename(src))):
        if os.path.exists(src) and not isDir(src):
            debuglog('copy ' + src + ' to ' + dst)
            shutil.copy(src, dst)
        else:
            f = cmds.workspace(expandName=src)
            if os.path.exists(f) and not isDir(f):
                debuglog('copy ws ' + f + ' to ' + dst)
                shutil.copy(f, dst)
            else:
                debuglog("!!! can't find file " + src)
    else:
        debuglog('dest already existing ' + os.path.join(dst, os.path.basename(src)))


def isDir(fname):
    return os.path.isdir(fname)


def debuglog(text):
    if False:
        print text


def checkFilename(filename):
    allowed = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_-. '
    for s in filename:
        if s in allowed:
            return False

    return True


def changeFilename(filename):
    return ''


def getChangedMayaFilename():
    a = os.path.basename(cmds.file(sceneName=True, q=1))
    changed = changeFilename(a)
    if changed != '':
        a = changed
    a = a.replace(' ', '_')
    if a == '':
        if cmds.file(q=1, type=1)[0] != 'mayaBinary':
            a = 'untitled.mb'
        else:
            a = 'untitled.ma'
    aorig = a
    i = 1
    while os.path.exists(os.path.join(farmWin.farmWin.m_defaultPath, farmWin.farmWin.m_userName, a)):
        a = aorig[:-3] + '_' + str(i) + aorig[-3:]
        i += 1

    return a


def calcMd5(filepath):
    md = '0'
    try:
        md = hashlib.md5(file(filepath).read()).hexdigest()
    except:
        md = '0'

    return md

 


def isImage(p):
    if not os.path.exists(p):
        return False
    try:
        fh = open(p)
        conts = [ ord(d) for d in fh.read(8) ]
        if conts[:2] == [255, 216]:
            return True
        if conts[:8] == [137,
         80,
         78,
         71,
         13,
         10,
         26,
         10]:
            return True
        if conts[:2] == [66, 77]:
            return True
        if conts[:3] == [73, 73, 42]:
            return True
        if conts[:3] == [77, 77, 42]:
            return True
    finally:
        fh.close()

    return False


def isMovieTexture(tex):
    movie_textures = ['.mov',
     '.avi',
     '.mpg',
     '.mpeg',
     '.wmv',
     '.wmv',
     '.asf',
     '.mp4',
     '.flv',
     '.divx']
    return tex in movie_textures


def generatePreview(stPath):
    curTime = cmds.currentTime(query=True)
    try:
        a = cmds.getAttr('defaultRenderGlobals.imageFormat')
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)
        cmds.playblast(frame=1, format='image', w=120, h=80, p=100, viewer=0, cf=stPath, fo=1, v=False, orn=False)
        cmds.setAttr('defaultRenderGlobals.imageFormat', a)
    except:
        cmds.setAttr('defaultRenderGlobals.imageFormat', a)

    cmds.currentTime(curTime)


def createPath(stPath, stFile):
    return 'X:\\' + stPath + '\\' + stFile


def _createPath(username, drive = 'X:/', *args):
    path = drive
    for folder in args:
        path = os.path.join(path, folder)

    return os.path.normpath(path).replace('\\', '/')


def createTempPath(stPath, stFile):
    return 'c:\\logs\\temprender\\' + stFile


def createOutPath(stUser):
    return 'c:\\logs\\output\\' + stUser


def getMentalLayers():
    layers = cmds.ls(et='renderLayer')
    mentalLayers = []
    for l in layers:
        mentalLayers.append(l)

    return mentalLayers


def getConfigFileContent():
    s = []
    file = os.path.join(os.path.dirname(__file__), 'clientsettings.cfg')
    try:
        cfgfile = open(file, 'r')
        while cfgfile:
            line = cfgfile.readline()
            if len(line) == 0:
                break
            line = line.replace('\r', '')
            line = line.replace('\n', '')
            s.append(line)

    except:
        print 'clientsettings.cfg not found at ' + file

    return s


def proptest1(testobj):
    props = cmds.listAttr(testobj)
    vals1 = []
    for p in props:
        try:
            vals1.append([testobj + '.' + p, cmds.getAttr(testobj + '.' + p)])
        except:
            a = 1

    return vals1


def proptest2(testobj, vals1):
    props = cmds.listAttr(testobj)
    vals2 = proptest1(testobj)
    res = []
    for i in range(0, len(vals1)):
        if cmds.getAttr(vals1[i][0]) != vals1[i][1]:
            res.append(vals1[i][0] + ' ' + str(vals1[i][1]) + ':' + str(cmds.getAttr(vals1[i][0])))

    return res


def readFtpFileContents(filePath):
    contsFiles = []
    contsSizes = []
    file = open(filePath, 'r')
    for f in file.readlines():
        try:
            entry = f.split(':')
            contsFiles.append(entry[0].lower())
            contsSizes.append(int(entry[1].lower()))
        except:
            pass

    file.close()
    return (contsFiles, contsSizes)


def onlyOneFrame():
    startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
    endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
    if startFrame == endFrame:
        return True
    else:
        return False


def rendererValidForDistributedRendering():
    current_renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
    renderers_blocked_for_distributed = ['arnold', 'ifmIrayPhotoreal', 'redshift']
    if current_renderer in renderers_blocked_for_distributed:
        return False
    else:
        return True


def renderFiveOrMoreFrames():
    start_frame = cmds.getAttr('defaultRenderGlobals.startFrame')
    end_frame = cmds.getAttr('defaultRenderGlobals.endFrame')
    frame_amount = end_frame - start_frame + 1
    if frame_amount >= 5:
        return True
    else:
        return False


def enableDistributedRenderingCheckbox():
    if onlyOneFrame() and rendererValidForDistributedRendering():
        return True
    else:
        return False


def enableCostEstimationButton():
    return renderFiveOrMoreFrames()


def isAllowedSingleFrameFormat(imageFormat):
    allowedFormats = [3,
     8,
     19,
     20,
     32,
     51]
    if imageFormat in allowedFormats:
        return True
    else:
        return False


def isAllowedSingleFrameFormatVray(imageFormat):
    allowedFormats = [None,
     'tif',
     'jpg',
     'tga',
     'bmp',
     'png',
     'exr']
    if imageFormat in allowedFormats:
        return True
    else:
        return False
        return


def getExtension(imageFormat, subformat = ''):
    if imageFormat == 51 and subformat != '':
        subf = {'tifu': '.tif',
         'tif': '.tif',
         'exr': '.exr',
         'hdr': '.hdr',
         'picture': '.picture',
         'ppm': '.ppm',
         'ps': '.ps',
         'qntntsc': 'yuv',
         'ct': '.ct',
         'st': '.st'}
        if subformat in subf:
            return subf[subformat]
    formats = [[0, '.gif'],
     [3, '.tif'],
     [6, '.als'],
     [7, '.iff'],
     [8, '.jpg'],
     [9, '.eps'],
     [10, '.iff'],
     [11, '.cin'],
     [19, '.tga'],
     [20, '.bmp'],
     [31, '.psd'],
     [32, '.png'],
     [35, '.dds'],
     [36, '.psd'],
     [51, '.exr']]
    for f in formats:
        if f[0] == imageFormat:
            return f[1]

    return ''


def parseSequence(filename, wildcard = '*', single_replace = True):
    if '<f>' in filename:
        return filename.replace('<f>', wildcard)
    filename = regex.sub('\\$F[0-9]', wildcard, filename)

    def replace_function(matched_object):
        replaced_characters = ''
        if single_replace == False:
            replaced_characters = wildcard * len(matched_object.group(2))
        else:
            replaced_characters = wildcard
        return matched_object.group(1) + replaced_characters + matched_object.group(3)

    filename = regex.sub('([\\.\\_])(\\d{1,5})(\\.\\D.*?)\\Z', replace_function, filename)
    return filename


def getRelativePath(stSourceFolder, stPath):
    root_dir_drive, _ = os.path.splitdrive(stSourceFolder)
    file_drive, _ = os.path.splitdrive(stPath)
    if root_dir_drive.lower() == file_drive.lower():
        return os.path.relpath(stPath, stSourceFolder)
    else:
        return ''


def findAllNodes(allnodes, type):
    try:
        if type in cmds.allNodeTypes():
            nodes = cmds.ls(et=type)
            if nodes == None:
                nodes = []
        else:
            nodes = []
        return nodes
    except:
        return []

    return


def convert_to_old_file_lists(all_scene_file_nodes):
    allTextures = []
    allObjects = []
    allParams = []
    allOptions = []
    for scene_node in all_scene_file_nodes:
        allTextures.append(scene_node.node_attribute_value)
        allObjects.append(scene_node.node_name)
        allParams.append(scene_node.complete_attribute_name)
        allOptions.append(False)

    return (allTextures,
     allObjects,
     allParams,
     allOptions)


def findAllTextures(allLayers = True):
    allTextures = []
    allObjects = []
    allParams = []
    allOptions = []
    not_found_by_SceneFiles = [SceneFiles.FilepathNode]
    scene_files = SceneFiles.SceneFiles()
    found_by_SceneFiles = scene_files.all_file_path_nodes
    found_by_findAllTextures = [SceneFiles.FilepathNode]
    scene_file_allTextures, scene_file_allObjects, scene_file_allParams, scene_file_allOptions = convert_to_old_file_lists(found_by_SceneFiles)
    if allLayers:
        oldRenderLayer = cmds.editRenderLayerGlobals(currentRenderLayer=1, q=1)
        renderLayers = cmds.ls(type='renderLayer')
    else:
        renderLayers = [1]
    for l in renderLayers:
        if allLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

        allnodes = cmds.allNodeTypes()
        file_nodes = []
        try:
            file_nodes.append(FileNodeAttributes('fileTextures', findAllNodes(allnodes, 'file'), 'fileTextureName', all_options=False, special_case=True))
            file_nodes.append(FileNodeAttributes('iblNodes', findAllNodes(allnodes, 'mentalrayIblShape'), 'texture', all_options=False, special_case=True))
            file_nodes.append(FileNodeAttributes('mentalrayFiles', findAllNodes(allnodes, 'mentalrayTexture'), 'fileTextureName', all_options=False, special_case=True))
            file_nodes.append(FileNodeAttributes('psdFiles', findAllNodes(allnodes, 'psdFileTex'), 'fileTextureName', all_options=False))
            file_nodes.append(FileNodeAttributes('imagePlanes', findAllNodes(allnodes, 'imagePlane'), 'imageName', all_options=False))
            file_nodes.append(FileNodeAttributes('iesfiles', findAllNodes(allnodes, 'mentalrayLightProfile'), 'fileName', all_options=False))
            file_nodes.append(FileNodeAttributes('vrayiesfiles', findAllNodes(allnodes, 'VRayLightIESShape'), 'iesFile', all_options=False))
            file_nodes.append(FileNodeAttributes('vraymeshfiles', findAllNodes(allnodes, 'VRayMesh'), 'fileName', all_options=False, special_case=True))
            file_nodes.append(FileNodeAttributes('vraymeshfiles', findAllNodes(allnodes, 'VRayProxy'), 'fileName', all_options=False, special_case=True))
            file_nodes.append(FileNodeAttributes('vrayptexfiles', findAllNodes(allnodes, 'VRayPtex'), 'ptexFile'))
            file_nodes.append(FileNodeAttributes('aifiles', findAllNodes(allnodes, 'makeIllustratorCurves'), 'illustratorFilename', all_options=False))
            file_nodes.append(FileNodeAttributes('mrBinaryProxyfiles', findAllNodes(allnodes, 'mip_binaryproxy'), 'object_filename'))
            file_nodes.append(FileNodeAttributes('movies', findAllNodes(allnodes, 'movie'), 'fileTextureName'))
            file_nodes.append(FileNodeAttributes('assemblyReferences', findAllNodes(allnodes, 'assemblyReference'), 'definition', special_case=True))
            file_nodes.append(FileNodeAttributes('vRaySimbiont', findAllNodes(allnodes, 'VRaySimbiont'), 'f'))
            file_nodes.append(FileNodeAttributes('substance', findAllNodes(allnodes, 'substance'), 'package', special_case=True))
            file_nodes.append(FileNodeAttributes('pxrTexture', findAllNodes(allnodes, 'PxrTexture'), 'filename'))
            file_nodes.append(FileNodeAttributes('pxrNormalMap', findAllNodes(allnodes, 'PxrNormalMap'), 'filename'))
            file_nodes.append(FileNodeAttributes('pxrBump', findAllNodes(allnodes, 'PxrBump'), 'filename'))
            file_nodes.append(FileNodeAttributes('pxrStdEnvMapLight', findAllNodes(allnodes, 'PxrStdEnvMapLight'), 'rman__EnvMap'))
            file_nodes.append(FileNodeAttributes('rmanImageFile', findAllNodes(allnodes, 'rmanImageFile'), 'File'))
            file_nodes.append(FileNodeAttributes('rmanTexture3d', findAllNodes(allnodes, 'rmanTexture3d'), 'File'))
            file_nodes.append(FileNodeAttributes('redshiftEnv', findAllNodes(allnodes, 'RedshiftEnvironment'), 'tex0'))
            file_nodes.append(FileNodeAttributes('redshiftVolume', findAllNodes(allnodes, 'RedshiftVolumeShape'), 'fileName'))
            file_nodes.append(FileNodeAttributes('redshiftIESLight', findAllNodes(allnodes, 'RedshiftIESLight'), 'profile'))
            file_nodes.append(FileNodeAttributes('redshiftDomeLight', findAllNodes(allnodes, 'RedshiftDomeLight'), 'tex0'))
            file_nodes.append(FileNodeAttributes('redshiftNormalMap', findAllNodes(allnodes, 'RedshiftNormalMap'), 'tex0'))
            file_nodes.append(FileNodeAttributes('redshiftSprite', findAllNodes(allnodes, 'RedshiftSprite'), 'tex0'))
            file_nodes.append(FileNodeAttributes('redshiftBokeh', findAllNodes(allnodes, 'RedshiftBokeh'), 'dofBokehImage'))
            file_nodes.append(FileNodeAttributes('vRayScannedMtl', findAllNodes(allnodes, 'VRayScannedMtl'), 'file'))
            file_nodes.append(FileNodeAttributes('mashAudio', findAllNodes(allnodes, 'MASH_Audio'), 'filename'))
            allReferencedFiles = cmds.file(q=True, l=True)
        except:
            allReferencedFiles = []

        for nodes in file_nodes:
            if nodes.special_case:
                if nodes.node_name == 'iblNodes':
                    appendIblNodes(nodes, allTextures, allObjects, allParams, allOptions)
                elif nodes.node_name == 'vraymeshfiles':
                    appendVraymeshFiles(nodes, allTextures, allObjects, allParams, allOptions)
                elif nodes.node_name == 'mentalrayFiles':
                    appendMentalrayFiles(nodes, allTextures, allObjects, allParams, allOptions)
                elif nodes.node_name == 'substance':
                    appendSubstance(nodes, allTextures, allObjects, allParams, allOptions)
                elif nodes.node_name == 'assemblyReferences':
                    appendAssemblyReference(nodes, allTextures, allObjects, allParams, allOptions)
                elif nodes.node_name == 'fileTextures':
                    appendFileTextures(nodes, allTextures, allObjects, allParams, allOptions)
            else:
                appendDefaultTextureNodes(nodes, allTextures, allObjects, allParams, allOptions)

    if allLayers:
        cmds.editRenderLayerGlobals(currentRenderLayer=oldRenderLayer)
    for i, texture in enumerate(scene_file_allTextures):
        if texture in allTextures:
            scene_file_allTextures.pop(i)
            scene_file_allObjects.pop(i)
            scene_file_allParams.pop(i)
            scene_file_allOptions.pop(i)
        else:
            not_found_by_SceneFiles.append(SceneFiles.FilepathNode(scene_file_allObjects[i], scene_file_allParams[i], scene_file_allTextures[i], scene_file_allOptions[i]))

    for i, texture in enumerate(allTextures):
        found_by_findAllTextures.append(SceneFiles.FilepathNode(allObjects[i], allParams[i], allTextures[i], allOptions[i]))

    allTextures.extend(scene_file_allTextures)
    allObjects.extend(scene_file_allObjects)
    allParams.extend(scene_file_allParams)
    allOptions.extend(scene_file_allOptions)
    return (allTextures,
     allObjects,
     allParams,
     allOptions)


def appendDefaultTextureNodes(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.' + nodes.attribute_name):
            attribute = cmds.getAttr(node + '.' + nodes.attribute_name)
            if attribute:
                allTextures.append(attribute)
                allObjects.append(node)
                allParams.append(node + '.' + nodes.attribute_name)
                allOptions.append(nodes.all_options)


def appendAssemblyReference(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.' + nodes.attribute_name):
            attribute = cmds.getAttr(node + '.' + nodes.attribute_name)
            if attribute:
                allTextures.append(attribute)
                allObjects.append(node)
                allParams.append(node + '.' + nodes.attribute_name)
                allOptions.append(nodes.all_options)
                i = 0
            while True:
                p = node + '.representations[' + str(i) + ']'
                repData = cmds.getAttr(p + '.repData')
                repType = cmds.getAttr(p + '.repType')
                if repData == None:
                    break
                if repType in ('Cache', 'Scene'):
                    allTextures.append(repData)
                    allObjects.append(node)
                    allParams.append(p + '.repData')
                    allOptions.append(nodes.all_options)
                i += 1

    return


def appendSubstance(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.' + nodes.attribute_name):
            attribute = cmds.getAttr(node + '.' + nodes.attribute_name)
            if attribute:
                if not existsFile(attribute):
                    if attribute[0] == '/':
                        attribute = attribute[1:]
                    attribute = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'plug-ins/substance/substances', attribute)
                allTextures.append(attribute)
                allObjects.append(node)
                allParams.append(node + '.' + nodes.attribute_name)
                allOptions.append(nodes.all_options)


def appendMentalrayFiles(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.' + nodes.attribute_name):
            attribute = cmds.getAttr(node + '.' + nodes.attribute_name)
            if attribute or cmds.attributeQuery('miWritable', node=node, exists=True):
                allTextures.append(attribute)
                allObjects.append(node)
                allParams.append(node + '.' + nodes.attribute_name)
                allOptions.append(nodes.all_options)


def appendVraymeshFiles(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.' + nodes.attribute_name):
            attribute = cmds.getAttr(node + '.' + nodes.attribute_name)
            if attribute and '%0' not in attribute and '<' not in attribute:
                allTextures.append(attribute)
                allObjects.append(node)
                allParams.append(node + '.' + nodes.attribute_name)
                allOptions.append(nodes.all_options)


def appendIblNodes(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.' + nodes.attribute_name):
            attribute = cmds.getAttr(node + '.' + nodes.attribute_name)
            if attribute and cmds.getAttr(node + '.type') == 0:
                allTextures.append(attribute)
                allObjects.append(node)
                allParams.append(node + '.' + nodes.attribute_name)
                allOptions.append(nodes.all_options)


def appendFileTextures(nodes, allTextures, allObjects, allParams, allOptions):
    for node in nodes.available_nodes_list:
        if cmds.objExists(node + '.fileTextureName'):
            attribute = cmds.getAttr(node + '.fileTextureName')
            uvt = False
            if attribute != '':
                if attribute.find('<') > 0 and attribute.find('>') > 0 and attribute.find('<f>') < 0:
                    uvt = True
                    patternName = attribute.replace('<u>', '*').replace('<v>', '*').replace('<U>', '*').replace('<V>', '*').replace('<UDIM>', '*').replace('<udim>', '*')
                    if not os.path.exists(os.path.dirname(patternName)):
                        patternName = cmds.workspace(expandName=patternName)
                    found = False
                    for infile in glob.glob(patternName):
                        allTextures.append(infile)
                        allObjects.append(node)
                        allParams.append('')
                        allOptions.append(nodes.all_options)
                        found = True

                    allTextures.append(attribute)
                    allObjects.append(node)
                    allParams.append(node + '.' + nodes.attribute_name)
                    allOptions.append(2 if found else True)
                else:
                    allTextures.append(attribute)
                    allObjects.append(node)
                    allParams.append(node + '.' + nodes.attribute_name)
                    allOptions.append(nodes.all_options)
            try:
                tiling = cmds.getAttr(node + '.uvTilingMode')
                if tiling != 0 and not uvt:
                    patternName = cmds.getAttr(node + '.computedFileTextureNamePattern')
                    patternName = patternName.replace('<u>', '*').replace('<v>', '*').replace('<U>', '*').replace('<V>', '*').replace('<UDIM>', '*').replace('<udim>', '*')
                    for infile in glob.glob(patternName):
                        allTextures.append(infile)
                        allObjects.append(node)
                        allParams.append('')
                        allOptions.append(nodes.all_options)

            except:
                pass


def getMentalrayParserResult(parserPath, miFile, searchFolder):
    res = {'tex': [],
     'texmissing': []}
    args = parserPath + ' passX4f -i "' + miFile + '" -s "' + searchFolder + '" -t check'
    output = subprocess.Popen(args.encode(locale.getpreferredencoding()), stdout=subprocess.PIPE).communicate()[0]
    resultLines = output.splitlines()
    tex = []
    texfound = []
    for line in resultLines:
        if line == 'error':
            ret = False
            return None
        testResult = line.split('|')
        if len(testResult) == 2:
            if testResult[0] == 'tex':
                tex.append(testResult[1])
            if testResult[0] == 'texfound':
                texfound.append(testResult[1])

    for t in tex:
        found = False
        for tf in texfound:
            if os.path.basename(t) == os.path.basename(tf):
                res['tex'].append(tf)
                found = True
                break

        if not found:
            res['texmissing'].append(t)

    return res


def getVrayParserResult(parserPath, vrsceneFile, searchFolder):
    res = {'tex': [],
     'texmissing': []}
    args = parserPath + ' passX4f -i "' + vrsceneFile + '" -s "' + searchFolder + '" -t check'
    output = subprocess.Popen(args.encode(locale.getpreferredencoding()), stdout=subprocess.PIPE).communicate()[0]
    resultLines = output.splitlines()
    tex = []
    texfound = []
    for line in resultLines:
        if line == 'error':
            ret = False
            return None
        testResult = line.split('|')
        if len(testResult) == 2:
            if testResult[0] == 'tex':
                tex.append(testResult[1])
            if testResult[0] == 'vrmesh':
                tex.append(testResult[1])
            if testResult[0] == 'include':
                tex.append(testResult[1])
            if testResult[0] == 'texfound':
                texfound.append(testResult[1])
            if testResult[0] == 'vrmeshfound':
                texfound.append(testResult[1])
            if testResult[0] == 'includefound':
                texfound.append(testResult[1])

    for t in tex:
        found = False
        for tf in texfound:
            if os.path.basename(t) == os.path.basename(tf):
                res['tex'].append(tf)
                found = True
                break

        if not found:
            res['texmissing'].append(t)

    return res


def getRedshiftParserResult(parserPath, rsFile, searchFolder):
    res = {}
    args = parserPath + ' passX4f -i "' + rsFile + '" -t check'
    output = subprocess.Popen(args.encode(locale.getpreferredencoding()), stdout=subprocess.PIPE).communicate()[0]
    resultLines = output.splitlines()
    for line in resultLines:
        if line == 'error':
            ret = False
            return None
        testResult = line.split('|')
        if len(testResult) >= 2:
            if testResult[0] not in res:
                res[testResult[0]] = []
            res[testResult[0]].append(testResult[1])

    return res


def changeFileWithParser(parserPath, file_to_change, newTexPath, newOutPath):
    args = parserPath + ' passX4f -i "' + file_to_change + '" -t change -ro "' + newOutPath + '" -rt "' + newTexPath + '"'
    output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def getIflFilenames(file, fullPath = False):
    filenames = []
    if not os.path.exists(file):
        file = cmds.workspace(expandName=file)
    if os.path.exists(file):
        f = open(file)
        for line in f.readlines():
            line = line.strip()
            if len(line) == 0 or line[0] == ';':
                continue
            arr = line.split(' ')
            if len(arr) > 0 and is_number(arr[-1]):
                line = line[:-(len(arr[-1]) + 1)]
            if fullPath:
                line = findIflPath(file, line)
            filenames.append(line)

        f.close()
    return filenames


def findIflPath(iflfile, ifl_entry):
    iflPath = ifl_entry
    if os.path.exists(iflPath):
        return iflPath
    iflPath = cmds.workspace(expandName=iflPath)
    if os.path.exists(iflPath):
        return iflPath
    iflPath = os.path.join(os.path.dirname(iflfile), os.path.basename(iflPath))
    if os.path.exists(iflPath):
        return iflPath
    return ifl_entry


def findFilesRecursive(path):
    subst = len(path) + 1
    if path[-1] == '\\' or path[-1] == '/':
        subst = len(path)
    files = [ os.path.join(dp, f)[subst:] for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn ]
    return files


def getGchaAssets(characterFiles):
    import xml.etree.ElementTree as ET
    tree = ET.parse(characterFiles)
    for p in tree.findall('.//geometryAssets/element/filename'):
        yield p.attrib['value']


def adjustGchaFile(characterFiles, rootFolder):
    import xml.etree.ElementTree as ET
    tree = ET.parse(characterFiles)
    changed = False
    for p in tree.findall('.//geometryAssets/element/filename'):
        p.attrib['value'] = os.path.join(rootFolder, os.path.basename(p.attrib['value'])).replace('\\', '/')
        changed = True

    if changed:
        tree.write(characterFiles)


def get_farminizer_build():
    file = os.path.join(os.path.dirname(__file__), 'version.txt')
    with open(file) as version_file:
        return version_file.readline().strip()


def urString(inputString):
    try:
        inputString = inputString.decode('raw_unicode_escape')
    except AttributeError:
        pass

    return inputString
