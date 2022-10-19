# =============================================================================
# MIT License
# 
# Copyright (c) 2022 luckytyphlosion
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

import difflib
import pathlib
import json
import collections
import platform
import os
import sys
import struct
import itertools
import errno

MASK_OFFSET = 0x3c84
GAME_NAME_OFFSET = 0x4ba8
CHECKSUM_OFFSET = 0x4b88
REG_STRUCTURE_OFFSET = 0x8530
SAVE_SIZE = 0xc7a8
FOLDER_OFFSET = 0x7500

class ErrorMsg:
    __slots__ = ("message", "line_num")

    def __init__(self, message, line_num):
        self.message = message
        self.line_num = line_num

def get_platform():
    if platform.system() == "Windows":
        return "Windows"
    elif platform.system() == "Darwin":
        return "Darwin"
    elif platform.system() == "Linux":
        if "microsoft" in platform.uname()[3].lower():
            raise RuntimeError("Folder editor is not supported with WSL!")
        else:
            return "Linux"
    else:
        return None

def get_tango_config_filepath():
    user_platform = get_platform()
    if user_platform is None:
        raise RuntimeError("Unknown platform!")

    if user_platform == "Windows":
        appdata_roaming_dirname = os.getenv("APPDATA")
        tango_config_dirpath = pathlib.Path(f"{appdata_roaming_dirname}/Tango/config")
    elif user_platform == "Darwin":
        tango_config_dirpath = pathlib.Path.home() / pathlib.Path("Library/Application Support/Tango")
    elif user_platform == "Linux":
        linux_home_pathname = os.getenv("XDG_DATA_HOME")
        if linux_home_pathname is not None:
            tango_config_dirpath = pathlib.Path(linux_home_pathname) / pathlib.Path("Tango")
        else:
            tango_config_dirpath = pathlib.Path.home() / pathlib.Path(".config/Tango")

    tango_config_filepath = tango_config_dirpath / "config.json"
    return tango_config_filepath

# Taken from https://github.com/jamesturk/jellyfish
# License provided below
# ================================================================================
# Copyright (c) 2015, James Turk
# Copyright (c) 2015, Sunlight Foundation
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ================================================================================
def _check_type(s):
    if not isinstance(s, str):
        raise TypeError("expected str or unicode, got %s" % type(s).__name__)

def damerau_levenshtein_distance(s1, s2):
    _check_type(s1)
    _check_type(s2)

    len1 = len(s1)
    len2 = len(s2)
    infinite = len1 + len2

    # character array
    da = collections.defaultdict(int)

    # distance matrix
    score = [[0] * (len2 + 2) for x in range(len1 + 2)]

    score[0][0] = infinite
    for i in range(0, len1 + 1):
        score[i + 1][0] = infinite
        score[i + 1][1] = i
    for i in range(0, len2 + 1):
        score[0][i + 1] = infinite
        score[1][i + 1] = i

    for i in range(1, len1 + 1):
        db = 0
        for j in range(1, len2 + 1):
            i1 = da[s2[j - 1]]
            j1 = db
            cost = 1
            if s1[i - 1] == s2[j - 1]:
                cost = 0
                db = j

            score[i + 1][j + 1] = min(
                score[i][j] + cost,
                score[i + 1][j] + 1,
                score[i][j + 1] + 1,
                score[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1),
            )
        da[s1[i - 1]] = i

    return score[len1 + 1][len2 + 1]

# Taken from https://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_7
def lcs_length(a, b):
    # generate matrix of length of longest common subsequence for substrings of both words
    lengths = [[0] * (len(b)+1) for _ in range(len(a)+1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])

    # read a substring from the matrix
    result = ''
    j = len(b)
    for i in range(1, len(a)+1):
        if lengths[i][j] != lengths[i-1][j]:
            result += a[i-1]

    return len(result)

