# Portswigger  SQLi-Lab5

## SQL injection attack, querying the database type and version on Oracle

This lab is quite similar to what I have done in this previous labs , Techinically I have already solved this before like in this lab you just need to query the database and version being used so it's pretty easy , it also has the GET paramter `category` to be vulnerable to sqli.


<img src="https://i.imgur.com/pEbL6EY.png"/>

First we need to identify the number of columns so we are going to use `order by <number`

<img src="https://i.imgur.com/LhnFdww.png"/>

I tried to used order by 1 and 2 , it worked when I will use `order by 3` it will give an error because only 2 columns exists in the table

<img src="https://i.imgur.com/1nrqnMw.png"/>

But there's a problem , in oracle we need to include a table name or it will give us an error 

<img src="https://i.imgur.com/aTAG2nj.png"/>

So what we can do is , use a dummy table called `dual` 

<img src="https://i.imgur.com/d5GVfTZ.png"/>

(Ignore the lab completion as I did the lab before making this writeup)

Now we may need to use built in tables in order to retreive database and version, we can query the user by supplying `user`

<img src="https://i.imgur.com/NJyNVPv.png"/>

<img src="https://i.imgur.com/KjPtqlm.png"/>

In oracale database in order to retrieve version , we need to query for `banner` from a table named `v$version`

<img src="https://i.imgur.com/lO59oPx.png"/>

```sql
Pets' union select banner,null from v$version --
```

<img src="https://i.imgur.com/vJvHFQz.png"/>

<img src="https://i.imgur.com/OxPuDi6.png"/>


With this our lab is completed !