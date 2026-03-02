
(OPTIONAL)

Add given ip to host file `keeper.htb

`nano /etc/hosts`

![[HackTheBox/Keeper/images/1.png]]

Conduct `nmap` scan ->

fast-forward full scope 

`nmap -sV -sC -T4 -p- 10.129.229.41`

22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.3
80/tcp open  http    nginx 1.18.0 (Ubuntu)

Only ports below were open.

![[HackTheBox/Keeper/images/2.png]]

No results for `keeper.htb` in fuzzing ->

![[HackTheBox/Keeper/images/3.png]]

Let's check port `80`

![[HackTheBox/Keeper/images/4.png]]

Simple html with referencing another page let's add this also `hosts` file.

![[HackTheBox/Keeper/images/5.png]]

Now I conducted fuzzing on `tickets.keeper.htb` subdomain.

![[HackTheBox/Keeper/images/6.png]]

Jump to `/rt/` endpoint directly.

![[HackTheBox/Keeper/images/7.png]]

I did not see any exploit regarding to application login bypass via `searchsploit`. Therefore, I tried to search for default creds ->

![[HackTheBox/Keeper/images/8.png]]

on base endpoint `/` credentials did not work ,so I also applied on `/rt/` so as to ensure myself to be in correct backend proxy position.

![[HackTheBox/Keeper/images/9.png]]

Now I am in admin dashboard. Enumerate users ->

![[HackTheBox/Keeper/images/10.png]]

![[HackTheBox/Keeper/images/11.png]]

Observe that user pass includes in comments section. Let's connect through SSH.

![[HackTheBox/Keeper/images/12.png]]

Begin to see available binaries.

![[HackTheBox/Keeper/images/13.png]]

Took user flag:

![[HackTheBox/Keeper/images/14.png]]

Unzip zip file ->

`unzip RT30000.zip`

![[HackTheBox/Keeper/images/15.png]]

I searched for keepass keyword and found a repo related vulnerability -> [CVE-2023-32784](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-32784)
https://github.com/z-jxy/keepass_dump

To analyze, retrieve files to local:

`scp lnorgaard@keeper.htb:~/RT30000.zip /tmp/`

![[HackTheBox/Keeper/images/16.png]]

clone the repo -> `git clone https://github.com/z-jxy/keepass_dump?tab=readme-ov-file`

`unzip` again and move `.dmp, kdbx` files to `keepass-password-dumper` directory

![[HackTheBox/Keeper/images/17.png]]

The process terminated ,yet I found really extraordinary string

`dgrd med flde`

![[HackTheBox/Keeper/images/18.png]]

Sent to search engine

![[HackTheBox/Keeper/images/19.png]]

The found string is a dessert ->

`rødgrød med fløde`

![[HackTheBox/Keeper/images/20.png]]

The string is associated with the master password of KeePass ,so I identified a apt package called `keepass2` just by apt install `keepass` then it recommended correlated GUI tool.

![[HackTheBox/Keeper/images/21.png]]

Simply run the tool as `keepass2` then click folder icon (open database).

![[HackTheBox/Keeper/images/22.png]]

Find and select `passcodes.kdbx` file

![[HackTheBox/Keeper/images/23.png]]

Now it will ask the master password which is `rødgrød med fløde` ->

![[24.png]]

Click no by default.

![[25.png]]

Simply click the masked password on root user

![[26.png]]

Now authenticate as `root:F4><3K0nd!`

![[27.png]]

It did not work. Notice Putty user key file can be seen here ->

![[28.png]]

Now I did not have previous experience on how to conver Putty user key file to SSH ,so I discovered such a useful resource about it.

https://superuser.com/questions/232362/how-to-convert-ppk-key-to-openssh-key-under-linux

![[29.png]]

I passed through private-openssh so as to connect via `root` user.

`puttygen /home/kali/Desktop/putty.ppk -O private-openssh -o /home/kali/Desktop/root_id_rsa`

Connect with private key ->

`ssh -i root_id_rsa root@keeper.htb`

![[30.png]]

Get the root flag ->

![[31.png]]