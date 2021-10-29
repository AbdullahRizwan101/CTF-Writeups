# Portswigger Directory Traversal Lab-1 & 2

## File path traversal, simple case

This lab is about performing directory traversal or Local File inclusion which means that we can view files on the server. So we have to read `passwd` file through `image` parameter in order to complete the lab

<img src="https://i.imgur.com/KN3om6p.png"?>

We are given this web page and we can see some images being loaded , so by looking at the source we can see how they are being retrieved 

<img src="https://i.imgur.com/NBAXNbA.png"/>

Here there's a GET parameter named `image` which is getting the image file , we can try to request `/etc/passwd` file


<img src="https://i.imgur.com/1nzvVDF.png"/>

But it says `No such file` , we are in images directory and we need to go up a directory till we can we reach the root `/` directory and request the file `/etc/passwd`

<img src="https://i.imgur.com/78y7xL0.png"/>

This gives an error but it's different , it can't view the file because it's expecting an image so let's just download it and see if we actually grabbed the passwd file

<img src="https://i.imgur.com/dbbZ2I6.png"/>

##  File path traversal, traversal sequences blocked with absolute path bypass

This lab is somewhat similar to the previous one but we can request a file using  it's absolute path i.e `/etc/passwd` .

<img src="https://i.imgur.com/hkycXNO.png"/>

The web page is the same so we need to abuse the same GET parameter

<img src="https://i.imgur.com/kkIputd.png"/>

This gives us the error meaning that we are sucessful in requesting the file

<img src="https://i.imgur.com/21LfZzI.png"/>
