import maya.cmds as cmds
import shutil
import glob
import sys
import math 

import validator
from validator import *
import utilitis
from utilitis import *
 

def selectPassesDialogUi():
    form = cmds.setParent(q=True)
    cmds.columnLayout(columnAttach=('both', 10), rowSpacing=10, columnWidth=400)
    cmds.text(l='Input how many Renderpoints you like to spend for render\nand\ninput the maximal Iterations you like to have per frame\nThe farm renders each frame until:\n- the Renderpoints per frame are spent\nor\n- the Iterations per frame are completed.\n\nExample:\nsetup 100 Renderpoints and 100 Iterations for 100 frames\nyou get:\n- all 100 frames with 100 Iterations for LESS than 100 Renderpoints\nor\n- all 100 frames have the BEST POSSIBLE Iterations for 100 Renderpoints', align='left')
    maxRp = cmds.intField(min=1, max=10000, value=10)
    maxIterations = cmds.intField(min=32, max=10000, value=100)
    c = 'cmds.layoutDialog( dismiss=str(cmds.intField("' + maxRp + '", q=True, value=True)) + "," + str(cmds.intField("' + maxIterations + '", q=True, value=True)))'
    cmds.button(l='Ok', c=c)


def selectPassesDialog():
    res = cmds.layoutDialog(ui=selectPassesDialogUi)
    if res == None or res == 'dismiss':
        res = '-1,-1'
    return res


def selectCpuGpuDialogUi():
    form = cmds.setParent(q=True)
    cmds.columnLayout(columnAttach=('both', 3), rowSpacing=10, columnWidth=400)
    cmds.text(l='Do you want to render on GPU or on CPU?')
    cmds.button(l='GPU', c='cmds.layoutDialog( dismiss="GPU")')
    cmds.button(l='CPU', c='cmds.layoutDialog( dismiss="CPU")')


def selectCpuGpuDialog():
    res = cmds.layoutDialog(ui=selectCpuGpuDialogUi)
    if res == None or res == 'dismiss':
        res = ''
    return res


class ValIray(Validator):
    is_renderer_validator = True
    GPU_DIALOG = 1
    MAX_RP_DIALOG = 2
    toRetarget = []
    rpHourFactor = 1.35
    rpHourFactorGpu = 7.56
    GpuCpu = ''
    maxRp = -1
    maxIterations = -1

    def getName(self):
        return 'Iray'

    def getIdentifier(self):
        return ['ifmIrayPhotoreal']

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
            if curRend == self.getIdentifier():
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                resultList.append(TestResult(8015, 2, self, 'Iray is currently supported on Render Farm Application', False, 0))
                if framestep < 1:
                    resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                if self.mainDialog.isSingleFrameRender():
                    resultList.append(TestResult(8015, 2, self, 'Common: Iray Distributed Single frame rendering not yet supported', False, 0))
                if self.mainDialog.gpu_enabled == False:
                    resultList.append(TestResult(8015, 2, self, 'Do you want to render on GPU or CPU?', True, self.GPU_DIALOG))
                elif self.GpuCpu == 'GPU':
                    self.mainDialog.gpu_enabled = True
                    resultList.append(TestResult(8015, 0, self, 'Your job will be rendered on GPU', True, self.GPU_DIALOG))
                else:
                    self.mainDialog.gpu_enabled = False
                    resultList.append(TestResult(8015, 0, self, 'Your job will be rendered on CPU only', True, self.GPU_DIALOG))
                if self.maxRp == -1:
                    resultList.append(TestResult(8015, 2, self, 'Select your options', True, self.MAX_RP_DIALOG))
                else:
                    resultList.append(TestResult(8015, 0, self, 'Your Job is setup to use ' + str(self.maxRp) + ' Renderpoints or reach ' + str(self.maxIterations) + ' iterations!', True, self.MAX_RP_DIALOG))
                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))
                rend = 'irayGPU' if self.GpuCpu == 'GPU' else 'iray'
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, rend))

    def furtherAction(self, result):
        if result.type == self.GPU_DIALOG:
            self.GpuCpu = selectCpuGpuDialog()
            if self.GpuCpu in ('GPU', 'CPU'):
                self.mainDialog.gpu_enabled = True
            return True
        if result.type == self.MAX_RP_DIALOG:
            res = selectPassesDialog().split(',')
            self.maxRp, self.maxIterations = int(res[0]), int(res[1])
            return True

    def prepareSave(self, path, vecFiles):
        if not cmds.objExists('ifmGlobalsCommon'):
            return ''
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
                self.toRetarget.append(['ifmGlobalsIrayPhotoreal.irayMaxSamples',
                 cmds.getAttr('ifmGlobalsIrayPhotoreal.irayMaxSamples'),
                 l,
                 'int'])
                cmds.setAttr('ifmGlobalsIrayPhotoreal.irayMaxSamples', max(self.maxIterations, 32))
                self.toRetarget.append(['ifmGlobalsIrayPhotoreal.irayMaxTime0',
                 cmds.getAttr('ifmGlobalsIrayPhotoreal.irayMaxTime0'),
                 l,
                 'int'])
                cmds.setAttr('ifmGlobalsIrayPhotoreal.irayMaxTime0', days)
                self.toRetarget.append(['ifmGlobalsIrayPhotoreal.irayMaxTime1',
                 cmds.getAttr('ifmGlobalsIrayPhotoreal.irayMaxTime1'),
                 l,
                 'int'])
                cmds.setAttr('ifmGlobalsIrayPhotoreal.irayMaxTime1', hours)
                self.toRetarget.append(['ifmGlobalsIrayPhotoreal.irayMaxTime2',
                 cmds.getAttr('ifmGlobalsIrayPhotoreal.irayMaxTime2'),
                 l,
                 'int'])
                cmds.setAttr('ifmGlobalsIrayPhotoreal.irayMaxTime2', minutes)
                settingsToWrite += 'maxrp=' + str(self.maxRp) + '\r\n'
                settingsToWrite += 'samplinglevel=' + str(self.maxIterations) + '\r\n'

        return settingsToWrite

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
