
Hi everyone today I will analyze the machine called "Lianyu" on **TryHackMe** platform. Before you begin please add your `ipv4` address to `/etc/hosts`.

![[TryHackMe/Lianyu/images/1.png]]

Firstly, run your `VPN` file then try to `ping` the target so that you can understand whether you can communicate with target server or not.

![[TryHackMe/Lianyu/images/2.png]]

Gotcha !

## Reconnaissance:

Now, finally, checking the most common port is beneficial for us because of the penetration testing time restrictions.

Payload:

```
curl http://lianyu.thm:80
curl http://lianyu.thm:8080
```


![[TryHackMe/Lianyu/images/3.png]]


![[TryHackMe/Lianyu/images/4.png]]

As you can see, I did not have such application instances on ports `8080` and `443` respectively. 

`Wappalayzer` just showed the web server software.

![[TryHackMe/Lianyu/images/5.png]]

There were nothing interesting on `Page Source` ,so let me move on `automated reconnaissance`. After a couple of `wordlist` attempts I used `directory-list-medium-2.3-medium.txt` then it gave me just one endpoint on our web application.

```
dirsearch -u http://lianyu.thm -w/usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium. txt
```

![[TryHackMe/Lianyu/images/6.png]]
