# HackMyVM-Drifting Blues 6

## Netdiscover

<img src="https://imgur.com/cxDUTFc.png"/>


## Rustscan

```
rustscan -a 192.168.1.9 -- -A -sC -sV                                         
.----. .-. .-. .----..---.  .----. .---.   .--.  .-. .-.             
| {}  }| { } |{ {__ {_   _}{ {__  /  ___} / {} \ |  `| |                  
| .-. \| {_} |.-._} } | |  .-._} }\     }/  /\  \| |\  |
`-' `-'`-----'`----'  `-'  `----'  `---' `-'  `-'`-' `-'                  
The Modern Day Port Scanner.                                              
________________________________________                          
: https://discord.gg/GFrQsGy           :              
: https://github.com/RustScan/RustScan :                            
 --------------------------------------                                                                                                             
Nmap? More like slowmap.🐢          
                                                                          
[~] The config file is expected to be at "/root/.rustscan.toml"
[!] File limit is lower than default batch size. Consider upping with --ulimit. May cause harm to sensitive servers
[!] Your file limit is very small, which negatively impacts RustScan's speed. Use the Docker image, or up the Ulimit with '--ulimit 5000'.          

Open 192.168.1.9:80              


PORT   STATE SERVICE REASON         VERSION
80/tcp open  http    syn-ack ttl 64 Apache httpd 2.2.22 ((Debian))
| http-methods:                     
|_  Supported Methods: GET HEAD POST OPTIONS
| http-robots.txt: 1 disallowed entry  
|_/textpattern/textpattern
|_http-server-header: Apache/2.2.22 (Debian)
|_http-title: driftingblues

```

## PORT 80 (HTTP)

<img src="https://imgur.com/hJLrStv.png"/>

Seeing `robots.txt` 

<img src="https://imgur.com/VElot5S.png"/>

So we will be fuzzing for files with `.zip` extension

<img src="https://imgur.com/ennZ6Ft.png"/>

This archive is password protected so we need to crack the password

<img src="https://imgur.com/RvtSScX.png"/>

<img src="https://imgur.com/v0gnytc.png"/>

We are logged in 

<img src="https://imgur.com/Is0UbJy.png"/>

<img src="https://imgur.com/Ck4z3gi.png"/>

We have the ability to upload a file

<img src="https://imgur.com/e2qp3Fo.png"/>

<img src="https://imgur.com/nlZbK95.png"/>

Now we have a shell we could either use this or start a reverse shell

<img src="https://imgur.com/czDSmLa.png"/>

<img src="https://imgur.com/5QOlD6R.png"/>

Seeing the kernel version 

<img src="https://imgur.com/XtDISGH.png"/>

There's an exploit for this kernel 

<img src="https://imgur.com/NNMuTBW.png"/>

<img src="https://imgur.com/MLGTkcd.png"/>

Execute the kernel exploit

<img src="https://imgur.com/jrupEOv.png"/>

We are root 

<img src="https://imgur.com/Y1PItu1.png"/>
