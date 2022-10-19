import struct
import json

charset = [" ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "*", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "ÿ", "Ÿ", "EX", "SP", "DS", "Œ", "œ", "?", "+", "-", "×", "À", "Á", "Â", "Ã", "Ä", "Å", "Æ", "Ç", "È", "É", "Ê", "Ë", "Ì", "Í", "Î", "Ï", "Ð", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ö", "ý", "Ø", "Ù", "Ú", "Û", "Ü", "Ý", "Þ", "ß", "à", "á", "â", "ã", "ä", "å", "æ", "ç", "è", "é", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "ò", "ó", "ô", "õ", "ö", "þ", "ø", "ù", "ú", "û", "ü", "[×alt]", "÷", "XX", "V2", "V3", "¿", "@", "<", ">", "\\[", "\\]", "[-]", "[×]", "=", ":", "%", "¡", "[+]", "█", "[bat]", "ー", "!", "[V4]", "[V5]", "&", ",", "。", ".", "・", ";", "'", "\"", "~", "/", "(", ")", "「", "」", "α", "β", "Ω", "■", "_", "[z]", "[S]", "[M]", "[G]", "[1px]", "[MB]", "[Trophy1A]", "[Trophy1B]", "[Trophy2A]", "[Trophy2B]", "[TVShow1]", "[TVShow2]", "[Promise1]", "[Promise2]", "[Meal1]", "[Meal2]", "[School1]", "[School2]", "[Other1]", "[Other2]", "[bracket1]", "[bracket2]", "[8px]", "⋯", "$", "€", "£", "¥", "¢", "#", "←", "↑", "→", "↓", "[0lower]", "[1lower]", "[2lower]", "[3lower]", "[4lower]", "[5lower]", "[6lower]", "[7lower]", "[8lower]", "[9lower]", "[Alower]", "[Plower]", "[Mlower]", "[:lower]", "わ", "研", "げ", "ぐ", "ご", "が", "ぎ", "ぜ", "ず", "じ", "ぞ", "ざ", "で", "ど", "づ", "だ", "ぢ", "べ", "ば", "び", "ぼ", "ぶ", "ぽ", "ぷ", "ぴ", "ぺ", "ぱ", "ぅ", "ぁ", "ぃ", "ぉ", "ぇ", "ゅ", "ょ", "っ", "ゃ", "[Ω]", "[←]", "[↓]", "木", "[MB2]", "無", "現", "実", "[circle]", "[cross]", "[#]", "[⋯]", "不", "止", "彩", "[\\[]", "父", "集", "院", "一", "二", "三", "四", "五", "六", "七", "八", "陽", "十", "百", "千", "万", "脳", "上", "下", "左", "右", "手", "足", "日", "目", "月", "[\\]]", "[<]", "人", "入", "出", "山", "口", "光", "電", "気", "助", "科", "次", "名", "前", "学", "校", "省", "祐", "室", "世", "界", "燃", "朗", "枚", "島", "悪", "路", "闇", "大", "小", "中", "自", "分", "間", "系", "花", "問", "[>]", "[$]", "城", "王", "兄", "化", "行", "街", "屋", "水", "見", "終", "丁", "桜", "先", "生", "長", "今", "了", "点", "井", "子", "言", "太", "属", "風", "会", "性", "持", "時", "勝", "赤", "年", "火", "改", "計", "画", "体", "波", "回", "外", "地", "正", "造", "値", "合", "戦", "川", "秋", "原", "町", "所", "用", "金", "郎", "作", "数", "方", "社", "攻", "撃", "力", "同", "武", "何", "発", "少", "以", "白", "早", "暮", "面", "組", "後", "文", "字", "本", "階", "明", "才", "者", "立", "々", "ヶ", "連", "射", "綾", "切", "土", "炎", "伊"]

def dump_simple_text_script(f, offset, num_scripts):
    f.seek(offset)

    script_offsets = []

    for i in range(num_scripts):
        script_offsets.append(struct.unpack("<H", f.read(2))[0])

    text_scripts = []

    for script_offset in script_offsets:
        f.seek(offset + script_offset)
        cur_text_script = ""
        while True:
            cur_byte = ord(f.read(1))
            if cur_byte == 0xe5:
                break
            cur_text_script += charset[cur_byte]

        text_scripts.append(cur_text_script)

    return text_scripts

all_chip_codes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ*"

