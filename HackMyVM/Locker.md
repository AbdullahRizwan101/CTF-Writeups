# HackMyVM-Locker

## NMAP


```
nmap -p- -sC -sV 192.168.1.140
Starting Nmap 7.80 ( https://nmap.org ) at 2021-01-26 15:48 PKT
Nmap scan report for 192.168.1.140
Host is up (0.00013s latency).
Not shown: 65534 closed ports
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: Site doesn't have a title (text/html).
MAC Address: 08:00:27:6A:15:D5 (Oracle VirtualBox virtual NIC)
```

## PORT 80

<img src="https://imgur.com/XsFTzE7.png"/>

On clicking the hyperlink

<img src="https://imgur.com/Je7EoHF.png"/>

We can see an image of the lock also we can the parameter `image` having value of 1 so let's changing the value

<img src="https://imgur.com/b1PjLlx.png"/>

<img src="https://imgur.com/ZBG8xNV.png"/>

We have 3 images , I tried running gobuster there wasn't anything intersting also I tried steghide, strings,exiftool on these images but didn't get anything useful

<img src="https://imgur.com/TZQ2D0z.png"/>

So I had no idea what to do at this point than thought about the obivous RCE

<img src="https://imgur.com/Q1PEJOv.png"/>

<img src="https://imgur.com/qzlPXYP.png"/>

But got nothing.After asking for hints on discord looking at the screen for quite a while I just added `;id;` and got rce to be working

<img src="https://imgur.com/fsocs9U.png"/>

<img src="https://imgur.com/o87YGho.png"/>


To get a reverse shell we will use python payload adding the payload after `;` 

<img src="https://imgur.com/dBAQmdx.png"/>

Transfer linpeas for further enumeration although it isn't necessary but if you want to just enumerate faster you should run the script it's very helpful

<img src="https://imgur.com/CiVZTUI.png"/>

<img src="https://imgur.com/W6I1bKm.png"/>

Here we can see `/usr/sbin/sulogin` which is not commonly set as SUID

<img src="https://imgur.com/L8zSRSq.png"/>

Seeing the man page of sulogin

<img src="https://imgur.com/NCuitgD.png"/>

<img src="https://imgur.com/ljg3xFA.png"/>

```
sulogin looks for the environment variable SUSHELL or sushell to determine what shell to start.If the environment variable is not set,it will try to execute root's shell from /etc/passwd.If that fails,it will fall back to /bin/sh.
```
Create c program to set uid and gid to 0 and execute /bin/bash using system

<img src="https://imgur.com/GzvnG02.png"/>

Compile and transfer it to the target machine

<img src="https://imgur.com/IpObjOF.png"/>

As it said in the man page of sulogin that it will look for SUSHELL variable and will start it so we need to exit from sulogin and then run the command again

<img src="https://imgur.com/3mqw33f.png"/>

<img src="https://imgur.com/Yz3nzQN.png"/>
