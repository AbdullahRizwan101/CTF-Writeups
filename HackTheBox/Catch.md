# HackTheBox-Catch

## NMAP

```bash
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http Apache httpd 2.4.41 ((Ubuntu))
3000/tcp open  ppp?       
| fingerprint-strings:
|   FourOhFourRequest:
|     HTTP/1.0 404 Not Found
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: i_like_gitea=0eb9e22f84769b34; Path=/; HttpOnly                
|     Set-Cookie: _csrf=qeeMQU6Ir6U9YV6qRlnEuGDw_qQ6MTY0NzExMTgwNDEyODk2NTc1Nw; Path=/; Expires=Sun, 13 Mar 2022 19:03:24 GMT; HttpOnly; SameS
ite=Lax
|     Set-Cookie: macaron_flash=; Path=/; Max-Age=0; HttpOnly
|     X-Frame-Options: SAMEORIGIN
|     Date: Sat, 12 Mar 2022 19:03:24 GMT
|     <!DOCTYPE html>
|     <html lang="en-US" class="theme-">
|     <head data-suburl="">
|     <meta charset="utf-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1">
|     <meta http-equiv="x-ua-compatible" content="ie=edge">
|     <title>Page Not Found - Catch Repositories </title>
|     <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiQ2F0Y2ggUmVwb3NpdG9yaWVzIiwic2hvcnRfbmFtZSI6IkNhdGNoIFJlcG9zaXRvcmll
cyIsInN0YXJ0X3VybCI6Imh0dHA6Ly9naXRlYS5jYXRjaC5odGI6MzAwMC8iLCJpY29ucyI6W3sic3JjIjoiaHR0cDov
|   GenericLines, Help, SSLSessionReq: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 200 OK
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: i_like_gitea=c80803a2ab02d6cd; Path=/; HttpOnly
|     Set-Cookie: _csrf=29E07EOgvIM_KzVXS6nso7GG84s6MTY0NzExMTczMTQzMDI5NTEzMA; Path=/; Expires=Sun, 13 Mar 2022 19:02:11 GMT; HttpOnly; Same
5000/tcp open  upnp?
| fingerprint-strings: 
|   DNSVersionBindReqTCP, RTSPRequest, SMBProgNeg, ZendJavaBridge: 
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest: 
|     HTTP/1.1 302 Found
|     X-Frame-Options: SAMEORIGIN
|     X-Download-Options: noopen
|     X-Content-Type-Options: nosniff
|     X-XSS-Protection: 1; mode=block
|     Content-Security-Policy: 
|     X-Content-Security-Policy: 
|     X-WebKit-CSP: 
|     X-UA-Compatible: IE=Edge,chrome=1
|     Location: /login
|     Vary: Accept, Accept-Encoding 
|     Content-Type: text/plain; charset=utf-8
|     Content-Length: 28
|     Set-Cookie: connect.sid=s%3ARoyphBO72_t24uVW7T_YPTzcq7a8CU8t.5QVgNB%2FnNafCwZz0%2BnNn48mpy6GIhJvSBkiCFOXkqAg; Path=/; HttpOnly
|     Date: Sat, 12 Mar 2022 19:02:16 GMT
|     Connection: close
|_    Found. Redirecting to /login
8000/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
```

## PORT 80 (HTTP)

<img src="https://i.imgur.com/f5e10Yo.png"/>

On visiting this port we can see an options to download and click the button we get an android application, the login and signup buttons are just for show, doesn't really take us anywhere on clicking them

<img src="https://i.imgur.com/issQcaD.png"/>


## PORT 3000 (Gitea)

On this port we can see an instance of `gitea` running 

<img src="https://i.imgur.com/CrwEOpW.png"/>


## PORT 5000 (Let's Chat)

<img src="https://i.imgur.com/kbFCj5g.png"/>

