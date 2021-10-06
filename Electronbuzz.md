# Electronbuzz (Misc)

In this challenge we were given an electron application in the form of windows,linux file , so I downloaded the debian package and extracted it , on which I `app.asar` file , which in electron holds the source code and some configuration file of the main application

<img src="https://i.imgur.com/BTwLhZx.png"/>

We can extract this by using `npx asar extract app.asar .` , you can install `npx` using `npm install -g asar`

<img src="https://i.imgur.com/yivO93v.png"/>

And we can get the flag by reading `challenge.yml`

<img src="https://i.imgur.com/8Q0KleS.png"/>


## References
- https://stackoverflow.com/questions/38523617/how-to-unpack-an-asar-file