import json
import os
import xml.etree.cElementTree as ET
import datetime
import glob
from TkbsDocument import Document
import glob

class Config:
    def __init__(self, path):
                           self.src_path =  path
                           self.export_tei = True
                           self.export_plaintext = True
                           self.export_csv = True
                           print("1")


def set_export(exformat):
    result = input("Press Enter to create " + exformat + " files, or type NO to skip: ")
    try:
        if result != None and str(result).upper == "NO":
            return False
    except:
        return True
    return True


def set_source_path():
    user_input = input("Enter the source path of your files (or press Enter for current folder): ")
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
        return set_source_path()


def set_destination_path():
    user_input = input("Enter the destination path of your files (or press Enter if you don't want to download): ")
    if user_input.strip() == "":  # Check for empty string
        return ""
    if os.path.isabs(user_input):  # Check if the input is absolute path or relative
        dir_name = user_input
    else:
        work_dir = os.path.dirname(__file__)
        dir_name = os.path.join(work_dir, user_input)
    if os.path.isdir(dir_name):
        return dir_name
    else:
        print("Illegal path, try again")
        return set_destination_path




def read_tkbs_json_file(trp_json_path):
    with open(trp_json_path) as f:
        data = json.load(f)
        # print(data)
        return data


def create_json_for_request(document_id, page_ids):
    d = {"docId": int(document_id), "pageList": {"pages": [{"pageId": pid} for pid in page_ids.values()]}}
    json_string = json.dumps(d)
    return json_string


def find_sub_folders_with_toc_file(dir_path):  # Get absolute path
    sub_folders_with_TOC_file = []
    for subdir, dirs, files in os.walk(dir_path):
        for file in files:
            if file == "TOC.xml":
                sub_folders_with_TOC_file.append(subdir)
    return sub_folders_with_TOC_file


def extract_title_from_TOC_xml(TOC_path):
    tree = ET.parse(TOC_path)
    root = tree.getroot()
    source = {}
    for s in root.iter('Link'):
        source = s.attrib
    if source == {}:
        title = "unknown title"
    else:
        title = (source["SOURCE"])[:-4]
    return title


#check if dir exists, creates it if not
def prep_dir(out_dir):
    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        return(out_dir)
    except Exception as e:
        print("ERROR in prep_dir " + out_dir)
        print (e)
        print ("END ERROR \n\n")
        raise e

def find_latest_folder(topfolder, start_pattern):
    try:
        found_folders = glob.glob(os.path.join(topfolder, start_pattern) + '*')
        return max(found_folders, key=os.path.getctime)
    except Exception as e:
        print("ERROR in find_latest_folder " + topfolder + start_pattern)
        print (e)
        print ("END ERROR \n\n")
        raise e

v = False
def export_pipeline(config):
    folders_to_be_exported = find_sub_folders_with_toc_file(config.src_path)
    tkbs_topfolder = os.path.join(config.src_path, "transkribus_output")
    exportfolder = prep_dir(os.path.join(config.src_path, "transkribus_export"))
    if config.export_csv:
        csvfolder_byregion = prep_dir(os.path.join(exportfolder, 'csv_by_region'))
        csvfolder_byarticle = prep_dir(os.path.join(exportfolder, 'csv_by_article'))
    if config.export_plaintext:
        plaintextfolder = prep_dir(os.path.join(exportfolder, 'plaintext'))
        plaintextfolder_byarticle = prep_dir(os.path.join(exportfolder, 'plaintext_by_article'))
    if config.export_tei:
        teifolder = prep_dir(os.path.join(exportfolder, 'tei'))
    for sfolder in folders_to_be_exported:
        try:
            if not os.path.isfile(os.path.join(sfolder, 'TOC.xml')):
                continue
            infolder = sfolder

            start = str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M"))
            print(start + " - " + infolder)# + "\n==============")
            v and print("---   LOADING Legacy data ---")
            p = Document()
            p.load_legacy_data(infolder)
            tkbsfolder = find_latest_folder(tkbs_topfolder, p.doc_title)
            p.load_tkbs_data(tkbsfolder) #FIX
            p.load_legacy_articles(p.legacy_metafile)
            p.match_legacy_articles()

            if config.export_tei:
                v and print("---   TEI export           ---")
                p.export_tei(teifolder)

            if config.export_plaintext:
                v and print("---   PLAINTEXT export     ---")
                p.export_plaintext(plaintextfolder)
                values = config.src_path.split("/")
                #p.export_plaintext_articles("/home/aor7/work/historical_press/OCR_Pipeline/hamagid-1885-1900/outputs/" + values[7] + "/" + values[8] + "/" + values[9] + "/")
                p.export_plaintext_articles(plaintextfolder_byarticle)

            if config.export_csv:
                v and print("---   CSV export           ---")
                p.export_csv_articles(csvfolder_byarticle)
                p.export_csv_regions(csvfolder_byregion)


        except Exception as e:
            print("ERROR in export_pipeline main loop ")
            print (e)
            print ("END ERROR \n\n")
            pass


    print("DONE. Output is under " + exportfolder)

def main():
    path = set_source_path()
    text_files = glob.glob(path + "/**/TOC.xml", recursive = True)
    print (text_files)
    str1 = "TOC.xml"
    for path in text_files:
        path = path.replace(str1,'')
        if len(os.listdir(path+ "transkribus_output/") ) != 0:
           config = Config(path)
           print("1")
           export_pipeline(config)


if __name__ == '__main__':
    main()
