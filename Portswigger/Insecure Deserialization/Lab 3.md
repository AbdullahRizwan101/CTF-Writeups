# Portswigger Insecure Deserialization - Lab 3

## Using application functionality to exploit insecure deserialization

In this lab we need to modfiy the serliazled cookie for the account either for ``wiener`` or ``gregg`` and delete `morale.txt` from `carlos` user's home directory


<img src="https://i.imgur.com/jCjIlVR.png"/>

We can login with the credentials ``wiener:peter`` although we are given another account ``gregg:rosebud`` but we'll see what's the purpose of `gregg` user

<img src="https://i.imgur.com/q9oLSZW.png"/>

<img src="https://i.imgur.com/XkXd4TK.png"/>

We can grab the user's cookie and see that's it's a serialized cookie which is base64 encoded

<img src="https://i.imgur.com/LgEZhQa.png"/>

<img src="https://i.imgur.com/Eu1AJfH.png"/>

```bash
O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"evc58p8rx44g58fzvikyrajffjmtfn8q";s:11:"avatar_link";s:19:"users/wiener/avatar";}
```

To understand what's happening in the cookie here 

- `O:4` represents the object `user` of  character length `4` which as `3` attributes
- `s:8` represents the the string attribute `username` which is of character length `8` which has the string value `wiener` of having length `6` 
- `s:12` represents the string attribute `access_token` of the character length `12` which has a random value of `32` characters 
- `s:11` represents the string attribute `avatar_link` of character legnth `11` having the value `users/wiener/avatar` which is the path where the avatar is stored of character length `19`


It also has an option to delete the account which also deletes the avatar `users/wiener/avatar`  so this is probably the reason why we are given two accounts if we fail to exploit the application's functionality with wiener

<img src="https://i.imgur.com/HseFKuK.png"/>

To solve the lab we need to delete `morale.txt` from `carlos's` home directory so we need to change the avatar path to `/home/carlos/morale.txt`


```bash
O:4:"User":3:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"jg6c74hrhfs1r1y44n0arp5hmux7zem2";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";}
```

<img src="https://i.imgur.com/z400Hx8.png"/>

Replacing the cookie and clicking on the delete account button we'll solve the lab

<img src="https://i.imgur.com/T0Idh1m.png"/>



