# PG-FunboxRookie

## NMAP

```bash

PORT   STATE SERVICE REASON         VERSION

21/tcp open  ftp     syn-ack ttl 63 ProFTPD 1.3.5e                      
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 anna.zip            
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 ariel.zip
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 bud.zip
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 cathrine.zip  
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 homer.zip
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 jessica.zip
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 john.zip
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 marge.zip
| -rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 miriam.zip
| -r--r--r--   1 ftp      ftp          1477 Jul 25  2020 tom.zip          
| -rw-r--r--   1 ftp      ftp           170 Jan 10  2018 welcome.msg      
|_-rw-rw-r--   1 ftp      ftp          1477 Jul 25  2020 zlatan.zip
22/tcp open  ssh     syn-ack ttl 63 OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:                                                            
|   2048 f9:46:7d:fe:0c:4d:a9:7e:2d:77:74:0f:a2:51:72:51 (RSA)            
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMD7EHN/CpFOxv4hW16hSiL9/hrqfgN7N5gfqvnRwCeDJ8jj4kzV9XNVm/NN3u+fE7zrclQWDtGRu4oryuQv+25XjPJG7z+OdJ6ncD8k/VyH
m3ncPIt1skZNTe8WGR9BGHf2dSvyEgW6Iu2TqICR+Vak48KdMIbmjCo8jbiAx4pNvUjkv7z+vzmr3wJakRhiIa2aA7TFeAVe5o9/Se6IOc/I4ByXcarmeU6hOytDb8qmUSYxSV1nea1jYKinXgCZ
7MpAoFB8qPtiy4wryzBgssjAiqAFPEmPjaU96hDAsGMeQ0yFLeCoDTxeY8xnc+oWjU/mm1ISbiJ/IqX2N81xtP
|   256 15:00:46:67:80:9b:40:12:3a:0c:66:07:db:1d:18:47 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBHG2MCQtlbU+bwb4Cuz2xWoPH4/WBRJtUP5pDp8LQM175mj/IP9ORztHIBB+dyfrCshyxnFcIF
c35MXp2qhgJFM=
|   256 75:ba:66:95:bb:0f:16:de:7e:7e:a1:7b:27:3b:b0:58 (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFhzTG7CoqPllLoboDB4lTrHUfFJLHbEWIRUP1lMA4rT
80/tcp open  http    syn-ack ttl 63 Apache httpd 2.4.29 ((Ubuntu))
| http-methods: 
|_  Supported Methods: HEAD GET POST OPTIONS
| http-robots.txt: 1 disallowed entry  
|_/logs/
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

```

From the nmap scan we see port 21 ,22 and 80 , so let's enumerate FTP first

## PORT 21 (FTP)

As we saw directory listing from nmap scan , anonmyous login is enabled

<img src="https://i.imgur.com/cV0cYzX.png"/>

We can do `ls -la` to see files 

<img src="https://i.imgur.com/nHzoOxe.png"/>

We have some zip files and two hidden files `@admin` and `@users` , we can download all these files using `mget *`

<img src="https://i.imgur.com/tMrrVlF.png"/>

All the archive files have the same size and asks the password , so reading the two other files we find base64 text and a mesage telling that passwords are old

<img src="https://i.imgur.com/wGWVDB3.png"/>

<img src="https://i.imgur.com/qlnTlBB.png"/>

That base64 text is nothing but the same mesage

<img src="https://i.imgur.com/fLJEc97.png"/>

## PORT 80 (HTTP)

The web server has default apache page but from the scan it revealed us that there's `robots.txt`

<img src="https://i.imgur.com/WaVa59f.png"/>

<img src="https://i.imgur.com/SjG9ECs.png"/>


<img src="https://i.imgur.com/5S34JY1.png"/>

Log doesn't exists so this is a proabably a rabbit hole

## PORT 22 (SSH)

I went through all zip files and running `fcrackzip` to crack thie password but I was able to crack `tom.zip`

<img src="https://i.imgur.com/qIq57Nf.png"/>

<img src="https://i.imgur.com/tpvMG9Z.png"/>

<img src="https://i.imgur.com/xdT1klt.png"/>

We can check `sudo -l` to see if we can run any commands as sudo but we don't know the password

<img src="https://i.imgur.com/X5Ojr2t.png"/>

If we try to use auto complete using `tab` key we are going to get this error

<img src="https://i.imgur.com/msbjaGz.png"/>

On printing the environment variable `$SHELL` we can see it's set to `rbash` which stands for restricted bash, restricted bash can be seen like this rbash and the purpose of rbash is to not allow you as a pentester to execute commands . There's a blacklist of commands like `python,bash,vi,vim,nano,less,cat,cd` that you won't be allowed to run and won't be able to spawn bash shell .

But in this case , it's not that restricted we can just set `$SHELL` to `/bin/bash`

<img src="https://i.imgur.com/pfqgcIe.png"/>

We see `.mysql_history` file and see that there's some quries written there

<img src="https://i.imgur.com/MwidLAP.png"/>

```sql
insert into support(tom,xx11yy22)!
```

So this `xx11yy22` maybe a password for user tom

<img src="https://i.imgur.com/7rJsGbG.png"/>

## References

- https://null-byte.wonderhowto.com/how-to/escape-restricted-shell-environments-linux-0341685/