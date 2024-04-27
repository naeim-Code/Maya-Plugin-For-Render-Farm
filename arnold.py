import maya.cmds as cmds
import shutil
import glob
import sys


import validator
from validator import *
import utilitis
from utilitis import *


import re
regexStandins = re.compile(urString('(?:MayaFile)\\s*\\{[^\\}]*?filename\\s+\\"(.*?)\\".*?\\}'), re.DOTALL)
regexStandinsOtherFiles = re.compile(urString('(?:image)\\s*\\{[^\\}]*?filename\\s+\\"(.*?)\\".*?\\}'), re.DOTALL)

def getStandinFilenames(file, fullPath = False):
    filenames = []
    searchpath = ''
    if not os.path.exists(file):
        file = cmds.workspace(expandName=file)
    if not os.path.exists(file):
        file = os.path.join(cmds.workspace(q=1, rd=1), 'data', file)
    if os.path.exists(file):
        f = open(file)
        content = f.read()
        f.close()
        filenames = re.findall(regexStandins, content)
        sp = re.findall('texture_searchpath\\s\\"(.*)\\"', content)
        if len(sp) > 0:
            searchpath = sp[0]
    return {'filenames': filenames,
     'searchpath': searchpath}


def getStandinOtherFilenames(file):
    filenames = []
    searchpath = ''
    if not os.path.exists(file):
        file = cmds.workspace(expandName=file)
    if not os.path.exists(file):
        file = os.path.join(cmds.workspace(q=1, rd=1), 'data', file)
    if os.path.exists(file):
        f = open(file)
        content = f.read()
        f.close()
        filenames = re.findall(regexStandinsOtherFiles, content)
    return {'filenames': filenames}


def adjustStandinFile(file, serverPath):
    regexSubStandins = re.compile(urString('(?:procedural)\\s*\\{[^\\}]*?dso\\s+\\"(.*?)\\".*?\\}'), re.DOTALL)
    if os.path.exists(file):
        fh = open(file)
        content = fh.read()
        fh.close()
        filenames = re.findall(regexStandins, content)
        for ff in filenames:
            content = content.replace(ff, os.path.basename(ff))

        searchpath = re.findall('texture_searchpath\\s\\"(.*)\\"', content)
        for ff in searchpath:
            if len(ff) > 0:
                content = content.replace(ff, (serverPath + '/sourceimages').replace('\\', '/'))

        subStandins = re.findall(regexSubStandins, content)
        for ff in subStandins:
            if len(ff) > 0:
                content = content.replace(ff, (serverPath + '/data/' + os.path.basename(ff)).replace('\\', '/'))

        others = re.findall(regexStandinsOtherFiles, content)
        for ff in others:
            if len(ff) > 0:
                content = content.replace(ff, (serverPath + '/sourceimages/' + os.path.basename(ff)).replace('\\', '/'))

        fh = open(file, 'w')
        fh.write(content)
        fh.close()


def findAllStandinFiles(arr, missing, path):
    regexSubStandins = re.compile(urString('(?:procedural)\\s*\\{[^\\}]*?dso\\s+\\"(.*?)\\".*?\\}'), re.DOTALL)
    ppath = path
    if not os.path.exists(ppath):
        ppath = cmds.workspace(expandName=ppath)
    if not os.path.exists(ppath):
        ppath = os.path.join(cmds.workspace(q=1, rd=1), 'data', path)
    if os.path.exists(ppath):
        if ppath not in arr:
            fh = open(ppath)
            content = fh.read()
            fh.close()
            subStandins = re.findall(regexSubStandins, content)
            for s in subStandins:
                findAllStandinFiles(arr, missing, s)

            arr.add(ppath)
    else:
        missing.add(path)


