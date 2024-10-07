
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

