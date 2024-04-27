import maya.cmds as cmds
import shutil
import sys
import math
import glob
import tempfile
import time 

import validator
from validator import *
import utilitis
from utilitis import *
 

def getVrayVersion():
    return float(cmds.vray('version')[:4])


class ValVray(Validator):
    GI_PHOTON_MAP_NEW = 1
    GI_PHOTON_MAP_FILE = 2
    GI_LIGHTCACHE_SINGLE = 3
    GI_LIGHTCACHE_PATH = 4
    GI_LIGHTCACHE_FLY = 5
    GI_IRRADIANCE_SINGLE = 6
    GI_IRRADIANCE_MULTI = 7
    GI_IRRADIANCE_BUCKET = 8
    CAUSTICS_NEW_MAP = 9
    CAUSTICS_FROM_FILE = 10
    INTERPOLATION_MAT = 11
    GI_LIGHTCACHE_DISTRIBUTED = 12
    GI_IRRADIANCE_DISTRIBUTED = 13
    INTERPOLATION_MAT_SINGLE = 14
    GI_IRRADIANCE_PREPASS = 15
    GI_IRRADIANCE_ANIMRENDER = 16
    VRAY_STANDALONE = 17
    GPU_DIALOG = 18
    GpuCpu = ''
    toRetarget = []
    vrsceneExport = False
    vrsceneTemp = ''
    vrsceneCheckResult = []
    originalMats = []
    replacedMats = []

    def getName(self):
        return 'VRay'

    def getIdentifier(self):
        return ['vray', 'vrayrt']

    def exportVrscene(self, vrscenePath, startframe, endframe):
        vrscenePathAfterExport = vrscenePath
        layerName = ''
        renderLayers = cmds.ls(type='renderLayer')
        if len(renderLayers) > 1:
            layerName = cmds.editRenderLayerGlobals(query=True, currentRenderLayer=True)
            if layerName == 'defaultRenderLayer':
                layerName = 'masterLayer'
            vrscenePathAfterExport = vrscenePath[:-len('.vrscene')] + '_' + layerName + '.vrscene'
        res = False
        if existsFile(vrscenePathAfterExport):
            os.remove(vrscenePathAfterExport)
        cmds.setAttr('vraySettings.vrscene_render_on', 0)
        cmds.setAttr('vraySettings.vrscene_on', 1)
        cmds.setAttr('vraySettings.vrscene_filename', vrscenePath, type='string')
        cmds.setAttr('vraySettings.misc_eachFrameInFile', 0)
        cmds.setAttr('vraySettings.misc_meshAsHex', 1)
        cmds.setAttr('vraySettings.misc_transformAsHex', 1)
        cmds.setAttr('vraySettings.misc_compressedVrscene', 1)
        cmds.setAttr('vraySettings.animBatchOnly', 0)
        cmds.setAttr('defaultRenderGlobals.startFrame', startframe)
        cmds.setAttr('defaultRenderGlobals.endFrame', endframe)
        if cmds.attributeQuery('animType', node='vraySettings', exists=1):
            cmds.setAttr('vraySettings.animType', 1)
        else:
            cmds.setAttr('defaultRenderGlobals.animation', 1)
        print vrscenePath
        print vrscenePathAfterExport
        camFound = False
        cams = cmds.listCameras()
        for c in cams:
            if cmds.getAttr(c + '.renderable') == 1:
                camFound = True
                cmds.vrend(w=20, h=20, camera=c)
                break

        if not camFound:
            print 'Error: no renderable camera given in vray settings'
        cmds.setAttr('vraySettings.vrscene_render_on', 1)
        cmds.setAttr('vraySettings.vrscene_on', 0)
        print 'looking for: ' + vrscenePath + ' or ' + vrscenePathAfterExport
        foundPath = ''
        if existsFile(vrscenePath):
            foundPath = vrscenePath
            res = True
        if existsFile(vrscenePathAfterExport):
            foundPath = vrscenePathAfterExport
            res = True
        return (res, foundPath)

    def checkVrscene(self, vrscenePath, vrsceneparser):
        keyval = []
        searchPaths = []
        searchPaths.append(cmds.workspace(q=1, rd=1))
        searchPaths.append(os.environ['MAYA_LOCATION'])
        stSearchPaths = ''
        for f in searchPaths:
            stSearchPaths = stSearchPaths + ' -s "' + f + '"'

        args = vrsceneparser + ' passX4f -i "' + vrscenePath + '" ' + stSearchPaths + ' -t check'
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
                    debuglog('vrsceneparser split invalid: ' + line)
                    return None
            except:
                debuglog('invalid vrsceneparser line: ' + line)
                return None

        return keyval

    def changeVrscene(self, vrscenePath, vrsceneparser, texPath, outPath):
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

        args = vrsceneparser + ' passX4f -i "' + vrscenePath + '" ' + stSearchPaths + ' -t change -ro "' + outPath + '" -rt "' + texPath + '"' + stChange
        output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    def replaceMat(self, oldMat, newMat):
        print 'Replacing ' + str(oldMat) + ' with ' + str(newMat)
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
            if curRend == self.getIdentifier()[0]:
                if self.vrsceneExport:
                    self.mainDialog.isVrsceneExport = True
                    break

    def standaloneExport(self, resultList, fPath, vecFiles):
        settingsToWrite = ''
        if self.mainDialog.isVrsceneExport:
            vrVersion = cmds.pluginInfo('vrayformaya', v=True, q=True)
            vrDecimal = 'punkt'
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
                    vrsceneCheckResult = []
                    allValid = True
                    vrparser = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'vray')
                    vrparser = os.path.join(vrparser, 'vrayparser' if cmds.about(mac=1) else 'vrayparser.exe')
                    if existsFile(vrparser):
                        vrsceneTemp = os.path.join(tempfile.gettempdir(), str(time.time()) + '.vrscene')
                        startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                        endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                        framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                        self.originalMats = []
                        self.replacedMats = []
                        self.replaceMaterials()
                        exportResult = self.exportVrscene(vrsceneTemp, startFrame, endFrame)
                        vrsceneTemp = exportResult[1]
                        if exportResult[0]:
                            vrsceneCheckResult = []
                            keyval = self.checkVrscene(vrsceneTemp, vrparser)
                            if keyval != None:
                                for chkRes in keyval:
                                    key = chkRes[0]
                                    val = chkRes[1]
                                    if key == 'err':
                                        resultList.append(TestResult(7070, 2, self, 'Vrscene: ' + val, False, 0))
                                        allValid = False
                                    else:
                                        vrsceneCheckResult.append(chkRes)

                            else:
                                resultList.append(TestResult(7070, 2, self, 'Unknown error checking vrscene', False, 0))
                                allValid = False
                        else:
                            resultList.append(TestResult(7070, 2, self, 'Scene could not be exported to .vrscene', False, 0))
                            allValid = False
                        self.restoreMats()
                    else:
                        resultList.append(TestResult(7070, 2, self, 'Please install the Vray plugin in the Render Farm Application settings', False, 0))
                        allValid = False
                    if allValid:
                        texPath = createPath(self.mainDialog.m_userName, 'tex').replace('\\', '/')
                        outPath = createOutPath(self.mainDialog.m_userName).replace('\\', '/')
                        self.changeVrscene(vrsceneTemp, vrparser, texPath, outPath)
                        dest = (fPath + '/tex/' + getChangedMayaFilename() + '.0000.vrscene').replace('\\', '/')
                        if existsFile(dest):
                            os.remove(dest)
                        os.rename(vrsceneTemp, dest)
                        appendFileInfo(vecFiles, 'tex/' + os.path.basename(dest), dest, -1, False)
                        for chkRes in vrsceneCheckResult:
                            key = chkRes[0]
                            val = chkRes[1]
                            if key == 'texfound' or key == 'vrmeshfound' or key == 'includefound':
                                appendFileInfo(vecFiles, 'tex/' + os.path.basename(val), val)

                        settingsToWrite += 'singleVrayFile=1\n'

        return settingsToWrite

    def findIrrFiles(self):
        irrpath = cmds.getAttr('vraySettings.imap_fileName')
        irrFiles = []
        if irrpath != None and len(irrpath) > 6 and irrpath.endswith('.vrmap'):
            for f in glob.glob(os.path.dirname(irrpath) + '/*.vrmap'):
                irrFiles.append(f)

        return irrFiles

    def test(self, resultList, fastCheck, layerinfos):
        self.giFile = ''
        renderLayers = cmds.ls(type='renderLayer')
        cntRenderables = 0
        for r in renderLayers:
            if cmds.getAttr(r + '.renderable') == 1:
                cntRenderables += 1

        if self.mainDialog.isSingleFrameRender() and cntRenderables > 1:
            resultList.append(TestResult(7062, 2, self, 'You may only have one enabled layer if you render a single frame', False, 0))
        bVRFound = False
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
            if curRend == self.getIdentifier()[0]:
                vrayversion = getVrayVersion()
                if vrayversion < 2.2:
                    resultList.append(TestResult(7001, 2, self, 'You need at least VRay 2.2 for rendering', False, 0))
                if not cmds.getAttr('vraySettings.fileNamePrefix'):
                    resultList.append(TestResult(5013, 2, self, 'Vray-Rendersettings: Please provide a filename to render at Render Farm Application', False, 0))
                bVRFound = True
                if cmds.attributeQuery('productionEngine', node='vraySettings', exists=1):
                    if cmds.getAttr('vraySettings.productionEngine') in (1, 2):
                        self.mainDialog.gpu_enabled = True
                        resultList.append(TestResult(8015, 0, self, 'Your job will be rendered on GPU', False, 0))
                    elif cmds.getAttr('vraySettings.productionEngine') in (3,):
                        self.mainDialog.gpu_enabled = True
                        self.mainDialog.rtx_enabled = True
                        resultList.append(TestResult(8015, 0, self, 'Your job will be rendered on RTX GPU', False, 0))
                    else:
                        resultList.append(TestResult(8015, 0, self, 'Your job will be rendered on CPU', False, 0))
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                vraytype = 'VrayRTX' if self.mainDialog.gpu_enabled == True else 'Vray'
                vraytype += ('GPU' if self.mainDialog.gpu_enabled == True else '') + str(vrayversion)
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, vraytype))
                if framestep < 1:
                    resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                if not cmds.objExists('vraySettings'):
                    continue
                if not cmds.attributeQuery('animation', node='vraySettings', exists=1):
                    resultList.append(TestResult(7002, 2, self, 'VRay Settings could not be found.(' + l + ')', False, 0))
                    continue
                if cmds.attributeQuery('animType', node='vraySettings', exists=1):
                    if cmds.getAttr('vraySettings.animType') == 2:
                        resultList.append(TestResult(7063, 2, self, 'Animation: "Specific Frames" not supported, please set to "Standard"', False, 0))
                if self.mainDialog.isSingleFrameRender():
                    imageFormat = cmds.getAttr('vraySettings.imageFormatStr')
                    if not isAllowedSingleFrameFormatVray(imageFormat):
                        resultList.append(TestResult(7063, 2, self, 'Rendering: Image Format not allowed for single frame Rendering. Use .png instead', False, 0))
                if not cmds.getAttr('vraySettings.globopt_light_doLights'):
                    resultList.append(TestResult(7006, 1, self, 'VRay: Lights are disabled (' + l + ')', False, 0))
                if not cmds.getAttr('vraySettings.globopt_light_doShadows'):
                    resultList.append(TestResult(7007, 1, self, 'VRay: Shadows are disabled (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.globopt_light_onlyGI'):
                    resultList.append(TestResult(7008, 1, self, 'VRay: Show GI only active (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.globopt_gi_dontRenderImage'):
                    resultList.append(TestResult(7009, 2, self, "VRay: Don't render Final image active (" + l + ')', False, 0))
                if cmds.getAttr('vraySettings.globopt_mtl_limitDepth'):
                    if cmds.getAttr('vraySettings.globopt_mtl_maxDepth') <= 14:
                        resultList.append(TestResult(7010, 1, self, 'VRay: maximum depth very low (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.globopt_mtl_maxDepth') >= 76:
                        resultList.append(TestResult(7011, 1, self, 'VRay: maximum depth very high (' + l + ')', False, 0))
                if not cmds.getAttr('vraySettings.globopt_mtl_doMaps'):
                    resultList.append(TestResult(7012, 1, self, 'VRay: No maps during render active (' + l + ')', False, 0))
                sampletype = cmds.getAttr('vraySettings.samplerType')
                if sampletype == 0:
                    if cmds.getAttr('vraySettings.fixedSubdivs') <= 1:
                        resultList.append(TestResult(7013, 1, self, 'VRay: Image sampler seems very low (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.fixedSubdivs') >= 4:
                        resultList.append(TestResult(7014, 1, self, 'VRay: Image sampler seems very high (' + l + ')', False, 0))
                if sampletype == 1:
                    if cmds.getAttr('vraySettings.dmcMinSubdivs') >= 4 or cmds.getAttr('vraySettings.dmcMaxSubdivs') >= 8:
                        resultList.append(TestResult(7015, 1, self, 'VRay: Image sampler seems very high (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.dmcMinSubdivs') > cmds.getAttr('vraySettings.dmcMaxSubdivs'):
                        resultList.append(TestResult(7016, 2, self, 'VRay: Image sampler Min is bigger than Max (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.dmcShowSamples'):
                        resultList.append(TestResult(7017, 1, self, 'VRay: Image sampler Show samples active (' + l + ')', False, 0))
                if sampletype == 2:
                    if cmds.getAttr('vraySettings.subdivMinRate') < -1:
                        resultList.append(TestResult(7018, 1, self, 'VRay: Image sampler seems very low (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.subdivMaxRate') > 5:
                        resultList.append(TestResult(7019, 1, self, 'VRay: Image sampler seems very high (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.subdivMinRate') > cmds.getAttr('vraySettings.subdivMaxRate'):
                        resultList.append(TestResult(7020, 2, self, 'VRay: Image sampler Min is bigger than Max (' + l + ')', False, 0))
                frmt = cmds.getAttr('vraySettings.imageFormatStr')
                if frmt in ('exr (multichannel)', 'exr'):
                    if cmds.getAttr('vraySettings.imgOpt_exr_compression') == 1:
                        resultList.append(TestResult(7020, 2, self, 'VRay: Please activate compression for your Exr output (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.giOn'):
                    if cmds.getAttr('vraySettings.primaryEngine') == 1 or cmds.getAttr('vraySettings.secondaryEngine') == 1:
                        if cmds.getAttr('vraySettings.pmap_mode') == 0:
                            if self.mainDialog.isSingleFrameRender():
                                resultList.append(TestResult(7021, 2, self, 'GI engine Photon map: For Distributed Render, Photon map must be rendered to file first.(' + l + ')', False, 0))
                            else:
                                resultList.append(TestResult(7022, 1, self, 'GI engine Photon map: Attention, map mode is set to "new map" (' + l + ')', True, self.GI_PHOTON_MAP_NEW))
                                if cmds.getAttr('vraySettings.pmap_autoSave') == True:
                                    resultList.append(TestResult(7023, 2, self, 'GI engine Photon map: Auto save not supported (' + l + ')', False, 0))
                                if cmds.getAttr('vraySettings.pmap_file') != None and cmds.getAttr('vraySettings.pmap_file') != '':
                                    resultList.append(TestResult(7024, 2, self, 'GI engine Photon map: Please clear "New map" File property (' + l + ')', False, 0))
                        if cmds.getAttr('vraySettings.pmap_mode') == 1:
                            resultList.append(TestResult(7025, 1, self, 'GI engine Photon map: Attention, map mode is set to "from file" (' + l + ')', True, self.GI_PHOTON_MAP_FILE))
                            if existsFile(cmds.getAttr('vraySettings.pmap_file')) == False:
                                resultList.append(TestResult(7026, 2, self, 'GI engine Photon Map: Can not find Photon Map file (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.primaryEngine') == 3 or cmds.getAttr('vraySettings.secondaryEngine') == 3:
                        if self.mainDialog.isSingleFrameRender():
                            if not (cmds.getAttr('vraySettings.mode') == 0 and cmds.getAttr('vraySettings.autoSave') == False or cmds.getAttr('vraySettings.mode') == 2 and existsFile(cmds.getAttr('vraySettings.fileName')) == True):
                                resultList.append(TestResult(7064, 2, self, 'GI engine Lightcache: For Distributed Render, set mode to "Single frame" (' + l + ')', True, self.GI_LIGHTCACHE_DISTRIBUTED))
                            recommendedSubdiv = math.sqrt(cmds.getAttr('vraySettings.wi') * cmds.getAttr('vraySettings.he')) / 2.0
                            if cmds.getAttr('vraySettings.subdivs') < 0.85 * recommendedSubdiv or cmds.getAttr('vraySettings.subdivs') > 1.15 * recommendedSubdiv:
                                resultList.append(TestResult(7065, 1, self, 'GI engine Lightcache: Recommended Lightcache subdivision is ' + str(int(recommendedSubdiv)) + ' (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.autoSave') == True:
                                resultList.append(TestResult(7066, 2, self, 'GI engine Lightcache: Please disable Autosave for singleframe rendering. (' + l + ')', False, 0))
                        else:
                            if cmds.getAttr('vraySettings.mode') == 0:
                                resultList.append(TestResult(7027, 1, self, 'GI engine Lightcache: Attention, map mode is set to "single frame" (' + l + ')', True, self.GI_LIGHTCACHE_SINGLE))
                                if cmds.getAttr('vraySettings.autoSave') == True:
                                    resultList.append(TestResult(7028, 2, self, 'GI engine Lightcache: Auto save not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.mode') == 1:
                                resultList.append(TestResult(7029, 2, self, 'GI engine Lightcache: Attention, map mode "Fly through" not supported (' + l + ')', True, self.GI_LIGHTCACHE_FLY))
                                if cmds.getAttr('vraySettings.autoSave') == True:
                                    resultList.append(TestResult(7030, 2, self, 'GI engine Lightcache: Auto save not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.mode') == 2:
                                if existsFile(cmds.getAttr('vraySettings.fileName')) == False:
                                    resultList.append(TestResult(7031, 2, self, 'GI engine Lightcache: Can not find Light cache file (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.mode') == 3:
                                resultList.append(TestResult(7032, 1, self, 'GI engine Lightcache: Attention, map mode is set to "path tracing" (' + l + ')', True, self.GI_LIGHTCACHE_PATH))
                                if cmds.getAttr('vraySettings.autoSave') == True:
                                    resultList.append(TestResult(7033, 2, self, 'GI engine Lightcache: Auto save not supported (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.primaryEngine') == 0:
                        if cmds.getAttr('vraySettings.imap_maxRate') >= 1:
                            resultList.append(TestResult(7034, 1, self, 'GI engine Irradiance: Max rate seems to be very high (' + l + ')', False, 0))
                        if cmds.getAttr('vraySettings.imap_detailEnhancement') == True:
                            resultList.append(TestResult(7035, 1, self, 'GI engine Irradiance: Detail enhancement is active (' + l + ')', False, 0))
                        if self.mainDialog.isSingleFrameRender():
                            if not (cmds.getAttr('vraySettings.imap_mode') == 0 and cmds.getAttr('vraySettings.imap_autoSave') == False or cmds.getAttr('vraySettings.imap_mode') == 2 and existsFile(cmds.getAttr('vraySettings.imap_fileName')) == True):
                                resultList.append(TestResult(7067, 2, self, 'GI engine Irradiance: For Distributed Render, set mode to "Single frame" (' + l + ')', True, self.GI_IRRADIANCE_DISTRIBUTED))
                            if cmds.getAttr('vraySettings.imap_currentPreset') > 4:
                                resultList.append(TestResult(7068, 1, self, 'GI engine Irradiance: Irradiance preset will produce a giant irradiance map and can increase rendertime !!! (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_autoSave') == True:
                                resultList.append(TestResult(7069, 2, self, 'GI engine Irradiance: Please disable Autosave for singleframe rendering. (' + l + ')', False, 0))
                        else:
                            if cmds.getAttr('vraySettings.imap_mode') == 0:
                                resultList.append(TestResult(7036, 1, self, 'GI engine Irradiance: Attention, map mode is set to "single frame" (' + l + ')', True, self.GI_IRRADIANCE_SINGLE))
                                if cmds.getAttr('vraySettings.imap_autoSave') == True:
                                    resultList.append(TestResult(7037, 2, self, 'GI engine Irradiance: Auto save not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 1:
                                resultList.append(TestResult(7038, 2, self, 'GI engine Irradiance: Attention, Mode Multiframe Incremantal is used (' + l + ')', True, self.GI_IRRADIANCE_MULTI))
                                if cmds.getAttr('vraySettings.imap_autoSave') == True:
                                    resultList.append(TestResult(7039, 2, self, 'GI engine Irradiance: Auto save not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 2:
                                if existsFile(cmds.getAttr('vraySettings.imap_fileName')) == False:
                                    resultList.append(TestResult(7040, 2, self, 'GI engine Irradiance: Can not find file (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 3:
                                resultList.append(TestResult(7041, 2, self, 'GI engine Irradiance: Add to current map not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 4:
                                resultList.append(TestResult(7042, 2, self, 'GI engine Irradiance: Incremental add to current map not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 5:
                                resultList.append(TestResult(7043, 1, self, 'GI engine Irradiance: Bucket mode (' + l + ')', True, self.GI_IRRADIANCE_BUCKET))
                                if cmds.getAttr('vraySettings.imap_autoSave') == True:
                                    resultList.append(TestResult(7044, 2, self, 'GI engine Irradiance: Auto save not supported (' + l + ')', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 6:
                                resultList.append(TestResult(7045, 1, self, 'GI engine Irradiance: GI mode "Animation prepass" is used (' + l + ')', True, self.GI_IRRADIANCE_PREPASS))
                                if farmWin.farmWin.estimateEnabled:
                                    resultList.append(TestResult(7045, 2, self, 'Common: estimating Animation prepass rendering currently not possible', False, 0))
                            if cmds.getAttr('vraySettings.imap_mode') == 7:
                                irrFiles = self.findIrrFiles()
                                if len(irrFiles) == 0:
                                    resultList.append(TestResult(7047, 2, self, 'GI engine Irradiance: No vrmap files found (' + l + ')', True, self.GI_IRRADIANCE_ANIMRENDER))
                                else:
                                    missingMaps = []
                                    for i in range(int(startFrame), int(endFrame) + 1):
                                        bFound = False
                                        for f in irrFiles:
                                            if f.find(str(i)) >= 0:
                                                bFound = True

                                        if not bFound:
                                            missingMaps.append(i)

                                    for i in missingMaps:
                                        resultList.append(TestResult(7047, 2, self, 'GI engine Irradiance: IRR file for frame ' + str(i) + ' not found (' + l + ')', False, self.GI_IRRADIANCE_ANIMRENDER))

                if cmds.getAttr('vraySettings.causticsOn') == True:
                    if cmds.getAttr('vraySettings.causticsMode ') == 0:
                        if self.mainDialog.isSingleFrameRender():
                            resultList.append(TestResult(7048, 2, self, 'Caustics: Map mode "new map" is not supported for single frame rendering.', False, 0))
                        else:
                            resultList.append(TestResult(7049, 1, self, 'Caustics: Attention, recompute mode is set to "new map" (' + l + ')', True, self.CAUSTICS_NEW_MAP))
                        if cmds.getAttr('vraySettings.causticsAutoSave') == True:
                            resultList.append(TestResult(7050, 2, self, 'Caustics: Auto save not supported (' + l + ')', False, 0))
                    if cmds.getAttr('vraySettings.causticsMode ') == 1:
                        if not self.mainDialog.isSingleFrameRender():
                            resultList.append(TestResult(7051, 1, self, 'Caustics: Attention, recompute mode is set to "from file" (' + l + ')', True, self.CAUSTICS_FROM_FILE))
                        causticsFile = cmds.getAttr('vraySettings.causticsFile')
                        if causticsFile == None:
                            causticsFile = ''
                        if existsFile(causticsFile) == False:
                            resultList.append(TestResult(7052, 2, self, 'Caustics: Can not find file "' + causticsFile + '" (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.dmcs_timeDependent'):
                    resultList.append(TestResult(7053, 1, self, 'Settings: To get identical image noise Time Dependent(Animated noise pattern(Vray render Settings)) should be disabled (' + l + ') ', False, 0))
                if cmds.getAttr('vraySettings.dmcs_adaptiveMinSamples') >= 17:
                    resultList.append(TestResult(7054, 1, self, 'Settings: Minimum Samples very high (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.dmcs_subdivsMult') > 1:
                    resultList.append(TestResult(7055, 1, self, 'Settings: Subdivision Mulitplier higher 1 can increase rendertime a lot (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.sys_regsgen_xc') <= 15 or cmds.getAttr('vraySettings.sys_regsgen_yc') <= 15:
                    resultList.append(TestResult(7056, 1, self, 'Settings: Buckets size is very small and can increase rendertime (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.sys_regsgen_xc') <= 7 or cmds.getAttr('vraySettings.sys_regsgen_yc') <= 7:
                    resultList.append(TestResult(7057, 2, self, 'Settings: Buckets size is to small (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.sys_regsgen_xc') >= 127 or cmds.getAttr('vraySettings.sys_regsgen_yc') >= 127:
                    resultList.append(TestResult(7058, 1, self, 'Settings: Buckets size is very big and can increase rendertime (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.sys_distributed_rendering_on'):
                    resultList.append(TestResult(7059, 2, self, 'Settings: Distributed render needs to be disabled (' + l + ')', False, 0))
                if cmds.getAttr('vraySettings.vrscene_on'):
                    resultList.append(TestResult(7060, 2, self, 'Translator: Export to .vrscene file not supported (' + l + ')', False, 0))
                vraymeshfiles = []
                try:
                    vraymeshfiles = cmds.ls(et=['VRayMesh', 'VRayProxy'])
                    if vraymeshfiles == None:
                        vraymeshfiles = []
                except:
                    debuglog('Unexpected error:' + str(sys.exc_info()))
                    vraymeshfiles = []

                for f in vraymeshfiles:
                    if cmds.objExists(f + '.fileName'):
                        a = cmds.getAttr(f + '.fileName')
                        if a != '':
                            if not a.endswith('vrmesh') and not a.endswith('abc'):
                                resultList.append(TestResult(7061, 2, self, 'VRayProxy: File extension must be ".vrmesh" or ".abc": "' + a + '" (' + l + ')', False, 0))

                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))

        return

    def furtherAction(self, result):
        st = ''
        if result.flagMoreInfos:
            if result.type == self.GI_PHOTON_MAP_NEW:
                st = 'Map mode "new map" is used for non static scenes only !\nA non static scene include animated objects, morphing objects, animated lights or textures\nAttention, that recomputing mode force the renderer to redo the Photon map solution each frame\nthat causes different solutions in each frame and can produce a flickering in the final output\nto reduce flickering you could increase the settings but that rise the rendertime per image without guarantee of flickerfree output\nNote: refer map mode "from file" for static scene rendering'
            if result.type == self.GI_PHOTON_MAP_FILE:
                st = 'Map mode "from file" force Vray to read the caustic information from file\nVray will NOT compute the Photon map solution during the render process.\nTo create a Photon map file on your computer you MUST have a static scene\nA static scene have no animated objects, no morphing objects, no animated lights or textures\n! the camera is the only moving part\n-go Vray options and hit "dont render final image"\n-set one frame to render\n-check "auto save" and specify a save path\n-hit render\n-on renderend load Photon map from file\n-switch back "dont render final image"'
            if result.type == self.GI_LIGHTCACHE_SINGLE:
                st = 'Map mode "single frame" is used for non static scenes only !\nA non static scene include animated objects, morphing objects, animated lights or textures\nAttention, that mode force Vray to redo the Light map solution each frame\nthat causes different solutions in each frame and can produce a flickering in the final output\nto reduce flickering you could increase the settings but that rise the rendertime per image without guarantee of flickerfree output\nNote: A flickerfree animation can be generated by using Bute Force with the disadvantage of high rendertime per image'
            if result.type == self.GI_LIGHTCACHE_PATH:
                st = 'Map mode "pathtracing" will refine the image during the render until all subdivisions are done\nthat mode can produce rendertimes of several hours per image'
            if result.type == self.GI_LIGHTCACHE_FLY:
                st = 'That mode is used to render the Light solution to file\nTo create a Light cache file on your computer you MUST have a static scene otherwise you must use "single frame" mode\nA static scene include no animated objects, no morphing objects, no animated lights or textures\n! the camera is the only moving part\n-go vray options and hit "dont render final image"\n-set frame range you need\n-check "auto save" and specify a save path\n-hit render\n-on renderend set Lightcache "from file" and load map\n-switch back "dont render final image"'
            if result.type == self.GI_IRRADIANCE_SINGLE:
                st = 'Map mode "single frame" is used for non static scenes only !\nA non static scene include animated objects, morphing objects, animated lights or textures\nAttention, that mode force Vray to redo the Irridiance map solution each frame\nthat causes different solutions in each frame and can produce a flickering in the final output\nto reduce flickering you could increase the settings but that rise the rendertime per image without guarantee of flickerfree output\nNote: A flickerfree animation can be generated by using Bute Force with the disadvantage of high rendertime per image'
            if result.type == self.GI_IRRADIANCE_MULTI:
                st = 'Multiframe Incremantal is used to render the Irridiance map solution to file\nTo create an Irridiance map file on your computer you MUST have a static scene\nA static scene include no animated objects, no morphing objects, no animated lights or textures\n! the camera is the only moving part\n-go vray options and hit "dont render final image"\n-set frame range you need\n-set frame step to 10 or higher depending on the camera speed\n-check "auto save" and specify a save path\n-hit render\n-you will notice the file size is growing as more frames are rendered\n-on renderend set Irridiance map "from file" and load map\n-switch back "dont render final image"'
            if result.type == self.GI_IRRADIANCE_BUCKET:
                st = 'Bucket mode renders GI bucket by bucket and can cause impropper GI solutions on the bucket borders'
            if result.type == self.CAUSTICS_NEW_MAP:
                st = 'Recompute mode "new map" is used for non static scenes only!\nA non static scene include animated objects, morphing objects, animated lights or textures\nAttention, that recomputing mode force the renderer to redo the Caustic solution each frame\nthat causes different solutions in each frame and can produce a flickering in the final output\nto reduce flickering you could increase the settings but that rise the rendertime per image without guarantee of flickerfree output'
            if result.type == self.CAUSTICS_FROM_FILE:
                st = 'Recompute mode "from file" force VRay to read the caustic information from file\nVray will NOT compute the caustic solution during the render process.\nTo create a caustic file on your computer you MUST have a static scene\nA static scene have no animated objects, no morphing objects, no animated lights or textures\n! the camera is the only moving part\n-go vray options and hit "dont render final image"\n-set one frame to render\n-check "auto save" and specify a save path\n-hit render\n-on renderend load caustic from file\n-switch back "dont render final image"'
            if result.type == self.GI_LIGHTCACHE_DISTRIBUTED:
                st = 'You could pre-render the Lightcache to file to save rendertime and costs.\n-set Light cache mode "single image"\n-enable autosave and specify save path\n-hit render\nIf Lightcache finished cancel render\nswitch back "dont render final image" and choose Lightcache mode "from file"'
            if result.type == self.GI_IRRADIANCE_DISTRIBUTED:
                st = 'You could pre-render the Irradiance map to file to save rendertime and costs.\n-set Irradiance map mode "single image"\n-enable autosave and specify save path\n-hit render\nIf Irradiance map finished cancel render\nswitch back "dont render final image" and choose Irridiance mode "from file"'
            if result.type == self.GI_IRRADIANCE_PREPASS:
                st = 'Even if GI is pre-calculated to file the animation can flicker.\nThis GI mode is used for animations with moving objects or lights. If your scene includes no moving objects\n\nrefer to GI mode "multiframe incremantal"'
            if result.type == self.GI_IRRADIANCE_ANIMRENDER:
                st = 'You need to generate all Irradience maps first\nto create all IRR maps:\n-set GI mode to "animation prepass"\n-below, enable autosave, set save path and save file name\n-enable "don\'t render final image" (vray global switches)\n-hit render and vray generates all IRR maps\nAfterwards reset all settings and set GI mode "animation render".\nSelect the maps you just created.\n\n!!   can render the Irradience map for you.\nSet GI mode to "Animation prepass".'
            if st != '':
                cmds.confirmDialog(title='Message', message=st, button='Ok')
            else:
                if result.type == self.VRAY_STANDALONE:
                    if cmds.confirmDialog(title='Message', message='Do you want to render with Vray Standalone?', button=('Yes', 'No')) == 'Yes':
                        self.vrsceneExport = True
                    else:
                        self.vrsceneExport = False
                    return True
                if result.type == self.GPU_DIALOG:
                    self.GpuCpu = selectCpuGpuDialog()
                    if self.GpuCpu in ('GPU', 'CPU'):
                        self.mainDialog.gpu_enabled = True
                    if self.GpuCpu == 'GPU':
                        result.message = 'Your job will be rendered on GPU'
                    else:
                        result.message = 'Your job will be rendered on CPU only'
                    return True

    def prepareSave(self, path, vecFiles):
        if not cmds.objExists('vraySettings'):
            return ''
        else:
            settingsToWrite = ''
            renderLayers = cmds.ls(type='renderLayer')
            for l in renderLayers:
                if cmds.getAttr(l + '.renderable') == 0:
                    continue
                try:
                    cmds.editRenderLayerGlobals(currentRenderLayer=l)
                except:
                    continue

                curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
                if curRend == self.getIdentifier()[0]:
                    self.toRetarget = []
                    destfolder = os.path.join(path, 'tex')
                    workspacefolder = os.path.join(destfolder, 'maya')
                    fgMapFolder = os.path.join(workspacefolder, 'renderData')
                    outFile = cmds.getAttr('vraySettings.fileNamePrefix')
                    if outFile != None and ('/' in outFile or '\\' in outFile):
                        self.toRetarget.append(['vraySettings.fileNamePrefix', cmds.getAttr('vraySettings.fileNamePrefix'), l])
                        outFile = outFile.split('\\')[-1]
                        outFile = outFile.split('/')[-1]
                        if self.mainDialog.isSingleFrameRender():
                            outFile = outFile.replace('.', '_').replace(':', '_').replace('<', '_').replace('>', '_').replace('/', '_').replace('\\', '_')
                        cmds.setAttr('vraySettings.fileNamePrefix', outFile, type='string')
                    cmds.setAttr('vraySettings.sys_max_threads', 0)
                    cmds.setAttr('vraySettings.vrscene_render_on', 1)
                    cmds.setAttr('vraySettings.runToCurrentTime', 0)
                    cmds.setAttr('vraySettings.runToAnimationStart', 0)
                    if cmds.getAttr('vraySettings.giOn') and cmds.getAttr('vraySettings.primaryEngine') == 0:
                        self.toRetarget.append(['vraySettings.imap_fileName', cmds.getAttr('vraySettings.imap_fileName'), l])
                        if cmds.getAttr('vraySettings.imap_fileName') != None:
                            mpath = cmds.getAttr('vraySettings.imap_fileName')
                            if existsFile(mpath):
                                ppath = 'tex/maya/renderData/' + os.path.basename(mpath)
                                appendFileInfo(vecFiles, ppath, mpath)
                                cmds.setAttr('vraySettings.imap_fileName', createPath(self.mainDialog.m_userName + '\\tex\\maya\\renderData', os.path.basename(mpath)), type='string')
                        if cmds.getAttr('vraySettings.imap_mode') == 7:
                            irrFiles = self.findIrrFiles()
                            for f in irrFiles:
                                if existsFile(f):
                                    ppath = 'tex/maya/renderData/' + os.path.basename(f)
                                    appendFileInfo(vecFiles, ppath, f)

                            irrpath = cmds.getAttr('vraySettings.imap_fileName')
                            self.toRetarget.append(['vraySettings.imap_fileName', irrpath, l])
                            cmds.setAttr('vraySettings.imap_fileName', createPath(self.mainDialog.m_userName + '\\tex\\maya\\renderData', os.path.basename(irrpath)), type='string')
                    if cmds.getAttr('vraySettings.giOn') and cmds.getAttr('vraySettings.primaryEngine') == 1 or cmds.getAttr('vraySettings.secondaryEngine') == 1 and cmds.getAttr('vraySettings.pmap_mode') == 1:
                        self.toRetarget.append(['vraySettings.pmap_file', cmds.getAttr('vraySettings.pmap_file'), l])
                        if cmds.getAttr('vraySettings.pmap_file') != None:
                            mpath = cmds.getAttr('vraySettings.pmap_file')
                            if existsFile(mpath):
                                ppath = 'tex/maya/renderData/' + os.path.basename(mpath)
                                appendFileInfo(vecFiles, ppath, mpath)
                                cmds.setAttr('vraySettings.pmap_file', createPath(self.mainDialog.m_userName + '\\tex\\maya\\renderData', os.path.basename(mpath)), type='string')
                    if cmds.getAttr('vraySettings.giOn') and cmds.getAttr('vraySettings.primaryEngine') == 3 or cmds.getAttr('vraySettings.secondaryEngine') == 3 and cmds.getAttr('vraySettings.mode') == 2:
                        self.toRetarget.append(['vraySettings.fileName', cmds.getAttr('vraySettings.fileName'), l])
                        if cmds.getAttr('vraySettings.fileName') != None:
                            mpath = cmds.getAttr('vraySettings.fileName')
                            if existsFile(mpath):
                                ppath = 'tex/maya/renderData/' + os.path.basename(mpath)
                                appendFileInfo(vecFiles, ppath, mpath)
                                cmds.setAttr('vraySettings.fileName', createPath(self.mainDialog.m_userName + '\\tex\\maya\\renderData', os.path.basename(mpath)), type='string')
                    if cmds.getAttr('vraySettings.causticsOn') and cmds.getAttr('vraySettings.causticsMode') == 1:
                        self.toRetarget.append(['vraySettings.causticsFile', cmds.getAttr('vraySettings.causticsFile'), l])
                        if cmds.getAttr('vraySettings.causticsFile') != None:
                            mpath = cmds.getAttr('vraySettings.causticsFile')
                            if existsFile(mpath):
                                ppath = 'tex/maya/renderData/' + os.path.basename(mpath)
                                appendFileInfo(vecFiles, ppath, mpath)
                                cmds.setAttr('vraySettings.causticsFile', createPath(self.mainDialog.m_userName + '\\tex\\maya\\renderData', os.path.basename(mpath)), type='string')
                    if cmds.getAttr('vraySettings.giOn') and cmds.getAttr('vraySettings.primaryEngine') == 0 and cmds.getAttr('vraySettings.imap_mode') == 6 and not self.mainDialog.isSingleFrameRender():
                        self.toRetarget.append(['vraySettings.imap_mode',
                         cmds.getAttr('vraySettings.imap_mode'),
                         l,
                         True])
                        cmds.setAttr('vraySettings.imap_mode', 7)
                        vrmap = createTempPath(self.mainDialog.m_userName, os.path.basename(getChangedMayaFilename() + '.vrmap'))
                        self.toRetarget.append(['vraySettings.imap_fileName2', cmds.getAttr('vraySettings.imap_fileName2'), l])
                        cmds.setAttr('vraySettings.imap_fileName2', vrmap, type='string')
                        settingsToWrite += 'mayaVrayAnimPrepass=1\n'
                    cmds.setAttr('vraySettings.imap_showCalcPhase', 1)
                    cmds.setAttr('vraySettings.showCalcPhase', 1)
                    cmds.setAttr('vraySettings.numPasses', 32)
                    if cmds.getAttr('vraySettings.vfbSA') and len(cmds.getAttr('vraySettings.vfbSA')) > 10:
                        vfbSettings = cmds.getAttr('vraySettings.vfbSA')
                        vfbFlags = vfbSettings[10]
                        isColorProfileBtn = vfbFlags & 64 == 64
                        isIcc = vfbFlags & 2097152 == 2097152
                        isSrgb = isColorProfileBtn and not isIcc
                        settingsToWrite += 'displaySRGB=' + ('1' if isSrgb else '0') + '\r\n'

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

                width = cmds.getAttr('vraySettings.wi')
                height = cmds.getAttr('vraySettings.he')
                cmds.setAttr('defaultResolution.width', width)
                cmds.setAttr('defaultResolution.height', height)
                if curRend == self.getIdentifier()[0]:
                    cmds.setAttr('vraySettings.fileNamePadding', 1)
                    settingsToWrite += 'singleframeMayaVray=1\r\n'
                    settingsToWrite += 'resolution=' + str(width) + 'x' + str(height) + '\r\n'
                    primary = 'undef'
                    secondary = 'undef'
                    if cmds.getAttr('vraySettings.giOn'):
                        gi_primary_type = cmds.getAttr('vraySettings.primaryEngine')
                        gi_secondary_type = cmds.getAttr('vraySettings.secondaryEngine')
                        adv_irradmap_mode = cmds.getAttr('vraySettings.imap_mode')
                        lightcache_mode = cmds.getAttr('vraySettings.mode')
                        if gi_primary_type == 0 and adv_irradmap_mode == 2:
                            primary = 'IRRf'
                        elif gi_primary_type == 0:
                            primary = 'IRR'
                        elif gi_primary_type == 1:
                            primary = 'PM'
                        elif gi_primary_type == 2:
                            primary = 'QMC'
                        elif gi_primary_type == 3 and lightcache_mode == 2:
                            primary = 'LCf'
                        elif gi_primary_type == 3:
                            primary = 'LC'
                        if gi_secondary_type == 1:
                            secondary = 'PM'
                        elif gi_secondary_type == 2:
                            secondary = 'QMC'
                        elif gi_secondary_type == 3 and lightcache_mode == 2:
                            secondary = 'LCf'
                        elif gi_secondary_type == 3:
                            secondary = 'LC'
                    settingsToWrite += 'primary=' + primary + '\n'
                    settingsToWrite += 'secondary=' + secondary + '\n'
                cmds.editRenderLayerGlobals(currentRenderLayer=oldRenderLayer)
            return settingsToWrite

    def postSave(self):
        for f in self.toRetarget:
            if f[1] != '' and f[1] != None:
                cmds.editRenderLayerGlobals(currentRenderLayer=f[2])
                if len(f) < 4:
                    cmds.setAttr(f[0], f[1], type='string')
                else:
                    cmds.setAttr(f[0], f[1])

        return
