# TryHackMe- Super-Spam

First of all let's check for open ports on the machine so I will be running rustscan

## Rustscan

<img src="https://imgur.com/BzKBX8m.png"/>

It showed us 3 ports , port 80 is for HTTP but we don't know about the other two so let's wait for the scan to complete

<img src="https://imgur.com/TLiQYED.png"/>

It showed us that port 4012 is `SSH` and port 4019 is `FTP` so let's start enumerating FTP first



### PORT 4019 (FTP) 

<img src="https://imgur.com/99nzC8I.png"/>

We can a `.cap` folder , `IDS_logs` and a `note.txt` reading that note 

```
12th January: Note to self. Our IDS seems to be experiencing high volumes of unusual activity.
We need to contact our security consultants as soon as possible. I fear something bad is going
to happen. -adam

13th January: We've included the wireshark files to log all of the unusual activity. It keeps
occuring during midnight. I am not sure why.. This is very odd... -adam

15th January: I could swear I created a new blog just yesterday. For some reason it is gone... -adam

24th January: Of course it is... - super-spam :)

```

It seems the blog has been hacker by someone , let's just dive into `.cap` as it was meant to be hidden

<img src="https://imgur.com/pg3OnLb.png"/>

This folder contain a lot of .cap files and a hidden note as well which says

```
It worked... My evil plan is going smoothly.
 I will place this .cap file here as a souvenir to remind me of how I got in...
 Soon! Very soon!
 My Evil plan of a linux-free galaxy will be complete.
 Long live Windows, the superior operating system!

```
So this is refering to how he got in so it must be important to see what .cap file is and why it is important to him , google says that 

```
the CAP file extension is most likely a Packet Capture file created by packet sniffing programs
```

Now looking at the name `SamsNetwork` this maybe a capture file related to WIFI also opening the file with wireshark it includes a TP-Link router

<img src="https://imgur.com/d10G7eB.png"/>

So this confirms that this is a file containing WIFI handshake. We can crack the password of the wifi with `aircrack-ng` or by converting this file to hashcat's format of cracking WPA2 passwords

<img src="https://imgur.com/k9a0Nax.png"/>

<img src="https://imgur.com/erIoEUy.png"/>

And we got a password `sandiago` so now let's visit the web page

## PORT (80)

We can find the web flag in `robots.txt`

<img src="https://imgur.com/70zQ5TN.png"/>


<img src="https://imgur.com/XVGdm6q.png"/>


I tried logging in with `Adam_Admin` but it failed so let's try logging in with other users with that password we cracked

<img src="https://imgur.com/5GyNbmr.png"/>

I found this username and try to login

<img src="https://imgur.com/4qSRxFL.png"/>

We logged in and looks like we are admin on this blog

<img src="https://imgur.com/nPy7Nk2.png"/>

We can go to `Reports` tab and can see that this is an outdated version of druapl cms so it might have some vulnerabilites

<img src="https://imgur.com/0ktsP7p.png"/>

Found RCE exploit for drupal_cms so let's test to see if it works

<img src="https://imgur.com/jiSVZ7y.png"/>

<img src="https://imgur.com/38vtxDo.png"/>

<img src="https://imgur.com/awWUqKI.png"/>

<img src="https://imgur.com/BcSAZ24.png"/>

<img src="https://imgur.com/loaD5Rb.png"/>


Now if we visit `http://ip/modules/drupal_rce/shell.php?cmd=id;` 

<img src="https://imgur.com/eNxUYeQ.png"/>

We can do remote code execution so let's just catch a reverse shell 

<img src="https://imgur.com/UDBfFL1.png"/>


If we check what permissions `www-data` has 

<img src="https://imgur.com/huW4QP5.png"/>

It can run symlink binary as root so we can exploit this by making a file having bash command in it then making a symlink with `ln` binary and run it as sudo so it will execute `bash`

<img src="https://imgur.com/gUnFpO8.png"/>