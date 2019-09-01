import matplotlib.pyplot as plt
import io
import base64

def makeReadFateChart(readFates:dict, sampleID:str=None, explodeCell:[str, list] = None, explodeCellSize:float = 0.1, saveFormat:str='png'):
    def makePrettyForPrint(label:str):
        label = label.replace("_like", "-like")
        label = label.replace("_Like", "-like")
        label = label.replace("_", " ")
        label = list(label)
        label[0] = label[0].upper()
        return "".join(label)
    plt.figure(dpi=300)
    labels = []
    explodeCellTable = []
    size = []
    if not explodeCell:
        explodeCell = []
    else:
        if type(explodeCell) == str:
            explodeCell = [explodeCell]
    orderedReadFateLabels = []
    if "Aligned To Reference" in readFates:
        orderedReadFateLabels.append("Aligned To Reference")
    for label in readFates:
        if not label == "Aligned To Reference":
            orderedReadFateLabels.append(label)
    for label in orderedReadFateLabels:
        labels.append(makePrettyForPrint(label))
        if label in explodeCell:
            explodeCellTable.append(explodeCellSize)
        else:
            explodeCellTable.append(0)
        size.append(readFates[label])
    plt.pie(size, explode=explodeCellTable, labels=labels, autopct='%1.1f%%', startangle=90)
    if sampleID:
        title = "%s READ FATES" %sampleID
    else:
        title = "READ FATES"
    plt.title(title)
    plt.axis('equal')
    plt.tight_layout()
    byteStream = io.BytesIO()
    plt.savefig(byteStream, format = saveFormat)
    byteStream.seek(0)
    encodedImage = base64.b64encode(byteStream.read())
    plt.clf()
    plt.close()
    return encodedImage.decode()

