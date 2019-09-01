def performReplacement(template:str, replacementTable:dict):
    import re
    for target in replacementTable:
        targetRegex = "%%" + target + "%%"
        template = re.sub(targetRegex, replacementTable[target], template)
    return template


def generateReport(template:str, replacementTable):
    report = performReplacement(template, replacementTable)
    return report
