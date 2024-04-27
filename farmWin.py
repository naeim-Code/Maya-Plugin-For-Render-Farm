from octane import *
import octane
from redshift import *
import redshift
from renderman import *
import renderman
from iray import *
import iray
from arnold import *
import arnold
from maxwell import *
import maxwell
from vray import *
import vray
from fr import *
import fr
from mental import *
import mental
from texture import *
import texture
from rendersettings import *
import rendersettings
from general import *
import general 
from utilitis import *
from val_arnold import *
import val_arnold

 

import maya.cmds as cmds
import math
import os
import ssl
import urllib
import time
import sys
import subprocess
import webbrowser
import threading
import json 
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt
import shiboken2
import maya.cmds as cmds  

import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QPalette, QColor
from PySide2.QtCore import Qt
import shiboken2
import maya.cmds as cmds
import farmWin
import farm 
import sys 
import webbrowser
 
combo_box = QtWidgets.QComboBox()
index=0
class MyWindow(QtWidgets.QDialog):
    def __init__(self, parent=None,style=""):
        super(MyWindow, self).__init__(parent)
         
        self.setGeometry(200, 200, 1000, 540)

        self.dragPosition = None
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        image_path = 'C:/Users/nnn/Desktop/sky_back.jpg'

        pixmap = QtGui.QPixmap(image_path)
        self.label = QtWidgets.QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        
        self.close_button = QtWidgets.QPushButton(self)
        self.close_button.setGeometry(QtCore.QRect(960, 10, 30, 30))
        self.close_button.setText("X")
        self.close_button.clicked.connect(self.close)

        

        # QComboBox  Create
     

        # Connect the combo box signal to the print_selected_item function
        global combo_box
        combo_box = QtWidgets.QComboBox(self)
        combo_box.addItems(['Bronze', 'Silver', 'Gold'])
        combo_box.setGeometry(298, 200, 160, 20)
        combo_box.setProperty("styleSheet",style) 
        combo_box.setCurrentIndex(index)
        combo_box.currentIndexChanged.connect(selected_item)
        

        # QCheckBox Create         
        self.check_box = QtWidgets.QCheckBox(  self)
        self.check_box.setGeometry(422, 257, 14, 14)
        self.check_box.setStyleSheet("QCheckBox{background-color:#ffffff;}" )        
        
        # QCheckBox Create         
        self.check_box = QtWidgets.QCheckBox(  self)
        self.check_box.setGeometry(422, 286, 14, 14)
        self.check_box.setStyleSheet("QCheckBox{background-color:#ffffff;}")   
        
        # QCheckBox Create         
        self.check_box = QtWidgets.QCheckBox(  self)
        self.check_box.setGeometry(422, 320, 14, 14)
        self.check_box.setStyleSheet("QCheckBox{background-color:#ffffff;}" )  
        
        
        # QCheckBox Create         
        self.check_box = QtWidgets.QCheckBox(  self)
        self.check_box.setGeometry(666, 198, 14 ,14)
        self.check_box.setStyleSheet("QCheckBox{background-color:#ffffff;}")  
        
        # QCheckBox Create         
        self.check_box = QtWidgets.QCheckBox(  self)
        self.check_box.setGeometry(666, 232,14 ,14)
        self.check_box.setStyleSheet("QCheckBox{background-color:#ffffff;}" )  
       
        # Send Button Options
        self.btnSend = QtWidgets.QPushButton(self)
        self.btnSend.setGeometry(540, 348, 160, 44)
        self.btnSend.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Send_n.jpg'))
        self.btnSend.setIconSize(QtCore.QSize(160, 44))
        self.btnSend.clicked.connect(shelfRenderNow)
        
        # Analyze Button Options
        self.btnAnalyze = QtWidgets.QPushButton(self)
        self.btnAnalyze.setGeometry(540, 286, 160, 44)
        self.btnAnalyze.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Analyze_n.jpg'))
        self.btnAnalyze.setIconSize(QtCore.QSize(160, 44))
        self.btnAnalyze.clicked.connect(QuickCheck)
        
        # Cost Calculate Button Options
        self.btnCalc = QtWidgets.QPushButton(self)
        self.btnCalc.setGeometry(303, 397, 160, 44)
        self.btnCalc.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Cost_n.jpg'))
        self.btnCalc.setIconSize(QtCore.QSize(160, 44))
        self.btnCalc.clicked.connect(CostCalculate)
        
        # Dashboard Button Options
        self.btnDashboard = QtWidgets.QPushButton(self)
        self.btnDashboard.setGeometry(65, 275, 160, 44)
        self.btnDashboard.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Dashboard_n.jpg'))
        self.btnDashboard.setIconSize(QtCore.QSize(160, 44))
        self.btnDashboard.clicked.connect(Dashboard)
        
        # Credit Button Options
        self.btnCredit = QtWidgets.QPushButton(self)
        self.btnCredit.setGeometry(65, 345, 160, 44)
        self.btnCredit.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/BuyCredits_n.jpg'))
        self.btnCredit.setIconSize(QtCore.QSize(160, 44))
        self.btnCredit.clicked.connect(Credit)
        
        # Adding events to buttons
        self.btnSend.installEventFilter(self)      
        self.btnAnalyze.installEventFilter(self) 
        self.btnCalc.installEventFilter(self) 
        self.btnDashboard.installEventFilter(self) 
        self.btnCredit.installEventFilter(self) 
        
        userName = ''
        defaultPath = ''
        managerPath = ''
        PluginVersion = ''
        conf = getConfigFileContent()
        if len(conf) >= 4:
            userName = conf[0]
            defaultPath = conf[1]
            managerPath = conf[2]
            PluginVersion = conf[3]
        
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(68 ,206 ,160 ,44)
        self.label.setText(userName)
        self.label.setStyleSheet("color: #fff;")
        
    
    # Send buttons event   
    def eventFilter(self, obj, event):
        # Start Send Button Events
        if obj == self.btnSend and event.type() == QtCore.QEvent.MouseButtonPress:
            self.btnSend.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Send_d.jpg'))
            
        elif obj == self.btnSend and event.type() == QtCore.QEvent.MouseButtonRelease:
            self.btnSend.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Send_n.jpg'))
            
        elif obj == self.btnSend and event.type() == QtCore.QEvent.Enter:
            self.btnSend.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Send_o.jpg'))
            
        elif obj == self.btnSend and event.type() == QtCore.QEvent.Leave:
            self.btnSend.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Send_n.jpg')) 
        # End Send Button Events
        
        
        # Start Analyze Button Events            
        elif obj == self.btnAnalyze and event.type() == QtCore.QEvent.MouseButtonPress:
            self.btnAnalyze.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Analyze_d.jpg'))
            
        elif obj == self.btnAnalyze and event.type() == QtCore.QEvent.MouseButtonRelease:
            self.btnAnalyze.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Analyze_n.jpg'))
            
        elif obj == self.btnAnalyze and event.type() == QtCore.QEvent.Enter:
            self.btnAnalyze.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Analyze_o.jpg'))
            
        elif obj == self.btnAnalyze and event.type() == QtCore.QEvent.Leave:
            self.btnAnalyze.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Analyze_n.jpg'))
        # End Analyze Button Events
            
            
        # Start Calculate Button Events   
        elif obj == self.btnCalc and event.type() == QtCore.QEvent.MouseButtonPress:
            self.btnCalc.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Cost_d.jpg'))
            
        elif obj == self.btnCalc and event.type() == QtCore.QEvent.MouseButtonRelease:
            self.btnCalc.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Cost_n.jpg'))
            
        elif obj == self.btnCalc and event.type() == QtCore.QEvent.Enter:
            self.btnCalc.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Cost_o.jpg'))
            
        elif obj == self.btnCalc and event.type() == QtCore.QEvent.Leave:
            self.btnCalc.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Cost_n.jpg'))
        # End Calculate Button Events   
        
        
        # Start Dashboard Button Events   
        elif obj == self.btnDashboard and event.type() == QtCore.QEvent.MouseButtonPress:
            self.btnDashboard.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Dashboard_d.jpg'))
            
        elif obj == self.btnDashboard and event.type() == QtCore.QEvent.MouseButtonRelease:
            self.btnDashboard.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Dashboard_n.jpg'))
            
        elif obj == self.btnDashboard and event.type() == QtCore.QEvent.Enter:
            self.btnDashboard.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Dashboard_o.jpg'))
            
        elif obj == self.btnDashboard and event.type() == QtCore.QEvent.Leave:
            self.btnDashboard.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/Dashboard_n.jpg'))
        # End Dashboard Button Events   
        
        
        # Start Credit Button Events   
        elif obj == self.btnCredit and event.type() == QtCore.QEvent.MouseButtonPress:
            self.btnCredit.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/BuyCredits_d.jpg'))
            
        elif obj == self.btnCredit and event.type() == QtCore.QEvent.MouseButtonRelease:
            self.btnCredit.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/BuyCredits_n.jpg'))
            
        elif obj == self.btnCredit and event.type() == QtCore.QEvent.Enter:
            self.btnCredit.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/BuyCredits_o.jpg'))
            
        elif obj == self.btnCredit and event.type() == QtCore.QEvent.Leave:
            self.btnCredit.setIcon(QtGui.QIcon('C:/Users/nnn/Desktop/Bottuns/BuyCredits_n.jpg'))
        # End Credit Button Events   
         
         
        return super(MyWindow, self).eventFilter(obj, event)
 
    
  
    def mousePressEvent(self, event):
        self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self.dragPosition is not None:
            self.move(event.globalPos() - self.dragPosition)
        event.accept()


