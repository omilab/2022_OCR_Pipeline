import json
import logging
import glob, os
from typing import Any
from xml.etree import ElementTree
import requests

from tqdm import tqdm
from TkbsDocument import Document
from utilities import add_transkribus_args, find_existing, gather_document_folders, init_tkbs_connection, load_document, save_job_indication, setup_logging, setup_parser

from TranskribusPyClient import TranskribusClient

import zipfile
import xml.etree.ElementTree as ET

from PIL import Image

def get_args():
    parser = setup_parser()
    add_transkribus_args(parser)
    args = parser.parse_args()

    return args

def lines_in_doc(doc: dict):
    return doc['md']['nrOfLines'] > 0

def unzip_folder(zip_path: str, folder: str, job_id: int):
    print(zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        outpath = f'{folder}\\export_document_{job_id}'
        zip_ref.extractall(outpath)

def edit_mets(args):
    unzipped_folders = list(gather_document_folders(args.base, f'mets.xml'))
    for unzipped_folder in unzipped_folders:
        with open(os.path.join(unzipped_folder, "mets.xml"), "r+") as mets_file:
            mets = mets_file.read()
        mets = mets.replace("MANUSCRIPT", "PHYSICAL")
        mets = mets.replace('<ns3:div ID="PAGE_1" ORDER="1" TYPE="SINGLE_PAGE">', '<ns3:div ID="PAGE_1" ORDER="1" TYPE="PAGE">')
        with open(os.path.join(unzipped_folder, "mets.xml"), "w") as mets_file:
            mets_file.write(mets)

def rename_folders(zip_path: str):
    root_path = zip_path.replace(".zip","")
    for first_level_file in os.listdir(root_path):
        if ".txt" not in first_level_file:
            sub_path = os.path.join(root_path,first_level_file)
            for second_level_file in os.listdir(sub_path):
                strings = second_level_file.split("-")
                pub_code = strings[1]
                issue_date = strings[2] + strings[3] + strings[4] + "_01"
                os.rename(sub_path, os.path.join(root_path,issue_date))
                os.rename(
                    os.path.join(root_path,issue_date,second_level_file),
                    os.path.join(root_path,issue_date,pub_code)
                )



def write_error(e: Exception):
    print("ERROR")
    print(f'{e}')
    print("END ERROR")

def download(zip_path, resp) -> int:
    with open(zip_path, 'wb') as out_file:
        content = requests.get(resp['result'], stream=True).content
        out_file.write(content)
    return 1

def get_job_id(job_indication_file):
    f = open(job_indication_file)
    data = json.load(f)
    job_id = data["job"]
    return job_id

def convert_to_jpg(args):
    unzipped_folders = list(gather_document_folders(args.base, f'mets.xml'))
    for folder in unzipped_folders:
        for file in os.listdir(folder):
            if file.endswith(".png"):
                im = Image.open(os.path.join(folder,file))
                rgb_im = im.convert('RGB')
                rgb_im.save(os.path.join(folder, file.replace('png','jpg')))
                os. remove(os.path.join(folder,file))

def main():

    print('Running download alto started')
    logging.debug('Running download alto started')

    args = get_args()
    setup_logging(args)

    tkbs = TranskribusClient(sServerUrl=args.tkbs_server)
    tkbs.auth_login(args.tkbs_user, args.tkbs_password, True)

    print(f'Running download alto documents from Trankribus collection {args.tkbs_collection_id}')
    logging.info(f'Running download alto on all documents from Trankribus collection {args.tkbs_collection_id}')

    downloaded = skipped = errors_download = errors_edit_mets = 0

    folders = list(gather_document_folders(args.base))
    for folder in tqdm(folders):
        job_indication_file = os.path.join(folder, 'job-status-export-alto.json')
        if os.path.exists(job_indication_file):
            try:
                job_id = get_job_id(job_indication_file)

                if os.path.exists(f'{folder}\\export_document_{job_id}.zip'):
                    skipped += 1
                    continue

                resp = tkbs.getJobStatus(job_id)
                if resp['state'] == 'FINISHED':
                    zip_path = f'{folder}\\export_document_{job_id}.zip'
                    downloaded += download(zip_path, resp)

                    try:
                        unzip_folder(zip_path, folder, job_id)
                        convert_to_jpg(args)
                        edit_mets(args)
                        rename_folders(zip_path)

                    except Exception as e:
                        write_error(e)
                        errors_edit_mets += 1

                else :
                    print (f'job {resp["jobId"]} is {resp["state"]}. Please try again later')
                    errors_download += 1
            except Exception as e:
                write_error(e)
                errors_download += 1

    print(f'Done. downloaded: {downloaded}. skipped: {skipped}. errors download: {errors_download}. errors edit: {errors_edit_mets}')


if __name__ == '__main__':
    main()