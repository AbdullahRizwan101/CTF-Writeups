# echoCTF - Cretin

We can find the first flag by printing the environmental variable `env`after connecting with `nc`

<img src="https://i.imgur.com/W3pfD6y.png"/>

## Privilege Escalation (dribble)

Running `sudo -l` we can see that this user can run`ed` binary as `dribble` user

<img src="https://i.imgur.com/yUcCpkO.png"/>

So looking at GTFOBINS 

<img src="https://i.imgur.com/xCVTDQ4.png"/>

<img src="https://i.imgur.com/gH0MIhH.png"/>

## Privilege Escalation (scribble)
Again running sudo -l we can see this user can now run `capsh` binary as `scribble` user

<img src="https://i.imgur.com/CKRs4Zu.png"/>

<img src="https://i.imgur.com/CQCgPnI.png"/>

## Privilege Escalation (ETSCTF)

This is the last priv esc that we need to do , we can run `whiptail` as `ETSCTF` user

<img src="https://i.imgur.com/d0E4RS4.png"/>

<img src="https://i.imgur.com/epD2yyq.png"/>

Running that we will get ambiguous redirect , so this isn't actually a binary but a script which is running the actual whiptail binary

<img src="https://i.imgur.com/YnGY3XY.png"/>

We just need to specify the file name to read as the privesc is already included here 

<img src="https://i.imgur.com/3plgxnf.png"/>

<img src="https://i.imgur.com/VfmywhW.png"/>
