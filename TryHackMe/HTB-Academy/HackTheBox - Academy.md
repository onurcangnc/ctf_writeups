Hi everyone, in this article I would like to analyze `Academy` from `HackTheBox` platform.

![[HTB-Academy/images/1.png]]

Before I begin, let's attach our ip address to customized domain name ->

`nano /etc/hosts`

![[HTB-Academy/images/2.png]]

## Reconnaissance

I wanted to conduct `nmap` scan & `whatweb` enumeration seperately to identify whether there is application or not. Plus if there is application, I iterate the `whatweb` scan twice.

**Full-Scope Faster Scan**:
`sudo nmap -sV -sC -T4 -p- academy.htb`

**Lightweight Version Scan**:
`sudo nmap -sV -Pn --script=vuln academy.htb`

**Rustscan**:
`rustscan -a academy.thm`

Duration was longer than I expected on `nmap` scans.

![[HTB-Academy/images/3.png]]

Due to my VPN, **EU VIP4** I got high ping responses ->

![[HTB-Academy/images/4.png]]

Finally, I was ready to see **port scan** & **whatweb** results ->

**Whatweb** returned such result ->

![[HTB-Academy/images/11.png]]


We have application running on port `80` ->

![[HTB-Academy/images/5.png]]

Nmap results ->

![[HTB-Academy/images/6.png]]

I was able to retrieve juicy endpoints while `nmap` was conducting `NSE vuln` ->
![[HTB-Academy/images/7.png]]

Moreover, versions include a lot of CVE exploits on **SSH** and **Apache 2.4.41** according to scan results. Having direct endpoints via `HTTP enum` resulted in efficient time management.

How to interact with **HTTP** on browsers ?

As all you know, giving URI format is a daily basis method to interact with HTTP protocol ->

![[HTB-Academy/images/9.png]]

On the other hand, simply appending on last sequence to domain `:80` is also useful method ->

![[HTB-Academy/images/8.png]]

During the registration process to the web application, I was also conducting fuzzing on background ->

![[HTB-Academy/images/10.png]]

I used **dirsearch** + **gobuster** combination to pass fuzzing phase so as to examine each endpoint rapidly.

**Dirsearch** ->

![[HTB-Academy/images/12.png]]

**Gobuster** ->

![[HTB-Academy/images/13.png]]

After a couple of attempts in the application, I did not get move further then I started to analyze every packet with `Burpsuite`.


## Exploitation

There was a form retrieving username:password combination from user ->

![[HTB-Academy/images/14.png]]

After I created my first account, except the vulnerable **SSH** and **Apache** version, I did not see anything vulnerable on the application. Then I decided to register as normal user.

When I capture the `POST` request, I detected a parameter called **roleid=**, most likely responsible for user privileges. ->

![[HTB-Academy/images/15.png]]

Moreover, I switched the parameter 0 to 1 ->

![[HTB-Academy/images/16.png]]



However, I was looking for cookie parameter in order to grant my privileges on the application. ->

![[HTB-Academy/images/17.png]]

After an admin user generation, I hesitately logged as admin on `admin.php` ->

![[HTB-Academy/images/18.png]]

It looks like I found a credentials then I preferred this on `SSH` as credentials ->

![[HTB-Academy/images/19.png]]

It was not possible to authenticate as user `cry0l1t3` ->

![[HTB-Academy/images/20.png]]

What's more, I found a domain that was working on staging environment ->
![[HTB-Academy/images/21.png]]

I also added it on my `/etc/hosts` file ->
![[HTB-Academy/images/22.png]]

Now, after I reached target domain, I encountered with a error output corresponding system sensitive php scripts and mysql database credentials ->

![[HTB-Academy/images/23.png]]

In addition to the these information disclosures, I discovered admin use of the server ->
![[HTB-Academy/images/24.png]]


Let's dump the **administrator user credentials** from DB & start post exploitation phase:

Using this juicy resource to understand how we can interact with mysql client ? ->

https://www.bytebase.com/reference/mysql/how-to/top-mysql-commands-with-examples/

Due to my previous `rustscan` result, instead of using port number as `3306` I wanted to use `33060` ->

![[HTB-Academy/images/25.png]]

Although I successfuly put necessary credentials to mysql client, I was not able to connect DB ->

![[HTB-Academy/images/26.png]]

Then I asked `Laravel` to `searchsploit` to find useful vulnerabilities ->

![[HTB-Academy/images/29.png]]

I solely knew that application envionment app key was leaked ,so there should be a way to use it.

`dBLUaMuZz7Iq06XtL/Xnz/90Ejq+DEEynggqubHWFj0=`

