
After a long exam period, I have finally started to analyze all the TryHackMe machines again. Let me start with embedding our ip address to customized domain named `willy.thm`.

`nano /etc/hosts`

![[TryHackMe/Chocolate Factory/images/1.png]]


## Reconnaissance

Start with `curl` instead of browser to understand port `80` & `443` response. It is likely more efficient way compared to manual browser approach.

`curl -v willy.thm`

![[TryHackMe/Chocolate Factory/images/2.png]]

