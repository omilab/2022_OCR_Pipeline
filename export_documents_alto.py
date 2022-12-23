import json
import logging
import os
from typing import Any
from xml.etree import ElementTree

from tqdm import tqdm
from TkbsDocument import Document
from utilities import add_transkribus_args, find_existing, gather_document_folders, init_tkbs_connection, load_document, save_job_indication, setup_logging, setup_parser

from TranskribusPyClient import TranskribusClient

params="""
{   "commonPars" : {
      "pages" : "1",
      "doExportDocMetadata" : true,
      "doWriteMets" : true,
      "doWriteImages" : true,
      "doExportPageXml" : true,
      "doExportAltoXml" : true,
      "doExportSingleTxtFiles" : false,
      "doWritePdf" : false,
      "doWriteTei" : false,
      "doWriteDocx" : false,
      "doWriteOneTxt" : false,
      "doWriteTagsXlsx" : false,
      "doWriteTagsIob" : false,
      "doWriteTablesXlsx" : false,
      "doWriteStructureInMets" : false,
      "doCreateTitle" : false,
      "useVersionStatus" : "Latest version",
      "writeTextOnWordLevel" : false,
      "doBlackening" : false,
      "selectedTags" : [ "add", "date", "Address", "human_production", "supplied", "work", "unclear", "sic", "structure", "div", "highlight", "place1", "regionType", "speech", "person", "gap", "organization", "comment", "abbrev", "place", "add1", "Initial", "lat" ],
      "font" : "FreeSerif",
      "splitIntoWordsInAltoXml" : true,
      "pageDirName" : "page",
      "fileNamePattern" : "${filename}",
      "useHttps" : true,
      "remoteImgQuality" : "orig",
      "doOverwrite" : true,
      "useOcrMasterDir" : true,
      "exportTranscriptMetadata" : true,
      "updatePageXmlImageDimensions" : false
   },
   "altoPars" : {
      "splitIntoWordsInAltoXml" : true
   },
   "pdfPars" : {
      "doPdfImagesOnly" : false,
      "doPdfImagesPlusText" : true,
      "doPdfWithTextPages" : false,
      "doPdfWithTags" : false,
      "doPdfWithArticles" : false,
      "doPdfA" : false,
      "pdfImgQuality" : "view"
   },
   "docxPars" : {
      "doDocxWithTags" : false,
      "doDocxPreserveLineBreaks" : false,
      "doDocxForcePageBreaks" : false,
      "doDocxMarkUnclear" : false,
      "doDocxKeepAbbrevs" : false,
      "doDocxExpandAbbrevs" : false,
      "doDocxSubstituteAbbrevs" : false,
      "doDocxWriteFilenames" : false,
      "doDocxIgnoreSuppliedTag" : false,
      "doDocxShowSuppliedTagWithBrackets" : false
   }
}
"""

def get_args():
    parser = setup_parser()
    add_transkribus_args(parser)
    args = parser.parse_args()

    return args

def lines_in_doc(doc: dict):
    return doc['md']['nrOfLines'] > 0

def main():

    print('Running export to alto started')
    logging.debug('Running export to alto started')

    args = get_args()
    setup_logging(args)

    tkbs = TranskribusClient(sServerUrl=args.tkbs_server)
    tkbs.auth_login(args.tkbs_user, args.tkbs_password, True)
    #tkbs = init_tkbs_connection(args)

    print(f'Running export to alto documents from Trankribus collection {args.tkbs_collection_id}')
    logging.info(f'Running export to alto on all documents from Trankribus collection {args.tkbs_collection_id}')

    logging.debug('Loading documents from Transkribus')
    existing_docs = tkbs.listDocsByCollectionId(args.tkbs_collection_id)

    jobs_issued = skipped = missing = 0

    folders = list(gather_document_folders(args.base))
    for folder in tqdm(folders):
        doc = load_document(folder)
        existing = find_existing(doc, existing_docs)
        if not existing:
            print(f"Can't locate document for {folder}, skipping")
            logging.warning(f"Can't locate document for {folder}, skipping")
            missing += 1
            continue
        tkbs_doc_id = int(existing['docId'])

        output_folder = os.path.join(folder, 'transkribus_alto_output')
        if os.path.exists(output_folder):
            if not args.overwrite:
                print(f'Skipping {doc.title}, it already has a transkribus output')
                logging.info(f'Skipping {doc.title}, it already has a transkribus output')
                skipped += 1
                continue
        
        logging.info(f'Starting export on document {doc.title}')
        job_id  = tkbs.exportCollection(args.tkbs_collection_id, tkbs_doc_id, params)
        save_job_indication(folder, job_id, "job-status-export-alto.json")
        jobs_issued += 1

    print(f'Done, {jobs_issued} jobs issued, {missing} documents missing, {skipped} documents skipped')


if __name__ == '__main__':
    main()