# echoCTF - Anvil

This is an OS category challenge in which we are provided an IP address and a port to conenct using `nc` 

<img src="https://i.imgur.com/2yvvZOl.png"/>

We can find the first flag by printing the evnironmental variables using `env`

<img src="https://i.imgur.com/pZSPZEI.png"/>

## Privilege Escalation (silver)

Running `sudo -l` we can see that we are user `copper` and we can run `/sbin/debugfs` as `silver` user

<img src="https://i.imgur.com/yRvltDQ.png"/>

In this user's directory we can find the first flag

<img src="https://i.imgur.com/BjuWPg5.png"/>

## Privilege Escalation (gold)
Next we can again run sudo -l to see which commands we can run as other user and here we can run `/usr/bin/sftp` with `gold` user , now in order to escalate we need to have a ssh port running but here we can't open that port as we need root privileges so we can open ssh port on our host machine

<img src="https://i.imgur.com/KsP1RAz.png"/>

<img src="https://i.imgur.com/jWUGxFL.png"/>

<img src="https://i.imgur.com/R3bm2gU.png"/>

Following GTFOBINS we can spawn a bash shell

<img src="https://i.imgur.com/xTJtY8a.png"/>

<img src="https://i.imgur.com/u7fmZqU.png"/>

And in gold's home directory we can get the second flag.

## Privilege Escalation (ETSCTF)

Doing sudo -l again we can see that this user can run `/bin/bzless` as `ETSCTF` user

<img src="https://i.imgur.com/Xul6cMm.png"/>

bzless is similar to `less` binary but it's for viewing bzip2 compressed text  so we can try to pass a filename to it and then privesc similar to less 

<img src="https://i.imgur.com/uZ1ul2D.png"/>

<img src="https://i.imgur.com/EBAEmwP.png"/>

<img src="https://i.imgur.com/uIBSEoD.png"/>

<img src="https://i.imgur.com/ecmDVEt.png"/>
