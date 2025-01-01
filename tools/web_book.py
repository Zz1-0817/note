from functions import *


def print_preamble(path):
    preamble = open(path + "preamble.tex", "r", encoding="utf-8")
    next(preamble)
    print("\\documentclass{book}")
    for line in preamble:
        if line.find("%") == 0:
            continue
        if line.find("externaldocument") >= 0:
            continue
        if line.find("multicol") >= 0:
            continue
        if line.find("xr-hyper") >= 0:
            continue
        print(line, end="")
    preamble.close()
    return


path = get_path()

print_preamble(path)

print("\\begin{document}")

lijstje = list_text_files(path)

ext = ".tex"
for name in lijstje:
    filename = path + name + ext
    tex_file = open(filename, "r")
    verbatim = 0
    for line in tex_file:
        verbatim = verbatim + beginning_of_verbatim(line)
        if verbatim:
            if end_of_verbatim(line):
                verbatim = 0
            if name != "introduction":
                print(line, end="")
            continue
        if line.find("\\input{preamble}") == 0:
            continue
        if line.find("\\begin{document}") == 0:
            continue
        if line.find("\\title{") == 0:
            line = line.replace("\\title{", "\\chapter{")
        if line.find("\\maketitle") == 0:
            continue
        if line.find("\\tableofcontents") == 0:
            continue
        if line.find("\\input{chapters}") == 0:
            continue
        if line.find("\\bibliography") == 0:
            continue
        if line.find("\\end{document}") == 0:
            continue
        if is_label(line):
            text = "\\label{" + name + "-"
            line = line.replace("\\label{", text)
        if contains_ref(line):
            line = replace_refs(line, name)
        print(line, end="")

    tex_file.close()

print("\\end{document}")
