# This is the first stage of the pipeline - unzip the Olive Document.zip files inplace

import argparse
from glob import glob
import os
import shutil
from typing import Any
import zipfile
from os.path import exists
from tqdm import tqdm
import logging
from utilities import setup_parser, setup_logging

flags = os.O_CREAT | os.O_RDWR | 0x8000 | 0x400000


# Unzip the files in `zip`. 
# We do not use ZipFile.extract_all because the zip files are a bit messy - directories are also stored as 0-length files, which
# causes the standard Python unzipping process to fail (it tries to create a file with the name of an existing directory)
#
# The solution is to find those messy zip file entries, and not extract them in the first place.
#
# Easiest way to find these extra files is by looking at their external attribute = 0x10 means a directory
def unzip(zip, dest):
    with zipfile.ZipFile(zip, 'r') as zf:
        all_files = zf.filelist
        proper_files = [f for f in zf.filelist if f.external_attr != 0x10]
        zf.extractall(dest, [f.filename for f in proper_files])

def main():
    parser = setup_parser()
    args = parser.parse_args()
    setup_logging(args)

    logging.info(f'Unzipping all Document.zip files from {args.base}')
    print(f"Unzipping all Document.zip files from {args.base}")
    document_zips = glob(os.path.join(args.base, '**', 'Document.zip'), recursive=True)
    skipped = unzipped = 0
    for zip_path in tqdm(document_zips):
        folder_path = os.path.join(os.path.dirname(zip_path), 'Document')

        if os.path.isdir(folder_path):
            if not args.overwrite:
                logging.info(f"Skipping ${folder_path}, it already exists")
                skipped += 1
                continue
            else:
                logging.debug(f"Removing existing folder ${folder_path}")
                shutil.rmtree(folder_path)

        logging.info(f"Unzipping from {zip_path} to {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        unzip(zip_path, folder_path)
        unzipped += 1

    print(f'Unziped {unzipped} files, skipped {skipped} folders')

if __name__ == '__main__':
    main()