def get_most_similar_from_dict_lcs(unknown_name, all_names, chip_code_tiebreak=None, exe45_chips_uncased=None):
    most_similar_names = []
    most_similar_distance = 0

    for cur_name in all_names.keys():
        cur_distance = lcs_length(unknown_name, cur_name)
        if cur_distance > most_similar_distance:
            most_similar_distance = cur_distance
            most_similar_names = [cur_name]
        elif cur_distance == most_similar_distance:
            most_similar_names.append(cur_name)

    possible_most_similar_name_shortest_len = min(len(most_similar_name) for most_similar_name in most_similar_names)
    unknown_name_len = len(unknown_name)

    min_len = min(unknown_name_len, possible_most_similar_name_shortest_len)
    min_len_minus_most_similar_distance = min_len - most_similar_distance
    # some metric
    # maybe will explain later
    if min_len <= 4 and min_len_minus_most_similar_distance > 1 or min_len > 4 and min_len_minus_most_similar_distance > 2:
        return None, (most_similar_distance, min_len_minus_most_similar_distance)
    else:
        if len(most_similar_names) == 1:
            most_similar_name = most_similar_names[0]
        else:
            # tiebreak somehow
            # pick the name with the least number of characters that do not appear in the unknown name
            print(f"most_similar_names: {most_similar_names}")
            unknown_name_chars = set(unknown_name)
            most_similar_names_round_2 = []
            most_similar_name_num_uncommon_chars = 100

            for most_similar_name_candidate in most_similar_names:
                cur_similar_name_num_uncommon_chars = len(set(most_similar_name_candidate) - unknown_name_chars)
                print(f"cur_similar_name_num_uncommon_chars: {cur_similar_name_num_uncommon_chars}")
                if cur_similar_name_num_uncommon_chars < most_similar_name_num_uncommon_chars:
                    most_similar_names_round_2 = [most_similar_name_candidate]
                    most_similar_name_num_uncommon_chars = cur_similar_name_num_uncommon_chars
                elif cur_similar_name_num_uncommon_chars == most_similar_name_num_uncommon_chars:
                    most_similar_names_round_2.append(most_similar_name_candidate)

            if len(most_similar_names_round_2) != 1 and chip_code_tiebreak is not None:
                most_similar_names_round_3 = []
                for most_similar_name_candidate in most_similar_names_round_2:
                    if chip_code_tiebreak in exe45_chips_uncased[most_similar_name_candidate]["codes"]:
                        most_similar_names_round_3.append(most_similar_name_candidate)

                if len(most_similar_names_round_3) != 0:
                    most_similar_names_round_2 = most_similar_names_round_3

            most_similar_name = most_similar_names_round_2[0]

            min_len = min(unknown_name_len, len(most_similar_name))
            min_len_minus_most_similar_distance = min_len - most_similar_distance

        return most_similar_name, (most_similar_distance, min_len_minus_most_similar_distance)

def get_most_similar_from_dict_damerau_levenshtein(unknown_name, all_names):
    most_similar_name = None
    most_similar_distance = 100000

    for cur_name in all_names.keys():
        cur_distance = damerau_levenshtein_distance(unknown_name, cur_name)
        if cur_distance < most_similar_distance:
            most_similar_distance = cur_distance
            most_similar_name = cur_name

    if most_similar_distance > 16:
        return None, most_similar_distance
    else:
        return most_similar_name, most_similar_distance

#def get_most_similar_from_dict_lcs_and_damerau_levenshtein(unknown_name, all_names):
#    most_similar_name = None
#    most_similar_lcs = 0
#    most_similar_dl = 100000
#
#    for cur_name in all_names.keys():
#        cur_lcs = lcs_length(unknown_name, cur_name)
#        if cur_lcs > most_similar_lcs:
#            most_similar_lcs = cur_lcs
#            most_similar_name = cur_name
#
#    # if the 
#    if len(most_similar_name) 
#        if cur_lcs_len
#        cur_dl = damerau_levenshtein_distance(unknown_name, cur_name)
#        # max 3 insertions, deletions, substitutions
#        if cur_dl > 3:
#            
#        
#        if cur_distance > most_similar_distance:
#            most_similar_distance = cur_distance
#            most_similar_name = cur_name
#
#    if most_similar_distance == 0:
#        return None, 0
#    else:
#        return most_similar_name, most_similar_distance

