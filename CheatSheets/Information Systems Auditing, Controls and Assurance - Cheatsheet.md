# Risk in Information Systems - Cheatsheet

---

## 1.2 Introduction to Risk in Information System

### What is Risk?

Risk, according to my understanding, is a possibility of having a negative impact.

---

## Elements of Risk

|Element|Description|
|---|---|
|**Threats**|Natural disaster, Man-made threats (internal: fraud, external: hacking), Technical (hardware failure)|
|**Impact**|Measure of damage|
|**Probabilities**|Likelihood of having risk|

### Who can give you the highest damage?

The internal man-made threats are more serious than the external ones because internal person is within the organization and knows your business process, so they can damage you the most compared to external.

> **Key Point:** Internal threats give more damage to the organization than external ones.

---

## Examples of Risk in Information System

|Example|Link|
|---|---|
|Gmail Outage|https://www.cnet.com/news/gmail-is-down-outage-around-the-world-for-some-users/|
|Capital One Data Breach|https://www.nytimes.com/2019/07/29/business/capital-one-data-breach-hacked.html|
|Cathay Pacific First Class Ticket Error|https://www.scmp.com/news/hong-kong/hong-kong-economy/article/2181853/cathay-pacific-sells-first-class-ticket-portugal|

---

## Impact

![[impact.png]]

---

## Probabilities

Likelihood of having risk

![[likelihood.png]]

---

## Recent News of Risks Related to Information Systems

|#|Incident|Date|Link|
|---|---|---|---|
|1|Google recovers from outage that took down YouTube, Gmail, and Snapchat|Jun 2019|https://www.theverge.com/2019/6/2/18649635/youtube-snapchat-down-outage|
|2|Unsecured Facebook Databases Leak Data Of 419 Million Users|Sep 2019|https://www.forbes.com/sites/daveywinder/2019/09/05/facebook-security-snafu-exposes-419-million-user-phone-numbers/#18a045b71ab7|
|3|AWS servers hit by sustained DDoS attack|Oct 2019|https://www.cloudpro.co.uk/cloud-essentials/public-cloud/8276/aws-servers-hit-by-sustained-ddos-attack|
|4|Reports says workers are biggest data security threat|Oct 2019|http://www.startribune.com/insiders-drive-most-cyber-security-breaches-according-to-study-for-minnesota-s-code42/562174112/|

---

## Risk Management Process Overview

What is the process of risk management?

|Step|Process|
|---|---|
|1|Risk Assessment|
|2|Risk Mitigation|
|3|Risk Re-evaluation|

---

## Risk Management Process 1 - Risk Assessment

- Identify area of having high risk
- 3 elements of risk: Threats, Impact, Probabilities

### Step 1: Define Risk

![[risk.png]]

### Step 2: Define the probability of having risk

_e.g. based on historical data_

![[risk2.png]]

### Step 3: Identify the risk for different threats & create the risk matrix

![[risk3.png]]

### Step 4: Rate the risk

![[risk4.png]]

---

## Risk Assessment Example

**Risk to your organization**

|Question|Answer|
|---|---|
|What is the threat?|Cyber hacking to online server|
|What is the impact?|4. Serious impact: Operation → Breakdown of key activities leading to reduction in performance|
|What is the probability?|4. Likely → The event will probably occur|

**Multiply on matrix →**

![[risk5.png]]

---

## Risk Management Process 2 - Risk Mitigation

Risk mitigation means reduce the risks using controls.

### Risk Mitigation Example

**How can we reduce the risk of cyber hacking?**

![[risk6.png]]

![[risk7.png]]

![[risk8.png]]

![[risk9.png]]

---

### What are the options if senior management still not happy with the existing risk?

|Option|Description|
|---|---|
|**Transfer the remaining risk to 3rd party**|Insurance Policy|
|**Avoid the risk**|Example: We are a bank and would like to go for e-banking. It seems that e-banking is high risk for organization. We are worrying about the data lost maybe hacking to your customers information. You decided to continue with traditional banking, but no e-banking.|

---

### What is the difference between eliminate the risk and avoid the risk?

|Action|Meaning|
|---|---|
|**Eliminate the risk**|We still go for e-banking and we come up with many many controls and decide, we don't have risks at all.|
|**Avoid the risk**|No, we don't do e-banking, but we do traditional banking only.|

> ⚠️ **Note:** Not doing e-banking leads to lose customer - **DONT PREFERRED**

---

### Risk Mitigation Options Summary

|#|Option|
|---|---|
|1|Reduce the risk using control to a level acceptable by senior management|
|2|Transfer the risk to third party|
|3|Avoid the risk|

> ⚠️ **Remember: Cannot eliminate**

---

## Risk Management Process 3 - Risk Re-evaluation

### When are we doing risk evaluation?

Two different scenarios that we do risk re-evaluation:

|Trigger Type|Description|Example|
|---|---|---|
|**Time Driven**|Periodically - once every six months or once every year|Scheduled assessment|
|**Event Driven**|Environment change (something changed within organisation or similar organisations), government regulation, natural disaster|Japan earthquake (nuclear plant melt down) → environment change example|

---

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