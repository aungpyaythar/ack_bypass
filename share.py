import socket
import struct

def calc_checksum(header):
    result = 0
    header_len = len(header)
    if (header_len % 2):
        header_len += 1
        header += '\x00'        
    for i in range(0, header_len, 2):
        temp = ord(header[i]) << 8 | ord(header[i+1])
        result += temp
        result = (result >> 16) + (result & 0xffff)
    return (~result & 0xffff)

def tcp_checksum(src_ip, dst_ip, header_len, header):
    reserved = 0 
    protocol = 6
    checksum_data = struct.pack("!2BH", reserved, protocol, header_len)
    psh = socket.inet_aton(src_ip) + socket.inet_aton(dst_ip) + checksum_data
    return calc_checksum(psh + header)
        
def craft_ack(conn_info, syn_ack, data):
    # conn_info is a tuple of four memebers where the first
    # two members represent the sender ip and port 
    # while the last twos represent target ip and port.
    # syn_ack is a two-member tuple where the first
    # twos are the syn and ack number of the about-to-send
    # packet.
    src_port = conn_info[1]
    dst_port = conn_info[3]
    seq_num = syn_ack[0]
    ack_num = syn_ack[1]
    tcp_len = 5
    offset_reserv = tcp_len << 4
    flags = 0b00010000
    window_size = 2048  
    checksum = 0
    urg_ptr = 0
    tcp_header = struct.pack("!2H2L2B3H", src_port, dst_port, seq_num, ack_num, 
                             offset_reserv, flags, window_size, checksum,
                             urg_ptr) + data
    checksum = tcp_checksum(conn_info[0], conn_info[2], tcp_len * 4 + len(data), tcp_header)
    tcp_header = struct.pack("!2H2L2B3H", src_port, dst_port, seq_num, ack_num, 
                             offset_reserv, flags, window_size, checksum,
                             urg_ptr) + data
    return tcp_header