def get_most_similar_from_dict(unknown_name, all_names):
    sequence_matcher = difflib.SequenceMatcher(isjunk=None, a=unknown_name)
    most_similar_name = None
    most_similar_ratio = 0

    for cur_name in all_names.keys():
        sequence_matcher.set_seq2(cur_name)
        cur_ratio = sequence_matcher.ratio()
        if cur_ratio > most_similar_ratio:
            most_similar_ratio = cur_ratio
            most_similar_name = cur_name

    if most_similar_ratio == 0:
        return None, 0
    else:
        return most_similar_name, most_similar_ratio

all_chip_codes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ*"
all_chip_codes_set = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ*".casefold())

def edit_folder_chip(save_data, navi_id, chip_slot, chip_info, chip_code):
    chip_code_as_num = 26 if chip_code == "*" else ord(chip_code.casefold()) - ord("a")
    if chip_code_as_num > 26 or chip_code_as_num < 0:
        raise RuntimeError()
    chip_and_code_packed = struct.pack("<H", chip_info["id"] | chip_code_as_num << 9)

    folder_chip_base_offset = FOLDER_OFFSET + (30 * 2) * navi_id + chip_slot * 2
    save_data[folder_chip_base_offset:folder_chip_base_offset+2] = chip_and_code_packed

def get_folder_chip(save_data, navi_id, chip_slot, chip_ids_to_chip_names):
    folder_chip_base_offset = FOLDER_OFFSET + (30 * 2) * navi_id + chip_slot * 2

    chip_and_code_packed = struct.unpack("<H", save_data[folder_chip_base_offset:folder_chip_base_offset+2])[0]
    chip_id = chip_and_code_packed & 0x1ff
    chip_code_as_num = chip_and_code_packed >> 9

    chip_name = chip_ids_to_chip_names.get(chip_id, f"BdChp{chip_id:03X}")
    if chip_code_as_num < 0 or chip_code_as_num > 26:
        print(f"Invalid chip code detected for navi {navi_id} at chip slot {chip_slot} (0-in)!")
        chip_code = f"Code_0x{chip_code_as_num:x}"
    else:
        chip_code = all_chip_codes[chip_code_as_num]
    return chip_name, chip_code

def edit_reg(save_data, navi_id, chip_slot):
    save_data[REG_STRUCTURE_OFFSET + 0x40 * navi_id + 0x2f] = chip_slot

def get_reg(save_data, navi_id):
    return save_data[REG_STRUCTURE_OFFSET + 0x40 * navi_id + 0x2f]

def mask_save(save_data):
    mask = save_data[MASK_OFFSET:MASK_OFFSET+4]
    mask_first_byte = mask[0]

    # "We only actually need to use the first byte of the mask, even though it's 32 bits long."
    for i in range(SAVE_SIZE):
        save_data[i] ^= mask_first_byte

    save_data[MASK_OFFSET:MASK_OFFSET+4] = mask

def is_correct_savegame(save_data):
    game_str = save_data[GAME_NAME_OFFSET:GAME_NAME_OFFSET+20]
    return game_str in (bytearray(b"ROCKMANEXE4RO 040607"), bytearray(b"ROCKMANEXE4RO 041217"))

def calc_checksum_and_expected_checksum(save_data):
    checksum = 0

    for byte in itertools.islice(save_data, SAVE_SIZE):
        checksum = (checksum + byte) & 0xffffffff

    expected_checksum = struct.unpack("<I", save_data[CHECKSUM_OFFSET:CHECKSUM_OFFSET+4])[0]
    for i in range(4):
        checksum = (checksum - save_data[CHECKSUM_OFFSET+i]) & 0xffffffff

    checksum = (checksum + 0x38) & 0xffffffff

    return checksum, expected_checksum

