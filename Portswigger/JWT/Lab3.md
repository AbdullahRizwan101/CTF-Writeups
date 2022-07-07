# Portswigger JWT - Lab 3

## JWT authentication bypass via weak signing key

In this lab we need to modify the JWT of the user we log in and brute force the secret key to sign JWT and edit JWT to become administrator user

<img src="https://i.imgur.com/25q6H16.png"/>

After logging we'll get a JWT for the user `wiener`

<img src="https://i.imgur.com/JIe4MRH.png"/>

<img src="https://i.imgur.com/ii0hZIr.png"/>

For brute forcing the secret key against the JWT we can use the worldlist provided in the lab, we can use `hashcat` to crack the secret key 

<Img src="https://i.imgur.com/ril0xOD.png"/>

<img src="https://i.imgur.com/2bfdksa.png"/>

<img src="https://i.imgur.com/FOwjT9G.png"/>

WIth this we got the secret key which is `secret1`

To sign the token with the secret and modify the username we can use this site

https://jwt.io/

<img src="https://i.imgur.com/Jl82FZa.png"/>

Now replacing the token through developer tools

<img src="https://i.imgur.com/DbeGbz3.png"/>

We are now the administrator user and can access the admin panel

<img src="https://i.imgur.com/LXrblWd.png"/>

On deleting the `carlos` user we can solve the lab

<img src="https://i.imgur.com/Q5VK2ds.png"/>



## References

- https://hashcat.net/wiki/doku.php?id=example_hashes
- https://jwt.io/

