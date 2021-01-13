# HackMyVM-Helium

## NMAP

```
Host is up (0.00019s latency).
Not shown: 65533 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 12:f6:55:5f:c6:fa:fb:14:15:ae:4a:2b:38:d8:4a:30 (RSA)
|   256 b7:ac:87:6d:c4:f9:e3:9a:d4:6e:e0:4f:da:aa:22:20 (ECDSA)
|_  256 fe:e8:05:af:23:4d:3a:82:2a:64:9b:f7:35:e4:44:4a (ED25519)
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: RELAX
MAC Address: 08:00:27:4C:32:E1 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.73 seconds
```

## PORT 80

<img src="https://imgur.com/gzIZcvW.png"/>

<img src="https://imgur.com/3KW7uWJ.png"/>

If we look at the bootstrap css file

<img src="https://imgur.com/S3y6VwI.png"/>

On anaylzing the wav file with audactiy and adding a spectogram we can see a text

<img src="https://imgur.com/RfQUPUe.png"/>

Saying `dancingpassyo`  

On trying the password with the username `paul` with ssh

<img src="https://imgur.com/1Dfj0Op.png"/> 

## Privilege Escalation

We can check what commands can paul run as root so do `sudo -l`

<img src="https://imgur.com/RmwIoYp.png"/>

Seems we can run `ln` as root which is for making symlinks.We can create a binary in which we call `bash` in it and link it with the `/usr/bin/ln` binary

<img src="https://imgur.com/wBcXuVD.png"/>

<img src="https://imgur.com/dlNnerf.png"/>