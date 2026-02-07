# Information Systems Auditing, Controls and Assurance - Cheatsheet

---

## 1. IS Audit Process Overview

The IS audit process consists of three main phases:

**Planning → Fieldwork & Documentation → Reporting & Follow Up**

|Phase|Step|Description|
|---|---|---|
|**Planning**|1. Understanding of the audit areas/subjects|Identify what will be audited|
||2. Risk assessment & general audit plan|Assess risks and create high-level plan|
||3. Detailed audit planning|Develop detailed procedures and timelines|
|**Fieldwork & Documentation**|4. Verifying & evaluating controls|Verify that controls exist and work properly|
||5. Compliance Tests & Substantive Testing|Test adherence to policies and verify accuracy of data|
|**Reporting & Follow Up**|6. Reporting (communicating results)|Communicate findings to management|
||7. Follow up|Ensure corrective actions are taken|

---

## 2. Compliance Testing vs Substantive Testing

### Compliance Testing

Compliance testing checks whether controls are **operating in accordance with policy**. It uses a **sampling** approach.

**Example — Change Management Policy:**

- Programmer makes code changes
- Supervisor approves the changes
- Auditor selects a sample from the change log (Change 101, 102, ... 108) and checks whether each was properly approved

### What if Compliance Testing Fails?

If a sampled change (e.g., Change 104) was **not approved**, then **substantive testing** must be performed on that change.

### Substantive Testing

Substantive testing is a **detailed analysis** triggered when compliance testing fails. The auditor dives into the failed record and performs a **line-by-line review**.

**Example:**

- Compliance testing found Change 104 was not approved → "Not Approved"
- Substantive testing: Examine each line of code within Change 104 (Code 1, Code 2, Code 3, Code 4, Code 5)
- Issue identified in Code 3

> **Summary:** Compliance test → "Does the control exist?" | Substantive test → "Is the data actually correct?"

---

## 3. Audit Procedures

### 3.1 Re-performance

Re-performance means the auditor **independently re-executes a calculation or process** to verify its accuracy.

**Example Scenario:**

1. A Clerk in the Finance Department prepares payroll → pays Staff $10,000/month
2. Staff bribes the Clerk: "Add more hours and I'll give you $5,000"
3. Clerk inflates total overtime from 10 hours to 60 hours (10 + 50)
4. Result: Basic Salary $10,000 + 60 hrs × $200/hr = Total Payment $22,000
5. **Compliance officer manually recalculates** → Correct payment should be $12,000, not $22,000!

> **Key Point:** Re-performance = The auditor performs the calculation from scratch and compares the results.

### 3.2 Confirmation

Confirmation means verifying information through **independent third-party sources**.

**Example Scenario:**

1. Company A (IT Officer) sends a system development request to Company B (Outsource IT Developer)
2. Company B develops and delivers the system
3. Company B invoices $2M
4. Compliance officer contacts Company B directly: "Did it really cost $2M to develop this system?" — obtaining third-party verification

> **Key Point:** Confirmation = 3rd party verification. The auditor verifies information directly from its source.

---

## 4. Risk in Information Systems

### 4.1 What is Risk?

Risk is the possibility of having a negative impact.

![[controls2.png]]

> Risk = Fire (threat) 🔥 | Control = Fire extinguisher (countermeasure) 🧯

### 4.2 Elements of Risk

|Element|Description|
|---|---|
|**Threats**|Natural disaster, Man-made threats (internal: fraud, external: hacking), Technical (hardware failure)|
|**Impact**|Measure of damage|
|**Probabilities**|Likelihood of the risk occurring|

> **Key Point:** Internal threats are more dangerous than external ones because insiders know the organization's business processes and can cause greater damage.

### 4.3 Examples of Risk in IS

|Example|Description|
|---|---|
|Gmail Outage|Worldwide Gmail service disruption|
|Capital One Data Breach|Major data breach exposing customer data|
|Cathay Pacific Ticket Error|First class ticket pricing error|

---

## 5. Risk Assessment

### Step 1: Define Risk — Impact Scale (Measure of Damage)

![[impact.png]]

|Level|Rating|People|Asset|Operation|Environment|
|---|---|---|---|---|---|
|**5**|**Major**|Multiple fatalities or permanent total disability|Extensive damage|Critical failure preventing core activities|Massive and long-term impact|
|**4**|**Serious**|Single fatality or permanent total disability|Serious & major damage|Breakdown of key activities leading to reduction in performance|Major and mid-term impact|
|**3**|**Moderate**|Major injury / health effects|Local damage|Targets not met, reduction in performance|Moderate and controllable impact|
|**2**|**Minor**|Minor injury|Minor damage|Minor delays in operation|Minor impact and easy restorable|
|**1**|**Negligible**|Negligible injury|Negligible damage|Negligible interruption|Negligible impact|

### Step 2: Define the Probability (Likelihood of Having Risk)

![[likelihood.png]]

|Level|Rating|Definition|
|---|---|---|
|**5**|Probable|The event is expected to occur|
|**4**|Likely|The event will probably occur|
|**3**|Possible|The event might occur at some time|
|**2**|Unlikely|The event could occur but is improbable|
|**1**|Very Unlikely|The event could have little or no chance of occurrence|