On port 5000 there's a `let's chat` application hosted which is taken from this github repoistory which is a small team chat application  https://github.com/sdelements/lets-chat

## PORT  8000 (Cachet)

<img src="https://i.imgur.com/H0tXJrJ.png"/>

On port 8000 there's `Cachet` running which is an opensource status page system which tells about the status of the web application's components like website functional or is there any problem with the api being used 

## Analyzing the apk
We can do some static analysis on the apk through `MobSF` 

<img src="https://i.imgur.com/eYsmwSM.png"/>


We can find some tokens from this app as they are hardcoded in the application

<img src="https://i.imgur.com/dGhp1fj.png"/>

I spend so much time to make the git_tea token then moved to lets_chat_token at first when I looked at and thought that there isn't any api as the let's chat only display us a login page so I googled for let's chat token which led me to this that there's an api for this web app

<img src="https://i.imgur.com/xxz7K6P.png"/>

https://github.com/sdelements/lets-chat/wiki/API

This shows us that how we can authenticate to access these api end points

<img src="https://i.imgur.com/y0N0Soo.png"/>

<img src="https://i.imgur.com/9OXjWcc.png"/>

So making a request using `curl` with the header `'Authorization: Bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ=='` we can access the endpoints

```bash
curl -X GET http://10.10.11.150:5000/account -H 'Authorization: Bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ=='
```
	 
<img src="https://i.imgur.com/WYv6JDZ.png"/>

I checked the `messages` and `files` endpoint but it didn't reutrn any data

<img src="https://i.imgur.com/JvGUakP.png"/>

<img src="https://i.imgur.com/l3ylM5I.png"/>

Using the `rooms` end point it should us that there are three rooms , `Status` ,`Android Development` and `Employees`

<img src="https://i.imgur.com/zSnoskg.png"/>

So first checking the messages in `android_dev`

```bash
curl -X GET http://10.10.11.150:5000/rooms/android_dev/messages -H 'Authorization: Bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ==' | jq
```

<img src="https://i.imgur.com/ffpfjmP.png"/>

Nothing really in there moving onto `employees`

<img src="https://i.imgur.com/oIsgBXC.png"/>

This shows that a new employee is hired, so maybe now we'll get something juicy from last room we have left

```bash
curl -X GET http://10.10.11.150:5000/rooms/status/messages -H 'Authorization: Bearer NjFiODZhZWFk
OTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ==' | jq
```

<img src="https://i.imgur.com/Jj07DUP.png"/>

Using these creds on catchet login page

<img src="https://i.imgur.com/KpEin4M.png"/>

And we are logged in as john 

<img src="https://i.imgur.com/CcVpkpH.png"/>

After logging we can see catchet version which is `2.4.0-dev`

<img src="https://i.imgur.com/vTNHD0T.png"/>

Searching for vulnerabilites on catchet we can find a blog post talking about the three CVEs

https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection

 The first one `CVE-2021-39172 - Remote Code Execution` requires a poc and the redis service to be reachable which in this case doesn't fit in our scenario and the third one which is `CVE-2021-39173 - Forced Reinstall` didn't worked as well so this leads us to  `CVE-2021-39174 - Configuration Leak` which can leak the variables in `.evn` file, so checking out what the env file would have
 
 https://docs.cachethq.io/docs/installing-cachet
 
<img src="https://i.imgur.com/qCb9pOE.png"/>

## Foothold

We can leak variables `APP_KEY` which can be useful for getting a reverse shell but since there wasn't any straight forward way or proof of concept in the blog  to either leak the env variables or to get a reverse shell with this but anyways here's how we were able to leak the env variables (after a lot trial, error and swearing  )

<img src="https://i.imgur.com/Ojjsz1h.png"/>

First we need to intercept the request when saving the values in mail configuration 

<img src="https://i.imgur.com/HOuMAIz.png"/>

<img src="https://i.imgur.com/VLvGPkW.png"/>

Here we can see post parameter `mail_driver` so we need to change this parameter's value to `${APP_KEY}` and after that hit the `test` button which will get tested and the APP_KEY value will get stored in the logs

<img src="https://i.imgur.com/dM1stOs.png"/>

<img src="https://i.imgur.com/stN0uAX.png"/>

After this we will be shown a 500 status code but it's okay, after checking the logs we'll see that it has leaked the value of APP_KEY

<img src="https://i.imgur.com/apKlGYF.png"/>

But I wasn't able to figure out how would I use this to get a reverse shell so going back to see the default env file we can try leaking the password vairable, `DB_PASSWORD` is the one which seems promising

<img src="https://i.imgur.com/KYmPuQj.png"/>

We can try using this password for the usernames we got from the /users endpoint from let's chat api

<img src="https://i.imgur.com/m8cE3pN.png"/>

From which the password from DB_PASSWORD worked on `will`

<img src="https://i.imgur.com/9g88FWZ.png"/>

Running `sudo -l` to see what we can run as root user 

<img src="https://i.imgur.com/36z2QPf.png"/>

## Privilege Escalation

There wasn't anything else I could think of other than running `pspy` to see what cron jobs or processes was running as root user, so after transferring pspy we can see a script being ran `/opt/mdm/verify.sh` as root user

<img src="https://i.imgur.com/ghFePlq.png"/>

<img src="https://i.imgur.com/cpKOubo.png"/>

Starting with this script first it will check for apk file in `/opt/mdm/apk_bin` and will run a for loop to read all apk files in this directory and generate a 12 character long hex value using `openssl` so the filename becomes unique, after renaming it will move the apk file to `/root/mdm/apk_bin` 

After moving the apk file, it will perform three checks on the apk file

<img src="https://i.imgur.com/jiSMd8k.png"/>

<img src="https://i.imgur.com/niLeCpi.png"/>

The first check `sig_check` will check if apk is signed or not using `jarsigner`, if it isn't will ignore the apk by running the cleanup function which will remove the apk and the folder created for that apk

<img src="https://i.imgur.com/O6LztLF.png"/>

The second function `comp_check` ,will run `apktool` to decompile the apk with `d` and with `-s` will decode file resources to read the `AndroidManifest.xml` file to check the sdk version which should be greater then 18 meaning should be compatible with android version 4 and above it fails this check then it would run cleanup function and delete the file.

<img src="https://i.imgur.com/MQjtzwy.png"/>

The third function `app_check`, it will check application name from `strings.xml` that it must have "Catch" in it doesn't matter what contains before or after it and will run shell command after piping it to `xargs` 

```bash
echo -n $APP_NAME|xargs -I {} sh -c 'mkdir {}'
```

Which means that we can do command injection in the application name, so what we need do here is modify the catch1.0.apk that we got from the website, decompile it using apktool and change the application name, make sure to use the updated apktool which is 2.6.1 because buldiing the application after decompiling the resources wouldn't work with apktool 2.5.0

https://github.com/iBotPeaches/Apktool/releases/tag/v2.6.1

And to make apktool 2.6.1 to execute directly, remove the one from /usr/bin/, since this is a jar file we can convert it to executable by following this 

https://stackoverflow.com/questions/44427355/how-to-convert-jar-to-linux-executable-file

<img src="https://i.imgur.com/1ZHvbu9.png"/>

This step isn't really needed it's just what I found useful for future purpose

<img src="https://i.imgur.com/HrGVUhk.png"/>

After decompiling the apk, we can find strings.xml in `./res/values`

<img src="https://i.imgur.com/iETIo50.png"/>

<img src="https://i.imgur.com/y23smPe.png"/>

<img src="https://i.imgur.com/L3hZqdZ.png"/>

Here we have placed a simple command injection to make bash a SUID binary, after that we need to compile the apk by using `apktool b ./folder`

<img src="https://i.imgur.com/yXSNDcm.png"/>

The apk file will be saved in `dist` folder

<img src="https://i.imgur.com/jpm56R7.png"/>

We still need to sign it, jarsigner will show that this apk file is unsigned as we have modified this apk

<img src="https://i.imgur.com/yMEfU2m.png"/>

Following this post from stackoverflow

https://stackoverflow.com/questions/10930331/how-to-sign-an-already-compiled-apk

```bash
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
```

<img src="https://i.imgur.com/si9bKRs.png"/>

After generating keystore file, we can use jarsigner to sign the apk

```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore catchv2.0.apk alias_name
```

<img src="https://i.imgur.com/uOPvgOW.png"/>

<img src="https://i.imgur.com/qhkVgah.png"/>

Running jarsigner again to check if the apk is signed

<img src="https://i.imgur.com/7buSDSX.png"/>

Transferring the apk file on the machine

<img src="https://i.imgur.com/kFreQ9V.png"/>

<img src="https://i.imgur.com/J0Y4mnp.png"/>

Within a minute we'll see that bash has a SUID and we can then become root user by running bash with `bash -p`

<img src="https://i.imgur.com/jrbXWwu.png"/>



## References
- https://github.com/sdelements/lets-chat/wiki/API
- https://blog.sonarsource.com/cachet-code-execution-via-laravel-configuration-injection
- https://docs.cachethq.io/docs/installing-cachet
- https://github.com/iBotPeaches/Apktool/releases/tag/v2.6.1
- https://stackoverflow.com/questions/44427355/how-to-convert-jar-to-linux-executable-file
- https://stackoverflow.com/questions/10930331/how-to-sign-an-already-compiled-apk