def shelfRenderNow():
    farmWin.initWindow()
    farmWin.actionExport()
        
def QuickCheck():
    shelfCheckScene()
        
def CostCalculate():
    webbrowser.open('https://google.com')
        
def Dashboard():
    webbrowser.open('https://google.com')
        
def Credit():
    webbrowser.open('https://google.com')

def selected_item():
    print(combo_box.currentText())


def maya_main_window():
    """
    Get the main window as a QMainWindow instance
    @return: QMainWindow instance of Maya's main window
    """    
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow )

def show_window():
    """
    Create instance of the window and show it
    """ 
    style_sheet = " QComboBox {  background-color: #336699;   color: white;   border: 2px solid #336699;     selection-background-color: #99CCFF;  } "
    global my_window
    my_window = MyWindow(parent=maya_main_window(),style=style_sheet)
    my_window.show()
 


import utilitis
 

class AboutDialog(object):

    def __init__(self):
        pass

    def show(self): 
        userName = ''
        defaultPath = ''
        managerPath = ''
        PluginVersion = ''
        conf = getConfigFileContent()
        if len(conf) >= 4:
            userName = conf[0]
            defaultPath = conf[1]
            managerPath = conf[2]
            PluginVersion = conf[3]
          

class PreUpload(object):
    dlg = 0

    def __init__(self, dlg):
        self.dlg = dlg

    def getName(self):
        return 'PreUpload'

    def furtherAction(self, result):
        pass


class CheckDone(object):
    dlg = 0

    def __init__(self, dlg):
        self.dlg = dlg

    def getName(self):
        return 'CheckComplete'

    def furtherAction(self, result):
        pass


