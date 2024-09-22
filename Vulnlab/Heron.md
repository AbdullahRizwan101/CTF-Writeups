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

Checking the access on smb shares with svc-web-account-d, there's write access on accounting share

<img src="https://i.imgur.com/jdFb9mk.png"/>
The accounting share has the application files including the web.config 

<img src="https://i.imgur.com/j3gUK7E.png"/>

# References

- https://www.hackingarticles.in/credential-dumping-group-policy-preferences-gpp/
- https://github.com/t0thkr1s/gpp-decrypt
