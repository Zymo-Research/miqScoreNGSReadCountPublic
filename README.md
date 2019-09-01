# MIQ (Measurement Integrity Quotient) Score Calculator for NGS Reads

With our standardized samples for molecular analysis, we make quantitative, objective benchmarking possible, but at Zymo Research, our motto is *"The beauty of science is to make things simple*."  With that in mind, we present you with the MIQ score, a simplified metric for grading the accuracy of an analysis relative to a known standard sample input.

#### Publication
Publication on this method is pending.  Watch this space for news and a link once it is available on bioRXiv.

## Quick Start Guide

### Prerequisites

This package is designed to work with Python 3.6.7 and Matplotlib 3.0.2.  It will most likely be compatible with other recent versions of both.


### Installation

This package is designed to be either copied in as a Python module or (my preferred method) cloned in as a git submodule

## Using the NGS MIQ scoring package

#### Key Classes and Functions

The general workflow for this system is to load a set of standard reference data that will describe various properties of your standard sample, generate read counts or some other measure of frequency or relative abundance of signals from your analysis of the standard stamples, and create a Python object from these that contains a MIQ Score for the sample as well as some plots that may give information as to the source of any bias or inaccuracy in the test.

----------
##### miqScoreNGSReadCountPublic.referenceHandler.StandardReference(standardDataPath)
This method is your most likely starting point for the use of this package.  This method will instantiate your StandardReference class object.  The path should point to JSON formatted key:values that describe the standard as well as how data may be delivered and aliases for template names.  For an example of this using the Zymo Research Mock Microbial Community Standard, please look in the reference handler directory of this package.

| Attribute        | Type             | Description |
| --------------- |:--------------:|-------------|
nameLookup | dict | Key values linking potential templates (reference contigs) to their source name. Especially useful in microbiome, since a read may map to different templates but still be effectively the same source.
printNames | dict | Key values linking source names to how they should be printed for figures
itemIDs | list | List of possible read sources for this standard
sortings | dict of lists | Possible ways to sort the read sources, generally useful to detect bias at one end of the spectrum or the other
expectedValues | dict of dicts | Dictionary of analysisMethod:readSource:expectedValue.  Generally relative abundances in percent.
analysisMethods | list | List of analysis methods from the above value.

--------
##### miqScoreNGSReadCountPublic.MiqScoreCalculator(standardReference: *miqScoreNGSReadCountPublic.referenceHandler.StandardReference*, analysisMethod:*str*, percentToleranceInStandard:*[int, float]=0*, floor:*[int, float]=0*)
This method will instantiate a MIQ Score calculator object, which is the "business end" of this entire package.  Required arguments include a standard reference of StandardReference type (see previous item for more info on that type) and an analysis method (chosen from possible analysis methods for the standard).  If you are unsure of potential analysis methods for the standard, standardReference.analysisMethods will list them if the object is loaded, or they will be visible in the JSON storing the reference data.  Optional arguments include percentToleranceInStandard, which represents the manufacturing tolerances of your standard expressed as a percentage (enter 15 for 15% and not 0.15), and floor, which is a minimum value for the miqScore (defaults to zero, but can be set to None if unwanted).  The percent tolerance will be used to adjust any deviations from expected that are observed in your measurement, as this package assumes that any deviation from expected that can be explained by manufacturing tolerances in the standard should be treated as such.  Generally, having the miq score floor out to zero improves the ease of understanding and rapid analysis for scores where there is an upper limit of 100 and no set lower limit.

##### miqScoreNGSReadCountPublic.MiqScoreCalculator.calculateMiq(sampleData:*dict*, sampleID:str=*None*)
This method will calculate a MIQ score for a set of input data and return a MiqScoreData object.  The MiqScoreData object is the main output from this package and has the following attributes and methods:

##### miqScoreNGSReadCountPublic.MiqScoreCalculator.MiqScoreData
Reads will generally be divided into expected/reference reads and unexpected/nonreference reads here.  Expected/reference reads will be only reads that aligned to an expected read source.  Unexpected/nonreference reads will be those that aligned to something other than an expected reference sequence, were unalignable, or were removed before alignment.  These can help diagnose problems in library quality or other issues.  These are not used to calculate the MIQ score (although they can be used to explain an unexpectedly low score due to issues with sample/library preparation and sequencing).

