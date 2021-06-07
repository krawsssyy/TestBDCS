from platform import system
from sys import argv
from os import listdir, access, W_OK, getcwd, stat
from os.path import isfile, join, getctime, getsize, exists
from datetime import datetime
from stat import FILE_ATTRIBUTE_HIDDEN
import json

def createDate(date):
    fromts = str(datetime.fromtimestamp(date))
    return fromts[0:4] + "/" + fromts[5:7] + "/" + fromts[8:10] + "-" + fromts[11:13] + ":" + fromts[14:16]

def scan(operatingSystem):
    globalFiles = { }
    if operatingSystem == "Windows":
        files = [f for f in listdir(getcwd()) if isfile(f)]
        for file in files:
            globalFiles[file] = {"FileSize":getsize(file),"Changed":createDate(getctime(file)), "Hidden":1 if bool(stat(file).st_file_attributes & FILE_ATTRIBUTE_HIDDEN) == True else 0, "ReadOnly":0 if access(file, W_OK) else 1}
    else:
        files = [f for f in listdir(getcwd()) if isfile(f)]
        for file in files:
            globalFiles[file] = {"FileSize":getsize(file),"Changed":createDate(getctime(file)), "Hidden":1 if file.startswith('.') else 0, "ReadOnly":0 if access(file, W_OK) else 1}
    return globalFiles

def biggestFive(globalFiles):
    top = []
    limit = 5 if len(globalFiles.keys()) >= 5 else len(globalFiles.keys())
    maxSize = -1
    i = 0
    while (i < limit):
        for key in globalFiles.keys():
            if key not in top:
                if globalFiles[key]["FileSize"] > maxSize:
                    maxKey = key
        top.append(maxKey)
        i = i + 1
    return top

def getPercentageAttr(globalFiles, attr):
    size = len(globalFiles.keys())
    count = 0
    for key in globalFiles.keys():
        if globalFiles[key][attr] == 1:
            count = count + 1
    return count * 100 / size;

def getMonthlyUsage(globalFiles):
    months = {}
    for key in globalFiles.keys():
        date = globalFiles[key]["Changed"][:7].replace('-', '/')
        if date not in months.keys():
            months[date] = 1
        else:
            months[date] = months[date] + 1
    return months

def main():
    operatingSystem = system()
    globFiles = {}
    if len(argv) != 2:
        print("Usage: python3 main.py [OPTION]\nUse python3 main.py -h for help")
        exit(1)
    option = argv[1]
    print("Detected platform: " + operatingSystem)
    print("Given option: " + option)
    if option == "-h":
        print("HELP PAGE\nUsage: python3 main.py [OPTION]\nAvailable options: scan/query")
        exit(0)
    elif option == "scan":
        globFiles = scan(operatingSystem)
        with open('cache.json','w') as f:
            json.dump(globFiles, f, indent=4)
    elif option == "query":
        if exists('cache.json'):
            with open('cache.json','r') as f:
                globFiles = json.load(f)
        else:
            globFiles = scan(operatingSystem)
            with open('cache.json','w') as f:
                json.dump(globFiles, f, indent=4)
        print("Number of files: " + str(len(globFiles.keys())))
        topFiles = biggestFive(globFiles)
        topFilesLen = len(topFiles)
        TopFiles = ', '.join(topFiles)
        print(f"Top {topFilesLen} largest files: {TopFiles}")
        print(f"{getPercentageAttr(globFiles, 'Hidden')}% are hidden")
        print(f"{getPercentageAttr(globFiles, 'ReadOnly')}% are read-only")
        months = getMonthlyUsage(globFiles)
        for date in months.keys():
            if months[date] == 1:
                print(date + ":" + str(months[date]) + " modified file")
            else:
                print(date + ":" + str(months[date]) + " modified files")
    else:
        print("Invalid option!")
        print("Usage: python3 main.py [OPTION]\nUse python3 main.py -h for help")
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
