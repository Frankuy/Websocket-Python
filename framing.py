## CONSTANT ##

FIN_IDX = 0
RSV_1_IDX = 0
RSV_2_IDX = 0
RSV_3_IDX = 0
OPCODE_IDX = 0

MASK_IDX = 1
PAYLOAD_LEN_IDX = 1
MASK_KEY_IDX = 0
PAYLOAD_IDX = 0


def parse_frame(frame):
    ## GET ALL FRAME DETAIL
    fin = frame[FIN_IDX] >> 7
    rsv1 = (frame[RSV_1_IDX] >> 6) & 0x01
    rsv2 = (frame[RSV_2_IDX] >> 5) & 0x01
    rsv3 = (frame[RSV_3_IDX] >> 4) & 0x01
    opcode = frame[OPCODE_IDX] & 0x0f
    mask = frame[MASK_IDX] >> 7

    payload_len = frame[PAYLOAD_LEN_IDX] & 0x7f
    if (payload_len < 126):
        PAYLOAD_IDX = 2
        if mask == 1:
            MASK_KEY_IDX = 2
            PAYLOAD_IDX += 4
    elif (payload_len == 126):
        PAYLOAD_IDX = 4
        if mask == 1:
            MASK_KEY_IDX = 4
            PAYLOAD_IDX += 4
    elif (payload_len == 127):
        PAYLOAD_IDX = 10
        if mask == 1:
            MASK_KEY_IDX = 10
            PAYLOAD_IDX += 4

    ## GET MASK KEY ##
    mask_key = frame[MASK_KEY_IDX:MASK_KEY_IDX+4]

    ## GET PAYLOAD ##
    payload = frame[PAYLOAD_IDX:]

    result = {
		"FIN" : fin,
		"RSV1" :rsv1,
		"RSV2" :rsv2,
		"RSV3" :rsv3,
		"OPCODE" : opcode,
		"MASK" : mask,
		"PAYLOAD_LEN" : payload_len,
		"MASK_KEY" : mask_key,
		"PAYLOAD" : payload
	}

    return result

def build_frame(fin, rsv1, rsv2, rsv3, opcode, mask, payload_len, mask_key, 
        payload):
    # ADD FIRST 4-BIT 
    frame = (fin << 3) + (rsv1 << 2) + (rsv2 << 1) + rsv3

    # Append OPCODE to FRAME 
    frame = (frame << 4) + opcode

    # Append MASK to FRAME
    frame = (frame << 1) + mask

    # Append PAYLOAD_LEN to FRAME
    if (len(payload) >= 0 and len(payload) <= 125):
        frame = (frame << 7) + len(payload)
    elif (len(payload) >= 126 and len(payload) <= 65535):
        frame = (frame << 7) + 126
        frame = (frame << 16) + len(payload)
    elif (len(payload) >= 65536):
        frame = (frame << 7) + 127
        frame = (frame << 64) + len(payload)
    
    # Append MASK_KEY to FRAME
    if (mask == 1):
        frame = (frame << 32) + int.from_bytes(mask_key, byteorder='big')
    
    # Append PAYLOAD to FRAME
    # frame = int_to_bytes((frame << len(payload)) + int.from_bytes(payload, byteorder='big'))
    frame = int_to_bytes((frame << len(payload)*8) + int.from_bytes(payload, byteorder='big'))

    return frame

def get_real_payload(mask, mask_key, payload):
    if (mask == 1):
        hasil = b''
        for i in range(len(payload)):
            hasil = hasil + int_to_bytes(payload[i] ^ mask_key[i % 4])
        return hasil
    elif (mask == 0):
        return payload
    else:
        raise ValueError

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

# print(get_real_payload(1, b'%r\x14d', b'D\x01|\rD\x13u\x14U\x02'))
# print(build_frame(1, 1, 1, 1 , 1, 0, 1, 1, bytes('', 'utf-8')))
