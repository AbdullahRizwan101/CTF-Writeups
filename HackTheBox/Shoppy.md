# HackTheBox - Shoppy

## NMAP

```bash
Nmap scan report for 10.10.11.180                                                                                                                                                                                                 
Host is up (0.12s latency).                                                                                                                                                                                                       
Not shown: 65532 closed tcp ports (reset)                                                                                                                                                                                         
PORT     STATE SERVICE  VERSION                                                                                                                                                                                                   
22/tcp   open  ssh      OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)                                                                                                                                                             
| ssh-hostkey:                                                                                                                                                                                                                    
|   3072 9e:5e:83:51:d9:9f:89:ea:47:1a:12:eb:81:f9:22:c0 (RSA)            
|   256 58:57:ee:eb:06:50:03:7c:84:63:d7:a3:41:5b:1a:d5 (ECDSA)           
|_  256 3e:9d:0a:42:90:44:38:60:b3:b6:2c:e9:bd:9a:67:54 (ED25519)         
80/tcp   open  http     nginx 1.23.1                                                                             
|_http-title: Did not follow redirect to http://shoppy.htb                
| http-methods:                                                                                                  
|_  Supported Methods: GET HEAD POST OPTIONS                                                                     
|_http-server-header: nginx/1.23.1                                                                               
9093/tcp open  copycat?                                                                                          
| fingerprint-strings:                                                                                           
|   GenericLines:                                                                                                
|     HTTP/1.1 400 Bad Request                                                                                   
|     Content-Type: text/plain; charset=utf-8                                                                    
|     Connection: close                                                                                          
|     Request                                                                                                    
|   GetRequest, HTTPOptions:                 
```

## PORT 80 

Visting the website, it redirects to `shoppy.htb` so, add this in `/etc/hosts` file

![](https://i.imgur.com/cEhZI7i.png)

![](https://i.imgur.com/qXKvzsZ.png)

The site just only shows a timer for a beta site

![](https://i.imgur.com/6PXuMPw.jpg)

Fuzzing for files and directories using `gobuster`, this finds `admin` which rredirects us to   `login` page also fuzzing for subdomain it finds `mattermost`

<img src="https://i.imgur.com/aiSGsi3.png"/>

![](https://i.imgur.com/AqOV6mv.png)

Adding the subdomain in /etc/hosts file

![](https://i.imgur.com/AoWDbti.png)

Visting the subdomain we'll get a login page which needs valid credentials so let's move back to the admin panel we had 

![](https://i.imgur.com/WgVxfhh.png)
![](https://i.imgur.com/kt8LdS3.png)


Checking for sql injection, it just doesn't respond if there's a single qoute `'` in username

![](https://i.imgur.com/gXJIEmh.png)

And just times out

<img src="https://i.imgur.com/78Y1y89.png"/>

So there's some filtering going on I guess as sqlmap doesn't work either

![](https://i.imgur.com/UitdmyK.png)

If we make an invalid request it will show a message about cannot GET the request which indicates that web application is using routes which usually how node js works

![](https://i.imgur.com/nHgBTib.png)

So this application is probably using node js, we can try looking for ways to bypass login on node js, for this I spent hours on search bypassing login on node and didn't find much, tried different payloads, read artices on bypassing but no dice. I found this article 

https://nullsweep.com/a-nosql-injection-primer-with-mongo/

## Foothold

From this article it explained using ``' || 'a'=='a`` which will make the query return true allowing us to login so our paylodad will be

```bash
admin' || 'a'=='a
```

![](https://i.imgur.com/chWrOCz.png)

![](https://i.imgur.com/W6t6KHk.png)

From the dashboard, we can search for users

![](https://i.imgur.com/sGxAKHA.png)

Which is also vulnreable to sqli

![](https://i.imgur.com/eWvykxQ.png)


On using the same sqli payload, we'll get `exports.json` file which has user's hashes, we can try cracking them if they are crackable

![](https://i.imgur.com/RWUQuYr.png)

Cracksation cracked `josh`'s hash but admin's hash wasn't crackable

![](https://i.imgur.com/o5GB2Yz.png)


Now using the credentials on mattermost, we'll get logged in and we can find the credentials which we can use on SSH from `Deploy Machine` channel

![](https://i.imgur.com/XkJ9T0p.png)

![](https://i.imgur.com/Z2WYHZU.png)

## Privilege Escalation (deploy)

WIth `sudo -l` we can check what permissions we have to run something as a privileged or other user

![](https://i.imgur.com/N7R7K86.png)

This shows that we can run `password-manager` with `deploy` user but this binary asks for a password which we don't know 

![](https://i.imgur.com/Pfg90x4.png)

For this we need to reverse the binary through `ghidra`

![](https://i.imgur.com/C1HeEOp.png)

This shwos us the string `Sample` which is being comapred to our input and allow us to read `/home/deploy/creds.txt` if it's the matches with it

![](https://i.imgur.com/D5KoY53.png)

So we can enter Sample as the password which will return the contents of creds.txt from deploy's home directory

![](https://i.imgur.com/crDN1IG.png)

We can use this password to switch to deploy user

![](https://i.imgur.com/yU4YoiM.png)

## Privilege Escalation (root)

From the id ouput, this user is in `docker` group so we can abuse that by mounting `chroot (/)` of the host machine in `/mnt`  and spawn an apline container executing commands so we can spawn bash 

![](https://i.imgur.com/BmKfRGp.png)

```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt bash
```

![](https://i.imgur.com/ypBNH7t.png)

## References

- https://book.hacktricks.xyz/pentesting-web/login-bypass
- https://www.stackhawk.com/blog/node-js-sql-injection-guide-examples-and-prevention/
- https://nullsweep.com/a-nosql-injection-primer-with-mongo/
- https://gtfobins.github.io/gtfobins/docker/


