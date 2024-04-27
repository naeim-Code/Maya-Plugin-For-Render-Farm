import maya.cmds as cmds
import shutil
import sys
    
import validator
from validator import *
import utilitis
from utilitis import *


class ValMaxwell(Validator):
    is_renderer_validator = True
    texfiles = []
    toRetarget = []
    settingsToSet = []

    def getName(self):
        return 'Maxwell'

    def getIdentifier(self):
        return ['maxwell']

    def test(self, resultList, fastCheck, layerinfos):
        self.texfiles = []
        self.settingsToSet = []
        renderLayers = cmds.ls(type='renderLayer')
        bMaxwellFound = False
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
                bMaxwellFound = True
                startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
                endFrame = cmds.getAttr('defaultRenderGlobals.endFrame')
                framestep = cmds.getAttr('defaultRenderGlobals.byFrameStep')
                layerinfos.append(LayerInfos(l, startFrame, endFrame, framestep, 'MX'))
                if framestep < 1:
                    resultList.append(TestResult(7002, 2, self, 'Common: "Frame Range - By frame" lower than 1 not allowed (' + l + ')', False, 0))
                if not cmds.objExists('maxwellRenderOptions'):
                    resultList.append(TestResult(3001, 2, self, 'Maxwell render options not found (' + l + ')', False, 0))
                    return
                if not cmds.attributeQuery('renderTime', node='maxwellRenderOptions', exists=1):
                    resultList.append(TestResult(3002, 2, self, 'Maxwell render options not found (' + l + ')', False, 0))
                    print 'maxwell not found'
                    return
                if not cmds.attributeQuery('roughnessChannel', node='maxwellRenderOptions', exists=1):
                    resultList.append(TestResult(3005, 2, self, 'You need at least Maxwell v2 (' + l + ')', False, 0))
                    return
                if startFrame == endFrame:
                    resultList.append(TestResult(3006, 2, self, 'Maxwell still frame render out of Maya not yet supported, export scene to mxs format and use Render Farm Application to import (' + l + ')', False, 0))
                if not cmds.getAttr('maxwellRenderOptions.renderChannel'):
                    resultList.append(TestResult(3007, 2, self, 'At least the RGB channel must be active (' + l + ')', False, 0))
                cmdLine = cmds.getAttr('maxwellRenderOptions.cmdLine')
                if cmdLine != '' and cmdLine != '-d -nowait':
                    resultList.append(TestResult(3008, 2, self, 'Please remove additional flags "' + cmdLine + '" (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.samplingLevel') <= 7:
                    resultList.append(TestResult(3009, 1, self, 'Sampling level very low (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.samplingLevel') >= 15:
                    resultList.append(TestResult(3010, 1, self, 'Sampling level very high - high levels produce long rendertimes (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.renderTime') > 120:
                    resultList.append(TestResult(3011, 2, self, 'Maximum rendertime is 120min. If you need higher values contact Render Farm Application (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.multiLight') >= 1:
                    resultList.append(TestResult(3012, 1, self, 'Multilight increases the rendertime and is not recommended for animation renders (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.directLayer') == False:
                    resultList.append(TestResult(3013, 2, self, 'Layer "Direct Lighting" not active (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.indirectLayer') == False:
                    resultList.append(TestResult(3014, 1, self, 'Layer "Indirect Lighting" not active (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.directCausticReflLayer') == False:
                    resultList.append(TestResult(3015, 1, self, 'Layer "Direct Reflection Caustics" not active (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.directCausticRefrLayer') == False:
                    resultList.append(TestResult(3016, 1, self, 'Layer "Direct Refraction Caustics" not active (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.indirectCausticReflLayer') == False:
                    resultList.append(TestResult(3017, 1, self, 'Layer "Indirect Reflection Caustics" not active (' + l + ')', False, 0))
                if cmds.getAttr('maxwellRenderOptions.indirectCausticRefrLayer') == False:
                    resultList.append(TestResult(3018, 1, self, 'Layer "Indirect Refraction Caustics" not active (' + l + ')', False, 0))
                path = cmds.getAttr('maxwellRenderOptions.environment[0].envTexture')
                if path != '':
                    if not existsFile(path):
                        resultList.append(TestResult(3019, 2, self, 'IBE: Background Map not found (' + cmds.getAttr('maxwellRenderOptions.environment[0].envTexture') + ') (' + l + ')', False, 0))
                    else:
                        self.texfiles.append([cmds.getAttr('maxwellRenderOptions.environment[0].envTexture'), 'maxwellRenderOptions.environment[0].envTexture', l])
                if not cmds.getAttr('maxwellRenderOptions.environment[1].envSameAsBackground'):
                    path = cmds.getAttr('maxwellRenderOptions.environment[1].envTexture')
                    if path != '':
                        if not existsFile(cmds.getAttr('maxwellRenderOptions.environment[1].envTexture')):
                            resultList.append(TestResult(3020, 2, self, 'IBE: Reflection Map not found (' + cmds.getAttr('maxwellRenderOptions.environment[1].envTexture') + ') (' + l + ')', False, 0))
                        else:
                            self.texfiles.append([cmds.getAttr('maxwellRenderOptions.environment[1].envTexture'), 'maxwellRenderOptions.environment[1].envTexture', l])
                if not cmds.getAttr('maxwellRenderOptions.environment[2].envSameAsBackground'):
                    path = cmds.getAttr('maxwellRenderOptions.environment[2].envTexture')
                    if path != '':
                        if not existsFile(cmds.getAttr('maxwellRenderOptions.environment[2].envTexture')):
                            resultList.append(TestResult(3021, 2, self, 'IBE: Refraction Map not found (' + cmds.getAttr('maxwellRenderOptions.environment[2].envTexture') + ') (' + l + ')', False, 0))
                        else:
                            self.texfiles.append([cmds.getAttr('maxwellRenderOptions.environment[2].envTexture'), 'maxwellRenderOptions.environment[2].envTexture', l])
                if not cmds.getAttr('maxwellRenderOptions.environment[3].envSameAsBackground'):
                    path = cmds.getAttr('maxwellRenderOptions.environment[3].envTexture')
                    if path != '':
                        if not existsFile(cmds.getAttr('maxwellRenderOptions.environment[3].envTexture')):
                            resultList.append(TestResult(3022, 2, self, 'IBE: Illumination Map not found (' + cmds.getAttr('maxwellRenderOptions.environment[3].envTexture') + ') (' + l + ')', False, 0))
                        else:
                            self.texfiles.append([cmds.getAttr('maxwellRenderOptions.environment[3].envTexture'), 'maxwellRenderOptions.environment[3].envTexture', l])
                if cmds.getAttr('maxwellRenderOptions.simDiffraction') == True:
                    if cmds.getAttr('maxwellRenderOptions.simApertureMap') != '':
                        if not existsFile(cmds.getAttr('maxwellRenderOptions.simApertureMap')):
                            resultList.append(TestResult(3023, 2, self, 'IBE: Aperture Map not found (' + cmds.getAttr('maxwellRenderOptions.simApertureMap') + ') (' + l + ')', False, 0))
                        else:
                            self.texfiles.append([cmds.getAttr('maxwellRenderOptions.simApertureMap'), 'maxwellRenderOptions.simApertureMap', l])
                    if cmds.getAttr('maxwellRenderOptions.simObstacleMap') != '':
                        if not existsFile(cmds.getAttr('maxwellRenderOptions.simObstacleMap')):
                            resultList.append(TestResult(3024, 2, self, 'IBE: Obstacle Map not found (' + cmds.getAttr('maxwellRenderOptions.simObstacleMap') + ') (' + l + ')', False, 0))
                        else:
                            self.texfiles.append([cmds.getAttr('maxwellRenderOptions.simObstacleMap'), 'maxwellRenderOptions.simObstacleMap', l])
                if not fastCheck:
                    mxMaterials = cmds.ls(et='maxwellMaterial')
                    if mxMaterials != None:
                        for m in mxMaterials:
                            i = 0
                            while cmds.getAttr(m + '.layers[' + str(i) + '].layerUsed'):
                                if cmds.getAttr(m + '.layers[' + str(i) + '].bsdfUseIorFile'):
                                    iorFile = cmds.getAttr(m + '.layers[' + str(i) + '].bsdfIorFile')
                                    if iorFile != None and iorFile != '' and not existsFile(iorFile):
                                        resultList.append(TestResult(3025, 2, self, 'IOR R2 File not found (' + iorFile + ')', False, 0))
                                    else:
                                        self.texfiles.append([iorFile, m + '.layers[' + str(i) + '].bsdfIorFile', ''])
                                if cmds.getAttr(m + '.layers[' + str(i) + '].bsdfUseFullFile'):
                                    iorFile = cmds.getAttr(m + '.layers[' + str(i) + '].bsdfFullFile')
                                    if iorFile != None and iorFile != '' and not existsFile(iorFile):
                                        resultList.append(TestResult(3026, 2, self, 'IOR File not found (' + iorFile + ')', False, 0))
                                    else:
                                        self.texfiles.append([iorFile, m + '.layers[' + str(i) + '].bsdfFullFile', ''])
                                c = 0
                                while cmds.getAttr(m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingUsed'):
                                    if cmds.getAttr(m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingUseIorFile'):
                                        iorFile = cmds.getAttr(m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingIorFile')
                                        if iorFile != None and iorFile != '' and not existsFile(iorFile):
                                            resultList.append(TestResult(3027, 2, self, 'Coating IOR File not found (' + iorFile + ')', False, 0))
                                        else:
                                            self.texfiles.append([iorFile, m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingIorFile', ''])
                                    if cmds.getAttr(m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingUseFullFile'):
                                        iorFile = cmds.getAttr(m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingFullFile')
                                        if iorFile != None and iorFile != '' and not existsFile(iorFile):
                                            resultList.append(TestResult(3028, 2, self, 'Coating Full IOR File not found (' + iorFile + ')', False, 0))
                                        else:
                                            self.texfiles.append([iorFile, m + '.layers[' + str(i) + '].coatings[' + str(c) + '].coatingFullFile', ''])
                                    c += 1

                                i += 1

                    mxRefMaterials = cmds.ls(et='maxwellRefMaterial')
                    if mxRefMaterials != None:
                        for m in mxRefMaterials:
                            debuglog('refmaterial found: ' + m)
                            mxmFile = cmds.getAttr(m + '.mxmFile')
                            bFound = False
                            if mxmFile != None and mxmFile != '':
                                if not existsFile(mxmFile):
                                    resultList.append(TestResult(3029, 2, self, 'mxm File not found (' + mxmFile + ')', False, 0))
                                    continue
                                else:
                                    bFound = True
                            if bFound:
                                self.texfiles.append([mxmFile, m + '.mxmFile', ''])
                                mwcheck = 'mwcheck.exe'
                                if cmds.about(mac=1):
                                    mwcheck = 'mwcheck'
                                cmd = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'maxwell', mwcheck)
                                if mxmFile.find(' ') != -1 and cmd.find(' ') != -1:
                                    resultList.append(TestResult(3030, 2, self, 'Could not check mxm file, white spaces in the path are not allowed: ' + mxmFile, False, 0))
                                    continue
                                if cmd.find(' ') != -1:
                                    cmd = '"' + cmd + '"'
                                if mxmFile.find(' ') != -1:
                                    mxmFile = '"' + mxmFile + '"'
                                cmd = cmd + ' passX4f -mxm ' + mxmFile
                                fh = os.popen(cmd)
                                cont = fh.read()
                                fh.close()
                                for line in cont.splitlines():
                                    entries = line.split('|')
                                    if len(entries) != 2:
                                        resultList.append(TestResult(3031, 2, self, 'Could not check mxm file', False, 0))
                                    elif entries[0] == 'tex':
                                        if not existsFile(entries[1]):
                                            resultList.append(TestResult(3032, 2, self, 'File in mxm "' + mxmFile + '" not found: ' + entries[1].decode('utf-8', 'replace'), False, 0))
                                        else:
                                            self.texfiles.append([entries[1], '', ''])

                    mxBsdfs = cmds.ls(et='maxwellBsdf')
                    if mxBsdfs != None:
                        for m in mxBsdfs:
                            if cmds.attributeQuery('irf', node=m, exists=True):
                                iorFile = cmds.getAttr(m + '.irf')
                                if iorFile != None and iorFile != '' and not existsFile(iorFile):
                                    resultList.append(TestResult(3025, 2, self, 'IOR File not found (' + iorFile + ')', False, 0))
                                else:
                                    self.texfiles.append([iorFile, m + '.irf', ''])

                    mxEmitter = cmds.ls(et='maxwellEmitter2')
                    if mxEmitter != None:
                        for m in mxEmitter:
                            if cmds.attributeQuery('ies', node=m, exists=True):
                                iesFile = cmds.getAttr(m + '.ies')
                                if iesFile != None and iesFile != '' and not existsFile(iesFile):
                                    resultList.append(TestResult(3034, 2, self, 'IES File not found (' + iesFile + ')', False, 0))
                                else:
                                    self.texfiles.append([iesFile, m + '.ies', ''])

                resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))
                self.settingsToSet.append(['-nowait -nomxi -node -mintime:60 -bitmaps:"' + createPath(self.mainDialog.m_userName + '\\tex\\maya', 'sourceimages') + '"',
                 cmdLine,
                 'maxwellRenderOptions.cmdLine',
                 l,
                 True])
                self.settingsToSet.append([1,
                 cmds.getAttr('maxwellRenderOptions.persistentMXS'),
                 'maxwellRenderOptions.persistentMXS',
                 l,
                 False])
                self.settingsToSet.append([1,
                 cmds.getAttr('maxwellRenderOptions.specifyMXI'),
                 'maxwellRenderOptions.specifyMXI',
                 l,
                 False])
                self.settingsToSet.append(['c:\\logs\\temp.mxs',
                 cmds.getAttr('maxwellRenderOptions.mxsPath'),
                 'maxwellRenderOptions.mxsPath',
                 l,
                 True])
                self.settingsToSet.append(['c:\\logs\\temp.mxi',
                 cmds.getAttr('maxwellRenderOptions.mxiPath'),
                 'maxwellRenderOptions.mxiPath',
                 l,
                 True])
                self.settingsToSet.append([0,
                 cmds.getAttr('maxwellRenderOptions.multiLight'),
                 'maxwellRenderOptions.multiLight',
                 l,
                 False])
                self.settingsToSet.append([120,
                 cmds.getAttr('maxwellRenderOptions.renderTime'),
                 'maxwellRenderOptions.renderTime',
                 l,
                 False])
            else:
                bOthersFound = True
            if bMaxwellFound and bOthersFound:
                resultList.append(TestResult(3033, 2, self, "You can't mix Maxwell Layers with other renderers, please use only layers with Maxwell", False, 0))

        return

    def furtherAction(self, result):
        st = ''
        if result.flagMoreInfos:
            if result.type == self.GI_STILL:
                st = ''
            cmds.confirmDialog(title='Message', message=st, button='Ok')

    def prepareSave(self, path, vecFiles):
        destfolder = os.path.join(path, 'tex')
        workspacefolder = os.path.join(destfolder, 'maya')
        imgfolder = os.path.join(workspacefolder, 'sourceimages')
        cmds.setAttr('defaultRenderGlobals.animation', True)
        cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)
        cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', True)
        cmds.setAttr('defaultRenderGlobals.periodInExt', True)
        self.toRetarget = []
        for f in self.texfiles:
            if f[0] != '' and f[0] != None:
                if f[2] != '':
                    cmds.editRenderLayerGlobals(currentRenderLayer=f[2])
                mpath = f[0]
                if existsFile(mpath):
                    ppath = 'tex/maya/sourceimages/' + os.path.basename(mpath)
                    appendFileInfo(vecFiles, ppath, mpath)
                    if f[1] != '':
                        cmds.setAttr(f[1], createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(mpath)), type='string')
                        self.toRetarget.append([f[0], f[1], f[2]])
                else:
                    print ('file not found: ', f)

        for f in self.settingsToSet:
            print f
            if f[3] != '':
                cmds.editRenderLayerGlobals(currentRenderLayer=f[3])
            if f[4]:
                cmds.setAttr(f[2], f[0], type='string')
            else:
                cmds.setAttr(f[2], f[0])

        return ''

    def postSave(self):
        for f in self.toRetarget:
            if f[0] != '' and f[0] != None:
                if f[2] != '':
                    cmds.editRenderLayerGlobals(currentRenderLayer=f[2])
                cmds.setAttr(f[1], f[0], type='string')

        for f in self.settingsToSet:
            if f[3] != '':
                cmds.editRenderLayerGlobals(currentRenderLayer=f[3])
            if f[4]:
                cmds.setAttr(f[2], f[1], type='string')
            else:
                cmds.setAttr(f[2], f[1])

        return
