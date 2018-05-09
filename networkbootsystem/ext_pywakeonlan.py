import socket
import binascii
import struct
import re


def send_magic_packet(mac):
    mac_re = re.compile(r'''
                      (^([0-9A-F]{1,2}[-]){5}([0-9A-F]{1,2})$
                      |^([0-9A-F]{1,2}[:]){5}([0-9A-F]{1,2})$
                      |^([0-9A-F]{1,2}[.]){5}([0-9A-F]{1,2})$
                      )''',
                        re.VERBOSE | re.IGNORECASE)
    # print(re.match(mac_re, mac))
    if re.match(mac_re, mac):
        if mac.count(':') == 5 or mac.count('-') == 5 or mac.count('.'):
            sep = mac[2]
            mac_fm = mac.replace(sep, '')
            data = 'FF'*6 + str(mac_fm)*16
            # print(data)
            # print(type(data))
            send_data = binascii.unhexlify(data)

            # broadcast_address = '192.168.97.255'
            broadcast_address = '255.255.255.255'
            port = 9
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(send_data, (broadcast_address, port))
            return True
        else:
            return False
    else:
        return False




