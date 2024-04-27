import maya.cmds as cmds
import sys, os
 
import validator
from validator import *
import utilitis
from utilitis import *
 
class ValGeneral(Validator):
    is_renderer_validator = False
    INSTALL_PATH_CHANGED = 1
    connections = []

    def getName(self):
        return 'General'

    def test(self, resultList, fastCheck, layerinfos):
        ver = cmds.about(v=True)
        if not ver[0:1] == '2' and not int(ver[0:4]) >= 2014:
            resultList.append(TestResult(2001, 2, self, 'You need at least Maya 2014 to use Farminizer', False, 0))
        if mstr(cmds.file(sceneName=True, q=1)) == '':
            resultList.append(TestResult(2002, 2, self, 'Please save your scene before you try to export it!', False, 0))
        if len(os.path.basename(cmds.file(sceneName=True, q=1))) <= 7:
            resultList.append(TestResult(2002, 2, self, 'Scenefile name hast to be longer than 3 characters(not including the extension).', False, 0))
        for f in sys.path:
            if f.endswith('/Farm'):
                localfolder = os.path.dirname(__file__).replace('\\', '/')
                if localfolder != f:
                    resultList.append(TestResult(2006, 1, self, 'Installation path changed from %s to %s' % (f, localfolder), True, self.INSTALL_PATH_CHANGED))
                break

        found = False
        for f in os.environ['MAYA_SCRIPT_PATH'].split(':' if cmds.about(mac=1) else ';'):
            localfolder = os.path.dirname(os.path.dirname(__file__)).replace('\\', '/')
            if f.replace('\\', '/') == localfolder:
                found = True

        if not found:
            resultList.append(TestResult(2007, 1, self, 'Installation path not found', True, self.INSTALL_PATH_CHANGED))
        lights = cmds.ls(type='light')
        vrlights = []
        try:
            vrlights = cmds.ls(type='VRayPluginNodeLightShape')
        except:
            pass

        errorinstallplugs = os.path.join(self.mainDialog.m_defaultPath, 'at2_reb_errorinstallplugs.txt')
        if existsFile(errorinstallplugs):
            resultList.append(TestResult(2004, 2, self, 'Farminizer was not installed correctly, please close Maya and call "Reinstall Plugins" from Render Farm Application!', False, 0))
        if fastCheck:
            resultList.append(TestResult(1, 0, self, 'QuickCheck does not check all files the scene contains.', False, 0))
        particleCache = cmds.ls(et='dynGlobals')
        if particleCache == None:
            particleCache = []
        for p in particleCache:
            if cmds.getAttr(p + '.useParticleDiskCache') == 1:
                resultList.append(TestResult(2005, 1, self, 'Particle disk cache (' + p + ') is enabled', False, 0))

        if self.mainDialog.isSingleFrameRender():
            for sh in ['lambert', 'rampShader']:
                try:
                    for mat in cmds.ls(type=sh):
                        if cmds.getAttr(mat + '.glowIntensity') > 0:
                            resultList.append(TestResult(2008, 2, self, 'Glow not support for Distributed Render (' + mat + ')', False, 0))

                except:
                    pass

        resultList.append(TestResult(1, 0, self, self.getName() + ' settings have been checked', False, 0))
        return

    def furtherAction(self, result):
        st = ''
        if result.flagMoreInfos:
            if result.type == self.INSTALL_PATH_CHANGED:
                st = 'Your maya installation path has changed, perhaps due to updating your maya version.\nPlease make sure that you add the new Path to the Render Farm Application Manager. If this message persists please delete the file %s and reinstall the plugins from Render Farm Application' % (os.path.dirname(os.path.dirname(__file__)) + '/userSetup.py')
        cmds.confirmDialog(title='Message', message=st, button='Ok')

    def prepareSave(self, path, vecFiles):
        self.connections = []
        connectionsToDisconnect = ['vraySettings.numPasses']
        for conn in connectionsToDisconnect:
            try:
                subconn = cmds.listConnections(conn, p=True)
                for s in subconn:
                    cmds.disconnectAttr(conn, s)
                    self.connections.append([conn, s])

            except:
                pass

        return ''

    def postSave(self):
        for conn in self.connections:
            cmds.connectAttr(conn[0], conn[1])
