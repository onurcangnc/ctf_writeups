
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

