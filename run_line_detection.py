
import json
import logging
from typing import Any

from tqdm import tqdm
from TkbsDocument import Document
from utilities import add_transkribus_args, gather_document_folders, init_tkbs_connection, load_document, setup_logging, setup_parser

def get_args():
    parser = setup_parser()
    add_transkribus_args(parser)
    args = parser.parse_args()

    return args
    
def lines_in_doc(doc: dict):
    return doc['md']['nrOfLines'] > 0

def find_existing(doc: Document, existing_docs: list[Any]) -> dict | None:
    for existing in existing_docs:
        if existing['title'] == doc.title:
            return existing
    return None

def main():
    args = get_args()
    setup_logging(args)
    tkbs = init_tkbs_connection(args)

    print(f'Running line detection on all documents from Trankribus collection {args.tkbs_collection_id}')
    logging.info(f'Running line detection on all documents from Trankribus collection {args.tkbs_collection_id}')

    logging.debug('Loading documents from Transkribus')
    existing_docs = tkbs.listDocsByCollectionId(args.tkbs_collection_id)

    jobs_issued = skipped = missing = 0

    folders = list(gather_document_folders(args.base))
    for folder in tqdm(folders):
        doc = load_document(folder)
        existing = find_existing(doc, existing_docs)
        if not existing:
            logging.warning(f"Can't locate document for {folder}, skipping")
            missing += 1
            continue
        tkbs_doc_id = int(existing['docId'])

        logging.debug(f'Loading document {tkbs_doc_id} from Transkribus')
        tkbs_doc = tkbs.getDocById(args.tkbs_collection_id, tkbs_doc_id)

        if lines_in_doc(tkbs_doc):
            if not args.overwrite:
                logging.info(f'Skipping {doc.title}, it has already been segmented')
                skipped += 1
                continue
        
        # Run segmentation
        page_dict = {
            "docList":
            {
                "docs":
                [{
                    "docId": tkbs_doc_id,
                    "pageList":
                    {
                        "pages":
                        [ page['pageId'] for page in tkbs_doc['pageList']['pages']]
                    }
                }]
            }
        }
        logging.info(f'Starting layout analysis on document {doc.title}')
        response = tkbs.analyzeLayout(args.tkbs_collection_id, json.dumps(page_dict), False, True)
        logging.debug(response)
        jobs_issued += 1

    print(f'Done, {jobs_issued} jobs issued, {missing} documents missing, {skipped} documents skipped')



if __name__ == '__main__':
    main()