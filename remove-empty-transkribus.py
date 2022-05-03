from glob import glob
import os
import shutil
from tqdm import tqdm
import logging
from utilities import setup_parser, setup_logging
import xml.etree.ElementTree as ET


def is_text_exists(tkbs_folder):
    for filename in os.listdir(tkbs_folder):
        if filename.endswith(".xml") or filename.endswith(".pxml"):
            
            tree = ET.parse(os.path.join(tkbs_folder,filename))
            root = tree.getroot()

            data_string = ET.tostring(root, encoding="unicode", method="html")
            print(data_string)

            if 'TextEquiv' in data_string:
                # check if it contains something
                return True
           
    return False

def main():
    parser = setup_parser()
    args = parser.parse_args()
    setup_logging(args)

    logging.info(f'Remove empty transkribus folders from {args.base}') # todo - add logs
    print(f"Remove empty transkribus folders from {args.base}")
    folders = glob(os.path.join(args.base, '**', 'transkribus_output'), recursive=True)
    deleted = undeleted = 0
    for tkbs_folder in tqdm(folders):
        logging.info(f"Check if text exist in {tkbs_folder}")

        if is_text_exists(tkbs_folder):
            undeleted += 1
            logging.debug(f"Undeleted ${tkbs_folder}, it has text")
           
        else:
             # delete transkribus_output folder
            logging.debug(f"Deleting transkribus_output folder ${tkbs_folder}")

            deleted += 1
            shutil.rmtree(tkbs_folder)
            
    print(f'Deleted {deleted} folders, undeleted {undeleted} folders')

if __name__ == '__main__':
    main()
