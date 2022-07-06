# Portswigger JWT - Lab 1

## Athentication bypass via unverified signature

In this lab we need to bypass the implementation flaw of the JWT token to login as the admin user, we can login as the normal user with the credentials `wiener:peter`

<img src="https://i.imgur.com/M9fNRy1.png"/>

<img src="https://i.imgur.com/h2lEsQY.png"/>

We are now logged in as wiener

<img src="https://i.imgur.com/GyF9tlI.png"/>

Visiting `/admin` we can see a username `administrator`

<img src="https://i.imgur.com/Aie1Ld9.png"/>

To check the JWT token for this user we can go to developer tools, `storage` tab, we'll see the JWT in a `session` variable

<img src="https://i.imgur.com/72kQZTH.png"/>

We can analyze this token on the site https://token.dev/

<img src="https://i.imgur.com/m1DM1ar.png"/>

Although it shows `Signature Verification failed` we can still try to modify the username if the server doesn't check the verification of the JWT

<img src="https://i.imgur.com/MyG9BZK.png"/>

Now we need to replace the JWT with our forge JWT to become the administrator user

<img src="https://i.imgur.com/JdNjCiM.png"/>

<img src="https://i.imgur.com/jRWVHRK.png"/>

We can now delete `Carlos` user to solve the lab

<img src="https://i.imgur.com/wlM4GoF.png"/>