class ListDialog(object):
    vecTests = []
    vecResults = []
    mapListResult = []
    vecLayerinfos = []
    isVrsceneExport = False
    isMiExport = False
    m_userName = ''
    m_defaultPath = ''
    m_managerPath = ''
    m_PluginVersion = ''
    m_CpuData = ''
    listbox = ''
    userTextBox = ''
    progressTextBox = ''
    progressTxt = ''
    lastRefresh = 0
    rendererSelect = ''
    rendererSoftware = 'Software'
    rendererMental = 'Mental Ray'
    rendererFR = 'Final Render'
    rendererMaxwell = 'Maxwell'
    rendererArnold = 'Arnold'
    rendererRenderman = 'Renderman'
    rendererIray = 'Iray'
    rendererRedshift = 'redshift'
    gpu_enabled = False
    try:
        if cmds.getAttr('defaultArnoldRenderOptions.renderDevice'):
            gpu_enabled = True
    except:
        pass

    rtx_enabled = False
    liveExport = ''
    m_chkAll = True
    m_chkErr = False
    m_chkWar = False
    clrActive = (0.6, 0.6, 0.6)
    clrInactive = (1, 1, 1)
    m_window = ''
    estimateEnabled = False

    def initWindow(self):
        frame_width = 850 
        self.m_window = cmds.window('Render Farm Application', title='Farm Analyze', width=frame_width, height=350)
        form = cmds.formLayout(numberOfDivisions=100)
        self.listbox = cmds.textScrollList(numberOfRows=20, width=frame_width - 10, allowMultiSelection=False, selectCommand=self.onListSelected)
        self.progressTextBox = cmds.text('progressTextBox', label='', height=50)
        self.send_render_btn = cmds.button('send_render_btn', label='Submit to Farm', command=self.submitToSky, height=50, enable=False, visible=False)
        cmds.formLayout(form, edit=True, attachForm=[(self.progressTextBox, 'bottom', 5),
         (self.listbox, 'top', 5),
         (self.listbox, 'left', 5),
         (self.listbox, 'right', 5),
         (self.send_render_btn, 'right', 5),
         (self.send_render_btn, 'bottom', 5)], attachControl=[(self.listbox,
          'bottom',
          5,
          self.progressTextBox), (self.progressTextBox,
          'left',
          5,
          self.send_render_btn)])
        cmds.showWindow(self.m_window)

    def __init__(self):
        conf = getConfigFileContent()
        if len(conf) >= 4:
            self.m_userName = conf[0]
            self.m_defaultPath = conf[1]
            self.m_managerPath = conf[2]
            self.m_PluginVersion = conf[3]
            self.m_CpuData = ''
            if len(conf) >= 5:
                self.m_CpuData = conf[4]
        self.vecTests = []
        v = ValGeneral(self)
        self.vecTests.append(v)
        v = ValRendersettings(self)
        self.vecTests.append(v)
        v = ValTexture(self)
        v.managerPath = self.m_managerPath
        v.defaultPath = self.m_defaultPath
        self.vecTests.append(v)
        v = ValMental(self)
        self.vecTests.append(v)
        v = ValFR(self)
        self.vecTests.append(v)
        v = ValVray(self)
        self.vecTests.append(v)
        v = ValMaxwell(self)
        self.vecTests.append(v)
        v = ValArnold(self)
        self.vecTests.append(v)
        v = ValRenderman(self)
        self.vecTests.append(v)
        v = ValIray(self)
        self.vecTests.append(v)
        v = ValRedshift(self)
        self.vecTests.append(v)
        v = ValOctane(self)
        self.vecTests.append(v) 
        self.setFileModifiedConditionAndCallback()

    def disableSendRenderButton(self):
        try:
            cmds.button('send_render_btn', edit=True, enable=False)
        except:
            pass

    def fileGotUnsavedChanges(self):
        return cmds.file(q=True, modified=True)

    def setFileModifiedConditionAndCallback(self):
        try:
            cmds.condition('FileModified', delete=True)
        except:
            pass

    def setStatus(self, txt):
        cmds.text(self.progressTextBox, label=txt, edit=True)
        if time.time() - self.lastRefresh > 1:
            self.lastRefresh = time.time()
            cmds.refresh(force=True)

    def onListSelected(self):
        selected = cmds.textScrollList(self.listbox, q=1, selectIndexedItem=2)
        for e in self.mapListResult:
            if e[0] == selected[0]:
                if e[1].flagMoreInfos == True:
                    resolved = e[1].validator.furtherAction(e[1])
                    if resolved == True:
                        e[1].severity = 3
                        self.displayResults()

    def getSelectedRenderer(self):
        return cmds.optionMenu(self.rendererSelect, v=1, q=1)

    def submitToSky(self, _):
        if self.actionStart(False):
            f = os.path.join(self.m_defaultPath, self.m_userName)
            self.doExportFolder(f)
            cmds.button('send_render_btn', edit=True, enable=False)
            self.estimateEnabled = False
        else:
            cmds.confirmDialog(title='Farminizer', message='This project could not be exported, please check the displayed errors.', button=['Ok'])
            self.displayResults()

    def displayResults(self):
        list = []
        txtLine = ''
        self.mapListResult = []
        sev = 0
        sev_text = ['Info',
         'Warning',
         'Error',
         'Resolved',
         '',
         '',
         '',
         '',
         '']
        sev_sep = ['            ',
         '     ',
         '           ',
         '     ',
         '',
         '',
         '',
         '']
        sev_filter = 0
        grp = ''
        pre_grp = ''
        hint = ''
        bContent = False
        if self.chkAllChecked():
            sev_filter = 0
        if self.chkErrorChecked():
            sev_filter = 2
        if self.chkWarningChecked():
            sev_filter = 1
        i = 0
        for vr in self.vecResults:
            if vr.validator != 0:
                grp = vr.validator.getName()
                if grp != pre_grp:
                    if i > 1:
                        list.append(' ')
                    list.append(grp)
                    pre_grp = grp
            sev = vr.severity
            if sev == sev_filter or sev_filter == 0:
                if vr.flagMoreInfos:
                    hint = ' (click here...)'
                else:
                    hint = ''
                txtLine = '      ' + sev_text[sev] + sev_sep[sev] + vr.message + hint
                list.append(txtLine)
                self.mapListResult.append([len(list), vr])
                bContent = True
            i += 1

        if not bContent and len(self.vecResults) > 0:
            if self.chkErrorChecked():
                list.append('                  No Errors')
            if self.chkWarningChecked():
                list.append('                  No Warnings')
        if not self.listbox:
            self.initWindow()
        cmds.textScrollList(self.listbox, edit=True, removeAll=True)
        for l in list:
            cmds.textScrollList(self.listbox, edit=True, append=l)

    def isAllValid(self):
        bValid = True
        if len(self.vecResults) == 0:
            return False
        for i in self.vecResults:
            bValid = bValid and i.severity != 2

        return bValid

    def writeTestresultsToManager(self):
        try:
            st = ''
            doc = getChangedMayaFilename()
            for i in self.vecResults:
                st = st + 'MAYA:' + str(i.id) + ':' + doc + ':' + str(i.severity) + ';'

            file = open(os.path.join(self.m_defaultPath, 'at2_reb_testresults.txt'), 'a')
            file.write(st)
            file.close()
        except:
            pass

    def liveExportActivated(self, *args): 
        cmds.checkBox(self.liveExport, edit=True, value=False)

 

    def removeDuplicateLayerInfos(self, vecLayerInfos):
        toRemove = set()
        for i in range(len(vecLayerInfos)):
            for j in range(i + 1, len(vecLayerInfos)):
                if vecLayerInfos[i] == vecLayerInfos[j]:
                    toRemove.add(i)

        for i in reversed(sorted(list(toRemove))):
            del vecLayerInfos[i]

    def actionSmartCheck(self, *args):
        cmds.button('send_render_btn', edit=True, enable=False, visible=False)
        return self.actionStart(True)

    def actionStart(self, fastCheck):
        self.vecResults = []
        self.vecLayerInfos = []
        conf = getConfigFileContent()
        if len(conf) >= 4:
            self.m_userName = conf[0]
            self.m_defaultPath = conf[1]
            self.m_managerPath = conf[2]
            self.m_PluginVersion = conf[3]
            self.m_CpuData = ''
            if len(conf) >= 5:
                self.m_CpuData = conf[4]
        else:
            self.vecResults.append(TestResult(1, 2, 0, 'clientsettings.cfg could not be found, please reinstall plugin from Render Farm Application!', False, 0))
        if self.m_userName == '':
            self.vecResults.append(TestResult(2, 2, 0, 'You are not logged in correcly, please login from Render Farm Application first', False, 0))
        self.isVrsceneExport = False
        self.isMiExport = False
        self.gpu_enabled = False
        if skyMainDlg.isMultilayerEnabled():
            self.vecResults.append(TestResult(5, 0, 0, 'Each layer will be rendered in an extra pass', False, 0))
        oldRenderLayer = cmds.editRenderLayerGlobals(currentRenderLayer=1, q=1)
        current_renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
        for v in self.vecTests:
            v.preCheckStandalone()

        for v in self.vecTests:
            self.setStatus('Checking: ' + v.getName())
            if v.getIdentifier() and current_renderer in v.getIdentifier():
                print 'Checking: ' + v.getName()
                v.test(self.vecResults, fastCheck, self.vecLayerInfos)
            elif not v.is_renderer_validator:
                v.test(self.vecResults, fastCheck, self.vecLayerInfos)

        self.removeDuplicateLayerInfos(self.vecLayerInfos)
        if not skyMainDlg.isMultilayerEnabled():
            bDifferentLayerTimes = False
            if len(self.vecLayerInfos) > 0:
                firstStartframe = self.vecLayerInfos[0].startframe
                firstStopframe = self.vecLayerInfos[0].stopframe
                firstFramestep = self.vecLayerInfos[0].framestep
                for l in self.vecLayerInfos:
                    if l.startframe != firstStartframe or l.stopframe != firstStopframe or l.framestep != firstFramestep:
                        bDifferentLayerTimes = True

            if bDifferentLayerTimes == True:
                self.vecResults.append(TestResult(6, 2, self.LayerValidator(self), 'Different Layer Times found', True, 0))
        if len(self.vecLayerInfos) == 0:
            self.vecResults.append(TestResult(8, 2, 0, 'None of your render layers are activated. Please activate at least one layer in the Layer Editor', False, 0))
        cmds.editRenderLayerGlobals(currentRenderLayer=oldRenderLayer)
        if len(self.vecResults) == 0:
            self.vecResults.append(TestResult(7, 0, 0, 'No errors or warnings found', False, 0))
        skyMainDlg.updatePrioBox()
        self.displayResults()
        self.setStatus('')
        return self.isAllValid()

    def isSingleFrameRender(self):
        if onlyOneFrame() and skyMainDlg.isDistributed():
            return True
        return False

    class LayerValidator(object):
        dlg = 0

        def __init__(self, dlg):
            self.dlg = dlg

        def getName(self):
            return 'Layers'

        def furtherAction(self, result):
            cmds.confirmDialog(title='Message', message='You have renderlayers with different frame ranges. Check "Activate Layers" so every layer will be rendered in an extra pass', button=['Ok'])

    def actionExport(self, *args):
        f = ''
        valid = self.actionStart(True)
        if not valid:
            cmds.button('send_render_btn', edit=True, enable=False, visible=True)
            cmds.confirmDialog(title='Farminizer', message='This project could not be exported, please check the displayed errors.', button=['Ok'])
            return
        cmds.button('send_render_btn', edit=True, enable=True, visible=True)
        val_check_done = CheckDone(farmWin)
        self.vecResults.append(TestResult(1, 0, val_check_done, 'Scene checked successfully', False, 0))
        f = os.path.join(self.m_defaultPath, self.m_userName)  
        ftpContentsPath = os.path.join(self.m_defaultPath, 'shadows.txt')
        if not existsFile(f):
            os.mkdir(f) 
        if not existsFile(ftpContentsPath):            
            if existsFile(os.path.join(f, getChangedMayaFilename())) == True and existsFile(os.path.join(f, getChangedMayaFilename() + '.cfg')) == True:
                cmds.confirmDialog(title='Farminizer', message='Project already existing, please delete old project from Render Farm Application first!', button=['Ok'])
                try:
                    if cmds.about(mac=1):
                        subprocess.Popen(self.m_managerPath, shell=False)
                    else:
                        subprocess.Popen('"' + self.m_managerPath + '"', shell=False)
                except:
                    print 'Farm Win: ' + str(sys.exc_info())

    def doExportFolder(self, fname):
        vecFiles = []
        stSettingsToWrite = ''
        mayapath = os.path.join(fname, 'tex', 'maya', 'scenes', getChangedMayaFilename())
        mayadummypath = os.path.join(fname, getChangedMayaFilename())
        generatePreview(mayadummypath + '.jpg')
        for v in self.vecTests:
            stSettingsToWrite += v.prepareSave(fname, vecFiles)

        if self.isVrsceneExport or self.isMiExport:
            for v in self.vecTests:
                stSettingsToWrite += v.standaloneExport(self.vecResults, fname, vecFiles)

        if not self.isAllValid():
            cmds.confirmDialog(title='Farminizer', message='This project could not be exported, please check the displayed errors.', button=['Ok'])
            self.displayResults()
            for v in self.vecTests:
                v.postSave()

            return
        else:
            oldName = cmds.file(sceneName=True, q=1)
            cmds.file(rename=mayapath)
            savetype = 'mayaBinary' if mayapath[-3:] == '.mb' else 'mayaAscii'
            cmds.file(save=True, type=savetype)
            cmds.file(rename=oldName)
            appendFileInfo(vecFiles, 'tex/maya/scenes/' + getChangedMayaFilename(), mayapath, toCopy=False)
            settingsFile = open(mayadummypath, 'w')
            settingsFile.write(str(time.time()))
            settingsFile.close()
            for v in self.vecTests:
                v.postMayaFileSave(fname, vecFiles)

            if len(self.vecLayerInfos) >= 1:
                renderer = 'undef'
                for layer in self.vecLayerInfos:
                    if layer.type == 'ARNOLD':
                        verArnold = cmds.pluginInfo('mtoa', query=True, version=True)
                        renderer = 'ARNOLD_MTOA_' + verArnold
                    elif layer.type[:4] == 'Vray' or layer.type in ('MR', 'MX', 'renderManRIS', 'renderMan', 'iray', 'irayGPU') or layer.type.startswith('redshift') or layer.type.startswith('octane'):
                        if renderer == 'undef' or renderer == 'intern':
                            if layer.type[:4] == 'Vray' and self.isVrsceneExport:
                                renderer = 'VrayStandalone' + layer.type[4:]
                            elif layer.type == 'MR' and self.isMiExport:
                                renderer = 'mentalStandalone'
                            else:
                                renderer = layer.type

                stSettingsToWrite += 'renderer=' + renderer + '\r\n'
            else:
                stSettingsToWrite += 'renderer=undef\r\n'
            if skyMainDlg.isMultilayerEnabled() and len(self.vecLayerInfos) >= 2:
                i = 0
                for l in self.vecLayerInfos:
                    stSettingsToWrite += 'layername' + str(i) + '=' + l.layername + '\r\n'
                    stSettingsToWrite += 'layerstart' + str(i) + '=' + str(int(l.startframe)) + '\r\n'
                    stSettingsToWrite += 'layerstop' + str(i) + '=' + str(int(l.stopframe)) + '\r\n'
                    stSettingsToWrite += 'layerstep' + str(i) + '=' + str(int(l.framestep)) + '\r\n'
                    i += 1

                stSettingsToWrite += 'layers=' + str(i) + '\r\n'  
            
            print(combo_box.currentIndex())
            prio = combo_box.currentIndex()
            if prio != None:
                stSettingsToWrite += 'prio=' + str(prio) + '\r\n'
            if self.estimateEnabled:
                stSettingsToWrite += 'estimationFrames=3\r\n'
                stSettingsToWrite += 'autostart=1\r\n'
            elif skyMainDlg.isAutostartEnabled():
                stSettingsToWrite += 'autostart=1\r\n'
            if skyMainDlg.isSendMailByStartEnabled():
                stSettingsToWrite += 'notifyStart=1\r\n'
            if skyMainDlg.isSendMailCompleteEnabled():
                stSettingsToWrite += 'notifyCompletedit=True\r\n'
            stSettingsToWrite += 'localRend=2\r\n'
            stSettingsToWrite += '[files]\r\n'
            i = 0
            for f in vecFiles:
                stSettingsToWrite += 'path' + str(i) + '=' + f.serverPath + '\r\n'
                stSettingsToWrite += 'pathlocal' + str(i) + '=' + f.localPath + '\r\n'
                stSettingsToWrite += 'pathsize' + str(i) + '=' + str(f.fileSize) + '\r\n'         
                i += 1
            
            
            
            stSettingsToWrite += 'paths=' + str(i) + '\r\n'
            stSettingsToWrite += '[checksum]\r\n'
            stSettingsToWrite += 'check=' + calcMd5(mayadummypath) + '\r\n'
            stSettingsToWrite += 'scenesize=' + str(os.stat(mayadummypath).st_size) + '\r\n'
            settingsFile = open(mayadummypath + '.cfg', 'wb')
            if sys.hexversion > 34013184:
                settingsFile.write(stSettingsToWrite.encode('utf-8', errors='ignore'))
            else:
                settingsFile.write(stSettingsToWrite.encode('utf-8'))
            settingsFile.close()
            for v in self.vecTests:
                v.postSave()

            #refreshFile = open(os.path.join(self.m_defaultPath, 'at2_reb_refresh.txt'), 'w')
            #refreshFile.close()
            self.setStatus('Export finished!')
            val_check_done = CheckDone(farmWin)
            self.vecResults.append(TestResult(1, 0, val_check_done, 'Scene Successfully prepared and send to Render Farm Application', False, 0))
            self.displayResults()
            self.gpu_enabled = False
            ftpContentsPath = os.path.join(self.m_defaultPath, 'shadows.txt')
            if not existsFile(ftpContentsPath):
                try:
                    if cmds.about(mac=1):
                        subprocess.Popen(self.m_managerPath, shell=False)
                    else:
                        subprocess.Popen('"' + self.m_managerPath + '"', shell=False)
                except:
                    print 'Farm: ' + str(sys.exc_info())

            return

    def doSaveLog(self, *args):
        filename = args[0]
        extension = args[1]
        f = open(filename, 'w')
        if f:
            fileTxt = ''
            curos = cmds.about(os=True)
            sysbit = '32Bit'
            if cmds.about(is64=True):
                sysbit = '64Bit' 
            fileTxt += '\r\n'
            fileTxt += 'Environment:\r\n'
            fileTxt += '------------------------------ \r\n'
            fileTxt += 'Client Document: ' + getChangedMayaFilename() + '\r\n'
            fileTxt += 'Scripts Path: ' + __file__ + '\r\n'
            fileTxt += 'Client Maya Ver.: ' + cmds.about(v=True) + '\r\n'
            fileTxt += 'Client OS: ' + curos + '\r\n'
            fileTxt += '\r\n\r\n'
            fileTxt += 'Farminizer Plugin output:\r\n'
            fileTxt += '------------------------------ \r\n\r\n'
            sev_text = ['Info',
             'Warning',
             'Error',
             '',
             '',
             '',
             '',
             '']
            grp = ''
            pre_grp = ''
            for i in self.vecResults:
                if i.validator != 0:
                    grp = i.validator.getName()
                    if grp != pre_grp:
                        fileTxt += '\r\n' + grp + ':\r\n\r\n'
                        pre_grp = grp
                fileTxt += ' --- ' + sev_text[i.severity] + ' --- ' + i.message + '\r\n'

            f.write(fileTxt)

    def actionSaveLog(self, *args):
        cmds.fileBrowserDialog(m=1, fc=self.doSaveLog, an='Save Log...', om='SaveAs')
 
    def actionAbout(self, *args):
        ab = AboutDialog()
        ab.show()

    def chkAllChecked(self):
        return self.m_chkAll

    def chkErrorChecked(self):
        return self.m_chkErr

    def chkWarningChecked(self):
        return self.m_chkWar

    def isVrayStandalone(self):
        return self.isVrsceneExport

    def isMentalStandalone(self):
        return self.isMiExport

    def saveFileDialogUI(self):
        confirm = 'Yes'
        dismiss = 'No'
        message = 'File has been changed since last Check.\nShould your file be saved and the scene be checked for changes?\nAttention: File will be overwritten'
        title = 'Save and check file'
        cmds.button('send_render_btn', edit=True, enable=False)
        save_file = cmds.confirmDialog(title=title, message=message, button=[confirm, dismiss], defaultButton=confirm, cancelButton=dismiss, messageAlign='center', parent='Render Farm Application ')
        if save_file == 'Yes':
            cmds.file(save=True)
            self.actionStart(False)
            return True
        else:
            return False


