import struct
import itertools

MASK_OFFSET = 0x1064
SAVE_SIZE = 0x6710
CHECKSUM_OFFSET = 0x1c6c

def main():
    with open("bn6f.sav", "rb") as f:
        save_data = bytearray(f.read())

    mask = save_data[MASK_OFFSET:MASK_OFFSET+4]
    mask_first_byte = mask[0]

    # "We only actually need to use the first byte of the mask, even though it's 32 bits long."
    for i in range(SAVE_SIZE):
        save_data[i] ^= mask_first_byte

    save_data[MASK_OFFSET:MASK_OFFSET+4] = mask

    with open("bn6f_decrypted.sav", "wb+") as f:
        f.write(save_data)

def calc_checksum_and_expected_checksum(save_data):
    checksum = 0

    for byte in itertools.islice(save_data, SAVE_SIZE):
        checksum = (checksum + byte) & 0xffffffff

    expected_checksum = struct.unpack("<I", save_data[CHECKSUM_OFFSET:CHECKSUM_OFFSET+4])[0]
    for i in range(4):
        checksum = (checksum - save_data[CHECKSUM_OFFSET+i]) & 0xffffffff

    checksum = (checksum + 0x72) & 0xffffffff

    return checksum, expected_checksum

def encrypt_save():
    with open("bn6f_decrypted.sav", "rb") as f:
        save_data = bytearray(f.read())

    checksum, expected_checksum = calc_checksum_and_expected_checksum(save_data)
    save_data[CHECKSUM_OFFSET:CHECKSUM_OFFSET+4] = struct.pack("<I", checksum)

    mask = save_data[MASK_OFFSET:MASK_OFFSET+4]
    mask_first_byte = mask[0]

    # "We only actually need to use the first byte of the mask, even though it's 32 bits long."
    for i in range(SAVE_SIZE):
        save_data[i] ^= mask_first_byte

    save_data[MASK_OFFSET:MASK_OFFSET+4] = mask

    with open("bn6g_encrypted.sav", "wb+") as f:
        f.write(save_data)

if __name__ == "__main__":
    encrypt_save()