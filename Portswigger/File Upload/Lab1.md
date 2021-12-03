# Portswigger File Upload - Lab 1
## Remote code execution via web shell upload
In this lab we have to upload a php file which can read contents from a file callled `secret`. We are given the credentials through that we can login to an account which can update his email address and can change his avatar , so this where file upload vulnerability can occur 

<img src="https://i.imgur.com/BzpTHOg.png"/>

Here we have an option `Myaccount` ,so login with `wiener:peter`

<img src="https://i.imgur.com/EGrBILk.png"/>

<img src="https://i.imgur.com/EdIDoA0.png"/>

We can upload the image file from here , so let's make a php file which will read the contents from `/home/carlos/secret` , I tried to upload a php web shell which could execute any commands but functions like `system` , `passthru` , `shell_exec` are blocked 

```php
<?php echo file_get_contents('/home/carlos/secret'); ?> 
```

So by using `file_get_contents` to read file we can retrieve the file that is required in order to complete the lab

<img src="https://i.imgur.com/VqHovHH.png"/>

Visit any post , and you'll get the option to comment on it , look into the source code , you'll see the url from your avatar is being fetched from

<img src="https://i.imgur.com/IsohzgU.png"/>

<img src="https://i.imgur.com/Ih70UCZ.png"/>

Then just submit this string to complete the lab
