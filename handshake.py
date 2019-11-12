## LIBRARY ##
import hashlib
import base64

## CONSTANT ##
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def validate_handshake(handshake):
    """Return key handshake from client if handshake are true else return false"""
    arr_header = handshake.split('\r\n')
    connection_upgrade = False
    upgrade_websocket = False
    web_socket_key = False
    i = 0
    valid = True
    for header in arr_header:
        # VALIDATE GET CONNECTION
        if i == 0:  
            content = header.split(' ')
            if content[0] != 'GET':
                valid = False
        # VALIDATE HEADER FIELD
        else:
            content = header.split(':')
            try:
                # Connection : Upgrade
                if 'Connection' in content[0] and 'Upgrade' in content[1]:
                    connection_upgrade = True
                # Upgrade : websocket
                elif 'Upgrade' in content[0] and 'websocket'in content[1]:
                    upgrade_websocket = True
                # Sec-WebSocket-Key : xxxxx(16)
                elif 'Sec-WebSocket-Key' in content[0]:
                    key = content[1].replace(" ", "")
                    web_socket_key = True
            except:
                pass
        i += 1

    #RETURN VALDIAION
    if valid and connection_upgrade and upgrade_websocket and web_socket_key:
        return key
    else:
        return False

def response_handshake(handshake):
    """Handling response to client handshake"""
    key = validate_handshake(handshake.decode('utf-8'))
    if (key):
        hash_key = hashlib.sha1()
        hash_key.update(key.encode('utf-8'))
        hash_key.update(GUID.encode('utf-8'))
        accept_key = base64.b64encode(hash_key.digest()).decode('utf-8')
        return f"HTTP/1.1 101 Web Socket Protocol Handshake\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: {accept_key}\r\nUpgrade: websocket\r\n\r\n"
    else:
        return 'HTTP/1.1 400 Bad Request\r\n'
