# HackTheBox - Backdoor

## NMAP

```bash
nmap -p- -sC -sV 10.10.11.125 --min-rate 5000 -v

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-generator: WordPress 5.8.1
| http-methods: 
|_  Supported Methods: HEAD
1337/tcp open  waste?  syn-ack ttl 63
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

From the scan we saw that there's a web server apache server running on port 80

<img src="https://i.imgur.com/Ir2boo6.png"/>

At the bottom , we can see that this is a wordpresss site

<img src="https://i.imgur.com/wOGkKmC.png"/>

We can try to login with default creds like admin:admin 

<img src="https://i.imgur.com/IdB9CWr.png"/>

<img src="https://i.imgur.com/TbKd6Am.png"/>

It gives an error that password for `admin` user invalid but it didn't say that username is invalid so we could try to brute force but let's just leave it for the last. I tired to run an nmap scan for wordpress plugins but there wasn't any thing interesting

` nmap -p 80 --script http-wordpress-enum --script-args search-limit=2000 10.10.11.125 -vvv`

<img src="https://i.imgur.com/qdVJSJb.png"/>

I ran `wpscan` and used aggresive plugins scan but it was taking so long for it to complete instead I manully tried to enumerate plugins by going to `/wp-content/plugins`

<img src="https://i.imgur.com/KCvuLmZ.png"/>

The readme file shows that it's using version 1.1

<img src="https://i.imgur.com/zbfbe0k.png"/>

And this version is vulnerable to LFi 

<img src="https://i.imgur.com/6NzFp5p.png"/>

`10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../wp-config.php`

This will download `wp-config.php` file which has the database credentials

<img src="https://i.imgur.com/RIWMx3p.png"/>

We can also download `/etc/passwd` file

`http://10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../../../../etc/passwd`

<img src="https://i.imgur.com/SlWpd2r.png"/>

But we can't do things like log posining as we are only able to download the file not view them directly , remember from our nmap scan we saw that there was a port 1337 but on connecting on the port we don't get any response

<img src="https://i.imgur.com/dW01a1m.png"/>

## Foothold 
In order to find what's running on that port we need can find it by reading ` /proc/sched_debug` , which shows all the processes that are running on the system

<img src="https://i.imgur.com/8FhrOZ5.png"/>

On reading that file we can see that `gdbserver` is running and there's a remote code execution exploit available on metasploit

<img src="https://i.imgur.com/2IeFdoz.png"/>

I got another reverse shell as I wanted to stabilize the shell and the meterpreter shell isn't stable when we spawn bash

<img src="https://i.imgur.com/4y2ccHu.png"/>

So this enabled us to stabilize our shell , now to escalate our privleges I checked `sudo -l` to see if I can run something as root , tried the password that we found from wordpress config file but it didn't work

<img src="https://i.imgur.com/z15No9t.png"/>

Checked contab but there wasn't any cronjobs running, logging in to database we can see that there's an admin user's password for wordpress

<img src="https://i.imgur.com/xzoozsU.png"/>

## Privilege Escalation

I checked the running processes and found that a command was being ran to create a deattached `screen` session

<img src="https://i.imgur.com/WBmQYrR.png"/>

We can create a deattach session using `-dmS session_name` and we can reattach the session with `-r session_name` but this wasn't working , since screen has SUID bit

<img src="https://i.imgur.com/iIRapii.png"/>

We can actually access the screen session as root through `screen -r root/`

<img src="https://i.imgur.com/3mFZtQv.png"/>


## References
- https://www.armourinfosec.com/wordpress-enumeration/
- https://stackoverflow.com/questions/9953973/how-to-collect-information-of-every-single-cpu
- https://serverfault.com/questions/336594/share-screen-session-with-users-in-the-same-group-linux
