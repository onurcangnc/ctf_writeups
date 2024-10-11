
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

There were nothing interesting on `Page Source` ,so let me move on `automated reconnaissance`. After I used `common.txt` located on `dirb` directory I decided to use `directory-list-medium-2.3-medium.txt` then it gave me just one endpoint on our web application.

```
dirsearch -u http://lianyu.thm -w/usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-2.3-medium. txt
```

![[TryHackMe/Lianyu/images/6.png]]
I also applied extended fuzzing especially on `island` endpoint ,so applying `directory-list-2.3-medium.txt` was suitable. I highly recommend you to select `dirsearch` when you need fast fuzzing sessions. 

Since I was in `Bilkent Network`, it did not allow me to use all payloads in `directory-list-2.3-medium.txt`. As you can see below, tool seems to be bugged.

![[TryHackMe/Lianyu/images/7.png]]

I switched on `2100` endpoint direction. This is what HTML rendered:

![[TryHackMe/Lianyu/images/8.png]]

`HTML` source file indicates such an extension `.ticket`. I should find a way to fuzz both `2100` endpoint and specific extension called `.ticket`. Checking `-h` parameter or `man` is a great method to get parameters with specific purpose.

`-h` parameter was complicated to find necessary information about `extension` utility. That's why, I directly opened `manual pages` and found extension specific parameter.

![[TryHackMe/Lianyu/images/10.png]]

By using `-e` parameter we can achieve `.ticket` extension files.

![[TryHackMe/Lianyu/images/9.png]]

`Dirsearch` did not find anything ,so I shifted through B plan, `gobuster`. You must be patient to get results on `fuzzing` phases.

### Dirsearch Result:
![[TryHackMe/Lianyu/images/12.png]]

### Gobuster Result:

![[TryHackMe/Lianyu/images/11.png]]

I found an interesting string `RTy8yhBQdscX` appears to be `encoding` format.

![[TryHackMe/Lianyu/images/13.png]]

[Cyberchef](https://gchq.github.io/CyberChef/) could help me to decode it ,but it did not find.

[dcode](https://www.dcode.fr/cipher-identifier) detected many options for decoding resulting from `PlayFair Cipher` to `Substitution Cipher`.

![[TryHackMe/Lianyu/images/14.png]]

After I applied all of them, `Base 58` was the most meaningful result compared to others.

```
!#th3h00d
```


```
Ohhh Noo, Don't Talk...............

I wasn't Expecting You at this Moment. I will meet you there

You should find a way to Lian_Yu as we are planed. The Code Word is:
vigilante
```

Maybe, the `vigilante` or `!#th3h00d` is the user:pass combination. Vigilante was more likely a username ,so I initially tried it on `FTP server`.

GOTCHA ! ! !
![[TryHackMe/Lianyu/images/15.png]]

After I logged in successfully, interacting with `FTP` was crucial for file download process.

To list `directories`, `files`:

```
ls -al

dir
```

To download files from `FTP` client:

```
GET [File_Name]
```

Unless you understand, check it below:

![[TryHackMe/Lianyu/images/16.png]]

### Do not forget that FTP client will drop your files from which directory that you run. 

Since my files are located on `/usr/share/wordlists/SecLists/Discovery/Web-Content`, I want to move them to my `Desktop` directory.

```
mv Leave_me_alone.png aa.jpg Queen\'s_Gambit.png ../../../../../../home/kali/Desktop
```


