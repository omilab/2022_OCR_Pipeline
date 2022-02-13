import logging
import os, shutil
from pathlib import Path

from tqdm import tqdm
from TkbsDocument import Document
import glob

from utilities import setup_logging, setup_parser


def find_sub_folders_with_toc_file(dir_path):  # Get absolute path
    sub_folders_with_TOC_file = []
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            if file == "TOC.xml":
                sub_folders_with_TOC_file.append(subdir)
    return sub_folders_with_TOC_file


def create_unique_output_folder(dir_path):
    #start_time = str(datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S"))
    output_path = os.path.join(dir_path, "legacy_output")
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    return output_path


def create_sub_folders_in_output_folder(folders_to_be_converted, inpath, outpath):
    output_sub_folders = []
    for folder in folders_to_be_converted:
        to_create = folder.replace(inpath, outpath)
        if os.path.isdir(to_create):
            shutil.rmtree(to_create)
        path = Path(to_create)
        path.mkdir(parents=True)
        output_sub_folders.append(to_create)
    return output_sub_folders


def convert_legacy_folder_to_tkbs_format(src_path, dst_path):
    try:
        p = Document()
        p.load_legacy_data(src_path)
        p.export_tkbs_format(dst_path)
    except Exception as e:
        print("ERROR in convert_legacy_folder_to_tkbs_format with src_path " + src_path)
        print(e)


def main():
    parser = setup_parser()
    args = parser.parse_args()
    setup_logging(args)

    path = args.base

    print(f"Converting from Olive to TKSB in {path}")
    logging.info(f"Converting from Olive to TKSB in {path}")
    skipped = converted = failed = 0

    toc_files = glob.glob(path + "/**/TOC.xml", recursive = True)
    for file_path in tqdm(toc_files):
        file_dir = os.path.dirname(file_path)
        logging.debug(f"Procesing {file_dir}")
        output_dir = os.path.join(file_dir, "legacy_output")

        if os.path.isdir(output_dir):
            if not args.overwrite:
                logging.info(f'Skipping {output_dir}')
                skipped += 1
                continue
            else:
                shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        folders_to_be_converted = find_sub_folders_with_toc_file(file_dir)
        output_sub_folders = create_sub_folders_in_output_folder(folders_to_be_converted, file_dir, output_dir)

        for f in range(len(folders_to_be_converted)):  # The routine that take source folder and convert files into destination file
            try:
                convert_legacy_folder_to_tkbs_format(folders_to_be_converted[f], output_sub_folders[f])
                converted += 1
            except Exception as e:
                logging.exception(f"Can't convert from {folders_to_be_converted[f]} to {output_sub_folders[f]}", e)
                failed += 1
    print(f'{converted} subfolders converted, {failed} subfolders with errors, {skipped} folders skipped')

if __name__ == '__main__':
    main()
