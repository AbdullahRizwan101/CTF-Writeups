# Android-Pentesting- Android Appsec (Kotlin) HTTP & HTTPS Traffic

Android Appsec is an intentionally made vulnerable application made by https://twitter.com/hpandro1337 for educating about securtiy in android applications for learning purposes so I will be taking a look into intercepting HTTP and HTTPS traffic which comes in SSL pinning and it's a security flaw that developers leave in their applications as if one could intercept the requests being made from the application he can read the secrets , plain text data if not encrypted 

<img src="https://i.imgur.com/mU3VSFw.png"/>


To intercept the requets on burp suite we need to first install the certificate , this can be installed quite easilty.

You can follow this guide to install burp's certificate 

https://portswigger.net/support/installing-burp-suites-ca-certificate-in-an-android-device

After installing the certificate , make sure that your burp's listener is running on all interfaces

<img src="https://i.imgur.com/TxlPb6K.png"/>

Add the IP address of your host machine in the network's proxy configuration

<img src="https://i.imgur.com/nUDU52U.png"/>

Now let's test this to see if we can intercept HTTP traffic

## Intercepting HTTP Traffic

As we click on Reload button while having the intercept turned on we can intercept the request 

<img src="https://i.imgur.com/ID0GD5k.png"/>

Send the request to repeater to get the response

<img src="https://i.imgur.com/dEmXlGj.png"/>


## Intercepting HTTPS Traffic

Now intercepting https traffic may or maynot be easy as this is where ssl pinning comes in 

<img src="https://i.imgur.com/snJxUaY.png"/>

As you can see this is not intercepting https traffic even tho we have added the burp certificate , so it will only allow the https traffic only through a trusted certificate so we need to bypass this , this can bypassed through `objection`

```
objection --gadget com.hpandro.androidsecurity explore
```

```
android sslpinning disable
```

<img src="https://i.imgur.com/mv8ol6j.png"/>

Now if we try to intercept it , it will work

<img src="https://i.imgur.com/eyExK2m.png"/>

<img src="https://i.imgur.com/jdZaWeR.png"/>

## References
- https://portswigger.net/support/installing-burp-suites-ca-certificate-in-an-android-device
