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

def build_frame(fin, rsv1, rsv2, rsv3, opcode, mask, payload_len, mask_key, payload):
    ## TODO ##
    return b''

def get_real_payload(mask, mask_key, payload):

    hasil = b''

    if (mask == 1) :
        for i in range(len(payload)):
            hasil = hasil + int_to_bytes(payload[i] ^ mask_key[i % 4])

    return hasil

def int_to_bytes(data):
    result = bytes(str(chr(data)), "ascii")
    return result

def bytes_to_ascii(data):
    return data[4:8].decode("ascii")
