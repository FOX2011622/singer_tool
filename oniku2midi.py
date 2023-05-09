import os

import mido
import soundfile
import torch
import torchaudio
from mido import MidiFile

head_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

note_time = []
note_key = []
final_res = []


def pitch_to_name(pitch):
    if pitch:
        return f"{head_list[int(pitch % 12)]}{int(pitch / 12) - 1}"
    else:
        print(pitch)
        return "rest"


def note_map(start_time, final_time):
    key_index = -1
    for index, tuple_time in enumerate(note_time):
        if start_time <= tuple_time[1]:
            key_index = index
            break
    if key_index == -1:
        return 0

    if final_time <= note_time[key_index][1]:
        return note_key[key_index]
    elif (note_time[key_index][1] - start_time) > (final_time - note_time[key_index][1]):
        return note_key[key_index]
    else:
        return note_key[key_index + 1]


def analysis_midi(f_name):
    n_time = []
    n_key = []
    tempo = 0
    mid = MidiFile(f'{dataset_path}/{f_name}/{f_name}.mid')

    for i, track in enumerate(mid.tracks):
        time = 0
        for msg in track:
            time += msg.time
            if msg.type == "set_tempo":
                tempo = msg.tempo
            if msg.type == "note_off":
                n_time.append((mido.tick2second(time - msg.time, 480, tempo), mido.tick2second(time, 480, tempo)))
                n_key.append(msg.note)
    return n_time, n_key


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
            row = row.replace("I", "i").replace("U", "u").replace("GlottalStop", "cl")
            word = row.replace("\n", "").split(" ")[-1]
            if word != "pau":  # and word != "br":
                temp_list.append(row)
            else:
                sentence_list.append(temp_list)
                temp_list = [row]
        # 分音素
        for index, data in enumerate(sentence_list[1:]):
            text = []
            phoneme = []
            note = []
            note_duration = []
            phoneme_duration = []
            slur_note = []
            temp_slur_note = ""
            temp_note = ""
            for row in data:
                s_time = int(row.replace("\n", "").split(" ")[0]) / 10 ** 7
                f_time = int(row.replace("\n", "").split(" ")[1]) / 10 ** 7
                dur_time = round(f_time - s_time, 6)
                word = row.replace("\n", "").split(" ")[-1]
                key = note_map(s_time, f_time)

                if temp_slur_note == word and temp_note != pitch_to_name(key):
                    slur_note.append("1")
                else:
                    slur_note.append("0")

                if word == "br":
                    phoneme.append("AP")
                    note.append("rest")
                elif word == "pau" or word == "sil":
                    phoneme.append("SP")
                    note.append("rest")
                elif word == "cl":
                    phoneme.append("cl")
                    note.append("rest")
                else:
                    phoneme.append(word)
                    note.append(pitch_to_name(key))
                    temp_note = pitch_to_name(key)
                phoneme_duration.append(dur_time)

                temp_slur_note = word

            # 分词
            text_flag = False
            note_dur = 0
            for i in range(0, len(phoneme)):
                if text_flag:
                    text.append("啊")
                    note_dur += phoneme_duration[i]
                    note_duration.append(note_dur)
                    note_duration.append(note_dur)
                    note_dur = 0
                    text_flag = False
                else:
                    if phoneme[i] in ["AP", "SP"]:
                        note_duration.append(phoneme_duration[i])
                    elif phoneme[i] in ["N", "cl"]:
                        text.append("啊")
                        note_duration.append(phoneme_duration[i])
                    elif phoneme[i] not in ["a", "i", "u", "e", "o"]:
                        text_flag = True
                        note_dur = phoneme_duration[i]
                    else:
                        text.append("啊")
                        note_duration.append(phoneme_duration[i])
            note_duration = [str(round(x, 6)) for x in note_duration]
            phoneme_duration = [str(round(x, 6)) for x in phoneme_duration]
            res = "|".join([" ".join(text), " ".join(phoneme), " ".join(note), " ".join(note_duration),
                            " ".join(phoneme_duration), " ".join(slur_note)])
            start = int(data[0].replace("\n", "").split(" ")[0]) / 10 ** 7
            end = int(data[-1].replace("\n", "").split(" ")[1]) / 10 ** 7
            if len(phoneme) != len(note_duration):
                print(f"split_time:{start} {end}\r\n {res}\r\n")
            splice_name = f"{f_name}_{str(index + 1).zfill(2)}"
            if 15 >= (end - start) > 3:
                soundfile.write(f"./oniku/{splice_name}.wav", audio[int(start * sr):int(end * sr)], sr, format="wav")

                final_res.append(f"{splice_name}|{res}\n")


if __name__ == "__main__":
    dataset_path = "./ONIKU_KURUMI_UTAGOE_DB"
    audio_list = os.listdir(dataset_path)
    os.makedirs("oniku", exist_ok=True)

    for file_name in audio_list:
        note_time, note_key = analysis_midi(file_name)
        split_lab(file_name)

    with open("oniku.txt", "w", encoding='utf-8') as f:
        f.writelines(final_res)
