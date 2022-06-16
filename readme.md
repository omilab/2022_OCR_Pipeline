# HOP  (Historical OCR Pipeline)
## Introduction
HOP is a tool that can massively handle legacy products of various OCR systems, such as Olive Software's system products and bring more accurate OCR using [Transkribus](https://transkribus.eu/Transkribus/). It is a pipeline that transforms PRXML files via Transkribus into a research corpus,  and deals with the challenge of improving the OCR without losing the valuable work that was done hitherto to analyze the layout and content structure of the newspapers. 
for this we created an workflow which converts the legacy format to an open format, on which the improved text recognition technologies can run to produce improved output that meets the threshold and requirements of text analytical research.

## Getting started

### Prerequisites
- Python 3.10
- Username and password of your Transkribus account
- HTR model in Transkribus (for Hebrew 19th century press, we used 'OMILab')
- Layout analysis line detection model (e.g. Preset)

### Setting up the code
You need to create a Python virtual environment. We usually place it in `env` under the repository's root.
Once created, activate the environment (`source env/bin/activate` on Linux and Mac, or `env\scripts\activate.ps1` on Windows) and install the required packages:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Setting up your data
The current pipeline works with Olive Software exported data. It was tested with data exported by the NLI, which we received in the following directory structure

- Publication Root Folder
  - Publication Year
    - Publication Month
      - Publication Day
        - PDF file of Publication
        - Document.zip - containing information about specific articles
        - TOC.xml - table of contents of the publication

The zip file contains the following:
        - Document (the content of the zip file)
          - Page  A Folder for every  page in the issue that includes:
            - PgXXX.xml (where XXX is the page number; this file include a strcuctural inforamtion about this page)
            - ArYYY.xml for every article in this page (where YYY is the article number like that appears in the PgXXX.xml file; this file include a strcuctural inforamtion about this article)
            - AdYYY.xml for every advertisement in this page (where YYY is the advertisement number like that appears in the PgXXX.xml file; this file include a strcuctural inforamtion about this advertisement)
            - Img folder that includes images of all the objects in the page together and alone.


The pipeline expects the data to be in this layout.

Note: The pipeline makes changes to the data in the folder - make sure you run it on a copy of the data. You do not want to lose data if we have a bug.

## The pipeline scripts
The pipeline consists of multiple Python scripts that you need to run one after the other. These scripts share some common parameters:

    * root publication folder - the location of the data the script needs to process
    * --help - show helpful information about the script.
    * --log-file - this file will contain a log of the run (defaults to `pipeline.log`)
    * --verbose - write more information to the log file
    * --overwrite - overwrite the output of a previous run.

This last flag, `--overwrite` deserves some attention. Some of the pipeline stages can take a while. Almost all the scripts know how to handle being stopped in the middle (due to a network error, power outage or someone accidentally rebooting your computer) - they try to pick up from where they have stopped. However, you sometimes really do want them to start over. For this, add the `--overwrite` flag - the scripts will try to delete the work of their last run and start over.

Some scripts interact with Transkribus, those need the following arguments:

    * --tkbs-user - your username at Transkribus (default - the OMILab's user name)
    * --tkbs-server - the URL for Transkribus (default - their existing URL)
    * --tkbs-password - your Transkribs password (Ah! I see what you tried to do there! There is no default)
    * --tkbs-collection-id - the Transkribus collection ID for the publication (no default)
## Processing a publication
The pipeline works on one publication at a time. Make sure you know the path to your Publication Root Folder.
### Setting up a Transkribus collection
The pipeline expects each publication to be uploaded to a single Transkribus collection. For this you will need to create the collection. You can either do that manually on Transkribus, and keep note of the collection ID, or run your handy script that manages Transkribus collections:

    python tkbs-collections.py create <collection-name> --tkbs-user <username> --tkbs-password <password>

This command will create a collection and print its ID. You need this collection ID for later.

### stage 1 - unzip the Document.zip files

    python unzip_documents.py <publication-root-folder>
### stage 2 - Convert olice input to transkribus format

    python convert_olive_to_tkbs <publication-root-folder>

### stage 3 - Upload to Transkribus

    python upload_documents <publication-root-folder>  --tkbs-collection-id <collection-id> --tkbs-user ... --tkbs-password ...

### stage 4 - Run line detection on Transkribus

    python run_line_detection.py <publication-root-folder>  --tkbs-collection-id <collection-id> --tkbs-user ... --tkbs-password ...

### stage 5 - Check job output, to make sure everything is OK

Line detection and OCR is handled by Transkribus in Jobs. These jobs can take a while to finish. You can check the job status on the Transkribus website, or run

    python check_jobs.py publication-root-folder> --tkbs-user ... --tkbs-password ...

Only once all the jobs have finished can you proceed to the next stage. Line detecton jobs are usually very quick on Transkribus.
### stage 6 - Run HTR on Transkribus

    python run_htr.py <publication-root-folder>  --tkbs-collection-id <collection-id> --tkbs-user ... --tkbs-password ...

### stage 6 - Check job output, making sure everything is OK

This is identical to stage 4, it can only take longer, sometimes a lot longer - depending on the number of jobs and the load on the Transkribus servers

    python check_jobs.py publication-root-folder> --tkbs-user ... --tkbs-password ...

Once all the jobs have finished you can move on
### stage 7 - Download transkribus results

    python download_results.py <publication-root-folder>  --tkbs-collection-id <collection-id> --tkbs-user ... --tkbs-password ...

### stage 8 - Export transkribus output to various formats

Now we have everything we need to export the results. The pipeline supports exporting to TEI, CSV and plain text files. 

    python export_results.py <publication-root-folder> --output-dir <output directory> --format <formats>

The formats can be any of `csv`, `tei`, `txt`

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
