from ruamel import yaml
from time import sleep
import sys
import shutil
import os
import copy
import subprocess

try:
    docsPath = sys.argv[1]
except IndexError:
    print("Usage: export.py source_folder")
    exit()

if not os.path.exists(docsPath):
    raise FileNotFoundError("Sources folder not found.")

if not os.path.exists(docsPath + "/mkdocs.yml"):
    raise FileNotFoundError("MkDocs configuration file is missing.")

configPath = docsPath + "/mkdocs.yml"
softwarePath = docsPath+"/docs/daily-maintenance/software.md"
operationsPath = docsPath + "/docs/daily-maintenance/operations.md"
software_imgs = docsPath + "/docs/daily-maintenance/software/images"
operations_imgs = docsPath + "/docs/daily-maintenance/operations/images"

config = open(configPath,mode = 'r',encoding = 'utf-8')
loadedCfg = yaml.load(config,Loader = yaml.RoundTripLoader)
newCfg = copy.deepcopy(loadedCfg)
tmp_cfg = open(docsPath + "/tmp.yml",mode = 'w',encoding = 'utf-8')

if os.path.exists(docsPath + "/docs/processed"):
    print("Source documents have been processed, skipped processing.")

else:
    print("Merging documents...")
    software = open(softwarePath,mode ='w',encoding = 'utf-8')
    operations = open(operationsPath,mode = 'w',encoding = 'utf-8')
    for i in range(len(loadedCfg['nav'])):
        tmp = list(loadedCfg['nav'][i].values())[0]
        for j in range(len(tmp)):
            if type(list(tmp[j].values())[0]) == yaml.comments.CommentedSeq and str(list(tmp[j].keys())[0]) == "软件篇":
                for k in range(len(list(tmp[j].values())[0])):
                    path = docsPath + "/docs/" + str(list(list(tmp[j].values())[0][k].values())[0])
                    print(path,"has been merged into",softwarePath)
                    file = open(path,mode='r',encoding='utf-8')
                    software.write("# 软件篇\n")
                    software.write(file.read())
                    file.close()

            if type(list(tmp[j].values())[0]) == yaml.comments.CommentedSeq and str(list(tmp[j].keys())[0]) == "操作篇":
                for k in range(len(list(tmp[j].values())[0])):
                    path = docsPath + "/docs/" + str(list(list(tmp[j].values())[0][k].values())[0])
                    print(path,"has been merged into",operationsPath)
                    file = open(path,mode = 'r',encoding = 'utf-8')
                    operations.write("# 操作篇\n")
                    operations.write(file.read())
                    file.close()
    operations.close()
    software.close()

newCfg['nav'][1]['日常维护'][0]['软件篇'] = "daily-maintenance/software.md"
newCfg['nav'][1]['日常维护'][1]['操作篇'] = "daily-maintenance/operations.md"
newCfg['copyright'] = "本手册所有内容均在 CC BY-SA 4.0 和 SATA 协议条款下提供。"
newCfg['markdown_extensions'][7]['toc'] = {'permalink': 'true'}

try:
    del newCfg['edit_uri']
    del newCfg['repo_url']
    del newCfg['repo_name']
except KeyError:
    print("Some key-value pairs is missing. Maybe the configuration file has been modified?")

newCfg['plugins'] = [{'mkpdfs': {'design': os.getcwd() + '/mkpdfs-style/report.css', 'company': '赣州三中学生会', 'author': '秘书处', 'toc_title': '目录'}}]

yaml.dump(newCfg,tmp_cfg,Dumper=yaml.RoundTripDumper,default_flow_style=False,encoding='utf-8',allow_unicode=True)
config.close()
tmp_cfg.close()
try:
    os.remove(docsPath + "/docs/landing.md")
except FileNotFoundError:
    print("Landing page is missing, skipped.")
os.remove(configPath)
os.rename(docsPath + "/tmp.yml",configPath)
print("New mkdocs configuration generated.")

try:
    software_imgs_list=os.listdir(software_imgs)
    operations_imgs_list=os.listdir(operations_imgs)
    if not os.path.exists(docsPath + "/docs/daily-maintenance/images/"):
        os.mkdir(docsPath + "/docs/daily-maintenance/images/")
    for i in range(len(os.listdir(software_imgs))):
        path = os.path.join(software_imgs,software_imgs_list[i])
        src = os.path.join(docsPath + "/docs/daily-maintenance/software/images",software_imgs_list[i])
        dst = docsPath + "/docs/daily-maintenance/images/"
        shutil.move(src,dst)
    for i in range(len(os.listdir(operations_imgs))):
        path = os.path.join(operations_imgs,operations_imgs_list[i])
        src = os.path.join(docsPath + "/docs/daily-maintenance/operations/images",operations_imgs_list[i])
        dst = docsPath + "/docs/daily-maintenance/images/"
        shutil.move(src,dst)
    print("Images have been merged.\nCleaning up...")
except FileNotFoundError:
    print("Old images folders not found, skipped.")
try:
    shutil.rmtree(docsPath + "/docs/daily-maintenance/operations")
    shutil.rmtree(docsPath + "/docs/daily-maintenance/software")
except FileNotFoundError:
    print("Old documents folders not found, skipped.")
open(docsPath + "/docs/processed",mode='w')

print("Generating PDF...")
try:
    subprocess.check_call("cd " + docsPath + " && mkdocs build",shell=True)

except subprocess.CalledProcessError:
    print("Generation failed. Check the output above for more information.")

else:
    try:
        os.remove("./result.pdf")
    except FileNotFoundError:
        pass
    except PermissionError:
        print("The old result.pdf file is exist and cannot be overwriten. Check whether this file is in use, delete it and try again.\nAfter the file has been deleted, the generation process will continue.")
        continue_flag = 0
        while(not continue_flag):
            sleep(1)
            if(not os.path.exists("./result.pdf")):
                continue_flag = 1
    shutil.move(docsPath + "/site/pdf/combined.pdf","./result.pdf")
    shutil.rmtree(docsPath + "/site")
    exit = 0
    while(not exit):
        rm_source = input("All done. Get the generated PDF at ./result.pdf\nWould you like to delete sources folder? (y/n)")
        if(rm_source == "y"):
            import stat
            for root, dirs, files in os.walk(docsPath, topdown=False):
                for name in files:
                    filename = os.path.join(root, name)
                    os.chmod(filename, stat.S_IWUSR)
                    os.remove(filename)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(docsPath)
            exit = 1
        elif(rm_source == "n"):
            exit = 1
        else:
            print("Wrong opinion.")