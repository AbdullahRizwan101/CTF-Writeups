# HackTheBox-Monitor

## Rustscan

```bash

PORT   STATE SERVICE REASON         VERSION                 
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:         
|   256 69:43:37:6a:18:09:f5:e7:7a:67:b8:18:11:ea:d7:65 (ECDSA)           
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBKHKAgNKkq5XDcAfsuuxZFMPf+iEHjoq9DUmOmg0cCDgpE90GNOZeoaI24IlwlrSdTWTRA9HNJ
7DFyIkcHr37Dk=
|   256 5d:5e:3f:67:ef:7d:76:23:15:11:4b:53:f8:41:3a:94 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBi/L9gWCzbJ6GzFB1PsHZJco24eJW3wmC+a4Ul6fEe6
80/tcp open  http    syn-ack ttl 63 Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html; charset=iso-8859-1).
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
OS fingerprint not ideal because: Missing a closed TCP port so results incomplete
Aggressive OS guesses: Linux 2.6.32 (95%), Linux 3.1 (95%), Linux 3.2 (95%), AXIS 210A or 211 Network Camera (Linux 2.6.17) (94%), ASUS RT-N56U WAP 
(Linux 3.4) (93%), Linux 3.16 (93%), Linux 2.6.39 - 3.2 (92%), Linux 3.1 - 3.2 (92%), Linux 3.2 - 4.9 (92%), Linux 3.7 - 3.10 (92%)
No exact OS matches for host (test conditions non-ideal).
```

## PORT 80 (HTTP)

<img src="https://i.imgur.com/9IzPyiL.png"/>

We can see a domain name `monitors.htb` so let's add it to our `/etc/hosts` file

<img src="https://imgur.com/NHLiAL4.png"/>

<img src="https://imgur.com/Lh4nJ5f.png"/>

We can see at the bottom that this is a wordpress site

<img src="https://i.imgur.com/TWWW72J.png"/>
Using `wpscan` to enumerate for user we find a usernamed `admin` as we saw on the blog post

<img src="https://imgur.com/1mwCJgd.png"/>

<img src="https://i.imgur.com/YXHFWwf.png"/>

When I tried doing a brute force attack on wordpress login it wasn't allowing me to do because of WAF 

<img src="https://imgur.com/72WJp8A.png"/>

So then I tried to look for plugins on wordpress

<img src="https://imgur.com/VlaqXZf.png"/>

<img src="https://imgur.com/VlaqXZf.png"/>

On googling we can see that there's an exploit for `WP with Spritz` plugin which is an RFI vulnerability 

<img src="https://imgur.com/d9q9yow.png"/>
Let's try to test it by reading the  `/etc/passwd` file

`http://monitors.htb/wp-content/plugins/wp-with-spritz/wp.spritz.content.filter.php?url=/../../../..//etc/passwd`

<img src="https://imgur.com/ppmI9jk.png"/>

Great it worked but we won't get a shell with it as RFI does not execute the file it will only read it and we can't put our reverse shell on the machine so what we can do is try to read local files and since wordpress is being used on the machine we can try to read `wp-config.php` since it has credentials for database 

<img src="https://i.imgur.com/lQBZSLS.png"/>

We found the creds another thing we can do is to read apache virtual host configuration file `etc/apache2/sites-available/000-default.conf`

<img src="https://i.imgur.com/Gfdm9Vq.png"/>

We can see a subdomain here so let's add this again to our `/etc/hosts` file

<img src="https://imgur.com/vaOqOLQ.png"/>

On visiting the subdomain we will be introducted with `Cacti` which is an open-source, web-based network monitoring and graphing tool


<img src="https://imgur.com/hbPIMDc.png"/>

Now we already have found the credentials we know that admin@mointors.htb was seen on the home page so we can try logging in as user `admin` with the password we found


<img src="https://imgur.com/aAcfgZs.png"/>

And we are in, notice the version number is `1.2.12` so we can look for an exploit

<img src="https://imgur.com/RALJ32L.png"/>

On running the exploit we will get a shell as `www-data`

<img src="https://imgur.com/Vqcp5af.png"/>

Stabilize the shell you got 

<img src="https://imgur.com/XFNs8hh.png"/>

Now going into `/home` folder we can see that we have access to `marcus's` directory so going into his home folder we can a folder named `.backup` which has executabale permissions only means we cannot read it and it was interesting to see this directory here

<img src="https://i.imgur.com/1Q63uEL.png"/>

So I search for `marcus` recursivley in `/etc/` folder and we see a service which was running that script 

<img src="https://i.imgur.com/EuvVyaF.png"/>

On reading that script file we can a passow

<img src="https://i.imgur.com/21KJynU.png"/>

Let's try to swtiching to marcus with that password

<img src="https://imgur.com/JKCAVBs.png"/>

It worked now let's read `note.txt`

<img src="https://imgur.com/IfNSbWz.png"/>

It says about updating a docker image so a container is running on the machine let's see the local ports on the machine

<img src="https://i.imgur.com/gFe1OkD.png"/>

We can see port 8443 but we are not sure if it's for docker so let's see the processes on the machine  by running `ps aux --forest`

<img src="https://imgur.com/uQmxTdd.png"/>

Hmm it does show docker but we are not getting the whole output so let's set rows and columns on the terminal with `stty rows 30 columns 148`

<img src="https://imgur.com/lYyhRLh.png"/>

Yup that's definatley the container running on port 8443 so let's do a little ssh port forwading in order to interact with it

<img src="https://imgur.com/FKNR7Y0.png"/>

<img src="https://imgur.com/DhCwsuP.png"/>

This tells us that apache tomcat is running and we can see the version as well so let's try to find an exploit for it 

<img src="https://i.imgur.com/RzvLS3r.png"/>

It looks like we do have an exploit , now here I tried to run the manaul exploits for github and none of them worked some of them would show me that status that reverse shell is uploaded but I really didn't get a shell so I searched the exploit for metasploit and found one 

<img src="https://imgur.com/Hue6jxP.png"/>

<img src="https://imgur.com/I3GRilm.png"/>

It fails when we run it without enabling force exploit

<img src="https://i.imgur.com/guRO0vx.png"/>

Even enabling force exploit it goes crazy

<img src="https://imgur.com/KXNrp9K.png"/>

<img src="https://imgur.com/0MkHZZN.png"/>

We get a session but it isn't really helpful , doesn't do anything so here we need to change our target

<img src="https://i.imgur.com/E9tkeRT.png"/>

<img src="https://imgur.com/05a3VZV.png"/>

<img src="https://i.imgur.com/EQKleYn.png"/>

Now we have a unstabilized shell so let's first stabilize it so we can interact with it better

<img src="https://imgur.com/OVqVRdt.png"/>

Checking for container capabilites we have cap_sys_module capability which means this docker conatiner can insert kernel modules so there's an article on how we can abuse it in order to gain root on host machine 

<img src="https://i.imgur.com/zz1BXjQ.png"/>

So according to the article we have to make c language  kernel module program having a bash reverse shell

<img src="https://imgur.com/ZlwRt3b.png"/>

Then  we need to make a Makefile which will compile kernel module

<img src="https://imgur.com/iyK9ngp.png"/>

Now run the `make` command

<img src="https://imgur.com/hmxDgsN.png"/>

Start you netcat listener on what ever port you specifed in the reverse shell and run the module

<img src="https://i.imgur.com/7iHJspW.png"/>

<img src="https://imgur.com/GwT2gce.png"/>