# HackMyVM-Hommie

## Netdiscover


<img src="https://imgur.com/rLuVROg.png"/>

## NMAP

```
Nmap scan report for 192.168.1.96                                                                                                             [6/43]
Host is up (0.00024s latency).                                            
Not shown: 997 closed ports                                               
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3                                                                                                                   
| ftp-anon: Anonymous FTP login allowed (FTP code 230)     
|_-rw-r--r--    1 0        0               0 Sep 30 09:39 index.html
| ftp-syst:                                                                                                                                         
|   STAT: 
| FTP server status:
|      Connected to ::ffff:192.168.1.8
|      Logged in as ftp
|      TYPE: ASCII
|      No session bandwidth limit
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 2
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 c6:27:ab:53:ab:b9:c0:20:37:36:52:a9:60:d3:53:fc (RSA)
|   256 48:3b:28:1f:9a:23:da:71:f6:05:0b:a5:a6:c8:b7:b0 (ECDSA)
|_  256 b3:2e:7c:ff:62:2d:53:dd:63:97:d4:47:72:c8:4e:30 (ED25519)
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: Site doesn't have a title (text/html).
MAC Address: 08:00:27:AD:86:5A (Oracle VirtualBox virtual NIC)
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.39 seconds

```

## PORT 21 (FTP)

<img src="https://imgur.com/NatpPUF.png"/>

Now we have write permissions in the folder so let's try to upload a random text file.I tried to upload an empty text file `a.txt` and it got uploaded to ftp server.

<img src="https://imgur.com/477uGku.png"/>

So now we can upload a php reverse shell 

Download the shell from here https://github.com/pentestmonkey/php-reverse-shell and edit the lhost and lport (optional).

<img src="https://imgur.com/ZolF2Si.png"/>

But whenever I was trying to execute the php revershell it wasn't executing.

<img src="https://imgur.com/xipV6mU.png"/>

## PORT 80

<img src="https://imgur.com/PYlM9w4.png"/>


At this point I had no idea what to do , I tried running `gobuster` but it only returned the index.html and the files we were uploading so I again started to enumerate ports through nmap

<img src="https://imgur.com/ozoDyfv.png"/>

I ran a udp scan on the machine specifying the flag `-sU` and `-p 1-100` for scanning the ports from 1 to 100 because udp scan takes a lot of time than tcp scan.So what we got was a dhcp and tftp service ruuning on udp. We can enumrate tftp which is trivial file transfer protocol and it's different than ftp.

<img src="https://i.ibb.co/h1tj0M1/1.png"/>

We got connected to tftp because it doesn't use any authentication also tftp has a only a few commands as comapred to ftp we can only get or put a file so I assumed `id_rsa` must be here as it was hinted on the web page

<img src="https://imgur.com/G9BRpNu.png"/>

Set the permissions on `id_rsa` chmod 600

<img src="https://imgur.com/CSBzaFb.png"/>

Going into `/opt` directory we can see binary having a SUID

<img src="https://imgur.com/3vI0ccz.png"/>

Running the binary gives us the ssh key for alexia

<img src="https://imgur.com/H72XTZY.png"/>

I ran strings on the binary and saw that it was printing the ssh key with `cat` so here we can exploit PATH variable

<img src="https://imgur.com/RQ1jexg.png"/>

<img src="https://imgur.com/ezmck6Z.png"/>

root.txt isn't in the root's home directory so use the `find` command to search for the flag : )