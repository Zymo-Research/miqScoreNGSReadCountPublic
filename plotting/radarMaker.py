import matplotlib.pyplot as plt
from math import pi
import matplotlib.patches


def makeTopDownList(orderedList:list):
    reverseOrderedList = orderedList[::-1]
    topDownList = []
    addToEnd = True
    while reverseOrderedList:
        itemToAdd = reverseOrderedList.pop(0)
        if addToEnd:
            topDownList.append(itemToAdd)
        else:
            topDownList.insert(0, itemToAdd)
        addToEnd = not addToEnd
    return topDownList


def getSamplesAndVariables(data:dict):
    samples = list(data.keys())
    variables = set(data[samples[0]].keys())
    for sample in samples:
        if not set(data[sample].keys()) == variables:
            raise ValueError("All samples must have the same strains present. Sample %s appears to be incorrect" %sample)
    return (samples, variables)


def getListOfAngles(variableCount:int):
    angles = [angle / float(variableCount) * 2 * pi for angle in range(variableCount)]
    angles.append(angles[0])
    return angles


def makeRadarPlot(data:dict, dataRankOrder:list, orderedFeature:str, topHigh = True, sampleRestriction = None, titleAppend="", format:str="png", printNames:dict = None):
    import io
    import base64
    plt.figure(dpi=300)
    #Setting up the triangle plot on the left
    trianglePlotAxes = plt.subplot2grid((4, 5), (0, 0), rowspan = 4)
    plt.xlim(0, 1.5)
    plt.ylim(0, 5)
    topHighTriangle = ((0,0), (0,5), (1,5))
    bottomHighTriangle = ((0,0), (0,5), (1,0))
    if topHigh:
        triangleCoordinates = topHighTriangle
    else:
        triangleCoordinates = bottomHighTriangle
    triangle = plt.Polygon(triangleCoordinates, color=(0, 1, 0))
    plt.gca().add_patch(triangle)
    trianglePlotAxes.set_title(" " + orderedFeature)
    trianglePlotAxes.axis('off')


    #Setting up radar plot on the right (starting with the background)
    radarPlotAxes = plt.subplot2grid((4, 5), (0, 1), rowspan = 4, colspan = 4, polar = True)
    samples, variables = getSamplesAndVariables(data)
    for variable in dataRankOrder:
        if not variable in variables:
            raise ValueError("Got a variable in the rank order that is missing from the data: %s" %variable)
    displayOrderedVariables = makeTopDownList(dataRankOrder)
    variableCount = len(variables)
    angles = getListOfAngles(variableCount)

    #setting the theta so that the first variable points directly up (0.5 pi radians)
    radarPlotAxes.set_theta_offset(pi / 2)
    radarPlotAxes.set_theta_direction(-1)

    # Draw one axis per variable and add labels to them
    plt.xticks(angles[:-1], list(data)[1:])

    # Setup our y-values and axes
    radialAxes = [0, 50, 100, 150, 200]
    radarPlotAxes.set_rlabel_position(0)
    plt.yticks(radialAxes, [str(mark) for mark in radialAxes], color="grey", size=7)
    plt.ylim(min(radialAxes), max(radialAxes))

    # Make a dark circle around the 100% axis to mark our target value
    targetCircleResolution = 720 #number of points to use in drawing the circle
    targetCircleAngles = getListOfAngles(targetCircleResolution)
    targetCircleRadii = [100] * (targetCircleResolution + 1)
    radarPlotAxes.plot(targetCircleAngles, targetCircleRadii, 'k-', linewidth = 2)

    # Iteratively add the plots to the radar, limited to the number of available colors
    colorList = ["b", "r", "y", "g"]
    if len(samples) > len(colorList):
        raise ValueError("More samples present than colors listed for plotting.  Please either limit the number of samples per plot or increase the number of colors in use.  Suggest more plots with fewer samples, since too many samples on one plot is unreadable.")
    if not sampleRestriction == None:
        if type(sampleRestriction) == str:
            sampleRestriction = [sampleRestriction]
    displayedSamples = []
    for sample in samples:
        if not sampleRestriction == None:
            if not sample in sampleRestriction:
                continue
        displayedSamples.append(sample)
        values = []
        for variable in displayOrderedVariables:
            values.append(data[sample][variable])
            # close the shape by relisting the last value
        values.append(values[0])
        radarPlotAxes.plot(angles, values, linewidth=1, linestyle='solid', label=sample)
        radarPlotAxes.fill(angles, values, 'b', alpha=0.1)
    if printNames:
        xTickList = []
        for name in displayOrderedVariables:
            xTickList.append(printNames[name])
    else:
        xTickList = displayOrderedVariables
    radarPlotAxes.set_xticklabels(xTickList)
    if displayedSamples:
        if len(displayedSamples) > 1:
            legend = radarPlotAxes.legend(displayedSamples)
        else:
            title = displayedSamples[0]
            if titleAppend:
                title += " " + titleAppend
            radarPlotAxes.set_title(title)
    plt.tight_layout()
    byteStream = io.BytesIO()
    plt.savefig(byteStream, format=format, bbox_extra_artists=radarPlotAxes)
    byteStream.seek(0)
    encodedImage = base64.b64encode(byteStream.read())
    plt.clf()
    plt.close()
    return encodedImage.decode()

