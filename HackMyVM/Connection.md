# HackMyVM-Connection

## NMAP

```
Nmap scan report for adroit.local (192.168.1.7)                           
Host is up (0.000068s latency).                                           
Not shown: 65531 closed ports                                             
PORT    STATE SERVICE     VERSION                                         
22/tcp  open  ssh         OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                                                            
| ssh-hostkey:                       
|   2048 b7:e6:01:b5:f9:06:a1:ea:40:04:29:44:f4:df:22:a1 (RSA)                                                                                      
|   256 fb:16:94:df:93:89:c7:56:85:84:22:9e:a0:be:7c:95 (ECDSA)                                                                                     
|_  256 45:2e:fb:87:04:eb:d1:8b:92:6f:6a:ea:5a:a2:a1:1c (ED25519)                                                                                   
80/tcp  open  http        Apache httpd 2.4.38 ((Debian))                  
|_http-server-header: Apache/2.4.38 (Debian)                              
|_http-title: Apache2 Debian Default Page: It works                       
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)                                                                               
445/tcp open  netbios-ssn Samba smbd 4.9.5-Debian (workgroup: WORKGROUP)                                                                            
MAC Address: 08:00:27:43:41:50 (Oracle VirtualBox virtual NIC)                                                                                      
Service Info: Host: CONNECTION; OS: Linux; CPE: cpe:/o:linux:linux_kernel       
Host script results:                 
|_clock-skew: mean: 1h40m00s, deviation: 2h53m12s, median: 0s                                                                                       
|_nbstat: NetBIOS name: CONNECTION, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)                                                       
| smb-os-discovery:                  
|   OS: Windows 6.1 (Samba 4.9.5-Debian)                                  
|   Computer name: connection                                             
|   NetBIOS computer name: CONNECTION\x00                                 
|   Domain name: \x00                
|   FQDN: connection                 
|_  System time: 2021-01-19T14:47:33-05:00                                
| smb-security-mode:                 
|   account_used: guest              
|   authentication_level: user                                            
|   challenge_response: supported                                         
|_  message_signing: disabled (dangerous, but default)                    
| smb2-security-mode:                
|   2.02:                            
|_    Message signing enabled but not required                            
| smb2-time:                         
|   date: 2021-01-19T19:47:33                                             
|_  start_date: N/A                  

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .                                                      
Nmap done: 1 IP address (1 host up) scanned in 14.27 seconds               
```

## PORT 80

<img src="https://imgur.com/u7OGWKm.png"/>

<img src="https://imgur.com/p4yVKT5.png"/>


I didn't find any directories through `gobuster`

## PORT 139/445 (SMB)

There is smb on the box so lets enumerate the shares and if we can read one of them

<img src="https://imgur.com/wwWWcYp.png"/>

There are three shares and hopefully we can read `share`

<img src="https://imgur.com/idHhwmi.png"/>

`html` is a directory so try to upload a reverse shell there and see if it gets uploaded

<img src="https://imgur.com/0c1RdPZ.png"/>

Perfect so by looking at `index.html` it seems this is a storage of web server 

<img src="https://imgur.com/vTyX6zZ.png"/>

<img src="https://imgur.com/7GwEcfv.png"/>

On stabilizing the shell and looking for SUID we find `gdb` which is not commonly set as SUID so go to GTFOBINS to see if we can escalate our privileges

<img src="https://imgur.com/DhP6bMR.png"/>

<img src="https://imgur.com/mjtqzYO.png"/>

We are root !!!