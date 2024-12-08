Greetings everyone, hope you are well. Today I had the opportunity to  analyze `Archangel`, başmelek in Turkish from `TryHackMe` platform. 

Add your ip address to `hosts` file to make customizable domain. This is a local method to override `DNS resolution` and create your own domain mappings for testing, development, or other purposes.

### Run commands respectively

- `nano /etc/hosts`
- `<ipv4 address> <customized domain name>`
- `Control S and X`


### Final Result:

![[TryHackMe/Archangel/images/1.png]]


## Reconnaissance

The faster you conduct reconnaissance, the more time you gain for the `vulnerability detection` and `exploitation` phases. Cyber intelligence is always a significant asset in understanding the technology an application uses and its vulnerability scope.

As penetration testers, we frequently seek to move directly to the vulnerability exploitation phase, but we should first gather information about the target, whether it involves application testing or local area network assessments. That's why I conducted a `curl` scan to identify HTTP ports `80`, `443`, and Apache `8080`. If further investigation is required, we should also perform a full-port scan. The technique I usually use is a demand-based approach, meaning we apply what is necessary based on the situation.

Let's use `curl`:

`curl -v cuneyt.sevgi`

By default it will automatically move forward to port `80`

![[TryHackMe/Archangel/images/2.png]]

There is nothing on other ports `443` and `8080`:

![[TryHackMe/Archangel/images/3.png]]

Port `80` successfully identified web page's `html` structure and prompted as terminal output. Let me first analyze the source code's comment part and manually investigate with browser.

I saw an email address with domain `@mafialive.thm` as an internal information.

![[TryHackMe/Archangel/images/4.png]]

After a couple of page discover attempts, there was nothing especially uniquely identifiable data on the page content. Nearly entire page consisting default configuration texts, source files and so on... 

![[TryHackMe/Archangel/images/5.png]]

![[TryHackMe/Archangel/images/6.png]]

Majority of the navigation elements redirected me to empty hyperlinks. Therefore, it would be suitable to `fuzzing` phase.

I utilized couple of tools including `dirsearch`, `dirb`, `gobuster`.

### Used Payloads:

- dirsearch -u http://cuneyt.sevgi
- dirb http://cuneyt.sevgi
- gobuster dir http://cuneyt.sevgi -w /usr/share/wordlists/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt


I deliberately ended the `gobuster` scan due to the length of wordlist. It also detected the paths included in both `dirseach` and `dirb`.

![[TryHackMe/Archangel/images/7.png]]

![[TryHackMe/Archangel/images/8.png]]

![[TryHackMe/Archangel/images/9.png]]

`dirb` and `gobuster` was trying to recursively fuzz the entire directory structures ,so I terminated the process.

After I navigated through `/flags/` endpoint there was a file, redirected me to this page:

![[TryHackMe/Archangel/images/10.png]]

There was not any clues about `flags`. Therefore, it was suitable to conduct port scan. Furthermore, you can reach out the `web server` version & type.

![[TryHackMe/Archangel/images/13.png]]


![[TryHackMe/Archangel/images/11.png]]

Wappalyzer result:

![[TryHackMe/Archangel/images/12.png]]


I conducted different port scans with below commands:

`sudo nmap -sV -T4 -p 20-1000 cuneyt.sevgi`

`sudo nmap -sV -sC cuneyt.sevgi`

`sudo nmap -T4 -A cuneyt.sevgi`

However, the results were not sufficient to move to the `exploitation` phase. There must be undiscovered content on the web application or a web-based vulnerability to gain a shell on the target. That's why I would like to move the content referred to a youtube video where I previously demonstrated techniques in the `fuzzing` phase.

**Notice:** I could not find anything technical part such as dynamic page rendering content or backend instance. Observe the answer format: `something.***`.

![[TryHackMe/Archangel/images/15.png]]

After a long time, I was suspicious about the email and its domain. Although I tried different approach against target, I also wanted to add the given hostname `mafialive.thm`. Maybe there was another gate (web app or static page) for different `DNS resolution`. Technically, there was not anything since I applied main & essential methodologies on the instance.

**Immediately change & refresh the page then result was different:**

![[TryHackMe/Archangel/images/14.png]]

Let's check `test.php` and `robots.txt`.

![[TryHackMe/Archangel/images/16.png]]

Contents of endpoints:

![[TryHackMe/Archangel/images/17.png]]

`User-agent:` All bots (crawlers)
`Disallow:` These bots cannot crawl this endpoint.

![[TryHackMe/Archangel/images/18.png]]

It looks like `file-inclusion` or `LFI/RFI`.







