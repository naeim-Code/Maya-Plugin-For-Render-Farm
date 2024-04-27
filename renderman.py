import maya.cmds as cmds
import shutil
import glob
import sys

import validator
from validator import *
import utilitis
from utilitis import *

class ValRenderman(Validator):
    is_renderer_validator = True
    toRetarget = []

    def getName(self):
        return 'Renderman'

    def getIdentifier(self):
        return ['renderMan', 'renderManRIS']

    def test(self, resultList, fastCheck, layerinfos):
        renderLayers = cmds.ls(type='renderLayer')
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
            if curRend in ('renderManRIS', 'renderMan'):
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, 'renderMan'))
                resultList.append(TestResult(9001, 2, self, 'Renderman currently not supported', False, 0))
                if framestep < 1:
                    resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))

    def furtherAction(self, result):
        pass

    def prepareSave(self, path, vecFiles):
        workspacefolder = os.path.join(path, 'tex', 'maya')
        renderLayers = cmds.ls(type='renderLayer')
        for l in renderLayers:
            if cmds.getAttr(l + '.renderable') == 0:
                continue
            try:
                cmds.editRenderLayerGlobals(currentRenderLayer=l)
            except:
                continue

            curRend = cmds.getAttr('defaultRenderGlobals.currentRenderer')
            if curRend in ('renderManRIS', 'renderMan'):
                self.toRetarget = []
                rootFolder = os.path.join(cmds.workspace(q=1, rd=1), 'renderman')

        return ''

    def postSave(self):
        for f in self.toRetarget:
            if f[1] != '' and f[1] != None:
                cmds.editRenderLayerGlobals(currentRenderLayer=f[2])
                cmds.setAttr(f[0], f[1], type='string')

        return
