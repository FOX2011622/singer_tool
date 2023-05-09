import os


def get_end_file(dir_path, end):
    file_lists = []
    for root, dirs, files in os.walk(dir_path):
        files = [f for f in files if f[0] != '.']
        dirs[:] = [d for d in dirs if d[0] != '.']
        for f_file in files:
            if f_file.endswith(end):
                file_lists.append(os.path.join(root, f_file).replace("\\", "/"))
    return file_lists


phoneme_list = []
with open("japanese_dict.txt", "r", encoding='utf-8') as f:
    data = f.readlines()
for line in data:
    phoneme_list.append(line.split("\t")[0])

file_lists = get_end_file("processed_dataset", "txt")
for f_path in file_lists:
    with open(f_path, "r") as f:
        lab = f.readline()
    for i in lab.split(" "):
        if i not in phoneme_list:
            print(f"{f_path}:{i}")
            os.remove(f_path)