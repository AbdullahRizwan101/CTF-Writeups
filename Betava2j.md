# TryHackMe-Betav2j

## NMAP

```

Nmap scan report for 10.10.220.63
Host is up (0.41s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 2c:54:c1:d0:05:91:e1:c0:98:e1:41:f2:b3:21:d9:6b (RSA)
|   256 1e:ba:57:5f:29:8c:e4:7a:b4:e5:ac:ed:65:5d:8e:32 (ECDSA)
|_  256 7b:55:2f:23:68:08:1a:eb:90:72:43:66:e1:44:a1:9d (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
3306/tcp open  mysql   MySQL 5.5.5-10.1.47-MariaDB-0ubuntu0.18.04.1
| mysql-info: 
|   Protocol: 10
|   Version: 5.5.5-10.1.47-MariaDB-0ubuntu0.18.04.1
|   Thread ID: 69
|   Capabilities flags: 63487
|   Some Capabilities: SupportsTransactions, ConnectWithDatabase, DontAllowDatabaseTableColumn, LongPassword, ODBCClient, Speaks41ProtocolOld, Support41Auth, IgnoreSigpipes, Speaks41ProtocolNew, FoundRows, SupportsLoadDataLocal, IgnoreSpaceBeforeParenthesis, InteractiveClient, SupportsCompression, LongColumnFlag, SupportsMultipleResults, SupportsAuthPlugins, SupportsMultipleStatments
|   Status: Autocommit
|   Salt: :`Vl<)UProV?vX5?|vZ@
|_  Auth Plugin Name: mysql_native_password
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 38.06 seconds
```

## PORT 80

<img src="https://imgur.com/LFhMxAp.png"/>

Running gobuster on the web server

<img src="https://imgur.com/330CYFx.png"/>

These all were just rabbit holes

<img src="https://imgur.com/2mKpio4.png"/>

Looking at the memebers on the forum there's a member whith a white rabbit avatar

<img src="https://imgur.com/wQUEuOk.png"/>

So this hints us as the room description had a `follow the rabbit` picture

<img src="https://imgur.com/yQKolQ0.png"/>

We can see this user has some posts but when we try to view them it would not show them

<img src="https://imgur.com/3sw9YMm.png"/>

So let's try registring an account on `Linux-Bay` forum. I already registered on the forum before trying this so I'll login to the forum

<img src="https://imgur.com/jPYnMl0.png"/>

<img src="https://imgur.com/wVaicwC.png"/>

Now when you visit his profile you can see his post

<img src="https://imgur.com/wjgF3PK.png"/>

Here you can see a link to page

<img src="https://imgur.com/xzPvfRo.png"/>

<img src="https://imgur.com/0SdsaBA.png"/>

Viewing the source code we can find the link where white rabbit lead us 

<img src="https://imgur.com/h0iu64R.png"/>

Visting the page /reportPanel.php we can see a bunch of bugs that people have reported

<img src="https://imgur.com/rvhHilj.png"/>

Now a hint is given to us that the vulnerability must be from the year 2021 so we have three vulnerabilites that are reported in 2021.

<img src="https://imgur.com/CBUOYsW.png"/>

<img src="https://imgur.com/gZgtqbR.png"/>

<img src="https://imgur.com/9xPFfBH.png"/>

I will be testing against weak credentials so fire up burp suite and intercept the login request

<img src="https://imgur.com/ckSpHzv.png"/>

Send request to intruder

<img src="https://imgur.com/gQlfOqO.png"/>

Set the payloads for username and passowrd

<img src="https://imgur.com/MU8xkdH.png"/>

The first payload is for the usernames , I copied all the usernames found on mybb site

<img src="https://imgur.com/fq9bLyF.png"/>

The second payload is for the passwords which were weak credentials reported as a vulnerability in year 2021. Now let's start the attack.

<img src="https://imgur.com/8zgoUvZ.png"/>

Here we can see the lenght of the response for the `login successfully` message is 5982,6069 and in between this length so now let's sort out the moderators and admin from the credentials we got. We have the creds for the admin "ArnoldBagger" and a moderator "PalacerKing". So let's login as an administrator

<img src="https://imgur.com/ADYo0Le.png"/>

In the sent items we can see this intersting directory 

<img src="https://imgur.com/to2usIC.png"/>

<img src="https://imgur.com/rxCygpK.png"/>

Here the `modManagerv2.plugin` and `p.txt.gpg` is interesting



/devBuilds