chip_library_id_to_name = {
    0: "Standard",
    1: "Mega",
    2: "Giga"
}

CHIP_DATA_OFFSET = 0x1af0c
CHIP_NAMES_POINTERS_OFFSET = 0x3cb98
NAVI_NAMES_POINTER_OFFSET = 0x5174c
NUM_CHIPS = 389

def read_ptr_as_file_offset(f, offset):
    f.seek(offset)
    return struct.unpack("<I", f.read(4))[0] - 0x8000000

def main():
    with open("exe45_us_pvp.gba", "rb") as f:
        chip_names_pt1_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET)
        chip_names_pt2_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET + 4)
        navi_names_ptr = read_ptr_as_file_offset(f, NAVI_NAMES_POINTER_OFFSET)

        chip_names_pt1 = dump_simple_text_script(f, chip_names_pt1_ptr, 256)
        chip_names_pt2 = dump_simple_text_script(f, chip_names_pt2_ptr, NUM_CHIPS - 256)
        navi_names = dump_simple_text_script(f, navi_names_ptr, 23)

    chip_names = chip_names_pt1 + chip_names_pt2
    output = ""
    #with open("exe45_chips_template.json", "r") as f:
    #    exe45_chips = json.load(f)

    manual_chips = {
        "Cannon": 1,
        "LifeAura": 201,
        "FinalGun": 290,
        "Bass": 301
    }

    #for manual_chip_name, manual_chip_id in manual_chips.items():
    #    exe45_chips[manual_chip_name]["id"] = manual_chip_id
    #
    #for i, chip_name in enumerate(chip_names):
    #    if chip_name in exe45_chips and chip_name not in manual_chips:
    #        exe45_chips[chip_name]["id"] = i

    chip_infos = {}

    with open("exe45_us_pvp.gba", "rb") as f:
        for chip_id, chip_name in enumerate(chip_names):
            f.seek(CHIP_DATA_OFFSET + chip_id * 0x2c + 0x8)
            chip_library_as_num = ord(f.read(1))
            chip_effect_flags = ord(f.read(1))
            if 0 <= chip_library_as_num <= 2 and chip_effect_flags & 0x40 != 0:
                chip_info = {}
                chip_info["id"] = chip_id
                chip_info["name"] = chip_name

                f.seek(CHIP_DATA_OFFSET + chip_id * 0x2c)

                chip_codes = []
                for i in range(4):
                    chip_code_as_num = ord(f.read(1))
                    if chip_code_as_num == 0xff:
                        break
                    chip_codes.append(all_chip_codes[chip_code_as_num])

                chip_info["codes"] = chip_codes

                f.seek(CHIP_DATA_OFFSET + chip_id * 0x2c + 0x6)
                chip_mb = ord(f.read(1))
                chip_info["mb"] = chip_mb

                try:
                    chip_library = chip_library_id_to_name[chip_library_as_num]
                except KeyError as e:
                    raise RuntimeError(f"{chip_name}") from e
                chip_info["library"] = chip_library
                chip_infos[chip_name] = chip_info

    with open("exe45_chips.json", "w+") as f:
        json.dump(chip_infos, f, indent=2)

    navi_names_as_json = {}

    for i, navi_name in enumerate(navi_names):
        if navi_name != "XXXX":
            if navi_name == "NumberMan":
                navi_mb = 70
            else:
                navi_mb = 50

            if navi_name == "MegaMan":
                navi_megafolder = 7
            elif navi_name == "Bass":
                navi_megafolder = 4
            else:
                navi_megafolder = 5

            if navi_name == "MegaMan":
                navi_gigafolder = 2
            else:
                navi_gigafolder = 1

            navi_names_as_json[navi_name] = {
                "id": i,
                "name": navi_name,
                "mb": navi_mb,
                "megafolder": navi_megafolder,
                "gigafolder": navi_gigafolder
            }

    with open("navis.json", "w+") as f:
        json.dump(navi_names_as_json, f, indent=2)

        #if chip_name not in exe45_chips:
        #    print(f"{chip_name} missing! id: 0x{i:x}")
        #else:
        #    if chip_name in chip_names_as_set:
        #        print(f"Duplicate chip \"{chip_name}\"! id: 0x{i:x}")
        #    else:
        #        print(f"{chip_name}: 0x{i:x}")
        #        chip_names_as_set.add(chip_name)

    #output += "".join(f"{

if __name__ == "__main__":
    main()