def read_save_from_file(save_filename, wrong_save_error_message, wrong_checksum_error_message):
    with open(save_filename, "rb") as f:
        save_data = bytearray(f.read())

    mask_save(save_data)
    if not is_correct_savegame(save_data):
        error_pause_and_exit(f"{wrong_save_error_message} Got \"{game_str}\".")

    checksum, expected_checksum = calc_checksum_and_expected_checksum(save_data)

    if checksum != expected_checksum:
        error_pause_and_exit(f"{wrong_checksum_error_message} Expected: 0x{expected_checksum:08x}, Actual: 0x{checksum:08x}.")

    return save_data

def write_save_to_file(save_data, save_filepath):
    checksum, expected_checksum = calc_checksum_and_expected_checksum(save_data)
    save_data[CHECKSUM_OFFSET:CHECKSUM_OFFSET+4] = struct.pack("<I", checksum)

    mask_save(save_data)
    try:
        with open(save_filepath, "wb+") as f:
            f.write(save_data)
    except OSError as e:
        if e.errno == errno.EINVAL:
            print(f"Cannot write to {save_filepath}, try closing any emulators/programs using the save.")

def error_pause_and_exit(error_msg):
    print(f"{error_msg}\n")
    #input("Press enter to exit...")
    sys.exit(1)

HELP_MESSAGE = """Don't run this program directly! This program has two modes:
- Folder to Save: Drag a text file onto the executable. with your Navi on the first line and all 30 chips on the 2nd to 31st lines. This will add the save to the Tango saves directory.
- Save to Folder: Drag a save file onto the executable. This will create a directory containing text folders for all 21 Navis."""

def extract_save_folders(save_filepath):
    save_basename = save_filepath.with_suffix("").name
    if save_basename == "data":
        error_pause_and_exit("Save cannot be named data!")

    save_data = read_save_from_file(save_filepath, "Save isn't EXE4.5!", "Save has incorrect checksum (save potentially corrupted)!")

    with open("data/navis.json", "r") as f:
        navis = json.load(f)

    with open("data/exe45_chips.json", "r") as f:
        exe45_chips = json.load(f)

    exe45_chip_ids_to_chip_names = {chip_info["id"]: chip_name for chip_name, chip_info in exe45_chips.items()}

    all_folders = {}

    for navi_name, navi in navis.items():
        cur_folder = []
        navi_id = navi["id"]
        for chip_slot in range(30):
            chip_name, chip_code = get_folder_chip(save_data, navi_id, chip_slot, exe45_chip_ids_to_chip_names)
            cur_folder.append(f"{chip_name} {chip_code}")

        reg_slot = get_reg(save_data, navi_id)
        if reg_slot != 0xff:
            if not (0 <= reg_slot < 30):
                print(f"Invalid reg slot {reg_slot} (0-in) for navi {navi_id}")
            else:
                cur_folder[reg_slot] += " [REG]"

        all_folders[navi_name] = cur_folder

    output_text_folder_dirpath = pathlib.Path(sys.argv[0]).parent / save_basename

    if not output_text_folder_dirpath.is_dir():
        print(f"Creating folder text directory at {output_text_folder_dirpath}!")
        output_text_folder_dirpath.mkdir(parents=True)

    for navi_name, folder in all_folders.items():
        output_text_folder_filepath = output_text_folder_dirpath / f"{save_filepath.stem}_{navi_name}.txt"
        print(f"Writing text folder to {output_text_folder_filepath}!")
        folder_str_output = f"{navi_name}\n" + "\n".join(folder) + "\n"
        with open(output_text_folder_filepath, "w+") as f:
            f.write(folder_str_output)

def mb_to_max_chip_count(mb):
    if 0 <= mb <= 19:
        return 5
    elif 20 <= mb <= 29:
        return 4
    elif 30 <= mb <= 39:
        return 3
    elif 40 <= mb <= 49:
        return 2
    else:
        return 1

get_most_similar_from_dict_func = get_most_similar_from_dict_lcs

