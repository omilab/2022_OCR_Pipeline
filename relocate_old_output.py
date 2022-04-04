# This script relocates old transkribus_output files, generated by the old Nurit pipeline,
# and places them as if they were downloaded.
import glob
import logging
import os
import shutil

from tqdm import tqdm
from utilities import setup_parser, setup_logging

def find_dest_folder(folder: str, base_dir: str):
    folder = os.path.basename(os.path.normpath(folder))

    # Format is PPP-YYYY-MM-DD_extra stuff
    # P is prefix.
    # We don't even need a regex, we'll just extract the year, month and day and look for the corresponding directory under base_dir
    year = folder[4:8]
    month = folder[9:11]
    day = folder[12:14]

    daily_folder = os.path.join(base_dir, year, month, day)
    if not os.path.exists(daily_folder):
        raise ValueError(f"Can't locate folder {daily_folder} for output folder {folder}")

    return os.path.join(daily_folder, 'transkribus_output')

def main():
    parser = setup_parser()
    parser.add_argument('--old-output-dir', type=str, help='Location of old output dir')
    parser.add_argument('--newspaper-prefix', type=str, help='Prefix of newspaper to relocate')
    args = parser.parse_args()
    setup_logging(args)

    print(f'Relocating old output from {args.old_output_dir} {args.newspaper_prefix}* to {args.base}')
    logging.info(f'Relocating old output from {args.old_output_dir} {args.newspaper_prefix}* to {args.base}')

    old_folders = glob.glob(os.path.join(args.old_output_dir, args.newspaper_prefix + '*'), recursive=True)
    relocated = skipped = error = 0
    for old_folder in tqdm(old_folders):
        if not os.path.isdir(old_folder):
            logging.debug(f'{old_folder} is not a directory, ignoring')
            continue

        try:
            dest_folder = find_dest_folder(old_folder, args.base)
        except ValueError:
            logging.exception("Can't figure out destination folder of " + old_folder)
            error += 1
            continue

        if os.path.isdir(dest_folder):
            if not args.overwrite:
                logging.debug(f"Skipping folder {dest_folder}, it already exists")
                skipped += 1
                continue
            shutil.rmtree(dest_folder)

        os.makedirs(dest_folder)
        tkbs_files = glob.glob(os.path.join(old_folder, '*'))
        for file in tkbs_files:
            logging.debug(f'Copying {file} to {dest_folder}')
            shutil.copy(file, dest_folder)
        relocated += 1

    print(f"Done, relocated {relocated}, error {error}, skipped {skipped}")


if __name__ == '__main__':
    main()