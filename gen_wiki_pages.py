import struct
import json

charset_us = [" ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "*", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "ÿ", "Ÿ", "EX", "SP", "DS", "Œ", "œ", "?", "+", "-", "×", "À", "Á", "Â", "Ã", "Ä", "Å", "Æ", "Ç", "È", "É", "Ê", "Ë", "Ì", "Í", "Î", "Ï", "Ð", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ö", "ý", "Ø", "Ù", "Ú", "Û", "Ü", "Ý", "Þ", "ß", "à", "á", "â", "ã", "ä", "å", "æ", "ç", "è", "é", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "ò", "ó", "ô", "õ", "ö", "þ", "ø", "ù", "ú", "û", "ü", "[×alt]", "÷", "XX", "V2", "V3", "¿", "@", "<", ">", "\\[", "\\]", "[-]", "[×]", "=", ":", "%", "¡", "[+]", "█", "[bat]", "ー", "!", "[V4]", "[V5]", "&", ",", "。", ".", "・", ";", "'", "\"", "~", "/", "(", ")", "「", "」", "α", "β", "Ω", "■", "_", "[z]", "[S]", "[M]", "[G]", "[1px]", "[MB]", "[Trophy1A]", "[Trophy1B]", "[Trophy2A]", "[Trophy2B]", "[TVShow1]", "[TVShow2]", "[Promise1]", "[Promise2]", "[Meal1]", "[Meal2]", "[School1]", "[School2]", "[Other1]", "[Other2]", "[bracket1]", "[bracket2]", "[8px]", "⋯", "$", "€", "£", "¥", "¢", "#", "←", "↑", "→", "↓", "[0lower]", "[1lower]", "[2lower]", "[3lower]", "[4lower]", "[5lower]", "[6lower]", "[7lower]", "[8lower]", "[9lower]", "[Alower]", "[Plower]", "[Mlower]", "[:lower]", "わ", "研", "げ", "ぐ", "ご", "が", "ぎ", "ぜ", "ず", "じ", "ぞ", "ざ", "で", "ど", "づ", "だ", "ぢ", "べ", "ば", "び", "ぼ", "ぶ", "ぽ", "ぷ", "ぴ", "ぺ", "ぱ", "ぅ", "ぁ", "ぃ", "ぉ", "ぇ", "ゅ", "ょ", "っ", "ゃ", "[Ω]", "[←]", "[↓]", "木", "[MB2]", "無", "現", "実", "[circle]", "[cross]", "[#]", "[⋯]", "不", "止", "彩", "[\\[]", "父", "集", "院", "一", "二", "三", "四", "五", "六", "七", "八", "陽", "十", "百", "千", "万", "脳", "上", "下", "左", "右", "手", "足", "日", "目", "月", "[\\]]", "[<]", "人", "入", "出", "山", "口", "光", "電", "気", "助", "科", "次", "名", "前", "学", "校", "省", "祐", "室", "世", "界", "燃", "朗", "枚", "島", "悪", "路", "闇", "大", "小", "中", "自", "分", "間", "系", "花", "問", "[>]", "[$]", "城", "王", "兄", "化", "行", "街", "屋", "水", "見", "終", "丁", "桜", "先", "生", "長", "今", "了", "点", "井", "子", "言", "太", "属", "風", "会", "性", "持", "時", "勝", "赤", "年", "火", "改", "計", "画", "体", "波", "回", "外", "地", "正", "造", "値", "合", "戦", "川", "秋", "原", "町", "所", "用", "金", "郎", "作", "数", "方", "社", "攻", "撃", "力", "同", "武", "何", "発", "少", "以", "白", "早", "暮", "面", "組", "後", "文", "字", "本", "階", "明", "才", "者", "立", "々", "ヶ", "連", "射", "綾", "切", "土", "炎", "伊"]

