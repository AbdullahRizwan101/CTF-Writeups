# echoCTF - pathfinder
This is an OS category challenge in which we are provided an IP address and a port to conenct using `nc` 

We can get the first flag by connecting with netcat and printing the evnironmental variables with `env`

<img src="https://i.imgur.com/iBZ0c0T.png"/>

## Privilege Escalation (curiosity)
On runnning `sudo -l` we can see that opportunity user can run `ls` binary as `curiosity` 

<img src="https://i.imgur.com/3AAl8Bd.png"/>

<img src="https://i.imgur.com/gyyBC3n.png"/>

Using this flag we can switch to curiosity user

## Privilege Escalation (insight)

Running `sudo -l` to see what we can run as other user , it seems that there's a custom binary named `insight` 

<img src="https://i.imgur.com/CiDsC1s.png"/>

On running this binary , it will print this message

<img src="https://i.imgur.com/scL7NIW.png"/>

Let's transfer this binary on to our host machine so that we can analyze what's going on in this binary

<img src="https://i.imgur.com/at9i510.png"/>

I used `ghidra` to analyze the binary , looking at the `main` function it's just setting the uid,gid and eid to 1005 (pathfinder user's id) and just printing a string 

<img src="https://i.imgur.com/Cwld3CE.png"/>

But we can see here that a shared library is being used , shared library is loaded by the program when it starts 

<img src="https://i.imgur.com/cERe1ED.png"/>

By following this article https://www.hackingarticles.in/linux-privilege-escalation-using-ld_preload/ , I used the same c langugage code , changed the root's id to insight's id which was 1004

```c
#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init() {
unsetenv("LD_PRELOAD");
setgid(1004);
setuid(1004);
system("/bin/sh");
}
```

Now to compile this

<img src="https://i.imgur.com/dsCOTSI.png"/>

Host the shared object file and transfer it to the target machine

<img src="https://i.imgur.com/wNjeIUx.png"/>

<img src="https://i.imgur.com/FsKgQe4.png"/>


## Privilege Escalation (pathfinder)

Running `sudo -l` again , we can see this user can run `pathfinder` binary , another custom binary 

<img src="https://i.imgur.com/4GRQYzf.png"/>

on running this in a directory where we don't have permissions to read file , it will give us an error that `ls` cannot open directory , which means that ls binary is being used here and it's possible that it isn't using it's absolute path i.e `/bin/ls` , here comes PATH variable exploit in which we create a fake `ls` binary which will invoke `bash` and for that we will need to add the path for our fake binary 

<img src="https://i.imgur.com/DZXyd8y.png"/>

## Privilege Escalation (ETSCTF)
Doing `sudo -l` with this user will show us that we can run `/usr/bin/env` which is used to print environmental variables as `ETSCTF` user 

<img src="https://i.imgur.com/eQ0OcLx.png"/>

Let's just visit GTFOBINS for this binary

<img src="https://i.imgur.com/9XJfbN8.png"/>

<img src="https://i.imgur.com/GGe94q0.png"/>
