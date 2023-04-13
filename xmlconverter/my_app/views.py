from django.shortcuts import render
from collections import OrderedDict
import re
from dict2xml import dict2xml
import tempfile
from django.contrib import messages
from django.views.static import serve
import os
from django.http import FileResponse
def remove_unwanted_words(line1):
    remove_words = ["https://","http://","Ã"]
    replace_words = [(":","-")]
    for words in remove_words:
        line1 = line1.replace(words,"")
    for words in replace_words:
        line1 = line1.replace(words[0],words[1])
    return line1


def  home(request):
    regex = re.compile(r"^(\s)+", re.IGNORECASE)
    addr = re.compile(r"@(.)+", re.IGNORECASE)
    if request.method ==  "POST":
        file = request.FILES['file'].readlines()
        lines = []
        for i in range(len(file)):
            output = str(file[i], 'UTF-8')
            lines.append(output)
        root = OrderedDict()
        i = 0
        while i < len(lines):
            line1 = lines[i].replace('\n', '')
            if line1[0] == '#':
                i += 1
                continue
            line = line1
            command = line.split(' ')
            if command[0] == 'config':
                if command[1] not in root.keys():
                    root[command[1]] = OrderedDict()
                config = root[command[1]]
                if command[2] not in config.keys():
                    config[command[2]] = OrderedDict()
                mode = config[command[2]]
                rootMode = config[command[2]]
                if command[2] == 'replacemsg':
                    mode[command[3]] = command[4]
                    i += 1
                    continue
                while i < len(lines):
                    line = lines[i].replace('\n', '')
                    line = regex.sub("", line)
                    line = addr.sub("", line)
                    line = remove_unwanted_words(line)
                    command = line.split(' ')
                    temp = line.replace(" ","_")
                    if command[0] == 'set':
                        mode[command[1]] = ' '.join(command[2:])
                    if command[0] == 'edit':
                        if command[1] not in mode.keys():
                            if "\"" not in line:
                                mode[command[1]] = OrderedDict()
                                mode = mode[command[1]]
                            else:
                                mode[temp[6:len(temp)-1]] = OrderedDict()
                                mode = mode[temp[6:len(temp)-1]]
                    if command[0] == 'next':
                        mode = rootMode
                    if command[0] == 'end':
                        break
                    i += 1
            i += 1
        xml = dict2xml(root, wrap='config', indent="")
        temp = tempfile.NamedTemporaryFile(delete=False,suffix=".xml")
        dst = temp.name
        filepath = dst
        with open(dst, 'w') as f:
            f.write(xml)
            f.close()
        return FileResponse(open(filepath, 'rb'), as_attachment=True)
    return render(request, "index.html")