### Step 3 & 4: Risk Matrix (Probability × Impact)

||1. Negligible|2. Minor|3. Moderate|4. Serious|5. Major|
|---|---|---|---|---|---|
|**1. Very Unlikely**|1 🟩|2 🟩|3 🟩|4 🟩|5 🟩|
|**2. Unlikely**|2 🟩|4 🟩|6 🟩|8 🟨|10 🟨|
|**3. Possible**|3 🟩|6 🟩|9 🟨|12 🟨|15 🟥|
|**4. Likely**|4 🟩|8 🟨|12 🟨|16 🟥|20 🟥|
|**5. Probable**|5 🟩|10 🟨|15 🟥|20 🟥|25 🟥|

**Risk Levels:**

- 🟩 **1-6: Low** → Minor issue of little concern with some small disruptions
- 🟨 **7-14: Medium** → Requires attention, inconvenience and risk occur
- 🟥 **15-25: High** → Requires urgent attention, introduce control to reduce risk

### Risk Assessment Example — Cyber Hacking to Online Server

|Question|Answer|
|---|---|
|What is the threat?|Cyber hacking to online server|
|What is the impact?|**4. Serious** → Breakdown of key activities leading to reduction in performance|
|What is the probability?|**4. Likely** → The event will probably occur|
|**Risk Score**|**4 × 4 = 16 🟥 HIGH**|

---

## 6. Risk Mitigation

Risk mitigation means reducing risks using **controls**.

### Risk Reduction Through Controls

|Risk %|Control|Description|
|---|---|---|
|100%|—|No controls in place|
|80%|Username + Password|Basic authentication|
|60%|Username + Password + Firewall|Network security added|
|50%|Username + Password + Firewall + Encryption|Data encryption added|
|40%|Username + Password + Firewall + Encryption + Biometrics|Biometric authentication added|
|0%|❌ Eliminate risk impossible|Complete risk elimination is not possible!|

> **Cost Effective Decision:** Senior management typically accepts **60% risk level** (Username + Password + Firewall). As controls increase, so does cost. Management balances control strength against cost.

### Control Example

![[controls1.png]]

> IT staff notifies general staff to change their username and password every 3 months. This is a simple **preventive control** example.

### Risk Mitigation Options

|#|Option|Description|
|---|---|---|
|1|**Reduce**|Use controls to lower risk to a level acceptable by senior management|
|2|**Transfer**|Transfer remaining risk to a third party (e.g., insurance policy)|
|3|**Avoid**|Avoid the risky activity entirely (e.g., not offering e-banking)|

> ⚠️ **Eliminate ≠ Avoid:**
> 
> - **Eliminate:** Continue with e-banking, add many controls, and claim "no risk" → **Not possible!**
> - **Avoid:** Don't do e-banking at all, stick to traditional banking only → Leads to customer loss, **not preferred**

---

## 7. Risk Re-evaluation

Risk management is a **cyclical process**:

**1. Risk Assessment → 2. Risk Mitigation → 3. Risk Re-evaluation → (back to step 1)**

### When Do We Perform Risk Re-evaluation?

|Trigger Type|Description|Example|
|---|---|---|
|**Time Driven**|Periodically — every six months or once a year|Scheduled assessment|
|**Event Driven**|Environmental change, government regulation, natural disaster|Japan earthquake (nuclear plant meltdown) → environmental change|

---

<<<<<<< HEAD
# Identify Internal Controls

## Feasibility and Requirements

**Why develop new application ?**
- New opportunity to new/existing business process
- Problem found in business process
- New opportunity to take advantage of technology (e.g. FinTech)
- Problem with current technology

**Software Development Lifecycle**

![[sdlc.png]]

Traditional system development lifecycle approach

**Phase 1 - Feasibility** -> **Phase 2 - Requirements** -> **Phase 3A - Design** -> **Phase 3B -Selection** -> **Phase 4A - Development** -> **Phase 4B - Configuration** -> **Phase 5 - Implementation** ->
-> **Phase 6 - Post Implementation**

![[sdlc2.png]]

**In these SDLC phases, which one is the most important one ?**

The most important phase is phase 2 which is the requirement phase.

*Note:* If we don't do well in the phase 2, our entire system development would be a failure.

**What is feasibility study ?**
Yes, there are three different ones. We call them operational feasibility, technical feasibility, and economic feasibility.
### Phase 1 - Feasibility
- **Operational Feasibility:** Operational feasibility means whether that system is being developed whether we can operate within our organization, whether we have software or hardware to operate the system.
- **Technical Feasibility:** Technical feasibility means whether we have expertise to develop system, as well as maintain systems within ourselves.
- **Economic Feasibility:** The system gives you an economic benefit. That's something that we look at economic feasibility.

**What is the definition of requirements ?**
We are trying to find out what is needed for the users because most important people for a system are whoever use the system.
### Phase 2 - Requirements
- Identify & specify business requirements during feasibility study
- Description, users interaction, operation conditions & information criteria.

