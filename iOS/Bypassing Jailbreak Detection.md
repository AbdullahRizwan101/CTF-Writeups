# iOS Pentesting - Bypassing Jailbreak Detection

For bypassing jailbreak detection I will be showcasing it through DVIA-2 , which is a vulnerable iOS application that teaches about various vulnerabilities and how to abuse them, I already have a jail broken iphone (I'll cover on how to jailbreak an iphone hopefully) and it's complicated, mostly ios is Semi-Untethered Jailbroken which means that it will need to be jailbroken again on either reboot or shutdown. The device which I am using is already jailbroken with `unc0ver` which jailbreaks versions 11.0 - 14.8 and the ios version I have is 12.5.5

## Installing IPA

We can install any third party IPA through `Cydia Impactor` , `3utools`  or `Sideloadly`, I'll go with Sideloadly now it does need an apple developer ID to bind it with the IPA as there are a lot of restrictions in an iphone

![](https://linuxhint.com/install-neo4j-ubuntu/)
![](https://i.imgur.com/SRSGt5z.png)


After having it installed we can try exploring differnet vulnerabilities in an iphone application

![](https://i.imgur.com/adgdPhw.png)

But the focus of this post is bypassing jailbreak detection and SSL pinning so I'll try to cover jailbreak tests in this app

## Bypassing Jailbreak detection Using Liberty

These tests show a popup whether a device is jailbroken or not and some of the tests terminates the application on detection of jailbreak

![](https://i.imgur.com/ISGscDs.png)

I'll try to bypass jailbreak detection first through some tools like `ihide`  and `liberty-lite` but in this scenario only liberty was able to successfully bypass jailbreak detection on all checks so first install liberty through cydia which is a third party app store that gets installed during the jailbreak process

<img src="https://i.imgur.com/bTSHjXX.png"/>

Now go to settings, there you'll see liberty and toggle on block jailbreak detection

<img src="https://i.imgur.com/g0cugi9.png"/>

After launching the app we'll see that it bypass all checks for jailbreak detection

<img src="https://i.imgur.com/iduv63N.png"/>


## Bypassing Jailbreak Detection through Frida

To bypass this with frida, we need to first install frida through cydia and after installing, it will automatically start the frida-server so we don't have to start it by ourself, to verify that frida is running we can use list the processes running 

<img src="https://i.imgur.com/7VP7vHg.png"/>


```
frida-ps -Uia
```

<img src="https://i.imgur.com/PABRGxX.png"/>

So frida is working fine, we need to now inject a jailbreak detection bypass script from here 
https://gist.github.com/izadgot/5783334b11563fb08fee4cd250455ede

<img src="https://i.imgur.com/gLK6vBt.png"/>

```
frida -l ./jailbreak_bypass.js -f com.highaltitudehacks.DVIAswiftv2 -U
```

This will bypass all the checks implemented in this application it's not necessary that this will always work, on clicking any of the tests it will bypass the check for jailbreak detection by marking the return values as false for existence of Cydia, sshd binary, bash binary, apt and cydia package


<img src="https://i.imgur.com/gwLnlrk.png"/>


## Bypassing Jailbreak Detection through Objection

If it has been bypassed by frida script it can also be bypassed through objection as well 

```
objection -g explore com.highaltitudehacks.DVIAswiftv2
```

<img src="https://i.imgur.com/x7BngzU.png"/>

```
ios jailbreak disable
```

<img src="https://i.imgur.com/o0QZxbC.png"/>

<img src="https://i.imgur.com/laTC3np.png"/>


We can also change the boolean value of the function which is responsible for jailbreak detection for that need to search for jailbreak class


```bash
ios hooking search classes jailbreak
```

<img src="https://i.imgur.com/FJnoA9P.png"/>

Now we need to find the function name which detects jailbreak, for that we need to `watch` the methods used by JailbreakDetection class, clicking on any of the jailbreak test we'll get an output that `isJailbroken` function is being called  

```
ios hooking watch class JailbreakDetection
```

<img src="https://i.imgur.com/BMdLvaN.png"/>

<img src="https://i.imgur.com/XLPZ1BS.png"/>

Watching the method `isJailbroken`

```
ios hooking watch method "+[JailbreakDetection isJailbroken]" --dump-args --dump-backtrace --dump-return
```

Clicking the test again to trigger this fuction we'll get a return value of `1`  returning true, which means that device is jailbroken

<img src="https://i.imgur.com/gSxJRwX.png"/>

So we need to hook this function and set the return value to false which would return `0`

```
ios hooking set return_value "+[JailbreakDetection isJailbroken]" false
```

<img src="https://i.imgur.com/JhjOvSV.png"/>

<img src="https://i.imgur.com/jrvjiZ1.png"/>

And this would bypass jailbreak detection

## Bypassing Jailbreak Detection Through HideJB

HideJB is another application which can bypass jailbreak detection that is installed through cydia  which works similarly to liberty

<img src="https://i.imgur.com/dawxbzX.png"/>

<img src="https://i.imgur.com/KJeXnW3.png"/>

<img src="https://i.imgur.com/ANeSKdM.png"/>

Launch the DVIA-2 application and you'll see that this will bypass jailbreak detection as well

<img src="https://i.imgur.com/P3MB7pY.png"/>

There are some other tools which I didn't used for bypassing  detection including Shadow, Hestia and A-Bypass. in the next few articles I'll try to cover bypassing SSL pinning and some other vulnerabilities in iOS including dumping keychain and also jailbreaking iOS.

## References

- https://bypass.beerpsi.me/
- https://www.andnixsh.com/2020/10/how-to-bypass-jailbreak-detection.html
- https://www.techacrobat.com/bypass-jailbreak-detection/
- https://www.nowsecure.com/blog/2021/09/08/basics-of-reverse-engineering-ios-mobile-apps/
- https://gist.github.com/izadgot/5783334b11563fb08fee4cd250455ede
- https://unc0ver.dev/
