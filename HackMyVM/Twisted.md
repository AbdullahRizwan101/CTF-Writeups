# HackMyVM-Twisted

## NMAP

```
Starting Nmap 7.80 ( https://nmap.org ) at 2021-01-12 09:38 PKT
Nmap scan report for 192.168.1.66
Host is up (0.00018s latency).
Not shown: 998 closed ports
PORT     STATE SERVICE VERSION
80/tcp   open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: Site doesn't have a title (text/html).
2222/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 67:63:a0:c9:8b:7a:f3:42:ac:49:ab:a6:a7:3f:fc:ee (RSA)
|   256 8c:ce:87:47:f8:b8:1a:1a:78:e5:b7:ce:74:d7:f5:db (ECDSA)
|_  256 92:94:66:0b:92:d3:cf:7e:ff:e8:bf:3c:7b:41:b7:5a (ED25519)
MAC Address: 08:00:27:72:46:36 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.92 seconds
```

## PORT 80

On the web page we see two images and one hinting being different so this means there is some stegnography invloved

<img src="https://imgur.com/RS8GTLK.png"/>

I ran`stegcracker` on both the images and found two messages

<img src="https://imgur.com/1ZY3C8U.png"/>

<img src="https://imgur.com/RtHfpUI.png"/>

<img src="https://imgur.com/p1nQnLf.png"/>

In `markus` directory we see a note which tells about bonita's ssh private key.

<img src="https://imgur.com/M4nBZHD.png"/>

Going to web directory we find a `gogo.wav` file so let's download it to our machine and analyze it !

<img src="https://imgur.com/eOwvhRd.png"/>

I uploaded this file as it was a morse code so analyzed it through online morese code analyzer and it was a rabbithole
<img src="https://imgur.com/yfMduF9.png"/>

So only option left for me was to run linpeas.

<img src="https://imgur.com/B5eLeWd.png"/>

I found that there was a capaiblity set on `tail` which is like a SUID.So id_rsa that we found for `bonita` we cannot read it but we can read it through tail command. Tail will print the last ten lines of a file so we need to specify to print last 30 or 40 lines so we can get the whole id_rsa key

<img src="https://imgur.com/5Plzg1R.png"/>

<img src="https://imgur.com/URtaWMW.png"/>

There is a SUID binary but when running it says WRONG CODE so let's transfer it to our machine and analyze the binary

<img src="https://imgur.com/tw9Gtn7.png"/>

So using ghidra I saw that it is comparing variable with a hex value 0x16f8

<img src="https://imgur.com/3mGEucD.png"/>

Convert the hex value to decimal value

<img src="https://imgur.com/5r857Zi.png"/>

<img src="https://imgur.com/aaqDZOO.png"/>