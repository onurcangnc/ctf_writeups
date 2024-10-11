
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

As you can see, I did not have such application instances on ports `8080` and `443` respectively. There were nothing interesting on `Page Source` ,so let me move on `automated reconnaissance`.




