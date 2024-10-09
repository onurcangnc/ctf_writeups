
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

Using variable without conditional statements mainly cause vulnerability especially in `php`. That's why, I can  



