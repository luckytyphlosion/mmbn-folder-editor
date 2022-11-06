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

import glob
import subprocess
import pathlib
import shutil
import json
import collections
import struct

MASK_OFFSET = 0x3c84
GAME_NAME_OFFSET = 0x4ba8
CHECKSUM_OFFSET = 0x4b88
REG_STRUCTURE_OFFSET = 0x8530
SAVE_SIZE = 0xc7a8
FOLDER_OFFSET = 0x7500

def extract_wrams():
    for replay_filename in glob.glob("done_replays/*.tangoreplay"):
        replay_wram = subprocess.check_output(("C:/Users/User/AppData/Local/Programs/Tango/tango.exe", replay_filename, "wram"))
        wram_filename = f"replaywram/{pathlib.Path(replay_filename).stem}.bin"
        with open(wram_filename, "wb+") as f:
            f.write(replay_wram)

        print(f"Done {replay_filename}!")

def fix_wram_names():
    for wram_filename in glob.glob("replaywram/*.bin"):
        fixed_wram_filename = wram_filename.replace(".tangoreplay", "")
        shutil.move(wram_filename, fixed_wram_filename)
        print(f"Renamed {wram_filename}!")

def extract_wrams_opponent():
    for replay_filename in glob.glob("done_replays/*.tangoreplay"):
        invert_filename = f"inverted_replays/{pathlib.Path(replay_filename).stem}_opp.tangoreplay"
        subprocess.run(("C:/Users/User/AppData/Local/Programs/Tango/tango.exe", replay_filename, "invert", invert_filename), check=True)
        invert_replay_wram = subprocess.check_output(("C:/Users/User/AppData/Local/Programs/Tango/tango.exe", invert_filename, "wram"))
        invert_wram_filename = f"replaywram/{pathlib.Path(replay_filename).stem}_opp.bin"
        with open(invert_wram_filename, "wb+") as f:
            f.write(invert_replay_wram)

        print(f"Done {replay_filename} invert!")

def extract_metadatas():
    for replay_filename in glob.glob("done_replays/*.tangoreplay") + glob.glob("inverted_replays/*.tangoreplay"):
        metadata = subprocess.check_output(("C:/Users/User/AppData/Local/Programs/Tango/tango.exe", replay_filename, "metadata")).decode("utf-8")
        metadata_filename = f"metadata/{pathlib.Path(replay_filename).stem}.json"
        with open(metadata_filename, "w+") as f:
            f.write(metadata)

        print(f"Done {replay_filename} metadata!")

all_chip_codes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ*"

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
    return chip_name, chip_code, chip_id, chip_code_as_num

def get_reg(save_data, navi_id):
    return save_data[REG_STRUCTURE_OFFSET + 0x40 * navi_id + 0x2f]

def dump_raw_stats_as_json():
    with open("data/exe45_chips.json", "r") as f:
        exe45_chips = json.load(f)

    with open("data/navis.json", "r") as f:
        navis = json.load(f)

    exe45_chip_ids_to_chip_names = {chip_info["id"]: chip_name for chip_name, chip_info in exe45_chips.items()}
    exe45_navi_ids_to_navis = {navi["id"]: navi for navi in navis.values()}
    all_folder_info = {}

    for wram_filename in glob.glob("replaywram/*.bin"):
        wram_filestem = pathlib.Path(wram_filename).stem
        print(f"Extracting {wram_filename}!")
        with open(wram_filename, "rb") as f, open(f"metadata/{wram_filestem}.json", "r") as f2:
            cur_metadata = json.load(f2)
            patch = cur_metadata["local_side"]["game_info"]["patch"]
            if patch["name"] not in ("exe45_pvp", "bn45_us_pvp"):
                raise RuntimeError(f"Unknown patch {patch['name']} for {wram_filename}!")
            version = patch["version"]

            #if local_side is None:
            #    raise RuntimeError(f"Error for {wram_filename}! local_side is None!")

            wram_data = bytearray(f.read())
            navi_id = wram_data[0x4ad1]
            cur_folder_info = {}
            cur_folder_info["ts"] = cur_metadata["ts"]
            cur_folder_info["version"] = version
            navi = exe45_navi_ids_to_navis[navi_id]
            cur_folder_info["navi"] = {"id": navi_id, "name": navi["name"]}
            reg_slot = get_reg(wram_data, navi_id)
            cur_folder_info["reg"] = reg_slot
            cur_folder_data = []

            for chip_slot in range(30):
                chip_name, chip_code, chip_id, chip_code_as_num = get_folder_chip(wram_data, navi_id, chip_slot, exe45_chip_ids_to_chip_names)
                cur_chip = {"id": chip_id, "name": chip_name, "code": chip_code, "is_reg": False}
                cur_folder_data.append(cur_chip)

            if reg_slot != 0xff:
                cur_folder_data[reg_slot]["is_reg"] = True

            cur_folder_info["contents"] = cur_folder_data
            all_folder_info[wram_filestem] = cur_folder_info

    all_folder_info_sorted = {k: v for k, v in sorted(all_folder_info.items(), key=lambda x: x[1]["ts"], reverse=True)}
    with open("exe45_pvp_all_folder_info_pretty.json", "w+") as f:
        json.dump(all_folder_info_sorted, f, indent=2)

    with open("exe45_pvp_all_folder_info.json", "w+") as f:
        json.dump(all_folder_info_sorted, f, separators=(',', ':'))

