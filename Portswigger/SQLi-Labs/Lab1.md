# Portswigger SQLi-Lab 1

## SQL injection UNION attack, determining the number of columns returned by the query

The description of this labs says that sqli vulnerability exists in `category` filter of the web application meaning that we need to test sqli on the GET parameter `category`

<img src="https://imgur.com/iAavPSf.png"/>

Select one of the category on web application we can see that the url contains a paramter named "category"

<img src="https://i.imgur.com/3rVnQR9.png"/>

Here let's test for blind sqli first to see if we can break the application so I am going to supply a single quote `'`

<img src="https://i.imgur.com/XtV5Mv8.png"/>

And notice that we get an error , now let's add a boolean query `' and 1=1 --`, what this query will do first will close the previous query with `'` and then it's going to check the condition if "1=1" is TRUE which will always return TRUE and `--`  will comment out the rest of the query

<img src="https://i.imgur.com/TKzboCV.png"/>

We can confirm that sqli vulnerability exists so now is the time to see how many columns are there in the table so then we can extract information from the database in order to do that we are going to use `ORDER BY` which sorts the data according the column number we provide , it's a good way to see if the column exists or not. We keep doing this until we get an error and if we get an error we conclude that we have found the number of columns on which it didn't gave an error so let's test this

<img src="https://i.imgur.com/TrcGWxP.png"/>

We get a result which means there's 1 column , let's test for 2

<img src="https://i.imgur.com/01mRUpr.png"/>

Now for 3rd column

<img src="https://i.imgur.com/LLnCoxV.png"/>

It shows us a result means that 3rd column also exists in the table

<img src="https://i.imgur.com/7mKRYHv.png"/>

On the fourth column it gave us an error meaning only 3 columns exists in the table so now we can use union based sqli to get the results from the database

```sql
Gifts' union select null,null,null --
```

<img src="https://i.imgur.com/JeegH3k.png"/>

With this we have completed this lab but I want to a step further to see if I can dump the database name, version ,table and etc.

In order to do that the column data type must be the same like if we want to see the version of database it's in `string` so the column data type must be `string` too so it won't work in 1st column

<img src="https://i.imgur.com/7VczDyt.png"/>

Let's try it on the second column maybe it's a string data type

```sql
Gifts' union select null,version(),null --
```

<img src="https://i.imgur.com/RM2Wo32.png"/>

And we got to know the version of database being used which is postgreSQL so we can try to list the databases

<img src="https://i.imgur.com/VBMvE9P.png"/>

We can also do this automatically with a tool called `sqlmap`

<img src="https://i.imgur.com/ImVgEok.png"/>

It can dump the data from the tables

<img src="https://imgur.com/vsgC6g2.png"/>
