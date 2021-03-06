import os, shutil
from pathlib import Path
from TkbsDocument import Document
import glob


def get_path_from_user():
    user_input = input("Enter the path of your files (or press Enter for current folder): ")
    if user_input.strip() == "":  # Check for empty string
        return os.path.dirname(__file__)
    if os.path.isabs(user_input):  # Check if the input is absolute path or relative
        dir_name = user_input
    else:
        work_dir = os.path.dirname(__file__)
        dir_name = os.path.join(work_dir, user_input)
    if os.path.isdir(dir_name):
        return dir_name
    else:
        print("Illegal path, try again")
        return ""

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
        path = get_path_from_user()

        text_files = glob.glob(path + "/**/TOC.xml", recursive = True)
        print (text_files)
        str1 = "TOC.xml"
        for path in text_files:
            path = path.replace(str1,'')
            print(path)
		    #while path == "":
			#path = get_path_from_user()

            output_dir = create_unique_output_folder(path)

            folders_to_be_converted = find_sub_folders_with_toc_file(path)
            output_sub_folders =                                       create_sub_folders_in_output_folder(folders_to_be_converted, path, output_dir)

            for f in range(len(
    folders_to_be_converted)):  # The routine that take source folder and convert files into destination file
                        try:
                            convert_legacy_folder_to_tkbs_format(folders_to_be_converted[f], output_sub_folders[f])
                        except Exception as e:
                            print("ERROR in main loop")
                            print (e)
                            print ("END ERROR \n\n")
                            continue



            print("{} files converted successfully from legacy format to Transkribus format.\n"
      " You can find them now in {}'.".format(len(folders_to_be_converted), output_dir))


if __name__ == '__main__':
    main()
