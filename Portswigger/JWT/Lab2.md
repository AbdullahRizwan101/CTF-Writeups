# Portswigger JWT - Lab 2

## JWT authentication bypass via flawed signature verification

In this lab we need bypass authuntication via flawed JWT signature verfication to become the administrator user by modifiying token and access `/admin` , we can login with the credentials  `wiener:peter` as a normal user

<img src="https://i.imgur.com/1PjGPnb.png"/>

<img src="https://i.imgur.com/quEHQKc.png"/>

<img src="https://i.imgur.com/ADQx4qt.png"/>

We can try accessing `/admin` , which only allows the `administrator` user to access it

<img src="https://i.imgur.com/B5Bwb7Z.png"/>

Checking the session cookie from developer tools

<img src="https://i.imgur.com/IMCZlid.png"/>

We can see a JWT token which can be analyzed by going to https://token.dev/

<img src="https://i.imgur.com/gHboZdR.png"/>

I tried modifying the name username to `administrator`

<img src="https://i.imgur.com/WlfQ2Kc.png"/>

But when changing the JWT it just logs out the user

<img src="https://i.imgur.com/GxIv8LQ.png"/>

It could be that it doesn't valid what algorithm is being used so we can try to set `alg` to `none`

<img src="https://i.imgur.com/fU9qIP8.png"/>

But also to add `.`  at the end of payload part

<img src="https://i.imgur.com/8i7IJu5.png"/>

<img src="https://i.imgur.com/ELdTvtZ.png"/>

After deleting carlos user we can solve the lab

<img src="https://i.imgur.com/4Dbgs5v.png"/>