They could be your employee, customers that means if you are developing a banking system,
Whoever it is, the person that uses a system day in day out. If they aren't happy with your new system development, no matter how good you think the system is, system will be retired very soon. So the most important thing are the users, what they feel about.

## Design and Selection

**What do you think? What's the difference between 3A and 3B?**

- 3A means we develop in house
- 3B means we do outsource the system development

![[sdlc3.png]]

what are the different ways for us to have a system in our place ? What we can do is one thing, we can develop the system by ourselves, we call it in house development or we can outsource it that means we can ask someone.

1) Just by package and use exactly as it is.
2) There is a package out there ,but package does not really fit to your organization, your business process, your business need. We asked them to modify the package to a certain extent so that the package will be fit to use into your system.
3) There is no package. Your system is very unique, something like financial technology, you ask someone else to develop a system, brand new system and give it to us.

### Phase 3A - Design

- In house development 
### Phase 3B - Selection

- Outsource development

**Careful:** If you outsource the system development, whatever the future maintenance means fixing the bug, adding a new feature, you cannot do it by yourself you won't get the source codes.
=======
## 8. Internal Controls — System Development Life Cycle (SDLC)

### SDLC Phases Overview

![[design.png]]

|Phase|Name|Description|
|---|---|---|
|Phase 1|**Feasibility**|Feasibility study|
|Phase 2|**Requirements**|Requirements analysis|
|Phase 3A|**Design**|System design for in-house development|
|Phase 3B|**Selection**|Vendor/package selection for outsourcing|
|Phase 4A|**Development**|In-house coding and development|
|Phase 4B|**Configuration**|Configuration of outsourced system|
|Phase 5|**Implementation**|System go-live|
|Phase 6|**Post Implementation**|Post go-live review and evaluation|

> **3A vs 3B Difference:** 3A (Design) is the in-house development path, 3B (Selection) is the outsourcing path. Similarly, 4A (Development) and 4B (Configuration) correspond to these two paths.

### System Acquisition Methods

|Method|Description|
|---|---|
|**In-house Development**|Develop the system internally (Phase 3A → 4A)|
|**Outsourcing — Package (as-is)**|Buy a ready-made package and use it as-is|
|**Outsourcing — Modified Package**|Buy a package and have it customized to fit your needs|
|**Outsourcing — Custom Development**|Have a vendor build a fully custom system|

### Key Considerations for Outsourcing

|Consideration|Description|
|---|---|
|**Software Escrow Agreement**|Protects source code if the developer goes bankrupt|
|**Reliability**|Vendor reliability (not just cost)|
|**Installation Support**|Whether the vendor helps with system installation|
|**User Manuals**|Whether the vendor helps develop user documentation|
|**Training**|User training — "train the trainers" approach so internal staff can train others|

---

## 9. Development Phase — Testing

![[development.png]]

Testing is the **most important part** of the development phase. Bugs and errors must be found and fixed before implementation.

### Testing Levels

|Test Type|Scope|Focus|Performed By|
|---|---|---|---|
|**Unit Testing**|Single module|Input/Output correctness|Developers|
|**Integration Testing**|Multiple modules together|Inter-module communication and interfaces|Developers|
|**System Testing**|Entire system|End-to-end behavior|IT Team|
|**Final Acceptance Test (UAT)**|Business requirements|User satisfaction|**End Users**|

### Unit Testing vs Integration Testing

![[testvs.png]]

- **Unit Testing:** Tests a single module in isolation. Give input, observe output. No dependency on other modules.
- **Integration Testing:** Tests how two or more modules work together. Module 1's output may be Module 2's input — this interface is what gets tested.

### System Testing Types

|Test Type|Description|Key Question|
|---|---|---|
|**Recovery Testing**|Deliberately crash the system and measure how fast it can be recovered|Can the system recover after failure?|
|**Security Testing**|Test security features using penetration testing and ethical hacking|Is the system protected from attacks?|
|**Volume Testing**|Input large amounts of data to see if the system malfunctions|Can the system handle large data volumes?|
|**Stress Testing**|Many concurrent users access the system at the same time|How does the system behave under extreme load?|
|**Performance Testing**|Speed and efficiency testing (benchmarking — compare two similar systems)|How fast and efficient is the system?|

> **Most Important Test:** **Final Acceptance Test (UAT)** — All other tests are performed by IT staff, but UAT is done by **end users**. If users are not satisfied, the system will retire quickly.

### Phase 4B — Configuration (Outsourcing)

When a system is built by an external vendor or purchased as a package, the configuration phase ensures it is **properly configured** to meet the organization's needs and the auditor's required controls.

---

## Recent News of Risks Related to IS

|#|Incident|Date|Description|
|---|---|---|---|
|1|Google Outage|Jun 2019|YouTube, Gmail, Snapchat went down|
|2|Facebook Data Leak|Sep 2019|419 million users' data exposed|
|3|AWS DDoS Attack|Oct 2019|Sustained DDoS attack on AWS servers|
|4|Insider Threats Report|Oct 2019|Workers identified as biggest data security threat|

---

> **Note:** This cheatsheet is compiled from the Information Systems Auditing, Controls and Assurance course lecture materials.
>>>>>>> 69086ac (new study notes)
