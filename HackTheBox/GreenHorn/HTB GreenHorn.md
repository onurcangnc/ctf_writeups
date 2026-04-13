
## Reconnaissance

Add IP address of target to `/etc/hosts` file.

![[HackTheBox/GreenHorn/images/1.png]]

Conduct port scan at first:

```bash
sudo nmap -sV -sC --max-rate=10000 greenhorn.htb
```

![[HackTheBox/GreenHorn/images/2.png]]

I just moved port `80` to check the whether there is static page or application working currently.

![[HackTheBox/GreenHorn/images/3.png]]

I clicked on both page anchor tags then redirected me two seperated applications which are `pluck 4.7.18` and `Plesk Obsidian 18.0.77`

Found an exploit on `plucl 4.7.18`:

![[HackTheBox/GreenHorn/images/4.png]]

Since we must get access in target host I will use `RCE`.

```bash
cp /usr/share/exploitdb/exploits/php/webapps/51592.py .
```

Normally, it requires you to download a module called `requests_toolbelt`.

![[HackTheBox/GreenHorn/images/5.png]]

It asked a zip file for exploitation ,yet I found another version automatically creates and uploads malicious payload:

[Pluck_Cms_4.7.18_RCE_Exploit](https://github.com/b0ySie7e/Pluck_Cms_4.7.18_RCE_Exploit)

I could not find anything regarding to the exploit explanation just because it requires an admin authentication. Let's move on port `3000`.

I began to fuzz repository management system on port 3000.

```bash
dirsearch -u http://greenhorn.htb:3000 -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
```

![[HackTheBox/GreenHorn/images/7.png]]


During the process, I also manually check pages beginning with `repos` endpoint which is too interesting:

![[HackTheBox/GreenHorn/images/6.png]]


I decided to check credentials manually if there is:

![[HackTheBox/GreenHorn/images/8.png]]

Manual commit history at first will be very useful compared to file to file checks:

http://greenhorn.htb:3000/GreenAdmin/GreenHorn/commit/d3278c32f25df1c2ae16c092b8d383d68bce977d

![[HackTheBox/GreenHorn/images/10.png]]

Manual ways are burden I discovered a page that reveals automatically secrets at the same time `trufflehog`did not find anything.

Clone repo `git clone http://greenhorn.htb:3000/GreenAdmin/GreenHorn`

This cheatsheet worked in my case very well.

[Mining Creds](https://notes.benheater.com/books/web/page/mining-data-from-git-repos)

![[HackTheBox/GreenHorn/images/11.png]]


Let's check files respectively:

