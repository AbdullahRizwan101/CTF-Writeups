# Vulnlab - Retro2

```bash
PORT      STATE SERVICE
53/tcp    open  domain
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
445/tcp   open  microsoft-ds
593/tcp   open  http-rpc-epmap
3268/tcp  open  globalcatLDAP
3389/tcp  open  ms-wbt-server
5722/tcp  open  msdfsr
49154/tcp open  unknown
49156/tcp open  unknown
49173/tcp open  unknown
```


Enumerating smb shares will null authentication

<img src="https://i.imgur.com/T2Top5U.png"/>

We have `public` , which has two directories `DB` and `Temp`

<img src="https://i.imgur.com/wAtBYfH.png"/>

Temp directory has `staff.accdb` which is a microsoft access database file

<img src="https://i.imgur.com/yqYxFiv.png"/>

At the same time enumerating domain users by brute forcing their SIDs with `lookupsid.py` from impacket with guest account being enabled

<img src="https://i.imgur.com/FLq2jXN.png"/>

We could try AS-REP roasting on these accounts but first let's focus on the access database file that we have retrieved from the smb share

<img src="https://i.imgur.com/aWbM33m.png"/>

On opening this file on microsoft access, it will prompt us for password, with `office2john` we can get the hash of the access db file

<img src="https://i.imgur.com/xgWzc9I.png"/>

The hash can be cracked with john with the rockyou.txt wordlist

<img src="https://i.imgur.com/AFU0csW.png"/>

With the password we can now access the file and retrieve the password of `ldapreader`

<img src="https://i.imgur.com/cDD9Ikc.png"/>

Enumerating the shares with this user again to see if there's any write access that we have

<img src="https://i.imgur.com/aysV0e1.png"/>

Enumerating the domain with bloodhound  with `python-bloodhound`

<img src="https://i.imgur.com/XzIx3mw.png"/>

From bloodhound, it didn't showed any path leading to other domain users, however there's a group `PRE Windows 2000 Compatible Access` indicating that there might be a computer account assigned as pre windows 2000 account which means the password will be the same as the machine account in lowercase with the `$` symbol

<img src="https://i.imgur.com/2hMiEPL.png"/>

Verifying this through nxc

<img src="https://i.imgur.com/iAcY2x9.png"/>

The status `STATUS_NOLOGON_WORKSTATION_TRUST_ACCOUNT ` shows that the password is correct  but this has not been used so the password needs to be changed

<img src="https://i.imgur.com/u03r1OG.png"/>

The password can be changed with `kpasswd` but prior to that, `/etc/kr5.conf` needs to modified to add retro2.vl as domain realm 

```bash
[libdefaults]
        default_realm = RETRO2.VL
        dns_lookup_realm = false
        ticket_lifetime = 24h
        renew_lifetime = 7d
        rdns = false
        kdc_timesync = 1
        ccache_type = 4
        forwardable = true
        proxiable = true


[realms]        
        RETRO2.VL = {
                kdc = BLN01.RETRO2.VL
                admin_server = BLN01.RETRO2.VL

                                }
```

<img src="https://i.imgur.com/u79MpuQ.png"/>

Checking the bloodhound again for FS02

<img src="https://i.imgur.com/RBOwin7.png"/>

For abusing this, we can use `net rpc` to change the password of `ADMWS01` and add ldapreader to `Services` group through ADMWS01 using net rpc

<img src="https://i.imgur.com/UWskWMs.png"/>

```bash
net rpc password "ADMWS01$" -U "retro2.vl"/"fs02$" -S 10.10.90.65
```

Adding the user into services group

<img src="https://i.imgur.com/pU5y2To.png"/>

We can verify if the user has been added to services group

<img src="https://i.imgur.com/NvfR5iV.png"/>

On attempting to login through xfreerdp, it's going to show an error, tls connection failed due to how old the system was

<img src="https://i.imgur.com/vARlDlC.png"/>

Specifying `/tls-seclevel:0` we'll be able to login

```bash
xfreerdp /u:ldapreader /p:password /v:10.10.90.65 /tls-seclevel:0
```

<img src="https://i.imgur.com/bDLocDa.png"/>

# References

- https://www.thehacker.recipes/ad/movement/builtins/pre-windows-2000-computers
- https://medium.com/@offsecdeer/finding-weak-ad-computer-passwords-e3dc1ed220df
- https://www.thehacker.recipes/ad/movement/dacl/forcechangepassword
- https://www.thehacker.recipes/ad/movement/dacl/addmember
- https://github.com/asbru-cm/asbru-cm/issues/688


```
ldapreader:ppYaVcB5R
fs02:fs02
```

