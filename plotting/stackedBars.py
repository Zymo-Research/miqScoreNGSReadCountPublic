import matplotlib.pyplot as canvas
import io
import base64

def makeStackedBar(sampleDataTable:dict, valueOrderList:[list, tuple] = (), sampleOrderList:[list, tuple] = (), sampleName:str = "", format:str = "png", printNameTable:dict = None):
    '''
    :param sampleDataTable: Expecting a dictionary where keys are sample names and values are dictionaries of taxa:proportion
    :param valueOrderList:  How to order the values when plotting for consistency between plots
    :param sampleOrderList: How to order the samples from left to right
    :return: base-64 encoded string of the image
    '''
    canvas.figure(figsize=(7,5), dpi=300)
    if len(sampleDataTable) >= 11:
        topSpace = 0
        bottomSpace = 5
        leftSpace = 0
        rightSpace = 7
    elif len(sampleDataTable) >= 4:
        topSpace = 0
        bottomSpace = 3
        leftSpace = 1
        rightSpace = 7
    elif len(sampleDataTable) == 3:
        topSpace = 0
        bottomSpace = 1
        leftSpace = 2
        rightSpace = 7
    else:
        topSpace = 0
        bottomSpace = 0
        leftSpace = 1
        rightSpace = 7
    if leftSpace:
        leftVertBar = canvas.subplot2grid((20, 20), (0, 0), rowspan=20, colspan= leftSpace)
        leftVertBar.axis('off')
    if rightSpace:
        rightVertBar = canvas.subplot2grid((20, 20), (0, 20 - rightSpace), rowspan=20, colspan= rightSpace)
        rightVertBar.axis('off')
    if topSpace:
        topHorizBar = canvas.subplot2grid((20, 20), (0, leftSpace), rowspan=topSpace, colspan = 20 - leftSpace - rightSpace)
        topHorizBar.axis('off')
    if bottomSpace:
        bottomHorizBar = canvas.subplot2grid((20, 20), (20 - bottomSpace, leftSpace), rowspan= bottomSpace, colspan = 20 - leftSpace - rightSpace)
        bottomHorizBar.axis('off')
    plt = canvas.subplot2grid((20, 20), (topSpace, leftSpace), rowspan = 20 - topSpace - bottomSpace, colspan = 20 - leftSpace - rightSpace)

    taxaSpace = set()
    for sample in sampleDataTable:
        for taxa in sampleDataTable[sample]:
            taxaSpace.add(taxa)
    if not valueOrderList:
        valueOrderList = list(taxaSpace)
    if not sampleOrderList:
        sampleOrderList = list(sampleDataTable.keys())
    valueOrderSet = set(valueOrderList)
    if not len(valueOrderSet) == len(valueOrderList):
        raise ValueError("Value order list was given with duplicate entries. %s" %valueOrderList)
    if not taxaSpace.issubset(valueOrderSet):
        missingTaxa = valueOrderSet.difference(taxaSpace)
        raise ValueError("Value order list is missing some values relative to data given.\nMissing values: %s\nValue set given: %s\nValues found in data: %s" %(missingTaxa, valueOrderList, taxaSpace))
    sampleSpace = set(sampleDataTable.keys())
    orderedSampleSet = set(sampleOrderList)
    if not sampleSpace == orderedSampleSet:
        missingSamples = sampleSpace.difference(orderedSampleSet).union(orderedSampleSet.difference(sampleSpace))
        raise ValueError("Different samples in sample order list and provided sample names.\nMissing: %s\nGiven samples: %s\nSample order: %s" %(missingSamples, sampleSpace, sampleOrderList))
    plotDataMatrix = []
    for index, sample in enumerate(sampleOrderList):
        plotDataMatrix.append([])
        for value in valueOrderList:
            if value in sampleDataTable[sample]:
                plotDataMatrix[index].append(sampleDataTable[sample][value])
            else:
                plotDataMatrix[index].append(0)
    plotBarInfo = []
    width = 0.5
    for index, data in enumerate(plotDataMatrix):
        bottomValue = 0
        for colorIndex, element in enumerate(data):
            if index == 0:
                plotBarInfo.append(
                    plt.bar(index, element, width, bottom=bottomValue)
                )
            else:
                plt.bar(index, element, width, bottom=bottomValue, color = plotBarInfo[colorIndex][0]._facecolor)
            bottomValue += element
    plt.set_ylabel("Relative Abundance (%)")
    if sampleName:
        plt.set_title(sampleName)
    plt.set_yticks(range(0, 101, 10))
    plt.set_xticks(range(len(sampleOrderList)))
    if len(sampleOrderList) >= 11:
        rotation = 80
        alignment = 'center'
    elif len(sampleOrderList) >= 4:
        rotation = 40
        alignment = 'right'
    elif len(sampleOrderList) == 3:
        rotation = 20
        alignment = 'right'
    else:
        rotation = 0
        alignment = 'center'
    plt.set_xticklabels(sampleOrderList, rotation=rotation, ha=alignment)
    orderedColorList = [barInfo[0] for barInfo in plotBarInfo]
    if printNameTable:
        printValueOrderList = []
        for value in valueOrderList:
            if value in printNameTable:
                printValueOrderList.append(printNameTable[value])
            else:
                printValueOrderList.append(value)
    else:
        printValueOrderList = valueOrderList
    printValueOrderList.reverse()
    orderedColorList.reverse()
    plt.legend(orderedColorList, printValueOrderList, loc='center left', bbox_to_anchor=(1, 0.5))
    #canvas.tight_layout()
    byteStream = io.BytesIO()
    canvas.savefig(byteStream, format=format)
    byteStream.seek(0)
    encodedImage = base64.b64encode(byteStream.read())
    canvas.clf()
    plt.clear()
    canvas.close()
    return encodedImage.decode()
