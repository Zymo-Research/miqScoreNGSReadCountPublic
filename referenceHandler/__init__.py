
class StandardReference(object):

    __slots__ = ["nameLookup",
                 "printNames",
                 "itemIDs",
                 "sortings",
                 "expectedValues",
                 "analysisMethods"]

    def __init__(self, standardDataPath:str):
        import os
        if os.path.isfile(standardDataPath):
            rawData = self.loadDictionary(standardDataPath)
        else:
            raise FileNotFoundError("Unable to find standard reference dictionary at %s" %standardDataPath)
        self.processRawData(rawData)

    def loadDictionary(self, path:str):
        import json
        file = open(path, 'r')
        data = json.load(file)
        file.close()
        return data

    def loadStoredReferenceDict(self, fileName):
        import os
        referenceFolder = os.path.split(__file__)[0]
        path = os.path.join(referenceFolder, fileName)
        return self.loadDictionary(path)

    def processRawData(self, rawData:dict):
        self.nameLookup = rawData["nameLookup"]
        self.printNames = rawData["printNames"]
        self.itemIDs = rawData["itemIDs"]
        self.sortings = rawData["sortings"]
        self.expectedValues = rawData["expectedValues"]
        self.analysisMethods = list(self.expectedValues.keys())


def determineExpectedReadSources(analysisMethod:str, standardReference:StandardReference):
    if not analysisMethod in standardReference.analysisMethods:
        raise KeyError("%s is not a valid analysis method in the reference" %analysisMethod)
    sampleSpace = set()
    for sampleItem in standardReference.expectedValues[analysisMethod]:
        if not standardReference.expectedValues[analysisMethod][sampleItem]:
            continue
        else:
            if not sampleItem in sampleSpace:
                sampleSpace.add(sampleItem)
            else:
                raise ValueError("Duplicate entry found for sample item %s.  This should never be able to happen if you are loading JSON and needs to be debugged." %sampleItem)
    return sampleSpace


def convertKeysToStandardIdentifiers(readCountDict:dict, standardReference:StandardReference):
    convertedDict = {}
    for rawName in readCountDict:
        if rawName in standardReference.nameLookup:
            newName = standardReference.nameLookup[rawName]
        else:
            newName = rawName
        if not newName in convertedDict:
            convertedDict[newName] = 0
        convertedDict[newName] += readCountDict[rawName]
    return convertedDict


def convertKeysToPrintIdentifiers(readCountDict:dict, standardReference:StandardReference):
    convertedDict = {}
    for standardName in readCountDict:
        if standardName in standardReference.printNames:
            printName = standardReference.printNames[standardName]
        else:
            printName = standardName
        if not printName in convertedDict:
            convertedDict[printName] = 0
        convertedDict[printName] += readCountDict[standardName]
    return convertedDict
