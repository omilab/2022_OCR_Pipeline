# Upload documents to a single Transkribus Collection

import argparse
import glob
import logging
import os
from typing import Any
from xml.etree import ElementTree

from tqdm import tqdm
from TkbsApiClient import TranskribusClient
from TkbsDocument import Document
from utilities import add_transkribus_args, init_tkbs_connection, save_job_indication, setup_logging, setup_parser


def get_args() -> Any:
    parser = setup_parser()
    add_transkribus_args(parser)
    args = parser.parse_args()
    setup_logging(args)

    return args

# Gather all documents, returning a list of (base_dir, Document object)
def gather_documents(base: str):
    folders = glob.glob(os.path.join(base, '**', 'legacy_output'), recursive=True)
    folders = [os.path.dirname(f) for f in folders]

    for folder in folders:
        doc = Document()
        doc.load_legacy_data(folder)
        yield (folder, doc)


# Upload Transkribus document, returning the document id and job id
def upload_document(tkbs: TranskribusClient, args: argparse.Namespace, doc_dir: str, doc: Document) -> tuple[int, int]:
    ImgObjects = {}
    pageImages = doc.img_names_by_pgnum()
    pageXmls = doc.pxml_names_by_pgnum()
    for key, value in pageImages.items():
        ImgObjects[key] = open(os.path.join(doc_dir, value), 'rb')
    XmlObjects = {}
    for key, value in pageXmls.items():
        XmlObjects[key] = open(os.path.join(doc_dir, value), 'rb')
    pfiles = []
    jstring = '{"md": {"title": "' + doc.title + '", "author": "' + args.tkbs_user + '", "description": "N/A"}, "pageList": {"pages": [' # type:ignore
    psik = ', '
    for key, value in pageImages.items():
        if len(pageImages) <= int(key):
            psik = ''
        jstring = jstring + '{"fileName": "' + value + '", "pageXmlName": "' + pageXmls[key] + '", "pageNr": ' + key + '}' + psik
        pfiles.append({'img': (value, ImgObjects[key], 'application/octet-stream'), 'xml': (pageXmls[key], XmlObjects[key], 'application/octet-stream')})
    jstring = jstring + ']}}'
    response = tkbs.createDocFromImages(args.tkbs_collection_id, jstring, pfiles)
    tree = ElementTree.fromstring(response)
    uploadElement = tree.find('uploadId')
    if uploadElement is None:
        raise ValueError('No upload Id')
    try:
        docid = int(uploadElement.text or 'xxx')
    except:
        raise ValueError(f"Can't parse upload Id '{uploadElement.text}'")

    jobElement = tree.find('jobId')
    if jobElement is None:
        raise ValueError("No job id")
    try:
        jobid = int(jobElement.text or 'xxx')
    except:
        raise ValueError(f"Can't parse job id '{jobElement.text}'")
    jobid = jobElement.text

    return docid, jobid

def find_existing(doc: Document, existing_docs: list[Any]) -> int | None:
    for existing in existing_docs:
        if existing['title'] == doc.title:
            return int(existing['docId'])
    return None


def main():
    args = get_args()
    setup_logging(args)
    tkbs = init_tkbs_connection(args)

    print(f'Loading existing documents from Transkribus collection {args.tkbs_collection_id}')
    logging.info(f'Loading existing documents from Transkribus collection {args.tkbs_collection_id}')

    logging.debug('Loading existing documents from Transkribus')
    existing_docs = tkbs.listDocsByCollectionId(args.tkbs_collection_id)

    uploaded = skipped = 0

    print(f'Uploading documents from {args.base} to Transkribus collection {args.tkbs_collection_id}')
    for folder, doc in tqdm(gather_documents(args.base)):
        existing_doc_id = find_existing(doc, existing_docs)
        if existing_doc_id:
            if not args.overwrite:
                logging.info(f'Skipping {doc.title}, it already exists')
                skipped += 1
                continue
            else:
                logging.info(f'Deleting document {doc.title} before uploading it again')
                tkbs.deleteDocument(args.tkbs_collection_id, existing_doc_id)

        logging.info(f'Uploading document {doc.title}')
        doc_id, job_id = upload_document(tkbs, args, os.path.join(folder, 'legacy_output'), doc)
        save_job_indication(folder, job_id)
        uploaded += 1

    print(f"Done, uploaded {uploaded} documents, skipped {skipped}")

if __name__ == '__main__':
    main()