# HackMyVM-Dominator

## NMAP

```
Nmap scan report for 192.168.1.6                                          
Host is up (0.00022s latency).                                            
Not shown: 998 closed ports                                               
PORT   STATE SERVICE VERSION                                              
53/tcp open  domain  (unknown banner: not currently available)                                                                                      | dns-nsid:                          
|_  bind.version: not currently available                                                                                                           
| fingerprint-strings:                                                                                                                              
|   DNSVersionBindReqTCP:                                                                                                                           
|     version                                                                                                                                       
|     bind                                                                                                                                          
|_    currently available            
80/tcp open  http    Apache httpd 2.4.38 ((Debian))                                                                                                 
|_http-server-header: Apache/2.4.38 (Debian)                                                                                                        
|_http-title: Apache2 Debian Default Page: It works                       
65222/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 f7:ea:48:1a:a3:46:0b:bd:ac:47:73:e8:78:25:af:42 (RSA)
|   256 2e:41:ca:86:1c:73:ca:de:ed:b8:74:af:d2:06:5c:68 (ECDSA)
|_  256 33:6e:a2:58:1c:5e:37:e1:98:8c:44:b1:1c:36:6d:75 (ED25519)
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/
submit.cgi?new-service :             
SF-Port53-TCP:V=7.80%I=7%D=1/11%Time=5FFC4A4A%P=x86_64-pc-linux-gnu%r(DNSV                                                                          
SF:ersionBindReqTCP,52,"\0P\0\x06\x85\0\0\x01\0\x01\0\x01\0\0\x07version\x                                                                          
SF:04bind\0\0\x10\0\x03\xc0\x0c\0\x10\0\x03\0\0\0\0\0\x18\x17not\x20curren                                                                          
SF:tly\x20available\xc0\x0c\0\x02\0\x03\0\0\0\0\0\x02\xc0\x0c");                                                                                    
MAC Address: 08:00:27:0D:8F:62 (Oracle VirtualBox virtual NIC)                                                                                      

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .                                                      
Nmap done: 1 IP address (1 host up) scanned in 25.75 seconds                 
```

## PORT 80

<img src="https://imgur.com/Ig54o0Y.png"/>


Fuzzing for directories didn't returned interesting for us other than robots.txt

<img src="https://imgur.com/aNc01hr.png"/>

Looking for `robots.txt` we find a domain name so there is a port 53 open we can check for zone transfer by that.

<img src="https://imgur.com/iocFe86.png"/>

## DNS Zone Transfer

<img src="https://imgur.com/afAK5hc.png"/>

Through TXT records we find a directory named `/fhcrefrperg`.But this wasn't a directory it was encrypted using a cipher so headed to cyberchef and check if it was ROT13 which was correct.

<img src="https://imgur.com/hwz7bWs.png"/>

<img src="https://imgur.com/bTj3ajI.png"/>

<img src="https://imgur.com/dThh6HT.png"/>

But this key was protected with a passphrase.

<img src="https://imgur.com/eUWzSn3.png"/>

Using ssh2john we got the hash for the `id_rsa` key now let's crack it with johntheripper

<img src="https://imgur.com/Dnb9aw3.png"/>

<img src="https://imgur.com/M4sWBCP.png"/>

And boom we are in !!!

## Privilege Escalation

Look for any SUID on the machine

<img src="https://imgur.com/qDEcp1k.png"/>
I found a article regarding exploiting systemctl service which has a SUID or can be run as sudo

https://medium.com/@klockw3rk/privilege-escalation-leveraging-misconfigured-systemctl-permissions-bc62b0b28d49

Now we can exploit `systemctl` by making a service and ruuning it with systemctl

<img src="https://imgur.com/d0XzIwr.png"/>

<img src="https://imgur.com/Q6nizZ6.png"/>