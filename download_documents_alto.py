import json
import logging
import os
from typing import Any
from xml.etree import ElementTree
import requests

from tqdm import tqdm
from TkbsDocument import Document
from utilities import add_transkribus_args, find_existing, gather_document_folders, init_tkbs_connection, load_document, save_job_indication, setup_logging, setup_parser

from TranskribusPyClient import TranskribusClient

import zipfile
import xml.etree.ElementTree as ET

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

    print(f'Running download alto documents from Trankribus collection {args.tkbs_collection_id}')
    logging.info(f'Running download alto on all documents from Trankribus collection {args.tkbs_collection_id}')

    folders = list(gather_document_folders(args.base))
    print(folders)

    downloaded = 0
    skipped = 0
    errors_download = 0
    errors_edit_mets = 0

    for folder in tqdm(folders):
        job_indication_file = os.path.join(folder, 'job-status-export-alto.json')
        if os.path.exists(job_indication_file):
            try:
                f = open(job_indication_file)
                data = json.load(f)
                job_id = data["job"]

                if os.path.exists(f'{folder}\\export_document_{job_id}.zip'):
                    skipped += 1
                    continue

                resp = tkbs.getJobStatus(job_id)
                if resp['state'] == 'FINISHED':
                    zip_path = f'{folder}\\export_document_{job_id}.zip'
                    with open(zip_path, 'wb') as out_file:
                        content = requests.get(resp['result'], stream=True).content
                        out_file.write(content)
                        downloaded += 1

                        try:
                            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                outpath = f'{folder}\\export_document_{job_id}'
                                zip_ref.extractall(outpath)

                                unzipped_folders = list(gather_document_folders(args.base, f'mets.xml'))
                                for unzipped_folder in unzipped_folders:
                                    with open(os.path.join(unzipped_folder, "mets.xml"), "r+") as mets_file:
                                        mets = mets_file.read()
                                    mets = mets.replace("MANUSCRIPT", "PHYSICAL")
                                    mets = mets.replace('<ns3:div ID="PAGE_1" ORDER="1" TYPE="SINGLE_PAGE">', '<ns3:div ID="PAGE_1" ORDER="1" TYPE="PAGE">')
                                    with open(os.path.join(unzipped_folder, "mets.xml"), "w") as mets_file:
                                        mets_file.write(mets)

                        except Exception as e:
                            print("ERROR")
                            print(f'{e}')
                            print("END ERROR")
                            errors_edit_mets += 1

                else :
                    print (f'job {resp["jobId"]} is {resp["state"]}. Please try again later')
                    errors_download += 1
            except Exception as e:
                print("ERROR")
                print(f'{e}')
                print("END ERROR")
                errors_download += 1

    print(f'Done. downloaded: {downloaded}. skipped: {skipped}. errors download: {errors_download}. errors edit: {errors_edit_mets}')


if __name__ == '__main__':
    main()