# importing os module
import os

# importing shutil module
import shutil
import os, shutil, stat

def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir, mode)
        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)

def on_rm_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

for newespaper in os.listdir("E:/nurit_work buckup/data/pipeline/extrayears/" ):
    for year in os.listdir("E:/nurit_work buckup/data/pipeline/extrayears/"  + newespaper):
               for month in os.listdir("E:/nurit_work buckup/data/pipeline/extrayears/"  + newespaper + "/" + year):
                   for day in os.listdir("E:/nurit_work buckup/data/pipeline/extrayears/" 					+ newespaper+ "/" + year +"/" + month):
                       path = "E:/nurit_work buckup/data/pipeline/extrayears/" 					 + newespaper + "/" + year +"/" + month  + "/" + day + "/"

                       sourFir = path.split("/")
                       print(sourFir)
                       sourSec = '/'.join([sourFir[i] for i in [0, 1,2,3,4]])
                       sourSec += "/legacy_output/"
                       next = '/'.join([sourFir[i] for i in [5,6,7,8]])
                       #destSec = os.path.abspath(destSec)
                       source_path = sourSec + next
                       print(source_path)
                       # file_names = os.listdir(source_path)
                       #
                       #
                       dest = path + "/" + "legacy_output"
                       print(dest)
                       #
                       #
                       # #shutil.rmtree(dest, onerror=on_rm_error)
                       #
                       #
                       # change_permissions_recursive(dest,0o777)
                       # if not dest:
                       # # try:
                       # #      shutil.rmtree(dest)
                       # # except:
                       # #      print("1")
                       #      try:
                       #           print("remove")
                       #           shutil.rmtree(dest)
                       #      except:
                       #           print(2)
                       # else:
                       #     continue
                       os.mkdir(dest)

                       file_names = os.listdir(source_path)

                       for file_name in file_names:
                           shutil.move(os.path.join(source_path, file_name), dest)
