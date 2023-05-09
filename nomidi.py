import os

import soundfile
import torch
import torchaudio

final_res = []


def lab2mfa(text_list):
    res_list = []
    # 分词
    cl_flag = False
    temp_text = "@"
    for text in text_list:
        if text in ["AP", "SP"]:
            pass
        elif text == "cl":
            cl_flag = True
        elif text in ["a", "i", "u", "e", "o"]:
            if text == temp_text[-1]:
                pass
            else:
                res_list.append(text)
        else:
            if cl_flag:
                res_list.append(f"{text[0]}{text}")
                cl_flag = False
            else:
                temp_text = text
                res_list.append(text)

    return " ".join(res_list).lower()


def split_lab(f_name):
    audio, sr = torchaudio.load(f"{dataset_path}/{f_name}/{f_name}.wav")
    if len(audio.shape) == 2 and audio.shape[1] >= 2:
        audio = torch.mean(audio, dim=0).unsqueeze(0)
    audio = audio.cpu().numpy()[0]
    with open(f"{dataset_path}/{f_name}/{f_name}.lab", "r") as f:
        raw_data = f.readlines()
        sentence_list = []
        temp_list = []
        # 分句
        for row in raw_data:
            row = row.replace("I", "i").replace("U", "u")
            word = row.replace("\n", "").split(" ")[-1]
            if word != "pau":  # and word != "br":
                temp_list.append(row)
            else:
                sentence_list.append(temp_list)
                temp_list = [row]
        # 分音素
        for index, data in enumerate(sentence_list[1:]):
            text_list = []
            phoneme = []
            phoneme_duration = []

            for row in data:
                s_time = int(row.replace("\n", "").split(" ")[0]) / 10 ** 7
                f_time = int(row.replace("\n", "").split(" ")[1]) / 10 ** 7
                dur_time = round(f_time - s_time, 6)
                word = row.replace("\n", "").split(" ")[-1]

                if word == "GlottalStop":
                    pass
                elif word == "br":
                    phoneme.append("AP")
                elif word == "pau" or word == "sil":
                    phoneme.append("SP")
                elif word == "cl":
                    phoneme.append("cl")
                else:
                    phoneme.append(word)
                phoneme_duration.append(dur_time)

            # 分词
            text_flag = False
            cl_flag = False
            text = ""
            for i in range(0, len(phoneme)):
                if text_flag:
                    text += phoneme[i]
                    text_list.append(text)
                    text = ""
                    text_flag = False
                else:
                    if phoneme[i] in ["AP", "SP", "N"]:
                        text_list.append(phoneme[i])
                    elif phoneme[i] in ["cl"]:
                        text_list.append(phoneme[i])
                    elif phoneme[i] not in ["a", "i", "u", "e", "o"]:
                        text_flag = True
                        text = phoneme[i]
                    else:
                        text_list.append(phoneme[i])
            phoneme_duration = [str(round(x, 6)) for x in phoneme_duration]
            res = "|".join(["啊", " ".join(phoneme), "rest", "0", " ".join(phoneme_duration), "0"])
            start = int(data[0].replace("\n", "").split(" ")[0]) / 10 ** 7
            end = int(data[-1].replace("\n", "").split(" ")[1]) / 10 ** 7

            splice_name = f"{f_name}_{str(index + 1).zfill(2)}"
            if 15 >= (end - start) > 3:
                soundfile.write(f"{out_name}/{splice_name}.wav", audio[int(start * sr):int(end * sr)], sr,
                                format="wav")

                final_res.append(f"{splice_name}|{res}\n")
                with open(f"{mfa_path}/{splice_name}.txt", "w", encoding='utf-8') as f:
                    f.write(lab2mfa(text_list))


if __name__ == "__main__":
    dataset_path = "./ONIKU_KURUMI_UTAGOE_DB"
    mfa_path = "./oniku_mfa"
    out_name = "oniku"

    audio_list = os.listdir(dataset_path)
    os.makedirs(out_name, exist_ok=True)
    os.makedirs(mfa_path, exist_ok=True)
    for file_name in audio_list:
        split_lab(file_name)

    with open(f"{out_name}_nomidi.txt", "w", encoding='utf-8') as f:
        f.writelines(final_res)
