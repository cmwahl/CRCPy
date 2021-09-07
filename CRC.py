
CRCs = [{"bits": 16, "poly": 0x9eb2, "hd": 6, "data_bytes": 16},
        {"bits": 32, "poly": 0x9d7f97d6, "hd": 9, "data_bytes": 27},
        {"bits": 32, "poly": 0x9960034c, "hd": 6, "data_bytes": 4092}]


# This file gets data as a string, and adds a CRC to the end
def __isSigBit1(data, crc):
    sigBit = 1 << (crc["bits"] - 1)
    return True if data >= sigBit else False


def __dataToInt(data):
    tot_chars = len(data)
    value = 0
    for i in range(tot_chars):
        value += ord(data[-1 - i]) << (i * 8)

    return value



def addCRCToPacket(data, crc):
    if len(data) > crc["data_bytes"]:
        return ""

    data += '\0' * int(crc["bits"] / 8)
    remainder = __getCRCRemainder(data, crc)
    remainder_bytes = remainder.to_bytes(int(crc['bits']/8), 'big')
    data_list = list(data)
    for i in range(len(remainder_bytes)):
        data_list[-i - 1] = chr(remainder_bytes[-i - 1])

    data = "".join(data_list)
    return data




def __getCRCRemainderDEBUG(data, crc):
    tot_bits = len(data) * 8
    poly_bytes = int(crc["bits"] / 8)
    data_chunk = data[:poly_bytes]
    bit_index = 0
    byte_index = poly_bytes
    stored_remainder = 0
    working_remainder = __dataToInt(data_chunk)
    moving_window_size = poly_bytes + 1
    count = 0
    while True: #byte_index < len(data) and bit_index != 7:
        print(count, ":")
        bits_moved = 0  # number of bits needed to move
        bits_left = tot_bits - byte_index * 8 - bit_index
        print("bits left:", bits_left)
        # Move bits to most sig for next XOR'ing
        while not __isSigBit1(working_remainder, crc):
            working_remainder = working_remainder << 1
            bits_moved += 1
            # if not enough bits, break
            if bits_moved > bits_left:
                break

        if bits_moved > bits_left:
            break
        print("bits moved:", bits_moved)
        print("working remain:", working_remainder)

        # If there are enough bits to move over from data, get them
        if byte_index + moving_window_size > len(data):
            print("too big")
            data_chunk = __dataToInt(data[byte_index:] + '\0' * (byte_index + moving_window_size - len(data)))
        else:
            data_chunk = __dataToInt(data[byte_index:byte_index + moving_window_size])

        print("data_chunk fresh:", data_chunk)
        print("bit index:", bit_index)
        #data_chunk = data_chunk << bit_index # this doesn't cut off the first bits like in C++
        # cut off front bits we don't want
        bit_scissors = (1 << (moving_window_size * 8)) - 1
        bit_scissors = bit_scissors >> (bit_index)
        print("bitscissors:", bit_scissors)
        data_chunk = data_chunk & bit_scissors
        data_chunk = data_chunk >> (moving_window_size * 8 - bits_moved - bit_index)
        print("Data chunk:", data_chunk)

        working_remainder += data_chunk
        print("work_remainder preXOR:", working_remainder)

        # XOR
        working_remainder = working_remainder ^ crc["poly"]

        stored_remainder = working_remainder
        byte_index += int((bits_moved + bit_index) / 8)
        bit_index = (bits_moved + bit_index) % 8

        print("stored remainder:", stored_remainder)
        print()
        count += 1
    return stored_remainder

def __getCRCRemainder(data, crc):
    tot_bits = len(data) * 8
    poly_bytes = int(crc["bits"] / 8)
    data_chunk = data[:poly_bytes]
    bit_index = 0
    byte_index = poly_bytes
    stored_remainder = 0
    working_remainder = __dataToInt(data_chunk)
    moving_window_size = poly_bytes + 1
    count = 0
    while True:  # byte_index < len(data) and bit_index != 7:
        bits_moved = 0  # number of bits needed to move
        bits_left = tot_bits - byte_index * 8 - bit_index
        # Move bits to most sig for next XOR'ing
        while not __isSigBit1(working_remainder, crc):
            working_remainder = working_remainder << 1
            bits_moved += 1
            # if not enough bits, break
            if bits_moved > bits_left:
                break

        if bits_moved > bits_left:
            break

        # If there are enough bits to move over from data, get them
        if byte_index + moving_window_size > len(data):
            data_chunk = __dataToInt(data[byte_index:] + '\0' * (byte_index + moving_window_size - len(data)))
        else:
            data_chunk = __dataToInt(data[byte_index:byte_index + moving_window_size])

        # data_chunk = data_chunk << bit_index # this doesn't cut off the first bits like in C++
        # cut off front bits we don't want
        bit_scissors = (1 << (moving_window_size * 8)) - 1
        bit_scissors = bit_scissors >> (bit_index)
        data_chunk = data_chunk & bit_scissors
        data_chunk = data_chunk >> (moving_window_size * 8 - bits_moved - bit_index)

        working_remainder += data_chunk

        # XOR
        working_remainder = working_remainder ^ crc["poly"]

        stored_remainder = working_remainder
        byte_index += int((bits_moved + bit_index) / 8)
        bit_index = (bits_moved + bit_index) % 8

        count += 1
    return stored_remainder

if __name__ == "__main__":
    # our message
    data = "dog"
    print("Message:", data)
    # add CRC to the packet
    remainder = addCRCToPacket(data, CRCs[0])
    print("Message with CRC:", remainder)
    # Ensure our remainder is zero
    print("Check to ensure our remainder is now 0:", __getCRCRemainder(remainder, CRCs[0]))

    # Add 'noise' by changing a character
    print("Add 'noise' by changing a character in our message...")
    remainder_list = list(remainder)
    remainder_list[2] = 'x'
    remainder = "".join(remainder_list)

    # Ensure our remainder is no longer zero after 'noise'
    print("New, noisy message:", remainder)
    print("Check to ensure our remainder is not 0 after noise:", __getCRCRemainder(remainder, CRCs[0]))
