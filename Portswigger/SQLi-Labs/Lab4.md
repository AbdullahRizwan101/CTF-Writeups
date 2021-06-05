# Portswigger SQLi-Lab 4
## SQL injection UNION attack, retrieving multiple values in a single column

In this lab we need to retrieve data as we did in the previous lab but this time we need to get username and password in a single column so here we have the same application with the same parameter being vulnerable to sql injection

<img src="https://imgur.com/UWLOtyr.png"/>

<img src="https://i.imgur.com/8rQ1TQe.png"/>

We have to columns in the table so we need to extract the data but keep in mind to only utilize one column but in this lab things are a little different if we try to query username and password if we would get an error

<img src="https://i.imgur.com/3izsWYR.png"/>

Here maybe the first column isn't using `string` data type , let's to query username on second column

<img src="https://i.imgur.com/R3atulQ.png"/>

And it worked , now with this column name , we need to get `password` as well with the `username` to do that we have to do string concatenation

<img src="https://i.imgur.com/mUkKeLy.png"/>

It worked but doesn't look good maybe we can make better so let's try it

```sql
Gifts' union select null,username|| ':' || password from users --
```

<img src="https://i.imgur.com/1J4CvnK.png"/>

This is perfect now we just need to login to the application as `administrator`

<img src="https://i.imgur.com/17rHrX2.png"/>

With this we have solved this lab !!!