# flAWS

flAWS is a CTF focused for teaching about AWS (Amazon Web Services) pentesting, which introduces  issues in AWS and to exploit them, it's hosted on `http://flaws.cloud/` so we don't need to setup anything for AWS

<img src="https://i.imgur.com/7jxjIIW.png"/>

## Level 1

### This level is buckets of fun. See if you can find the first sub-domain

Using the url which is given to us, we can check the response of the url with `curl`

<img src="https://i.imgur.com/mar5apS.png"/>

Here it shows `AmazonS3` in server header in the response, `Level 1` is about finding the subdomain of the domain given from where we can access S3, which is a key-value store, for storing objects in amazon which is used for storing files, these objects are stored in a container known as `buckets`

The url of s3 bucket is in these formats

- http://s3.amazonaws.com/bucket
- http://bucket.s3.amazonaws.com

<img src="https://i.imgur.com/4NcCVT5.png"/>

As from the server response eariler, the site is being hosted as s3 bucket, so visiting `http://flaws.cloud.s3.amazonaws.com/`  will show us the bucket, and the reaons why it will show us the contents is because it's allowed for un-authorized access 

<img src="https://i.imgur.com/LLOUrnm.png"/>

This shows five html files 
- hint1.html
- hint2.html
- hint3.html
- index.html
- secret-dd02c7c.html

Having `secret-dd02c7c.html` , we don't really need to go through the hint files as we already have found about s3 and have the secret file

<img src="https://i.imgur.com/k4vJepz.png"/>

We can also access the bucket through command line as well using `aws-cli`

<img src="https://i.imgur.com/Ts6YaRX.png"/>

<img src="https://i.imgur.com/CGIuYHy.png"/>

If you encounter this error, it can be resolved by installing urlib version `1.26.7 `

<img src="https://i.imgur.com/atiT8Jf.png"/>

<img src="https://i.imgur.com/rSpDfNz.png"/>

To list the contents from s3 bucket the syntax is like this also we are using `--no-sign-request` because we don't want any authentication and the region is where the bucket is being hosted from
```bash
aws s3 ls s3://flaws.cloud/ --no-sign-request --region us-west-2 
```

<img src="https://i.imgur.com/S4uLX7K.png"/>

We can download the secret file like this 

```bash
aws s3 cp s3://flaws.cloud/hint1.html --no-sign-request --region us-west-2 .
```

<img src="https://i.imgur.com/oKfxxNV.png"/>

Or if we want we can use  `cp` and `--recursive` to download all files from the bucket on to our local machine

```bash
aws s3 cp s3://flaws.cloud/ --no-sign-request --region us-west-2 . --recursive 
```

<img src="https://i.imgur.com/l8jtAjA.png"/>

## Level 2

### Accessing a bucket with any valid AWS credential 

<img src="https://i.imgur.com/gobbYUi.png"/>

There can be a mis-configuation in buckets to allow anyone to view bucket with any valid AWS credential, so if we try accessing this bucket `http://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud.s3.amazonaws.com/` it will give access denied to bucket with un-authorized access

<img src="https://i.imgur.com/gxR7oa0.png"/>

For this we need to now create an aws free tier account which needs credit card information

<img src="https://i.imgur.com/1qy0wPI.png"/>

After filling up the details we'll have the account registered, login as a root user account 

<img src="https://i.imgur.com/lp7Iaho.png"/>

After logging in, we'll be brought to aws dashboard

<img src="https://i.imgur.com/OT2CFKB.png"/>

Now we need to setup AWS access key, to do that visit `Security Credentials`

<img src="https://i.imgur.com/xSgOm7e.png"/>

<img src="https://i.imgur.com/xSgOm7e.png"/>

After closing this pop up, it will make the key active

<img src="https://i.imgur.com/gLoLp0N.png"/>

We can set the AWS key with `aws configure`

<img src="https://i.imgur.com/mgNwNh3.png"/>

These keys are saved in `~/.aws/credentials 
`
<img src="https://i.imgur.com/878Zekr.png"/>

And now we can acess the level 2 bucket

<img src="https://i.imgur.com/bNV4BhG.png"/>

Download the secret html file

<img src="https://i.imgur.com/KFYQzJk.png"/>

