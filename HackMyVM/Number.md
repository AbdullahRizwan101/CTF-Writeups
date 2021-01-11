# HackMyVM-Number

## NMAP

```
Nmap scan report for 192.168.1.99
Host is up (0.00014s latency).
Not shown: 65533 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 2f:90:c5:7c:a1:62:89:3a:ec:ea:c3:51:fa:77:f8:3f (RSA)
|   256 8e:21:71:85:04:3d:a7:db:1d:e6:6f:16:27:0c:0d:c9 (ECDSA)
|_  256 e2:39:c7:eb:f2:6d:53:0f:fd:3c:2c:05:31:c9:5b:f2 (ED25519)
80/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
|_http-title: Site doesn't have a title (text/html).
MAC Address: 08:00:27:3B:F9:C5 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.55 seconds
```
## PORT 80

<img src="https://imgur.com/B3fu5k5.png"/>

I ran gobuster 

<img src="https://imgur.com/vPgWLPL.png"/>

Then I ran feroxbuster

<img src="https://imgur.com/9mimxWa.png"/>

But going to `whoami.php`

<img src="https://imgur.com/AexZHjr.png"/>

`command.php`

<img src="https://imgur.com/D5IIPBn.png"/>


All of this Lead to nowhere however we could bruteforce the pin using hydra for that we need to make a wordlists of numbers with a length of 4.

<img src="https://imgur.com/gxYm1VJ.png"/>

<img src="https://imgur.com/DSe4S4o.png"/>

<img src="https://imgur.com/mnB5WtU.png"/>

Now if we go back to `whoami.php`

<img src="https://imgur.com/jrVQHc6.png"/>

Go back to `/admin` and login as `melon` with the pin you found

<img src="https://imgur.com/bZn8nw0.png"/>

<img src="https://imgur.com/MDZg69J.png"/>

If we enter a string to check for rce it will show us a message that only numbers are allowed

<img src="https://imgur.com/eRt51P5.png"/>

Convert your IP address to decimal also launch wireshark and start analyze the network interface when you input the converted IP.

<img src="https://imgur.com/IKT51vS.png"/>

<img src="https://imgur.com/mhKuSn9.png"/>

Here I searched for target IP which is `192.168.1.99` which was trying to connect to port 4444 of our IP so we know that we need to listen for port 4444 on our netcat.

<img src="https://imgur.com/V8j4KKP.png"/>

Running linpeas I found capabilites

<img src="https://imgur.com/EOYQ1GE.png"/>

But these must be run as sudo

I guess the password of `melon` as `melon` and was logged in then I knew from the capability we found about `hping` search for escalation on gtfobins

<img src="https://imgur.com/4LiAdEa.png"/>

Then all I had to was to run it with sudo

<img src="https://imgur.com/Td90Myu.png"/>