# Android Pentesting-Bypassing Root Detection

For the deomonstartion of bypassing root detection I will be using a vulnerable apk known as `insecurebankv2` which is quite showcased in talks and presentations

# InsecureBankV2

This is a vulnerable bank application that I found from github (https://github.com/dineshshetty/Android-InsecureBankv2) which has a lot vulnerabilities that you can practice on 

<img src="https://i.imgur.com/X7fwqmj.png"/>

Download both the apk and `AndroLabServer.zip`

<img src="https://i.imgur.com/c5V9pCb.png"/>

I'll be using linux as for testing this application , and I have already installed tools like `drozer` , `MobSF` , `objection` and `frida` to analyze the application, to install this app we can use the command `adb install InsecureBankv2.apk`

<img src="https://i.imgur.com/a8ESa8c.png"/>

And going back to the device we can see that application is installed

<img src="https://i.imgur.com/bMMJ5Z4.png"/>

## Setting up the backend server

It was mentioned on github that in order for this app to work properly we need to run the androlab server , so we need to install the dependencies that the python script needs

<img src="https://i.imgur.com/OJjJPPw.png"/>

I tried installing through but for some reason it didn't worked , so I just manually installed modules when it prompted errors

```bash
python pip flask sqlalchemy simplejson web.py

```

And then run the python file with `python app.py`

<img src="https://i.imgur.com/5dXIRXw.png"/>

## Viewing the application

So now that application's backend server is running let's explore the application

<img src="https://i.imgur.com/EeJuZWn.png"/>

The first screen or the activity for this application is the login screen , so at the start it doesn't matter what we put because the application will ask for us to setup the IP address where the server is running

<img src="https://i.imgur.com/lMQbPSL.png"/>

<img src="https://i.imgur.com/sRnusUe.png"/>

Change the IP address according to the interface you have for internet connection , in my case I have wifi interface

<img src="https://i.imgur.com/IZ2KEW3.png"/>

<img src="https://i.imgur.com/CoWwpKx.png"/>

Credentials are already given for this application on the github page so let's use either one of the user 

<img src="https://i.imgur.com/MaRjvDu.png"/>

<img src="https://i.imgur.com/nl2uo5B.png"/>

Now to note that that after getting passed the login activity we'll another activity which will show 3 options , to transfer , view statement or change password also below it will show a text telling that our device rooted 

<img src="https://i.imgur.com/KaPaaGT.png"/>

Which is  where `Root Detection bypass` comes in , a lot of banking applications will try to detect if the device is rooted or not if it is then then application will not run so there are many methods avaiable to bypass root detection 

## Root Detection bypass

To bypass root detection I will be first showing to bypass it through `frida` script although we can try to use modules from EdXposed/Xposed or Magisk (which might not work ) also by decompiling the apk and modifiying the code , building the apk again and then signing the apk with a certificate

### Using Frida

Having frida already installed if it's not you can install it with `pip3 install frida` , also `pip3 intall frida-tools`, if you have `MobSF` installed then frida might be already installed

To start frida , transfer the frida android server binary on to the device through `adb push` , giving it executable permissions launch it then on the host machine run `frida-ps -U`

To inject script we either need to know the package name of the apk or the process ID

<img src="https://i.imgur.com/YVTMygl.png"/>

Using a universal bypass script for root detection we can try to see if we get lucky and save time by not reversing the apk file 

https://codeshare.frida.re/@dzonerzy/fridantiroot/

This is a universal script for bypassing root detecting it contains all possible checks that are used in applications to detect root 

Run the script against the app package name , and after running the command the application will start again with the script loaded and you'll see that it will bypass the check for rooted device

```bash
frida -U -f com.android.insecurebankv2 --codeshare dzonerzy/fridantiroot --no-pause
```

<img src="https://i.imgur.com/mwnm976.png"/>

<img src="https://i.imgur.com/z3O6V5I.png"/>

### Using Objection

<img src="https://i.imgur.com/empeabm.png"/>

Now I'll try to bypass root detection through objection which is a part of frida and is also to run scripts during runtime

Using the command

```bash
objection -g com.android.insecurebankv2 explore
```

This will lauch the application again , then type `android root disable` this will try to disable root detection which most likely would fail , it would show that file existence for `Superuser.apk` is being marked as false but it didn't worked

<img src="https://i.imgur.com/5uSmqbM.png"/>

<img src="https://i.imgur.com/Fea9TLT.png"/>

So we have to explicitly make it the function which is checking for superuser.apk and make it  return false and in order to do that we need to know name of the screen/activity and the method which is being called

It's pretty clear that a function is called after login so it will be listed in `com.android.insecurebankv2.PostLogin`

<img src="https://i.imgur.com/PlbmUjW.png"/>

These are two functions , the first one will check for `su` binary and second will check the superuser apk , both these functions will be returning a boolean value and as the status is "Device is rooted" it's returning `true` , so to make `doesSUexist` return `flase` we need to run this command

```bash
android hooking set return_value com.android.insecurebankv2.PostLogin.doesSUexist false
```

<img src="https://i.imgur.com/AhlY6Cf.png"/>

### Using EdXposed RootCloak

I have already shown the way to install EdXposed on the device however it's for version only from 8.0+ and EdXposed has a module called `RootCloak`

Install module enable it on which the device will ask to reboot enable this module

<img src="https://i.imgur.com/u3Z42sA.png"/>

After rebooting , launch the applicaion and add it in the list 

<img src="https://i.imgur.com/d8DJByx.png"/>

<img src="https://i.imgur.com/Aqr1ynu.png"/>

And rootcloak also bypasses root detection

### Using EdXposed Unrootbeer

Unrootbeer is an EdXposed module which is specially built for bypassing root detection on applications that are using RootBeer library for detecting root and in this case it will probably fail as this applicaiton isn't using any library to detect root

<img src="https://i.imgur.com/9pQSo3n.png"/>

<img src="https://i.imgur.com/s3Sevu7.png"/>

### Manually bypassing root detection

For static analysis I like to use `MobSF` which utilizes `jadex` to decomple apk which can also  make a report of things it has find also we can analyze the source code

<img src="https://i.imgur.com/h2dX0q6.png"/>

<img src="https://i.imgur.com/fY048Ux.png"/>

Here we need to provide the apk file and it will start analyzing it

<img src="https://i.imgur.com/EOA9Ni2.png"/>

<img src="https://i.imgur.com/m1elZLj.png"/>

Looking into the source code , we can search of strings in files so searching for the string `superuser` we can see there's only file that contains it which is `PostLogin.java`

<img src="https://i.imgur.com/rldHzGx.png"/>

<img src="https://i.imgur.com/y5oRh3a.png"/>

<img src="https://i.imgur.com/C1EzXHs.png"/>

If we look into our device `su` and superuser apk does exists 

<img src="https://i.imgur.com/cuWq0q9.png"/>

So to manually patch the apk , we need to decompile apk using `apktool` , modify the strings in smali file , recompile with apktool and sign the apk

<img src="https://i.imgur.com/dyrt3ls.png"/>

```bash
apktool d -r InsecureBankv2.apk
```

Where `d` is used for decompiling and `r` for not decoding resources file

<img src="https://i.imgur.com/DDL2sDn.png"/>

I ran `grep` to find the location of `PostLogin` file

<img src="https://i.imgur.com/d4TFlIq.png"/>

Encountering strings "su" , "Superuser" or anyother binary , append "info" or anything to the binary name

<img src="https://i.imgur.com/abD4VpY.png"/>

<img src="https://i.imgur.com/P6dkO6n.png"/>

<img src="https://i.imgur.com/WabNvcW.png"/>

After editing the strings ,verify there aren't any more strings 

<img src="https://i.imgur.com/LBM1BOE.png"/>

Now to recompile into apk

<img src="https://i.imgur.com/ekwcNEb.png"/>

The recompiled apk will be built in ./dist folder

<img src="https://i.imgur.com/b4FrTKp.png"/>

But before installing this , we need to sing the apk 

```bash
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000
```

<img src="https://i.imgur.com/D07nCll.png"/>

```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore InsecureBankv2.apk alias_name
```

<img src="https://i.imgur.com/M5H9Y1x.png"/>

Install the applicaiton and set the server IP again , and after logging in you will see that text says device is not rooted

<img src="https://i.imgur.com/hJcvvdT.png"/>


So these are some ways to bypass root detection however this was really simple as it was only looking for su binary and superuser application , it could also become more complex if  the source code is obfuscated and they are using libraries like `RootBeer` which can also be bypassed using the same approach. In the next post I'll try to cover some methods of SSL pinning in this application.

## References
- https://github.com/dineshshetty/Android-InsecureBankv2/releases/tag/2.3.1
- https://www.hebunilhanli.com/wonderland/mobile-security/root-detection-bypass/
- https://codeshare.frida.re/@dzonerzy/fridantiroot/
- https://github.com/jakev/unrootbeer
- https://book.hacktricks.xyz/mobile-apps-pentesting/android-app-pentesting/frida-tutorial/objection-tutorial
- https://stackoverflow.com/questions/10930331/how-to-sign-an-already-compiled-apk
