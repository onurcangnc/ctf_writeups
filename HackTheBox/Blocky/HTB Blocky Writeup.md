
Begin with attaching IP address to domain:

`nano /etc/hosts`

![[ctf_writeups/HackTheBox/Blocky/images/1.png]]

Firstly, check  80,443,8080  ports + conduct ` automated reconnaissance` 

![[ctf_writeups/HackTheBox/Blocky/images/2.png]]

Looks like Wordpress frontend. On meta part and footer it is observable

![[ctf_writeups/HackTheBox/Blocky/images/3.png]]

Let's conduct `port scan` & `fuzzing` respectively.

use both at the same time ->

`sudo nmap -sV -sC blocky.htb`

![[ctf_writeups/HackTheBox/Blocky/images/4.png]]

`sudo nmap -sV -sC -T4 -p- blocky.htb`

Faster results in 65535 ports

![[ctf_writeups/HackTheBox/Blocky/images/5.png]]

No meaningful services.

![[ctf_writeups/HackTheBox/Blocky/images/6.png]]

To dive into SMB shares  I conducted `enum4linux` scan.

![[ctf_writeups/HackTheBox/Blocky/images/7.png]]

There were no juicy findings.

Fuzzing matters ,but let me initially give a chance to `wpscan`

Clear RCE vector plugin can be seen below

![[ctf_writeups/HackTheBox/Blocky/images/8.png]]

Checking fuzz results:

`dirsearch -u blocky.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt`

Interesting path -> /plugins

![[ctf_writeups/HackTheBox/Blocky/images/10.png]]


Apply `--enumerate u` so as to identify current users available on application:

`wpscan --url http://blocky.htb --enumerate u`

![[ctf_writeups/HackTheBox/Blocky/images/11.png]]

Returning back to java files, I found a generic `root:pass` combination.

![[12.png]]

Upon that finding, I tried on SSH ,but still stucks. However, after a successful fuzzing operation, I saw phpmyadmin login.

![[13.png]]

Found user pass as hashed format.

![[14.png]]

Lets check via `Crackstation`

Could not determine

![[15.png]]

I used `hashes.com` to identify regarding hash type

![[16.png]]

Use `hash-identifier "$P$BiVoTj899ItS1EZnMhqeqVbrZI4Oq0/"`

![[17.png]]

Ready to brute via `hashcat`

![[18.png]]

`hashcat -m 400 o.hash /usr/share/wordlists/sqlmap.txt`

I was not successfuly. Instead, let me try to use password as SSH user `notch`

![[19.png]]

[GFTObins](https://gtfobins.org/) perfectly fine actually or I will figure out through `linpeas`.

Understand what commands can `notch` run ->

![[20.png]]

ITS OK. `Notch` can run everything as `Blocky` (AKA ROOT) do.

`sudo -u#-1 /bin/bash` from [HackTricks](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html#path)

![[21.png]]

I took `root` privileges as you can see above.

Find flags ->

![[22.png]]

![[23.png]]

