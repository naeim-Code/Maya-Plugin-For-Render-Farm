import maya.cmds as cmds
import shutil
import sys 

import validator
from validator import *
import utilitis
from utilitis import *


class ValFR(Validator):
    is_renderer_validator = True
    GI_CAMERA_FLY = 0
    GI_STILL = 1
    giFile = ''

    def getName(self):
        return 'finalRender'

    def getIdentifier(self):
        return ['finalRender']

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
                resultList.append(TestResult(1001, 2, self, 'Final Render is not supported by Render Farm Application anymore (' + l + ')', False, 0))
                
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, 'FR'))
                if framestep < 1:
                    resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                if not cmds.objExists('defaultFinalRenderSettings'):
                    return
                if not cmds.attributeQuery('antiAliasing', node='defaultFinalRenderSettings', exists=1):
                    print 'fR not found'
                    return
                if cmds.getAttr('defaultFinalRenderSettings.antiAliasing') == 1:
                    minrate = cmds.getAttr('defaultFinalRenderSettings.minSampleLevel')
                    if minrate >= 3:
                        resultList.append(TestResult(1004, 1, self, 'Antialiasing: AA Minrate is very high (' + l + ')', False, 0))
                    maxrate = cmds.getAttr('defaultFinalRenderSettings.maxSampleLevel')
                    if maxrate >= 4:
                        resultList.append(TestResult(1005, 1, self, 'Antialiasing: AA Maxrate is very high (' + l + ')', False, 0))
                    if not cmds.getAttr('defaultFinalRenderSettings.filterImage'):
                        resultList.append(TestResult(1006, 1, self, 'Antialiasing: Filter Image is disabled (' + l + ')', False, 0))
                else:
                    resultList.append(TestResult(1007, 1, self, 'Antialiasing: AA is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.enableMapping'):
                    resultList.append(TestResult(1008, 1, self, 'General Options: "Enable Mapping" is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.force2Side'):
                    resultList.append(TestResult(1009, 1, self, 'General Options: "Force 2-sided" is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.enableAtmosphere'):
                    resultList.append(TestResult(1010, 1, self, 'General Options: "Enable Atmospherics" is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.enableShadows'):
                    resultList.append(TestResult(1011, 1, self, 'General Options: "Enable Shadows" is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.enableDisplacement'):
                    resultList.append(TestResult(1012, 1, self, 'General Options: "Enable Displacement" is disabled (' + l + ')', False, 0))
                if cmds.getAttr('defaultFinalRenderSettings.bucketSize') < 1:
                    resultList.append(TestResult(1013, 1, self, 'General Options: Bucket size seems to be small, can increase rendertime depending on scene content (' + l + ')', False, 0))
                elif cmds.getAttr('defaultFinalRenderSettings.bucketSize') > 2:
                    resultList.append(TestResult(1014, 1, self, 'General Options: Bucket size seems to be high, can increase rendertime depending on scene content (' + l + ')', False, 0))
                if cmds.getAttr('defaultFinalRenderSettings.infoStamp'):
                    resultList.append(TestResult(1015, 2, self, 'General Options: Information stamp not allowed (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.useReflection'):
                    resultList.append(TestResult(1016, 1, self, 'Raytracing: "Enable Reflections" is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.enableBlurry'):
                    resultList.append(TestResult(1017, 1, self, 'Raytracing: "Enable Blurry" is disabled (' + l + ')', False, 0))
                if not cmds.getAttr('defaultFinalRenderSettings.useRefraction'):
                    resultList.append(TestResult(1018, 1, self, 'Raytracing: "Enable Refractions" is disabled (' + l + ')', False, 0))
                if cmds.getAttr('defaultFinalRenderSettings.globalIllumination'):
                    giengine = cmds.getAttr('defaultFinalRenderSettings.giEngine')
                    if giengine == 1:
                        resultList.append(TestResult(1019, 2, self, 'Global Illumination: "FR-Image" is not supported, please set to Adaptive QMC (' + l + ')', False, 0))
                    elif giengine == 2:
                        if cmds.getAttr('defaultFinalRenderSettings.giEnableDetailsDetection'):
                            resultList.append(TestResult(1020, 1, self, 'Global Illumination: Details Enhancement is enabled (' + l + ')', False, 0))
                        if cmds.getAttr('frEngineAdaptiveQMC.maxRate') >= 1:
                            resultList.append(TestResult(1021, 1, self, 'Global Illumination: Max Rate seems to be very high (' + l + ')', False, 0))
                        solutionmode = cmds.getAttr('frEngineAdaptiveQMC.solutionMode')
                        if solutionmode == 1:
                            resultList.append(TestResult(1022, 1, self, 'Global Illumination: Attention, Solution is set to "camera fly" (' + l + ')', True, self.GI_CAMERA_FLY))
                            if cmds.getAttr('frEngineAdaptiveQMC.animationPass') == 0:
                                resultList.append(TestResult(1023, 2, self, 'Global Illumination: Animation Pass Prepass not supported (' + l + ')', False, 0))
                            elif cmds.getAttr('frEngineAdaptiveQMC.animationPass') == 1:
                                if cmds.getAttr('frEngineAdaptiveQMC.animationUpdate') == 3:
                                    resultList.append(TestResult(1024, 2, self, 'Global Illumination: Update Solution is not supported (' + l + ')', False, 0))
                                if cmds.getAttr('frEngineAdaptiveQMC.gimAction') == 3:
                                    resultList.append(TestResult(1025, 2, self, 'Global Illumination: Load/Save Solution is not supported (' + l + ')', False, 0))
                                elif cmds.getAttr('frEngineAdaptiveQMC.gimAction') == 2:
                                    resultList.append(TestResult(1026, 2, self, 'Global Illumination: Save Solution is not supported (' + l + ')', False, 0))
                                fn = cmds.getAttr('frEngineAdaptiveQMC.gimFileLoad')
                                if len(fn) > 0:
                                    if not existsFile(fn):
                                        fn = os.path.join(cmds.workspace(q=1, rd=1), fn)
                                    if not existsFile(fn):
                                        resultList.append(TestResult(1027, 2, self, 'Global Illumination: Load from... file not found (' + l + ')', False, 0))
                                    else:
                                        self.giFile = fn
                        elif solutionmode == 2:
                            resultList.append(TestResult(1028, 2, self, 'Global Illumination: Solution Mode "Character Animation" not yet supported, please contact Render Farm Application (' + l + ')', False, 0))
                        elif solutionmode == 0:
                            resultList.append(TestResult(1029, 1, self, 'Global Illumination: Attention, Solution is set to "still" (' + l + ')', True, self.GI_STILL))
                            if cmds.getAttr('frEngineAdaptiveQMC.reuse'):
                                resultList.append(TestResult(1030, 2, self, 'Global Illumination: GI Solution Reuse is not supported (' + l + ')', False, 0))
                            if cmds.getAttr('frEngineAdaptiveQMC.lock'):
                                resultList.append(TestResult(1031, 2, self, 'Global Illumination: GI Solution Lock is not supported (' + l + ')', False, 0))
                            if len(cmds.getAttr('frEngineAdaptiveQMC.gimFileLoad')) > 0:
                                resultList.append(TestResult(1032, 2, self, 'Global Illumination: GI Solution Autosave... is not supported (' + l + ')', False, 0))
                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))

    def furtherAction(self, result):
        st = ''
        if result.flagMoreInfos:
            if result.type == self.GI_STILL:
                st = 'GI Solution mode "still" is used for non static scenes only !\r\nA non static scene include animated objects, morphing objects, animated lights or textures\r\nAttention, that mode force Final Render to redo the light solution each frame\r\nthat causes different solutions in each frame and can produce a flickering in the final output\r\nto reduce flickering you could increase the settings but that rise the rendertime per image without guarantee of flickerfree output\r\nNote: A flickerfree animation can be generated by using Quasi Montecarlo with the disadvantage of high rendertime per image'
            if result.type == self.GI_CAMERA_FLY:
                st = 'GI Solution mode "camera Fly" is used to bake the light solution to file\r\nTo bake the light solution to file on your computer you MUST have a static scene\r\nA static scene include no animated objects, no morphing objects, no animated lights or textures\r\n! the camera is the only moving part\r\n-set animation "prepass" and update solution\r\n-set "save to" path and filename\r\n-set frame range you need\r\n-set frame step to 10 or higher depending on the camera speed\r\n-hit render\r\n-you will notice the file size is growing as more frames are rendered\r\n-on renderend set map "Load from"\r\n-set animation pass "rendering"'
            cmds.confirmDialog(title='Message', message=st, button='Ok')

    def prepareSave(self, path, vecFiles):
        if self.giFile != '':
            mayafileName = os.path.basename(getChangedMayaFilename())
            destfolder = os.path.join(path, 'tex')
            workspacefolder = os.path.join(destfolder, mayafileName)
            appendFileInfo(vecFiles, 'tex/' + mayafileName + '/data/' + os.path.basename(self.giFile), self.giFile)
        return ''

    def postSave(self):
        pass
