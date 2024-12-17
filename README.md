# RechtChecker

# About the Project

This project involves developing a ChatBot designed to assist German citizens in understanding their rights as outlined in the Grundgesetz (Basic Law).

## Technical Overview

![DB Architektur](images/DB_Architektur.png)

The system operates through a multi-agent architecture where a "Manager Agent" coordinates interactions between the user and various specialized agents. Here's how it works:

1. The **user** submits a question to the Manager Agent.
2. The **Manager Agent** first checks whether the question has already been answered by querying the **Redis Agent**.
   - If the Redis Agent finds a cached response, it sends the answer back to the Manager Agent.
   - If the question is not cached, the Manager Agent determines which database to query and delegates the task to the corresponding agent.
3. The database-specific agent retrieves the necessary information, returning it to the Manager Agent, which then responds to the user.

### Agents

**_Manager Agent_**:

- Categorizes questions and assigns them to agents.
- No data storage.

**_Redis Agent_**:

- Provides cached responses.
- In-Memory DB: Stores key-value pairs (questions-responses) in Cache.

**_MinIO Agent_**:

- Retrieves PDFs of articles.
- Object-Oriented DB: Stores PDFs as objects in object storage.

**_MongoDB Agent_**:

- Summarizes and explains articles.
- Document DB: Stores data structured by articles as a JSON file.

**_Neo4J Agent_**:

- Handles article relationships.
- Graph DB: Stores data as nodes and relationships in a graph.

**_Postgres Agent_**:

- Answers general legal questions.
- Vector DB: Stores data chunks (articles) as vector embeddings.

### Workflow

1. Manager Agent → Redis Agent → Manager Agent
2. Manager Agent → MinIO Agent / MongoDB Agent / Neo4J Agent / Postgres Agent → Manager Agent

## Data Sources

The chatbot leverages reliable legal documents as its data foundation:

- **Grundgesetz** (Basic Law of Germany): [PDF](https://www.bundesregierung.de/resource/blob/974430/180722/b6c342e0e2f412d759a0a2a3af052a06/grundgesetz-data.pdf)
- **Bürgerliches Gesetzbuch (BGB)** (German Civil Code): [PDF](https://www.gesetze-im-internet.de/bgb/BGB.pdf)

This architecture ensures efficient, accurate, and structured responses to user queries about legal rights.

### Installation

```
git clone https://github.com/AnnaKohlbecker/RechtChecker.git
```

## Getting Started

1. Make .env and fill missing variables

   ```bash
   cp .env.example .env
   ```

2. Install requirements

   ```
   pip install -r requirements.txt
   ```

## Run

Run `main.py`

## Problems with Docker

Quit Docker Desktop

# Chatbot UI Lite

A simple chatbot starter kit for OpenAI's chat model using Next.js, TypeScript, and Tailwind CSS.

See a [demo](https://twitter.com/mckaywrigley/status/1634549098954248193?s=46&t=AowqkodyK6B4JccSOxSPew).

For an advanced version, see [Chatbot UI](https://github.com/mckaywrigley/chatbot-ui).

![Chatbot UI Lite](./public/screenshot.png)

## Features

Chatbot UI Lite provides a simple, fully-functional chat interface that you can use to start building your own chatbot apps powered by OpenAI.

It has everything you need to hit the ground running.

Modify the chat interface in `components/Chat`.

Tweak the system prompt in `utils/index.ts`.

Tweak the assistant prompt in `pages/index.tsx`.

## Deploy

**Vercel**

Host your own live version of Chatbot UI Lite with Vercel.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fmckaywrigley%2Fchatbot-ui-lite&env=OPENAI_API_KEY&envDescription=OpenAI%20API%20Key%20needed%20for%20chat.&envLink=https%3A%2F%2Fopenai.com%2Fproduct&project-name=chatbot-ui-lite&repository-name=chatbot-ui-lite)

**Replit**

Fork Chatbot UI on Replit [here](https://replit.com/@MckayWrigley/chatbot-ui).

## Running Locally

**1. Clone Repo**

```bash
git clone https://github.com/mckaywrigley/chatbot-ui-lite.git
```

**2. Install Dependencies**

```bash
npm i
```

**3. Provide OpenAI API Key**

Create a .env.local file in the root of the repo with your OpenAI API Key:

```bash
OPENAI_API_KEY=<YOUR_KEY>
```

**4. Run App**

```bash
npm run dev
```

**5. Start Building**

You should be able to start chatting with the bot.

Now, go build the app into whatever kind of chatbot you want!
