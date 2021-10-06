# Magician (Web)

This web challenege had an input field where it was asking for us to input the string whose md5 hash will be equal to the given one meaning a hash collision where hashes of different file or string are similar 

<img src="https://i.imgur.com/KILYmf2.png"/>

I tried to give some random text and in the bottom it should be the md5 hash of that string

<img src="https://i.imgur.com/Y7msap5.png"/>

But we need to put a string whose hash will be the same like this `0e365027561978452045683563242341` I  tried to crack this md5hash using crackstation and hashcat but failed ,so I googled for this hash

<img src="https://i.imgur.com/fh3saxZ.png"/>

<img src="https://i.imgur.com/LBGofQ2.png"/>

So we just have to submit this string `QNKCDZO` and we will pass the condition

<img src="https://i.imgur.com/qQTmOc6.png"/>

## References

- https://stackoverflow.com/questions/22140204/why-md5240610708-is-equal-to-md5qnkcdzo