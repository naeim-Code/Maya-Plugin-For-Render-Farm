
import maya.cmds as cmds
import sys
import math
    
import validator
from validator import *
import utilitis
from utilitis import *


g_slicesVal = 10

def selectSlicesDialogUi():
    global g_slicesVal
    form = cmds.setParent(q=True)
    cmds.columnLayout(columnAttach=('both', 5), rowSpacing=10, columnWidth=400)
    cmds.text(l='How many machines should work on your job?')
    lbl = cmds.text(label=str(g_slicesVal), align='center')
    cb1 = cmds.intSlider(min=10, max=100, value=g_slicesVal, step=10)
    cmds.intSlider(cb1, e=True, cc='val=int(round(cmds.intSlider("' + cb1 + '", q=True, value=True) / 10)*10); cmds.text("' + lbl + '", e=True, label=str(val)); cmds.intSlider("' + cb1 + '", e=True, value=val)')
    cmds.button(l='Ok', c='cmds.layoutDialog( dismiss=str(cmds.intSlider("' + cb1 + '", q=True, value=True)))')
    cmds.text(label='Lower the number of nodes to have less overhead charged on your job.\nLess nodes will result in slightly lower rendercosts, but will make your\nrenderjob take longer to complete.\n')



def selectSlicesDialog(value):
    global g_slicesVal
    g_slicesVal = value
    res = cmds.layoutDialog(ui=selectSlicesDialogUi)
    if res == None or res == 'dismiss':
        res = value
    return int(res)


