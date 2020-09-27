# BsidesCTF-Mercury

This is a forensics category challenge and in this we are provided with a zip file 

```
root@kali:~/BsidesCTF/Forensics/Mercury# unzip mercury.zip 

```

After extracting it 

```
root@kali:~/BsidesCTF/Forensics/Mercury/mercury# cd .hg
root@kali:~/BsidesCTF/Forensics/Mercury/mercury/.hg# ls -la
total 88
drwxrwxr-x 5 root root  4096 Sep  5 04:24 .
drwxrwxr-x 3 root root  4096 Sep  5 04:24 ..
-rw-rw-r-- 1 root root    57 Sep  5 04:23 00changelog.i
drwxrwxr-x 2 root root  4096 Sep  5 04:24 cache
-rw-rw-r-- 1 root root 12301 Sep  5 04:24 dirstate
-rw-rw-r-- 1 root root    44 Sep  5 04:24 last-message.txt
-rw-rw-r-- 1 root root    59 Sep  5 04:23 requires
drwxrwxr-x 3 root root  4096 Sep  5 04:24 store
-rw-rw-r-- 1 root root 12301 Sep  5 04:24 undo.backup.dirstate
-rw-rw-r-- 1 root root     0 Sep  5 04:24 undo.bookmarks
-rw-rw-r-- 1 root root     7 Sep  5 04:24 undo.branch
-rw-rw-r-- 1 root root    11 Sep  5 04:24 undo.desc
-rw-rw-r-- 1 root root 12301 Sep  5 04:24 undo.dirstate
drwxrwxr-x 2 root root  4096 Sep  5 04:24 wcache

```
We find `last-message.txt` and on reading the file

`Y2U1ZmYzMWVhY2EyNWMwMzg1OTJhNGI3YjAxNGVjNDcK`

It looked like hex text so after converting it : `!....`



```
root@kali:~/BsidesCTF/Forensics/Mercury/mercury/.hg/store# ls -la
total 152
drwxrwxr-x 3 root root  4096 Sep  5 04:24 .
drwxrwxr-x 5 root root  4096 Sep  5 04:24 ..
-rw-rw-r-- 1 root root 42269 Sep  5 04:24 00changelog.i
-rw-rw-r-- 1 root root 32533 Sep  5 04:24 00manifest.i
drwxrwxr-x 2 root root 28672 Sep  5 04:24 data
-rw-rw-r-- 1 root root 10452 Sep  5 04:24 fncache
-rw-rw-r-- 1 root root    43 Sep  5 04:23 phaseroots
-rw-rw-r-- 1 root root    93 Sep  5 04:24 undo
-rw-rw-r-- 1 root root    71 Sep  5 04:24 undo.backupfiles
-rw-rw-r-- 1 root root 10400 Sep  5 04:24 undo.backup.fncache
-rw-rw-r-- 1 root root    43 Sep  5 04:24 undo.phaseroots
root@kali:~/BsidesCTF/Forensics/Mercury/mercury/.hg/store# cat phaseroots 
───────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: phaseroots
───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 1 d84fea9fd7bdd1bc08362adbba38a07443ce748d
───────┴────────────────────────────────────────────────────────────────────────────

```

This is SHA-1 Hash on cracking it `960cb04d1905bac1b33870f7c3ff0f2c53510619`


Now there is directory named `data` and there are bunch of files maybe `binary` files.

Run this command `ls | xargs strings`

This command will first list all files since we are piping it to xargs which can run operation on multiple files so I just ran strings to check any strings are there in file and boom 

`flag{version_control_for_the_solar_system}`

We got our flag.
