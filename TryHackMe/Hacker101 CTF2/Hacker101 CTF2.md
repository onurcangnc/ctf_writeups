Greetings everyone !
Today, I would like to analyze `Micro-CMS v2` and `Encrypted Pastebin` on `Hacker101` platform. As you know, recently I have completed categories including `Trivial` and `Easy` levels. Now let's get start:


## Micro-CMS v2

On the main path, there was a `<li>` element which redirects users to `Changelog` path. 

![[TryHackMe/Hacker101 CTF2/images/1.png]]

On `Changelog` path, `edit/1` endpoint can be seen below. Let me also move on it in order to interact with the application.

![[TryHackMe/Hacker101 CTF2/images/2.png]]

Initially, I tried user:pass combination with `admin:admin`. However, it did not work.

![[TryHackMe/Hacker101 CTF2/images/3.png]]

Mostly, to manipulate `I/O` fields, as a second option I will apply `SQLi`.

`Generic Payloads` are great way to understand whether the application responds to `SQLi` or not. In this session, I used payload from [payloadbox](https://github.com/payloadbox/sql-injection-payload-list)

`' OR '1`

Page response was genuienly interesting because it seems like there was not any sanitization on `user` field or we can ensure that `SQLi` verified.

![[TryHackMe/Hacker101 CTF2/images/4.png]]

To understand the number of columns, I crafted a `UNION` payload with only 1 column:

`' UNION SELECT null -- `

![[TryHackMe/Hacker101 CTF2/images/5.png]]

Observe that it worked well ! !

However, if you apply the same query with 2 columns, it also gives error:

`' UNION SELECT null, null --`

![[TryHackMe/Hacker101 CTF2/images/6.png]]

As you can see above, it gave me an error implying no such thing (two columns). Now, I will keep to move from `UNION` opportunity especially it is more inclusive in terms of detection & bypass compared to `error-based`.

Meanwhile, I also ran `Intruder` to find possible user:pass or user:pass(EMPTY). Still, I could no reach any useful findings.

![[TryHackMe/Hacker101 CTF2/images/7.png]]

After couple of hours, I was curious about why I could not get any output from `SQL` errors. Then start to search about it since I could not directly know the table & column name precisely. Finally, I asked it for gpt to try many of the combinations with my `UNION` query with 1 column.

![[TryHackMe/Hacker101 CTF2/images/8.png]]

I crafted new payload with most suitable ones:

`UNION SELECT password FROM admins --`

then it did not work + it could not invoke `SQLi` directly since the error message said that `Unknown user`. After a couple of attempts, I decided to find the correlated query error from Google images.

```
Traceback (most recent call last):
  File "./main.py", line 145, in do_login
    if cur.execute('SELECT password FROM admins WHERE username=\'%s\'' % request.form['username'].replace('%', '%%')) == 0:
  File "/usr/local/lib/python2.7/site-packages/MySQLdb/cursors.py", line 250, in execute
    self.errorhandler(self, exc, value)
  File "/usr/local/lib/python2.7/site-packages/MySQLdb/connections.py", line 50, in defaulterrorhandler
    raise errorvalue
ProgrammingError: (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near ''''' at line 1")
```


