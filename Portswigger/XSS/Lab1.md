# Portswigger XSS-Lab 1

## Reflected XSS into HTML context with nothing encoded

In this lab we have to perform reflected cross site scripting (XSS) , first of all XSS is a vulnerability in web applications that is used to allow attackers to run javascript code on the application which can lead to running any malicious script generally they use this to steal cookies. There are 3 types of XSS , reflected , stored and DOM based XSS.

The task of this lab is this to exploit reflected XSS which allows anyone to include script within the `GET` parameter of the page through which the link can be sent to anyone and on opening that link it will executed the script or javascript code.

<img src="https://i.imgur.com/Hpisvcu.png"/>

We can try searching for something

<img src="https://i.imgur.com/1nMfAq4.png"/>

Here notice the url link 
```
https://ac281f821ff6626c80d28d9100f40098.web-security-academy.net/?search=ARZ
```

Here `?search=ARZ` , this is the GET parameter .We can try to execute javascript code like this

```javascript
<script>alert("This is XSS");</script>
```

<img src="https://i.imgur.com/2oIPN66.png"/>

And this popped up the dialog box meaning that this web application is vulnerable to Reflected XSS as we can add javascript code from the GET parameter in the url.

<img src="https://i.imgur.com/SSYm5XB.png"/>
