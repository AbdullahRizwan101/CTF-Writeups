# Portswigger Directory Traversal Lab-3

##  File path traversal, traversal sequences stripped non-recursively

In this lab we have to read `/etc/passwd` file through LFI (Local File Inclusion) or Directory Traversal through the vulnerable GET parameter `image` on the web page but this time the web application will be filtering those `../` to prevent us going out of the current directory from where it's loading those images

<img src="https://i.imgur.com/3rxFLOC.png"/>

We have the same web page as we saw from the other 2 labs 

<img src="https://i.imgur.com/KBOU7W1.png"/>

On trying those `../` it doesn't give us the `passwd` file so to get around this filter is to use `..././` instead of `../` and the way it's going to work is that the filter will check for `../` and it's going to remove it from the string so all that is left will be . , . / which will be treated as `../` 

<img src="https://i.imgur.com/aiRi28l.png"/>

<img src="https://i.imgur.com/vNf1PG7.png"/>
