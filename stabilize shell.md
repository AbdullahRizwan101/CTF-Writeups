---------------------------------
		CTF
---------------------------------

# Stablilize Shell
1) ctrl+z
2) stty raw -echo
3) fg (press enter x2)
4) export TERM=xterm

# Spawn bash
1) /usr/bin/script -qc /bin/bash 1&>/dev/null
2) python -c 'import pty;pty.spawn("/bin/bash")'
3) python3 -c 'import pty;pty.spawn("/bin/bash")'


# Finding Binaries

1) find . - perm /4000 (user id uid) 
2) find . -perm /2000 (group id guid)
----------------------------------
	      KoTH
----------------------------------

strace - debugging / tamper with processes
gbd  - c/c++ debugger
script - records terminal activites

w /who (check current pts ,terminal device)
ps -t ps/pts<number> (process monitoring)
script /dev/pts/<number>

cat /dev/urandom > /dev/pts/number

# Closing other shell

pkill -9 -t pts/number

# Changing file attributes

chattr + i <filename> (making file immutable)
chattr -i <filename> (making file mutable)
lschattr <filename>