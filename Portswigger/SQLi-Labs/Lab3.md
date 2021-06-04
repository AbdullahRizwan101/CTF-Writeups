# Portswigger SQLi-Lab 3
## SQL injection UNION attack, retrieving data from other tables

This lab is continuation from the previous sqli labs and in this we have to retieve the data from `users` table having column names `username` and `password` knowing that the GET paramter `category` is vulnerable to sqli , since the tables are changed we may have to know columns from "ORDERY BY" query in sqli

<img src="https://imgur.com/ltZhhSB.png"/>

Trying to find the column number using `order by`

<img src="https://i.imgur.com/F2MKc0M.png"/>

<img src="https://i.imgur.com/HAnkhSD.png"/>

<img src="https://i.imgur.com/y4wQtUN.png"/>

So we have only 2 columns in the table

<img src="https://i.imgur.com/y4wQtUN.png"/>

Since we know the table name we can grab data from it using the column names which are also known

<img src="https://i.imgur.com/el1tCAd.png"/>

With this we can grab the usernames and passwords from table 

<img src="https://i.imgur.com/w5u7Fu5.png"/>

<img src="https://imgur.com/QPnmTi4.png"/>

Now in order to complete this lab we need to login as `adminstartor` so we have his password we just need to login , so going to `My Account`

<img src="https://i.imgur.com/8sPMgEF.png"/>

<img src="https://imgur.com/9YDpoez.png"/>

<img src="https://i.imgur.com/Mu3pG9L.png"/>

And we are done with this lab !