# HackTheBox-Paper

## NMAP

```bash
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.0 (protocol 2.0)
| ssh-hostkey:                                                         
|   2048 10:05:ea:50:56:a6:00:cb:1c:9c:93:df:5f:83:e0:64 (RSA)
|   256 58:8c:82:1c:c6:63:2a:83:87:5c:2f:2b:4f:4d:c3:79 (ECDSA)
|_  256 31:78:af:d1:3b:c4:2e:9d:60:4e:eb:5d:03:ec:a0:22 (ED25519)   
80/tcp  open  http     Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
| http-methods: 
|   Supported Methods: POST OPTIONS HEAD GET TRACE
|_  Potentially risky methods: TRACE
|_http-title: HTTP Server Test Page powered by CentOS
443/tcp open  ssl/http Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
| http-methods: 
|_  Supported Methods: GET
| ssl-cert: Subject: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US
| Subject Alternative Name: DNS:localhost.localdomain
| Issuer: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-07-03T08:52:34
| Not valid after:  2022-07-08T10:32:34
| MD5:   579a 92bd 803c ac47 d49c 5add e44e 4f84
|_SHA-1: 61a2 301f 9e5c 2603 a643 00b5 e5da 5fd5 c175 f3a9
| tls-alpn: 
|_  http/1.1

```

## PORT 80/443 (HTTP/HTTPS)

<img src="https://i.imgur.com/NcYV9NX.png"/>

On web service we see a default web page which  tells that it's using centos, running `dirsearch` to fuzz for files and directories it only finds `manaul` and `cgi-bin`

<img src="https://i.imgur.com/byjRFT7.png"/>

And `cgi-bin` doesn't show anything there

<img src="https://i.imgur.com/Ag0s8lj.png"/>

So checking the response headers we see a domain `office.paper`  , so we'll need to add this domain in `hosts` file

<img src="https://i.imgur.com/3iwpbmp.png"/>

<img src="https://i.imgur.com/nQ6lSlY.png"/>

Now accessing the domain we see a web page which is using wordpress (from the output of wappalyzer extensions)

<img src="https://i.imgur.com/bs33AIG.png"/>

<img src="https://i.imgur.com/zD2T5a7.png"/>

Checking the blog post we find some usernames

<img src="https://i.imgur.com/O2bDRPc.jpg"/>

To enumerate wordpress further for users and plugins we can use `wpscan`

<img src="https://i.imgur.com/Mix5SBU.png"/>

<img src="https://i.imgur.com/trO6RLt.png"/>

Searching for vulns for this wordpress version there was

https://www.exploit-db.com/exploits/47690

<img src="https://i.imgur.com/ob2XweX.png"/>

So just by adding `?static=1` to the url would reveal the draft to us

<img src="https://i.imgur.com/sjdN8aG.jpg"/>

We get a subdomain  with a link to register  so add this subdomain in hosts file 

`http://chat.office.paper/register/8qozr226AhkCHZdyY`

<img src="https://i.imgur.com/oWKficA.png"/>

Here I tried to register an account

<img src="https://i.imgur.com/upGkoKt.png"/>

After creating an account we can read the chat and see that there's a bot that can allow us to perform local file read

<img src="https://i.imgur.com/wrbXzSx.png"/>

Since this chat is read only we can directly send command to bot that can read files

<img src="https://i.imgur.com/ycQFmMd.png"/>

This gives an error about cat command so  it's actually possible to do that

<img src="https://i.imgur.com/G3O6Rtf.png"/>

## Foothold

Interestingly we can also list files in the directory using `list` command and this way we can see the source code of the bot

<img src="https://i.imgur.com/bVFIBFP.png"/>

Listing contenst of `hubot` we see a `scripts` folder

<img src="https://i.imgur.com/AuvHBF1.png"/>

<img src="https://i.imgur.com/RsmSRPu.png"/>

There's a script `run.js` so this must be the source of this bot so taking a look at it would reveal that we can also run shell commands through `run`

<img src="https://i.imgur.com/HO2wBUS.png"/>

<img src="https://i.imgur.com/j0llnRr.png"/>

So let's just get a reverse shell from here , but this was an issue when I was trying to get a reverse shell as it was just getting hanged

<img src="https://i.imgur.com/KWJbJqL.png"/>

Instead we can just add our ssh key in `authorized_keys` file 

<img src="https://i.imgur.com/HpdXa6u.png"/>

We can confirm that the contents are written to authorized_keys file by listing `..ssh` directory

<img src="https://i.imgur.com/Ff7HFFH.png"/>

<img src="https://i.imgur.com/C7stgAG.png"/>

## Privilege Escalation

Now privesc in the box was the easier I have ever seen in a HTB machine , we can see as script named `pk.sh `, that was exploiting `polkit` and creating a new user named `hacked` with the password `password` , adding that user to sudoers file

<img src="https://i.imgur.com/qwaNn0U.png"/>

So running the script

<img src="https://i.imgur.com/gWThbsw.png"/>

<img src="https://i.imgur.com/hAtEsa5.png"/>

## References
- https://www.exploit-db.com/exploits/47690
- https://0day.work/proof-of-concept-for-wordpress-5-2-3-viewing-unauthenticated-posts/
