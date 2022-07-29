# Portswigger Insecure Deserialization - Lab 1

## Modifying serialized objects

In this lab we need to modify the session cookie which is using serlialization through which we need to escalate our privileges to administrator user and then delete the carlos user

<img src="https://i.imgur.com/kaGspTX.png"/>

We can login with the credentials `wiener:peter`

<img src="https://i.imgur.com/dtALDtP.png"/>

After logging in we'll see the session token

<img src="https://i.imgur.com/3MbdElV.png"/>

```
Tzo0OiJVc2VyIjoyOntzOjg6InVzZXJuYW1lIjtzOjY6IndpZW5lciI7czo1OiJhZG1pbiI7YjowO30%3d
```

Which is base64 encoded, we can decode this, I used cyberchef

<img src="https://i.imgur.com/MUd4vTf.png"/>

Now to understand the serlized cookie 

```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}
```

- `O:4` represents that `User` is a object of length 4, which has 2 attributes which are username and admin
- `username`  is a string of length `8`, which has the value `wiener` of length `6`
- `admin` is a string with length `5` which has a boolean value which is represented by `b` having the value `0` which is false

So we need to make this value true with `b:1`

<img src="https://i.imgur.com/FDEpRNF.png"/>

<img src="https://i.imgur.com/gghSrSP.png"/>

After refreshing the page we'll see that we have access to admin panel

<img src="https://i.imgur.com/4cubhe2.png"/>

And we can delete carlos user and complete the lab

<img src="https://i.imgur.com/W9kXxaY.png"/>

