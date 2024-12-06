Hello everyone, today I would like to share my insights on `hard` level challenge called `Encrypted Pastebin` from `Hacker101` platform.

## First Flag

Manipulating `HTTP` requests is sometimes beneficial especially when we do not detect anything on the `web application` surface. For the first solution, you can either use `browser` or `Burpsuite`.

Except the encryption algorithm information, there was not anything like `XSS`, `Sensitive Data Exposure`, `IDOR` and so on. That's why, I directly analyzed the HTTP requests instead of regular vulnerabilities.

It was interesting to see such an huge `POST` method variable in terms of its length. Instead of variable it seems like `HASH` or `Encryption` mechanism. 

Let's check:

I initially send request with the `title` yilmaz and `textarea` as atilla.

![[TryHackMe/Encrypted Pastebin/images/1.png]]

It might not be seem clearly ,so I also added it as code part:

`r9ZPjaTLJcw4Qv6mxb-6CRHRWOD8fTpCFrkBgR9j4c2L5n83CyI-dkTLPa8gFwCWedquvOIggDLWg8UIG48AaAzIYwYVW7UDKIP0VfCz4sLsQVhgigpoL9zW1JLVNp2bhnUG-hzRLy!ZHvtN5ooBTMcGjKGV!TbZkSu26WOkpOOqWENzJKpB2i-8DX5fQTNFhNTnR8evPZ4q1i5HUTsV7g~~`

I have never seen such thing like that. However, in the main page, application told that I was dealing with `AES128` military graded algorithm on the default path.

![[TryHackMe/Encrypted Pastebin/images/2.PNG]]

Observe that the application protected by `AES128` ,so it was tough to bypass or access unrestricted endpoints, parts and so on... Meanwhile, I decided to play with the `?POST=` parameter to see the reaction of the application. Therefore, I replaced this huge encrypted parameter to `empty` string.

`https://989aa4da0cc7149eddb8b848a4369ee0.ctf.hacker101.com/?post=`

The application crashed and prompted a couple of error messages resembles as `python` compiler errors. 

![[TryHackMe/Encrypted Pastebin/images/3.PNG]]

Most probably application is using `flask` because of the application's hierarchy. For example, `main.py` running the default application and `common.py` is liable for the encryption program in the backend. We cannot still decide on framework ,but the highest prediction for the `Flask`.

## Flag2

When I changed latest letter or any number (byte) application also crashed itself.

For instance:

`/?post=MZCqr4PTxoZv2DjgD14ByzehPbeOfuqe1xtvVNOXDeQfA-J1Iy82t7I0kMkq7ksiZ3GhR-1!elskyRNNcAFlSMSpE8ZN7ozPIhxwUcUyGcSkb23!D8Rexldw8P!NvyJCAgAZBlGqL1PcIcdT0QaEIjC9t67S2pphrM9WKJKOdI0S9OJ5MU1QvjTz4fY7QD1fLAhE3wZ13PircDmfVBM1Ba~~`

I altered `w` to `a` in this scenario then I encountered application flaw:


![[TryHackMe/Encrypted Pastebin/images/4.PNG]]

After that I noticed that post variable using such a conversion:

`post = json.loads(decryptLink(postCt).decode('utf8'))`

Trying a couple of variations might be useful to get other `types of error`:

GOTCHA ! ! !

![[TryHackMe/Encrypted Pastebin/images/5.PNG]]

When you try to exceed the length of the full encrypted deserialization operation, you also find flaw on the application:

In my session, I tried `17 length` payload for $post string.

`MZCqr4PTxoZv2DjgD14ByzehPbeOfuqe1xtvVNOXDeQfA-J1Iy82t7I0kMkq7ksiZ3GhR-1!elskyRNNcAFlSMSpE8ZN7ozPIhxwUcUyGcSkb23!D8Rexldw8P!NvyJCAgAZBlGqL1PcIcdT0QaEIjC9t67S2pphrM9WKJKOdI0S9OJ5MU1QvjTz4fY7QD1fLAhE3wZ13PircDmfVBM1Baa~~`

Observe that I added second `a` letter to exceed payload length, needs to pass `16 length` in total.

Do not consider about this payload because it is applying deserialization.

Most probably, `decryptLink()` method trying to decrypt the `postCt` coming from different section of the application. Plus, it initiates to `UTF8` decoding operation. Raising `PaddingException()`. Therefore, it is suitable to search for PaddingException thing and json conversion category:

Since I got successfully crash the target, I will try all the alphabet against the application.

Results:

![[TryHackMe/Encrypted Pastebin/images/6.png]]

It is clear that there are also matching values specifically `upper case letters`.  This means that what if I match different character set on entire encrypted thing. Since it will be complex, I decided to search for this especially the `PaddingException`.  

After couple of hours, there was a page indicating `padding oracle attack vector`. Therefore, I decided to implement this approach presented on the page.

[Padding Attack](https://www.nccgroup.com/us/research-blog/cryptopals-exploiting-cbc-padding-oracles/)

On this page there was a python script that handles the cryptographic operations. However, our application running on web ,so I immediately customize the script:

**Detect Padding Exceptions**

import requests

def oracle(iv, ct):
    response = requests.post("https://989aa4da0cc7149eddb8b848a4369ee0.ctf.hacker101.com/?post=RHAgDiavHF5VVy-uR0bdS6HxTnZ66adcSVL0EMr5Sr24JdHjNOcJcvexjeQB86GtGUeHyk4iqVjHSxGfjQAh3wkvleSkARGJEHbNit23mKmA15LJm-C0XDD2GXJUg-BRXuBM3zTRam4GzI4ptKVk7ryUEZkcQHvEEdxso6GVR9XSDb92Q7JSZOpmbhtnr4vbmCvgHvg085r5mOnXtGkoGb~~", data={"iv": iv, "ct": ct})
    if "PaddingException" in response.text:
        return False
    return True


,but I could not successfully handle the script. Instead, I found the logic behind the algorithm then found a script against specifically for this implementation.

![[TryHackMe/Encrypted Pastebin/images/7.png]]

Special characters (`~`, `!`, `-`) are replaced to form a standard Base64 string. However, this might not fully fix the string's formatting issues.

`b64d = lambda x: base64.decodestring(x.replace('~', '=').replace('!', '/').replace('-', '+'))`



