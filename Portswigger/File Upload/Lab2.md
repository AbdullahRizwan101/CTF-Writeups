# Portswigger File Upload - Lab 2
## Web shell upload via Content-Type restriction bypass

<img src="https://i.imgur.com/yn1xska.png"/>

We have user name and password through which we can login 

<img src="https://i.imgur.com/QbLlY39.png"/>

<img src="https://i.imgur.com/NhjUhxM.png"/>

This user has option to update his email and to upload avatar , so let's try to upload a php file which will read the contents of `/home/carlos/secret`

So our php file will look like this 

```php
<?php echo file_get_contents('/home/carlos/secret'); ?> 
```

<img src="https://i.imgur.com/lGxMtsZ.png"/>

But on uploading this , it will show an error that only jpeg and png file are allowed

<img src="https://i.imgur.com/N4YvMrW.png"/>

Using `burp suite` we can capture the request while uploading the file and sent it to `repeater` to make changes in `Contet-Type` header by setting it to `image/jpeg`

<img src="https://i.imgur.com/BG4LZA7.png"/>

Now by going to any post and looking at the source to see from where our avatar is being loaded we can follow that to execute the php file we uploaded

<img src="https://i.imgur.com/AXMA2oe.png"/>

And this will execute the php code to read contents from `secret` file , submit this and you'll complete this lab

<img src="https://i.imgur.com/qGupMrx.png"/>