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

   1. node verion v20.18.0

   ```
   node -v
   ```

   2. npm version 9.6.6

   ```
   npm install -g npm@9.6.6
   ```

   2.

   ```
   pip install -r requirements.txt
   ```

## Run

```
npm run dev
```