class ValRendersettings(Validator):
    is_renderer_validator = False
    oldRendOutPath = ''
    DR_SELECT_SLICES = 4
    drSlices = 100

    def getName(self):
        return 'Rendersettings'

    def cleanupMel(self, m):
        if m == None or len(m) == 0:
            return ''
        else:
            allowedMels = ['xgprerendering',
             'crowdproxyarnoldevalattributes',
             'crowdproxyvrayevalattributes',
             'oxsetisrendering(true)',
             'oxsetisrendering(false)',
             'glmrendercallback("prerender")',
             'glmrendercallback("postrender")',
             'glmrendercallback("prerenderframe")',
             'glmrendercallback("postrenderframe")',
             'glmrendercallback("prerenderlayer")',
             'glmrendercallback("postrenderlayer")']
            cleaned = m.lower()
            for mel in allowedMels:
                cleaned = cleaned.replace(mel + '.mel', '')
                cleaned = cleaned.replace(mel, '')

            print (m, cleaned)
            return cleaned.strip(' \t\n\r;')

    def test(self, resultList, fastCheck, layerinfos):
        self.oldRendOutPath = ''
        startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
        endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
        curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
        supportedRenderers = ['mayaSoftware',
         'mayaHardware',
         'mentalRay',
         'vray',
         'maxwell',
         'arnold',
         'renderManRIS',
         'renderMan',
         'redshift',
         'OctaneRender']
        if cmds.getAttr('defaultRenderGlobals.imageFormat') == 23:
            resultList.append(TestResult(5001, 2, self, 'Common: Image Format (.avi) not supported', False, 0))
        byframe = int(cmds.getAttr('defaultRenderGlobals.byFrameStep'))
        numFrames = int(math.ceil(float(int(endFrame) - int(startFrame) + 1) / float(byframe)))
        if farmWin.farmWin.estimateEnabled:
            if numFrames < 5:
                resultList.append(TestResult(5031, 2, self, 'Common: for Cost Estimation your frame range must consist of at least 5 frames', False, 0))
            if farmWin.skyMainDlg.isMultilayerEnabled():
                resultList.append(TestResult(5031, 2, self, 'Common: estimating multilayer rendering currently not possible', False, 0))
        preMel = self.cleanupMel(cmds.getAttr('defaultRenderGlobals.preMel'))
        if preMel != None and len(preMel) > 0:
            resultList.append(TestResult(5002, 2, self, 'Common: MEL render scripts are not allowed "' + preMel + '"', False, 0))
        postMel = self.cleanupMel(cmds.getAttr('defaultRenderGlobals.postMel'))
        if postMel != None and len(postMel) > 0:
            resultList.append(TestResult(5003, 2, self, 'Common: MEL render scripts are not allowed "' + postMel + '"', False, 0))
        preRenderLayerMel = self.cleanupMel(cmds.getAttr('defaultRenderGlobals.preRenderLayerMel'))
        if preRenderLayerMel != None and len(preRenderLayerMel) > 0:
            if preRenderLayerMel.find('import mentalcore') >= 0 and cmds.about(version=1).find('2015') >= 0:
                pass
            else:
                resultList.append(TestResult(5004, 2, self, 'Common: MEL render scripts are not allowed "' + preRenderLayerMel + '"', False, 0))
        postRenderLayerMel = self.cleanupMel(cmds.getAttr('defaultRenderGlobals.postRenderLayerMel'))
        if postRenderLayerMel != None and len(postRenderLayerMel) > 0:
            if postRenderLayerMel.find('import mentalcore') >= 0 and cmds.about(version=1).find('2015') >= 0:
                pass
            else:
                resultList.append(TestResult(5005, 2, self, 'Common: MEL render scripts are not allowed "' + postRenderLayerMel + '"', False, 0))
        preRenderMel = self.cleanupMel(cmds.getAttr('defaultRenderGlobals.preRenderMel'))
        if preRenderMel != None and len(preRenderMel) > 0:
            resultList.append(TestResult(5006, 2, self, 'Common: MEL render scripts are not allowed "' + preRenderMel + '"', False, 0))
        postRenderMel = self.cleanupMel(cmds.getAttr('defaultRenderGlobals.postRenderMel'))
        if postRenderMel != None and len(postRenderMel) > 0:
            resultList.append(TestResult(5007, 2, self, 'Common: MEL render scripts are not allowed "' + postRenderMel + '"', False, 0))
        framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
        if framestep != 1:
            if self.mainDialog.isSingleFrameRender():
                resultList.append(TestResult(5008, 2, self, 'Common: "Frame Range - By frame" must be set to 1 for distributed render', False, 0))
            elif framestep < 1:
                resultList.append(TestResult(5008, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed ', False, 0))
            else:
                resultList.append(TestResult(5008, 1, self, 'Common: "Frame Range - By frame" is set to ' + str(framestep), False, 0))
        renumber_frames_enabled = cmds.getAttr('defaultRenderGlobals.modifyExtension')
        if renumber_frames_enabled == True:
            resultList.append(TestResult(5018, 2, self, 'Common: Renumber frames is currently not supported, please deactivate', False, 0))
        width = cmds.getAttr('defaultResolution.width')
        if width < 350:
            resultList.append(TestResult(5009, 1, self, 'Common: Resolution X seems to be very low.', False, 0))
        if width > 1921 and not self.mainDialog.isSingleFrameRender():
            resultList.append(TestResult(5010, 1, self, 'Common: Resolution X seems to be very high.', False, 0))
        height = cmds.getAttr('defaultResolution.height')
        if height < 350:
            resultList.append(TestResult(5011, 1, self, 'Common: Resolution Y seems to be very low.', False, 0))
        if height > 1081 and not self.mainDialog.isSingleFrameRender():
            resultList.append(TestResult(5012, 1, self, 'Common: Resolution Y seems to be very high.', False, 0))
        renderLayers = cmds.ls(type='renderLayer')
        if self.mainDialog.isSingleFrameRender():
            if width < 400 or height < 400:
                resultList.append(TestResult(5013, 2, self, 'Common: Single Frame Rendering needs a minimum resolution of 400x400', False, 0))
            if startFrame != 0 or endFrame != 0:
                resultList.append(TestResult(5014, 2, self, 'Common: Only frame 0 can be rendered as single frame, please select frame range 0 to 0!', False, 0))
            resultList.append(TestResult(5032, 0, self, 'Rendering: Your scene will render distributed on ' + str(self.drSlices) + ' Nodes. To lower overhead costs', True, self.DR_SELECT_SLICES))
        if cmds.getAttr('defaultResolution.fields') != 0:
            resultList.append(TestResult(5017, 1, self, 'Common: "Render to Fields" is activated.', False, 0))
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            if not cmds.getAttr('defaultRenderGlobals.animation'):
                curFrame = cmds.currentTime(query=True)
                cmds.setAttr('defaultRenderGlobals.animation', True)
                cmds.setAttr('defaultRenderGlobals.startFrame', curFrame)
                cmds.setAttr('defaultRenderGlobals.endFrame', curFrame)
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                resultList.append(TestResult(5018, 1, self, 'Common: No Frames to render were set. You will be rendering the current Frame: ' + str(curFrame), False, 0))
            elif startFrame == endFrame:
                resultList.append(TestResult(5018, 1, self, 'Common: You will be rendering Frame: ' + str(startFrame), False, 0))
            if curRend not in supportedRenderers:
                resultList.append(TestResult(5019, 2, self, 'Common: Renderer "' + str(curRend) + '" is not allowed.(' + l + ')', False, 0))
            if curRend == 'mayaHardware':
                resultList.append(TestResult(5020, 2, self, 'Common: Maya Hardware Renderer not allowed.(' + l + ')', False, 0))
            if startFrame > endFrame:
                resultList.append(TestResult(5030, 2, self, 'Common: your Start frame is higher than your End frame (' + l + ')', False, 0))
            cams = cmds.listCameras()
            bCamFound = False
            for c in cams:
                if cmds.getAttr(c + '.renderable') == 1:
                    resultList.append(TestResult(5021, 0, self, 'Common: Render Camera: ' + c + ' (' + l + ')', False, 0))
                    if self.mainDialog.isSingleFrameRender():
                        if bCamFound:
                            resultList.append(TestResult(5021, 2, self, 'Common: Render Camera: multiple Render Cameras not allowed for distributed single frame Rendering', False, 0))
                        if curRend != 'vray':
                            if cmds.getAttr(c + '.ma') == 1 or cmds.getAttr(c + '.dep') == 1:
                                resultList.append(TestResult(5021, 2, self, 'Common: Render Camera: Camera alpha and depth channels not allowed, use render passes instead', False, 0))
                    bCamFound = True

            if not bCamFound:
                resultList.append(TestResult(5022, 2, self, 'Common: No active Camera found (' + l + ')', False, 0))
            if curRend == 'mayaSoftware':
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, 'intern'))
                if cmds.getAttr('defaultRenderQuality.maxShadingSamples') < 2:
                    resultList.append(TestResult(5023, 1, self, 'Maya Software: AA "Max shading" is very low.(' + l + ')', False, 0))
                if cmds.getAttr('defaultRenderQuality.maxShadingSamples') > 8:
                    resultList.append(TestResult(5024, 1, self, 'Maya Software: AA "Max shading" is very high.(' + l + ')', False, 0))
                if cmds.getAttr('defaultRenderQuality.shadingSamples') > 2:
                    resultList.append(TestResult(5025, 1, self, 'Maya Software: AA "Shading" is very high.(' + l + ')', False, 0))
                if cmds.getAttr('defaultRenderQuality.enableRaytracing'):
                    if cmds.getAttr('defaultRenderQuality.reflections') >= 3:
                        resultList.append(TestResult(5026, 1, self, 'Maya Software: Maximal Reflection depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('defaultRenderQuality.refractions') >= 7:
                        resultList.append(TestResult(5027, 1, self, 'Maya Software: Maximal Refraction depth is very high.(' + l + ')', False, 0))
                    if cmds.getAttr('defaultRenderQuality.shadows') >= 3:
                        resultList.append(TestResult(5028, 1, self, 'Maya Software: Maximal Shadow depth is very high.(' + l + ')', False, 0))
                if cmds.getAttr('defaultRenderGlobals.numCpusToUse') != 0:
                    resultList.append(TestResult(5029, 2, self, 'Maya Software: Memory: use all avaliable CPUs is disabled.(' + l + ')', False, 0))

        resultList.append(TestResult(1, 0, self, self.getName() + ' have been checked', False, 0))
        return

    def furtherAction(self, result):
        if result.type == self.DR_SELECT_SLICES:
            self.drSlices = selectSlicesDialog(self.drSlices)
            result.message = 'Rendering: Your scene will render distributed on ' + str(self.drSlices) + ' Nodes. To lower overhead costs'
            return True

    def prepareSave(self, path, vecFiles):
        self.oldRendOutPath = ''
        outputPath = createOutPath(self.mainDialog.m_userName)
        stSettingsToWrite = '[region]\r\n'
        stSettingsToWrite += 'user=' + self.mainDialog.m_userName + '\r\n'
        stSettingsToWrite += 'units=0\r\n'
        stSettingsToWrite += 'program=MAYA\r\n'
        version = cmds.about(version=1)
        try:
            if cmds.about(iv=True).find('Extension 1') >= 0:
                version += 'ext'
            if version.find('2016') >= 0 and cmds.about(iv=True).find('Extension 2') >= 0:
                version = '2016ext2'
        except:
            pass

        if not self.mainDialog.isMiExport:
            stSettingsToWrite += 'version=' + version + '\r\n'
            stSettingsToWrite += 'decimal=undef\r\n'
        renderLayers = cmds.ls(type='renderLayer')
        for l in renderLayers:
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
                if cmds.getAttr(l + '.renderable') == 0:
                    continue
            except:
                continue

            startframe = str(int(cmds.getAttr('defaultRenderGlobals.startFrame')))
            endframe = str(int(cmds.getAttr('defaultRenderGlobals.endFrame')))
            isDR = self.mainDialog.isSingleFrameRender()
            if isDR:
                startframe = endframe = '1'
                outfile = mstr(cmds.getAttr('defaultRenderGlobals.imageFilePrefix'))
                if cmds.getAttr('defaultRenderGlobals.currentRenderer') == 'vray':
                    outfile = mstr(cmds.getAttr('vraySettings.fileNamePrefix'))
                if outfile == '':
                    outfile = getChangedMayaFilename()
                outfile = outfile.replace('.', '_').replace(':', '_').replace('<', '_').replace('>', '_').replace('/', '_').replace('\\', '_')
                outputPath += '\\' + outfile
                if cmds.getAttr('defaultRenderGlobals.currentRenderer') == 'vray':
                    frm = cmds.getAttr('vraySettings.imageFormatStr')
                    if not frm:
                        frm = 'png'
                    outputPath += '.' + frm
                else:
                    outputPath += getExtension(int(cmds.getAttr('defaultRenderGlobals.imageFormat')), subformat=cmds.getAttr('defaultRenderGlobals.imfPluginKey'))
                cmds.setAttr('defaultRenderGlobals.extensionPadding', 1)
                stSettingsToWrite += 'slices=' + str(self.drSlices) + '\r\n'
            elif cmds.getAttr('defaultRenderGlobals.currentRenderer') == 'vray':
                outputPath += '\\' + mstr(cmds.getAttr('vraySettings.fileNamePrefix')) + '.' + cmds.getAttr('vraySettings.imageFormatStr')
            else:
                outputPath += '\\' + mstr(cmds.getAttr('defaultRenderGlobals.imageFilePrefix')) + getExtension(int(cmds.getAttr('defaultRenderGlobals.imageFormat')), subformat=cmds.getAttr('defaultRenderGlobals.imfPluginKey'))
            break

        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        stSettingsToWrite += 'resolution=' + str(width) + 'x' + str(height) + '\r\n'
        framestep = int(cmds.getAttr('defaultRenderGlobals.byFrameStep'))
        if framestep < 1:
            framestep = 1
        stSettingsToWrite += 'rangestep=' + str(framestep) + '\r\n'
        stSettingsToWrite += 'startframes=' + startframe + ' \r\n'
        stSettingsToWrite += 'endframes=' + endframe + ' \r\n'
        stSettingsToWrite += 'gamma=undef\r\n'
        stSettingsToWrite += 'gamma_bitmap_in=undef\r\n'
        stSettingsToWrite += 'gamma_bitmap_out=undef\r\n'
        stSettingsToWrite += 'field_order=' + str(cmds.getAttr('defaultResolution.fields')) + '\r\n'
        osys = 'undef'
        if cmds.about(win=1):
            osys = 'Windows'
        elif cmds.about(li=1):
            osys = 'Linux'
        elif cmds.about(mac=1):
            osys = 'Mac'
        legacyLayers = ''
        try:
            import maya.mel as mel
            print 'Render Farm Application: The following Error is intended and does nothing wrong'
            legacyLayers = mel.eval('catchQuiet($tempvar=$renderSetupEnableCurrentSession);')
        except:
            pass

        try:
            legacyLayers = 1 if cmds.mayaHasRenderSetup() else 0
        except:
            pass

        stSettingsToWrite += 'mayaRendersetupEnable=' + mstr(legacyLayers) + '\r\n'
        stSettingsToWrite += 'OS=' + osys + '\r\n'
        bits = '32'
        if cmds.about(is64=1):
            bits = '64'
        stSettingsToWrite += 'Bits=' + bits + '\r\n'
        outputSuffix = ''
        if self.mainDialog.isVrsceneExport:
            try:
                outputSuffix = '.' + cmds.getAttr('vraySettings.imageFormatStr')
            except:
                outputSuffix = '.png'

        stSettingsToWrite += 'output=' + outputPath + outputSuffix + '\r\n'
        stSettingsToWrite += 'downloadpath=' + os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='images')) + '\r\n'
        cntCams = 0
        cntCamsAvailable = 0
        for c in cmds.listCameras():
            if cmds.getAttr(c + '.renderable') == 1:
                stSettingsToWrite += 'camera' + mstr(cntCams) + '=' + mstr(c) + '\r\n'
                cntCams += 1
            stSettingsToWrite += 'cameraAvailable' + mstr(cntCamsAvailable) + '=' + mstr(c) + '\r\n'
            cntCamsAvailable += 1

        stSettingsToWrite += 'cameraCount=' + mstr(cntCams) + '\r\n'
        stSettingsToWrite += 'cameraAvailableCount=' + mstr(cntCamsAvailable) + '\r\n'
        renderLayers = cmds.ls(type='renderLayer')
        for l in renderLayers:
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            outpath = mstr(cmds.getAttr('defaultRenderGlobals.imageFilePrefix'))
            if isDR:
                outpath = outpath.replace('.', '_').replace(':', '_').replace('<', '_').replace('>', '_').replace('/', '_').replace('\\', '_')
            else:
                outpath = outpath.replace('.', '_').replace(':', '_')
                outpath = outpath.lstrip('/\\')
            cmds.setAttr('defaultRenderGlobals.imageFilePrefix', outpath, type='string')
            print 'OutPath: ' + outpath
            if cmds.getAttr('defaultRenderGlobals.modifyExtension') == False:
                cmds.setAttr('defaultRenderGlobals.startExtension', int(startframe))
                cmds.setAttr('defaultRenderGlobals.byExtension', 1)
            try:
                cmds.setAttr('defaultRenderGlobals.skipExistingFrames', 0)
            except:
                pass

        return stSettingsToWrite

    def postSave(self):
        pass