def debug_str(x):
    if False:
        return x
    else:
        return ""

def is_code(code):
    return len(code) == 1 and code.casefold() in all_chip_codes_set

DEBUG = True

def convert_folder_to_save(input_folder_filepath):
    tango_config_filepath = get_tango_config_filepath()
    if not tango_config_filepath.is_file():
        error_pause_and_exit(f"Cannot find Tango config file. Make sure Tango is installed (https://tango.n1gp.net/).")

    with open(tango_config_filepath, "r") as f:
        tango_config = json.load(f)

    data_path = tango_config.get("data_path")
    if data_path is None:
        error_pause_and_exit(f"Tango is installed, but Tango data folder is missing!")

    save_data = read_save_from_file("exe45_us_pvp_template.sav", "Template save isn't EXE4.5!", "Template save has incorrect checksum (save potentially corrupted)!")

    with open(input_folder_filepath, "r") as f:
        folder_input_as_text = f.read()

    folder_input = folder_input_as_text.strip().splitlines()
    if len(folder_input) != 31:
        print("Input folder should be 31 lines long (1 line for Navi + 30 lines for chips)!")

    with open("data/navis.json", "r") as f:
        navis_cased = json.load(f)

    with open("data/exe45_chips.json", "r") as f:
        exe45_chips_cased = json.load(f)

    navis_uncased = {navi_name_uncased.casefold(): v for navi_name_uncased, v in navis_cased.items()}
    exe45_chips_uncased = {chip_name.casefold(): v for chip_name, v in exe45_chips_cased.items()}

    navi_name = folder_input[0].strip()
    navi_name_uncased = navi_name.casefold()
    navi = navis_uncased.get(navi_name_uncased)
    error_messages = collections.defaultdict(list)

    if navi is None:
        most_similar_navi_name_uncased, most_similar_navi_name_ratio = get_most_similar_from_dict_func(navi_name_uncased, navis_uncased)
        error_message_partial = f"Unknown navi {navi_name}!"
        if most_similar_navi_name_uncased is not None:
            navi = navis_uncased.get(most_similar_navi_name_uncased)
            most_similar_navi_name_cased = navis_uncased.get(most_similar_navi_name_uncased)["name"]
            error_message_partial += f" Did you mean \"{most_similar_navi_name_cased}\" or \"{most_similar_navi_name_uncased}\"?"
            if DEBUG:
                error_message_partial += f" (Ignore This: {most_similar_navi_name_ratio})"
            navi_name_cased = most_similar_navi_name_cased
            navi_name_uncased = most_similar_navi_name_uncased
        else:
            navi = navis_uncased.get("megaman")
            navi_name = "MegaMan"
            navi_name_cased = "MegaMan"
            navi_name_uncased = "megaman"
        error_messages[1].append(error_message_partial)
    else:
        # navi offset
        navi_name_cased = navi["name"]
        save_data[0x4ad1] = navi["id"]

    reg_line_num = -1
    collapsed_folder = collections.defaultdict(int)
    num_megas = 0
    num_gigas = 0

    for line_num, chip in enumerate(folder_input[1:], 2):
        is_chip_guess = False
        chip = chip.strip()

        chip_name_with_spaces = None

        chip_name_chip_code_reg = chip.split()
        if len(chip_name_chip_code_reg) == 0:
            error_messages[line_num].append("Line is empty!")
            continue
        elif len(chip_name_chip_code_reg) == 1:
            chip_name = chip
            chip_code = None
            chip_reg = ""
        elif len(chip_name_chip_code_reg) == 2:
            if not is_code(chip_name_chip_code_reg[1]):
                chip_name_with_spaces = chip
                chip_name = "".join(chip_name_chip_code_reg)
                chip_code = None
                chip_reg = ""
            else:
                chip_name, chip_code = chip_name_chip_code_reg
                chip_reg = ""
        # try to catch people using spaces in chip names
        else:
            # four cases
            # [-1] is code, that means spaces in chip name
            # [-2] is code:
            #   if len is not 3, then that means spaces in chip name + reg
            # neither is code, but [-1] contains reg, that means missing code, chip name is [0:-2]
            # neither is code, and [-1] doesn't contain reg, that means missing code, chip name is [0:-1]
            if is_code(chip_name_chip_code_reg[-1]):
                chip_name = "".join(chip_name_chip_code_reg[:-1])
                chip_code = chip_name_chip_code_reg[-1]
                chip_reg = ""
                chip_name_with_spaces = chip.rsplit(maxsplit=1)[0]
            elif is_code(chip_name_chip_code_reg[-2]):
                chip_name = "".join(chip_name_chip_code_reg[:-2])
                chip_code = chip_name_chip_code_reg[-2]
                chip_reg = chip_name_chip_code_reg[-1]
                if len(chip_name_chip_code_reg) != 3:
                    chip_name_with_spaces = chip.rsplit(maxsplit=2)[0]
            elif "reg" in chip_name_chip_code_reg[-1].lower() or any(c in chip_name_chip_code_reg[-1] for c in ("[", "]", "{", "}", "<", ">", "(", ")")):
                chip_name = "".join(chip_name_chip_code_reg[:-1])
                chip_code = None
                chip_reg = chip_name_chip_code_reg[-1]
                chip_name_with_spaces = chip.rsplit(maxsplit=1)[0]
            else:
                chip_name = "".join(chip_name_chip_code_reg)
                chip_code = None
                chip_reg = ""
                chip_name_with_spaces = chip

        if chip_name_with_spaces is not None:
            error_messages[line_num].append(f"Spaces detected in chip name \"{chip_name_with_spaces}\"!")

        if chip_code is None:
            error_messages[line_num].append(f"Chip \"{chip_name_with_spaces if chip_name_with_spaces is not None else chip_name}\" has missing code!")

        chip_name_uncased = chip_name.casefold()

        chip_info = exe45_chips_uncased.get(chip_name_uncased)

        if chip_info is None:
            is_chip_guess = True
            most_similar_chip_name_uncased, most_similar_navi_name_ratio = get_most_similar_from_dict_func(chip_name_uncased, exe45_chips_uncased, chip_code_tiebreak=chip_code, exe45_chips_uncased=exe45_chips_uncased)
            error_message_partial = f"Unknown chip {chip_name}!"
            if most_similar_chip_name_uncased is not None:
                chip_info = exe45_chips_uncased.get(most_similar_chip_name_uncased)
                most_similar_chip_name_cased = chip_info["name"]
                error_message_partial += f" Did you mean \"{most_similar_chip_name_cased}\" or \"{most_similar_chip_name_uncased}\"?"
                if DEBUG:
                    error_message_partial += f" (Ignore This: {most_similar_navi_name_ratio})"
                chip_name_cased = most_similar_chip_name_cased
                chip_name_uncased = most_similar_chip_name_uncased
            else:
                chip_name_cased = chip_name

            error_messages[line_num].append(error_message_partial)
        else:
            chip_name_cased = chip_info["name"]

        if chip_code is not None and chip_info is not None:
            if chip_code.upper() not in chip_info["codes"]:
                error_messages[line_num].append(f"{chip_name_cased} does not come in code {chip_code}!")

        if chip_reg != "":
            if chip_reg.casefold() != "[reg]":
                error_messages[line_num].append(f"Unknown text \"{chip_reg}\" after chip! (Add [REG] after a chip to select a reg)")
            elif reg_line_num != -1:
                error_messages[line_num].append(f"Reg already set on line {reg_line_num}!")
            else:
                reg_line_num = line_num
                if chip_info is not None:
                    if chip_info["mb"] > navi["mb"]:
                        error_messages[line_num].append(f"{chip_name_cased} ({chip_info['mb']}MB) exceeds {navi_name_cased}'s reg capacity ({navi['mb']}MB)!")
                    else:
                        edit_reg(save_data, navi["id"], reg_line_num - 2)

        if chip_info is not None:
            collapsed_folder[chip_name_uncased] += 1
            if chip_info["library"] == "Mega":
                num_megas += 1
            elif chip_info["library"] == "Giga":
                num_gigas += 1

        if error_messages.get(line_num) is None:
            edit_folder_chip(save_data, navi["id"], line_num - 2, chip_info, chip_code)

    if reg_line_num == -1:
        edit_reg(save_data, navi["id"], 0xff)

    folder_error_message = ""

    if len(error_messages) != 0:
        folder_error_message += "Provided folder has errors:\n\n"
        for line_num, error_messages_for_line in error_messages.items():
            if len(error_messages_for_line) != 0:
                folder_error_message += f"At line {line_num}:"
                if len(error_messages_for_line) == 1:
                    folder_error_message += f" {error_messages_for_line[0]}\n"
                else:
                    folder_error_message += "\n" + "".join(f"    {error_message}\n" for error_message in error_messages_for_line)

    for chip_name_uncased, chip_count in collapsed_folder.items():
        chip_info = exe45_chips_uncased.get(chip_name_uncased)
        chip_mb = chip_info["mb"]
        max_chip_count = mb_to_max_chip_count(chip_mb)
        if chip_count > max_chip_count:
            folder_error_message += f"{chip_info['name']} ({chip_mb}MB) exceeds maximum allowed count of {max_chip_count}! (Folder has {chip_count})\n"

    if num_megas > navi["megafolder"]:
        folder_error_message += f"Folder exceeds {navi_name_cased}'s Mega Chip capacity of {navi['megafolder']}! (Folder has {num_megas})\n"

    if num_gigas > navi["gigafolder"]:
        folder_error_message += f"Folder exceeds {navi_name_cased}'s Giga Chip capacity of {navi['gigafolder']}! (Folder has {num_gigas})\n"

    if folder_error_message != "":
        error_pause_and_exit(folder_error_message)

    saves_dirpath = pathlib.Path(data_path) / pathlib.Path("saves")

    if not saves_dirpath.is_dir():
        print("Creating Tango saves directory!")
        saves_dirpath.mkdir(parents=True)

    save_filepath = saves_dirpath / input_folder_filepath.with_suffix(".sav").name
    write_save_to_file(save_data, save_filepath)

    print(f"Successfully wrote save to {save_filepath}")

