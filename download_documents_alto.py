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

    downloaded = 0
    skipped = 0
    errors = 0

    for folder in tqdm(folders):
        job_indication_file = os.path.join(folder, 'job-status-export-alto.json')
        if os.path.exists(job_indication_file):
            try:
                f = open(job_indication_file)
                data = json.load(f)
                job_id = data["job"]

                if os.path.exists(f'{folder}/export_document_{job_id}.zip'):
                    skipped += 1
                    continue

                print(f'export job_id {job_id}')
                resp = tkbs.getJobStatus(job_id)
                if resp['state'] == 'FINISHED':
                    with open(f'{folder}/export_document_{job_id}.zip', 'wb') as out_file:
                        content = requests.get(resp['result'], stream=True).content
                        out_file.write(content)
                        downloaded += 1
                else :
                    print (f'job {resp["jobId"]} is {resp["state"]}. Please try again later')
                    errors += 1
            except Exception as e:
                print("ERROR")
                print(f'{e}')
                print("END ERROR")
                errors += 1

    print(f'Done. downloaded: {downloaded}. skipped: {skipped}. errors: {errors}')


if __name__ == '__main__':
    main()