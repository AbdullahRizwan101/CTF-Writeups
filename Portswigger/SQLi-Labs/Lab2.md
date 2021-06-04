# Portswigger SQLi-Lab 2

## SQL injection UNION attack, finding a column containing text

So in this lab following the previous one , we know that the `category` parameter is vulnerabile to sqli and we know the exact number of columns so we can perform union based sqli . Here we need to show a random string using union sqli so let's begin

<img src="https://i.imgur.com/0dQmTnN.png"/>

We can see the random string that we need to retreive so selecting any category will make the url appear with the GET parameter `category`

<img src="https://i.imgur.com/fIIfnC9.png"/>

Performing union based sqli

<img src="https://i.imgur.com/9iYY9uC.png"/>

The reason we used `null` is because we don't know yet the data type of the columns being used in the table so by supplying null data type it's convertable to every data type that is why used it so it can increase our chances that column count is correct we won't get any errors

Now to retrevie the random string we first need to identifiy which column is using data type `string` or `varchar` in DBMS terms. We can use `version()` which returns the version of database being used as string so we can use it to identify which column is using string data type

<img src="https://i.imgur.com/AbR3dEH.png"/>

The first column is not compatible , let's try the second column

<img src="https://i.imgur.com/FSTpOKG.png"/>

Neat , we now know the second column uses string data type so we can just add random string like this 

```sql
Gifts' union select null,'hXl2ys',null --
```

The reason we are using single quotes is because this is a string 

<img src="https://i.imgur.com/wRn2I4Q.png"/>

With this we have solved this lab