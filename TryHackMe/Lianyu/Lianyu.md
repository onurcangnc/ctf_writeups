
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

I should analyze image files with the techniques of `steganography`. Specifically, in order to apply image steganorgraphy, I needed to find proper tools. Today, I would like to run `exiftool`.

After a couple of attempt, I did not find juicy data on images ,but one of the instance  did not match its file format called `Leave_me_alone.png`.

![[TryHackMe/Lianyu/images/18.png]]

A normal result should looked like that:

![[TryHackMe/Lianyu/images/17.png]]

You can also verify through `Image Viewer` which is a default image application in kali environment.

![[TryHackMe/Lianyu/images/19.png]]

![[TryHackMe/Lianyu/images/20.png]]


Further image analyze must be done ,so let's use `hexedit` and modify its first line. As you can see below, leave_me_alone does not match with .PNG format. Moreover, you can reach out the long description and magic numbers of many extension from here: [File Magic Numbers](https://gist.github.com/leommoore/f9e57ba2aa4bf197ebc5) . 

![[TryHackMe/Lianyu/images/21.png]]

![[TryHackMe/Lianyu/images/22.png]]


In my first attempt, I could not convert correct format ,but I found a different source giving full format of `PNG`. On this [website](https://www.netspi.com/blog/technical-blog/web-application-pentesting/magic-bytes-identifying-common-file-formats-at-a-glance/) you will find appropriate format.

![[TryHackMe/Lianyu/images/23.png]]

Now it worked ! It indicated a `password` for something. At first I applied it on `SSH` ,but it did not true. After that let's also use `steghide` because kali gave me the clue about it. The image consisting data inside.

![[TryHackMe/Lianyu/images/24.png]]


```
┌──(root㉿kali)-[/home/kali/Desktop]
└─# steghide extract -sf Leave_me_alone.png
Enter passphrase: 
steghide: the file format of the file "Leave_me_alone.png" is not supported.
```

Maybe other image formats may work:

```
┌──(root㉿kali)-[/home/kali]
└─# steghide extract -sf aa.jpg
Enter passphrase: 
wrote extracted data to "ss.zip".
```

YES !
Furthermore, the man appeared was the same as `aa.jpg` and `Leave_me_alone.png`. Anyway, use `unzip` to extract data inside the archive.

![[TryHackMe/Lianyu/images/25.png]]

Content of the `passwd.txt`:

```
This is your visa to Land on Lian_Yu # Just for Fun ***


a small Note about it


Having spent years on the island, Oliver learned how to be resourceful and 
set booby traps all over the island in the common event he ran into dangerous
people. The island is also home to many animals, including pheasants,
wild pigs and wolves.
```

Obtain a string most likely password of the `SSH`.

![[TryHackMe/Lianyu/images/26.png]]

However, I could not find any `username` for it. Vigilante did not work. I instantly move on `FTP` again. There was a hidden file named `.other_user`.

![[TryHackMe/Lianyu/images/27.png]]

Reaching was impossible on that. Therefore, there was only one opportunity to deal with that issue. `Further Reconnaissance` is mandatory to reach username. What if I move parent directory on `FTP` ?

GOTCHA ! ! !

I found a different user rather than `vigilante`:

![[TryHackMe/Lianyu/images/28.png]]


I successfully reached the target instance through `SSH` with this credential:

```
user:pass
slade:M3tahuman
```

![[TryHackMe/Lianyu/images/29.png]]


## Exploitation

Get your `user` flag from here:

![[TryHackMe/Lianyu/images/30.png]]

Now, lets check which commands we can run on `slade` account:

```
sudo -l
```

Give its password:

```
slade@LianYu:~$ sudo -l
[sudo] password for slade: #M3tahuman
Matching Defaults entries for slade on LianYu:
```

![[TryHackMe/Lianyu/images/31.png]]

The binary called `pkexec` can be run on this account. I checked the `GFTObins` for this binary.

[pkexec documentation](https://gtfobins.github.io/gtfobins/pkexec/)

`GFTObins` claims that we can directly be `root` just using below command:

![[TryHackMe/Lianyu/images/32.png]]

What exactly `pkexec` does ?

`pkexec` is part of the PolicyKit package and it is used to execute commands as another user. Typically with root privileges. By using `/bin/sh` with `sudo` target may deploy a shell with root privileges.

YESSS !!!!
Reach out the PoC of the `binary exploitation`.

![[TryHackMe/Lianyu/images/33.png]]

Get your flag directly on the same directory:

![[TryHackMe/Lianyu/images/34.png]]




May The Pentest Be With You ! ! !

![[pentest.jpg]]