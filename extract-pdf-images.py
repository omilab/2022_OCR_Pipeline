# Extract the highest resolution image from the PDF file, instead of using the lower resolution images in the Document.zip file

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
import fitz

def extract_images(pdf_file, image_path):
    pdf = fitz.open(pdf_file)
    for i in range(len(pdf)):
        pdf_page = pdf[i]
        images = pdf_page.get_images()
        if len(images) != 1:
            raise ValueError("Expected exactly one image per page")
        img_data = images[0]

        img = pdf.extract_image(img_data[0])
        img_file = os.path.join(image_path, f'FullPg{i+1:02}.{img["ext"]}')
        with open(img_file, "wb") as fout:
            fout.write(img['image'])


def main():
    parser = setup_parser()
    args = parser.parse_args()
    setup_logging(args)

    logging.info(f'Extracting all images from PDFs in {args.base}')
    print('Extracting all images from PDFs in {args.base}')
    pdf_files = glob(os.path.join(args.base, '**', '*.pdf'), recursive=True)
    skipped = extracted = 0
    for pdf_file in tqdm(pdf_files):
        folder_path = os.path.join(os.path.dirname(pdf_file), 'pdf-images')

        if os.path.isdir(folder_path):
            if not args.overwrite:
                logging.info(f"Skipping ${folder_path}, it already exists")
                skipped += 1
                continue
            else:
                logging.debug(f"Removing existing folder ${folder_path}")
                shutil.rmtree(folder_path)

        logging.info(f"Extracting images from {pdf_file} to {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        extract_images(pdf_file, folder_path)
        extracted += 1

    print(f'Extracted images from {extracted} PDF files, skipped {skipped} files')

if __name__ == '__main__':
    main()
