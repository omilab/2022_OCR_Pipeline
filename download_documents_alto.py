import json
import logging
import shutil
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
from pdfrw import PdfReader, PdfWriter

def get_args():
    parser = setup_parser()
    add_transkribus_args(parser)
    args = parser.parse_args()

    return args

def lines_in_doc(doc: dict):
    return doc['md']['nrOfLines'] > 0

def unzip_folder(zip_path: str, folder: str, job_id: int):
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

def create_folders_tree(second_level_file: str, args) -> str:
    strings = second_level_file.split("-")
    pub_code = strings[1]
    if not os.path.exists(os.path.join(args.base, pub_code)):
        os.mkdir(os.path.join(args.base,pub_code))   
    if not os.path.exists(os.path.join(args.base, pub_code, strings[2])):
        os.mkdir(os.path.join(args.base,pub_code, strings[2]))    
    if not os.path.exists(os.path.join(args.base, pub_code, strings[2], strings[3])):
        os.mkdir(os.path.join(args.base, pub_code, strings[2], strings[3]))       
    issue_date = strings[2] + "/" + strings[3] + "/" + strings[4] + "_01"
    dest_folder = os.path.join(args.base, pub_code, issue_date)
    if not os.path.exists(dest_folder):       
        os.mkdir(dest_folder)
        os.mkdir(os.path.join(dest_folder, "ALTO"))
        os.mkdir(os.path.join(dest_folder, "PAGEPDF"))

    return dest_folder

def build_files_and_folders_hirrechy(zip_path: str, args) -> str:
    dest_folder = ''
    root_path = zip_path.replace(".zip","")
    for first_level_file in os.listdir(root_path):
        if ".txt" not in first_level_file:
            sub_path = os.path.join(root_path,first_level_file)
            for second_level_file in os.listdir(sub_path):
                dest_folder = create_folders_tree(second_level_file, args)
                if ".pdf" not in second_level_file:
                    second_level_file_full_path = os.path.join(sub_path, second_level_file)
                    for third_level_file in os.listdir(second_level_file_full_path):
                        if third_level_file == "alto":
                            third_level_file_full_path = os.path.join(second_level_file_full_path, third_level_file)
                            for alto_file in os.listdir(third_level_file_full_path):
                                shutil.copy(os.path.join(third_level_file_full_path, alto_file), os.path.join(dest_folder, "ALTO", alto_file))
                else:          
                    extract_pdf_to_single_pages(second_level_file, sub_path, dest_folder)
                    shutil.move(os.path.join(sub_path,second_level_file), os.path.join(dest_folder, second_level_file))

    return dest_folder

def extract_pdf_to_single_pages(pdf_file_name: str, sub_path: str, dest_folder: str):
    pages = PdfReader(os.path.join(sub_path , pdf_file_name)).pages
    i = 0
    for page in pages:
        single_page_pdf_name = calc_page_number(i)
        outdata = PdfWriter(os.path.join(dest_folder, "PAGEPDF" ,single_page_pdf_name))
        outdata.addpage(pages[i])
        outdata.write()
        i += 1

def calc_page_number(index: int) -> str:
    if index >= 9 :
        return f'000{index+1}.pdf'
    else:
        return f'0000{index+1}.pdf'


def edit_and_rename_alto_files(path: str):
    alto_files_path = os.path.join(path,"ALTO")
    for alto_file_path in os.listdir(alto_files_path):
        new_file_name = rename_file(alto_files_path, alto_file_path)
        edit_file(alto_files_path, new_file_name)

def edit_file(folder: str, file_name: str):
    page_number = int(file_name.replace('.xml',''))
    with open(os.path.join(folder, file_name), "r+", encoding="utf8") as alto_file:
        alto = alto_file.read()
    alto = alto.replace('TextBlock ID="', f'TextBlock ID="P{page_number}_')
    with open(os.path.join(folder, file_name), "w", encoding="utf8") as alto_file:
        alto_file.write(alto)


def rename_file(folder: str, file_name: str) -> str:
    page_number = file_name[2:5]
    page_number = "00" + page_number
    new_file_path = os.path.join(folder,f'{page_number}.xml')
    os.rename(
        os.path.join(folder,file_name), 
        new_file_path
        )
    return f'{page_number}.xml'

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

def remove_folder(path: str, destination_folder: str):
    os.remove(path)
    extracted_folder_path = path.replace(".zip","")
    for folder in os.listdir(extracted_folder_path):
        alto_path = os.path.join(extracted_folder_path, folder)
        if os.path.isdir(alto_path):
            shutil.move(alto_path, destination_folder)

    shutil.rmtree(extracted_folder_path)

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
                        new_root_path = build_files_and_folders_hirrechy(zip_path, args)
                        edit_and_rename_alto_files(new_root_path)

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