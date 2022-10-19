import struct

MASK_OFFSET = 0x3c84
SRAM_SIZE = 0xc7a8

def main():
    with open("exe45_us_pvp_template.sav", "rb") as f:
        save_data = bytearray(f.read())

    mask = save_data[MASK_OFFSET:MASK_OFFSET+4]
    mask_first_byte = mask[0]

    # "We only actually need to use the first byte of the mask, even though it's 32 bits long."
    for i in range(SRAM_SIZE):
        save_data[i] ^= mask_first_byte

    save_data[MASK_OFFSET:MASK_OFFSET+4] = mask

    with open("exe45_us_pvp_template_decrypted.sav", "wb+") as f:
        f.write(save_data)

if __name__ == "__main__":
    main()