def sumDictionary(dictionary:dict):
    sum = 0
    for key in dictionary:
        if key:
            sum += dictionary[key]
    return sum

def separateReferenceAndNonreferenceReads(observedReadCounts:dict, expectedReads:[dict, list]):
    if type(expectedReads) == dict:
        expectedReads = list(expectedReads.keys)
    referenceReads = {}
    nonreferenceReads = {}
    for readSource in observedReadCounts:
        if readSource in expectedReads:
            referenceReads[readSource] = observedReadCounts[readSource]
        else:
            nonreferenceReads[readSource] = observedReadCounts[readSource]
    for readSource in expectedReads:
        if not readSource in referenceReads:
            referenceReads[readSource] = 0
    return referenceReads, nonreferenceReads

