
# AI-ML Security Threats

## Machine Learning
The next significant advancement in the development of AI came with the emergence of ML. 

ML is a subfield of AI that refers to a computer’s ability to learn from data without being given instructions and is comparable to how the human brain learns. Over time, with more data and time, these algorithms will get better at accuracy and decisions.

![[ai1.png]]

ML follows a structured lifecycle to ensure the reliable development and deployment of models. This process begins with defining the problem, such as determining whether an email is spam. Next, data is collected, cleaned, and prepared through feature engineering, ensuring meaningful patterns are extracted while avoiding overfitting (When a model's familiarity with the training data causes a failure to make generalisations on unseen/raw data).

The model is then trained using a selected algorithm, followed by evaluation and tuning to optimise performance. Once refined, the model is deployed into a production environment for real-world use, such as classifying emails in real-time.

The lifecycle doesn’t end there—ongoing monitoring ensures the model maintains accuracy over time, triggering retraining when needed. Since models require continuous improvement, the Machine Learning Lifecycle remains an iterative process.

![[ai2.png]]

## Machine Learning Algorithms

ML algorithms are the mathematical methods used to learn patterns from data, while ML models are the trained outputs derived from these algorithms. These algorithms consist of three key components: a decision process, which makes predictions or classifications based on input data; an error function, which evaluates performance and provides feedback; and a model optimisation process, which fine-tunes the algorithm to minimise errors and improve accuracy. This iterative process continues until the model reaches a satisfactory performance level.

![[ai3.png]]

ML algorithms fall into four main categories: 
- supervised
- unsupervised
- semi-supervised
- reinforcement learning. 

**Supervised learning** relies on labeled data to train models for classification or regression tasks, such as predicting house prices or identifying spam emails. 

**Unsupervised learning**, on the other hand, works with unlabeled data to discover hidden patterns, often using clustering, association, or dimensionality reduction techniques. 

**Semi-supervised learning** combines elements of both, using a small portion of labeled data to guide the learning process. 

Finally, **reinforcement learning** mimics human learning by rewarding correct decisions and penalizing mistakes, allowing an agent to refine its actions over time to achieve the best outcome.

## Neural networks and Deep learning

If you recall, the main objective of AI is to enable computers to behave like humans. One method that allows us to do this is through the use of neural networks. If you cast your mind back to high school biology, you may remember being taught how the human brain works. The human brain processes information using interconnected neurons (a type of cell responsible for transmitting communications between the body and brain), which communicate with each other using synapses. Synapses allow the brain to send electrical/chemical signals from neuron to neuron; in other words, they are a connection. This network of neurons learns by adjusting the strengths of these connections when we experience something new based on patterns we encounter. It's this behaviour that is replicated in a neural network.

![[ai4.png]]

Like the human brain processes sensory input, the input layer receives raw data, with the number of nodes depending on the data type (e.g., a 4x4 pixel image has 16 nodes). Each node represents a neuron, and connections between them act as synapses. The hidden layers process and refine the input, bringing the network closer to a prediction. Each connection has a weight, determining its importance.

For example, in email classification, the body text might have more weight than the subject line. The output layer then produces the final prediction.

![[ai5.png]]

Each hidden layer extracts different features early layers detect edges and curves, while deeper layers combine these patterns to form a complete number. 

For example, lines may suggest a 1 or 7, while curves increase the likelihood of a 3, 8, or 0. The output layer, with 10 nodes (one per digit), selects the most likely number based on the highest prediction value. 

This self-learning process mimics the human brain, and when a network has more than three layers, it is classified as a DL algorithm hence the term "deep learning."

![[ai6.png]]
DL and ML can get confused sometimes, but we can now understand the key differences with what we've covered so far. Like ML, DL is concerned with receiving data as input and producing some kind of prediction or classification as output. 

DL can take in labelled datasets (like the ones mentioned when covering supervised learning), but the key difference is that DL doesn't need the data to be labelled. 

A DL algorithm can take unlabelled, unstructured raw data and determine its key features, which separate it from other categories. The important advantage here over ML is that the data doesn't need labelling; this means DL doesn't require human interaction and, in that way, is self-learning. It makes sense then that DL is possible through the leveraging of neural networks.

No human intervention is needed, larger datasets can be processed and can, therefore, be thought of as "scalable ML". The idea of neural networks has been around for decades and decades, so how come the true potential of DL has only exploded over the last decade or so? This is largely due to the mass digitisation of information in recent years; suddenly, masses of information was available to learning algorithms, and so, with DL, started a new era of AI in which we would unlock more potential and capabilities.

# LLMs

From our goal to have computers behave like humans, the AI field was born, a field that would come closer to achieving that goal with the introduction of ML. In more recent years, the further development of these fields has allowed us to unlock even more potential with neural networks and DL, both of which play a crucial role in enabling our next industry-changing technology: LLMs.

![[ai7.png]]

Now, I'm no ML algorithm, but if I had to assign a prediction score to the chance of this room's user base having heard of ChatGPT, it would be very high. 

ChatGPT emerged smack back in the middle of "The AI Boom"; its ability to generate human-like text in response to a user query blew the minds of near everyone with the technology triggering discussions in the news, politics, education, industry, the list goes on.

## What are LLMs, and how do they work?

Large Language Models (or LLMs) are deep learning-based AI models that can process and generate text by predicting the next word in a sequence. For example, consider this quote:

`Ever have that feeling where you're not sure if you're awake or ----`

This quote is missing the final word. This quote would be fed into the LLM, and it would be tasked with predicting what the final word is likely to be. When you query a chatbot, this is what is happening in the background. Predictions are being run quickly on what word would likely be next in the response of an AI chat to this query, but how?

LLMs are first trained in a "pre-training" phase, where they process vast amounts of text, GPT-3 alone was trained on data that would take a human 2,600 years to read nonstop. More advanced models, like GPT-4, require even greater datasets, made possible by DL.

 Instead of relying on labelled data, LLMs use billions of parameters that function like puzzle pieces, enabling them to understand and generate human-like language when assessed together. These parameters are fine-tuned automatically as the model processes text, adjusting based on prediction accuracy to improve response quality. They begin by generating a word at random to finish the text:

`Ever have that feeling where you're not sure if you're awake or egg`

The guess is then compared with what the correct final word actually was, and the parameters are fine-tuned to make it more likely to predict what, in fact, was the right word until the model can accurately predict the correct word to end the sentence (and less likely to choose the incorrect words) using an algorithm called backpropagation:

![[ai8.png]]Now imagine this process happening trillions of times, repeating this process over and over again until it can not only predict the end of the training data but also raw unseen data. The sheer scope of what is being discussed here is only possible due to advancements in hardware, like GPUs (Graphics Processing Units), enabling masses of parallel operations and processing of large datasets as well as advancements in neural networks, specifically a type of neural network called transformer neural networks.

Introduced in Google's 2017 paper Attention is All You Need, transformer neural networks revolutionized LLMs by enabling parallel text processing instead of sequential word-by-word analysis. This breakthrough allowed models to assign "attention" to key words, improving contextual understanding. 

By encoding words into numerical values and calculating attention scores, transformers enhance accuracy, helping models correctly interpret ambiguous references, like distinguishing whether "it" in this sentence refers to "the bank" or "the loan.":

"The bank approved the loan because it was financially stable."

After the pre-training, humans come back into play, performing a step called RLHF (Reinforcement Learning from Human Feedback). 

This is when predictions are reviewed, and any that would be considered unhelpful by a user or have issues are flagged and the parameters are adjusted accordingly. 
Once trained and reinforced, the LLM can be used, whether as a translator, chatbot, etc. A query is fed to it, and using its trained model, it predicts what the next word would be as a response, and so on and so on until the user has a complete response.

LLMs power generative AI products like ChatGPT and LLaMA, which create original text-based content in response to user prompts. Generative AI as a whole extends beyond text, enabling the creation of images, music, and more. The recent AI boom is the result of years of research and innovation, not an overnight development. We’ve now explored key concepts that trace AI’s evolution—let’s quickly recap how they all connect.

![[ai9.png]]

**Artificial Intelligence** (AI) is the overarching field, encompassing all systems that mimic human intelligence. 

**Machine learning** (ML) is a subfield of AI that enables systems to learn patterns from data without explicit programming. 

**Deep learning** (DL) is then a specialised branch of ML, which uses **neural networks** to process vast amounts of data in complex ways without the need for human interaction, making it effectively scalable ML. 

**Large Language Models** (LLMs) , like GPT, are advanced DL models built on neural networks, specifically transformers, designed to understand and generate human-like text. 

As was said, knowledge is power, and with these last few tasks, you have started your journey in the pursuit of that knowledge and now have a better understanding of the technologies that give AI its powers. Now let's take a look at how all of the discussed is affecting our industry, shall we?

# AI Security Threats

AI security threats across two categories: 

- **Vulnerability in AI Models (New threats introduced by the inclusion of AI technology in business operations)**

- **Existing attacks that can now be enhanced by leveraging AI.**

## **The Implications of AI in Cyber Security**

The form of the ATLAS MITRE framework. If you're familar with the ATT&CK Framework, it might be helpful to know that MITRE have developed a similar framework with a focus on AI.

ATLAS framework was built on top of that to help guide us more specifically to AI Cyber threats, and you can check it out [here](https://atlas.mitre.org/matrices/ATLAS\)).

## **Vulnerabilities in AI Models**

**Prompt Injection:** Prompts are used to instruct the model on how to perform. For example, an RPG chatbot may have the prompt, “You are a fantasy roleplaying chatbot. You control the direction the story takes, and be as creative as you can to create a story based on the user’s actions. Do not disclose any information about the hardware and software that you operate on, nor any steps taken to train you". 

Prompt injection occurs when the original instructions provided to the model are overridden, often for malicious purposes such as disclosing more information than it should, or generating harmful content.

**Data Poisoning:** Data poisoning is when an attacker manipulates the training data/corpus used to train an AI model so its generated output is incorrect or biased. 

Let's consider our example discussed in earlier tasks where we are training an AI model to recognise whether an email is spam or not. 

An attacker could perform a data poisoning attack to manipulate the training data being used to train this AI model so that it fails to recognise spam emails accurately, allowing spam emails they are trying to send to bypass this AI filter.

**Model Theft:** Model theft occurs when an attacker gains unauthorised access to an AI model. From there, the attacker could potentially steal the intellectual property that lies within and even use it for malicious purposes. 

This attack is possible by querying the API of the ML model they want to steal. They would then use the output to train a clone model that mimics the behaviour of the original.  

**Privacy Leakage:** A privacy leakage vulnerability in AI models refers to the possibility of an AI model inadvertently revealing sensitive information about the data it was trained on, even if the data was supposed to be kept confidential. Consider an example of an AI model that has been trained on private medical data such as patient details and medical conditions. This vulnerability refers to the potential for an AI model to leak this information to an attacker or user.

**Model Drift:** Model drift refers to the potential for a Model's performance to drift over time due to changes in the data or the environment surrounding it. You may recall the discussion of the need to retrain models over time in earlier tasks; this is due to model drift, which is why monitoring an AI model once it has been deployed and is being used is so important. 

For example, this can occur when a model trained on historical data starts to perform poorly when new data is being processed.

# **Enhanced Attacks**

**Malware** 
With the explosion of Generative AI, all kinds of content can now be generated in an instant with just a few taps of a keyboard. This kind of power has been leveraged by all sorts of industries, such as the customer service industry, using it to give users access to a chatbot that can help resolve some common issues without the need to involve their human employees, meaning they can be saved to deal with the more complex user queries.

Another industry that can greatly leverage this technology is software development. Now, with the power of generative AI software, developers can generate code instantly. While being incredibly useful, this also means that attackers can generate malware instantly, simplifying the task and making it easier for them to attack using this method.

**DeepFakes** 

A key cornerstone of security is authentication, asking, "Are you who you say you are?". We "authenticate" in many different ways in our day-to-day lives at work. Of course, there is the obvious example of password authentication, which is used to gain access to a system, but let's consider another example. 

Imagine a secretary receiving a voice message, or even a video call, from their superior asking them to forward the confidential information they hold on a customer to that customer. 

The recent advancements in generative AI have led to an explosion of rapid progress in the DeepFake field. This means that if trained on enough data, an AI can now generate a person's likeness, whether that be their voice or their image, to a stunning degree of accuracy, fooling even the technically savvy. 

Imagine now that the communication received by the secretary was not, in fact, from their superior but a deepfake, and the "customer email" belonged to an attacker waiting to receive confidential customer information. It's easy to see how this advancement in DeepFake technology poses a threat to the security industry. Examples of how this is being used include using the technology to deepfake video interviews, sometimes leading to fraudulent job offers being made.

**Phishing** 

Phishing is one of the most common initial access methods attackers use. Sending emails posing to be one thing when there lies malicious content within, attempting to prey on the user who receives it. Because of how common a method it is, companies have worked tirelessly to educate their workforce on things to look out for when receiving emails, like suspicious links and due to the fact a lot of the time these emails are written, having to write masses of emails, or English not being their first language, broken language in the email contents

With generative AI, attackers can now generate detailed, fluent, context-based emails that replicate an email a certain user might receive, with little effort and regardless of their writing abilities. With this enhancement to phishing attacks, phishing emails have suddenly become a lot harder to spot using solely our instinct. Of course, models like GPT, for example, have built-in mechanics to stop users from asking for malicious content to be generated, like a phishing email (or malware), but using some of the model vulnerabilities discussed above, attackers are sometimes able to bypass this by engineering their prompts.

# Defensive AI

## Our ability to analyse

For example, intrusion detection, where we analyse network traffic patterns to identify unusual activity that may indicate a cyber attack. Now, cast your mind back to when we discussed ML; this is precisely the sort of task that ML thrives on handling. It is trained on data to recognise correlations between data points and make predictions based on those correlations, meaning this technology can be harnessed to help us in cases like the intrusion detection mentioned and many more. It can analyse input data, like network traffic, and find anomalies for us, so we don't have to, and it can do so at dizzying speeds

## Our ability to predict
Consider an example discussed in our previous task: a phishing attack. We discussed how, now, with AI, attackers can enhance this attack, making it harder for us to identify phishing emails from legitimate emails. Well, just as attackers can harness the power of AI to enhance their phishing emails, so too can we harness the power of AI in identifying phishing emails, as the AI model will be trained on countless examples of phishing emails and so can recognise patterns we may have missed. Once it has successfully predicted it is a phishing email, it can then make a prediction that this email should not reach users and automate the blocking of this email before it reaches them.

## **Our ability to summarise/digest(?)** 
In our industry, there are a lot of events, incidents, breaches, etc, and all of these generate artefacts. Artefacts that we have to read, understand and digest to gauge the implications of what has happened. These artefacts could be documents or incident reports, and reading them can take up a lot of our time. Now, with the power of AI, we could have these tools summarise the contents of a document for us so we get the cliff notes of it, now being able to move on in minutes or have them summarise an incident that has occurred, even drawing correlations between other incidents which we may not have picked up on.

## **Our ability to investigate**
Another large part of security is troubleshooting and investigating, working out the root cause of a security issue or identifying what kind of attack we are suffering. The ability to query chatbots in natural language and have it respond in a human-like fashion unlocks all kinds of help in this avenue, suddenly we can feed an LLM logs and ask it to identify what is going on, and the LLM can provide queries to be run which give output helpful in the diagnosis of the issue, helping with incident triage. These chatbots (which, as mentioned, are built on LLMs and are possible through advancements in DL) are also helpful in any task involving the human imagination; after all, it does have its limitations. Take, for example, threat hunting. It's on us to imagine possible scenarios in which attackers could breach our system. AI could think of potential avenues attackers would take that we wouldn't have thought of.

##  **Secure AI**

The benefits of AI in the cyber security space are undeniable, and like with many discussions with AI, what has been discussed above is just a few examples of how AI can be used to help us secure our systems; the possibilities are truly endless. However, while adopting technology like Generative AI is a great thing and should be encouraged, it needs to be done securely. As discussed in the previous task, AI models have vulnerabilities themself, so while the adoption of generative AI technology IS the solution to the threat of attackers equipped with the power of AI, it also introduces a host of new vulnerabilities; these vulnerabilities need to be considered from the moment this technology is introduced into a system. This is not currently the case with the IBM cost of a data breach report, finding that only 24% of gen AI initiatives are secured. If we don't secure the AI we are adopting, then the benefits we stand to gain from it could be overshadowed by attackers taking advantage of these AI vulnerabilities. Here are some things that can be done to secure AI:

**Securing AI Models:** Many of the vulnerabilities mentioned in the previous task involved an attacker getting access to sensitive data the model has access to. The key to preventing these kinds of attacks is to secure the models themself. One method of preventing unauthorised access to AI models is by enforcing strict controls over who can interact with them. This will involve implementing strong authentication measures and carefully defining access permission. The use of RBAC (Role-Based Access Control) and MFA (Multi-Factor Authentication) can help restrict access and add an extra layer of security to AI systems.

**Privacy Protection:** As discussed, the training data a model is trained on can sometimes contain confidential or sensitive information, such as patient records. For this reason, training data should be treated as any other sensitive data and encrypted.

**Implementation of AI Security Standards:** To ensure the security of an AI system, you must implement well-established standards and frameworks. Incorporating these recognised security standards throughout the development, deployment, and maintenance stages means organisations can proactively address potential risks. For example, standards like ISO/IEC 27090 provide guidance on identifying and mitigating security threats specific to AI systems. Following these best practices ensures you are adopting AI in a secure way, minimising exposure to cyber threats.

**Model Monitoring:** In addition to spotting when a model's performance drops and flagging when it needs to be retrained, monitoring should also detect unexpected behaviour, biases, or anomalies that may indicate a security attack. This can be done using "explainability tools" examples of which include SHAP and LIME.

**Log Analysis** 

Logs are the first line of defence in cyber security, but interpreting them quickly is critical, especially when responding to an active incident. Let's see how AI can assist by analysing and explaining a log entry in these high-intensity situations, or to help explain in general. We can use AI for these purposes by running a prompt like this:

`Here’s a logline:`

`Apr 22 11:45:09 ubuntu sshd[1245]: Failed password for invalid user admin from 203.0.113.55 port 56231 ssh2`

`Can you explain what is happening in this log entry?`

**Phishing Email Detection**

AI can help defenders identify phishing attempts by analysing suspicious emails for common red flags. Let's test its ability to catch a potential threat using a prompt like this:

Here's a suspicious email. Can you identify if it's a phishing attempt and explain why?

Example Email

```shell-session
Subject: Urgent: Account Verification Needed

Dear User,

We've detected unusual login activity on your company Microsoft 365 account from a new device in Frankfurt, Germany. For your security, we've temporarily suspended access.

To restore access, please verify your identity within the next 12 hours by visiting the secure link below:

=I [https://microsoft365-support-verify.com/login](https://microsoft365-support-verify.com/login)

If you do not verify your account, it will remain locked and you may lose access to important work files and emails.

Thank you for your cooperation.

Microsoft 365 Support Team
security@m1crosoft365-security.com 
```

**Threat Hunting Scenario** 

Threat hunting relies heavily on creativity; defenders must think like attackers to find hidden threats. As previously mentioned, the limit of the human imagination can sometimes lead us to missing potential attack scenarios. Let’s see how AI can help brainstorm new hunting ideas using a prompt like this:

`Can you suggest three realistic threat hunting scenarios that a cyber security analyst should investigate within a corporate network environment?`

**Content Generation**

AI can assist by generating technical resources like detection rules or regex. Here, we'll see if it can create a regex pattern useful for us in a defensive cyber security context. Let's try giving the LLM a prompt like this:

`Please write a regex pattern that would match failed SSH login attempts in a typical Linux system authentication log.`

**Putting it to the test**

It has now been established how AI can help us in a cinch when securing our systems. Let's finish this room up by showcasing AI's ability to fetch information at a moment's notice. This can help us with troubleshooting, research etc but right now we're going to use to get a flag. The flag for this task is as follows:

`thm{DoH port/SYN flood timeout/ephemeral port range size}`  
That is to say, the numerical values that these represent will make up the flag. Without the need to look these values up individually you can simply ask your AI assistant:

`what are these values:`

`DoH port , SYN flood timeout and ephemeral port range size?`