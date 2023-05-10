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
def get_file(dir_path):
    file_lists = []
    for root, dirs, files in os.walk(dir_path):
        files = [f for f in files if f[0] != '.']
        for f_file in files:
            file_lists.append(os.path.join(root, f_file).replace("\\", "/"))
    return file_lists
from tqdm  import tqdm
path = "S:\\diff-svc\\data\\"
# path = "S:\\training\\"
paths = get_end_file(path,"npy")
with tqdm(total=len(paths)) as p_bar:
    p_bar.set_description('删除中：')
    for path in paths:
        os.remove(path)
        # print(path)
        p_bar.update(1)
    print("down!")