import struct
import json

charset = [" ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "*", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "RV", "BX", "EX", "SP", "FZ", "ウ", "ア", "イ", "オ", "エ", "ケ", "コ", "カ", "ク", "キ", "セ", "サ", "ソ", "シ", "ス", "テ", "ト", "ツ", "タ", "チ", "ネ", "ノ", "ヌ", "ナ", "ニ", "ヒ", "ヘ", "ホ", "ハ", "フ", "ミ", "マ", "メ", "ム", "モ", "ヤ", "ヨ", "ユ", "ロ", "ル", "リ", "レ", "ラ", "ン", "熱", "斗", "ワ", "ヲ", "ギ", "ガ", "ゲ", "ゴ", "グ", "ゾ", "ジ", "ゼ", "ズ", "ザ", "デ", "ド", "ヅ", "ダ", "ヂ", "ベ", "ビ", "ボ", "バ", "ブ", "ピ", "パ", "ペ", "プ", "ポ", "ゥ", "ァ", "ィ", "ォ", "ェ", "ュ", "ヴ", "ッ", "ョ", "ャ", "-", "×", "=", ":", "%", "?", "+", "█", "[bat]", "ー", "!", "&", ",", "゜", ".", "・", ";", "'", "\"", "~", "/", "(", ")", "「", "」", "�", "_", "ƶ", "[L]", "[B]", "[R]", "[A]", "あ", "い", "け", "く", "き", "こ", "か", "せ", "そ", "す", "さ", "し", "つ", "と", "て", "た", "ち", "ね", "の", "な", "ぬ", "に", "へ", "ふ", "ほ", "は", "ひ", "め", "む", "み", "も", "ま", "ゆ", "よ", "や", "る", "ら", "り", "ろ", "れ", "[END]", "ん", "を", "わ", "研", "げ", "ぐ", "ご", "が", "ぎ", "ぜ", "ず", "じ", "ぞ", "ざ", "で", "ど", "づ", "だ", "ぢ", "べ", "ば", "び", "ぼ", "ぶ", "ぽ", "ぷ", "ぴ", "ぺ", "ぱ", "ぅ", "ぁ", "ぃ", "ぉ", "ぇ", "ゅ", "ょ", "っ", "ゃ", "容", "量", "全", "木", "[MB]", "無", "現", "実", "[circle]", "×", "緑", "道", "不", "止", "彩", "起", "父", "集", "院", "一", "二", "三", "四", "五", "六", "七", "八", "陽", "十", "百", "千", "万", "脳", "上", "下", "左", "右", "手", "来", "日", "目", "月", "獣", "各", "人", "入", "出", "山", "口", "光", "電", "気", "綾", "科", "次", "名", "前", "学", "校", "省", "祐", "室", "世", "界", "高", "朗", "枚", "野", "悪", "路", "闇", "大", "小", "中", "自", "分", "間", "系", "花", "問", "究", "門", "城", "王", "兄", "化", "葉", "行", "街", "屋", "水", "見", "終", "新", "桜", "先", "生", "長", "今", "了", "点", "井", "子", "言", "太", "属", "風", "会", "性", "持", "時", "勝", "赤", "代", "年", "火", "改", "計", "画", "職", "体", "波", "回", "外", "地", "員", "正", "造", "値", "合", "戦", "川", "秋", "原", "町", "晴", "用", "金", "郎", "作", "数", "方", "社", "攻", "撃", "力", "同", "武", "何", "発", "少", "教", "以", "白", "早", "暮", "面", "組", "後", "文", "字", "本", "階", "明", "才", "者", "向", "犬", "々", "ヶ", "連", "射", "舟", "戸", "切", "土", "炎", "伊", "夫", "鉄", "国", "男", "天", "老", "師", "堀", "杉", "士", "悟", "森", "霧", "麻", "剛", "垣", "★", "[bracket1]", "[bracket2]", "[.]"]

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
            if cur_byte == 0xe6:
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

CHIP_DATA_OFFSET = 0x21da8
CHIP_NAMES_POINTERS_OFFSET = 0x42068
NUM_CHIPS = 411

def read_ptr_as_file_offset(f, offset):
    f.seek(offset)
    return struct.unpack("<I", f.read(4))[0] - 0x8000000

def main():
    with open("bn6f.gba", "rb") as f:
        chip_names_pt1_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET)
        chip_names_pt2_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET + 4)
        #navi_names_ptr = read_ptr_as_file_offset(f, NAVI_NAMES_POINTER_OFFSET)

        chip_names_pt1 = dump_simple_text_script(f, chip_names_pt1_ptr, 256)
        chip_names_pt2 = dump_simple_text_script(f, chip_names_pt2_ptr, NUM_CHIPS - 256)
        #navi_names = dump_simple_text_script(f, navi_names_ptr, 23)

    chip_names = chip_names_pt1 + chip_names_pt2
    output = ""
    #with open("exe45_chips_template.json", "r") as f:
    #    exe45_chips = json.load(f)

    #for manual_chip_name, manual_chip_id in manual_chips.items():
    #    exe45_chips[manual_chip_name]["id"] = manual_chip_id
    #
    #for i, chip_name in enumerate(chip_names):
    #    if chip_name in exe45_chips and chip_name not in manual_chips:
    #        exe45_chips[chip_name]["id"] = i

    chip_infos = {}

    with open("bn6f.gba", "rb") as f:
        for chip_id, chip_name in enumerate(chip_names):
            f.seek(CHIP_DATA_OFFSET + chip_id * 0x2c + 0x7)
            chip_library_as_num = ord(f.read(1))
            chip_mb = ord(f.read(1))
            chip_effect_flags = ord(f.read(1))
            if 0 <= chip_library_as_num <= 2 and chip_effect_flags & 0x40 != 0 or (chip_library_as_num == 2 and chip_id < 312):
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

                chip_info["mb"] = chip_mb

                try:
                    chip_library = chip_library_id_to_name[chip_library_as_num]
                except KeyError as e:
                    raise RuntimeError(f"{chip_name}") from e
                chip_info["library"] = chip_library
                chip_infos[chip_name] = chip_info

    with open("bn6_chips.json", "w+") as f:
        json.dump(chip_infos, f, indent=2)

if __name__ == "__main__":
    main()
