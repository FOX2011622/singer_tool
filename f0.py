import json
import os
import shutil
from functools import reduce
from pathlib import Path
import parselmouth as pm
import matplotlib
import matplotlib.pyplot as plt
import yaml
from pylab import xticks, np
from tqdm import tqdm

from modules.vocoders.nsf_hifigan import NsfHifiGAN
head_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def get_f0_parselmouth(wavfile):
    f0 = pm.Sound(wavfile).to_pitch_ac(
            time_step= 0.01,
            voicing_threshold=0.45,
            pitch_floor=40,
            pitch_ceiling=1100,
        ).selected_array['frequency'],
    f0 = np.pad(f0, [0], mode='constant')
    return f0
def compare_pitch(f0_static_dict, pitch_time_temp, trans_key=0):
    return sum({k: v * f0_static_dict[str(k + trans_key)] for k, v in pitch_time_temp.items() if
                str(k + trans_key) in f0_static_dict}.values())


def f0_to_pitch(ff):
    f0_pitch = 69 + 12 * np.log2(ff / 440)
    return round(f0_pitch, 0)


def pitch_to_name(pitch):
    return f"{head_list[int(pitch % 12)]}{int(pitch / 12) - 1}"





def merge_f0_dict(dict_list):
    def sum_dict(a, b):
        temp = dict()
        for key in a.keys() | b.keys():
            temp[key] = sum([d.get(key, 0) for d in (a, b)])
        return temp

    return reduce(sum_dict, dict_list)


def collect_f0(f0):
    pitch_num = {}
    pitch_list = [f0_to_pitch(x) for x in f0[f0 > 0]]
    for key in pitch_list:
        pitch_num[key] = pitch_num.get(key, 0) + 1
    return pitch_num


def static_f0_time(f0):
    if isinstance(f0, dict):
        pitch_num = merge_f0_dict({k: collect_f0(v) for k, v in f0.items()}.values())
    else:
        pitch_num = collect_f0(f0)
    static_pitch_time = {}
    sort_key = sorted(pitch_num.keys())
    for key in sort_key:
        static_pitch_time[key] = round(pitch_num[key] * 512 / 44100, 2)
    return static_pitch_time


def get_end_file(dir_path, end):
    file_lists = []
    for root, dirs, files in os.walk(dir_path):
        files = [f for f in files if f[0] != '.']
        dirs[:] = [d for d in dirs if d[0] != '.']
        for f_file in files:
            if f_file.endswith(end):
                file_lists.append(os.path.join(root, f_file).replace("\\", "/"))
    return file_lists


if __name__ == "__main__":
    f0_dict = {}
    # 获取file_path文件夹下所有wav文件
    file_path= ""
    wav_paths = get_end_file(file_path, "wav")
    # parselmouth获取f0
    with tqdm(total=len(wav_paths)) as p_bar:
        p_bar.set_description('Processing')
        for wav_path in wav_paths:
            f0_dict[wav_path] = get_f0_parselmouth(wav_path)
            p_bar.update(1)
    pitch_time = static_f0_time(f0_dict)
    total_time = round(sum(pitch_time.values()), 2)
    pitch_time["total_time"] = total_time
    print(f"total time: {total_time}s")
    matplotlib.use('TkAgg')
    plt.title("数据集音域统计", fontproperties='SimHei')
    plt.xlabel("音高", fontproperties='SimHei')
    plt.ylabel("时长(s)", fontproperties='SimHei')
    xticks_labels = [pitch_to_name(i) for i in range(36, 96)]
    xticks(np.linspace(0, 55, 60, endpoint=True), xticks_labels)

    plt.plot(pitch_time.keys(), pitch_time.values(), color='dodgerblue')

    pitch_summary = os.path.join(file_path, 'pitch_distribution.png')
    #不太好使
    plt.savefig(fname=pitch_summary,
                dpi=1000,
                bbox_inches='tight',
                pad_inches=0.25,
                )
    file_path
    plt.show()
