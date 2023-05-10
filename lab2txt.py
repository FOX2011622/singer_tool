import os
from tqdm import tqdm
def get_end_file(dir_path, end):
    file_lists = []
    for root, dirs, files in os.walk(dir_path):
        files = [f for f in files if f[0] != '.']
        dirs[:] = [d for d in dirs if d[0] != '.']
        for f_file in files:
            if f_file.endswith(end):
                file_lists.append(os.path.join(root, f_file).replace("\\", "/"))
    return file_lists
file_lists = get_end_file("jp_s","lab")
with tqdm(total=len(file_lists)) as p_bar:
    p_bar.set_description('Processing')
    for i in file_lists:
        # print(i)
        ext = os.path.splitext(i)
        # print(ext)
        new_name = ext[0] + ".txt"
        os.rename(i,new_name)
        p_bar.update(1)