class MainDialog():

    def __init__(self):
        self.bannerImages = []
        self.imgRoot = os.path.join(os.path.dirname(__file__), 'res')
        self.clear()
        self.bannerTimer = None
        self.bannerIndex = 0
        self.waittimes = ['2 hours',
         '30 minutes',
         '10 minutes',
         '< 10 minutes',
         '< 10 minutes',
         '< 10 minutes',
         '< 10 minutes',
         '< 10 minutes']
        self.downloadImages()
        self.settings = dict()
        self.settings['setting_priority'] = 1
        self.settings['setting_autostart'] = False
        self.settings['setting_distributed'] = False
        self.settings['setting_layers'] = False
        self.settings['setting_send_mail'] = False
        self.settings['setting_mail_start'] = False
        self.settings['setting_mail_finish'] = False
        self.settings_file_path = os.path.join(farmWin.m_defaultPath, farmWin.m_userName, 'maya_farminizer_settings.txt')
        self.initializeSetupSettingsFromFile()
        self.removeAndAddCallbacks()
        return

    def clear(self):
        self.chkAutostart = ''
        self.chkDistributed = ''
        self.chkSendMail = ''
        self.chkActivateLayers = ''
        self.chkSendMailByStart = ''
        self.chkSendMailComplete = ''
        self.drpPrio = ''
        self.btnEstimation = ''
        self.priorities = self.getPrioritiesArray()
        self.prioSelectElements = []

    def getPrioritiesArray(self):
        cpuPrice = 1.8
        cpuStep = 0.6
        gpuPrice = 0.9
        gpuStep = 0.5
        modifiedDate = 0
        extraCost = 0
        filePath = os.path.join(farmWin.m_defaultPath, 'ghzprices.json')
        val = ''
        try:
            with open(filePath) as json_file:
                pricesjson = json.load(json_file)
                cpuPrice = pricesjson['cpu_price']
                cpuStep = pricesjson['cpu_price_step']
                gpuPrice = pricesjson['gpu_price']
                gpuStep = pricesjson['gpu_price_step']
                activeRenderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
                for renderer in pricesjson['renderers']:
                    if renderer['name'] in activeRenderer:
                        extraCost += renderer['price']

                for program in pricesjson['programs']:
                    if renderer['name'] in 'MAYA':
                        extraCost += program['price']

        except:
            pass
        finally:
            try:
                pass
            except:
                pass

        priorities = []
        priorities.append(('Standard (' + str(cpuPrice + extraCost) + ' Cent / GHzh)', 'Standard (' + str(gpuPrice + extraCost) + ' Cent / OBh)', 0))
        count = 1
        while count < 7:
            priorities.append(('Prio +' + str(count) + ' (' + str(cpuPrice + extraCost + cpuStep * count) + ' Cent / GHzh)', 'Prio +' + str(count) + ' (' + str(gpuPrice + +extraCost + gpuStep * count) + ' Cent / OBh)', count))
            count += 1

        return priorities

    def closed(self):
        if self.bannerTimer != None:
            self.bannerTimer.cancel()
        return

    def timerBannerUpdate(self):
        self.bannerTimer = threading.Timer(4, self.timerBannerUpdate)
        self.bannerTimer.start()
        maya.utils.executeDeferred(self.updateBanner)

    def updateBanner(self):
        try:
            self.bannerIndex += 1
            if self.bannerIndex >= len(self.bannerImages):
                self.bannerIndex = 0
            cmds.iconTextButton(self.imgBanner, image=self.bannerImages[self.bannerIndex][0], edit=True)
        except:
            pass

    def updatePrioText(self, *args):
        try:
            self.settings['setting_priority'] = cmds.optionMenu(self.drpPrio, select=1, query=1)
            if self.textWaittime:
                cmds.text(self.textWaittime, label='Estimated wait time ' + self.waittimes[int(self.getSelectedPrio()) - 1], edit=True)
        except:
            pass

        self.writeSetupSettingsToFile()

    

    def updateStatusInfo(self): 
        cmds.text(self.txtUser, label='User: ' + farmWin.m_userName, edit=True) 

    def writeSetupSettingsToFile(self):
        with open(self.settings_file_path, 'w') as settings_file:
            settings_file.write('setting_autostart=' + str(int(self.settings['setting_autostart'])) + '\n')
            settings_file.write('setting_priority=' + str(self.settings['setting_priority']) + '\n')
            settings_file.write('setting_distributed=' + str(int(self.settings['setting_distributed'])) + '\n')
            settings_file.write('setting_layers=' + str(int(self.settings['setting_layers'])) + '\n')
            settings_file.write('setting_send_mail=' + str(int(self.settings['setting_send_mail'])) + '\n')
            settings_file.write('setting_mail_start=' + str(int(self.settings['setting_mail_start'])) + '\n')
            settings_file.write('setting_mail_finish=' + str(int(self.settings['setting_mail_finish'])) + '\n')

    def initializeSetupSettingsFromFile(self):
        if os.path.exists(self.settings_file_path):
            with open(self.settings_file_path, 'r') as settings_file:
                for line in settings_file:
                    key, value = line.split('=')
                    if key == 'setting_priority':
                        self.settings[key] = int(value)
                    else:
                        self.settings[key] = bool(int(value))

    def initWindow(self): 
        cmds.showWindow()

    def updatePrioBox(self):
        if len(self.prioSelectElements) == 0 or self.drpPrio == '':
            return
        if str(cmds.getAttr('defaultRenderGlobals.currentRenderer')) == 'arnold':
            farmWin.gpu_enabled = False
            try:
                if cmds.getAttr('defaultArnoldRenderOptions.renderDevice') == 1:
                    farmWin.gpu_enabled = True
            except:
                pass

        if farmWin.gpu_enabled:
            for i in range(len(self.priorities)):
                cmds.menuItem(self.prioSelectElements[i], label=self.priorities[i][1], edit=True)

        else:
            for i in range(len(self.priorities)):
                cmds.menuItem(self.prioSelectElements[i], label=self.priorities[i][0], edit=True)

    def setupLayers(self, _):
        import maya.app.renderSetup.views.renderSetup
        maya.app.renderSetup.views.renderSetup.createUI()

    def notifyClicked(self, _):
        self.settings['setting_send_mail'] = cmds.checkBox(self.chkSendMail, q=1, v=1)
        cmds.checkBox(self.chkSendMailByStart, edit=True, enable=self.settings['setting_send_mail'])
        cmds.checkBox(self.chkSendMailComplete, edit=True, enable=self.settings['setting_send_mail'])
        self.writeSetupSettingsToFile()

    def mailStartClicked(self, _):
        self.settings['setting_mail_start'] = cmds.checkBox(self.chkSendMailByStart, q=1, v=1)
        self.writeSetupSettingsToFile()

    def mailCompleteClicked(self, _):
        self.settings['setting_mail_finish'] = cmds.checkBox(self.chkSendMailComplete, q=1, v=1)
        self.writeSetupSettingsToFile()

    def autoStartClicked(self, _):
        self.settings['setting_autostart'] = cmds.checkBox(self.chkAutostart, q=1, v=1)
        if self.settings['setting_autostart']:
            cmds.button(self.btnUpload, label='Render Now', edit=True)
        else:
            cmds.button(self.btnUpload, label='Upload to Render Farm Application', edit=True)
        self.writeSetupSettingsToFile()

    def distributedClicked(self, _):
        self.settings['setting_distributed'] = cmds.checkBox(self.chkDistributed, q=1, v=1)
        if self.settings['setting_distributed'] == True or utilitis.renderFiveOrMoreFrames() == False:
            enabled = False
        else:
            enabled = True
        cmds.button(self.btnEstimation, enable=enabled, edit=True)
        self.writeSetupSettingsToFile()

    def activateLayersClicked(self, _):
        self.settings['setting_layers'] = cmds.checkBox(self.chkActivateLayers, q=1, v=1)
        self.writeSetupSettingsToFile()

    def uploadClicked(self, _):
        farmWin.initWindow()
        farmWin.estimateEnabled = False
        farmWin.actionExport()

    def smartCheckClicked(self, _):
        farmWin.initWindow()
        farmWin.estimateEnabled = False
        farmWin.actionSmartCheck()
 

    def bannerClicked(self):
        url = self.bannerImages[self.bannerIndex][1]
        if url != None:
            webbrowser.open(url)
        return

    def isAutostartEnabled(self):
        return self.settings['setting_autostart']

    def isSendMailEnabled(self):
        if self.chkSendMail != '':
            return cmds.checkBox(self.chkSendMail, q=1, v=1)
        return False

    def isMultilayerEnabled(self):
        if self.chkActivateLayers != '':
            return cmds.checkBox(self.chkActivateLayers, q=1, v=1)
        return False

    def isSendMailByStartEnabled(self):
        if self.chkSendMailByStart != '' and self.isSendMailEnabled():
            return cmds.checkBox(self.chkSendMailByStart, q=1, v=1)
        return False

    def isSendMailCompleteEnabled(self):
        if self.chkSendMailComplete != '' and self.isSendMailEnabled():
            return cmds.checkBox(self.chkSendMailComplete, q=1, v=1)
        return False

    def getSelectedPrio(self):
        if self.drpPrio != '':
            prio = cmds.optionMenu(self.drpPrio, v=1, q=1)
            if prio != 'Standard':
                for p in self.priorities:
                    if prio == p[0] or prio == p[1]:
                        return str(p[2] + 1)

        return None

    def isDistributed(self):
        if self.chkDistributed != '':
            return cmds.checkBox(self.chkDistributed, q=1, v=1)
        return False

    def downloadImages(self):
        self.bannerImages = []
        try:  
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass

            try:
                urllib.urlretrieve(url, bannersFile)
            except:
                pass

            banners = ''
            try:
                fh = open(bannersFile)
                banners = fh.read()
                fh.close()
            except:
                print str(sys.exc_info())

            banners = banners.replace('\r\n', '\n')
            for i, banner in enumerate(banners.split('\n')):
                if len(banner.split('|')) == 2:
                    bannerUrl, bannerLink = banner.split('|')
                    img = 'mayaBanner' + str(i) + '.png'
                    dest = os.path.join(self.imgRoot, img)
                    if (not os.path.exists(dest) or os.path.getmtime(dest) < time.time() - 86400) and not hasattr(cmds, 'farm'):
                        try:
                            ssl._create_default_https_context = ssl._create_unverified_context
                        except:
                            pass

                        try:
                            urllib.urlretrieve(bannerUrl, dest)
                        except:
                            pass

                    if utilitis.isImage(dest):
                        self.bannerImages.append((dest, bannerLink))
                    else:
                        if os.path.exists(dest):
                            os.unlink(dest)
                        break

        except:
            pass
  

    def downloadWaittimes(self):
        waittimesFile = os.path.join(self.imgRoot, 'waittimes.txt')
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
        except:
            pass
 
        waittimes = ''
        try:
            fh = open(waittimesFile)
            waittimes = fh.read()
            fh.close()
        except:
            print str(sys.exc_info())

        waittimes = waittimes.replace('\r\n', '\n')
        for i, waittime in enumerate(waittimes.split('\n')):
            if i >= len(self.waittimes):
                break
            vec = waittime.split('|')
            if len(vec) == 2:
                waittext = ''
                t = int(vec[1])
                if t / 3600 > 0:
                    waittext = str(t / 3600) + ' hours'
                elif t / 60 > 0:
                    waittext = str(t / 60) + ' minutes'
                else:
                    waittext = '0 minutes'
                self.waittimes[i] = waittext

      
    def setPriorityListByRenderer(self):
        current_renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
        gpu_renderer = ['arnold', 'ifmIrayPhotoreal', 'redshift']
        if current_renderer in gpu_renderer:
            farmWin.gpu_enabled = True
        else:
            farmWin.gpu_enabled = False
        self.updatePrioBox()

    def farminizerSettingsCheck(self):
        self.priorities = self.getPrioritiesArray()
        self.setPriorityListByRenderer()
        distribution_enabled = enableDistributedRenderingCheckbox()
        if distribution_enabled == False:
            if self.chkDistributed:
                cmds.checkBox(self.chkDistributed, edit=True, value=distribution_enabled)
        if self.chkDistributed:
            cmds.checkBox(self.chkDistributed, edit=True, enable=distribution_enabled)
        cost_estimation_enabled = enableCostEstimationButton()
        if self.btnEstimation:
            cmds.button(self.btnEstimation, edit=True, enable=cost_estimation_enabled)
        self.updatePrioText()
        self.setPriorityListByRenderer()

    def removeAndAddCallbacks(self):
        cmds.scriptJob(attributeChange=['defaultRenderGlobals.startFrame', self.farminizerSettingsCheck])
        cmds.scriptJob(attributeChange=['defaultRenderGlobals.endFrame', self.farminizerSettingsCheck])
        cmds.scriptJob(attributeChange=['defaultRenderGlobals.currentRenderer', self.farminizerSettingsCheck])
        try:
            cmds.scriptJob(attributeChange=['defaultArnoldRenderOptions.renderDevice', self.farminizerSettingsCheck])
        except:
            pass


