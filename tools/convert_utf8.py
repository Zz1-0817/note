import sys
import os


def convert_to_utf8(input_file, output_file):
    with open(input_file, "r", errors="replace") as file:
        content = file.read()

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(content)


path = sys.argv[1]

convert_to_utf8(path, path)
