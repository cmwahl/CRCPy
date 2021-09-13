
CRCs = [{"bits": 16, "poly": 0x9eb2, "hd": 6, "data_bytes": 16},
        {"bits": 32, "poly": 0x9d7f97d6, "hd": 9, "data_bytes": 27},
        {"bits": 32, "poly": 0x9960034c, "hd": 6, "data_bytes": 4092}]


def getCRCRemainder(message, crc):
    byte_index = 0
    bit_index = 0
    max_bits = 8 * len(message)
    sig_bit = 1 << (crc["bits"] - 1)

    remainder = 0

    for i in range(int(crc["bits"]/8)):
        remainder = remainder << 8
        remainder += ord(message[byte_index])
        byte_index += 1

    no_more_bits = False
    while not no_more_bits:

        while not remainder & sig_bit:
            # If another bit
            if byte_index * 8 + bit_index + 1 > max_bits:
                no_more_bits = True
                break

            # Move over remainder
            remainder = remainder << 1

            # Get the bit, and add it
            bit = 1 if (ord(message[byte_index]) & (1 << (8 - bit_index - 1))) > 0 else 0
            remainder += bit

            # Update
            bit_index += 1
            byte_index += int(bit_index / 8)
            bit_index = bit_index % 8

        if no_more_bits:
            break

        # XOR
        remainder = remainder ^ crc["poly"]

    return remainder


if __name__ == "__main__":
    # our message
    data = "dogs!\0\0\0\0"
    crc_index = 0
    print("Message:", data)
    remainder = getCRCRemainder(data, CRCs[crc_index])
    print("Remainder:", remainder)

    # add CRC to the packet
    crc_bytes = int(CRCs[crc_index]["bits"]/8)
    the_bytes = int.to_bytes(remainder, crc_bytes, 'big')
    data_list = list(data)
    for i in range(crc_bytes):
        data_list[len(data) - crc_bytes + i] = chr(the_bytes[i])
    data = "".join(data_list)
    print("With CRC on:", data)

    print("New remainder:", getCRCRemainder(data, CRCs[crc_index]))