This will lead us to level 3

<img src="https://i.imgur.com/quAtCrR.png"/>

## Level 3

### Finding and acessing the bucket with authorized AWS key

<img src="https://i.imgur.com/cROIL2O.png"/>

Let's access the bucket by going to this url `http://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud.s3.amazonaws.com/`

<img src="https://i.imgur.com/zhFm03W.png"/>

This gives us unauthorize access to bucket having a git repo, we can download all files through `--recursive`

```bash
aws s3 cp s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/ --region us-west-2 . --recursive
```

<img src="https://i.imgur.com/O0vbRFD.png"/>
Using `git show` in `.git` directory we can see the commit which was deleted having the AWS access key

<img src="https://i.imgur.com/z0z5kSO.png"/>

<img src="https://i.imgur.com/60sUr6D.png"/>
With `aws s3 ls` we can list all the buckets but they are not accessible with this key

<img src="https://i.imgur.com/7p20NOM.png"/>
## Level 4 

### Accessing EC2 instance 

<img src="https://i.imgur.com/7HXAfef.png"/>

We are given a url which is running a web site hosted from ec2 instance `http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud`

We can't access the bucket without an authorized AWS key

<img src="https://i.imgur.com/hdV1GEJ.png"/>

An ec2 instance is a virtual server on aws, you can think of it as a linux server but being hosted and using aws infrastructre

<img src="https://i.imgur.com/pYd3Tm0.png"/>

This level mentions about a backup of ec2 instance was made

 >It'll be useful to know that a snapshot was made of that EC2 shortly after nginx was setup on it.

We can list the ec2 instances snapshots but before that we need the id and we can get that with 

```bash
aws sts get-caller-identity --output text
```

<img src="https://i.imgur.com/gsmhsJD.png"/>

To list the ec2 snapshots

```bash
aws ec2 describe-snapshots --owner-id 975426262029 --output text --region us-west-2
```

<img src="https://i.imgur.com/CxWRhNa.png"/>

But form the output we can't understand it properly so instead we can just output it with json format

<img src="https://i.imgur.com/kAtipXH.png"/>

Also to note that the reason we are specifying the `--owner-id` is because we want the snaphost which is owned by this AWS key, if we don't sepcfiy the id it will list all the snapshots which isn't owned by this user or id

<img src="https://i.imgur.com/vYYA3cz.png"/>

To mount this, we need to create a volume of this  snapshot to our AWS user account and to do that we need to again configure the AWS key but this time giving it a profile name so we can reference it 


<img src="https://i.imgur.com/ypc1wo9.png"/>


```bash
aws ec2 create-volume --profile arz --availability-zone us-west-2a --region us-west-2 --snapshot-id snap-0b49342abd1bdcb89
```

<img src="https://i.imgur.com/DtJaT7s.png"/>

We can check the status of the volume if it has been created 

```bash
aws ec2 describe-volumes --region us-west-2 --filters Name=volume-id,Values=vol-067022c1d15d83787 --profile arz 
```

<img src="https://i.imgur.com/CL6WT9s.png"/>

Now from AWS dashboard, go to `Services` -> `Compute` -> `EC2` -> `EBS` and `Volumes` there you'll see the volume created from the snapshot

<img src="https://i.imgur.com/VOWUuku.png"/>

Go to `Instances` , make sure to edit network settings to create the instance in `us-west-2a` 

<img src="https://i.imgur.com/erfbaUt.png"/>

Create a key pair

<img src="https://i.imgur.com/Y73wktS.png"/>

Then launch then instance

<img src="https://i.imgur.com/XYAvcY8.png"/>


Clicking on the instance, we can find the public IP and DNS 

<img src="https://i.imgur.com/ooKNmWf.png"/>

Now simply just login with the private key (pem) which was downloaded after setting the key pair using the username `ec2-user` which is the default user ( you can change that if you want)


<img src="https://i.imgur.com/b9Cerb2.png"/>

Attach the volume to this instance

<img src="https://i.imgur.com/xCTDVyx.png"/>

<img src="https://i.imgur.com/zspJcMV.png"/>

Run `blkid` to see the device number and then mount it with `mount`

<img src="https://i.imgur.com/VNtN9H8.png"/>

