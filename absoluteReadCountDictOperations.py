from . import generalDictOperations

def convertDictToPercentages(sampleData:dict):
    readSum = generalDictOperations.sumDictionary(sampleData)
    if readSum == 0:
        return sampleData
    percentageDict = {}
    for key in sampleData:
        percentageDict[key] = (sampleData[key] / readSum) * 100
    return percentageDict