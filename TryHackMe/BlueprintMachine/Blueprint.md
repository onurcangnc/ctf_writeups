
## Reconnaissance:

First of all, to understand whether machine live or not try to
`ping` it.

```
ping 10.10.118.119
```

The output should look like:

![[TryHackMe/BlueprintMachine/images/1.png]]

Add your ip address to `/etc/hosts` file.

```
nano /etc/host
```

Include your ip address the format provided below:

![[TryHackMe/BlueprintMachine/images/2.png]]


Before move on, I highly recommend you to check manually whether `web application` runs on `port 80/443` via browser. In most scenarios, we will not have https protocol.

```
//The route that you need to follow is:
http://blueprint.thm
```

This route automatically interact with HTTP protocol. Most of the time browsers have default routing mechanism directing to port 443. We should always try to route port 80 by just manually adding `http://`

![[TryHackMe/BlueprintMachine/images/3.png]]

Recently, I also tried to check `Apache` commonly running on port 8080:

![[TryHackMe/BlueprintMachine/images/4.png]]

As you can see above, we have an directory named `oscommerce-2.3.4`. I was curious about it ,so I searched about our Operating System commerce app.

![[5.png]]

It is clear that we should trigger RCE through web app. However, further reconnaissance is not harmful :) I also wanted to `fuzz` this route `http://blueprint:8080`

For the fuzzing, I thought that `dirsearch` and `dirb` will be suitable:

`Dirsearch` payload:

```
dirsearch -u http://blueprint.thm:8080
```

![[6.png]]

I just got `/server-status/`, `/server-info` paths. Capturing server data is useful for the architectural understanding. Let me extract what we have so far !


![[7.png]]

I was dealing with `Win32` architecture, `Apache` as a web server and for the backend `PHP` working on the machine. Furthermore, on `/oscommerce-2.3.4/docs/` path, there was a database dump. However, I could not reach any juicy information.

![[8.png]]


The `database scheme` pattern looks like `ER diagram`.

Nmap was beneficial to get extended data about application:

Nmap Payloads:
```
sudo nmap -sV -sC blueprint.thm

sudo nmap -sV -sC -p- blueprint.thm
```

Since I have already get what we need especially architecture of the application. I preferred to use only `default script` scan. Moreover, full port scan was not compatible on this scenario because it ran really slow. Anyway, let's check the `network mapper` output.

![[9.png]]

The results depicted that I did not check only the port `445` as known as `SMB` (Server Message Block).


![[10.png]]

`Nmap` script engine automatically run `default smb scripts` against on target. Lastly, checking the SMB will be crucial to get initial compromise since `nmap` script result revealed the potential discovery on `SMB`.

According to `HackTricks`, we can use `enum4linux` to enumerate the target:

[Pentesting SMB](https://book.hacktricks.xyz/network-services-pentesting/pentesting-smb)

![[11.png]]

```
enum4linux -a 10.10.118.119
```

The most identical part of the `enum4linux` output was the `nbtstat information`.

![[12.png]]

Script could get the `Domain/Workgroup` named `WORKGROUP`. Let me try to authenticate it through without giving credentials.

![[13.png]]

```
	//IPC$ did not allow me to run any commands
	──(root㉿kali)-[/home/kali]
	└─# smbclient -U '%' -N \\\\10.10.118.119\\IPC$  
	Try "help" to get a list of possible commands.
	smb: \> dir
	NT_STATUS_ACCESS_DENIED listing \*
	smb: \> whoami
	whoami: command not found
	smb: \> ls
	NT_STATUS_ACCESS_DENIED listing \*
	smb: \> 
```

SMB did not give me useful findings. Therefore, I switched on exploitdb to get initial compromise.

[RCE](https://www.exploit-db.com/exploits/44374)


![[14.png]]

There was a web app based vulnerability occurs ,so let me apply this manually before I demonstrate all the ways to compromise machine.

Specifically, `PHP engine` shows an error the path `/install.php?step=4`. DB configuration error occured.

![[15.png]]

I intended to do directly manual without any tool ,but it did not work. That's why, lets run `manual exploit

Firstly, edit the `url` part of the script:

![[TryHackMe/BlueprintMachine/images/15.png]]


As you can see below, it did not work because the script automatically tried to execute `system('ls')` command on the OS.

![[16.png]]

However, the web app disabled such commands by default ,so lets run another payload from [Github](https://github.com/nobodyatall648/osCommerce-2.3.4-Remote-Command-Execution)

To understand how the script works, I initially run it just by no parameters and inputs.

