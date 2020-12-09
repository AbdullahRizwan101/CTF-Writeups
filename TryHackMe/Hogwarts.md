#TryHackMe-Hogwarts


## NMAP

```
Host is up (0.15s latency).                                                                                                                         
Not shown: 65529 closed ports                                                                                                                       
PORT      STATE SERVICE VERSION                                                                                                                     
22/tcp    open  http    Apache httpd 2.4.38 ((Debian))                                                                                              
|_http-server-header: Apache/2.4.38 (Debian)                                                                                                        
|_http-title: Site doesn't have a title (text/html).                                                                                                
|_ssh-hostkey: ERROR: Script execution failed (use -d to debug)                                                                                     
7631/tcp  open  ftp     vsftpd 3.0.3                                                                                                                
|_ftp-anon: Anonymous FTP login allowed (FTP code 230)                                                                                              
| ftp-syst:                                                                                                                                         
|   STAT:                                                                                                                                           
| FTP server status:                                                                                                                                
|      Connected to ::ffff:10.14.3.143                                                                                                              
|      Logged in as ftp                                                                                                                             
|      TYPE: ASCII                                                                                                                                  
|      No session bandwidth limit                                                                                                                   
|      Session timeout in seconds is 300                                                                                                            
|      Control connection is plain text                                                                                                             
|      Data connections will be plain text                                                                                                          
|      At session startup, client count was 3                                                                                                       
|      vsFTPd 3.0.3 - secure, fast, stable                                                                                                          
|_End of status                                                                                                                                     
7801/tcp  open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.10 (Ubuntu Linux; protocol 2.0)                                                               
| ssh-hostkey:                                                                                                                                      
|   2048 c6:66:16:67:fe:08:16:23:f3:a8:1f:ba:41:66:3e:7a (RSA)                                                                                      
|   256 de:e7:8a:3c:e5:03:93:cb:75:b9:2c:53:46:c9:57:02 (ECDSA)                                                                                     
|_  256 9a:5d:41:31:7b:dc:97:99:13:2a:06:14:52:a0:8f:71 (ED25519)                                                                                   
9999/tcp  open  abyss?                                                                                                                              
| fingerprint-strings:                                                                                                                              
|   FourOhFourRequest:                                                                                                                              
|     HTTP/1.0 200 OK
|     Date: Wed, 11 Nov 2020 22:17:15 GMT
|     Content-Length: 0
|   GenericLines, Help, Kerberos, LDAPSearchReq, LPDString, RTSPRequest, SIPOptions, SSLSessionReq, TLSSessionReq, TerminalServerCookie: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest, HTTPOptions: 
|     HTTP/1.0 200 OK
|     Date: Wed, 11 Nov 2020 22:17:14 GMT
|_    Content-Length: 0
10008/tcp open  http    PHP cli server 5.5 or later
|_http-title: Hogwart's Royal Entry
47880/tcp open  unknown
| fingerprint-strings: 
|   GenericLines: 
|     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|     /||\x20 \n // // || \x20 \n // // || \x20 \n // \x20 || // \n // \x20 || // \x20
|     \x20|| // \n ===========||===========
|     -------------------------------------------------------~~
|     -Antioch, Cadmus and Ignotus Peverell
|     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
|     Death took a price, but I tell you for free, 
|     gifts that I had, I gave to these 3..
|_    last sighted in hogwa
2 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bi
n/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)============== 
```
## PORT 22

<img src="https://imgur.com/DHAhh9i.png"/>
By default firefox has block default ports for services , in this case port 22 is for ssh and here it is being used for http so , let's add a property in 

`about:config`

https://superuser.com/questions/1272036/firefox-quantum-i-want-to-access-restricted-port-but-network-security-ports-b

<img src="https://imgur.com/fZHcxl8.png"/>

Now that we have added the porperty let's try refershing the page again


<img src="https://imgur.com/jsM6pMl.png"/>


## Gobuster

```
directories.jbrofuzz                     directory-list-2.3-small.txt             
root@kali:~/TryHackMe/KoTH/Hogwarts# gobuster dir -u http://10.10.159.157:22/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt 
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.159.157:22/
[+] Threads:        10
[+] Wordlist:       /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2020/10/31 23:34:36 Starting gobuster
===============================================================
/uploads (Status: 301)
/strona_3 (Status: 200)
/WhitePapers (Status: 200)
Progress: 67021 / 220561 (30.39%)^C
[!] Keyboard interrupt detected, terminating.

```


On visting `/WhitePapers` we can find base64 encoded text`c3VjdmN4eXJ1Nw==` on decoding it 

<img src="https://imgur.com/RQQmLiu.png"/>


`sucvcxyru7`


Now I tried to guess that this may be a directory and infact it was

<img src="https://imgur.com/0Ws99Wb.png"/>

I tried to upload a php reverse shell but it didn't work

<img src="https://imgur.com/3aziUSV.png"/>


## PORT 10008
We will get a login prompt on this port but entering any credentials you will get logged and see this

<img src="https://imgur.com/CCEi8rq.png"/>

Visting `robots.txt`

<img src="https://imgur.com/s8QCYAU.png"/>

<img src="https://imgur.com/Y95F72c.png"/>

```
Nothing of interest could be detected about the input data.
Have you tried modifying the operation arguments?
```

Also looking at the css file

<img src="https://imgur.com/xiEC8fx.png"/>

`Elder wand: !k@zmh7gx4vi6pm8gw8v9grlr`

## PORT 7801 (SSH)


## PORT 7631 (FTP)

We can log in with `anonymous` 

We find `.IamHidden` text file

```
root@kali:~/TryHackMe/KoTH/Hogwarts# cat .IamHidden 
Hagrid: You just don't understand do you? shoooooooo Go away! this is prolly a ded end!.. huh 
```


## PORT 47880