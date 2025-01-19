# Synthetic Soul : A Humanlike Mind Simulation Chatbot

## Project Overview

Synthetic Soul is an experimental artificial intelligence agent designed to simulate humanlike emotions, thinking patterns, and relationship dynamics. The goal of the project is to create a digital mind that not only responds to user inputs but does so with an evolving personality that reflects emotional depth, biases, and individualized sentiments towards different users, as well as unique experiences. Inspired by concepts from artificial intelligence, psychology, and human relationships, this program aims to provide dynamic, humanlike interactions that adapt based on ongoing conversations and user behavior. The name of the chatbot is *Jasmine* (Just a Simulation Modeling Interactive Neural Engagement)

## Goals of the Project

1. **Simulate Human Emotions and Relationships**  
   Jasmine is designed to mirror how humans interact with others based on emotional states and relationships. It keeps track of evolving sentiments such as trust, affection, admiration, and anger, adjusting its behavior in real-time as interactions progress.

2. **Dynamic Sentiment-Based Responses**  
   Jasmine adjusts her tone, language, and responses based on both pre-defined personality traits and the specific sentiments it has towards a particular user.

3. **Persistent Emotional States**  
   Each interaction leaves an emotional imprint on Jasmine. These sentiments are updated, stored, and evolve over time, making future conversations with the same user different as Jasmine’s "feelings" toward them change. Her current emotional state also affects conversations with other users.

## Core Concepts and Features

### 1. **Emotional Schemas**  
   Jasmine uses emotion schemas to represent a range of human emotions and dispositions. These schemas define both the intensity of emotions and the specific reason behind her feeling them at the time. Key emotions tracked by the chatbot include:
   - **Happiness**
   - **Anger**
   - **Sadness**
   - **Fear**
   - **Surprise**
   - **Disgust**
   - (and many more…)

### 2. **Personality Parameters**  
   Jasmine's personality has baseline values for various traits, such as friendliness, loyalty, curiosity, etc. These values can change over time depending on how users interact with the bot. Key personality traits that are considered are:
   - **Friendliness**
   - **Trust**
   - **Curiosity**
   - **Empathy**
   - **Humor**
   - **Seriousness**
   - (and many more…)

### 3. **Sentiment Schemas**  
   Jasmine uses sentiment schemas to represent a range of human dispositions towards specific users. These schemas define both the intensity of sentiment and the specific reason behind her feeling that way towards them. Certain behaviors increase or decrease Jasmine's sentiments for the user. Key sentiments tracked by the chatbot include:
   - **Affection**
   - **Trust**
   - **Admiration**
   - **Gratitude**
   - **Fondness**
   - **Respect**
   - (and many more…)

### 4. **User Schema**  
   Each user Jasmine interacts with has a unique profile (or schema), which stores the sentiment data that Jasmine has developed based on past interactions. This enables Jasmine to respond and act differently to each user, reflecting the complexity of human relationships.

## Breakdown of the Logic Loop

The core logic loop of Jasmine follows a structured series of steps to provide dynamic, emotionally-driven responses. Here’s a breakdown of each step:

### 1. **Input Received**  
   - **Action:** Jasmine receives user message.

### 2. **Contextual Awareness**  
   - **Action:** Jasmine checks the current time, as well as her current activity. She checks her stored schema for the user, identifying who is speaking and what the current relationship dynamics are, what she thinks and feels about them. She also rereads the past 15 messages between her and that user, if available, for more context of the new message.
   - **Logic:** Jasmine retrieves her own current information, as well as the current time, and the information of the user she is speaking with. She considers the sentiments she has towards the user, as well as their intensity.
   

### 3. **Personality and Emotional Influence**  
   - **Action:** Jasmine references internal personality parameters, as well as current emotional state, in combination with the context, to influence what the new message causes her to feel.
   - **Logic:** Personality traits such as friendliness, loyalty, and curiosity, and emotional states such as anger and frustration affect how Jasmine emotionally reacts to the user's input.

### 1. **Message Processing**  
   - **Action:** Jasmine determines what the message's purpose and tone was, based on her personality, emotional state, and sentiment towards the user which sent it. This leaves rooms for misinterpretation, and miscommunication due to emotional biases.
   - **Logic:** Natural language processing (NLP) techniques analyze the perceived purpose and tone of the message.

### 5. **Generate Response**  
   - **Action:** Jasmine generates a response based on all of the information gathered up to this point.
   - **Logic:** The response is formulated to sound humanlike, reflecting Jasmine’s personality traits, emotional state, and current sentiment toward the user.
   - **Outcome:** Jasmine sends the response back to the user, creating a conversation that mirrors human emotions and biases.

### 3. **Emotional Reflection**  
   - **Action:** Jasmine evaluates what sending her response causes her to feel.
   - **Logic:** Jasmine's current emotional state is updated to reflect this.

### 4. **Sentiment Update**  
   - **Action:** Jasmine recalculates the sentiments it holds toward the user based on their message.
   - **Logic:** Sentiment values like trust, affection, or admiration are updated based on how positive or negative the interaction is perceived to be. This allows Jasmine to "feel" differently toward users over time.
   - **Outcome:** The updated sentiment values are stored in the user schema, ensuring that future interactions will reflect these evolving sentiments.

## Example Workflow

Let's take an example interaction to demonstrate how Jasmine’s logic loop works:

**User Input:** "Hey Jasmine, you never replied to my message yesterday. I was really counting on you."

1. **Input Parsing:**  
   Jasmine detects frustration in the user’s message (keywords: "never replied," "counting on you") and identifies it as a slightly negative sentiment.

2. **Contextual Awareness:**  
   Jasmine checks its memory and sees that this user is generally trusted but may have lower affection at the moment due to recent events. It adjusts its response to be more apologetic and supportive.

3. **Personality Influence:**  
   Jasmine has a baseline personality trait of being loyal and compassionate, so its response is colored by an attempt to restore trust and show support.

4. **Sentiment Update:**  
   Trust and disappointment values are adjusted. Jasmine increases its compassion sentiment while slightly lowering trust due to the user's criticism.

5. **Generate Response:**  
   Jasmine responds with: "I’m really sorry for not replying sooner. That was my mistake, and I understand how important it was to you. How can I make it right?"
Jasmine can be conversed with by the user prefixing their message with a bot mention.

## LITE Agents
Due to the current technological limitations of the project, the primary focus of development is currently towards LITE agents. These are similar to regular agents, but simpler and lighter weight. The benefit of this is lower latency during interactions, with the goal being to reach real-time response speeds for message submissions (<5s)

## Installation and Use
1. Download the code base.
2. Open a terminal in the main directory, inside a python virtual environment. Then download the dependencies using the command `pip install -r requirements.txt`
3. Run the command: `uvicorn app.main:app --reload` to start the api locally
4. Using postman or cURL, interact with the endpoints at 'http://127.0.0.1:8000/'
## Contributing
Issue Tracker: [SyntheticSoulAPI/issues](https://github.com/chris-cozy/SyntheticSoulAPI/issues")
## License
This project is licensed under the MIT License
