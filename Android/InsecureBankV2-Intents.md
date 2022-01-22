# Android Pentesting-Intents

When doing a black box pentesting for android , apart for looking at root detection bypass and ssl pinning looking for intents are also important , intents are the screens or activity of android application for example this InsecureBankv2 application has an activity for a login page which after logging in will show us avaiable options that we can do and the activity that is spawned after the login activity is called intent. Intent not only lies with in the same application it can take you to another activity from different appllications , let's say there's a youtube video link in your applicaiton when you click that it will either open up your browser application or youtube application , this is also an intent.

Now to abuse intent , specifically for this InsecureBankv2 applicaiton we need to first look at how many activities are there 

<img src="https://i.imgur.com/gxzbD8T.png"/>

Using `MobSF` we can analyze the applicaiton and can see that there are 10 activities  , to check which activities we can spawn withouit logging into application , there's a tool called `Drozer` which is similar to `frida` by working with the application during time but this has a feature to look which activites we can call explicitly

To do this we just need to setup drozer client on our host machine which I have previously showed in setting up the lab and install drozer agent on the android device

<img src="https://i.imgur.com/4gF9yk7.png"/>

<img src="https://i.imgur.com/MogY8lY.png"/>

Using the `list` command we can see the modules that we can use

<img src="https://i.imgur.com/kK8rUCr.png"/>

We can also see the activities manually or by using drozer by reading the manifest file

<img src="https://i.imgur.com/jcP5C26.png"/>

<img src="https://i.imgur.com/FcxLYpC.png"/>

Notice that some of the activites have `exported=True` which means that we can spawn these activities explicitly and rest of the activites do not have this property so we can't launch them on our own , this is a security issue because we can sometime bypass an activity which requires some kind of authentication or it's not authorized unless we can login

Running `app.package.attacksurface` this can show number of activities that have exported set to true

```bash
run app.package.attacksurface com.android.insecurebankv2
```

<img src="https://i.imgur.com/FKWbdgV.png"/>

We can check the activities that can be exported with this command

```bash
run app.activity.info -a com.android.insecurebankv2
```

<img src="https://i.imgur.com/ycDZZ86.png"/>

But this didn't worked for me when I tried doing it with drozer as no activity was launched 

<iimg src="https://i.imgur.com/eZtYDbC.png"/>

<img src="https://i.imgur.com/h10A4jQ.png"/>

An alternate to this is launching the activity through `adb`

```bash
adb shell am start -n com.android.insecurebankv2/com.android.insecurebankv2.ChangePassword
```

<img src="https://i.imgur.com/8UxDT1D.png"/>

We can lauch other activtiy which was for transfer amount 

<img src="https://i.imgur.com/7Vme6D6.png"/>

And with this we can launch activities which have exported property to true without being authorized and can abuse the flaw in the application however this can easily be mitigated by changing the `exported=true` to `exported=false`

## References

- https://github.com/FSecureLABS/drozer
- https://book.hacktricks.xyz/mobile-apps-pentesting/android-app-pentesting/drozer-tutorial
