import maya.cmds as cmds
import shutil
import glob
import sys
import math 
import validator
from validator import *
import utilitis
from utilitis import *
 

class ValOctane(Validator):
    MAX_RP_DIALOG = 2
    toRetarget = []
    rpHourFactor = 1.35
    rpHourFactorGpu = 7.56
    is_renderer_validator = True
    maxRp = -1
    maxIterations = -1

    def getName(self):
        return 'Octane'

    def getIdentifier(self):
        return ['OctaneRender']

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
                info_kernel_type_index = 3
                if startFrame > endFrame:
                    resultList.append(TestResult(8015, 2, self, "Startframe can't be higher than Endframe", False, 0))
                if self.mainDialog.isSingleFrameRender():
                    resultList.append(TestResult(8015, 2, self, 'Common: Octane Distributed Single frame rendering not yet supported', False, 0))
                if cmds.getAttr('octaneKernel1.KernelType') == info_kernel_type_index:
                    resultList.append(TestResult(8015, 1, self, 'Please be aware, that you are rendering in Octane Info Mode. ', False, 0))
                if cmds.getAttr('octaneKernel1.MaxSamples') >= 5000:
                    resultList.append(TestResult(8015, 1, self, 'Your Max Samples value seems to be very high', False, 0))
                if cmds.getAttr('octaneKernel1.RayEpsilon') != 0.0:
                    resultList.append(TestResult(8015, 1, self, 'Please be aware, that the Ray Epsilon values was changed. According to the Octane documentation this is not adviced', False, 0))
                if cmds.getAttr('octaneKernel1.FilterSize') > 4:
                    resultList.append(TestResult(8015, 1, self, 'Your Filter Size value seems to be very high. The result might get blurry', False, 0))
                self.mainDialog.gpu_enabled = True
                rend = 'octaneGPU'
                version = cmds.pluginInfo('OctanePlugin', v=True, q=True)
                rend = rend + '_' + version
                print rend
                print '{} - {} - {} - {}'.format(l, startFrame, endFrame, framestep)
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, rend))
                resultList.append(TestResult(1, 0, self, self.getName() + '  settings have been checked.', False, 0))

    def furtherAction(self, result):
        if result.type == self.MAX_RP_DIALOG:
            res = selectPassesDialog().split(',')
            self.maxRp, self.maxIterations = int(res[0]), int(res[1])
            return True

    def prepareSave(self, path, vecFiles):
        renderLayers = cmds.ls(type='renderLayer')
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
            if curRend == self.getIdentifier():
                self.toRetarget = []
                startframe = int(cmds.getAttr('defaultRenderGlobals.startFrame'))
                endframe = int(cmds.getAttr('defaultRenderGlobals.endFrame'))
                framecount = endframe - startframe + 1
                rpFac = self.rpHourFactor
                if self.mainDialog.gpu_enabled:
                    rpFac = self.rpHourFactorGpu
                timelimit = float(self.maxRp) / float(framecount) / rpFac
                days = int(math.floor(timelimit / 24))
                hours = int(math.floor(timelimit - days * 24))
                minutes = int(math.ceil((timelimit - days * 24 - hours) * 60))

        return ''

    def postSave(self):
        for f in self.toRetarget:
            if f[1] != '' and f[1] != None:
                cmds.editRenderLayerGlobals(currentRenderLayer=f[2])
                if len(f) < 4:
                    cmds.setAttr(f[0], f[1], type='string')
                else:
                    cmds.setAttr(f[0], f[1])

        self.maxRp = -1
        self.maxIterations = -1
        return
