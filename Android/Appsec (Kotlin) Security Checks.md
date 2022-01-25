# Android-Pentesting- Android Appsec (Kotlin) Bypassing security checks

Android Appsec is an intentionally made vulnerable application made by https://twitter.com/hpandro1337 for educating about securtiy in android applications for learning purposes so I will be taking a look into bypassing checks for root detection , magisk , su , busybox , root cloak ,EdXposed/Xposed 

This applicaiton can be downloaded from here 
https://github.com/RavikumarRamesh/hpAndro1337/tree/main/Android%20AppSec%20(Kotlin)/1.2

<img src="https://i.imgur.com/mlZPkZR.png"/>

Going into root detection section it lists what it's checking for

<img src="https://i.imgur.com/CiIN3Bx.png"/>

This app also explains about root detection it's methods which is good

<img src="https://i.imgur.com/MXBROfo.png"/>

The first check that we have to bypass is for root management apps

## Bypassing Securtiy Checks

<img src="https://i.imgur.com/brWg2xK.png"/>

So what root management apps basically are that give root permissions to some applications that can run as a root user , the most commonly used apps are magisk and superuser 

<img src="https://i.imgur.com/Phokxpn.png"/>

We can see that on clicking `Check root` it lists these packages as they got detecte by this application as this emulator is rooted and has magisk installed. There are many ways that can bypass this check , could be by reversing the application understanding it's source code , making changes , compiling it back and sigining the apk with a certificate which can be a little time consuming so I went with using `Frida` which is a tool which runs at runtime and dynamically hooks the application

First we need to get the package name of the application by checking the running processes

<img src="https://i.imgur.com/dOL0OgC.png"/>

Make sure that frida is installed on your OS  , verify that frida is able to communicate with the android device by running `frida-ps -U` which will list the processes from the device 

<img src="https://i.imgur.com/mCzw7Wq.png"/>

Now that it's working we need to run a universal script for root detection bypass , there are plenty scripts available online you could also come up with your script but for now I am using this one 

https://codeshare.frida.re/@dzonerzy/fridantiroot/

```bash
frida --codeshare dzonerzy/fridantiroot -f com.hpandro.androidsecurity -U
```

As you'll run with a script it will prompt you to use `%resume`

<img src="https://i.imgur.com/2BhOCy0.png"/>

This will bypass all the checks for magisk ,su binary , busybox binary

<img src="https://i.imgur.com/9GiwVFG.png"/>

Now this bypassed the check for magisk application but failed to bypass for superuser which we would have to do it through objection or reversing the application but this will bypass most of the securtiy checks 


## Bypassed Dangerous Props

This will also bypass check for system property which is `ro.debuggable": "1"`  which allows users to debug the android application and  `ro.secure": "0"` which allows the device to run as root user so this must be changed to  `ro.debuggable": "0"` and  `ro.secure": "0"`

<img src="https://i.imgur.com/qKUL34M.png"/>

## Bypassed BusyBox Binaries

Busybox is a suite of linux binaries like `cat` , `chmod` , `wget` , actually most of the commonly used commands in linux , so frida script also bypasses this check

<img src="https://i.imgur.com/aC7AQbg.png"/>


## Bypassed Su Binary

Su is a command which is used to switch users in linux and this can be used to switch to root user , frida script also bypass this check as well

<img src="https://i.imgur.com/ODSi40w.png"/>


## Bypassed RW 

RW means read write and it's a security risk that a device can read and write in the following paths when it's rooted 

```
/system
/system/bin
/system/sbin
/vendor/bin
/sbin
/etc
```

<img src="https://i.imgur.com/IFZdNsD.png"/>

## Bypassed Root Cloaking 

Root cloaking apps are apps that are used for hiding root detection in the device , the commonly used apps are RootCloak and Xposed/EdXposed so this script bypasses this check as well

<img src="https://i.imgur.com/xyioHQU.png"/>

The checks that this script failed to bypass is for EdXposed which comes in `Potentially Dangerous Task` and Test keys

<img src="https://i.imgur.com/0myhknv.png"/>