`Whatweb` could not get `PHP` version information or framework information. Besides, `Wappalyzer` also did not too. Therefore, I also used to retrieve version through `Burpsuite`. Moreover, Burpsuite could not find version number of PHP.

![[HTB-Academy/images/27.png]]

I tried to authenticate DB ,yet it did not work. Finally, I googled the PHP + appkey combination ->

![[HTB-Academy/images/28.png]]

Gotcha  ! ! !


## Automated Exploitation

Let's check PoC ->

`cat /usr/share/exploitdb/exploits/linux/remote/47129.rb`

It looks like `Ruby` file, most common extension depicts a Metasploit Framework exploit. Then I deployed `msfconsole` ->

```
msfconsole
search Laravel
use 6
```

![[HTB-Academy/images/31.png]]

then RUN:

![[HTB-Academy/images/30.png]]

I wrongly set `APP_KEY` then removed base64 string from appkey. After that switched VHOST parameter as my virtual host `dev-staging-01.academy.htb`.
then I got shell via Metasploit Framework.

![[HTB-Academy/images/32.png]]

## Manual Exploitation

I wanted to use `manual exploitation` to force myself to prepare OSCP exam. On GitHub I found a manual exploit to get direct reverse shell ->

https://github.com/aljavier/exploit_laravel_cve-2018-15133

Follow the steps that I provided so as to prepare exploit ->

![[HTB-Academy/images/33.png]]

Because of the recent updates made by OffSec, we were no longer use internal Python package management system. Therefore, I created virtual environment for the exploit ->

![[HTB-Academy/images/34.png]]

Once you run exploit, you will encounter an usage manual ->

![[HTB-Academy/images/35.png]]

I did not want to execute command instead I needed to get shell via exploit ,so I retrieved a command `--interactive` on the official GitHub page of exploit.

![[HTB-Academy/images/36.png]]

Do not forget to give full URL ->

![[HTB-Academy/images/37.png]]

Now we got fully manual reverse shell via PoC exploit called **exploit_laravel_cve-2018-15133**.

After I got shell, I started to manually enumerate server via sending consecutive commands ->

![[HTB-Academy/images/38.png]]

Then I discovered sensitive files. That's why, let's check what kind of information that includes ?

Observe that I prompted the same file, where debugger renders on browser ->

![[HTB-Academy/images/39.png]]

I want to keep forward to binary exploitation whether it is possible or not. Hence, `linepas` would be suitable ->

https://github.com/peass-ng/PEASS-ng/releases/tag/20250601-88c7a0f6

Deploy a `python web server` to transfer `linpeas` to target ->

![[HTB-Academy/images/40.png]]

It is clear that we have both `python3` and `curl` as binary in target server ->
![[HTB-Academy/images/41.png]]


Check for how to download files via `curl`:

https://www.digitalocean.com/community/tutorials/workflow-downloading-files-curl

I was not able to send it to the target. Let me try binary exploitation via python3 ->

Again it did not work at all.

![[HTB-Academy/images/42.png]]

Try manually read file paths repetitievly ->

```
cd ..; ls -al
cd ../..; ls -al
cd ../../academy; ls -al
cd ../../academy; cat .env
```

After this combination I found another application including different DB user:pass variation ->

![[HTB-Academy/images/43.png]]

Attempt authentication via **mysql** ->
![[HTB-Academy/images/44.png]]

It did not work ,but let me try also `SSH`:

Bingo ! ! !

Fuzzing approach worked for `cy0l1t3` user :)

![[HTB-Academy/images/45.png]]

Capture `user.txt` flag from `/home/cry0l1t3` directory ->

![[HTB-Academy/images/46.png]]

Generally, you can use `temp` folder to run & build script because most of the time this directory has privileges to do such tasks. That's why, I moved `tmp` folder then sent `linpeas.sh` ->

![[HTB-Academy/images/47.png]]

Wait for the `linpeas.sh` task to complete it enumerates all the kernel + OS ->
![[HTB-Academy/images/48.png]]

Kernel PoC exploit's occurence can be seen as below ->
![[HTB-Academy/images/49.png]]

I tried and abuse `Polkit` exploit ,yet it did not work on my instance ->

![[HTB-Academy/images/50.png]]

After further investigations, I discovered a credential looks like `mrb3n` user's credentials ->

![[HTB-Academy/images/51.png]]

**Cyberchef** successfully identified the type of the data ->

![[HTB-Academy/images/52.png]]

YESS ! ! ! It worked.

![[53.png]]

user `mrb3n` can run composer binary ->

![[54.png]]

Let's check `gftobins` ->

![[55.png]]

`Composer binary exploitation` method worked clearly ! ! !

![[56.png]]

Get `root.txt` flag from simply from `/root/` directory ->

`cat /root/root.txt`

![[57.png]]