| Attribute/method        | Type             | Description |
| --------------- |:--------------:|-------------|
miqScore | float | The MIQ score, which may be floored if a floor value was set when calculating
rawMiqScore | float | The MIQ score without any floor.  Will be equivalent to miqScore if no floor was set
referenceReadCounts | dict | Key values of reads from expected sources:count. Keys will be their unique identifier from the StandardReference object
nonReferenceReadCounts	|	dict	|	Dictionary with all nonreference/unexpected read counts and counts of any reads removed prior to alignment
samplePercentages	|	dict	|	Relative abundances of each reference read
samplePercentagesOfExpected	|	dict	|	Abundances of each reference read type relative to expected (*ie*. 100 means that the count seen was **exactly** what was expected)
percentToleranceInStandard	|	float	|	Directly stored from the MiqScoreCalculator object that created it for tracibility
analysisMethod	|	str	|	Directly stored from the MiqScoreCalculator object that created it for tracibility
standardReference	|	StandardReference	|	Directly stored from the MiqScoreCalculator object that created it for tracibility
readFateTable	|	dict	|	This table will be similar to nonReferenceReadCounts except that it will contain an additional group called "Reference" that has a count of all reads that ultimately aligned to an expected reference sequence.
sampleID	|	str	|	Directly stored from the MiqScoreCalculator object that created it for tracibility
storePlots	|	bool	|	If set to false, plots will be regenerated each time the plot creation method is called, otherwise they will be stored (see below for how)
plots	|	dict	|	Dictionary used to store plots.  Plots are all stored as base64-encoded PNG files (although other formats can be specified when calling the plot creation method).  Keys will be plot names or groups of plots. Values will either be the base64 string of the plot file or, if is a group of plots (such as radar plots), a dictionary of plotName:plotData in base64.
makeReadFateChart(format:*str="png"*, forceRedraw:*bool=False*, readFatePrintNames:*dict=None*)	|	str (base64)	|	Generates a pie chart describing the fate of all reads that entered the analysis from the read fate table.  Expected reads will be grouped as "Reference."  *format* should denote a valid file saving format for matplotlib and defaults to PNG (although SVG is another very good option for vector format).  *forceRedraw* will cause the plot to be regenerated even if it has already been saved. *readFatePrintNames* can contain a dictionary where any read fate identifier in the read fate table with a key present will be changed to the corresponding value when generating a key for the figure.
makeRadarPlots(format:str="png", forceRedraw:bool=False)	|	dict of str:base64	|	Iterates over possible sorting methods for standard and generates radar plots to help with bias detection.  Output will be a dictionary of sortingMethod:base64 of plot.  This takes optional *format* and *forceRedraw* objects with the same behavior as *makeReadFateChart*.
makeCompositionBarPlot(goodExample:dict=None, badExample:dict=None)	|	str (base64)	|	Makes a composition bar plot that is typical of microbiome samples.  Can take in a good example of samplePercentages (in a dictionary) and a badExample likewise.
jsonOutput	|	str	|	Returns a string of JSON-formatted output to store a detailed report on the sample

-----

##### miqScoreNGSReadCountPublic.MiqScoreCalculator.generateReport(replacementTable:*dict*, template:*str*, sampleMiq:*MiqScoreData*, goodExampleMiq:*MiqScoreData*, badExampleMiq:*MiqScoreData*, readFatePrintNames:*dict=None*)
Reads will generally be divided into expected/reference reads and unexpected/nonreference reads here.  Expected/reference reads will be only reads that aligned to an expected read source.  Unexpected/nonreference reads will be those that aligned to something other than an expected reference sequence, were unalignable, or were removed before alignment.  These can help diagnose problems in library quality or other issues.  These are not used to calculate the MIQ score (although they can be used to explain an unexpectedly low score due to issues with sample/library preparation and sequencing).

| Attribute/method        | Type             | Description |
| --------------- |:--------------:|-------------|
replacementTable	|	dict	|	Dictionary of values to replace in the HTML template (value identifiers should be surrounded with two percent symbols for %%VALUE%%
template	|	str (HTML template)	|	HTML template with values to be replaced surrounded by double percents (see above)


## Contributing

We welcome and encourage contributions to this project from the scientific community and will happily accept and acknowledge input (and possibly provide some free kits as a thank you).  We aim to provide a positive and inclusive environment for contributors that is free of any harassment or excessively harsh criticism. Our Golden Rule: *Treat others as you would like to be treated*.

## Versioning

We use a modification of [Semantic Versioning](https://semvar.org) to identify our releases.

Release identifiers will be *major.minor.patch*

Major release: Newly required parameter or other change that is not entirely backwards compatible
Minor release: New optional parameter
Patch release: No changes to parameters

## Authors

- **Michael M. Weinstein** - *Project Lead, Programming and Design* - [michael-weinstein](https://github.com/michael-weinstein)
- **Aishani Prem** - *Testing, Design* - [AishaniPrem](https://github.com/AishaniPrem)
- **Mingda Jin** - *Testing, Code Review* - [jinmingda](https://github.com/jinmingda)
- **Shuiquan Tang** - *Design* - [shuiquantang](https://github.com/shuiquantang)
- **Jeffrey Bhasin** - *Design, Code Review* - [jeffbhasin](https://github.com/jeffbhasin)
- **Justin J. Lin**  - *Design* - [jjlinscientist](https://github.com/jjlinscientist)
- **Ryan Kemp**  - *Design* - [Zymo Research](https://www.zymoresearch.com)
- **Brian Janssen**  - *Design* - [Zymo Research](https://www.zymoresearch.com)

See also the list of [contributors](https://github.com/Zymo-Research/miqScoreNGSReadCountPublic/contributors) who participated in this project.

## License

This project is not currently licensed  it will likely be licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details.
This license restricts the usage of this application for non-open sourced systems. Please contact the authors for questions related to relicensing of this software in non-open sourced systems.

## Acknowledgments

We would like to thank the following, without whom this would not have happened:
* The Python Foundation
* The staff at Zymo Research
* Our customers

---------------------------------------------------------------------------------------------------------------------

#### If you like this software, please let us know at info@zymoresearch.com.
#### Please support our continued development of free and open-source microbiomics applications by checking out the latest microbiomics offerings from [ZymoBIOMICS](https://www.zymoresearch.com/pages/zymobiomics-portfolio)


