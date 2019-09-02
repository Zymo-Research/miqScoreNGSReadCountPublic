from . import referenceHandler
from . import absoluteReadCountDictOperations
from . import generalDictOperations
from . import percentReadCountDictOperations
from . import plotting
from . import reportGeneration


__all__ = ["referenceHandler",
           "absoluteReadCountDictOperations",
           "generalDictOperations",
           "percentReadCountDictOperations",
           "plotting",
           "reportGeneration"]


class MiqScoreCalculator(object):
    '''
    Takes in an expected values dictionary with percentages.
    Can take in a percent tolerance in standard and a floor value for miq score
    '''
    def __init__(self, standardReference: referenceHandler.StandardReference, analysisMethod:str, percentToleranceInStandard:[int, float]=0, floor:[int, float]=0):
        self.standardReference = standardReference
        self.analysisMethod = analysisMethod
        if not analysisMethod in standardReference.analysisMethods:
            raise ValueError("Analysis method %s not found in analysis methods for the chosen standard. Valud methods: %s" %(analysisMethod, standardReference.analysisMethods))
        self.percentToleranceInStandard = percentToleranceInStandard
        self.floor = floor
        self.expectedReadSources = []
        for source in standardReference.expectedValues[analysisMethod]:
            if standardReference.expectedValues[analysisMethod][source]:
                self.expectedReadSources.append(source)

    def calculateMiq(self, sampleData:dict, sampleID:str=None):
        '''Sample Data should come in as absolute counts'''
        import statistics
        sampleData = referenceHandler.convertKeysToStandardIdentifiers(sampleData, self.standardReference)
        referenceReads, nonreferenceReads = generalDictOperations.separateReferenceAndNonreferenceReads(sampleData, self.expectedReadSources)
        samplePercentages = absoluteReadCountDictOperations.convertDictToPercentages(referenceReads)
        samplePercentOfExpected = percentReadCountDictOperations.calculateObservedPercentOfExpected(samplePercentages, self.standardReference.expectedValues[self.analysisMethod])
        rawPercentOfExpected = []
        for readSource in samplePercentages:
            rawPercentOfExpected.append(samplePercentOfExpected[readSource])
        unadjustedPercentErrors = [100 - value for value in rawPercentOfExpected]
        adjustedPercentErrorsSquared = []
        for i in range(len(unadjustedPercentErrors)):
            if self.percentToleranceInStandard:
                if abs(unadjustedPercentErrors[i]) <= self.percentToleranceInStandard:
                    adjustedPercentErrorsSquared.append(0) #deviation is within standard tolerance
                else:
                    adjustedPercentErrorsSquared.append((abs(unadjustedPercentErrors[i]) - self.percentToleranceInStandard) ** 2)
            else:
                adjustedPercentErrorsSquared.append(unadjustedPercentErrors[i] ** 2)
        meanDeviationSquared = statistics.mean(adjustedPercentErrorsSquared)
        rmse = meanDeviationSquared ** 0.5
        miqScore = 100 - rmse
        if self.floor is None:
            filteredMiqScore =  miqScore
        else:
            filteredMiqScore =  max([miqScore, self.floor])
        return MiqScoreData(filteredMiqScore, miqScore, referenceReads, nonreferenceReads, samplePercentages, samplePercentOfExpected, self.percentToleranceInStandard, self.analysisMethod, self.standardReference, sampleID)


