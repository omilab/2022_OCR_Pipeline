# This is the first stage of the pipeline - unzip the Olive Document.zip files inplace

import os
import zipfile
from os.path import exists

flags = os.O_CREAT | os.O_RDWR | 0x8000 | 0x400000



for newespaper in os.listdir("E://JPRESS_NLI_December2019//" ):
    for year in os.listdir("E://JPRESS_NLI_December2019//"  + newespaper):
               for month in os.listdir("E://JPRESS_NLI_December2019//"  + newespaper + "//" + year):
                   for day in os.listdir("E://JPRESS_NLI_December2019//" 					+ newespaper+ "//" + year +"//" + month):
                        path = "E://JPRESS_NLI_December2019//" 					 + newespaper + "//" + year +"//" + month +"//" +day
                        pathinput = os.path.abspath(path + "//" + "Document.zip")
                        os.makedirs(path + "//" + "Document")
                        pathoutput = os.path.abspath(path + "//" + "Document")
                        print(pathoutput)
                        with zipfile.ZipFile(pathinput, 'r') as zf:
                              for file in zf.filelist:
                                try:
                                    name = file.filename
                                    perm = ((file.external_attr >> 16) & 0o777)
                                    print("Extracting: " + name)
                                    if len(name.split("/")[-1].split(".")) == 1:
                                    #print("yes")
                                        os.mkdir(os.path.join(pathoutput, name), perm)
                                    else:
                                        outfile = os.path.join(pathoutput, name)
                                        fh = os.open(outfile,  flags, perm)
                                        os.write(fh, zf.read(name))
                                        os.close(fh)
                                except:
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
