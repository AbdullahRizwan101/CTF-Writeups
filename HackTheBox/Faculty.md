# HackTheBox-Faculty

## NMAP

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://faculty.htb
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT 80 (HTTP)

Visting port 80 it reidrects to `faculty.htb`, so adding that in hosts file

<img src="https://i.imgur.com/0sRH0qp.png"/>

<img src="https://i.imgur.com/Irqlh0M.png"/>

I tried with a random ID number but it failed

<img src="https://i.imgur.com/gywUc2F.png"/>

On trying a sqli to bypass login it worked

<img src="https://i.imgur.com/J2lvlg7.png"/>

<img src="https://i.imgur.com/drCUZGg.png"/>

 I intercepted the request with burp to run sqlmap on the parameter to dump database

 <img src="https://i.imgur.com/AoScERj.png"/>

 But the issues it, it's time-based blind sqli so it;s going to take a lot of time in dumping data, in the meantime I ran `gobuster` to fuzz for files and directories which found `/admin` 

 <img src="https://i.imgur.com/PShV5vj.png"/>

 After bypassing login, we can just visit /admin to access the admin dashboard

 <img src="https://i.imgur.com/ygdxXtP.png"/>

 From the `Course List` we have an option to download the course list in pdf format

 <img src="https://i.imgur.com/1TRJV2n.png"/>

 <img src="https://i.imgur.com/xj5I1km.png"/>

 On intercepting the request we see base64 content in the `pdf` POST parameter

 <img src="https://i.imgur.com/zp6eZO8.png"/>

<img src="https://i.imgur.com/NFkYoyX.png"/>

Using cyberchef we can see that data is first being double URL encoded then base64 encoded and then generated into pdf format and it's just html data being converted

From the url it seems that it uses `mpdf`  which is a php library for generating pdfs, and from googling it seems that it's vulnerable to remote code execution but that requires a crafted image with php deserlization to be uploaded on the server 

https://github.com/mpdf/mpdf/issues/949

There was LFI (Local File Inclusion) through mpdf 

https://github.com/mpdf/mpdf/issues/356

This was found by Jonathan Bouman

https://medium.com/@jonathanbouman/local-file-inclusion-at-ikea-com-e695ed64d82f

So our payload will look like this

```bash
<annotation file="/etc/passwd" content="/etc/passwd"  icon="Graph" title="Attached File: /etc/passwd" pos-x="195"/>
```

<img src="https://i.imgur.com/HrjUd67.png"/>

<img src="https://i.imgur.com/FyjGITX.png"/>

<img src="https://i.imgur.com/73aOXI4.png"/>

Even tho the page looks empty but on clicking on the attachment it shows the `passwd` file

<img src="https://i.imgur.com/o0NsuYi.png"/>

<img src="https://i.imgur.com/vRuLx44.png"/>

From the passwd file we can see two users, `developer` and `gbyolo`

<img src="https://i.imgur.com/kLayohq.png"/>

I tried to read ssh keys of the users if they were readable and were there

<img src="https://i.imgur.com/ddFsKEC.png"/>

<img src="https://i.imgur.com/F9JKvGZ.png"/>

## Foothold (gbyolo)

Which failed, going back to login page, we can see the error message through sqli which reveals the full path of the php file

<img src="https://i.imgur.com/aVeO6eO.png"/>

<img src="https://i.imgur.com/uKX4rpV.png"/>

Placing the encoded content in the POST parameter again we'll get `admin_class.php`

<img src="https://i.imgur.com/ENZ4Yp0.png"/>

We can see it's including `db_connect.php` file which might be having credentials to database

<img src="https://i.imgur.com/i41P6DS.png"/>

<img src="https://i.imgur.com/05sVcYH.png"/>

<img src="https://i.imgur.com/ezEbcK2.png"/>

<img src="https://i.imgur.com/OGawptu.png"/>

Using the password `Co.met06aci.dly53ro.per` we can login through ssh as `gbyolo` user

<img src="https://i.imgur.com/A6ntN2p.png"/>

## Privilege Escalation (developer)


We can see a message on login `You have mail` , on checking `/var/mail/gbyolo` it tells that we can manage git repositories belonging to `faculty` group

<img src="https://i.imgur.com/wikA0JI.png"/>

Doing `sudo -l` we can run `meta-git` as `developer` user

<img src="https://i.imgur.com/40QcsCR.png"/>

I didn't find any files owned by faculty group but meta-git itself was vulnerable to remote code execution

https://hackerone.com/reports/728040

It doesn't sanitize user input so we can execute arbitary commands

<img src="https://i.imgur.com/sjkDB7J.png"/>

This user is in `debug` group and checking what files or folders does this group have access it to reveals that it can run `gdb` binary

<img src="https://i.imgur.com/TIsvd50.png"/>

## Privilege Escalation (root)
Checking the capbilites on this system it seems that gdb has `cap_sys_ptrace` through which we can inject commands into the process

https://book.hacktricks.xyz/linux-hardening/privilege-escalation/linux-capabilities#example-with-binary-1

<img src="https://i.imgur.com/8VfjDiO.png"/>

We need to fiind the process id (pid) of processes running as root user

<img src="https://i.imgur.com/lyZkEb2.png"/>

I first tried attaching the process of id of cron job ` 908`

<img src="https://i.imgur.com/LTrZfle.png"/>

<img src="https://i.imgur.com/Nal7Bn7.png"/>

But this didn't worked, next I looked for another root owned process which was running python3 with process id `730`

<img src="https://i.imgur.com/ZO0B6Uw.png"/>

<img src="https://i.imgur.com/wo7DbsH.png"/>

Attaching it to a python3 process makes it possible to execute system calls and we can execute arbitary commands, all that is left is to get a reverse shell

<img src="https://i.imgur.com/vmXj8d7.png"/>


## References

- https://security.snyk.io/vuln/SNYK-PHP-MPDFMPDF-73647
- https://github.com/mpdf/mpdf/issues/949
- https://github.com/mpdf/mpdf/issues/356
- https://www.youtube.com/watch?v=tbjtfGvym4M&ab_channel=byq
- https://medium.com/@jonathanbouman/local-file-inclusion-at-ikea-com-e695ed64d82f
- https://hackerone.com/reports/728040
- https://book.hacktricks.xyz/linux-hardening/privilege-escalation
- https://book.hacktricks.xyz/linux-hardening/privilege-escalation/linux-capabilities#example-with-binary-1
