# Vulnlab - Phantom

```bash
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?        
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped                               
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: phantom.vl0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
3389/tcp open  ms-wbt-server Microsoft Terminal Services
```

Enumerating smb shares with anonymous login

<img src="https://i.imgur.com/Evv31jT.png"/>

From the `public` share, we have tech support mail file

<img src="https://i.imgur.com/vt9SE33.png"/>

Which has a base64 encoded pdf file

<img src="https://i.imgur.com/qJdqgpB.png"/>

After decoding it from base64, we'll get a password from this file

<img src="https://i.imgur.com/QlxbcQv.png"/>

We don't have a username yet, so bruteforcing SIDs for the username using `lookupsid` from impacket

<img src="https://i.imgur.com/RsS8vjk.png"/>

Spraying the password on all these users, only `ibryant`  will be the account that has this password set

<img src="https://i.imgur.com/msLQ7Z0.png"/>

After logging onto `Departments Share` , there's a backup file in the IT folder

<img src="https://i.imgur.com/VVbWom5.png"/>

The `.hc` extension tells that it's file from veracrypt software, as the name tells it encrypts data, this password can be cracked with hashcat but it wasn't present in rockyou.txt, so generating a custom wordlist, with company name, year and a special character as mention in the hint from vulnlab wiki

<img src="https://i.imgur.com/2xtdq6b.png"/>

<img src="https://i.imgur.com/LqjRpAa.png"/>
Mounting the image with veracrypt

<img src="https://i.imgur.com/VzzOUF4.png"/>

<img src="https://i.imgur.com/nbNBV8Z.png"/>

There's a vyos backup file, which is an open source OS for router and firewall, from the config file, we can retreive the password for lstanely

<img src="https://i.imgur.com/ZZSNLJi.png"/>
<img src="https://i.imgur.com/TekNLZu.png"/>

<img src="https://i.imgur.com/iYogdOt.png"/>

Which didn't worked but we can spary this password against the list of domain users that we have

<img src="https://i.imgur.com/M76PK2L.png"/>

This user can login through winrm

<img src="https://i.imgur.com/xY1hPgN.png"/>

Enumerating the domain with bloodhound, we can change password for domain users with `ForceChangePassword`

<img src="https://i.imgur.com/xIXL5Rf.png"/>

<img src="https://i.imgur.com/LQjoEGt.png"/>

<img src="https://i.imgur.com/KHtCGSE.png">

These users belong to `ICT Security` group which have `AddAllowedToAct` on domain controller, through this we can edit `msDS-AllowedToActOnBehalfOfOtherIdentity` to add a machine account in this property to perform Resource Based Constrained Delegation (RBCD), with `net rpc` password can be changed

```bash
net rpc password WSILVA -U phantom.vl/svc_sspr -S dc.phantom.vl
```

<img src="https://i.imgur.com/cAIrUOs.png"/>

<img src="https://i.imgur.com/trNLszz.png"/>

Editing the msDS-AllowedToActOnBehalfOfOtherIdentity property

```bash
rbcd.py -delegate-to 'DC$' -delegate-from 'WSILVA' -dc-ip 10.10.118.204 -action 'write' 'phantom.vl'/'WSILVA':'Phantom2023!'
```

<img src="https://i.imgur.com/vIveqgn.png"/>

To abuse RBCD, we need to first know the status of machine qouta in order to create a machine account and then add to DC's property but qouta is set to 0

<img src="https://i.imgur.com/tGchn75.png"/>

However we can still perform RBCD through a normal domain user, for this we need a modified branch of getST with U2U kerberos extension https://github.com/ShutdownRepo/impacket/tree/getST

<img src="https://i.imgur.com/AAlzZTr.png"/>

Frist retrieving TGT with overpass-the-hash, extracting the TGT session key and replacing it with the domain user's NTHash

<img src="https://i.imgur.com/tlhwWCI.png"/>

With S4U2Self and U2U, with WSILVA we can obtain a service ticket to itself on behalf of administrator and then proceed to S4U2proxy to obtain a service ticket to the target the user can delegate to.

```bash
KRB5CCNAME=./WSILVA.ccache getST.py -u2u -impersonate "Administrator" -spn "host/dc.phantom.vl" -k -no-pass phantom.vl/WSILVA
```

<img src="https://i.imgur.com/h46FYKB.png"/>

# References

- https://github.com/lvaccaro/truecrack
- https://codeonby.com/2022/01/19/brute-force-veracrypt-encryption/
- https://www.thehacker.recipes/a-d/movement/kerberos/delegations/rbcd
- https://github.com/ShutdownRepo/impacket/tree/getST
- https://github.com/GhostPack/Rubeus/pull/137
