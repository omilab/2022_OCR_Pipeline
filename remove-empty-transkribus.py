from glob import glob
import os
import shutil
from tqdm import tqdm
import logging
from utilities import setup_parser, setup_logging
import xml.etree.ElementTree as ET


def does_text_exists(tkbs_folder):
    for filename in os.listdir(tkbs_folder):
        if filename.endswith(".xml") or filename.endswith(".pxml"):
            tree = ET.ElementTree(file=os.path.join(tkbs_folder,filename))
            for myelement in tree.iterfind('*/*/*'):
                if myelement.tag.endswith("TextLine"):
                   
                    for mychild in myelement.iter():
                        if mychild.tag.endswith("TextEquiv"):
                            for txt in mychild.iter():
                                if myelement.tag.strip != '':
                                    logging.debug(f"File {filename} has text in it")
                                    return True
                    
    return False

def main():
    parser = setup_parser()
    parser.add_argument('--dry', action='store_true', default=False, help='Dry run - do not make any actual changes')
    args = parser.parse_args()
    setup_logging(args)

    logging.info(f'Remove empty transkribus folders from {args.base}') # todo - add logs
    print(f"Remove empty transkribus folders from {args.base}")
    folders = glob(os.path.join(args.base, '**', 'transkribus_output'), recursive=True)
    deleted = kept = 0
    for tkbs_folder in tqdm(folders):
        logging.info(f"Check if text exist in {tkbs_folder}")

        if does_text_exists(tkbs_folder):
            kept += 1
            logging.debug(f"Not deleting ${tkbs_folder}, it has text")
           
        else:
             # delete transkribus_output folder

            deleted += 1
            if not args.dry_run:
                logging.debug(f"Deleting transkribus_output folder ${tkbs_folder}")
                shutil.rmtree(tkbs_folder)
            else:
                logging.debug(f'Dry run - should have deleted folder ${tkbs_folder}')
            
    print(f'Deleted {deleted} folders, kept {kept} folders')

if __name__ == '__main__':
    main()
