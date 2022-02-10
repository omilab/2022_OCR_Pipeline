# This is the first stage of the pipeline - unzip the Olive Document.zip files inplace

import argparse
import os
from typing import Any
import zipfile
from os.path import exists
from utilities import enumerate_folders

flags = os.O_CREAT | os.O_RDWR | 0x8000 | 0x400000

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('base', type=str, help='Name of folder with all the newspaper files')

    return parser.parse_args()

def main():
    args: Any = parse_args()
    print('Unzipping all Document.zip files start at ', args.base)

    for folder in enumerate_folders(args.base):
        full_folder = os.path.join(args.base, folder)
        pathinput = os.path.join(full_folder, 'Document.zip')
        if not os.path.exists(pathinput):
            continue
        pathoutput = os.path.join(full_folder, 'Document')
        os.makedirs(pathoutput, exist_ok=True)
        print(f'{pathinput} --> {pathoutput}')
        with zipfile.ZipFile(pathinput, 'r') as zf:
            for file in zf.filelist:
                try:
                    name = file.filename
                    perm = ((file.external_attr >> 16) & 0o777)
                    print("Extracting: " + name)
                    if len(name.split("/")[-1].split(".")) == 1:  # Check if the file has an extension
                        dirname = os.path.join(pathoutput, name)
                        if not os.path.isdir(dirname):
                            os.mkdir(os.path.join(pathoutput, name), perm) # Create a subdirectory
                    else:
                        outfile = os.path.join(pathoutput, name)
                        fh = os.open(outfile,  flags, perm)
                        os.write(fh, zf.read(name))
                        os.close(fh)
                except Exception as e:
                    #print("222222222222222222222")
                    name = file.filename
                    perm = ((file.external_attr >> 16) & 0o777)
                    outfile = pathoutput
                    for i in range (len(name.split("/"))-1):
                        outfile = os.path.join(outfile, name.split("/")[i])
                    #print("00000000000")
                    print(outfile)
                    if  exists(outfile) == False:
                        os.mkdir(outfile, perm)
                    print("Extracting: " + name)
                    outfile = os.path.join(pathoutput, name)

                    fh = os.open(outfile, flags , perm)
                    os.write(fh, zf.read(name))
                    os.close(fh)

if __name__ == '__main__':
    main()
