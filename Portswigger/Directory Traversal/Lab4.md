# Portswigger Directory Traversal Lab-4

## File path traversal, traversal sequences stripped with superfluous URL-decode

In this lab we have to perform LFI to read `passwd`  file but this time those traversal sequences are removed from the url 

<img src="https://i.imgur.com/uAfHXRO.png"/>

We follow the same the url where there's a GET parameter  `image` that is loading the image file

<img src="https://i.imgur.com/axLX9Cb.png"/>

If we try to do `../` or `.././` it will not work

<img src="https://i.imgur.com/C6lwqJ2.png"/>

So let's try to url encode `../` and see if this works

<img src="https://i.imgur.com/2TnqUY7.png"/>

<imgs src="https://i.imgur.com/Q0KQkKB.png"/>

This didn't work so let's url encode it again and make it double url encoded 

<img src="https://i.imgur.com/kwLTxyZ.png"/>

<img src="https://i.imgur.com/jNaHduM.png"/>

<img src="https://i.imgur.com/eq6YwRO.png"/>