farmWin = ListDialog()
skyMainDlg = MainDialog()

def init():
    pass


def shelfCheckScene():
    farmWin.initWindow()
    farmWin.actionSmartCheck()


def add_string_to_file_if_not_present(search_string, file_path):
    with open(file_path, 'a+') as search_file:
        search_file.seek(0)
        for line in search_file:
            if line.strip().replace('\\', '/') == search_string:
                return True

        search_file.write(search_string + '\n')
    return False


def shelfPreUpload():
    allTextures, allObjects, allParams, allOptions = utilitis.findAllTextures(allLayers=False)
    paths = []
    file_count = 0 
    scene_upload_history_path = os.path.join(farmWin.m_defaultPath, farmWin.m_userName, os.path.basename(cmds.file(sceneName=True, q=1)) + '_upload_history.txt')
    for p in allTextures:
        try:
            if p and os.path.exists(p):
                paths.append(p)
        except:
            pass
 
        f.close()
    val_preupload = PreUpload(farmWin)
    if file_count > 0:
        farmWin.vecResults.append(TestResult(1, 0, val_preupload, str(file_count) + ' texture files uploading in the Background by Render Farm Application...', False, 0))
    else:
        farmWin.vecResults.append(TestResult(1, 0, val_preupload, 'Texture files are up to date', False, 0))
    farmWin.initWindow()
    farmWin.displayResults()
    print str(file_count) + ' files uploading in the Background by Render Farm Application...'


def shelfRenderNow():
    farmWin.initWindow()
    farmWin.actionExport()


def shelfRenderSetup():
    skyMainDlg.initWindow()


def shelfControlCenter():
    skyMainDlg.createOpenCCFile()

 


def shelfCostEstimation():
    farmWin.estimateEnabled = True
    farmWin.initWindow()
    farmWin.actionExport()


def shelfRenderOutput():
    path = os.path.join(farmWin.m_defaultPath, farmWin.m_userName, 'Render Farm Application', 'Download')
    if cmds.about(mac=1):
        subprocess.Popen(['open', '-R', path], shell=False)
    else:
        subprocess.Popen('explorer "' + os.path.normpath(path) + '"', shell=False)

 

 
     
