import json

romaji2ipa_dict = json.load(open("romaji2ipa.json"))
print(romaji2ipa_dict)
final_res = []


def phoneme2romaji(raw_phonemes):
    phoneme_list = raw_phonemes.split(" ")
    romaji_list = []
    # 分词
    text_flag = False
    text = ""
    for phoneme in phoneme_list:
        if text_flag:
            text += phoneme
            romaji_list.append(text)
            text = ""
            text_flag = False
        else:
            if phoneme in ["AP", "SP", "N", "cl"]:
                romaji_list.append(phoneme)
            elif phoneme not in ["a", "i", "u", "e", "o"]:
                text_flag = True
                text = phoneme
            else:
                romaji_list.append(phoneme)
    return romaji_list


def romaji2ipa(romaji_list):
    ipa_list = []
    for romaji in romaji_list:
        if romaji in ["AP", "SP"]:
            ipa_list.append(romaji)
        elif romaji == "cl":
            ipa_list.append("̚")
        else:
            if len(romaji) > 2:
                if romaji[0] == romaji[1]:
                    ipa_list.append("̚")
                    ipa = romaji2ipa_dict.get(romaji[1:], "$$")
                else:
                    ipa = romaji2ipa_dict.get(romaji, "$$")
            else:
                ipa = romaji2ipa_dict.get(romaji, "$$")
            if len(ipa) > 1:
                ipa_list.append(ipa[:-1])
                ipa_list.append(ipa[-1])
            else:
                ipa_list.append(ipa)

    return " ".join(ipa_list)


if __name__ == "__main__":
    with open(f"oniku.txt", "r", encoding='utf-8') as f:
        data = f.readlines()
    database_res = []
    cou = 0
    for line in data:
        split_data = line.split("|")
        phonemes = split_data[2]
        romaji_res = phoneme2romaji(phonemes)

        ipa_res = romaji2ipa(romaji_res)

        print(line.split("|")[0])
        print(" ".join(romaji_res))
        print(phonemes)
        print(ipa_res, "\r\n")

        if "$" in ipa_res:
            cou += 1
            continue
        assert len(ipa_res.split(" ")) == len(phonemes.split(" "))
        split_data[2] = ipa_res
        database_res.append("|".join(split_data))
    print(cou)
    with open(f"oniku_ipa.txt", "w", encoding='utf-8') as f:
        data = f.writelines(database_res)
