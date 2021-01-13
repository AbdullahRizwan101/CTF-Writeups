# HackMyVM-Pwned

## NMAP

```
Nmap scan report for 192.168.1.7
Host is up (0.00020s latency).
Not shown: 65532 closed ports
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 fe:cd:90:19:74:91:ae:f5:64:a8:a5:e8:6f:6e:ef:7e (RSA)
|   256 81:32:93:bd:ed:9b:e7:98:af:25:06:79:5f:de:91:5d (ECDSA)
|_  256 dd:72:74:5d:4d:2d:a3:62:3e:81:af:09:51:e0:14:4a (ED25519)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: Pwned....!!
MAC Address: 08:00:27:56:AD:A9 (Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 10.73 seconds
```

## PORT 80

<img src="https://imgur.com/hdhpc0j.png"/>

Looking at the source we can see a comment at the bottom of the page

<img src="https://imgur.com/EGXNHqD.png"/>

I ran gobuster 

<img src="https://imgur.com/eWbZgcm.png"/>

From fuzzing the directories `/nothing` led me to actually nothing

<img src="https://imgur.com/TqHtgE6.png"/>

However `/hidden_text` was intersting.

<img src="https://imgur.com/fvh7Wy4.png"/>

Which was like wordlist or maybe there directories exists on the machine.So using this wordlist it came back with a `pwned.vuln` file 

<img src="https://imgur.com/AkKUnqa.png"/>

<img src="https://imgur.com/8wHfNvu.png"/>

Looking at the source code again

<img src="https://imgur.com/2HJCZSX.png"/>

These were infact credentials for ftp server

<img src="https://imgur.com/0HGS6yw.png"/>

<img src="https://imgur.com/kCdsA41.png"/>

The note says

```
Wow you are here 

ariana won't happy about this note 

sorry ariana :( 

```
This is private key belongs to user `ariana` so we can ssh into the box with this.

<img src="https://imgur.com/JhfIbWO.png"/>

Run `sudo -l` to see what we can run as root or as other user

<img src="https://imgur.com/AvXO29D.png"/>

<img src="https://imgur.com/wsu4v6y.png"/>

Transfer linpeas on the box

<img src="https://imgur.com/DCll2PT.png"/>

Right at the start it says that the user is `docker` group and we can privesc abusing it 

<img src="https://imgur.com/7n2jqdH.png"/>

Visting GTFOBINS for any privesc on docker

<img src="https://imgur.com/JctoUvu.png"/>

<img src="https://imgur.com/kwkqfOu.png"/>

And we are root !!!
fb8d98be1265dd88bac522e1b2182140
711fdfc6caad532815a440f7f295c176
4d4098d64e163d2726959455d046fd7c