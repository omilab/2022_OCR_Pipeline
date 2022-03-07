# HOP  (Historical OCR Pipeline)
## Introduction
HOP is a tool that can massively handle legacy products of various OCR systems, such as Olive Software's system products and bring more accurate OCR using [Transkribus](https://transkribus.eu/Transkribus/). It is a pipeline that transforms PRXML files via Transkribus into a research corpus,  and deals with the challenge of improving the OCR without losing the valuable work that was done hitherto to analyze the layout and content structure of the newspapers. 
for this we created an workflow which converts the legacy format to an open format, on which the improved text recognition technologies can run to produce improved output that meets the threshold and requirements of text analytical research.

## Getting started

### Prerequisites
- Python 3.10
- Username in Transkribus
- HTR model in Transkribus (for Hebrew 19th century press, we used 'OMILab')
- Layout analysis line detection model (e.g. Preset)

##### Notes on using Transkribus' services:
Around September 2020 Transkribus  will be available as payed service, in the framework of the READ Coop:  https://read.transkribus.eu/coop/. 
## Tutorial
TODO: Rewrite tutorial to correspond to the new pipeline methodology
### stage 1 - unzip the Document.zip files
### stage 2 - Convert olice input to transkribus

### stage 3 - Upload to Transkribus

### stage 4 - Run line detection on Transkribus

### stage 5 - Check job output, to make sure everything is OK

### stage 6 - Run HTR on Transkribus

### stage 6 - Check job output, making sure everything is OK

### stage 7 - Download transkribus results

### stage 8 - Export transkribus output to various formats

### stage 1 - Legacy format to Transkribus format converter
This script allows the user to convert directories from the legacy format into the PAGE.XML files that can be uploaded later into Transkribus or used in another way.

#####INPUT DIRECTORY STRUCTURE:
For proper system operation, make sure your input a parent folder, with folders that are a Newspaper folder with the following structure:
  * TOC.xml file
  * a document folder that includes:
  *  PDF of the newspaper issue
  *  A Folder for every  page in the issue that includes:
     - PgXXX.xml (where XXX is the page number; this file include a strcuctural inforamtion about this page)
     - ArYYY.xml for every article in this page (where YYY is the article number like that appears in the PgXXX.xml file; this file include a strcuctural inforamtion about this article)
     - AdYYY.xml for every advertisement in this page (where YYY is the advertisement number like that appears in the PgXXX.xml file; this file include a strcuctural inforamtion about this advertisement)
     - Img folder that includes images of all the objects in the page together and alone.


For a demo, you may use the directory "resources_for_tests" which is included in the repo. 
You will see that the directory structure is like the description above.

Execute the script "legacy_to_tkbs_format_converter.py" via command line (or any other way you choose). Now, you'll be asked to insert the path of the  directory that you want to convert. You can choose a parent folder, and all the sub-folders will be converted.
![insert path please](https://github.com/yanirmr/historical_press/blob/master/OCR_Pipeline/images_for_tutorial/tutorial1.JPG)

For demo, use "resources_for_tests":
![resources_for_tests](https://github.com/yanirmr/historical_press/blob/master/OCR_Pipeline/images_for_tutorial/tutorial2.JPG)

Once the script is executed (this should take less than one second per folder; depending on size, of course). A successful response would contain an update on the number of successfully converted folders inside your directory and where to find them.
![successful response](https://github.com/yanirmr/historical_press/blob/master/OCR_Pipeline/images_for_tutorial/tutorial3.JPG)

### Part 2 - Work with Transkribus' API
With this part of the script you will upload the converted data from your directory to the Transkribus server, run layout analysis and your chosen HTR model. When running the script "tkbs_uploader.py" you will be prompted to insert:
* your transkribus username
* your transkribus password
* source path (use the same path you used for the first stage to work on the results of the conversion from legacy files)
* confirm (by pressing enter) or skip (by entering something else) performing line detection 
* the id of the collection in Transkribus where you would like to store the newspaper issues.
* the id of the HTR model

For convenience sake you can skip these stages by saving a file titled conf.json in the OCR_Pipeline folder, which includes this information:

<img src="https://github.com/omilab/historical_press/blob/master/OCR_Pipeline/images_for_tutorial/conf.JPG" width="300" height="250" />

### Part 3 - convert Transkribus' output to research input formats
At this stage you should have in your source directory a sub-directory with transkribus output, which may be converted in stage 3 to three formats: plain text, CSV, and/or TEI.XML. 

* Run "tkbs_exporter.py" and give as the source path the same directory as in previous stages. 
* you will be prompted to confirm (by pressing enter) or skip (by entering "NO") the conversion to each of the formats. 
    
#####OUTPUT FORMATS:
The output of s

## Roadmap
Future projects may further develop this pipeline:
* see "Issues", and especially issue 7: running parrallel processes.
* adding a conversion of corrected "Ground truth" data from Transkribus (in the output format of stage 2) to input formats for open source softare that enables training OCR models.
* Currently, part 1 of the pipeline converts the text regions from the legacy files into the PAGE.XML files, and uses other structural information - the order and structure types (Advertisements, Heads) - for the post processing. Adding a conversion of this information directly into the page.xml as custom attribute values of text regions will enable training e.g. region or article detection.
* In order to avail the output to external viewers the PAGE.XML will have to be converted to the viewer's input formats (e.g., METZ @ ALTO#)

## Authors
This project was initiated at [OMILab](https://www.openu.ac.il/en/omilab) and the pipeline was created by Nurit Greidinger, Yanir Marmor and Sinai Rusinek.

[OmiLab’s project on Historical Newspaper Archive Research](https://www.openu.ac.il/en/omilab/pages/historicalnewspaper.aspx) is run in collaboration with the [Historical Jewish Press project](https://web.nli.org.il/sites/JPress/English) of the Tel Aviv University and the National Library of Israel.  [The National Library of Israel (https://web.nli.org.il/sites/nli/english/pages/default.aspx)] provided access to selected image and OCR output files at the back end of JPRESS. 

## License
<img src="https://github.com/yanirmr/historical_press/blob/master/OCR_Pipeline/images_for_tutorial/CC-BY-SA_icon.svg.png" width="200" height="50" />

The code is licensed under a [Creative Commons Attribution-Share Alike 3.0](https://creativecommons.org/licenses/by-sa/4.0/). You are welcome to copy and redistribute the material in any medium or format, remix, transform, and build upon the material for any purpose, even commercially,  as long as you give appropriate credit to OMILab, provide a link to the license,  indicate if changes were made and distribute your contributions under the same license as the original. 

## Related projects
- [Transkribus Project](https://github.com/Transkribus)
"# 2022_OCR_Pipeline" 
