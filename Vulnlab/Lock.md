# Vulnlab - Lock

```
PORT     STATE SERVICE       VERSION               
80/tcp   open  http          Microsoft IIS httpd 10.0
445/tcp  open  microsoft-ds?
3000/tcp open  ppp?
3389/tcp open  ms-wbt-server Microsoft Terminal Services
5357/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
```

## PORT 80

The webserver has template page hosted with just about section and nothing else

<img src="https://i.imgur.com/4lnStxV.jpeg"/>

## PORT 3000

On this port there's an instance of gitea being hosted, having a repository `dev-scripts`

<img src="https://i.imgur.com/lBiVOm4.png"/>

This repo has python script which is going to list down all the repository of the user with his `PAT` (Presonal Access Token).

<img src="https://i.imgur.com/D6w1iHX.png"/>

## Enumerating repoistories

Checking the commit history, we'll find gitea token

<img src="https://i.imgur.com/GCOhyqf.png"/>

<img src="https://i.imgur.com/8f7h3ph.png"/>

Copying the script on your local machine and using the token from commit history, the script will show another repo named `website`

<img src="https://i.imgur.com/Sh2aeEa.png"/>
Using the PAT we can clone this repo 

```bash
git clone http://43ce39bb0bd6bc489284f2905f033ca467a6362f@10.10.109.226:3000/ellen.freeman/website.git
```

<img src="https://i.imgur.com/VKQ93pt.png"/>

## Uploading webshell

The `readme.md` from the repo, says that any changes made into this repo will be deployed on the webserver, so let's verify by creating a simple html file

<img src="https://i.imgur.com/0UsKUIX.png"/>

Adding the created html file with `git add file.html` also setting the username and email with `git config --global`

```
git add uwu.html 
git config --global user.name "ellen.freeman"
git config --global user.email "ellen.freeman"
git commit -m "uwu"
git push
```

<img src="https://i.imgur.com/hzHzb9j.png"/>

Now this file will be deployed on the webserver

<img src="https://i.imgur.com/bRIzMFV.png"/>

Since IIS server is being used as a webserver (from the nmap scan), we can upload an aspx web shell https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/asp/cmd.aspx
 
<img src="https://i.imgur.com/vmTcTOm.png"/>

<img src="https://i.imgur.com/xyiPJyv.png"/>

Transferring nc and getting a shell

<img src="https://i.imgur.com/oJHkf6S.png"/>

<img src="https://i.imgur.com/tYNorxp.png"/>

Under documents directory, we'll find `config.xml` which has an encrypted password for mRemoteNG

<img src="https://i.imgur.com/ypRB2Ir.png"/>

Using the script to decrypt the password https://github.com/gquere/mRemoteNG_password_decrypt/blob/master/mremoteng_decrypt.py

<img src="https://i.imgur.com/TVoNRvF.png"/>
Having the credentials, we can login as `gale.dakarios` through RDP, after logging we can see `PDF24` launcher on desktop

<img src="https://i.imgur.com/nTYVyMk.png"/>

## Escalating privileges through PDF24

Checking the version, it appears to be 11.15.1, which is vulnerable to local privilege escalation

<img src="https://i.imgur.com/iN8Xh1m.png"/>

<img src="https://i.imgur.com/c00KqTT.png"/>

The vulnerabilities lies with in the repair process of PDF24, the process calls `pdf24-PrinterInstall.exe` which gets executed with SYSTEM privileges with write access on faxPrnInst.log, with `SetOpLock`  this file can then be blocked or to hold that file so the pdf24-PrinterInstall.exe will still remain open and we can then the perform the actions listed in the article

- right click on the top bar of the cmd window
- click on properties
- under options click on the "Legacyconsolemode" link
- open the link with a browser other than internet explorer or edge (both don't open as SYSTEM when on Win11)
- in the opened browser window press the key combination CTRL+o
- type cmd.exe in the top bar and press Enter


In C drive there's a hidden directory `_install` having pdf24 msi file

<img src="https://i.imgur.com/PJUC0tW.png"/>

Before running it make sure to have SetOpLock from here 
https://github.com/googleprojectzero/symboliclink-testing-tools

<img src="https://i.imgur.com/Tc7wtFX.png"/>

Now executing the installer file with msiexec

<img src="https://i.imgur.com/o2cMxxh.png"/>

After sometime, we'll get a cmd window for pdf24-PrinterInstall.exe

<img src="https://i.imgur.com/NeryrDx.png"/>

Opening the properties of this window and clicking on legacy consolemodel link to open with firefox

<img src="https://i.imgur.com/s0qcpFW.png"/>

Use `ctrl+o` to open up a file and at the address bar type cmd.exe to spawn a shell as SYSTEM user because this whole process is being executed in the context on that user

<img src="https://i.imgur.com/BkSCkpD.png"/>

<img src="https://i.imgur.com/haaOHv1.png"/>

# References

- https://kettan007.medium.com/how-to-clone-a-git-repository-using-personal-access-token-a-step-by-step-guide-ab7b54d4ef83
- https://github.com/tennc/webshell/blob/master/fuzzdb-webshell/asp/cmd.aspx
- https://github.com/gquere/mRemoteNG_password_decrypt/blob/master/mremoteng_decrypt.py
- https://sec-consult.com/vulnerability-lab/advisory/local-privilege-escalation-via-msi-installer-in-pdf24-creator-geek-software-gmbh/
- https://github.com/googleprojectzero/symboliclink-testing-tools

