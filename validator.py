
class Validator(object):
    mainDialog = 0
    is_renderer_validator = False

    def __init__(self, main):
        self.mainDialog = main

    def getName(self):
        pass

    def getIdentifier(self):
        pass

    def preCheckStandalone(self):
        pass

    def standaloneExport(self, resultList, fPath, vecFiles):
        return ''

    def test(self, resultList, fastCheck, layerinfos):
        pass

    def furtherAction(self, result):
        pass

    def prepareSave(self, path, vecFiles):
        pass

    def postSave(self):
        pass

    def postMayaFileSave(self, path, vecFiles):
        pass


class TestResult(object):

    def __init__(self, id, severity, validator, message, flagMoreInfos, type):
        self.id = id
        self.severity = severity
        self.type = type
        self.validator = validator
        self.message = message
        self.flagMoreInfos = flagMoreInfos

    id = 0
    severity = 0
    type = 0
    validator = 0
    message = ''
    flagMoreInfos = False


class LayerInfos(object):

    def __init__(self, layername, startframe, stopframe, framestep, type):
        self.layername = layername
        self.startframe = startframe
        self.stopframe = stopframe
        self.framestep = framestep
        self.type = type

    def __eq__(self, other):
        return self.layername == other.layername and self.type == other.type and self.startframe == other.startframe and self.stopframe == other.stopframe and self.framestep == other.framestep

    layername = ''
    type = ''
    startframe = 0
    stopframe = 0
    framestep = 1