charset_jp = [" ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", "サ", "シ", "ス", "セ", "ソ", "タ", "チ", "ツ", "テ", "ト", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ", "ヘ", "ホ", "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ", "ル", "レ", "ロ", "ワ", "熱", "斗", "ヲ", "ン", "ガ", "ギ", "グ", "ゲ", "ゴ", "ザ", "ジ", "ズ", "ゼ", "ゾ", "ダ", "ヂ", "ヅ", "デ", "ド", "バ", "ビ", "ブ", "ベ", "ボ", "パ", "ピ", "プ", "ペ", "ポ", "ァ", "ィ", "ゥ", "ェ", "ォ", "ッ", "ャ", "ュ", "ョ", "ヴ", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "*", "-", "×", "=", ":", "%", "?", "+", "÷", "�", "ー", "!", "現", "実", "&", "、", "。", ".", "・", ";", "’", "\"", "~", "/", "(", ")", "「", "」", "V2", "V3", "V4", "V5", "_", "[z]", "周", "あ", "い", "う", "え", "お", "か", "き", "く", "け", "こ", "さ", "し", "す", "せ", "そ", "た", "ち", "つ", "て", "と", "な", "に", "ぬ", "ね", "の", "は", "ひ", "ふ", "へ", "ほ", "ま", "み", "む", "め", "も", "や", "ゆ", "よ", "ら", "り", "る", "れ", "ろ", "わ", "研", "究", "を", "ん", "が", "ぎ", "ぐ", "げ", "ご", "ざ", "じ", "ず", "ぜ", "ぞ", "だ", "ぢ", "づ", "で", "ど", "ば", "び", "ぶ", "べ", "ぼ", "ぱ", "ぴ", "ぷ", "ぺ", "ぽ", "ぁ", "ぃ", "ぅ", "ぇ", "ぉ", "っ", "ゃ", "ゅ", "ょ", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "容", "量", "内", "木", "[MB]", "無", "嵐", "[square]", "[circle]", "[cross]", "駅", "客", "不", "止", "彩", "起", "父", "集", "院", "一", "二", "三", "四", "五", "六", "七", "八", "陽", "十", "百", "千", "万", "脳", "上", "下", "左", "右", "手", "足", "日", "目", "月", "高", "各", "人", "入", "出", "山", "口", "光", "電", "気", "♯", "科", "$", "名", "前", "学", "校", "省", "¥", "室", "世", "界", "約", "朗", "枚", "女", "男", "路", "束", "大", "小", "中", "自", "分", "間", "村", "予", "問", "異", "門", "決", "定", "兄", "帯", "道", "行", "街", "屋", "水", "見", "終", "丁", "週", "先", "生", "長", "今", "了", "点", "緑", "子", "言", "太", "属", "風", "会", "性", "持", "時", "勝", "赤", "毎", "年", "火", "改", "計", "画", "休", "体", "波", "回", "外", "地", "病", "正", "造", "値", "合", "戦", "敗", "秋", "原", "町", "所", "用", "金", "習", "作", "数", "方", "社", "攻", "撃", "力", "同", "武", "何", "発", "少", "■", "以", "白", "早", "暮", "面", "組", "後", "文", "字", "本", "階", "明", "才", "者", "立", "泉", "々", "ヶ", "連", "射", "国", "綾", "切", "土", "炎", "伊"]


def dump_simple_text_script(f, offset, charset, num_scripts):
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

def dump_description_text_script(f, offset, charset, num_scripts):
    f.seek(offset)

    script_offsets = []

    for i in range(num_scripts):
        script_offsets.append(struct.unpack("<H", f.read(2))[0])

    text_scripts = []

    for script_offset in script_offsets:
        print(f"script_offset: 0x{script_offset:02x}")
        f.seek(offset + script_offset + 7)
        cur_text_script = ""
        while True:
            try:
                cur_byte = ord(f.read(1))
            except:
                print(f"len(text_scripts): {len(text_scripts)}")
                break
                #raise RuntimeError(f"len(text_scripts): {len(text_scripts)}")
            print(f"cur_byte: {cur_byte}, f.tell(): {f.tell():07x}")
            # keywait
            if cur_byte in (0xe5, 0xe6):
                break
            # newline
            if cur_byte == 0xe8:
                if charset is charset_us:
                    cur_text_script += " "
            else:
                cur_text_script += charset[cur_byte]

        print(f"cur_text_script: {cur_text_script}")
        text_scripts.append(cur_text_script)

    return text_scripts

all_chip_codes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ*"

chip_library_id_to_name = {
    0: "Standard",
    1: "Mega",
    2: "Giga"
}

CHIP_DATA_OFFSET = 0x1af0c
CHIP_DESCRIPTIONS_POINTERS_OFFSET = 0x2165c
CHIP_NAMES_POINTERS_OFFSET = 0x3cb98
NUM_CHIPS = 389

def read_ptr_as_file_offset(f, offset):
    f.seek(offset)
    return struct.unpack("<I", f.read(4))[0] - 0x8000000