<img src="https://i.imgur.com/aN5ZsOG.png"/>

## Bypassing Potentially Dangerous Task

Since frida script failed to bypass this check , we'll go with using objection which works with frida but provides more options and we can do much with it 

```bash
objection --gadget com.hpandro.androidsecurity explore
```

<img src="https://i.imgur.com/e9JhyfP.png"/>

Now we need to know the name of this activity , so we'll use this command to list all activities available in the application

```
android hooking list activities
```

<img src="https://i.imgur.com/dCbapx7.png"/>

This lists alot of activities but we only are concerned about dangerous task activity 

<img src="https://i.imgur.com/VJk5jzg.png"/>

Now that we have noted the activity name , we need to list the methods used in this activity which returns the check for apps that should not be on the rooted device

To load methods of the activity `com.hpandro.androidsecurity.ui.activity.task.rootDetection.PotentiallyDangerousTaskActivity` we need to first make sure that it's currently launched else it won't load the methods 

```
android hooking search methods com.hpandro.androidsecurity ui.activity.task.rootDetection.PotentiallyDangerousTaskActivity
```

<img src="https://i.imgur.com/YzROs2B.png"/>

But we don't know the what these methods return , we need to look for a method that returns either true or false when it detects applications from the list

```
android hooking list class_methods com.hpandro.androidsecurity.ui.activity.task.rootDetection.PotentiallyDangerousTaskActivity
```

<img src="https://i.imgur.com/4u35404.png"/>

Now we need to watch this `public final boolean com.hpandro.androidsecurity.ui.activity.task.rootDetection.PotentiallyDangerousTaskActivity.detectPotentiallyDangerousApps` method's arguments that what value does it return when it's called 

```
android hooking watch class_method com.hpandro.androidsecurity.ui.activity.task.rootDetection.PotentiallyDangerousTaskActivity.detectPotentiallyDangerousApps
 --dump-args --dump-backtrace --dump-return
```

<img src="https://i.imgur.com/qaXEXpj.png"/>

<img src="https://i.imgur.com/FXcuj0z.png"/>

This returned `True` so we need to make it return `False`

```
android hooking set return_value com.hpandro.androidsecurity.ui.activity.task.rootDetection.PotentiallyDangerousTaskActi
vity.detectPotentiallyDangerousApps false
```

<img src="https://i.imgur.com/qV5OMrt.png"/>

Now when hit the button to launch the method it will set the return value to false and thus bypassing this check

<img src="https://i.imgur.com/pvpbJ7t.png"/>

## Bypassing Test-Keys

There are two keys , `release-keys` and `test-keys` , release-keys mean that the android kernel version when it's compiled it's signed official keys and test-keys mean that kernel version is signed with a custom key or from a 3rd party 

So to bypass this we can follow the same procedure as we did for bypassing dangerous task by finding the activity name and listing the methods and the arguements

```
android hooking watch class_method com.hpandro.androidsecurity.ui.activity.task.rootDetection.TestKeysTaskActivity.check
FlagTestKeys --dump-args --dump-backtrace --dump-return
```

Picture here 

This returns true so we need to change this to false and this hopefully would bypass this check

Picture here 

And with this we have bypassed all security checks that were made in this applicaiton , however there's still about SafetyNet which provides set of services and APIs that help protect your app against security threats, including device tampering, bad URLs, potentially harmful apps, and fake users but this hasn't been implemented in this application so we'll be skipping this

One thing to note that we don't really need these tools to bypass root detection this all could be done by decompiling the apk and manually changing the strings in smali file which makes it easy to re-compile it back and sign the apk with a certificate.


## References

- https://codeshare.frida.re/@dzonerzy/fridantiroot/
- https://stackoverflow.com/questions/37143960/androidstudio-what-does-debuggable-do
- https://github.com/RavikumarRamesh/hpAndro1337/tree/main/Android%20AppSec%20(Kotlin)/1.2
- https://book.hacktricks.xyz/mobile-apps-pentesting/android-app-pentesting/frida-tutorial/objection-tutorial
- https://stackoverflow.com/questions/18808705/android-root-detection-using-build-tags
