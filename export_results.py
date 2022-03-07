# Export the Transkribus results

import logging
import os
import shutil
from typing import Any

from tqdm import tqdm
from TkbsDocument import Document

from utilities import gather_document_folders, setup_logging, setup_parser


def get_args() -> Any:
    parser = setup_parser()
    parser.add_argument('--output-dir', default=None, type=str, help='Output directory, if not specified, output is written to the transkribus_output folder of each input directory')
    parser.add_argument('--format', nargs='*', default='txt', choices=['csv', 'tei', 'txt'], help='Export formats')
    args = parser.parse_args()

    return args

def export(input_folder: str, output_folder: str, formats: list[str]):
    def prep_dir(dir):
        os.makedirs(dir, exist_ok=True)
        return dir

    logging.info(f'Exporting {input_folder} to {output_folder}')

    tkbs_folder = os.path.join(input_folder, 'transkribus_output')
    if not os.path.exists(tkbs_folder):
        raise ValueError(f"Can't export {input_folder} - no transkribus_output found")

    p = Document()
    p.load_legacy_data(input_folder)
    p.load_tkbs_data(tkbs_folder) #FIX
    p.load_legacy_articles(p.legacy_metafile)
    p.match_legacy_articles()

    if 'tei' in formats:
        teifolder = prep_dir(os.path.join(output_folder, 'tei'))
        p.export_tei(teifolder)

    if 'txt' in formats:
        plaintextfolder = prep_dir(os.path.join(output_folder, 'plaintext'))
        p.export_plaintext(plaintextfolder)
        plaintextfolder_byarticle = prep_dir(os.path.join(output_folder, 'plaintext_by_article'))
        p.export_plaintext_articles(plaintextfolder_byarticle)

    if 'csv' in formats:
        csvfolder_byregion = prep_dir(os.path.join(output_folder, 'csv_by_region'))
        p.export_csv_regions(csvfolder_byregion)
        csvfolder_byarticle = prep_dir(os.path.join(output_folder, 'csv_by_article'))
        p.export_csv_articles(csvfolder_byarticle)

def get_output_folder(base_folder: str, input_folder: str, output_folder_prefix: str):
    if not output_folder_prefix:
        return os.path.join(input_folder, 'transkribus_export')

    # Getting the output folder is a little tricky - take the input_folder, remove the base_folder parts from it,
    # and append them to the output_folder_prefix.
    #
    base_folder_parts = os.path.normpath(base_folder).split(os.sep)
    input_folder_parts = os.path.normpath(input_folder).split(os.sep)
    output_folder_prefix = os.path.normpath(output_folder_prefix)

    relevant_input_parts = input_folder_parts[len(base_folder_parts):]
    output_folder = os.path.join(output_folder_prefix, *relevant_input_parts)
    return output_folder

def main():
    args = get_args()
    setup_logging(args)

    print(f'Exporting Transkribus results to ' + args.output_dir if args.output_dir else './transkribus_export')
    logging.info(f'Exporting Transkribus results to ' + args.output_dir if args.output_dir else './transkribus_export')

    exported = skipped = 0
    folders = list(gather_document_folders(args.base))

    base_dir_parts = os.path.normpath(args.base).split(os.sep)
    for input_folder in tqdm(folders):
        output_folder = get_output_folder(args.base, input_folder, args.output_dir)

        if os.path.exists(output_folder):
            if args.overwrite:
                logging.debug(f'Overwrriting output in {output_folder}')
                shutil.rmtree(output_folder)
            else:
                logging.debug(f'Skipping {output_folder}')
                skipped += 1
                continue

        os.makedirs(output_folder)
        export(input_folder, output_folder, args.format)
        exported += 1 

    print(f'Exported {exported}, skipped {skipped}')
    logging.info(f'Exported {exported}, skipped {skipped}')

if __name__ == '__main__':
    main()