def dump_simple_stats():
    with open("exe45_pvp_all_folder_info.json", "r") as f:
        all_folder_info = json.load(f)

    with open("data/exe45_chips.json", "r") as f:
        exe45_chips = json.load(f)

    chip_usage = {}
    for chip_name in exe45_chips.keys():
        chip_usage[chip_name] = 0

    for cur_folder_info in all_folder_info.values():
        cur_folder_data = cur_folder_info["contents"]
        used_chips_in_folder = set(chip["name"] for chip in cur_folder_data)
        for used_chip in used_chips_in_folder:
            chip_usage[used_chip] += 1

    sorted_chip_usage = sorted(chip_usage.items(), key=lambda x: x[1], reverse=True)

    total_folders = len(all_folder_info)
    output = f"Number of folders: {total_folders}\n"
    output += "=========================================\n"

    for chip, amount_used in sorted_chip_usage:
        use_percent = (amount_used * 100)/total_folders
        output += f"{chip: >9} | {use_percent: >8.5f}% | {amount_used: >5}\n"

    with open("exe45_simple_chip_usage.txt", "w+") as f:
        f.write(output)

def dump_simple_stats_update_2():
    with open("exe45_pvp_all_folder_info.json", "r") as f:
        all_folder_info = json.load(f)

    with open("data/exe45_chips.json", "r") as f:
        exe45_chips = json.load(f)

    chip_usage = {}
    for chip_name in exe45_chips.keys():
        chip_usage[chip_name] = 0

    total_folders = 0

    for cur_folder_info in all_folder_info.values():
        if cur_folder_info["version"] not in ("0.3.0", "0.4.0", "0.5.0", "0.6.0"):
            continue

        total_folders += 1
        cur_folder_data = cur_folder_info["contents"]
        used_chips_in_folder = set(chip["name"] for chip in cur_folder_data)
        for used_chip in used_chips_in_folder:
            chip_usage[used_chip] += 1

    sorted_chip_usage = sorted(chip_usage.items(), key=lambda x: x[1], reverse=True)

    output = f"Number of folders: {total_folders}\n"
    output += "=========================================\n"

    for chip, amount_used in sorted_chip_usage:
        use_percent = (amount_used * 100)/total_folders
        output += f"{chip: >9} | {use_percent: >8.5f}% | {amount_used: >5}\n"

    with open("exe45_simple_chip_usage_update_2.txt", "w+") as f:
        f.write(output)

def dump_simple_stats_by_navi(update_2=False):
    with open("exe45_pvp_all_folder_info.json", "r") as f:
        all_folder_info = json.load(f)

    with open("data/exe45_chips.json", "r") as f:
        exe45_chips = json.load(f)

    with open("data/navis.json", "r") as f:
        navis = json.load(f)

    chip_usage_by_navi = {}
    total_folders_by_navi = {}

    for navi_name in navis.keys():
        chip_usage = {}
        for chip_name in exe45_chips.keys():
            chip_usage[chip_name] = 0

        chip_usage_by_navi[navi_name] = chip_usage
        total_folders_by_navi[navi_name] = 0

    total_folders = 0

    for cur_folder_info in all_folder_info.values():
        if update_2 and cur_folder_info["version"] not in ("0.3.0", "0.4.0", "0.5.0", "0.6.0"):
            continue

        total_folders += 1
        cur_folder_data = cur_folder_info["contents"]
        cur_navi_name = cur_folder_info["navi"]["name"]
        total_folders_by_navi[cur_navi_name] += 1
        used_chips_in_folder = set(chip["name"] for chip in cur_folder_data)
        for used_chip in used_chips_in_folder:
            chip_usage_by_navi[cur_navi_name][used_chip] += 1

    output = f"Number of folders: {total_folders}\n"
    output += "=========================================\n"

    for navi_name, chip_usage in chip_usage_by_navi.items():
        total_folders_for_navi = total_folders_by_navi[navi_name]
        output += f"---------------- {navi_name} ({total_folders_for_navi} folders) ----------------\n"

        sorted_chip_usage = sorted(chip_usage.items(), key=lambda x: x[1], reverse=True)
        unused_chips = []
        for chip, amount_used in sorted_chip_usage:
            if amount_used > 0:
                use_percent = (amount_used * 100)/total_folders_for_navi
                output += f"{chip: >9} | {use_percent: >8.5f}% | {amount_used: >5}\n"
            else:
                unused_chips.append(chip)

        output += "Unused: " + ", ".join(unused_chips) + "\n"

        output += "\n"

    if update_2:
        with open("exe45_simple_chip_usage_by_navi_update_2.txt", "w+") as f:
            f.write(output)
    else:
        with open("exe45_simple_chip_usage_by_navi.txt", "w+") as f:
            f.write(output)
        
def main():
    MODE = 8
    if MODE == 0:
        extract_wrams()
    elif MODE == 1:
        fix_wram_names()
    elif MODE == 2:
        extract_wrams_opponent()
    elif MODE == 3:
        extract_metadatas()
    elif MODE == 4:
        dump_raw_stats_as_json()
    elif MODE == 5:
        dump_simple_stats()
    elif MODE == 6:
        dump_simple_stats_update_2()
    elif MODE == 7:
        dump_simple_stats_by_navi()
    elif MODE == 8:
        dump_simple_stats_by_navi(True)
    else:
        print("no mode selected")

if __name__ == "__main__":
    main()
