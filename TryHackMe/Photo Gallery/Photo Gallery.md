Hi everyone ! First of all, have a nice weekend. Today I am going to solve `Photo Gallery` challenge from `Hacker 101` platform. Before I start, as always I try to give insights on source code. There might be useful findings beforehand.

![[TryHackMe/Photo Gallery/images/1.png]]

As you can see above, we have source images with correlated paths `fetch?id=` parameter. Let's see what will occur if we change the parameter to invalid & incremental ways.

Since I saw the `Invisible` `<br>` element on the page, I decided to fuzz the `id` parameter to reveal anything related to the flag. However, it did not work.

![[TryHackMe/Photo Gallery/images/2.png]]

Checking the running web app information always beneficial in most scenarios.

![[TryHackMe/Photo Gallery/images/3.png]]

Meanwhile, I ran `steganograph` tool called `exiftool` against the cat images:

![[TryHackMe/Photo Gallery/images/4.png]]

![[TryHackMe/Photo Gallery/images/5.png]]

Now, from my perspective, hidden data still inside the parameter in `fetch?id=3`.

I tried to send `POST`, `DEBUG` methods rather than `GET` ,yet still it was restricted.

![[TryHackMe/Photo Gallery/images/6.png]]

I noticed that images rendered as binary file not their corresponding `Content-Type`, image.

![[TryHackMe/Photo Gallery/images/7.png]]

`content-type` was `text/html` in this scenario ,but normally it has to be `image` instead of text/html because of the file type. It does not matter whether it is text/html or image on the rendering process. Hence, maybe as a last shot, I should also checked `SQLi` on `id` parameter. 

I initially ran `sqlmap` with the most basic attributes:

`sqlmap -u "https://1b8c95d2a8314425fe2ae8a3dedf3b3a.ctf.hacker101.com/fetch?id=1"`





