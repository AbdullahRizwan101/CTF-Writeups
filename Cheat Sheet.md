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

### Finding Binaries

* find . - perm /4000 (user id uid) 
* find . -perm /2000 (group id guid)

### Changing file attributes

chattr + i filename `making file immutable`<br/>
chattr -i filename `making file mutable`<br/>
lschattr filename `Checking file attributes`

# Windows Shell

### Adding User
net user "USER_NAME" "PASS" /add
### Changing User's password
net user "USER_NAME" "NEWPASS"
### Adding User to Administrators
net localgroup administrators "USER_NAME" /add


# King Of The Hill (KoTH)
#### Monitoring and Closing Shell
* strace `debugging / tamper with processes`
* gbd `c/c++ debugger`
* script - records terminal activites
* w /who `check current pts ,terminal device`
* ps -t ps/pts<number> `process monitoring`
* script /dev/pts/<number> `montior terminal`
* cat /dev/urandom > /dev/pts/pts-number  2>/dev/null `prints arbitary text on terminal`
* pkill -9 -t pts/pts-number