class ChipReader:
    __slots__ = ("f", "chip_id")

    def __init__(self, f):
        self.f = f

    def set_chip_id(self, chip_id):
        self.chip_id = chip_id

    def read_byte(self, offset):
        self.f.seek(CHIP_DATA_OFFSET + self.chip_id * 0x2c + offset)
        return ord(self.f.read(1))

    def read_hword(self, offset):
        self.f.seek(CHIP_DATA_OFFSET + self.chip_id * 0x2c + offset)
        return struct.unpack("<H", self.f.read(2))[0]

    def read_word(self, offset):
        self.f.seek(CHIP_DATA_OFFSET + self.chip_id * 0x2c + offset)
        return struct.unpack("<I", self.f.read(4))[0]

    def read_ptr_as_file_offset(self, offset):
        return read_ptr_as_file_offset(self.f, CHIP_DATA_OFFSET + self.chip_id * 0x2c + offset)

class ChipSeries:
    __slots__ = ("name", "is_series")

    def __init__(self, name, is_series):
        self.name = name
        self.is_series = is_series

missing_series = ChipSeries("<MISSINGCHIPSERIES>", False)
elem_names = ("Fire", "Aqua", "Elec", "Wood", "Recovery", "Plus", "Sword", "Invisible", "Ground", "Summon", "Wind", "Break", "Null")

