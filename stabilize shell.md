# Stablilize Shell
1. ctrl+z
2. stty raw -echo
3. fg (press enter x2)
4. export TERM=xterm , for using `clear` command

# Spawn bash
* /usr/bin/script -qc /bin/bash 1&>/dev/null
* python -c 'import pty;pty.spawn("/bin/bash")'
* python3 -c 'import pty;pty.spawn("/bin/bash")'


# Finding Binaries

* find . - perm /4000 (user id uid) 
* find . -perm /2000 (group id guid)

# King Of The Hill (KoTH)

* strace `debugging / tamper with processes`
* gbd `c/c++ debugger`
* script - records terminal activites
* w /who `check current pts ,terminal device`
* ps -t ps/pts<number> `process monitoring`
* script /dev/pts/<number> `montior terminal`
* cat /dev/urandom > /dev/pts/<number> 2>/dev/null `prints arbitary text on terminal`

# Closing Shells/Sessions

pkill -9 -t pts/number

# Changing file attributes

chattr + i <filename> `making file immutable`
chattr -i <filename> `making file mutable`
lschattr <filename> `Checking file attributes`