class ValArnold(Validator):
    is_renderer_validator = True
    toRetarget = []
    ARNOLD_DISABLED = 0

    def getName(self):
        try:
            if cmds.getAttr('defaultArnoldRenderOptions.renderDevice'):
                self.mainDialog.gpu_enabled = True
        except:
            self.mainDialog.gpu_enabled = False

        return 'Arnold'

    def getIdentifier(self):
        return ['arnold']

    def test(self, resultList, fastCheck, layerinfos):
        self.giFile = ''
        renderLayers = cmds.ls(type='renderLayer')
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
            if curRend in self.getIdentifier():
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                arnoldtype = 'ARNOLD'
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, arnoldtype))
                if framestep < 1:
                    resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                if int(cmds.about(version=1)[0:4]) < 2017:
                    resultList.append(TestResult(8001, 2, self, 'You need at least Maya 2017 to use Arnold', False, 0))
                if self.mainDialog.isSingleFrameRender():
                    resultList.append(TestResult(8015, 2, self, 'Common: Arnold Distributed Single frame rendering not yet supported', False, 0))
                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreTextures'):
                        resultList.append(TestResult(8002, 1, self, 'ignoreTextures is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreShaders'):
                        resultList.append(TestResult(8003, 1, self, 'ignoreShaders is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreAtmosphere'):
                        resultList.append(TestResult(8004, 1, self, 'ignoreAtmosphere is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreLights'):
                        resultList.append(TestResult(8005, 1, self, 'ignoreLights is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreShadows'):
                        resultList.append(TestResult(8006, 1, self, 'ignoreShadows is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreSubdivision'):
                        resultList.append(TestResult(8007, 1, self, 'ignoreSubdivision is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreDisplacement'):
                        resultList.append(TestResult(8008, 1, self, 'ignoreDisplacement is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreBump'):
                        resultList.append(TestResult(8009, 1, self, 'ignoreBump is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreSmoothing'):
                        resultList.append(TestResult(8010, 1, self, 'ignoreSmoothing is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreMotionBlur'):
                        resultList.append(TestResult(8011, 1, self, 'ignoreMotionBlur is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreSss'):
                        resultList.append(TestResult(8012, 1, self, 'ignoreSss is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreMis'):
                        resultList.append(TestResult(8013, 1, self, 'ignoreMis is activated', False, 0))
                except:
                    pass

                try:
                    if cmds.getAttr('defaultArnoldRenderOptions.ignoreDof'):
                        resultList.append(TestResult(8014, 1, self, 'ignoreDof is activated', False, 0))
                except:
                    pass

                try:
                    frmt = cmds.getAttr('defaultRenderGlobals.imageFormat')
                    if frmt == 51:
                        subfrmt = cmds.getAttr('defaultRenderGlobals.imfPluginKey')
                        if subfrmt == 'exr' and cmds.getAttr('defaultArnoldDriver.exrCompression') == 0 or subfrmt == 'tif' and cmds.getAttr('defaultArnoldDriver.tiffCompression') == 0:
                            resultList.append(TestResult(7020, 2, self, 'Please activate compression for your output (' + l + ')', False, 0))
                except:
                    pass

                allStandinFiles = set()
                missingStandinFiles = set()
                standIns = cmds.ls(et='aiStandIn')
                if standIns == None:
                    standIns = []
                for s in standIns:
                    path = cmds.getAttr(s + '.dso')
                    if path != None:
                        if '#' in path:
                            mpath = path.replace('#', '*')
                            if len(glob.glob(mpath)) == 0:
                                resultList.append(TestResult(8015, 2, self, 'No StandIn found: "' + mstr(path) + '"', False, 0))
                            else:
                                for standinPath in glob.glob(mpath):
                                    findAllStandinFiles(allStandinFiles, missingStandinFiles, standinPath)

                        elif not existsFile(path):
                            resultList.append(TestResult(8015, 2, self, 'StandIn not found: "' + mstr(path) + '"', False, 0))
                        else:
                            findAllStandinFiles(allStandinFiles, missingStandinFiles, path)

                for path in allStandinFiles:
                    standinInfo = getStandinFilenames(path)
                    for f in standinInfo['filenames']:
                        subpath = f
                        if not os.path.exists(subpath):
                            subpath = os.path.join(standinInfo['searchpath'], f)
                        if not os.path.exists(subpath):
                            subpath = os.path.join(standinInfo['searchpath'], os.path.basename(f))
                        if not os.path.exists(subpath):
                            subpath = cmds.workspace(expandName=f)
                        if not os.path.exists(subpath):
                            subpath = os.path.join(cmds.workspace(q=1, rd=1), 'data', f)
                        if not os.path.exists(subpath):
                            resultList.append(TestResult(8015, 2, self, 'StandIn dependency not found: "' + mstr(f) + '"', False, 0))

                    standinInfo = getStandinOtherFilenames(path)
                    for f in standinInfo['filenames']:
                        subpath = f
                        if not os.path.exists(subpath):
                            subpath = cmds.workspace(expandName=f)
                        if not os.path.exists(subpath):
                            subpath = os.path.join(cmds.workspace(q=1, rd=1), 'data', f)
                        if not os.path.exists(subpath):
                            resultList.append(TestResult(8015, 2, self, 'StandIn dependency not found: "' + mstr(f) + '"', False, 0))

                iesFiles = cmds.ls(et='aiPhotometricLight')
                if iesFiles == None:
                    iesFiles = []
                for i in iesFiles:
                    path = cmds.getAttr(i + '.aiFilename')
                    if not existsFile(path):
                        resultList.append(TestResult(8016, 2, self, 'Photometric file not found: "' + mstr(path) + '"', False, 0))

                aiImageFiles = cmds.ls(et='aiImage')
                if aiImageFiles == None:
                    aiImageFiles = []
                for i in aiImageFiles:
                    path = cmds.getAttr(i + '.filename')
                    if path.find('<') > 0 and path.find('>') > 0 and path.find('<f>') < 0:
                        patternName = path.replace('<u>', '*').replace('<v>', '*').replace('<U>', '*').replace('<V>', '*').replace('<UDIM>', '*').replace('<udim>', '*')
                        if not os.path.exists(os.path.dirname(patternName)):
                            patternName = cmds.workspace(expandName=patternName)
                        found = False
                        for infile in glob.glob(patternName):
                            found = True

                        if not found:
                            resultList.append(TestResult(8016, 2, self, 'aiImage file not found: "' + mstr(path) + '"', False, 0))
                    elif not existsFile(path):
                        resultList.append(TestResult(8016, 2, self, 'aiImage file not found: "' + mstr(path) + '"', False, 0))

                aiVolumes = cmds.ls(et='aiVolume')
                if aiVolumes == None:
                    aiVolumes = []
                for i in aiVolumes:
                    path = cmds.getAttr(i + '.filename')
                    if not existsFile(path):
                        resultList.append(TestResult(8016, 2, self, 'aiVolume file not found: "' + mstr(path) + '"', False, 0))

                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))

        return

    def get_arnold_license_count(self, arnold_license_file):
        """
        reads all lines in given file returns first two rows(row 1 = amount // row 2 = limit) as tuple
        """
        with open(arnold_license_file) as license_file:
            lines = license_file.readlines()
        return (lines[0].strip(), lines[1].strip())

    def furtherAction(self, result):
        if result.type == self.MAX_RP_DIALOG:
            res = selectPassesDialog().split(',')
            self.maxRp, self.maxIterations = int(res[0]), int(res[1])
            return True

    def prepareSave(self, path, vecFiles):
        if not cmds.objExists('defaultArnoldRenderOptions'):
            return ''
        else:
            renderLayers = cmds.ls(type='renderLayer')
            for l in renderLayers:
                if cmds.getAttr(l + '.renderable') == 0:
                    continue
                try:
                    cmds.editRenderLayerGlobals(currentRenderLayer=l)
                except:
                    continue

                curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
                if curRend in self.getIdentifier():
                    self.toRetarget = []
                    self.toRetarget.append(['defaultArnoldRenderOptions.log_filename', cmds.getAttr('defaultArnoldRenderOptions.log_filename'), l])
                    cmds.setAttr('defaultArnoldRenderOptions.log_filename', 'c:\\logs\\arnold.log', type='string')
                    exportPath = createPath(self.mainDialog.m_userName + '\\tex\\maya', 'sourceimages').replace('\\', '/')
                    self.toRetarget.append(['defaultArnoldRenderOptions.procedural_searchpath', cmds.getAttr('defaultArnoldRenderOptions.procedural_searchpath'), l])
                    cmds.setAttr('defaultArnoldRenderOptions.procedural_searchpath', createPath(self.mainDialog.m_userName + '\\tex\\maya', 'data\\').replace('\\', '/'), type='string')
                    self.toRetarget.append(['defaultArnoldRenderOptions.texture_searchpath', cmds.getAttr('defaultArnoldRenderOptions.texture_searchpath'), l])
                    cmds.setAttr('defaultArnoldRenderOptions.texture_searchpath', exportPath, type='string')
                    self.toRetarget.append(['defaultArnoldRenderOptions.bucketSize',
                     cmds.getAttr('defaultArnoldRenderOptions.bucketSize'),
                     l,
                     True])
                    cmds.setAttr('defaultArnoldRenderOptions.bucketSize', 16)
                    self.toRetarget.append(['defaultArnoldRenderOptions.renderType',
                     cmds.getAttr('defaultArnoldRenderOptions.renderType'),
                     l,
                     True])
                    cmds.setAttr('defaultArnoldRenderOptions.renderType', 0)
                    self.toRetarget.append(['defaultArnoldRenderOptions.abortOnLicenseFail',
                     cmds.getAttr('defaultArnoldRenderOptions.abortOnLicenseFail'),
                     l,
                     True])
                    cmds.setAttr('defaultArnoldRenderOptions.abortOnLicenseFail', 1)
                    self.toRetarget.append(['defaultArnoldRenderOptions.skipLicenseCheck',
                     cmds.getAttr('defaultArnoldRenderOptions.skipLicenseCheck'),
                     l,
                     True])
                    cmds.setAttr('defaultArnoldRenderOptions.skipLicenseCheck', 0)
                    try:
                        self.toRetarget.append(['defaultArnoldRenderOptions.autotx',
                         cmds.getAttr('defaultArnoldRenderOptions.autotx'),
                         l,
                         True])
                        cmds.setAttr('defaultArnoldRenderOptions.autotx', 0)
                    except:
                        pass

                    destfolder = os.path.join(path, 'tex', 'maya', 'data')
                    standIns = cmds.ls(et='aiStandIn')
                    if standIns == None:
                        standIns = []
                    allStandinFiles = set()
                    for s in standIns:
                        mpath = cmds.getAttr(s + '.dso')
                        if mpath != None:
                            self.toRetarget.append([s + '.dso', mpath, l])
                            if '#' in mpath:
                                cpath = mpath.replace('#', '*')
                                for p in glob.glob(cpath):
                                    findAllStandinFiles(allStandinFiles, set(), p)

                                cmds.setAttr(s + '.dso', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data', os.path.basename(mpath)), type='string')
                            elif existsFile(mpath):
                                findAllStandinFiles(allStandinFiles, set(), mpath)
                                cmds.setAttr(s + '.dso', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data', os.path.basename(mpath)), type='string')

                    for p in allStandinFiles:
                        standinInfo = getStandinFilenames(p)
                        changed = False
                        for f in standinInfo['filenames']:
                            subpath = f
                            if not os.path.exists(subpath):
                                subpath = os.path.join(standinInfo['searchpath'], f)
                            if not os.path.exists(subpath):
                                subpath = os.path.join(standinInfo['searchpath'], os.path.basename(f))
                            if not os.path.exists(subpath):
                                subpath = os.path.join(cmds.workspace(q=1, rd=1), 'data', f)
                            if not os.path.exists(subpath):
                                subpath = cmds.workspace(expandName=f)
                            if os.path.exists(subpath):
                                appendFileInfo(vecFiles, 'tex/maya/sourceimages/' + os.path.basename(subpath), subpath)
                                changed = True

                        standinInfo = getStandinOtherFilenames(p)
                        for f in standinInfo['filenames']:
                            subpath = f
                            basepath = 'tex/maya/sourceimages/' + os.path.basename(subpath)
                            if not os.path.exists(subpath):
                                subpath = cmds.workspace(expandName=f)
                            if not os.path.exists(subpath):
                                subpath = os.path.join(cmds.workspace(q=1, rd=1), 'data', f)
                                basepath = 'tex/maya/sourceimages/' + f
                            if os.path.exists(subpath):
                                appendFileInfo(vecFiles, basepath, subpath)
                                changed = True

                        if changed:
                            dest = os.path.join(destfolder, os.path.basename(p))
                            shutil.copyfile(p, dest)
                            adjustStandinFile(dest, createPath(self.mainDialog.m_userName, 'tex\\maya'))
                            appendFileInfo(vecFiles, 'tex/maya/data/' + os.path.basename(p), dest, toCopy=False)
                        else:
                            appendFileInfo(vecFiles, 'tex/maya/data/' + os.path.basename(p), p)

                    destfolder = os.path.join(path, 'tex', 'maya', 'sourceimages')
                    iesFiles = cmds.ls(et='aiPhotometricLight')
                    if iesFiles == None:
                        iesFiles = []
                    for i in iesFiles:
                        mpath = cmds.getAttr(i + '.aiFilename')
                        self.toRetarget.append([i + '.aiFilename', mpath, l])
                        if existsFile(mpath):
                            ppath = 'tex/maya/sourceimages/' + os.path.basename(mpath)
                            appendFileInfo(vecFiles, ppath, mpath)
                            cmds.setAttr(i + '.aiFilename', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(mpath)), type='string')

                    destfolder = os.path.join(path, 'tex', 'maya', 'sourceimages')
                    aiImageFiles = cmds.ls(et='aiImage')
                    if aiImageFiles == None:
                        aiImageFiles = []
                    for i in aiImageFiles:
                        mpath = cmds.getAttr(i + '.filename')
                        self.toRetarget.append([i + '.filename', mpath, l])
                        if mpath.find('<') > 0 and mpath.find('>') > 0 and mpath.find('<f>') < 0:
                            patternName = mpath.replace('<u>', '*').replace('<v>', '*').replace('<U>', '*').replace('<V>', '*').replace('<UDIM>', '*').replace('<udim>', '*')
                            if not os.path.exists(os.path.dirname(patternName)):
                                patternName = cmds.workspace(expandName=patternName)
                            for infile in glob.glob(patternName):
                                ppath = 'tex/maya/sourceimages/' + os.path.basename(infile)
                                appendFileInfo(vecFiles, ppath, infile)

                            cmds.setAttr(i + '.filename', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(mpath)), type='string')
                        if existsFile(mpath):
                            ppath = 'tex/maya/sourceimages/' + os.path.basename(mpath)
                            appendFileInfo(vecFiles, ppath, mpath)
                            cmds.setAttr(i + '.filename', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(mpath)), type='string')

                    destfolder = os.path.join(path, 'tex', 'maya', 'cache', 'openVDB')
                    aiVolumes = cmds.ls(et='aiVolume')
                    if aiVolumes == None:
                        aiVolumes = []
                    for i in aiVolumes:
                        mpath = cmds.getAttr(i + '.filename')
                        self.toRetarget.append([i + '.filename', mpath, l])
                        if existsFile(mpath):
                            ppath = 'tex/maya/cache/openVDB/' + os.path.basename(mpath)
                            appendFileInfo(vecFiles, ppath, mpath)
                            cmds.setAttr(i + '.filename', createPath(self.mainDialog.m_userName + '\\tex\\maya\\cache\\openVDB', os.path.basename(mpath)), type='string')

            return ''

    def postSave(self):
        for f in self.toRetarget:
            if f[1] != '' and f[1] != None:
                cmds.editRenderLayerGlobals(currentRenderLayer=f[2])
                if len(f) < 4:
                    cmds.setAttr(f[0], f[1], type='string')
                else:
                    cmds.setAttr(f[0], f[1])

        return
