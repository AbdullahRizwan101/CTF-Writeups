# Portswigger OS Command Injection-Lab 

## OS command injection, simple case

This lab is about the Operating System Command Injection , in which if a web application is running a OS script or taking some arguments we can try to include system commands that could compromise ther server.

From the description of the lab it says that command injection vulnerability exists in `product stock checker`.

<img src="https://i.imgur.com/OqcSZtW.png"/>

We can visit and product we want to and then find where that stock checker is.

<img src="https://i.imgur.com/Vi1NxRx.png"/>

If we click the `Check Stock` button , it's going to bring back some results

<img src="https://i.imgur.com/2xe3iJN.png"/>

There's a `POST ` request being sent as we do not see any parameters in URL , so to play around with it let's use `brup suite` to intercept the request

<img src="https://i.imgur.com/H5SWlae.png"/>

Send this request to `Repeater` using `CTRL+R` so we can try sending the request again and again by modifying it.

<img src="https://i.imgur.com/bXUx6yi.png"/>

Here we can see POST request being made to  `/product/stock` and at the bottom we can see the parameters having the value so these parameters are being passed to a shell and then being executed from there are displaying the resutls so there's a chance that there's isn't input sanitzation we can check by adding `;` which is used chain commands to gather 

https://owasp.org/www-community/attacks/Command_Injection

<img src="https://i.imgur.com/dOHe1Te.png"/>

We can do bunch of stuff like reading files on the server and doing other cool stuff but for now our goal was to achieve command injection.


<img src="https://i.imgur.com/aoOYLNa.png"/>
