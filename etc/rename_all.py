import os
import os.path
import glob
import re

target_dir = r"/mnt/c/data/VIDEO"
prefix = ""

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def run():
    count = 1
    for file_path in sorted(glob.glob(os.path.join(target_dir, "*.mp4")), key = natural_keys):
        prent_dir, file_name = os.path.split(file_path)
        ext = os.path.splitext(file_name)[1]

        newfile_name = prefix + "{0}".format(count) + ext
        newfile_path = os.path.join(parent_dir, newfile_name)

        os.rename(filepath, newfile_path)

if __name__ == '__main__':
    run()
