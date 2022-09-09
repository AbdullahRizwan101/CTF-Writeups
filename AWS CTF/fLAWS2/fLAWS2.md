# flAWS 2 - Attacker Path
flAWS 2 is the continuation of fLAWS CTF which is focused for teaching about AWS (Amazon Web Services) pentesting, which introduces issues in Lambda and ECR and to exploit them, it's hosted on `http://flaws2.cloud/` so we don't need to setup anything for AWS. I'll be focusing on doing the Attacker path and this path includes 3 levels


<img src="https://i.imgur.com/CNct7Sh.png"/>

## Level 1

### Finding AWS Access and Session

The page asks us to enter a 100 digit pin code

<img src="https://i.imgur.com/oeAdAqV.png"/>

If we try to see what request is made at the backend in the network tab from developer tools

<img src="https://i.imgur.com/HxORZHB.png"/>

It's making a request to `https://2rfismmoo8.execute-api.us-east-1.amazonaws.com/default/level1?code=1` with the value of the `code` so it must be evaluating from the backend whether the code is valid .  As we learned from fLAWS (prequel to fLAWS2) that it's used to make API requests, where `2rfismmoo8` is `rest-api-id` , `level` is the stage/function . This resource in AWS is known as `AWS Lambda` which is baiscally used to run code or make API requests

On making an invalid request like putting characters instead of numbers we'll get an error which will reveal `AWS_SECRET_KEY`, `AWS_ACCESS_KEY_ID` and `AWS_SESSION_TOKEN`

<img src="https://i.imgur.com/IvTFywf.png"/>

We can use this to access the s3 bucket which it's only allowed through a valid AWS key as we can't access it without it

<img src="https://i.imgur.com/zCY2elO.png"/>

<img src="https://i.imgur.com/PIU4ang.png"/>

Adding AWS_SESSION_TOKEN in the credentials file

<img src="https://i.imgur.com/sgLeyQp.png"/>

WIth `awscli` we can access the s3 bucket

```bash
aws s3 ls s3://level1.flaws2.cloud
```

<img src="https://i.imgur.com/XCNSurC.png"/>

We can download the secret html file with `cp`


<img src="https://i.imgur.com/hoY9zym.png"/>

This will give us the link to level 2

<img src="https://i.imgur.com/mK3uQxO.png"/>

## Level 2

### Accessing ECR images

<img src="https://i.imgur.com/FKk0t17.png"/>

Checking for un-authorized access on s3 buckets

<img src="https://i.imgur.com/ydZ23sE.png"/>

This level talks about a container on http://container.target.flaws2.cloud/ which is being referenced `Elastic Container Registry (ECR)` , it's basically a container (docker) image registry service 

So from awscli we can use `aws ecr` for interacting with elastic container registry (make sure to grab aws keys and session because they do get expired)

With `aws ecr get-login` we can get the username and password for ECR

<img src="https://i.imgur.com/Oa8auXn.png"/>
Also we get the endpoint for registory control, with `aws ecr describe-images --repository-name level2` we can list the images from repoistory `level2`

<img src="https://i.imgur.com/lveh26K.png"/>

All we have to do is login to registry control with docker

<img src="https://i.imgur.com/FzxJykn.png"/>

With `docker` we can pull the image `level2` with tag `latest`

```bash
docker pull 653711331788.dkr.ecr.us-east-1.amazonaws.com/level2:latest
```

<img src="https://i.imgur.com/spvu05a.png"/>

We can list the images with `docker images`

<img src="https://i.imgur.com/h6MFz97.png"/>

The container can be ran by executing `bash` in the container to get a shell

```
sudo docker run --rm -it --entrypoint bash 2d73de35b781
```

<img src="https://i.imgur.com/kimitwJ.png"/>

Going into `/var/www/html` we can find the link to level 3 in `index.htm` file

<img src="https://i.imgur.com/sGthtTz.png"/>

Now level 3 which is the last level of flaws2.cloud, wasn't working as 
 it requires us to accss http://container.target.flaws2.cloud which wasn't responding, I am not sure what's the reason but this concludes flaws2.cloud
## References
- http://flaws2.cloud/
- https://pentestbook.six2dez.com/enumeration/cloud/aws
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-pull-ecr-image.html
