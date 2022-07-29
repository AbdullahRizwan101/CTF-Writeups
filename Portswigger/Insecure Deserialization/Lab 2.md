# Portswigger Insecure Deserialization - Lab 2

## Modifying serialized data types

In this lab we need to modify the serlialized session which is vulnerable to authentication bypass through which we can get access to administrator account

<img src="https://i.imgur.com/S787FVy.png"/>

We can login as `wiener` with the given password `peter`

<img src="https://i.imgur.com/1KdYJpy.png"/>

<img src="https://i.imgur.com/3lGZIrk.png"/> 

The session cookie can be accessed from developer tools which is base64 encoded 

<img src="https://i.imgur.com/mzWD1Dn.png"/>

<img src="https://i.imgur.com/cxOUBdq.png"/>

```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:12:"access_token";s:32:"x64caqpmvk2jtz6vgxrit5eotzkg2h30";}
```

To understand what's happening in serialized cookie here,

- `O:4`  represents the object `user` which is length of  `4` and has two attirbutes `2` which are `username` and `acces_token`
-`s:8` represents the username attirbute of string type having length of `8` which has the key value `winener` of string data type having length of `6`
- `s:12` represents the `acess_token` of string type having length of 12 which has key value of string data type of lenght `32`

We can try replacing the session cookie with the username `admnistrator` also we should edit the length of string also we can try performing php loose comparision which is comparing string with an integer value `0`

https://owasp.org/www-pdf-archive/PHPMagicTricks-TypeJuggling.pdf

<img src="https://i.imgur.com/hhr75t6.png"/>

On replacing the token we'll see an error message which will reveal some access tokens and there are 3 tokens so they are probably for carlos, wiener and administrator

<img src="https://i.imgur.com/xORmlIS.png"/>

We can try using these tokens from which only `vxdtpdwjbj8mhrubuejx0b2dqi8o1ky8` token worked for administrator

<img src="https://i.imgur.com/q5Ik9Ay.png"/>

Now we can delete the carlos user and complete this lab

<img src="https://i.imgur.com/j1zPMId.png"/>


## References

- https://owasp.org/www-pdf-archive/PHPMagicTricks-TypeJuggling.pdf
