from copy import deepcopy
from pathlib import Path
from shutil import copytree, move, rmtree, ignore_patterns
from subprocess import check_call, CalledProcessError
from sys import argv
from time import sleep

from ruamel import yaml

try:
    sourcePath = Path(argv[1])
except IndexError:
    print("Usage: export.py source_folder")
    exit()

if not sourcePath.exists():
    raise FileNotFoundError("Sources folder not found.")

if not (sourcePath/"mkdocs.yml").exists():
    raise FileNotFoundError("MkDocs configuration file is missing.")

docsPath = Path.cwd()/"tmp"
try:
    copytree(sourcePath, docsPath, ignore=ignore_patterns(".git"))
except FileExistsError:
    rmtree(docsPath)
    copytree(sourcePath, docsPath, ignore=ignore_patterns(".git"))
configPath = docsPath/"mkdocs.yml"
softwarePath = docsPath/"docs/daily-maintenance/software.md"
operationsPath = docsPath/"docs/daily-maintenance/operations.md"
software_imgs = docsPath/"docs/daily-maintenance/software/images"
operations_imgs = docsPath/"docs/daily-maintenance/operations/images"

config = open(configPath, mode='r', encoding='utf-8')
loadedCfg = yaml.load(config, Loader=yaml.RoundTripLoader)
newCfg = deepcopy(loadedCfg)
tmp_cfg = open(docsPath/"tmp.yml", mode='w', encoding='utf-8')

if (docsPath/"docs/processed").exists():
    print("Source documents have been processed, skipped processing.")

else:
    print("Merging documents...")
    software = open(softwarePath, mode='w', encoding='utf-8')
    operations = open(operationsPath, mode='w', encoding='utf-8')
    for i in range(len(loadedCfg['nav'])):
        tmp = list(loadedCfg['nav'][i].values())[0]
        for j in range(len(tmp)):
            if type(list(tmp[j].values())[0]) == yaml.comments.CommentedSeq and str(list(tmp[j].keys())[0]) == "软件篇":
                for k in range(len(list(tmp[j].values())[0])):
                    path = docsPath/"docs"/str(list(list(tmp[j].values())[0][k].values())[0])
                    print(path, "has been merged into", softwarePath)
                    file = open(path, mode='r', encoding='utf-8')
                    for line in file.readlines():
                        if '{: target="_blank" rel="noopener noreferrer" .external }' in line:
                            line = line.replace('{: target="_blank" rel="noopener noreferrer" .external }', "")
                        if '{: style="width: 50%" }' in line:
                            line = line.replace('{: style="width: 50%" }', "")
                        if "../../" in line:
                            line = line.replace("../../", "../")
                        software.writelines(line)
                    file.close()

            if type(list(tmp[j].values())[0]) == yaml.comments.CommentedSeq and str(list(tmp[j].keys())[0]) == "操作篇":
                for k in range(len(list(tmp[j].values())[0])):
                    path = docsPath/"docs"/str(list(list(tmp[j].values())[0][k].values())[0])
                    print(path, "has been merged into", operationsPath)
                    file = open(path, mode='r', encoding='utf-8')
                    for line in file.readlines():
                        if '{: target="_blank" rel="noopener noreferrer" .external }' in line:
                            line = line.replace('{: target="_blank" rel="noopener noreferrer" .external }', "")
                        if '{: style="width: 50%" }' in line:
                            line = line.replace('{: style="width: 50%" }', "")
                        if "../../" in line:
                            line = line.replace("../../", "../")
                        operations.writelines(line)
                    file.close()
    operations.close()
    software.close()

newCfg['nav'][1]['日常维护'][0]['软件篇'] = "daily-maintenance/software.md"
newCfg['nav'][1]['日常维护'][1]['操作篇'] = "daily-maintenance/operations.md"
newCfg['copyright'] = "本手册所有内容均在 CC BY-SA 4.0 和 SATA 协议条款下提供。"
newCfg['markdown_extensions'][7]['toc'] = {'permalink': 'true'}

try:
    del newCfg['repo_url']
    del newCfg['repo_name']
except KeyError:
    print("Some key-value pairs is missing. Maybe the configuration file has been modified?")

newCfg['plugins'] = [{'mkpdfs': {'design': str(Path.cwd()/'mkpdfs-style/report.css'), 'company': '赣州三中学生会',
                                 'author': '秘书处', 'toc_title': '目录'}}]

yaml.dump(newCfg, tmp_cfg, Dumper=yaml.RoundTripDumper, default_flow_style=False, encoding='utf-8', allow_unicode=True)
config.close()
tmp_cfg.close()
configPath.unlink()
(docsPath/"tmp.yml").rename(configPath)
print("New mkdocs configuration generated.")

try:
    software_imgs_list = list(software_imgs.iterdir())
    operations_imgs_list = list(operations_imgs.iterdir())
    if not (docsPath/"docs/daily-maintenance/images/").exists():
        (docsPath/"docs/daily-maintenance/images/").mkdir()
    for i in range(len(list(software_imgs.iterdir()))):
        path = Path(software_imgs/software_imgs_list[i])
        src = Path(docsPath/"docs/daily-maintenance/software/images"/software_imgs_list[i])
        dst = docsPath/"docs/daily-maintenance/images/"
        move(src, dst)
    for i in range(len(list(operations_imgs.iterdir()))):
        path = Path(operations_imgs/operations_imgs_list[i])
        src = Path(docsPath/"docs/daily-maintenance/operations/images"/operations_imgs_list[i])
        dst = docsPath/"docs/daily-maintenance/images/"
        move(src, dst)
    print("Images have been merged.\nCleaning up...")
except FileNotFoundError:
    print("Old images folders not found, skipped.")
try:
    rmtree(docsPath/"docs/daily-maintenance/operations")
    rmtree(docsPath/"docs/daily-maintenance/software")
except FileNotFoundError:
    print("Old documents folders not found, skipped.")
open(docsPath/"docs/processed", mode='w')

print("Generating PDF...")
try:
    check_call("cd " + str(docsPath) + " && mkdocs build", shell=True)

except CalledProcessError:
    print("Generation failed. Check the output above for more information.")

else:
    try:
        Path("./result.pdf").unlink()
    except FileNotFoundError:
        pass
    except PermissionError:
        print(
            "The old result.pdf file is exist and cannot be overwriten. Check whether this file is in use, delete it "
            "and try again.\nAfter the file has been deleted, the generation process will continue.")
        continue_flag = 0
        while not continue_flag:
            sleep(1)
            if not Path("./result.pdf").exists():
                continue_flag = 1
    move(docsPath/"site/pdf/combined.pdf", "./result.pdf")
    rmtree(docsPath)
    print("All done. Get the generated PDF at ./result.pdf")
