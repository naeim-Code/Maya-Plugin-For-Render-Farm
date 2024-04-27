
import maya
import maya.cmds as cmds
import os
import shutil
import sys
import glob
import time
import sys
import re
import subprocess
import uuid 

import validator
from validator import *
import utilitis
from utilitis import *
 

class ValTexture(Validator):
    particleDir = ''
    managerPath = ''
    defaultPath = ''
    clothFiles = []
    clothObjects = []
    cacheFiles = []
    cacheObjects = []
    meshCaches = []
    meshCacheSubfiles = []
    toRetarget = []
    alembic_objects = []
    xgenMRloaded = False

    def getName(self):
        return 'Texture'

    def getAllReferences(self, vecProjs, subproj = ''):
        projs = cmds.file(subproj, q=1, r=1)
        for p in projs:
            st = p
            st = re.sub('\\.mb\\{.*\\}', '.mb', st)
            st = re.sub('\\.ma\\{.*\\}', '.ma', st)
            vecProjs.append(st)
            self.getAllReferences(vecProjs, subproj=st)

    def test(self, resultList, fastCheck, layerinfos):
        allTextures, allObjects, allParams, allOptions = findAllTextures()
        self.particleDir = ''
        self.clothFiles = []
        i = 0
        debuglog(self.managerPath)
        ftpContentsSizes = []
        ftpContentsFiles = []
        if self.defaultPath and existsFile(self.defaultPath):
            ftpContentsPath = os.path.join(self.defaultPath, 'shadows.txt')
            if(not existsFile(ftpContentsPath)): 
                timeout = 0
                bConnected = True
                try:
                    if cmds.about(mac=1):
                        subprocess.Popen(self.mainDialog.m_managerPath, shell=False)
                    else:
                        subprocess.Popen('"' + self.mainDialog.m_managerPath + '"', shell=False)
                except:
                    print 'val_texture: ' + str(sys.exc_info())

                waiting = cmds.window(retain=True)
                cmds.columnLayout(adjustableColumn=True)
                lblAsking = cmds.text(label='Asking Render Farm Application...')
                cmds.showWindow()
                while  not existsFile(ftpContentsPath):
                    if timeout > 15:
                        if cmds.confirmDialog(title='Farminizer', message='Render Farm Application is not answering, be sure that it is running. Do you want to wait some more?', button=('Yes', 'No')) == 'Yes':
                            timeout = 0
                        else:
                            resultList.append(TestResult(6002, 2, self, 'Could not connect to Render Farm Application. Be sure that it is opened and responding.', False, 0))
                            bConnected = False
                            break
                    time.sleep(1)
                    cmds.text(lblAsking, e=1, label='Asking Render Farm Application...' + str(timeout))
                    self.mainDialog.setStatus('Asking Render Farm Application...' + str(timeout))
                    timeout = timeout + 1

                cmds.deleteUI(waiting)
            #if bConnected:
            #    ftpContentsFiles, ftpContentsSizes = readFtpFileContents(ftpContentsPath)
            #    try:
            #        os.remove(ftpContentsPath)
            #    except:
            #        pass

        else:
            resultList.append(TestResult(6003, 2, self, 'Could not find Render Farm Application path "' + mstr(self.defaultPath) + '"', False, 0))
        alreadyChecked = []
        curWorkspace = cmds.workspace(rd=True, q=True)
        for f in allTextures:
            if f not in alreadyChecked and not allOptions[i] == 2:
                self.mainDialog.setStatus('Checking Texture ' + str(i) + ' of ' + str(len(allTextures)))
                if not cmds.attributeQuery('miWritable', node=allObjects[i], exists=True):
                    if not existsFile(f):
                        if f == None:
                            f = ''
                        if cmds.attributeQuery('useFrameExtension', node=allObjects[i], exists=True) and cmds.getAttr(allObjects[i] + '.useFrameExtension') == True:
                            sequencefile = os.path.basename(f)
                            sequencefile = parseSequence(sequencefile)
                            sequencefolder = os.path.dirname(f)
                            sequencepath = os.path.join(sequencefolder, sequencefile)
                            seqfiles = glob.glob(sequencepath)
                            if len(seqfiles) == 0:
                                sequencepath = cmds.workspace(expandName=sequencepath)
                                seqfiles = glob.glob(sequencepath)
                            if len(seqfiles) == 0:
                                resultList.append(TestResult(6004, 2, self, 'No sequence files found: ' + f, True, ['replaceAllMissing', allObjects[i]]))
                        else:
                            resultList.append(TestResult(6004, 2, self, 'File not found: ' + f, True, ['replaceAllMissing', allObjects[i]]))
                    elif 'maya/sourceimages/' + os.path.basename(f).lower() in ftpContentsFiles:
                        pos = ftpContentsFiles.index('maya/sourceimages/' + os.path.basename(f).lower())
                        if pos >= 0:
                            if myFileSize(f) != ftpContentsSizes[pos]:
                                resultList.append(TestResult(6006, 2, self, 'Texture "' + os.path.basename(f) + '" exported and used by other project. Please rename this texture', True, ['', allObjects[i]]))
                    if len(os.path.basename(f)) > 200:
                        resultList.append(TestResult(6023, 2, self, 'Texture name too long: "' + os.path.basename(f) + '"', False, 0))
                    relPath = getRelativePath(curWorkspace, f)
                    if relPath != '' and 0 <= os.path.dirname(f).lower().find('sourceimages') <= 2:
                        resultList.append(TestResult(6007, 2, self, 'Texture "' + os.path.basename(f) + '" is not in "sourceimages" folder', True, ['copyToSourceimages', 0]))
                    if f.endswith('.psd'):
                        resultList.append(TestResult(6008, 2, self, 'Filetype (psd) not supported: ' + f, True, ['', allObjects[i]]))
                    if isMovieTexture(os.path.splitext(f)[1]):
                        resultList.append(TestResult(6018, 2, self, 'Movie textures not supported, please use image sequences: ' + f, True, ['', allObjects[i]]))
                    if f.endswith('.ifl'):
                        for ff in getIflFilenames(f, fullPath=True):
                            if not existsFile(ff):
                                resultList.append(TestResult(6004, 2, self, 'Ifl entry not found: ' + ff, False, 0))

                alreadyChecked.append(f)
            i = i + 1

        if cmds.objExists('dynGlobals1'):
            if cmds.objExists('dynGlobals1.useParticleDiskCache'):
                if cmds.getAttr('dynGlobals1.useParticleDiskCache'):
                    cachedir = cmds.getAttr('dynGlobals1.cacheDirectory')
                    if cachedir == None:
                        resultList.append(TestResult(6009, 2, self, 'ParticleDiskCache is enabled but Directory not found', False, 0))
                    else:
                        self.particleDir = cachedir
                        if not existsFile(self.particleDir):
                            self.particleDir = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(rte='particles'), cachedir)
                        if not existsFile(self.particleDir):
                            self.particleDir = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='particles'), cachedir)
                        if not existsFile(self.particleDir):
                            resultList.append(TestResult(6010, 2, self, 'Particle folder not found: "' + self.particleDir + '"', False, 0))
                            debuglog('Error: particleDir not found ' + self.particleDir)
                        else:
                            debuglog('particleDir found ' + self.particleDir)
        vraymeshes = []
        try:
            vraymeshes = cmds.ls(et=['VRayMesh', 'VRayProxy'])
            if vraymeshes == None:
                vraymeshes = []
        except:
            vraymeshes = []

        for f in vraymeshes:
            if cmds.objExists(f + '.fileName'):
                path = cmds.getAttr(f + '.fileName')
                if path != '' and (path.find('%0') != -1 or path.find('<') != -1):
                    pre = os.path.basename(path)
                    specialChars = pre.find('%0')
                    if specialChars == -1:
                        specialChars = pre.find('<')
                    pre = pre[:specialChars]
                    folder = os.path.dirname(path)
                    if not existsFile(folder):
                        folder = os.path.join(cmds.workspace(q=1, rd=1), folder)
                    if not existsFile(folder):
                        resultList.append(TestResult(6019, 2, self, 'VRayMesh folder not found: "' + os.path.dirname(path) + '"', False, 0))
                        debuglog('Error: VRayMesh folder not found ' + path)
                    else:
                        localFiles = os.listdir(folder)
                        bFound = False
                        for ff in localFiles:
                            if ff.find(pre) == 0:
                                bFound = True

                        if not bFound:
                            resultList.append(TestResult(6020, 2, self, 'VRayMesh files not found: "' + path + '"', False, 0))

        vRayVolumeGrid = []
        try:
            vRayVolumeGrid = cmds.ls(et='VRayVolumeGrid')
            if vRayVolumeGrid == None:
                vRayVolumeGrid = []
        except:
            vRayVolumeGrid = []

        for f in vRayVolumeGrid:
            path = cmds.getAttr(f + '.inFile')
            if not existsFile(path):
                path = os.path.join(cmds.workspace(q=1, rd=1), path)
            if not existsFile(path):
                resultList.append(TestResult(6019, 2, self, 'VRayVolumeGrid not found: "' + cmds.getAttr(f + '.inFile') + '"', False, 0))

        fluidCaches = cmds.ls(et='diskCache')
        if fluidCaches == None:
            fluidCaches = []
        self.cacheFiles = []
        self.cacheObjects = []
        for f in fluidCaches:
            folder = os.path.dirname(cmds.getAttr(f + '.cacheName'))
            if not existsFile(folder):
                folder = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='diskCache'), os.path.basename(cmds.getAttr(f + '.cacheName')))
            if not existsFile(folder):
                resultList.append(TestResult(6011, 2, self, 'FluidCache folder not found: "' + cmds.getAttr(f + '.cacheName') + '"', False, 0))
                debuglog('Error: FluidCache folder not found ' + cmds.getAttr(f + '.cacheName'))
            elif os.path.isfile(folder):
                self.cacheFiles.append(folder)
                self.cacheObjects.append(f)
                debuglog('Cloth file found ' + folder)
            else:
                localFiles = os.listdir(folder)
                cname = os.path.basename(cmds.getAttr(f + '.cacheName'))
                if cname:
                    pos = cname.rfind('__')
                    if pos > 0:
                        cname = cname[0:pos - 1]
                        for l in localFiles:
                            if l[0:len(cname)] == cname:
                                self.cacheFiles.append(os.path.join(folder, l))

                        if len(self.cacheFiles) == 0:
                            resultList.append(TestResult(6012, 2, self, 'Fluid Cache files not found: "' + os.path.join(cmds.getAttr(f + '.cachePath'), cname) + '"', False, 0))
                        else:
                            self.cacheObjects.append(f)
                        debuglog('Cloth folder found ' + folder)
                    debuglog(localFiles)
                    debuglog(cname)

        clothCaches = cmds.ls(et='cacheFile')
        if clothCaches == None:
            clothCaches = []
        self.clothFiles = []
        self.clothObjects = []
        for f in clothCaches:
            folder = cmds.getAttr(f + '.cachePath')
            if not folder:
                continue
            if not existsFile(folder):
                folder = os.path.join(cmds.workspace(q=1, rd=1), cmds.workspace(fre='diskCache'), os.path.basename(cmds.getAttr(f + '.cachePath')))
            if not existsFile(folder):
                resultList.append(TestResult(6013, 2, self, 'Cache folder not found: "' + cmds.getAttr(f + '.cachePath') + '"', False, 0))
                debuglog('Error: Cache folder not found ' + cmds.getAttr(f + '.cachePath'))
            else:
                localFiles = os.listdir(folder)
                cname = cmds.getAttr(f + '.cacheName')
                if not cname:
                    continue
                if cname.find('$') >= 0:
                    cname = cname[:cname.find('$')]
                for l in localFiles:
                    if l[0:len(cname)] == cname:
                        self.clothFiles.append(os.path.join(folder, l))

                if len(self.clothFiles) == 0:
                    resultList.append(TestResult(6014, 2, self, 'Cache files not found: "' + os.path.join(cmds.getAttr(f + '.cachePath'), cname) + '"', False, 0))
                else:
                    self.clothObjects.append(f)
                debuglog('Cache folder found ' + folder)
                relPath = getRelativePath(curWorkspace, folder)
                debuglog(relPath + ' : Cache relPath')
                if relPath != '' and 'data' not in relPath and 'cache' not in relPath:
                    resultList.append(TestResult(6007, 2, self, 'Cache Base Directory must be set to "data" or "cache" for object "' + cname + '" ("' + folder + '")', False, 0))

        realflowMeshes = cmds.ls(et='RealflowMesh')
        if realflowMeshes == None:
            realflowMeshes = []
        for f in realflowMeshes:
            meshpath = cmds.getAttr(f + '.Path')
            folder = os.path.dirname(meshpath)
            framePadding = cmds.getAttr(f + '.framePadding')
            nameFormat = cmds.getAttr(f + '.nameFormat')
            if not folder:
                continue
            if not existsFile(folder):
                folder = os.path.join(cmds.workspace(q=1, rd=1), folder)
            if not existsFile(folder):
                resultList.append(TestResult(6013, 2, self, 'RealFlow Cache folder not found: "' + os.path.dirname(meshpath) + '"', False, 0))
            else:
                prefix = os.path.basename(meshpath)
                if nameFormat == 1:
                    prefix = prefix[0:-(0 + framePadding + 4)]
                else:
                    prefix = prefix[0:-(1 + framePadding + 4)]
                localFiles = glob.glob(os.path.join(folder, prefix + '*.bin'))
                if len(localFiles) == 0:
                    resultList.append(TestResult(6014, 2, self, 'RealFlow Cache files not found: "' + meshpath + '"', False, 0))

        bifrostCaches = []
        try:
            bifrostCaches = cmds.ls(et='bifrostContainer')
            if bifrostCaches == None:
                bifrostCaches = []
        except:
            pass

        self.bifrostFiles = []
        self.bifrostObjects = set()
        for f in bifrostCaches:
            cacheAttrs = [['cacheDir', 'cacheName', 'enableDiskCache'],
             ['liquidCachePath', 'liquidCacheFileName', 'enableLiquidCache'],
             ['solidCachePath', 'solidCacheFileName', 'enableSolidCache'],
             ['foamCachePath', 'foamCacheFileName', 'enableFoamCache']]
            for cacheDir, cacheName, enableCache in cacheAttrs:
                objattrs = cmds.listAttr(f)
                if cacheDir in objattrs and cacheName in objattrs and enableCache in objattrs:
                    folder = cmds.getAttr(f + '.' + cacheDir)
                    enabled = cmds.getAttr(f + '.' + enableCache)
                    if enabled == 0 or folder == None or curWorkspace == folder:
                        continue
                    if not existsFile(folder):
                        folder = os.path.join(cmds.workspace(q=1, rd=1), cmds.getAttr(f + '.' + cacheDir))
                    if not existsFile(folder):
                        resultList.append(TestResult(6013, 2, self, 'Cache folder not found: "' + cmds.getAttr(f + '.' + cacheDir) + '"', False, 0))
                        debuglog('Error: Cache folder not found ' + cmds.getAttr(f + '.' + cacheDir))
                    else:
                        localFiles = findFilesRecursive(folder)
                        cname = cmds.getAttr(f + '.' + cacheName)
                        bifrostFiles = []
                        for l in localFiles:
                            if l.find(cname) >= 0:
                                bifrostFiles.append(os.path.join(folder, l))

                        if len(bifrostFiles) == 0:
                            resultList.append(TestResult(6014, 2, self, 'Cache files not found: "' + os.path.join(cmds.getAttr(f + '.' + cacheDir), cname) + '"', False, 0))
                        else:
                            self.bifrostFiles += bifrostFiles
                            self.bifrostObjects.add(f)
                        debuglog('Cache folder found ' + folder)
                        relPath = getRelativePath(curWorkspace, folder)
                        if relPath == '':
                            resultList.append(TestResult(6014, 2, self, 'Bifrost Cache files must be within workspace: move "' + folder + '" to "' + curWorkspace + '"', False, 0))

        meshCaches = cmds.ls(type='mesh')
        if meshCaches == None:
            meshCaches = []
        self.meshCaches = []
        self.meshCacheSubfiles = []
        parserPath = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'mentalray', 'miparser' if cmds.about(mac=1) else 'miparser.exe')
        try:
            parserPath = parserPath.decode('utf-8', 'ignore')
        except:
            pass

        for f in meshCaches:
            if cmds.attributeQuery('miProxyFile', node=f, exists=True):
                meshpath = cmds.getAttr(f + '.miProxyFile')
                if meshpath != None:
                    if not existsFile(meshpath):
                        meshpath = os.path.join(cmds.workspace(q=1, rd=1), 'renderData', 'mentalRay', os.path.basename(meshpath))
                    if not existsFile(meshpath):
                        resultList.append(TestResult(6015, 2, self, 'MI proxy "' + mstr(cmds.getAttr(f + '.miProxyFile')) + '" not found.', False, 0))
                    else:
                        if not existsFile(parserPath):
                            resultList.append(TestResult(6015, 2, self, 'Please install the mentalray plugin in Render Farm Application if you want to use mr proxy files', False, 0))
                            break
                        miResult = getMentalrayParserResult(parserPath, meshpath, cmds.workspace(q=1, rd=1))
                        if miResult != None:
                            self.meshCaches.append(meshpath)
                            for item in miResult.get('texmissing', []):
                                resultList.append(TestResult(6015, 2, self, 'mi proxy: File "' + item + '" not found, referenced from "' + meshpath + '"', False, 0))

                            for item in miResult.get('tex', []):
                                self.meshCacheSubfiles.append(item)

                        else:
                            resultList.append(TestResult(6015, 2, self, 'Could not check proxy file "' + mstr(cmds.getAttr(f + '.miProxyFile')) + '"', False, 0))

        vrayScenes = cmds.ls(type='VRayScene')
        if vrayScenes == None:
            vrayScenes = []
        self.vrayScenes = []
        self.vraySceneSubfiles = []
        parserPath = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'vray', 'vrayparser' if cmds.about(mac=1) else 'vrayparser.exe')
        try:
            parserPath = parserPath.decode('utf-8', 'ignore')
        except:
            pass

        for f in vrayScenes:
            if cmds.attributeQuery('FilePath', node=f, exists=True):
                meshpath = cmds.getAttr(f + '.FilePath')
                if meshpath != None:
                    if not existsFile(meshpath):
                        meshpath = os.path.join(cmds.workspace(q=1, rd=1), 'renderData', 'mentalRay', os.path.basename(meshpath))
                    if not existsFile(meshpath):
                        resultList.append(TestResult(6015, 2, self, 'vrscene file "' + mstr(cmds.getAttr(f + '.FilePath')) + '" not found.', False, 0))
                    else:
                        if not existsFile(parserPath):
                            resultList.append(TestResult(6015, 2, self, 'Please install the vray plugin in Render Farm Application if you want to use vrscene files', False, 0))
                            break
                        miResult = getVrayParserResult(parserPath, meshpath, cmds.workspace(q=1, rd=1))
                        if miResult != None:
                            self.vrayScenes.append(meshpath)
                            for item in miResult.get('texmissing', []):
                                resultList.append(TestResult(6015, 2, self, 'vrscene: File "' + item + '" not found, referenced from "' + meshpath + '"', False, 0))

                            for item in miResult.get('tex', []):
                                self.vraySceneSubfiles.append(item)

                        else:
                            resultList.append(TestResult(6015, 2, self, 'Could not vrscene file "' + mstr(cmds.getAttr(f + '.FilePath')) + '"', False, 0))

        redshiftProxies = cmds.ls(type='RedshiftProxyMesh')
        if redshiftProxies == None:
            redshiftProxies = []
        self.redshiftProxies = []
        self.redshiftProxiesSubfiles = []
        parserPath = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'redshift', 'rsparser' if cmds.about(mac=1) else 'rsparser.exe')
        try:
            parserPath = parserPath.decode('utf-8', 'ignore')
        except:
            pass

        for f in redshiftProxies:
            meshpath = cmds.getAttr(f + '.fileName')
            if meshpath != None:
                if not existsFile(meshpath):
                    meshpath = os.path.join(cmds.workspace(q=1, rd=1), 'data', os.path.basename(meshpath))
                if not existsFile(meshpath):
                    resultList.append(TestResult(6015, 2, self, 'Redshift proxy "' + mstr(cmds.getAttr(f + '.fileName')) + '" not found.', False, 0))
                else:
                    if not existsFile(parserPath):
                        resultList.append(TestResult(6015, 2, self, 'Please install the redshift plugin in Render Farm Application if you want to use redshift proxy files', False, 0))
                        break
                    rsResult = getRedshiftParserResult(parserPath, meshpath, cmds.workspace(q=1, rd=1))
                    if rsResult != None:
                        if len(rsResult.get('success', [])) == 0:
                            resultList.append(TestResult(6015, 2, self, 'Something went wrong while checking proxy file. Make sure Redshift is installed "' + mstr(cmds.getAttr(f + '.fileName')) + '"', False, 0))
                        self.redshiftProxies.append((f, meshpath))
                        for item in rsResult.get('err', []):
                            resultList.append(TestResult(6015, 2, self, 'rs proxy ("' + f + '"): ' + item, False, 0))

                        for item in rsResult.get('tex', []):
                            self.redshiftProxiesSubfiles.append(item)

                    else:
                        resultList.append(TestResult(6015, 2, self, 'Could not check proxy file "' + mstr(cmds.getAttr(f + '.fileName')) + '"', False, 0))

        xgen = []
        try:
            xgen = cmds.ls(type='xgmPalette')
            if xgen == None:
                xgen = []
        except:
            pass

        for f in xgen:
            path = cmds.getAttr(f + '.xgFileName')
            if path == None or path == '':
                resultList.append(TestResult(6021, 2, self, 'xgen path empty for "' + f + '".xgFileName', False, 0))
            if not existsFile(path):
                path = os.path.join(cmds.workspace(q=1, rd=1), 'scenes', os.path.basename(path))
            if not existsFile(path):
                path = os.path.join(os.path.dirname(cmds.file(sceneName=True, q=1)), os.path.basename(path))
            if not existsFile(path):
                resultList.append(TestResult(6021, 2, self, 'xgen file not found "' + path + '".', False, 0))
            else:
                abcFiles = glob.glob(path[:-5] + '*.abc')
                if len(abcFiles) == 0:
                    resultList.append(TestResult(6022, 2, self, 'xgen Alembic files not found at "' + mstr(path[:-5] + '*.abc') + '".', True, ['xgen_alembic_missing', 0]))
                xgf = open(path, 'r')
                xgcontent = xgf.read()
                xgf.close()
                guideActivated = False
                regexSplineSettings = re.compile(urString('SplinePrimitive(.*?)endAttrs'), re.IGNORECASE | re.MULTILINE | re.DOTALL)
                for t in re.findall(regexSplineSettings, xgcontent):
                    regexMethod = re.compile(urString('iMethod\\s+1'), re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for m in re.findall(regexMethod, t):
                        guideActivated = True

                if guideActivated:
                    regexAbc = re.compile(urString('cacheFileName\\s*(.*)'), re.IGNORECASE | re.UNICODE)
                    filenames = re.findall(regexAbc, xgcontent)
                    for xpath in filenames:
                        mxpath = xpath.strip('"')
                        if not existsFile(mxpath):
                            mxpath = os.path.join(cmds.workspace(q=1, rd=1), 'scenes', os.path.basename(mxpath))
                        if not existsFile(path):
                            mxpath = os.path.join(os.path.dirname(cmds.file(sceneName=True, q=1)), os.path.basename(mxpath))
                        if not existsFile(mxpath):
                            resultList.append(TestResult(6024, 2, self, 'xgen cache file not found "' + xpath + '" in "' + path + '"', False, 0))

        fumeFX = []
        try:
            fumeFX = cmds.ls(type='ffxDyna')
            if fumeFX == None:
                fumeFX = []
        except:
            pass

        for f in fumeFX:
            if cmds.objExists(f + '.opath'):
                path = cmds.getAttr(f + '.opath')
                if path == '':
                    resultList.append(TestResult(6030, 2, self, 'FumeFX files not found "' + path + '"', False, 0))

        phoenixFD_caches = []
        try:
            phoenixFD_caches = cmds.ls(type='transform')
            if phoenixFD_caches == None:
                phoenixFD_caches = []
        except:
            pass

        for phxfd_object in phoenixFD_caches:
            if cmds.objExists(phxfd_object + '.inPathResolved'):
                path = cmds.getAttr(phxfd_object + '.inPathResolved')
                if path == '':
                    resultList.append(TestResult(6030, 2, self, 'PhoenixFD Simulation Save Path is empty.', False, 0))
                elif '$' in cmds.getAttr(phxfd_object + '.inPath'):
                    resultList.append(TestResult(6030, 2, self, 'PhoenixFD Output -> Simulation Save Path points to a non existing file. $(work_path)(or similar) might not work properly.\n "' + cmds.getAttr(phxfd_object + '.inPath') + '"', False, 0))

        references = []
        self.getAllReferences(references)
        for r in references:
            if not existsFile(r):
                resultList.append(TestResult(6016, 2, self, 'Referenced File not found (' + mstr(r) + ')', False, 0))
            if cmds.file(r, dr=1, q=1):
                resultList.append(TestResult(6017, 1, self, 'Referenced File is not loaded, please remove or activate (' + mstr(r) + ')', False, 0))
            if 'maya/scenes/' + os.path.basename(r).lower() in ftpContentsFiles:
                pos = ftpContentsFiles.index('maya/scenes/' + os.path.basename(r).lower())
                if pos >= 0:
                    if myFileSize(r) != ftpContentsSizes[pos]:
                        resultList.append(TestResult(6006, 2, self, 'Referenced file "' + os.path.basename(r) + '" exported and used by other project. Please rename this file or delete the other project from Render Farm Application', False, 0))

        crowdManagerNodes = []
        try:
            crowdManagerNodes = cmds.ls(type='CrowdManagerNode')
            if crowdManagerNodes == None:
                crowdManagerNodes = []
        except:
            crowdManagerNodes = []

        for f in crowdManagerNodes:
            crowdDirs = ['.escod']
            for setting, enabled in {'.efbxod': '.expEnableFbx',
             '.eabcod': '.expEnableAlembic',
             '.eribod': '.expEnableRib',
             '.emrod': '.expEnableMRay',
             '.evrod': '.expEnableVRay',
             '.eassod': '.expEnableArnold'}.items():
                try:
                    if cmds.getAttr(f + enabled):
                        crowdDirs.append(setting)
                except:
                    continue

            for cachdir in crowdDirs:
                cacheFileDir = cmds.getAttr(f + cachdir)
                os.path.exists(cacheFileDir)
                if not existsFile(cacheFileDir):
                    cacheFileDir = os.path.join(cmds.workspace(q=1, rd=1), cacheFileDir)
                if existsFile(cacheFileDir):
                    relPath = getRelativePath(curWorkspace, cacheFileDir)
                    if relPath == '':
                        resultList.append(TestResult(6025, 2, self, 'Golaem: Cache Directory must be inside your workspace found (' + mstr(cacheFileDir) + ')', False, 0))
                else:
                    resultList.append(TestResult(6025, 2, self, 'Golaem: Cache Directory not found (' + mstr(cacheFileDir) + ')', False, 0))

            characterFiles = cmds.getAttr(f + '.characterFiles')
            if not existsFile(characterFiles):
                cacheFileDir = os.path.join(cmds.workspace(q=1, rd=1), characterFiles)
            if not existsFile(characterFiles):
                resultList.append(TestResult(6025, 2, self, 'Golaem: Character files not found (' + mstr(characterFiles) + ')', False, 0))
            else:
                for gcha in getGchaAssets(characterFiles):
                    if not existsFile(gcha):
                        gcha = os.path.join(os.path.dirname(characterFiles), os.path.basename(gcha))
                    if not existsFile(gcha):
                        resultList.append(TestResult(6025, 2, self, 'Golaem: Character asset not found (' + mstr(gcha) + ') in (' + characterFiles + ')', False, 0))

        motionClip = []
        try:
            motionClip = cmds.ls(type='MotionClip')
            if motionClip == None:
                motionClip = []
        except:
            motionClip = []

        for f in motionClip:
            motionFile = cmds.getAttr(f + '.motionFile')
            if not existsFile(motionFile):
                motionFile = os.path.join(cmds.workspace(q=1, rd=1), motionFile)
            if not existsFile(motionFile):
                resultList.append(TestResult(6025, 2, self, 'Golaem: Motion file not found (' + mstr(motionFile) + ')', False, 0))

        resultList.append(TestResult(1, 0, self, self.getName() + '/Files have been checked', False, 0))
        return

    def furtherAction(self, result):
        if result.type[0] == 'copyToSourceimages':
            if cmds.confirmDialog(title='Message', message='All texture files have to be in the "sourceimages" folder of your project.\n\nDo you want to copy all files there automatically?\nA changed copy of your scene will be saved for you.', button=('Yes', 'No')) == 'Yes':
                allTextures, allObjects, allParams, allOptions = findAllTextures()
                i = 0
                curWorkspace = cmds.workspace(rd=True, q=True)
                imagefolder = os.path.join(curWorkspace, 'sourceimages')
                if not existsFile(imagefolder):
                    os.makedirs(imagefolder)
                for f in allTextures:
                    relPath = getRelativePath(curWorkspace, f)
                    if relPath != '' and os.path.basename(os.path.dirname(f)) != 'sourceimages':
                        if cmds.attributeQuery('useFrameExtension', node=allObjects[i], exists=True) and cmds.getAttr(allObjects[i] + '.useFrameExtension') == True:
                            sequencefile = os.path.basename(f)
                            sequencefile = parseSequence(sequencefile)
                            sequencefolder = os.path.dirname(f)
                            sequencepath = os.path.join(sequencefolder, sequencefile)
                            seqfiles = glob.glob(sequencepath)
                            if len(seqfiles) == 0:
                                sequencepath = cmds.workspace(expandName=sequencepath)
                                seqfiles = glob.glob(sequencepath)
                            for infile in seqfiles:
                                copyFile(mstr(infile), imagefolder)

                            cmds.setAttr(allParams[i], 'sourceimages/' + os.path.basename(mstr(f)), type='string')
                        else:
                            dest = os.path.join(imagefolder, os.path.basename(f))
                            debuglog('moving ' + f + ' to ' + dest)
                            copyFile(f, imagefolder)
                            cmds.setAttr(allParams[i], dest, type='string')
                    i = i + 1

                sceneName = getChangedMayaFilename()
                if sceneName[-9:] != 'Render-Farm-Application.mb':
                    sceneName = sceneName[0:-3] + 'Render-Farm-Application.mb'
                    cmds.file(rename=sceneName)
                cmds.file(save=True, type='mayaBinary')
                return True
        else:
            if result.type[0] == 'replaceAllMissing' and cmds.confirmDialog(title='Message', message='Do you want to replace all missing textures with a black 100x100 dummy texture?', button=('Yes', 'No')) == 'Yes':
                allTextures, allObjects, allParams, allOptions = findAllTextures()
                dummyfile = os.path.join(os.path.dirname(__file__), 'dummy.jpg')
                dummyvrmesh = os.path.join(os.path.dirname(__file__), 'dummy.vrmesh')
                i = 0
                for f in allTextures:
                    if not existsFile(f):
                        if not cmds.attributeQuery('miWritable', node=allObjects[i], exists=True):
                            debuglog('create dummy for ' + mstr(f))
                            newfile = dummyfile
                            if f != None and f.endswith('.vrmesh'):
                                newfile = dummyvrmesh
                            cmds.setAttr(allParams[i], newfile, type='string')
                    i += 1

                return True
            if result.type[0] == 'xgen_alembic_missing':
                import webbrowser
                url = 'http://docs.chaosgroup.com/display/VRAY3MAYA/XGen+in+Maya+Batch'
                webbrowser.open(url)
            else:
                maya.mel.eval('showEditor ' + result.type[1])
        return

    def prepareSave(self, path, vecFiles):
        mayafileName = os.path.basename(getChangedMayaFilename())
        curWorkspace = cmds.workspace(rd=True, q=True)
        destfolder = os.path.join(path, 'tex')
        workspacefolder = os.path.join(destfolder, 'maya')
        imagefolder = os.path.join(workspacefolder, 'sourceimages')
        particlesFolder = os.path.join(workspacefolder, 'particles', os.path.basename(self.particleDir))
        cacheFolder = os.path.join(workspacefolder, 'data')
        meshCacheFolder = os.path.join(workspacefolder, 'renderData', 'mentalRay')
        clothFolder = cacheFolder
        self.toRetarget = []
        if not existsFile(destfolder):
            os.makedirs(destfolder)
        if not existsFile(cacheFolder):
            os.makedirs(cacheFolder)
        if not existsFile(clothFolder):
            os.makedirs(clothFolder)
        allTextures, allObjects, allParams, allOptions = findAllTextures()
        self.createDummyWorkspace(destfolder, vecFiles)
        i = 0
        for f in allTextures:
            self.mainDialog.setStatus('Exporting Texture ' + str(i) + ' of ' + str(len(allTextures)))
            if cmds.attributeQuery('useFrameExtension', node=allObjects[i], exists=True) and cmds.getAttr(allObjects[i] + '.useFrameExtension') == True:
                sequencefile = os.path.basename(f)
                sequencefile = parseSequence(sequencefile)
                sequencefolder = os.path.dirname(f)
                sequencepath = os.path.join(sequencefolder, sequencefile)
                seqfiles = glob.glob(sequencepath)
                if len(seqfiles) == 0:
                    sequencepath = cmds.workspace(expandName=sequencepath)
                    seqfiles = glob.glob(sequencepath)
                for infile in seqfiles:
                    remotename = 'tex/maya/sourceimages/' + os.path.basename(mstr(infile))
                    appendFileInfo(vecFiles, remotename, mstr(infile))

                cmds.setAttr(allParams[i], 'sourceimages/' + os.path.basename(mstr(f)), type='string')
                self.toRetarget.append([allParams[i], f])
            elif cmds.attributeQuery('miWritable', node=allObjects[i], exists=True) and not existsFile(f):
                cmds.setAttr(allObjects[i] + '.miWritable', True)
                cmds.setAttr(allObjects[i] + '.miLocal', True)
                cmds.setAttr(allObjects[i] + '.fileTextureName', '', type='string')
            else:
                if cmds.attributeQuery('miLocal', node=allObjects[i], exists=True):
                    cmds.setAttr(allObjects[i] + '.miLocal', True)
                toCopy = True
                current_sourceimages_folder = os.path.join(curWorkspace, 'sourceimages')
                workspace_drive, _ = os.path.splitdrive(current_sourceimages_folder)
                file_drive, _ = os.path.splitdrive(f)
                if workspace_drive.lower() == file_drive.lower():
                    file_path_relative_to_sourceimages = os.path.relpath(os.path.join(curWorkspace, f), current_sourceimages_folder)
                else:
                    file_path_relative_to_sourceimages = ''
                if file_path_relative_to_sourceimages and os.path.exists(os.path.join(current_sourceimages_folder, file_path_relative_to_sourceimages)) and current_sourceimages_folder in f:
                    filename = mstr(file_path_relative_to_sourceimages.replace('\\', '/'))
                else:
                    filename = os.path.basename(mstr(f))
                if filename.endswith('.ifl'):
                    for ff in getIflFilenames(mstr(f), fullPath=True):
                        if existsFile(ff):
                            r = 'tex/maya/sourceimages/' + str(os.path.basename(ff))
                            appendFileInfo(vecFiles, r, ff)

                remotename = 'tex/maya/sourceimages/' + filename
                arnoldTx = mstr(f)
                arnoldTx = arnoldTx[:arnoldTx.rfind('.')] + '.tx'
                if existsFile(arnoldTx) and not isDir(arnoldTx):
                    r = 'tex/maya/sourceimages/' + os.path.basename(arnoldTx)
                    appendFileInfo(vecFiles, r, arnoldTx)
                if allOptions[i] != 2:
                    appendFileInfo(vecFiles, remotename, mstr(f), toCopy=toCopy)
                if len(allParams[i]) > 0:
                    if cmds.attributeQuery('ignoreColorSpaceFileRules', node=allObjects[i], exists=True):
                        cmds.setAttr(allObjects[i] + '.ignoreColorSpaceFileRules', True)
                        debuglog("The Farminizer has marked the checkbox 'Ignore Color Space File Rules' in every file node, so the selected color space will be taken on count during the rendering process.")
                        debuglog('Ignore Color Space File Rules state: ' + mstr(cmds.getAttr(str(allObjects[i] + '.ignoreColorSpaceFileRules'))))
                    if cmds.attributeQuery('uvTilingMode', node=allObjects[i], exists=True):
                        uvTilingTemp = cmds.getAttr(allObjects[i] + '.uvTilingMode')
                        if uvTilingTemp == 3:
                            udim_filename, udim_format = os.path.splitext(filename)
                            pattern = re.search('[0-9]{4,7}(?![0-9]$)', udim_filename)
                            filename = filename.replace(pattern.group(), '<UDIM>')
                    if allOptions[i] == False:
                        if uvTilingTemp == 3:
                            debuglog(allParams[i] + ' --> ' + createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', filename).replace('\\', '/'))
                            cmds.setAttr(allParams[i], createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', filename).replace('\\', '/'), type='string')
                            print ('UDIM:', cmds.getAttr(allParams[i]))
                            debuglog('state: ' + mstr(cmds.getAttr(allParams[i])))
                            uvTilingTemp = 0
                        else:
                            debuglog(allParams[i] + '-->sourceimages/' + filename)
                            cmds.setAttr(allParams[i], 'sourceimages/' + filename, type='string')
                            print ('NON-UDIM:', cmds.getAttr(allParams[i]))
                            debuglog('state: ' + mstr(cmds.getAttr(allParams[i])))
                    else:
                        debuglog(allParams[i] + ' --> ' + createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', filename).replace('\\', '/'))
                        cmds.setAttr(allParams[i], createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', filename).replace('\\', '/'), type='string')
                        debuglog('state: ' + mstr(cmds.getAttr(allParams[i])))
                    self.toRetarget.append([allParams[i], f])
            i += 1

        debuglog('copying... particles')
        if self.particleDir != '':
            if not existsFile(particlesFolder):
                os.makedirs(particlesFolder)
            for infile in glob.glob(os.path.join(self.particleDir, '*.*')):
                df = 'tex/maya/particles/' + os.path.basename(self.particleDir) + '/' + os.path.basename(infile)
                appendFileInfo(vecFiles, df, infile)

        debuglog('copying... fluids')
        for f in self.cacheFiles:
            destFileName = os.path.basename(mstr(f))
            destFileName = destFileName.replace('.ma_', '.mb_')
            df = 'tex/maya/data/' + destFileName
            appendFileInfo(vecFiles, df, f)

        try:
            iesfiles = cmds.ls(et='mentalrayLightProfile')
            if iesfiles == None:
                iesfiles = []
            for f in iesfiles:
                oldpath = mstr(cmds.getAttr(f + '.fileName'))
                cmds.setAttr(f + '.fileName', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(oldpath)).replace('\\', '/'), type='string')

        except:
            debuglog('Unexpected error:' + str(sys.exc_info()))

        debuglog('copying... cloth')
        for f in self.clothFiles:
            destFileName = os.path.basename(mstr(f))
            destFileName = destFileName.replace('.ma_', '.mb_')
            relative_file_path = getRelativePath(curWorkspace, os.path.dirname(f)).replace('..\\', '').replace('.\\', '')
            df = 'tex/maya/' + relative_file_path.replace('\\', '/') + '/' + destFileName
            appendFileInfo(vecFiles, df, f)

        for f in self.clothObjects:
            self.toRetarget.append([f + '.cachePath', cmds.getAttr(f + '.cachePath')])
            relative_file_path = getRelativePath(curWorkspace, os.path.dirname(cmds.getAttr(f + '.cachePath'))).replace('..\\', '').replace('.\\', '')
            debuglog('relative CachePath : ' + relative_file_path)
            cmds.setAttr(f + '.cachePath', relative_file_path.replace('\\', '/') + '/', type='string')

        vRayVolumeGrid = []
        try:
            vRayVolumeGrid = cmds.ls(et='VRayVolumeGrid')
            if vRayVolumeGrid == None:
                vRayVolumeGrid = []
        except:
            vRayVolumeGrid = []

        for f in vRayVolumeGrid:
            vRayVolumeGridPath = cmds.getAttr(f + '.inFile')
            if not existsFile(vRayVolumeGridPath):
                vRayVolumeGridPath = os.path.join(cmds.workspace(q=1, rd=1), vRayVolumeGridPath)
            if existsFile(vRayVolumeGridPath):
                inDontOfferPresets = cmds.getAttr(f + '.inDontOfferPresets')
                self.toRetarget.append([f + '.inFile', cmds.getAttr(f + '.inFile')])
                if not inDontOfferPresets:
                    self.toRetarget.append([f + '.inDontOfferPresets', False, True])
                    cmds.setAttr(f + '.inDontOfferPresets', True)
                appendFileInfo(vecFiles, 'tex/maya/sourceimages/' + os.path.basename(vRayVolumeGridPath), vRayVolumeGridPath)
                cmds.setAttr(f + '.inFile', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(vRayVolumeGridPath)).replace('\\', '/'), type='string')

        realflowMeshes = cmds.ls(et='RealflowMesh')
        if realflowMeshes == None:
            realflowMeshes = []
        for f in realflowMeshes:
            meshpath = cmds.getAttr(f + '.Path')
            folder = os.path.dirname(meshpath)
            framePadding = cmds.getAttr(f + '.framePadding')
            nameFormat = cmds.getAttr(f + '.nameFormat')
            if not folder:
                continue
            if not existsFile(folder):
                folder = os.path.join(cmds.workspace(q=1, rd=1), folder)
            if existsFile(folder):
                prefix = os.path.basename(meshpath)
                if nameFormat == 1:
                    prefix = prefix[0:-(0 + framePadding + 4)]
                else:
                    prefix = prefix[0:-(1 + framePadding + 4)]
                localFiles = glob.glob(os.path.join(folder, prefix + '*.bin'))
                if len(localFiles) > 0:
                    for ff in localFiles:
                        df = 'tex/maya/data/meshes/' + os.path.basename(ff)
                        appendFileInfo(vecFiles, df, ff)

                    cmds.setAttr(f + '.Path', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\meshes', os.path.basename(meshpath)).replace('\\', '/'), type='string')
                    self.toRetarget.append([f + '.Path', meshpath])

        debuglog('copying... alembics')
        self.alembic_objects = cmds.ls(et='AlembicNode')
        if self.alembic_objects == None:
            self.alembic_objects = []
        curWorkspace = cmds.workspace(rd=True, q=True)
        for alembic_object in self.alembic_objects:
            alembic_file = cmds.getAttr(alembic_object + '.fn').replace('\\', '/')
            relative_file_path = getRelativePath(curWorkspace, os.path.dirname(alembic_file)).replace('..\\', '').replace('.\\', '')
            debuglog(relative_file_path)
            destination_path = 'tex/maya/' + relative_file_path.replace('\\', '/') + '/' + os.path.basename(alembic_file)
            appendFileInfo(vecFiles, destination_path, alembic_file)
            cmds.setAttr(alembic_object + '.fn', createPath(self.mainDialog.m_userName, destination_path).replace('\\', '/'), type='string')
            if len(cmds.getAttr(alembic_object + '.fns')) > 0:
                cmds.setAttr(alembic_object + '.fns', 1, createPath(self.mainDialog.m_userName, destination_path).replace('\\', '/'), type='stringArray')
            self.toRetarget.append([alembic_object + '.fn', alembic_file])

        curWorkspace = cmds.workspace(rd=True, q=True)
        for f in self.bifrostFiles:
            rel = getRelativePath(curWorkspace, os.path.dirname(f))
            df = 'tex/maya/' + rel.replace('\\', '/') + '/' + os.path.basename(f)
            appendFileInfo(vecFiles, df, f)

        for f in self.bifrostObjects:
            cacheAttrs = ['cacheDir',
             'liquidCachePath',
             'solidCachePath',
             'foamCachePath']
            for cacheDir in cacheAttrs:
                objattrs = cmds.listAttr(f)
                if cacheDir in objattrs:
                    folder = cmds.getAttr(f + '.' + cacheDir)
                    if folder == None:
                        continue
                    if not existsFile(folder):
                        folder = os.path.join(cmds.workspace(q=1, rd=1), cmds.getAttr(f + '.' + cacheDir))
                    if existsFile(folder):
                        relPath = getRelativePath(curWorkspace, folder)
                        obj, pathtoset = f + '.' + cacheDir, createPath(self.mainDialog.m_userName + '\\tex\\maya', relPath).replace('\\', '/')
                        cmds.setAttr(obj, pathtoset, type='string')
                        self.toRetarget.append([f + '.' + cacheDir, folder])

        debuglog('copying... mrproxy')
        parserPath = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'mentalray', 'miparser' if cmds.about(mac=1) else 'miparser.exe')
        for f in self.meshCaches:
            dest = os.path.join(meshCacheFolder, os.path.basename(f))
            copyFile(f, meshCacheFolder)
            changeFileWithParser(parserPath, dest, createPath(self.mainDialog.m_userName + '\\tex\\maya', 'sourceimages').replace('\\', '/'), 'out')
            appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/' + os.path.basename(f), dest, toCopy=False)

        for f in self.meshCacheSubfiles:
            df = 'tex/maya/sourceimages/' + os.path.basename(f)
            appendFileInfo(vecFiles, df, f)

        debuglog('copying... vrscene')
        parserPath = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'vray', 'vrayparser' if cmds.about(mac=1) else 'vrayparser.exe')
        for f in self.vrayScenes:
            dest = os.path.join(imagefolder, os.path.basename(f))
            copyFile(f, imagefolder)
            changeFileWithParser(parserPath, dest, createPath(self.mainDialog.m_userName + '\\tex\\maya', 'sourceimages').replace('\\', '/'), 'out')
            appendFileInfo(vecFiles, 'tex/maya/sourceimages/' + os.path.basename(f), dest, toCopy=False)

        for f in self.vraySceneSubfiles:
            df = 'tex/maya/sourceimages/' + os.path.basename(f)
            appendFileInfo(vecFiles, df, f)

        debuglog('copying... rsproxy')
        parserPath = os.path.join(os.path.dirname(self.mainDialog.m_managerPath), 'plugins', 'redshift', 'rsparser' if cmds.about(mac=1) else 'rsparser.exe')
        for proxy, f in self.redshiftProxies:
            dest = os.path.join(imagefolder, os.path.basename(f))
            cmds.setAttr(proxy + '.fileName', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(f)).replace('\\', '/'), type='string')
            if cmds.getAttr(proxy + '.useFrameExtension') == 1:
                redshift_proxy_sequence = parseSequence(f)
                redshift_proxy_sequence_files = glob.glob(redshift_proxy_sequence)
                for redshift_proxy_sequence_file in redshift_proxy_sequence_files:
                    dest = os.path.join(imagefolder, os.path.basename(redshift_proxy_sequence_file).replace('\\', '/'))
                    copyFile(redshift_proxy_sequence_file, imagefolder)
                    changeFileWithParser(parserPath, dest, createPath(self.mainDialog.m_userName + '\\tex\\maya', 'sourceimages').replace('\\', '/'), 'out')
                    appendFileInfo(vecFiles, 'tex/maya/sourceimages/' + os.path.basename(redshift_proxy_sequence_file), dest, toCopy=False)

            else:
                copyFile(f, imagefolder)
                changeFileWithParser(parserPath, dest, createPath(self.mainDialog.m_userName + '\\tex\\maya', 'sourceimages').replace('\\', '/'), 'out')
                appendFileInfo(vecFiles, 'tex/maya/sourceimages/' + os.path.basename(f), dest, toCopy=False)
            self.toRetarget.append([proxy + '.fileName', f])

        for f in self.redshiftProxiesSubfiles:
            df = 'tex/maya/sourceimages/' + os.path.basename(f)
            appendFileInfo(vecFiles, df, f)

        debuglog('copying... xgen')
        xgen = []
        try:
            xgen = cmds.ls(type='xgmPalette')
            if xgen == None:
                xgen = []
        except:
            pass

        self.xgDestFile = []
        for f in xgen:
            xgpath = cmds.getAttr(f + '.xgFileName')
            if xgpath != None and xgpath != '':
                if not existsFile(xgpath):
                    xgpath = os.path.join(cmds.workspace(q=1, rd=1), 'scenes', os.path.basename(xgpath))
                if not existsFile(xgpath):
                    xgpath = os.path.join(os.path.dirname(cmds.file(sceneName=True, q=1)), os.path.basename(xgpath))
                if existsFile(xgpath):
                    df = 'tex/maya/scenes/' + os.path.basename(xgpath)
                    xgDestPath = os.path.join(path, 'tex/maya/scenes/')
                    copyFile(xgpath, xgDestPath)
                    self.xgDestFile.append(os.path.join(path, 'tex/maya/scenes/', os.path.basename(xgpath)))
                    self.toRetarget.append([f + '.xgFileName', cmds.getAttr(f + '.xgFileName')])
                    cmds.setAttr(f + '.xgFileName', os.path.basename(xgpath), type='string')
                    for abcf in glob.glob(xgpath[:-5] + '*.abc'):
                        df = 'tex/maya/scenes/' + os.path.basename(abcf)
                        appendFileInfo(vecFiles, df, abcf)

                    xgf = open(xgpath, 'r')
                    xgcontent = xgf.read()
                    xgf.close()
                    guideActivated = False
                    regexSplineSettings = re.compile(urString('SplinePrimitive(.*?)endAttrs'), re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for t in re.findall(regexSplineSettings, xgcontent):
                        regexMethod = re.compile(urString('iMethod\\s+1'), re.IGNORECASE | re.MULTILINE | re.DOTALL)
                        for m in re.findall(regexMethod, t):
                            guideActivated = True

                    if guideActivated:
                        regexAbc = re.compile(urString('cacheFileName\\s*(.*)'), re.IGNORECASE | re.UNICODE)
                        filenames = re.findall(regexAbc, xgcontent)
                        for xpath in filenames:
                            mxpath = xpath.strip('"')
                            if not existsFile(mxpath):
                                mxpath = os.path.join(cmds.workspace(q=1, rd=1), 'scenes', os.path.basename(mxpath))
                            if not existsFile(path):
                                mxpath = os.path.join(os.path.dirname(cmds.file(sceneName=True, q=1)), os.path.basename(mxpath))
                            if existsFile(mxpath):
                                df = 'tex/maya/sourceimages/' + os.path.basename(mxpath)
                                appendFileInfo(vecFiles, df, mxpath)

            xgpath = cmds.getAttr(f + '.xgBaseFile')
            if xgpath != None and xgpath != '':
                if not existsFile(xgpath):
                    xgpath = os.path.join(cmds.workspace(q=1, rd=1), 'scenes', os.path.basename(xgpath))
                if not existsFile(xgpath):
                    xgpath = os.path.join(os.path.dirname(cmds.file(sceneName=True, q=1)), os.path.basename(xgpath))
                if existsFile(xgpath):
                    df = 'tex/maya/scenes/' + os.path.basename(xgpath)
                    appendFileInfo(vecFiles, df, xgpath)
                    self.toRetarget.append([f + '.xgBaseFile', cmds.getAttr(f + '.xgBaseFile')])
                    cmds.setAttr(f + '.xgBaseFile', os.path.basename(xgpath), type='string')
                    for abcf in glob.glob(xgpath[:-5] + '*.abc'):
                        df = 'tex/maya/scenes/' + os.path.basename(abcf)
                        appendFileInfo(vecFiles, df, abcf)

            xgpath = cmds.getAttr(f + '.xgDeltaFiles')
            if xgpath != None and xgpath != '':
                files = []
                if len(xgpath) > 0 and existsFile(os.path.dirname(xgpath)):
                    files = glob.glob(xgpath.replace('.xgen', '') + '*')
                if len(files) == 0:
                    xgpath = os.path.join(cmds.workspace(q=1, rd=1), 'scenes', os.path.basename(xgpath))
                    files = glob.glob(xgpath.replace('.xgen', '') + '*')
                if len(files) == 0:
                    xgpath = os.path.join(os.path.dirname(cmds.file(sceneName=True, q=1)), os.path.basename(xgpath))
                    files = glob.glob(xgpath.replace('.xgen', '') + '*')
                if len(files) > 0:
                    for fp in files:
                        df = 'tex/maya/scenes/' + os.path.basename(fp)
                        appendFileInfo(vecFiles, df, fp)

                    self.toRetarget.append([f + '.xgDeltaFiles', cmds.getAttr(f + '.xgDeltaFiles')])
                    cmds.setAttr(f + '.xgDeltaFiles', os.path.basename(xgpath), type='string')

        if len(xgen) > 0:
            xgenroot = os.path.join(cmds.workspace(q=1, rd=1), 'xgen')
            if existsFile(xgenroot):
                destroot = 'tex/maya/xgen/'
                files = findFilesRecursive(xgenroot)
                for f in files:
                    df = destroot + f.replace('\\', '/')
                    appendFileInfo(vecFiles, df, os.path.join(xgenroot, f))

        if cmds.pluginInfo('xgenMR.py', query=True, loaded=True):
            self.xgenMRloaded = True
            cmds.unloadPlugin('xgenMR.py')
        xgen_geo = []
        try:
            xgen_geo = cmds.ls(type='xgen_geo')
            if xgen_geo == None:
                xgen_geo = []
        except:
            pass

        regexFileGeomPath = re.compile(urString('(-file|-geom)\\s*("[^"]*"|[^\\s]*)'), re.IGNORECASE | re.UNICODE)
        for f in xgen_geo:
            xgdata = cmds.getAttr(f + '.data')
            filenames = re.findall(regexFileGeomPath, xgdata)
            for ff in filenames:
                newpath = ff[1].replace('"', '')
                newpath = '${XGEN_ROOT}/../scenes/' + os.path.basename(newpath)
                xgdata = xgdata.replace(ff[1], '"' + newpath + '"')

            self.toRetarget.append([f + '.data', cmds.getAttr(f + '.data')])
            cmds.setAttr(f + '.data', xgdata, type='string')

        rootFolder = cmds.workspace(q=1, rd=1)
        if existsFile(rootFolder):
            furFiles = os.listdir(rootFolder)
            for l in furFiles:
                if l[0:len('fur')] == 'fur' and isDir(os.path.join(rootFolder, l)):
                    copyFolder(os.path.join(rootFolder, l), workspacefolder, vecFiles, 'tex/maya/' + l)

        rootFolder = os.path.join(rootFolder, 'renderData')
        if existsFile(rootFolder):
            furFiles = os.listdir(rootFolder)
            for l in furFiles:
                if l[0:len('fur')] == 'fur' and isDir(os.path.join(rootFolder, l)):
                    copyFolder(os.path.join(rootFolder, l), os.path.join(workspacefolder, 'renderData'), vecFiles, 'tex/maya/renderData/' + l)

        references = []
        self.getAllReferences(references)
        for r in references:
            if existsFile(r):
                df = 'tex/maya/scenes/' + os.path.basename(r)
                scenefolder = os.path.join(workspacefolder, 'scenes')
                appendFileInfo(vecFiles, df, r)

        debuglog('copying... vrmeshes')
        vraymeshes = []
        try:
            vraymeshes = cmds.ls(et='VRayMesh')
            if vraymeshes == None:
                vraymeshes = []
        except:
            vraymeshes = []

        for f in vraymeshes:
            if cmds.objExists(f + '.fileName'):
                path = cmds.getAttr(f + '.fileName')
                if path != '' and (path.find('%0') != -1 or path.find('<') != -1):
                    pre = os.path.basename(path)
                    specialChars = pre.find('%0')
                    if specialChars == -1:
                        specialChars = pre.find('<')
                    pre = pre[:specialChars]
                    folder = os.path.dirname(path)
                    if not existsFile(folder):
                        folder = os.path.join(cmds.workspace(q=1, rd=1), folder)
                    localFiles = os.listdir(folder)
                    for ff in localFiles:
                        if ff.find(pre) == 0:
                            fpath = os.path.join(folder, ff)
                            debuglog('copying ' + fpath + ' to ' + imagefolder)
                            df = 'tex/maya/sourceimages/' + ff
                            appendFileInfo(vecFiles, df, fpath)

                    cmds.setAttr(f + '.fileName', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(path)).replace('\\', '/'), type='string')
                    self.toRetarget.append([f + '.fileName', path])

        debuglog('copying... color management')
        try:
            colorpath = cmds.getAttr('defaultColorMgtGlobals.cfp')
            if existsFile(colorpath):
                df = 'tex/maya/sourceimages/' + os.path.basename(colorpath)
                appendFileInfo(vecFiles, df, colorpath)
                cmds.setAttr('defaultColorMgtGlobals.cfp', createPath(self.mainDialog.m_userName + '\\tex\\maya\\sourceimages', os.path.basename(colorpath)).replace('\\', '/'), type='string')
                self.toRetarget.append(['defaultColorMgtGlobals.cfp', colorpath])
                lutsFolder = os.path.join(os.path.dirname(colorpath), 'luts')
                if existsFile(lutsFolder):
                    for f in glob.glob(lutsFolder + '/*'):
                        df = 'tex/maya/sourceimages/luts/' + os.path.basename(f)
                        appendFileInfo(vecFiles, df, f)

        except:
            pass

        debuglog('copying... golaem')
        crowdManagerNodes = []
        try:
            crowdManagerNodes = cmds.ls(type='CrowdManagerNode')
            if crowdManagerNodes == None:
                crowdManagerNodes = []
        except:
            crowdManagerNodes = []

        for f in crowdManagerNodes:
            for cachdir in ['.escod',
             '.efbxod',
             '.eabcod',
             '.eribod',
             '.emrod',
             '.evrod',
             '.eassod']:
                try:
                    cacheFileDir = cmds.getAttr(f + cachdir)
                    if not existsFile(cacheFileDir):
                        cacheFileDir = os.path.join(cmds.workspace(q=1, rd=1), cacheFileDir)
                    if existsFile(cacheFileDir):
                        relPath = getRelativePath(curWorkspace, cacheFileDir).replace('..\\', '').replace('.\\', '')
                        copyFolder(cacheFileDir, os.path.join(workspacefolder, relPath.replace('\\', '/')), vecFiles, 'tex/maya/' + relPath.replace('\\', '/'))
                        self.toRetarget.append([f + cachdir, cmds.getAttr(f + cachdir)])
                        cmds.setAttr(f + cachdir, createPath(self.mainDialog.m_userName + '\\tex\\maya', relPath).replace('\\', '/'), type='string')
                except:
                    print cachdir
                    cacheFileDir == None

            isCharacterFilesLock = cmds.getAttr(f + '.characterFiles', lock=True)
            if not isCharacterFilesLock:
                characterFiles = cmds.getAttr(f + '.characterFiles')
                if not existsFile(characterFiles):
                    characterFiles = os.path.join(cmds.workspace(q=1, rd=1), characterFiles)
                if existsFile(characterFiles):
                    df = 'tex/maya/crowd/' + os.path.basename(characterFiles)
                    dest = os.path.join(destfolder, 'maya', 'crowd', os.path.basename(characterFiles))
                    shutil.copyfile(characterFiles, dest)
                    adjustGchaFile(dest, createPath(self.mainDialog.m_userName, 'tex\\maya\\crowd'))
                    appendFileInfo(vecFiles, df, dest, toCopy=False)
                    self.toRetarget.append([f + '.characterFiles', cmds.getAttr(f + '.characterFiles')])
                    cmds.setAttr(f + '.characterFiles', createPath(self.mainDialog.m_userName + '\\tex\\maya\\crowd', os.path.basename(characterFiles)).replace('\\', '/'), type='string')
                    for gcha in getGchaAssets(characterFiles):
                        if not existsFile(gcha):
                            gcha = os.path.join(os.path.dirname(characterFiles), os.path.basename(gcha))
                        if existsFile(gcha):
                            appendFileInfo(vecFiles, 'tex/maya/crowd/' + os.path.basename(gcha), gcha)

        debuglog('copying... golaem CrowdEntityTypeNode')
        CrowdEntityTypeNode = []
        try:
            CrowdEntityTypeNode = cmds.ls(type='CrowdEntityTypeNode')
            if CrowdEntityTypeNode == None:
                CrowdEntityTypeNode = []
        except:
            CrowdEntityTypeNode = []

        for f in CrowdEntityTypeNode:
            gch = cmds.getAttr(f + '.gch')
            df = 'tex/maya/crowd/' + os.path.basename(gch)
            dest = os.path.join(destfolder, 'maya', 'crowd', os.path.basename(gch))
            shutil.copyfile(gch, dest)
            adjustGchaFile(dest, createPath(self.mainDialog.m_userName, 'tex\\maya\\crowd'))
            appendFileInfo(vecFiles, df, dest, toCopy=False)
            self.toRetarget.append([f + '.gch', cmds.getAttr(f + '.gch')])
            cmds.setAttr(f + '.gch', createPath(self.mainDialog.m_userName + '\\tex\\maya\\crowd', os.path.basename(gch)).replace('\\', '/'), type='string')
            for gcha in getGchaAssets(gch):
                if not existsFile(gcha):
                    gcha = os.path.join(os.path.dirname(gch), os.path.basename(gcha))
                if existsFile(gcha):
                    appendFileInfo(vecFiles, 'tex/maya/crowd/' + os.path.basename(gcha), gcha)

        aiStandIn = []
        try:
            aiStandIn = cmds.ls(type='aiStandIn')
            if aiStandIn == None:
                aiStandIn = []
        except:
            aiStandIn = []

        reCacheFileDir = re.compile('\\ncacheFileDir\\s\\"(.*?)\\"')
        reCharacterFiles = re.compile('\\ncharacterFiles\\s\\"(.*?)\\"')
        for f in aiStandIn:
            ai_user_options = cmds.getAttr(f + '.ai_user_options')
            for ch in re.findall(reCacheFileDir, ai_user_options):
                relPath = getRelativePath(curWorkspace, ch)
                newPath = createPath(self.mainDialog.m_userName + '\\tex\\maya', relPath).replace('\\', '/')
                ai_user_options = ai_user_options.replace(ch, newPath)

            for ch in re.findall(reCharacterFiles, ai_user_options):
                newPath = createPath(self.mainDialog.m_userName + '\\tex\\maya\\crowd', os.path.basename(ch)).replace('\\', '/')
                ai_user_options = ai_user_options.replace(ch, newPath)

            self.toRetarget.append([f + '.ai_user_options', cmds.getAttr(f + '.ai_user_options')])
            cmds.setAttr(f + '.ai_user_options', ai_user_options, type='string')

        debuglog('copying... golaem simulation layout')
        simulationCacheProxyNode = []
        try:
            simulationCacheProxyNode = cmds.ls(type='SimulationCacheProxy')
            if simulationCacheProxyNode == None:
                simulationCacheProxyNode = []
        except:
            simulationCacheProxyNode = []

        for f in simulationCacheProxyNode:
            if cmds.getAttr(f + '.enableLayout') == True:
                layoutFiles = cmds.getAttr(f + '.layoutFile')
                multipleLayouts = layoutFiles.split(';')
                for layout in range(len(multipleLayouts)):
                    if not existsFile(multipleLayouts[layout]):
                        print "Cache didn't exists"
                        multipleLayouts[layout] = os.path.join(cmds.workspace(q=1, rd=1), multipleLayouts[layout])
                    if existsFile(multipleLayouts[layout]):
                        df = 'tex/maya/crowd/' + os.path.basename(multipleLayouts[layout])
                        appendFileInfo(vecFiles, df, multipleLayouts[layout])
                        self.toRetarget.append([f + '.layoutFiles[{}].path'.format(layout), cmds.getAttr(f + '.layoutFiles[{}].path'.format(layout))])
                        cmds.setAttr(f + '.layoutFiles[{}].path'.format(layout), createPath(self.mainDialog.m_userName + '\\tex\\maya\\crowd', os.path.basename(multipleLayouts[layout])).replace('\\', '/'), type='string')

        debuglog('copying... golaem motion')
        motionClip = []
        try:
            motionClip = cmds.ls(type='MotionClip')
            if motionClip == None:
                motionClip = []
        except:
            motionClip = []

        for f in motionClip:
            motionFile = cmds.getAttr(f + '.motionFile')
            if not existsFile(motionFile):
                motionFile = os.path.join(cmds.workspace(q=1, rd=1), motionFile)
            if existsFile(motionFile):
                df = 'tex/maya/crowd/' + os.path.basename(motionFile)
                appendFileInfo(vecFiles, df, motionFile)
                self.toRetarget.append([f + '.motionFile', cmds.getAttr(f + '.motionFile')])
                cmds.setAttr(f + '.motionFile', createPath(self.mainDialog.m_userName + '\\tex\\maya\\crowd', os.path.basename(motionFile)).replace('\\', '/'), type='string')

        alembic_objects = []
        try:
            alembic_objects = cmds.ls(type='AlembicNode')
            if alembic_objects == None:
                alembic_objects = []
        except:
            pass

        for alembic_object in alembic_objects:
            if cmds.objExists(alembic_object + '.fn'):
                path = cmds.getAttr(alembic_object + '.fn')
                if path != '':
                    path = os.path.dirname(path) + '/*.*'
                else:
                    resultList.append(TestResult(6030, 2, self, 'Alembic files not found "' + path + '"', False, 0))

        fume_fx = cmds.ls(type='ffxDyna')
        if fume_fx == None:
            fume_fx = []
        for f in fume_fx:
            fumefx_path = cmds.getAttr(f + '.opath')
            opath_filename = os.path.basename(cmds.getAttr(f + '.opath'))
            ppopath_filename = os.path.basename(cmds.getAttr(f + '.ppopath'))
            wopath_filename = os.path.basename(cmds.getAttr(f + '.wopath'))
            ropath_filename = os.path.basename(cmds.getAttr(f + '.ropath'))
            iopa_filename = os.path.basename(cmds.getAttr(f + '.iopa'))
            pt_im_filename = os.path.basename(cmds.getAttr(f + '.pt_im'))
            pt_mb_filename = os.path.basename(cmds.getAttr(f + '.pt_mb'))
            folder = os.path.dirname(os.path.normpath(fumefx_path))
            if folder != '':
                fume_fx_source_folder = os.path.basename(folder)
            else:
                print 'folder empty'
            if not folder:
                continue
            if not existsFile(folder):
                folder = os.path.join(cmds.workspace(q=1, rd=1), folder)
            if existsFile(folder):
                localFiles = glob.glob(os.path.join(folder, '*.*'))
                if len(localFiles) > 0:
                    for ff in localFiles:
                        df = 'tex/maya/data/' + fume_fx_source_folder + '/' + os.path.basename(ff)
                        appendFileInfo(vecFiles, df, ff)

                    cmds.setAttr(f + '.opath', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, opath_filename).replace('\\', '/'), type='string')
                    cmds.setAttr(f + '.ppopath', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, ppopath_filename).replace('\\', '/'), type='string')
                    cmds.setAttr(f + '.wopath', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, wopath_filename).replace('\\', '/'), type='string')
                    cmds.setAttr(f + '.ropath', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, ropath_filename).replace('\\', '/'), type='string')
                    cmds.setAttr(f + '.iopa', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, iopa_filename).replace('\\', '/'), type='string')
                    cmds.setAttr(f + '.pt_im', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, pt_im_filename).replace('\\', '/'), type='string')
                    cmds.setAttr(f + '.pt_mb', createPath(self.mainDialog.m_userName + '\\tex\\maya\\data\\' + fume_fx_source_folder, pt_mb_filename).replace('\\', '/'), type='string')
                    self.toRetarget.append([f + '.opath', fumefx_path])

        phoenixFD_cache_objects = cmds.ls(type='transform')
        if phoenixFD_cache_objects == None:
            phoenixFD_cache_objects = []
        for phoenixFD_cache_object in phoenixFD_cache_objects:
            if cmds.objExists(phoenixFD_cache_object + '.inPath'):
                phoenixFD_original_path = cmds.getAttr(phoenixFD_cache_object + '.inPath')
                phoenixFD_cache_path = cmds.getAttr(phoenixFD_cache_object + '.inPathResolved')
                if existsFile(phoenixFD_cache_path):
                    phoenixFD_cache_files = glob.glob(parseSequence(phoenixFD_cache_path))
                    phoenixFD_filename = parseSequence(os.path.basename(phoenixFD_cache_path), wildcard='#', single_replace=False)
                    phoenixFD_last_dirname = os.path.basename(os.path.dirname(phoenixFD_cache_path))
                    cmds.setAttr(phoenixFD_cache_object + '.inPath', os.path.normpath(createPath(self.mainDialog.m_userName + '/tex/maya/data/' + phoenixFD_last_dirname + '/', phoenixFD_filename)).replace('\\', '/'), type='string')
                    if len(phoenixFD_cache_files) > 0:
                        for phoenixFD_cache_file in phoenixFD_cache_files:
                            destination_path = 'tex/maya/data/' + phoenixFD_last_dirname + '/' + os.path.basename(phoenixFD_cache_file)
                            appendFileInfo(vecFiles, destination_path, phoenixFD_cache_file)

                        self.toRetarget.append([phoenixFD_cache_object + '.inPath', phoenixFD_original_path])

        return ''

    def createDummyFileFolder(self, path, folder):
        destfolder = os.path.join(path, folder)
        if not existsFile(destfolder):
            os.makedirs(destfolder)
        destfile = os.path.join(destfolder, 'farm')
        if not existsFile(destfile):
            f = open(destfile, 'w')
            f.close()

    def createDummyWorkspace(self, path, vecFiles):
        workspacefolder = os.path.join(path, 'maya')
        if not existsFile(workspacefolder):
            os.makedirs(workspacefolder)
        self.createDummyFileFolder(workspacefolder, 'assets')
        appendFileInfo(vecFiles, 'tex/maya/assets/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'crowd')
        appendFileInfo(vecFiles, 'tex/maya/crowd/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'data')
        appendFileInfo(vecFiles, 'tex/maya/data/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(os.path.join(workspacefolder, 'data'), 'ncloth')
        appendFileInfo(vecFiles, 'tex/maya/data/ncloth/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'fur')
        appendFileInfo(vecFiles, 'tex/maya/fur/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'images')
        appendFileInfo(vecFiles, 'tex/maya/images/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'particles')
        appendFileInfo(vecFiles, 'tex/maya/particles/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'renderData')
        appendFileInfo(vecFiles, 'tex/maya/renderData/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(os.path.join(workspacefolder, 'renderData'), 'mentalRay')
        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(os.path.join(workspacefolder, 'renderData', 'mentalRay'), 'finalgMap')
        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/finalgMap/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(os.path.join(workspacefolder, 'renderData', 'mentalRay'), 'photonMap')
        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/photonMap/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(os.path.join(workspacefolder, 'renderData', 'mentalRay'), 'shadowMap')
        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/shadowMap/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(os.path.join(workspacefolder, 'renderData', 'mentalRay'), 'lightMap')
        appendFileInfo(vecFiles, 'tex/maya/renderData/mentalRay/lightMap/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'renderScenes')
        appendFileInfo(vecFiles, 'tex/maya/renderScenes/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'scenes')
        appendFileInfo(vecFiles, 'tex/maya/scenes/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'sourceimages')
        appendFileInfo(vecFiles, 'tex/maya/sourceimages/farm', '', fileSize=0, toCopy=False)
        self.createDummyFileFolder(workspacefolder, 'textures')
        appendFileInfo(vecFiles, 'tex/maya/textures/farm', '', fileSize=0, toCopy=False)

    def postMayaFileSave(self, fname, vecFiles):
        regexProjPath = re.compile(urString('xgProjectPath\\s*(.*?)\\s*\\n'), re.IGNORECASE)
        for xgDestFile in self.xgDestFile:
            fh = open(xgDestFile)
            content = fh.read()
            fh.close()
            filenames = re.findall(regexProjPath, content)
            for ff in filenames:
                newPath = createPath(self.mainDialog.m_userName + '\\tex', 'maya\\').replace('\\', '/')
                content = content.replace(ff, newPath)

            fh = open(xgDestFile, 'w')
            fh.write(content)
            fh.close()
            df = 'tex/maya/scenes/' + os.path.basename(xgDestFile)
            appendFileInfo(vecFiles, df, xgDestFile, toCopy=False)

        self.xgDestFile = []

    def postSave(self):
        for f in self.toRetarget:
            if f[1] != None:
                if len(f) < 3:
                    cmds.setAttr(f[0], f[1], type='string')
                    print cmds.getAttr(f[0])
                else:
                    cmds.setAttr(f[0], f[1])
                    print cmds.getAttr(f[0])

        if self.xgenMRloaded:
            cmds.loadPlugin('xgenMR.py')
        return