def main():
    #ap = configargparse.ArgumentParser(
    #    allow_abbrev=False,
    #    config_file_parser_class=configargparse.YAMLConfigFileParser,
    #    config_file_open_func=lambda filename: open(
    #        filename, "r", encoding="utf-8"
    #    )
    #)
    #
    #ap.add_argument("-cfg", "--config", dest="config", default=None, is_config_file=True, help="Alternative config file to put in command line arguments. Arguments provided on the command line will override arguments provided in the config file, if specified.")
    #ap.add_argument("-i", "--input-folder-filename", dest="input_folder_filename", help="Folder filename", default=None)
    ##ap.add_argument("-o", "--output-save-filename", dest="output_save_filename", help="Output save filename", required=True)
    #args = ap.parse_args()

    if len(sys.argv) == 1:
        error_pause_and_exit(HELP_MESSAGE)

    input_folder_or_save_filename = sys.argv[1]
    input_folder_or_save_filepath = pathlib.Path(input_folder_or_save_filename)
    input_suffix = input_folder_or_save_filepath.suffix.casefold()
    input_is_save = input_suffix in (".sav", ".saveram")

    if not input_folder_or_save_filepath.is_file():
        if input_is_save:
            error_pause_and_exit(f"Provided save \"{input_folder_or_save_filename}\" does not exist!")
        else:
            error_pause_and_exit(f"Provided folder \"{input_folder_or_save_filename}\" does not exist!")            

    if input_is_save:
        extract_save_folders(input_folder_or_save_filepath)
    else:
        convert_folder_to_save(input_folder_or_save_filepath)

    print("Done!")

if __name__ == "__main__":
    main()