def main():
    with open("exe45_us_pvp.gba", "rb") as f:
        chip_names_pt1_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET)
        chip_names_pt2_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET + 4)
        chip_descs_pt1_ptr = read_ptr_as_file_offset(f, CHIP_DESCRIPTIONS_POINTERS_OFFSET)
        chip_descs_pt2_ptr = read_ptr_as_file_offset(f, CHIP_DESCRIPTIONS_POINTERS_OFFSET + 4)

        chip_names_pt1 = dump_simple_text_script(f, chip_names_pt1_ptr, charset_us, 256)
        chip_names_pt2 = dump_simple_text_script(f, chip_names_pt2_ptr, charset_us, NUM_CHIPS - 256)
        chip_descs_pt1 = dump_description_text_script(f, chip_descs_pt1_ptr, charset_us, 256)
        chip_descs_pt2 = dump_description_text_script(f, chip_descs_pt2_ptr, charset_us, NUM_CHIPS - 256)

    chip_names_us = chip_names_pt1 + chip_names_pt2
    chip_descs_us = chip_descs_pt1 + chip_descs_pt2

    with open("exe45_pvp.gba", "rb") as f:
        chip_names_pt1_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET)
        chip_names_pt2_ptr = read_ptr_as_file_offset(f, CHIP_NAMES_POINTERS_OFFSET + 4)
        chip_descs_pt1_ptr = read_ptr_as_file_offset(f, CHIP_DESCRIPTIONS_POINTERS_OFFSET)
        chip_descs_pt2_ptr = read_ptr_as_file_offset(f, CHIP_DESCRIPTIONS_POINTERS_OFFSET + 4)

        chip_names_pt1 = dump_simple_text_script(f, chip_names_pt1_ptr, charset_jp, 256)
        chip_names_pt2 = dump_simple_text_script(f, chip_names_pt2_ptr, charset_jp, NUM_CHIPS - 256)
        chip_descs_pt1 = dump_description_text_script(f, chip_descs_pt1_ptr, charset_jp, 256)
        chip_descs_pt2 = dump_description_text_script(f, chip_descs_pt2_ptr, charset_jp, NUM_CHIPS - 256)

    chip_names_jp = chip_names_pt1 + chip_names_pt2
    chip_descs_jp = chip_descs_pt1 + chip_descs_pt2

    output = ""
    #with open("exe45_chips_template.json", "r") as f:
    #    exe45_chips = json.load(f)

    #manual_chips = {
    #    "Cannon": 1,
    #    "LifeAura": 201,
    #    "FinalGun": 290,
    #    "Bass": 301
    #}

    #for manual_chip_name, manual_chip_id in manual_chips.items():
    #    exe45_chips[manual_chip_name]["id"] = manual_chip_id
    #
    #for i, chip_name in enumerate(chip_names):
    #    if chip_name in exe45_chips and chip_name not in manual_chips:
    #        exe45_chips[chip_name]["id"] = i

    chip_infos = {}

    with open("bn4_chip_full_names.txt", "r") as f:
        bn4_chip_full_names_as_str = f.read().strip()

    bn4_chip_full_names = {line.split(maxsplit=1)[0]: line.split(maxsplit=1)[1].strip() for line in bn4_chip_full_names_as_str.splitlines()}

    with open("bn4_wiki_series.txt", "r") as f:
        bn4_wiki_series_as_str = f.read().strip()

    bn4_wiki_series = {}
    for line in bn4_wiki_series_as_str.splitlines():
        split_line = line.split(": ", maxsplit=1)
        is_series = len(split_line) == 2
        series_name = split_line[0]
        series = ChipSeries(series_name, is_series)
        bn4_wiki_series[series_name] = series
        for i in range(1, 4):
            bn4_wiki_series[f"{series_name} {i}"] = series

        bn4_wiki_series[f"{series_name} SP"] = series
        bn4_wiki_series[f"{series_name} DS"] = series
        bn4_wiki_series[f"{series_name} EX"] = series

    all_chip_infos = []

    with open("exe45_us_pvp.gba", "rb") as f:
        chip_reader = ChipReader(f)
        for chip_id, (chip_name_us, chip_desc_us, chip_name_jp, chip_desc_jp) in enumerate(zip(chip_names_us, chip_descs_us, chip_names_jp, chip_descs_jp)):
            chip_reader.set_chip_id(chip_id)
            chip_library_as_num = chip_reader.read_byte(0x8)
            chip_effect_flags = chip_reader.read_byte(0x9)
            if chip_library_as_num in (0, 1, 2, 4) and chip_effect_flags & 0x40 != 0:
                #{{Infobox chip
                #|gamenumber=4.5PVP
                #|internalid=1
                #|sortorder=1
                #|name=Cannon
                #|fullname=Cannon
                #|series=Cannon
                #|description=Cannon to attack 1 enemy
                #|class=Standard
                #|librarysection=Standard
                #|gamevariant=
                #|karmarequirement=
                #|number=1
                #|element=Null
                #|damage=40
                #|mb=8
                #|codes=A,B,C,*
                #|delay=0
                #|name_ja=キャノン
                #|description_ja=前方のてき1たいを攻撃できるキャノンほう
                #}}

                #{{Infobox program advance
                #|gamenumber=4
                #|internalid=323
                #|sortorder=301
                #|name=GigaCan1
                #|fullname=Giga Cannon 1
                #|series=Giga Cannon
                #|description=A cannon driven by GigaPower
                #|number=1
                #|delay=0
                #|damage=300
                #|chips=Cannon A,Cannon B,Cannon C
                #|name_ja=ギガキャノン1
                #|description_ja=ギガパワーではなつきょうりょくなキャノン!
                #}}

                chip_name = chip_name_us
                full_name = bn4_chip_full_names.get(chip_name_us, "<MISSINGFULLNAME>")
                series = bn4_wiki_series.get(full_name, missing_series)
                series_name = series.name
                description = chip_desc_us
                sort_order = chip_reader.read_hword(0x1c)
                if sort_order <= 218:
                    library_number = sort_order
                elif 219 <= sort_order <= 279:
                    library_number = sort_order - 218
                elif 280 <= sort_order <= 292:
                    library_number = sort_order - 279
                elif 293 <= sort_order <= 323:
                    library_number = sort_order - 292
                else:
                    raise RuntimeError(f"Unknown libnum for chip {chip_name_us}! sort_order: {sort_order}")

                delay_frames = chip_reader.read_byte(0x14)
                damage = chip_reader.read_hword(0x1a)

                #|class=Standard
                #|librarysection=Standard
                #|gamevariant=
                #|karmarequirement=
                #|number=1
                #|element=Null
                #|damage=40
                #|mb=8
                #|codes=A,B,C,*

                chip_info = {
                    "gamenumber": "4.5PVP",
                    "internalid": chip_id,
                    "sortorder": sort_order,
                    "name": chip_name_us,
                    "fullname": full_name,
                    "series": series_name,
                    "description": description,
                    "number": library_number,
                    "delay": delay_frames,
                    "damage": damage,
                    "name_ja": chip_name_jp,
                    "description_ja": chip_desc_jp
                }

                if chip_library_as_num != 4:
                    chip_class = chip_library_id_to_name[chip_library_as_num]
                    library_section = chip_class
                    element = elem_names[chip_reader.read_byte(0x7)]
                    mb = chip_reader.read_byte(0x6)
                    chip_codes = []
                    for i in range(4):
                        chip_code_as_num = chip_reader.read_byte(i)
                        if chip_code_as_num == 0xff:
                            break
                        chip_codes.append(all_chip_codes[chip_code_as_num])
    
                    chip_codes_as_str = ",".join(chip_codes)
                    chip_info.update({
                        "class": chip_class,
                        "librarysection": library_section,
                        "gamevariant": "",
                        "karmarequirement": "",
                        "element": element,
                        "mb": mb,
                        "codes": chip_codes_as_str
                    })
                else:
                    chip_info.update({
                        "chips": "<MISSINGPACHIPS>"
                    })

                all_chip_infos.append(chip_info)

    with open("exe45_pvp_wiki_chips.json", "w+") as f:
        json.dump(all_chip_infos, f, indent=2)

if __name__ == "__main__":
    main()
