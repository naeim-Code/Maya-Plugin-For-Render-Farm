import maya.cmds as cmds
import shutil
import sys
import tempfile
import time

import validator
from validator import *
import utilitis
from utilitis import *
 

class ValMental(Validator):
    is_renderer_validator = True
    fgPath = []
    oldFgPaths = []
    oldFgMergePaths = []
    photonPath = []
    oldPhotonPaths = []
    fgMergePath = []
    FG_FREEZE = 0
    FG_ONOFF = 1
    FG_WRITE = 2
    LAYERSMIXED = 3
    MI_STANDALONE = 4
    miExport = False
    originalMats = []
    replacedMats = []

    def getName(self):
        return 'Mental Ray'

    def getIdentifier(self):
        return ['mentalRay']

    def exportMi(self, mipath, startframe, endframe):
        res = False
        if existsFile(mipath):
            os.remove(mipath)
        miExportOptions = 'binary=1;compression=0;tabstop=8;perlayer=1;pathnames=3313323333;assembly=0;fragment=0;fragsurfmats=0;fragsurfmatsassign=0;fragincshdrs=0;fragchilddag=0;passcontrimaps=1;passusrdata=1;overrideAssemblyRootName=0;assemblyRootName='
        cmds.file(mipath, force=True, options=miExportOptions, type='mentalRay', pr=True, ea=True)
        if existsFile(mipath):
            res = True
        return res

    def checkMi(self, mipath, miparser):
        keyval = []
        searchPaths = []
        searchPaths.append(cmds.workspace(q=1, rd=1))
        searchPaths.append(os.environ['MAYA_LOCATION'])
        stSearchPaths = ''
        for f in searchPaths:
            stSearchPaths = stSearchPaths + ' -s "' + f + '"'

        args = miparser + ' passX4f -i "' + mipath + '" ' + stSearchPaths + ' -t check'
        output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
        resultLines = output.splitlines()
        for line in resultLines:
            try:
                parts = line.split('|')
                if len(parts) == 2:
                    key = parts[0]
                    val = parts[1]
                    keyval.append([key, val])
                else:
                    debuglog('miparser split invalid: ' + line)
                    return None
            except:
                debuglog('invalid miparser line: ' + line)
                return None

        return keyval

    def changeMi(self, mipath, miparser, texPath, outPath):
        changeParams = []
        stChange = ''
        for p in changeParams:
            stChange = stChange + ' -so ' + p[0] + ':' + p[1] + '=' + p[2]

        searchPaths = []
        searchPaths.append(cmds.workspace(q=1, rd=1))
        searchPaths.append(os.environ['MAYA_LOCATION'])
        stSearchPaths = ''
        for f in searchPaths:
            stSearchPaths = stSearchPaths + ' -s "' + f + '"'

        args = miparser + ' passX4f -i "' + mipath + '" ' + stSearchPaths + ' -t change -ro "' + outPath + '" -rt "' + texPath + '"' + stChange
        output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    def replaceMat(self, oldMat, newMat):
        debuglog('restoreMats, NYI')
        self.originalMats.append(oldMat)
        self.replacedMats.append(newMat)

    def restoreMats(self):
        debuglog('restoreMats, NYI')

    def replaceMaterials(self):
        debuglog('replaceMaterials, NYI')

    def preCheckStandalone(self):
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
                if self.miExport:
                    self.mainDialog.isMiExport = True
                    break

    def standaloneExport(self, resultList, fPath, vecFiles):
        settingsToWrite = ''
        if self.mainDialog.isMiExport:
            mrVersion = '3.11'
            mrDecimal = 'punkt'
            settingsToWrite += 'version=' + str(mrVersion) + '\r\n'
            settingsToWrite += 'decimal=' + str(mrDecimal) + '\r\n'
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
                    miCheckResult = []
                    allValid = True
                    miparser = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'mentalray')
                    miparser = os.path.join(miparser, 'miparser' if cmds.about(mac=1) else 'miparser.exe')
                    if existsFile(miparser):
                        miTemp = os.path.join(tempfile.gettempdir(), str(time.time()) + '.mi')
                        startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                        endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                        framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                        if framestep < 1:
                            resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                        self.originalMats = []
                        self.replacedMats = []
                        self.replaceMaterials()
                        if self.exportMi(miTemp, startFrame, endFrame):
                            miCheckResult = []
                            keyval = self.checkMi(miTemp, miparser)
                            if keyval != None:
                                for chkRes in keyval:
                                    key = chkRes[0]
                                    val = chkRes[1]
                                    if key == 'err':
                                        resultList.append(TestResult(4031, 2, self, 'Mi: ' + val, False, 0))
                                        allValid = False
                                    else:
                                        miCheckResult.append(chkRes)

                            else:
                                resultList.append(TestResult(4031, 2, self, 'Unknown error checking mi', False, 0))
                                allValid = False
                        else:
                            resultList.append(TestResult(4031, 2, self, 'Scene could not be exported to .mi', False, 0))
                            allValid = False
                        self.restoreMats()
                    else:
                        resultList.append(TestResult(4031, 2, self, 'Please install the mentalray plugin in the Render Farm Application settings', False, 0))
                        allValid = False
                    if allValid:
                        texPath = createPath(self.mainDialog.m_userName, 'tex').replace('\\', '/')
                        outPath = createOutPath(self.mainDialog.m_userName).replace('\\', '/')
                        self.changeMi(miTemp, miparser, texPath, outPath)
                        dest = (fPath + '/tex/' + getChangedMayaFilename() + '.0001.mi').replace('\\', '/')
                        if existsFile(dest):
                            os.remove(dest)
                        os.rename(miTemp, dest)
                        appendFileInfo(vecFiles, 'tex/' + os.path.basename(dest), dest, -1, False)
                        for chkRes in miCheckResult:
                            key = chkRes[0]
                            val = chkRes[1]
                            if key == 'texfound' or key == 'linkfound' or key == 'includefound':
                                appendFileInfo(vecFiles, 'tex/' + os.path.basename(val), val)

                        settingsToWrite += 'singleMiFile=1\n'

        return settingsToWrite

    def test(self, resultList, fastCheck, layerinfos):
        self.fgPath = []
        self.photonPath = []
        self.fgMergePath = []
        self.oldFgPaths = []
        self.oldFgMergePaths = []
        renderLayers = cmds.ls(type='renderLayer')
        cntRenderables = 0
        for r in renderLayers:
            if cmds.getAttr(r + '.renderable') == 1:
                cntRenderables += 1

        if self.mainDialog.isSingleFrameRender() and cntRenderables > 1:
            resultList.append(TestResult(4001, 2, self, 'You may only have one enabled layer if you render a single frame', False, 0))
        bMRFound = False
        bOthersFound = False
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
            if curRend in self.getIdentifier():
                bMRFound = True
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, 'MR'))
                if not cmds.objExists('miDefaultOptions'):
                    continue
                if not cmds.attributeQuery('minSamples', node='miDefaultOptions', exists=1):
                    resultList.append(TestResult(4004, 2, self, 'Mental Settings could not be found.(' + l + ')', False, 0))
                    continue
                if self.mainDialog.isSingleFrameRender():
                    imageFormat = cmds.getAttr('defaultRenderGlobals.imageFormat')
                    if not isAllowedSingleFrameFormat(imageFormat):
                        resultList.append(TestResult(4005, 2, self, 'Rendering: Image Format not allowed for single frame Rendering. Use .png instead', False, 0))
                frmt = cmds.getAttr('defaultRenderGlobals.imageFormat')
                if frmt == 51:
                    subfrmt = cmds.getAttr('defaultRenderGlobals.imfPluginKey')
                    if subfrmt == 'exr' and cmds.getAttr('mentalrayGlobals.imageCompression') == 1 or subfrmt == 'tifu':
                        resultList.append(TestResult(7020, 2, self, 'Rendering: Please activate compression for your output (' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.minSamples') <= -2:
                    resultList.append(TestResult(4006, 1, self, 'Sampling Quality: Minimum Samples seems very low.(' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.minSamples') >= 2:
                    resultList.append(TestResult(4007, 1, self, 'Sampling Quality: Minimum Samples seems very high.(' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.maxSamples') <= 0:
                    resultList.append(TestResult(4008, 1, self, 'Sampling Quality: Maximum Samples seems very low.(' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.maxSamples') >= 3:
                    resultList.append(TestResult(4009, 1, self, 'Sampling Quality: Maximum Samples seems very high.(' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.scanline') != 1:
                    resultList.append(TestResult(4010, 1, self, 'Rendering: Scanline is deactivated (' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.rayTracing') != 1:
                    resultList.append(TestResult(4011, 1, self, 'Rendering: Ray Tracing is deactivated (' + l + ')', False, 0))
                if cmds.getAttr('mentalrayGlobals.renderMode') != 0:
                    resultList.append(TestResult(4012, 2, self, 'Rendering: Render Mode must be set to "Normal" (' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.shadowMethod') == 0:
                    resultList.append(TestResult(4013, 1, self, 'Rendering: Shadows are deactivated (' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.diagnoseSamples') == 1 or cmds.getAttr('miDefaultOptions.diagnoseFinalg') == 1:
                    resultList.append(TestResult(4014, 1, self, 'Options: Diagnostics is activated (' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.rayTracing'):
                    if cmds.getAttr('miDefaultOptions.maxReflectionRays') >= 5:
                        resultList.append(TestResult(4015, 1, self, 'Quality: Reflection depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('miDefaultOptions.maxRefractionRays') >= 4:
                        resultList.append(TestResult(4016, 1, self, 'Quality: Refraction depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('miDefaultOptions.maxRayDepth') >= 4:
                        resultList.append(TestResult(4017, 1, self, 'Quality: Max Trace depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('miDefaultOptions.maxShadowRayDepth') >= 5:
                        resultList.append(TestResult(4018, 1, self, 'Quality: Shadow depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('miDefaultOptions.maxReflectionBlur') >= 4:
                        resultList.append(TestResult(4019, 1, self, 'Quality: Reflection blur depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('miDefaultOptions.maxReflectionBlur') >= 4:
                        resultList.append(TestResult(4020, 1, self, 'Quality: Refraction blur depth is very high.(' + l + ')', False, 0))
                if cmds.getAttr('miDefaultOptions.finalGather') == 1:
                    if cmds.getAttr('miDefaultOptions.finalGatherRebuild') == 1 or cmds.getAttr('miDefaultOptions.finalGatherRebuild') == 0 and not self.mainDialog.isSingleFrameRender():
                        if cmds.getAttr('miDefaultOptions.finalGatherFilename') != '':
                            resultList.append(TestResult(4021, 2, self, 'Indirect Lighting: FinalGather write mode activated (' + l + ')', True, self.FG_WRITE))
                        else:
                            resultList.append(TestResult(4022, 1, self, 'Indirect Lighting: FinalGather frame by frame mode activated (' + l + ')', True, self.FG_ONOFF))
                    if cmds.getAttr('miDefaultOptions.finalGatherRebuild') == 2:
                        oldFgPath = cmds.getAttr('miDefaultOptions.finalGatherFilename')
                        self.oldFgPaths.append([l, oldFgPath])
                        curfgPath = oldFgPath
                        if not existsFile(curfgPath):
                            curfgPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(rte='mentalRay'), 'finalgMap', os.path.basename(curfgPath))
                        if not existsFile(curfgPath):
                            curfgPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='mentalRay'), 'finalgMap', os.path.basename(curfgPath))
                        if not existsFile(curfgPath):
                            curfgPath = os.path.join(cmds.workspace(q=1, rd=1), 'renderData', 'mentalRay', 'finalgMap', os.path.basename(curfgPath))
                        if not existsFile(curfgPath):
                            curfgPath = os.path.join(cmds.workspace(q=1, rd=1), 'mentalRay', 'finalgMap', os.path.basename(curfgPath))
                        if not existsFile(curfgPath):
                            resultList.append(TestResult(4023, 2, self, 'Indirect Lighting: Final Gather Map "' + cmds.getAttr('miDefaultOptions.finalGatherFilename') + '" not found (' + l + ')', False, 0))
                            debuglog('Error: fgmap not found ' + curfgPath)
                        else:
                            debuglog('fgmap found ' + curfgPath)
                            self.fgPath.append([l, curfgPath])
                        if 'finalGatherMergeFiles' in cmds.listAttr('miDefaultOptions'):
                            i = 0
                            while True:
                                fgMergePath = cmds.getAttr('miDefaultOptions.finalGatherMergeFiles[%d]' % i)
                                if fgMergePath != '':
                                    self.oldFgMergePaths.append([l, fgMergePath, i])
                                    curfgPath = fgMergePath
                                    if not existsFile(curfgPath):
                                        curfgPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(rte='mentalRay'), 'finalgMap', os.path.basename(curfgPath))
                                    if not existsFile(curfgPath):
                                        curfgPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='mentalRay'), 'finalgMap', os.path.basename(curfgPath))
                                    if not existsFile(curfgPath):
                                        curfgPath = os.path.join(cmds.workspace(q=1, rd=1), 'renderData', 'mentalRay', 'finalgMap', os.path.basename(curfgPath))
                                    if not existsFile(curfgPath):
                                        curfgPath = os.path.join(cmds.workspace(q=1, rd=1), 'mentalRay', 'finalgMap', os.path.basename(curfgPath))
                                    if not existsFile(curfgPath):
                                        resultList.append(TestResult(4023, 2, self, 'Indirect Lighting: Final Gather Merge Files "' + fgMergePath + '" not found (' + l + ')', False, 0))
                                        debuglog('Error: fgmap not found ' + curfgPath)
                                    else:
                                        self.fgMergePath.append([l, curfgPath, i])
                                else:
                                    break
                                i += 1

                        if not self.mainDialog.isSingleFrameRender():
                            resultList.append(TestResult(4024, 1, self, 'Indirect Lighting: FinalGather render mode activated (' + l + ')', True, self.FG_FREEZE))
                if cmds.getAttr('miDefaultOptions.globalIllum') == 1 or cmds.getAttr('miDefaultOptions.caustics') == 1:
                    if self.mainDialog.isSingleFrameRender():
                        resultList.append(TestResult(4025, 0, self, 'For distributed render you need to bake GI/photon map first', False, 0))
                        curPhotonPath = cmds.getAttr('miDefaultOptions.photonMapFilename')
                        if not existsFile(curPhotonPath):
                            curPhotonPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(rte='mentalRay'), 'photonMap', os.path.basename(curPhotonPath))
                        if not existsFile(curPhotonPath):
                            curPhotonPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='mentalRay'), 'photonMap', os.path.basename(curPhotonPath))
                        if not existsFile(curPhotonPath):
                            resultList.append(TestResult(4026, 2, self, 'Indirect Lighting: Photon Map "' + cmds.getAttr('miDefaultOptions.photonMapFilename') + '" not found (' + l + ')', False, 0))
                            debuglog('Error: photon map not found ' + curPhotonPath)
                            curPhotonPath = ''
                        else:
                            debuglog('photon map found ' + curPhotonPath)
                            self.photonPath.append([l, curPhotonPath])
                    else:
                        if cmds.getAttr('miDefaultOptions.photonMapRebuild') == 1 and len(cmds.getAttr('miDefaultOptions.photonMapFilename')) > 0:
                            resultList.append(TestResult(4027, 2, self, 'Indirect Lighting: Phton Map Rebuild "On" with not empty filename not supported (' + l + ')', False, 0))
                        if cmds.getAttr('miDefaultOptions.photonMapRebuild') == 0 and len(cmds.getAttr('miDefaultOptions.photonMapFilename')) > 0:
                            oldPhotonPath = cmds.getAttr('miDefaultOptions.photonMapFilename')
                            self.oldPhotonPaths.append([l, oldPhotonPath])
                            curPhotonPath = oldPhotonPath
                            if not existsFile(curPhotonPath):
                                curPhotonPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(rte='mentalRay'), 'photonMap', os.path.basename(curPhotonPath))
                            if not existsFile(curPhotonPath):
                                curPhotonPath = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='mentalRay'), 'photonMap', os.path.basename(curPhotonPath))
                            if not existsFile(curPhotonPath):
                                resultList.append(TestResult(4028, 2, self, 'Indirect Lighting: Photon Map "' + cmds.getAttr('miDefaultOptions.photonMapFilename') + '" not found (' + l + ')', False, 0))
                                debuglog('Error: photon map not found ' + curPhotonPath)
                                curPhotonPath = ''
                            else:
                                debuglog('photon map found ' + curPhotonPath)
                                self.photonPath.append([l, curPhotonPath])
                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))
            else:
                bOthersFound = True

        if bMRFound and bOthersFound:
            resultList.append(TestResult(4029, 2, self, 'Mental Ray render-layers mixed with others', True, self.LAYERSMIXED))

    def furtherAction(self, result):
        st = ''
        if result.flagMoreInfos:
            if result.type == self.FG_FREEZE:
                st = 'This mode reads the Final Gather from file only and will NOT calculate Final Gather\r\npoints during the render progress.\r\nTo creat a FG map on your computer you MUST have a static scene!\r\nA static scene include NO animated or moving objects, lights and textures.\r\n! the camera is the only moving part.\r\n-set frame range you need\r\n-set anti alising to lowest possible level to speed up render\r\n-set frame step to render to 5 or higher depending on camera speed\r\n-set FG mode to "rebuild on"\r\n-specify FG map name\r\n-hit render\r\nyou will notice the FG map is growing as more frames are calculated\r\nif render is done set FG mode to "Freeze"\r\nNote: if your scene is non-static set the FG mode to "rebuild on" and run plugin again'
            if result.type == self.FG_ONOFF:
                st = 'This mode re-calculate the Final Gather solution each frame and is used for non-static scenens only!\r\nA non-static scene include animated or moving objects, lights or textures.\r\n!Attention - due to the re-calculation the FG solution is different from frame to frame and \r\ncan cause a "flicker" the final output!\r\nTo remove flicker you could higher the FG settings without guarantee of flicker free output'
            if result.type == self.FG_WRITE:
                st = 'This mode write the Final Gather solution to file and is used for static scenes only !\r\nA static scene include NO animated or moving objects, lights and textures.\r\n! the camera is the only moving part.\r\n-set frame range you need\r\n-set anti alising to lowest possible level to speed up render\r\n-set frame step to render to 5 or higher depending on camera speed\r\n-set FG mode to "rebuild on"\r\n-specify FG map name\r\n-hit render\r\nyou will notice the FG map is growing as more frames are calculated\r\nif render is done set FG mode to "Freeze"\r\nNote: if your scene is non-static remove the FG map name and run plugin again'
            if result.type == self.LAYERSMIXED:
                st = 'Due to rendering restrictions you can not have multiple render layers that mix "mental ray" and other renderers.\r\nPlease send two jobs to the farm. One including only "mental ray"-layers, and one with the remaining layers.'
            if st != '':
                cmds.confirmDialog(title='Message', message=st, button='Ok')
            elif result.type == self.MI_STANDALONE:
                if cmds.confirmDialog(title='Message', message='Do you want to render with mental ray Standalone?', button=('Yes', 'No')) == 'Yes':
                    self.miExport = True
                else:
                    self.miExport = False
                return True

    def prepareSave(self, path, vecFiles):
        if not cmds.objExists('miDefaultOptions'):
            return ''
        settingsToWrite = ''
        destfolder = os.path.join(path, 'tex')
        workspacefolder = os.path.join(destfolder, 'maya')
        fgMapFolder = os.path.join(workspacefolder, 'renderData', 'mentalRay', 'finalgMap')
        photonMapFolder = os.path.join(workspacefolder, 'renderData', 'mentalRay', 'photonMap')
        serverFgMapFolder = createPath(self.mainDialog.m_userName, 'tex\\maya\\renderData\\mentalRay\\finalgMap\\')
        serverPhotonMapFolder = createPath(self.mainDialog.m_userName, 'tex\\maya\\renderData\\mentalRay\\photonMap\\')
        for fgPath in self.fgPath:
            if fgPath[1] != '' and existsFile(fgPath[1]):
                try:
                    cmds.editRenderLayerGlobals(currentRenderLayer=fgPath[0])
                    if cmds.getAttr('miDefaultOptions.finalGather') == 1 and cmds.getAttr('miDefaultOptions.finalGatherRebuild') == 2:
                        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/finalgMap/' + os.path.basename(fgPath[1]), fgPath[1])
                        newpath = serverFgMapFolder + os.path.basename(fgPath[1])
                        cmds.setAttr('miDefaultOptions.finalGatherFilename', newpath, type='string')
                except:
                    continue

        for fgMergePath in self.fgMergePath:
            print fgMergePath
            if fgMergePath[1] != '' and existsFile(fgMergePath[1]):
                try:
                    cmds.editRenderLayerGlobals(currentRenderLayer=fgMergePath[0])
                    if cmds.getAttr('miDefaultOptions.finalGather') == 1 and cmds.getAttr('miDefaultOptions.finalGatherRebuild') == 2:
                        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/finalgMap/' + os.path.basename(fgMergePath[1]), fgMergePath[1])
                        newpath = serverFgMapFolder + os.path.basename(fgMergePath[1])
                        cmds.setAttr('miDefaultOptions.finalGatherMergeFiles[%d]' % fgMergePath[2], newpath, type='string')
                except:
                    continue

        for photonPath in self.photonPath:
            if len(photonPath[1]) > 0 and existsFile(photonPath[1]):
                try:
                    cmds.editRenderLayerGlobals(currentRenderLayer=photonPath[0])
                    appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/photonMap/' + os.path.basename(photonPath[1]), photonPath[1])
                    cmds.setAttr('miDefaultOptions.photonMapFilename', serverPhotonMapFolder + os.path.basename(photonPath[1]), type='string')
                except:
                    continue

        if self.mainDialog.isSingleFrameRender():
            oldRenderLayer = cmds.editRenderLayerGlobals(currentRenderLayer=1, q=1)
            renderLayers = cmds.ls(type='renderLayer')
            curRend = ''
            for r in renderLayers:
                if cmds.getAttr(r + '.renderable') == 1:
                    try:
                        cmds.editRenderLayerGlobals(currentRenderLayer=r)
                        curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
                    except:
                        continue

            width = cmds.getAttr('defaultResolution.width')
            height = cmds.getAttr('defaultResolution.height')
            if curRend in self.getIdentifier():
                settingsToWrite += 'singleframeMayaMental2=1\r\n'
                settingsToWrite += 'resolution=' + str(width) + 'x' + str(height) + '\r\n'
                fgenabled = 'fgenabled=0\r\n'
                if cmds.getAttr('miDefaultOptions.finalGather'):
                    fgenabled = 'fgenabled=1\r\n'
                settingsToWrite += fgenabled
                freeze = '0'
                if cmds.getAttr('miDefaultOptions.finalGatherRebuild') == 2:
                    freeze = '1'
                settingsToWrite += 'fgfreeze=' + freeze + '\r\n'
            cmds.editRenderLayerGlobals(currentRenderLayer=oldRenderLayer)
        try:
            size = cmds.getAttr('miDefaultOptions.stringOptions', size=1)
            for i in range(size):
                if cmds.getAttr('miDefaultOptions.stringOptions[' + str(i) + '].name') == 'finalgather mode' and cmds.getAttr('miDefaultOptions.stringOptions[' + str(i) + '].value') == 'auto':
                    cmds.setAttr('miDefaultOptions.stringOptions[' + str(i) + '].value', 'automatic', type='string')
                if cmds.getAttr('miDefaultOptions.stringOptions[' + str(i) + '].name') == 'irradiance particles file':
                    path = cmds.getAttr('miDefaultOptions.stringOptions[' + str(i) + '].value')
                    if existsFile(path):
                        debuglog('copying ' + path + ' to ' + photonMapFolder)
                        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/photonMap/' + os.path.basename(path), path)
                        cmds.setAttr('miDefaultOptions.stringOptions[' + str(i) + '].value', serverPhotonMapFolder + os.path.basename(path), type='string')
                    else:
                        debuglog('irradiance particle file not found ' + mstr(path))
                if cmds.getAttr('miDefaultOptions.stringOptions[' + str(i) + '].name') == 'gi gpu devices':
                    cmds.setAttr('miDefaultOptions.stringOptions[' + str(i) + '].value', '0', type='string')

            lightshapes = cmds.ls(type='areaLight')
            for l in lightshapes:
                if cmds.attributeQuery('miLightShader', node=l, exists=1):
                    shader = cmds.connectionInfo(l + '.miLightShader', sfd=True)
                    if len(shader) > 0:
                        shader = shader[:shader.find('.')]
                        if cmds.getAttr(shader + '.on'):
                            cmds.setAttr(l + '.areaVisible', True)

        except:
            pass

        return settingsToWrite

    def postSave(self):
        for fgPath in self.oldFgPaths:
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=fgPath[0])
                cmds.setAttr('miDefaultOptions.finalGatherFilename', fgPath[1], type='string')
            except:
                continue

        for fgPath in self.oldFgMergePaths:
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=fgPath[0])
                cmds.setAttr('miDefaultOptions.finalGatherMergeFiles[%d]' % fgPath[2], fgPath[1], type='string')
            except:
                continue

        for photonPath in self.oldPhotonPaths:
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=photonPath[0])
                cmds.setAttr('miDefaultOptions.photonMapFilename', photonPath[1], type='string')
            except:
                continue
