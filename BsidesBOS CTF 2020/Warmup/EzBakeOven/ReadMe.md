# BsidesCTF-EZ Bake Oven

This challenge was part of Warmup and it was difficult . I send like an hour to figure out what to do with it. Anyways

<img src="https://imgur.com/THjmYiF.png"/>

Now we see `Magic Cookies` is fishy here 


<img src="https://imgur.com/cDK7oFr.png"/>

But as you can see it's gonna take forever to timeout. So I looked at the dev tools


<img src="https://imgur.com/TqViuIU.png"/>

Thought about modifying the cookie , You can see that it is base64 encoded text by looking at`=` on the end.


<img src="https://imgur.com/EHyYsw6.png"/>

Modify the cookie by changing a date way back so timer ends.


<img src="https://imgur.com/insw9jq.png"/>

Take the modified cookie's base64 encoded text and replace it with the cookie in the dev tools then refresh the page

<img src="https://imgur.com/GsVuDQd.png"/>