<img src="https://i.imgur.com/LMp3cc9.png"/>
This reveals the username `flaws` with password `nCP8xigdjpjyiXgJ7nJu7rw5Ro68iE8M`, with the credentials we can login to the nginx web page amd find the link to the next level

<img src="https://i.imgur.com/T0N5TOk.png"/>

## Level 5

### Accessing buckets through HTTP proxy

<img src="https://i.imgur.com/6UfTwwI.png"/>

This EC2 instance is using nginx as a proxy

`http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud/proxy/`

If we make a request to `127.0.0.1` which should see the index page for the level5 page for completing level4

<img src="https://i.imgur.com/Tuoj7XT.png"/>

Which means there's SSRF here through which can make a request to `169.254.169.254` which is a reserverd IP for EC2 meta data service  known as `maigc IP` 

<img src="https://i.imgur.com/baYWkAZ.png"/>

We want the `latest` meta data from where we'll get `identity-credentials`  and the role name `flaws` having the AWS access key

<img src="https://i.imgur.com/xpSx5u6.png"/> 

<img src="https://i.imgur.com/4VgxgmN.png"/>

Having the access keys, we can configure them in the default profile

<img src="https://i.imgur.com/zKXd7qG.png"/>

But we won't be able to view the user id and the bucket becasuse it will need a token as from the error it tells that token is invalid

<img src="https://i.imgur.com/s7JXOOp.png"/>

The token can be added in `~/.aws/credentials`

<img src="https://i.imgur.com/bwM22sa.png"/>

And now we'll be able to use the AWS access key with the token added

<img src="https://i.imgur.com/IZXiabe.png"/>

<img src="https://i.imgur.com/GVoSjQP.png"/>

In the bucket we see `ddcc78ff/` so we'll just download the files recusively

<img src="https://i.imgur.com/gM9AGn7.png"/>

Opening the index.html we'll get the page of the next challenge

## Level 6

### Enumerating AWS Policies

<img src="https://i.imgur.com/OUQOxpo.png"/>

<img src="https://i.imgur.com/OsF2dFD.png"/>

We are given AWS access key , make sure to remove the previous token

<img src="https://i.imgur.com/EspkLJo.png"/>

<img src="https://i.imgur.com/0ToC5Ie.png"/>

On Checkinng the bucket, we'll get an access denied error

<img src="https://i.imgur.com/3EVitEl.png"/>

As the challenge is about policies , we can try playing with `iam` which is Identity and Acess Management


```bash
aws iam list-roles
```

<img src="https://i.imgur.com/PGe5bek.png"/>

```
aws iam list-attached-user-policies --user-name "level6
```
``
<img src="https://i.imgur.com/PHjvFsn.png"/>

This user has Security Audit and api gateway policies attached, having api gateway policy we can see the function `Level6` in lambda, lambda is used for running application or some code as you can see here that in runtime it's showing `python2.7`

<img src="https://i.imgur.com/x0a0rXP.png"/>
 
We need to get the API id of Level6 function

```bash
aws lambda get-policy --function-name Level6
```

<img src="https://i.imgur.com/UrVyzS4.png"/>

Through this id we can list the stage name with `get-stages`

```bash
aws apigateway get-stages --rest-api-id s33ppypa75 
```


<img src="https://i.imgur.com/mippMwz.png"/>

This makes the URL of the api 

```
http://s33ppypa75.execute-api.us-west-2.amazonaws.com/Prod/level6
```

<img src="https://i.imgur.com/TOMnGdR.png"/>

On visting this link will mark the finish of fLAWS challenge

<img src="https://i.imgur.com/L0HSGRi.png"/>



## References


- https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingBucket.html
- https://blog.cloudanix.com/a-complete-list-of-aws-s3-misconfigurations/
- https://stackoverflow.com/questions/33791069/quick-way-to-get-aws-account-number-from-the-aws-cli-tools
- https://pentestbook.six2dez.com/enumeration/cloud/aws
- https://labs.nettitude.com/blog/how-to-exfiltrate-aws-ec2-data/
- https://hacktricks.boitatech.com.br/pentesting-web/ssrf-server-side-request-forgery#abusing-ssrf-in-aws-environment

