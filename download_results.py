# Download HTR results from Transkribus

import json
import logging
import os
import shutil
from typing import Any, Dict, Union
import xml.etree.cElementTree as ET

from tqdm import tqdm
from TkbsApiClient import TranskribusClient
from TkbsDocument import Document
from utilities import add_transkribus_args, find_existing, gather_document_folders, init_tkbs_connection, load_document, setup_logging, setup_parser


def get_args() -> Any:
    parser = setup_parser()
    parser.add_argument('--line-threshold', type=int, default=13, help='Lines shorter than the threshold are ignored')
    add_transkribus_args(parser)
    args = parser.parse_args()

    return args

def download(tkbs: TranskribusClient, collection_id: int, doc_id: int, folder: str, metafilename: str) -> Union[Dict, None]:
    response = tkbs.download_document(collection_id, doc_id, folder)
    pages = len(response[1]) # type: ignore
    if pages > 0:
        with open(os.path.join(folder, metafilename)) as j:
            data = json.load(j)
            return data
    return None

def delete_garbage_text(pgfile: str, garbage_line_width: int):
    ET.register_namespace('', "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15")
    tree = ET.ElementTree(file=pgfile)
    xml_changed = False
    for myelement in tree.iterfind('*/*/*'):
        if myelement.tag.endswith("TextLine"):
            line_changed = False
            textchild = None
            for mychild in myelement.iter():
                if mychild.tag.endswith("TextEquiv"):
                    textchild = mychild
                if mychild.tag.endswith("Baseline"):
                    points = mychild.attrib.get('points')
                    points_list = points.split(" ") if points else []
                    smallpoint = int(points_list[0].split(",")[0])
                    bigpoint = int(points_list[(len(points_list) - 1)].split(",")[0])
                    linewidth = bigpoint - smallpoint
                    if linewidth <= garbage_line_width:
                        xml_changed = True
                        line_changed = True
            if line_changed and textchild != None:
                for tnode in textchild.iter():
                    tnode.text = ""
    if (xml_changed):
        tree.write(pgfile)
        return True
    else:
        return False


def download_results(tkbs: TranskribusClient, doc: Document, collection_id: int, doc_id: int, output_folder: str, garbage_width: int):
    logging.debug(f'Downloading all data of {doc.title}')
    ocrdocjson = download(tkbs, collection_id, doc_id, output_folder, doc.tkbs_meta_filename)
    pageids = doc.load_tkbs_page_ids(ocrdocjson)

    if garbage_width > 0:
        logging.debug(f'Removing garabge lines in {doc.title}')
        for num, fname in doc.pxml_names_by_pgnum().items():
            fullname = os.path.join(output_folder, fname)
            delete_garbage_text(fullname, garbage_width)


def main():
    args = get_args()
    setup_logging(args)
    tkbs = init_tkbs_connection(args)

    print(f'Downloading HTR output from Transkribus collection {args.tkbs_collection_id}')
    logging.info(f'Downloading HTR output from Transkribus collection {args.tkbs_collection_id}')

    existing_docs = tkbs.listDocsByCollectionId(args.tkbs_collection_id)

    downloaded = skipped = error = 0

    folders = list(gather_document_folders(args.base))
    for folder in tqdm(folders):
        doc = load_document(folder)

        existing_doc = find_existing(doc, existing_docs)
        if not existing_doc:
            logging.error(f"Can't locate document {doc.title} in collection")
            error += 1
            continue

        output_folder = os.path.join(folder, 'transkribus_output')
        if os.path.exists(output_folder):
            if not args.overwrite:
                logging.info(f'Skipping {doc.title}, output folder already exists')
                skipped += 1
                continue
            shutil.rmtree(output_folder)
            logging.debug(f'Deleted old results of {doc.title}')

        logging.info(f'Downloading data for {doc.title}')
        download_results(tkbs, doc, args.tkbs_collection_id, existing_doc['docId'], output_folder, args.line_threshold)
        downloaded += 1

    print(f"Done, downloaded {downloaded}, skipped {skipped}, errpr {error}")


if __name__ == '__main__':
    main()
