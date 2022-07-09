# HackTheBox - RouterSpace

## NMAP

```bash
PORT   STATE SERVICE VERSION                         
22/tcp open  ssh     (protocol 2.0)                                      
| fingerprint-strings:                                                  
|   NULL:                                    
|_    SSH-2.0-RouterSpace Packet Filtering V1
80/tcp open  http                                      
| fingerprint-strings:                                     
|   FourOhFourRequest:                                      
|     HTTP/1.1 200 OK                                       
|     X-Powered-By: RouterSpace                              
|     X-Cdn: RouterSpace-41677               
|     Content-Type: text/html; charset=utf-8                                   
|     Content-Length: 76             
|     ETag: W/"4c-daU9QTsu+JmXzduj1YN/Vqx5tUc"                                  
|     Date: Sun, 27 Feb 2022 16:02:12 GMT
|     Connection: close
|     Suspicious activity detected !!! {RequestID: xJG p RrjCI GYGF c VrTe l }
|   GetRequest: 
|     HTTP/1.1 200 OK
|     X-Powered-By: RouterSpace
|     X-Cdn: RouterSpace-64002
|     Accept-Ranges: bytes
|     Cache-Control: public, max-age=0
|     Last-Modified: Mon, 22 Nov 2021 11:33:57 GMT
|     ETag: W/"652c-17d476c9285"
|     Content-Type: text/html; charset=UTF-8
|     Content-Length: 25900
|     Date: Sun, 27 Feb 2022 16:02:11 GMT

```

## PORT 80 (HTTP)

The web server has a template page which has a download option

<img src="https://i.imgur.com/n9klPP0.png"/>

This will download `routerspace.apk`

<img src="https://i.imgur.com/INlbPh1.png"/>
Now here I ran into a rabbithole or should I say had trouble in setting up the environment, there are two routes in getting a foothold one being reversing the application but issue is that this is react application and it's code is obfuscated, by decompiling the apk with `apktool` we can find `index.android.bundle` file which will have the obfuscated javascript code, I did tried to deobfuscate but couldn't deobfuscated it properly 

<img src="https://i.imgur.com/jSmZo0K.png"/>

<img src="https://i.imgur.com/AI3sNjR.png"/>

<img src="https://i.imgur.com/JWPaxqW.png"/>

We can use `js-beatufiy` to make the code a bit cleaner which can be installed through `npm`

<img src="https://i.imgur.com/AEaIsUQ.png"/>

<img src="https://i.imgur.com/HT72w5E.png"/>

<img src="https://i.imgur.com/cxwyhCT.png"/>

We do see some strings which tells the url but still I wasn't able to deobfuscate it and make the proper url or endpoint

## Foothold

Next was to run this application on android emulator, I like using `Genymotion` so setup a new device and make sure that you use android 7 because if your android  version is above 7 you'll face an issue when you'll try to intercept the requests being made by this application. So using an android 7 device we installed the application using `adb`

<img src="https://i.imgur.com/tiUboTb.png"/>

<img src="https://i.imgur.com/fhqUbbg.png"/>

Before running make sure to add a proxy setting to the WiFI access point

<img src="https://i.imgur.com/SL1v6gw.png"/>

Now run the application while having burpsuite to listen on all interfaces and intercept the request

<img src="https://i.imgur.com/TnF1iuo.png"/>

<img src="https://i.imgur.com/aDmKjEi.png"/>

<img src="https://i.imgur.com/B3zJBjz.png"/>

So we can do command injection here and get RCE, next we can just add our ssh public key in `/home/paul/.ssh/authorized_keys` file and login through ssh

<img src="https://i.imgur.com/34VpBQp.png"/>

Checking the source code of the application we can see why were able to command injection as it was executing it as a process

<img src="https://i.imgur.com/BSnVJ8y.png"/>

## Privilege Escalation

So for escalating privileges I didn't find any thing that I could abuse or saw any cronjobs running, so only option I could think of was running `linpeas` but all outbound traffic was blocked as I couldn't transfer linpeas from my machine 

<img src="https://i.imgur.com/spDU4Gz.png"/>

Copying the linpeas bash script and copy pasting it through clipboard was the only solution I could up with and then I ran the script which showed the sudoedit was vulnerable to a CVE know as `sudo Baron Samedit (CVE-2021-3156)`

<img src="https://i.imgur.com/oAU4nCB.png"/>


We can confrim that sudoedit is vulnerable as when we run sudoedit with `-s Y` it should not ask for password instead it should show us the usage options

<img src="https://i.imgur.com/bwMZ7b3.png"/>

But on the target machin it was asking for a password

<img src="https://i.imgur.com/SljaPZ9.png"/>

We can grab the exploit from here by copy pasting the exploit from clipboard

<img src="https://github.com/blasty/CVE-2021-3156"/>

<img src="https://i.imgur.com/su1iuuy.png"/>

Running `id` command we can see that we are root

<img src="https://i.imgur.com/uHwsdV5.png"/>

## References
- https://blog.assetnote.io/bug-bounty/2020/02/01/expanding-attack-surface-react-native/
- https://github.com/blasty/CVE-2021-3156