class MiqScoreData(object):

    def __init__(self, miqScore:float, rawMiqScore:float, referenceReadCounts:dict, nonreferenceReadCounts:dict, samplePercentages:dict, samplePercentagesOfExpected:dict, percentToleranceInStandard:float, analysisMethod:str, standardReference: referenceHandler.StandardReference, sampleID:str = None, storePlots:bool=True):
        self.miqScore = miqScore
        self.rawMiqScore = rawMiqScore
        self.referenceReadCounts = referenceReadCounts.copy()
        self.nonreferenceReadCounts = nonreferenceReadCounts.copy()
        self.samplePercentages = samplePercentages.copy()
        self.samplePercentagesOfExpected = samplePercentagesOfExpected.copy()
        self.percentToleranceInStandard = percentToleranceInStandard
        self.analysisMethod = analysisMethod
        self.standardReference = standardReference
        self.readFateTable = self.makeReadFateTable()
        self.sampleID = sampleID
        self.storePlots = storePlots
        self.plots = {}

    def makeReadFateTable(self):
        readFates = self.nonreferenceReadCounts.copy()
        readFates["Reference"] = generalDictOperations.sumDictionary(self.referenceReadCounts)
        readFates = absoluteReadCountDictOperations.convertDictToPercentages(readFates)
        return readFates

    def makeReadFateChart(self, format:str="png", forceRedraw:bool=False, readFatePrintNames:dict=None):
        if "readFates" in self.plots and not forceRedraw:
            return self.plots["readFates"]
        printReadFateTable = {}
        if readFatePrintNames:
            for readFate in self.readFateTable:
                if readFate in readFatePrintNames:
                    printReadFateTable[readFatePrintNames[readFate]] = self.readFateTable[readFate]
                else:
                    printReadFateTable[readFate] = self.readFateTable[readFate]
        else:
            printReadFateTable = self.readFateTable.copy()
        encodedPlot = plotting.readFateChart.makeReadFateChart(printReadFateTable, self.sampleID, explodeCell="Aligned To Reference", saveFormat=format)
        if self.storePlots:
            self.plots["readFates"] = encodedPlot
        return encodedPlot

    def makeRadarPlots(self, format:str="png", forceRedraw:bool=False):
        if "radarPlots" in self.plots and not forceRedraw:
            return self.plots["radarPlots"]
        radarPlots = {}
        for sortingMethod in self.standardReference.sortings:
            orderType, orderedListUnfiltered = self.standardReference.sortings[sortingMethod]
            topHigh = orderType == "descending"
            orderedList = [item for item in orderedListUnfiltered if item in self.referenceReadCounts]
            if self.sampleID:
                plotTitle = "%s: %s" %(self.sampleID, "Sorted By " + sortingMethod)
            else:
                plotTitle = sortingMethod
            plottingDict = {plotTitle: self.samplePercentagesOfExpected}
            encodedPlot = plotting.radarMaker.makeRadarPlot(plottingDict, orderedList, sortingMethod, topHigh=topHigh, format=format, printNames=self.standardReference.printNames)
            radarPlots[sortingMethod] = encodedPlot
        if self.storePlots:
            self.plots["radarPlots"] = radarPlots
        return radarPlots

    def makeCompositionBarPlot(self, goodExample:dict=None, badExample:dict=None):
        expectedPercentagesRaw = self.standardReference.expectedValues[self.analysisMethod]
        barPlotValueOrder = []
        for value in self.standardReference.sortings["Lysis Difficulty"][1]:
            if value in self.samplePercentages:
                barPlotValueOrder.append(value)
        expectedPercentages = {}
        for value in expectedPercentagesRaw:
            if expectedPercentagesRaw[value]:
                expectedPercentages[value] = expectedPercentagesRaw[value]
        barPlotData = {"Theoretical" : expectedPercentages,
                       self.sampleID : absoluteReadCountDictOperations.convertDictToPercentages(self.referenceReadCounts)}
        usingExamples = False
        if goodExample or badExample:
            usingExamples = True
            if goodExample:
                barPlotData["Good"] = goodExample
            if badExample:
                barPlotData["Biased"] = badExample
            sampleOrder = ("Theoretical", "Good", self.sampleID, "Biased")
        else:
            sampleOrder = ("Theoretical", self.sampleID)
        encodedPlot = plotting.stackedBars.makeStackedBar(barPlotData, barPlotValueOrder, sampleOrder, "%s Composition" %self.sampleID, printNameTable=self.standardReference.printNames)
        if self.storePlots:
            self.plots["compositionPlot"] = encodedPlot
        return encodedPlot

    def jsonOutput(self):
        import json
        resultTable = {"nonreferenceReadCounts": self.nonreferenceReadCounts,
                       "miqScore": self.miqScore,
                       "rawMiq": self.rawMiqScore,
                       "percentToleranceInStandard": self.percentToleranceInStandard,
                       "plots": self.plots,
                       "readFateTable": self.readFateTable,
                       "referenceReadCounts": self.referenceReadCounts,
                       "sampleID": self.sampleID,
                       "samplePercentages": self.samplePercentages,
                       "samplePercentagesOfExpected": self.samplePercentagesOfExpected}
        return json.dumps(resultTable, indent=4)


def loadExampleData(goodMiqPath:str, badMiqPath:str, referenceData:[str, referenceHandler.StandardReference], analysisMethod:str):
    import os
    import json
    if not os.path.isfile(goodMiqPath):
        raise FileNotFoundError("Unable to find good miq example at %s" %goodMiqPath)
    if not os.path.isfile(badMiqPath):
        raise FileNotFoundError("Unable to find bad miq example at %s" %badMiqPath)
    if not type(referenceData) == referenceHandler.StandardReference:
        if not os.path.isfile(referenceData):
            raise FileNotFoundError("Unable to find reference data file at %s" %referenceData)
        else:
            referenceData = referenceHandler.StandardReference(referenceData)
    examples = []
    for path in [goodMiqPath, badMiqPath]:
        file = open(path, 'r')
        report = json.load(file)
        file.close()
        sampleCounts = report["nonreferenceReadCounts"]
        sampleCounts.update(report["referenceReadCounts"])
        calculator = MiqScoreCalculator(referenceData, analysisMethod=analysisMethod, percentToleranceInStandard=report["percentToleranceInStandard"], floor=0)
        miqScoreResult = calculator.calculateMiq(sampleCounts, report["sampleID"])
        miqScoreResult.makeReadFateChart()
        miqScoreResult.makeRadarPlots()
        miqScoreResult.makeCompositionBarPlot()
        examples.append(miqScoreResult)
    return examples


def loadReferenceCompositionFromExampleMiq(goodMiqPath:str, badMiqPath:str):
    import os
    import json
    if not os.path.isfile(goodMiqPath):
        raise FileNotFoundError("Unable to find good miq example at %s" % goodMiqPath)
    if not os.path.isfile(badMiqPath):
        raise FileNotFoundError("Unable to find bad miq example at %s" % badMiqPath)
    examples = []
    for path in [goodMiqPath, badMiqPath]:
        file = open(path, 'r')
        report = json.load(file)
        file.close()
        referenceReadCounts = report["referenceReadCounts"]
        examples.append(absoluteReadCountDictOperations.convertDictToPercentages(referenceReadCounts))
    return examples


