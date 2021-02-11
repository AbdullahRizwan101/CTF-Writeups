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

<img src="https://imgur.com/k2oRRlq.png"/>

<img src="https://imgur.com/gZgtqbR.png"/>

<img src="https://imgur.com/z39Pfvl.png"/>

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

Here we can see the lenght of the response for the `login successfully` message is 5982,6069 and in between this length so now let's sort out the moderators and admin from the credentials we got. We have the creds for the two moderators "ArnoldBagger" and "PalacerKing". 

<img src="https://imgur.com/ADYo0Le.png"/>

In the sent items we can see this intersting directory 

<img src="https://imgur.com/to2usIC.png"/>

<img src="https://imgur.com/rxCygpK.png"/>

Here the `modManagerv2.plugin` and `p.txt.gpg` is interesting.Now we need to find the password for decrypting the `p.txt.gpg` file so we can have a look at the plugin file

<img src="https://imgur.com/JEzPy3d.png"/>

`$sql_p = file_get_contents('inc/tools/manage/SQL/p.txt'); //read SQL password from p.txt`

This line is getting the sql password from that ecnrypted text file so we really need to decrypt it inorder to login into mysql and if we scroll down a little we maybe able to find the username 

<img src="https://imgur.com/orBLvaP.png"/>

So to summarize the stuff we had done uptill now , we bruteforced the passwords and got into a moderator account then from there we saw one of the email that lead us to /devBuilds then we saw an ecnrypted that we need to find a password for it so let's go back and see if we left something or not

<img src="https://imgur.com/wfWrQWl.png"/>

Going back to `/reportPanel.php` we find a hidden text which says the keymaker's message

<img src="https://imgur.com/uOt5RrW.png"/>

I didn't really understood what the message was but that binary text was our directory

<img src="https://imgur.com/Ofp9EUi.png"/>

<img src="https://imgur.com/cEK8sDB.png"/>

If we look closely into those chinese characters we can see some english letters `ofqxvg` then with these letters we perform permutation

<img src="https://imgur.com/hosykMT.png"/>

And we get a list of words from the permutation. Now we can covert this gpg file into a file that johntheripper can understand and then we can crack the hash with the wordlist we found so 

<img src="https://imgur.com/nSFHJnA.png"/>

Run this command to see where `gpg2john` is stored

<img src="https://imgur.com/kBEAIRj.png"/>

Save the hash in a file

<img src="https://imgur.com/rZxJcoC.png"/>

Then run john against the file with the wordlist

<img src="https://imgur.com/jm9fBKg.png"/>

Now we can connect to mysql with this password

<img src="https://imgur.com/56gxZdx.png"/>

<img src="https://imgur.com/1bSY32z.png"/>

<img src="https://imgur.com/wuoKJSE.png"/>

<img src="https://imgur.com/6Hmongd.png"/>

Here we can see login_key of `Ellie` but the question is what is a login_key so I found something on mybb community forums 

<img src="https://imgur.com/t3NOpec.png"/>

Also if see the cookies 

<img src="https://imgur.com/840t1hX.png"/>

We can see that `OoTfmlJyJhdJiqHXucrvRueHvGhE6LnBi5ih27KLQBKfigQLud` is the login_key for ArnoldBagger and the id for this user is 11

If we go back to `Team` we can see the super moderator is `BlackCat` with the user id 7 (we can count the id from seeing the members page)

<img src="https://imgur.com/GxVLBxe.png"/> 

<img src="https://imgur.com/xa0ln1K.png"/>

<img src="https://imgur.com/cK9L89Y.png"/>

And now we are logged in as BlackCat 

<img src="https://imgur.com/IIpYppo.png"/>
