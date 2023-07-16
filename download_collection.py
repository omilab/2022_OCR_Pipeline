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


def main():
    args = get_args()
    setup_logging(args)
    tkbs = init_tkbs_connection(args)

    print(f'Downloading HTR output from Transkribus collection {args.tkbs_collection_id}')
    logging.info(f'Downloading HTR output from Transkribus collection {args.tkbs_collection_id}')
    try:
        tkbs.download_collection(args.tkbs_collection_id, args.base, bForce = True)

        print(f'Done')
        logging.info(f'Done')
    except Exception as e:
        print(f"An exception occurred: {e}")


if __name__ == '__main__':
    main()
