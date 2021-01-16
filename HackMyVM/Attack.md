# HackMyVM-Attack

## NMAP

```
Nmap scan report for 192.168.1.144
Host is up (0.000080s latency).
Not shown: 65532 closed ports
PORT   STATE SERVICE VERSION
21/tcp open  ftp     ProFTPD
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: n
|   2048 f4:8d:08:b4:99:d2:0c:5d:75:b8:22:83:7b:c2:88:15 (RSA)
|   256 e2:16:0a:e7:38:4a:ec:76:cf:d3:56:78:07:fd:2f:25 (ECDSA)
|_  256 0b:5a:9c:71:cc:3b:50:04:46:18:ad:67:8a:df:d0:d6 (ED25519)
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: Site doesn't have a title (text/html).
MAC Address: 08:00:27:A4:8E:56 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 14.94 seconds

```

## PORT 80

<img src="https://imgur.com/C5mDTuw.png"/>

<img src="https://imgur.com/9kXsAiF.png"/>


## Wireshark

<img src="https://imgur.com/E8FKsmB.png"/>

Following the FTP data request the changing the stream we may see this request 

<img src="https://imgur.com/O0hxipZ.png"/>

<img src="https://imgur.com/2PL6mV7.png"/>

<img src="https://imgur.com/0XKERHX.png"/>

We get an id_rsa key file but we don not know the username so we can't actually use it without a vaid username so let's look for it.

<img src="https://imgur.com/2YBRoLS.png"/>

Going back to the ftp login on the top we can see the username and password

<img src="https://imgur.com/NbTBVhB.png"/>


Note says

```
I need to find the file!
```
So this is referring to the id_rsa file we found we actually went a step ahead : )


Using the username `teste` and id_rsa key let's login with ssh

<img src="https://imgur.com/lMBasY7.png"/>


<img src="https://imgur.com/PA1EwiR.png"/>

In `jackob`'s directory we can see that there is a note

<img src="https://imgur.com/2vWRKmJ.png"/>

<img src="https://imgur.com/5VdtC13.png"/>

But we don't have permissions to execute and there was nothing else we could do as `teste`. So going back to the pcap file I tried to export objects as HTTP and found an archive with the same name

<img src="https://imgur.com/ZkMrR5A.png"/>

<img src='https://imgur.com/qlWgDKO.png'/>

We can see there is a difference between those two archive one we got from FTP other by exporting objects as HTTP

<img src="https://imgur.com/qlWgDKO.png"/>

This is the image we get

<img src="https://imgur.com/k1FsNKY.png"/>

Now I though this was braille so I tried different sites to convert braille image to text , used different python scripts for reading braille looked at the table for it but I couldn't figure out the pattern then I uploaded this file to a barcode reader convert and it gave me a url

<img src="https://imgur.com/cA9MkEV.png"/>

<img src="https://imgur.com/kot0sB6.png"/>

And we got `jackob`'s id_rsa key

<img src="https://imgur.com/PGnh1iA.png"/>

<img src="https://imgur.com/lMcKVG2.png"/>

We can run `attack.sh` as user `kratos`

<img src="https://imgur.com/LIOjSdm.png"/>

So either delete or change the name of `attack.sh` and make your own attack.sh file

<img src="https://imgur.com/DYk68ho.png"/>

Put `/bin/bash` in the attack.sh file

<img src="https://imgur.com/n9CNHvU.png"/>

Check for `sudo -l` that what we can run as root or other user

<img src="https://imgur.com/RI6UjdF.png"/>

What `cppw` does is it will overwrite the `/etc/passwd` file so create file in the format having a username,password hash,user_id,group_id and the home directory. I copied my root user password hash and saved it in a text file then executed the cppw binary so it saved this in the /etc/passwd and it got overwritten.

<img src="https://imgur.com/Xs7pQZY.png"/>

Knowing my root password I successfully logged in as root without the root on that machine !!.