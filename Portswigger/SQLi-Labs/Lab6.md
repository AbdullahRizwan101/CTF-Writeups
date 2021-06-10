# Portswigger  SQLi-Lab 6

## SQL injection attack, querying the database type and version on MySQL and Microsoft

This lab is similar to the lab#5 which invloved query version of oracle database , so this also involves the GET parameter `category` vulnerable to sqli

<img src="https://i.imgur.com/7ydvvXB.png"/>


<img src="https://i.imgur.com/BZBCH4a.png"/>

Here the blind sqli didn't work although I have it right but it's just not working so I launched burpsuite and intercepted the request and send it to burp repeater

<img src="https://i.imgur.com/ZwOu80C.png"/>

Now on your keyboard press `CTRL+R` this will send the request to brup repeater

<img src="https://i.imgur.com/Yl97L64.png"/>

<img src="https://i.imgur.com/V8TkIyI.png"/>

Our blind sqli works with burp don't know why but let's roll with it and identify the number of columns

<img src="https://i.imgur.com/L4zoLOm.png"/>

Notice that I used `--` , well in mysql both `#` and `--`  works for comments but -- works if we supply a space afterwards that's why I included `+` which tells it's a space in url encoding

<img src="https://i.imgur.com/QsEg22D.png"/>

So second column exists as well , let's try for the third column

<img src="https://i.imgur.com/Sm8hPxj.png"/>

Here only 2 columns exists so now we can use union based sqli to know the version of mysql database

<img src="https://i.imgur.com/8pwEqu1.png"/>

With this we completed this lab

<img src="https://i.imgur.com/BNr1Jon.png"/>

In the end I noticed that all we wanted to do was to url encode our sqli payload

```sql
Accessories'+union+select+@@version,null+--+
```
<img src="https://i.imgur.com/Bvd35eo.png"/>

<img src="https://i.imgur.com/n28sR0V.png"/>