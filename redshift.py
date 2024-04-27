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


class ValRedshift(Validator):
    is_renderer_validator = True
    MAX_RP_DIALOG = 2
    toRetarget = []
    rpHourFactor = 1.35
    rpHourFactorGpu = 7.56
    maxRp = -1
    maxIterations = -1

    def getName(self):
        return 'Redshift'

    def getIdentifier(self):
        return ['redshift']

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
                if cmds.getAttr('redshiftOptions.primaryGIEngine') == 1 or cmds.getAttr('redshiftOptions.secondaryGIEngine') == 1 or cmds.getAttr('redshiftOptions.photonCausticsEnable') == 1:
                    if cmds.getAttr('redshiftOptions.photonMode') != 2:
                        resultList.append(TestResult(8015, 2, self, "Photon Mode not yet supported, set to Rebuild (don't save)", False, 0))
                if cmds.getAttr('redshiftOptions.subsurfaceScatteringMode') != 3:
                    resultList.append(TestResult(8015, 2, self, "SSS Mode not yet supported, set to Rebuild (don't save)", False, 0))
                if cmds.getAttr('redshiftOptions.irradiancePointCloudMode') != 3:
                    resultList.append(TestResult(8015, 2, self, "Irradiance Point Cloud Mode not yet supported, set to Rebuild (don't save)", False, 0))
                if cmds.getAttr('redshiftOptions.irradianceCacheMode') != 3:
                    resultList.append(TestResult(8015, 2, self, "Irradiance Cache Mode not yet supported, set to Rebuild (don't save)", False, 0))
                if self.mainDialog.isSingleFrameRender():
                    resultList.append(TestResult(8015, 2, self, 'Common: Redshift Distributed Single frame rendering not yet supported', False, 0))
                self.mainDialog.gpu_enabled = True
                rend = 'redshiftGPU'
                version = cmds.pluginInfo('redshift4maya', v=True, q=True)
                rend = rend + '_' + version
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, rend))
                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))

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
                self.toRetarget.append(['redshiftOptions.abortOnLicenseFail',
                 cmds.getAttr('redshiftOptions.abortOnLicenseFail'),
                 l,
                 True])
                cmds.setAttr('redshiftOptions.abortOnLicenseFail', 1)

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
