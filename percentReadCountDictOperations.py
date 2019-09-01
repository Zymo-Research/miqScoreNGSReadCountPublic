from . import generalDictOperations

def convertDecimalPercentages(sampleData:dict):
    sum = generalDictOperations.sumDictionary(sampleData)
    if sum > 2:  #if they're using percentages that are already multiplied and their total percent is less than 2, they have bigger problems to worry about
        return sampleData
    convertedData = {}
    for key in sampleData:
        convertedData[key] = sampleData[key] * 100
    return convertedData

def fillInMissingPercentPortion(sampleData:dict):
    sum = generalDictOperations.sumDictionary(sampleData)
    if sum == 0:
        return sampleData
    missingPortion = 100 - sum
    if missingPortion <= 1:
        return sampleData
    filledInData = {}
    for key in sampleData:
        originalWeight = sampleData[key] / sum
        filledInData[key] = sampleData[key] + (missingPortion * originalWeight)
    return filledInData

def calculateObservedPercentOfExpected(observedReadPercent:dict, expectedReadPercent:dict):
    observedSources = set()
    for source in observedReadPercent:
        if observedReadPercent[source]:
            observedSources.add(source)
    expectedSources = set()
    for source in expectedReadPercent:
        if expectedReadPercent[source]:
            expectedSources.add(source)
    if not observedSources.issubset(expectedSources):
        errorInfo = "All observed read sources should be expected read sources by this point. Be sure to separate out reads from expected and unexpected sources before running this."
        errorData = "Observed sources: %s\nExpectedSources: %s" %(observedSources, expectedSources)
        raise ValueError("\n".join([errorInfo, errorData]))
    percentOfExpectedDict = {}
    for readSource in expectedSources:
        if readSource in observedSources:
            percentOfExpectedDict[readSource] = (observedReadPercent[readSource] / expectedReadPercent[readSource]) * 100
        else:
            percentOfExpectedDict[readSource] = 0
    return percentOfExpectedDict