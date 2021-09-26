# Hackathon-OS

## NMAP

```bash
PORT    STATE SERVICE     REASON         VERSION
22/tcp  open  ssh         syn-ack ttl 64 OpenSSH 8.4p1 Ubuntu 5ubuntu1.1 (Ubuntu Linux; protocol 2.0)                                               
80/tcp  open  http        syn-ack ttl 64 Apache httpd 2.4.46 ((Ubuntu))
| http-methods:                                                           
|_  Supported Methods: GET POST OPTIONS HEA                          
| http-robots.txt: 6 disallowed entries          
|_/test/ /t3$t@123/ /includes/ /external/ /api/ /hashes/                     
|_http-server-header: Apache/2.4.46 (Ubuntu)               
|_http-title: Apache2 Ubuntu Default Page: It works         
139/tcp open  netbios-ssn syn-ack ttl 64 Samba smbd 4.6.2          
445/tcp open  netbios-ssn syn-ack ttl 64 Samba smbd 4.6.2                  
MAC Address: 80:00:0B:3C:4A:7E (Intel Corporate)          
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
Host script results:                 
|_clock-skew: 1s                     
| nbstat: NetBIOS name: FILESERVER, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)                                                       
| Names:                             
|   FILESERVER<00>       Flags: <unique><active>                          
|   FILESERVER<03>       Flags: <unique><active>                          
|   FILESERVER<20>       Flags: <unique><active>                          
|   \x01\x02__MSBROWSE__\x02<01>  Flags: <group><active>                         

```


NMAP scan shows us  4 ports out which http and smb service looks interesting to us 

## PORT 135/445 (SMB)

We have three shares here out of which `shares` looks interesting 

<img src="https://i.imgur.com/1S1TMhd.png"/>

<img src="https://i.imgur.com/Nqp2Fvc.png"/>

But we can see that we don't have read access to any of them so let's move on !


## PORT 80 (HTTP)

On the web server we can see a default apache page 

<img src="https://i.imgur.com/NFPbOTM.png"/>

Since we already know about `robots.txt` from the nmap scan we can just visit that file and see what entries we may find

<img src="https://i.imgur.com/dETv98r.png"/>

None of these directories lead us to anywhere so let's fuzz for files and directories using `gobuster`

<img src="https://i.imgur.com/pgKKfqU.png"/>

This is only returned us robots.txt so no files are on the server , let's go a step back and run `enum4linux-ng` to enumerate users through smb

<img src="https://i.imgur.com/LLCDl3F.png"/>

<img src="https://i.imgur.com/yIdxuP2.png"/>

This gave us the username `test` , if we remember from robots.txt file there was entry named `test` and  `t3$t@123`  so this maybe test user's password 

<img src="https://i.imgur.com/noRwaxf.png"/>

## Foothold

With this we logged into `shares` directory on smb and we see few files there

<img src="https://i.imgur.com/m6yObjf.png"/>

`HINT` file contains a username and a hash 

```
clark:46a8047d5f9178c75aa6bf1090592427

```

While `pass.txt` contains list of potential passwords so we need to crack the `clark`'s hash using the provided worlist , we can either use `hashcat` or `john` but I'll be using hashcat for cracking this md5 hash

<img src="https://i.imgur.com/LICCHT6.png"/>

So we got clark's password , now we need to ssh into the machine 

<img src="https://i.imgur.com/RfEPsxl.png"/>

<img src="https://i.imgur.com/v7Pwq2o.png"/>

This user isn't in sudoers group also isn't allowed to run any commands as other user so let's enumerate the machine to find other user folders 

<img src="https://i.imgur.com/DuXm07L.png"/>

## Privilege Escalation (maker)

Here we see `Deep.zip` which was not related to rooting for this box as it only contains a flag and we can get flag by just cracking this archive's password by using the previous password list , so moving on we see `.bash_history` that's important to look at what commands the user ran 

<img src="https://i.imgur.com/0wu5sNW.png"/>


## Rooting the box

<img src="https://i.imgur.com/hUTKa1r.png"/>

After switching to `maker` we realize that this user is in `villan` group so let's see what files are owned by villan group 

<img src="https://i.imgur.com/Upexet8.png"/>

`/etc/passwd` file is owned by this group so this means that we can read/write to this file , let's verify this

<img src="https://i.imgur.com/uzl0SUK.png"/>

All that is left to do is to add a hash in root's entry, you can do this by generating a password hash using `openssl` but I just copied my hash from `/etc/shadow` and just pasted there 

<img src="https://i.imgur.com/9OskQtj.png"/>

<img src="https://i.imgur.com/iyv0IA8.png"/>

And with this we rooted this fun, amazing , challenging , hard ,OP,hackathon,not a vulnhub copied box.
