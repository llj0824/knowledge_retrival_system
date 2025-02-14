# Engineering Documentation: VitaDAO AI Agent

This document outlines the engineering architecture for VitaDAOs AI Agent. We will start with an AI system (aka knowledge retrival system) that will be the source of truth for VitaDao's tokenimics, Research IP, and ongoing project updates. The information will be grounded by the DAO's internal documents and web search to track latest updates to research projects of VitaDao. 

Then we will integrate with ElizaOS, a agent framework that speicalizes in community engagement by interacting across multiple platforms (twitter, discord, telegram, slack, etc) while maintaining consistent personalities and knowledge. We will do this by introducing a plugin-VitaDAO, so that all agents on ElizaOS will be able to reference VitaDAO for information related to VitaDAO, and more broadly longevity research and DeSci.

---

### **Rationale**

#### Q: Why build VitaDao's own AI system (Knowledge Retrieval System [KRS]) instead of building directly with ElizaOS?

**A:** This addresses a common concern about potential duplicate work. Here's why a separate KRS is essential:

1. **ElizaOS is for community engagement. It relies on downstream information.**
   - ElizaOS excels at community engagement and cross-platform interactions (Twitter, Discord, Telegram, Slack, etc.)
   - ElizaOS relies on data providers to get accurate information
   - Knowledge retrieval and accuracy is not ElizaOS's appeal.
   - We need to ensure accurate, verified responses before they flow into ElizaOS for community engagement

2. **Allows VitaDAO to be data provider for Agent economy on longevity and DeSci**
     - Major AI companies (OpenAI - Operator/Swarm, Meta - Messenger, Anthropic - Computer Use, NVIDIA) will all have their own agents.
     - All agents will need data sources and data providers. It's trending towards unstructure data (Agents talking to Agents). 
     - We want to own and control our data access while making it consumable by others. Granularity of data to token owners & community members vs external public.
     - Use ElizaOS instead of becoming married to their ecosystem. Can integrate with other open-source agent frameworks (LangChain, LlamaIndex, Haystack, G.A.M.E)
   - Our data flow will be: VitaDAO Data → AI System (Knowledge retreival system) → Multiple Platforms (ElizaOS, OpenAI Operator, Virtuals, etc.)



#### Q: What are the key requirements for the KRS System?

**A:** The system needs to handle:

1. **Relevancy and Timeliness**
   - **Data Staleness**
     - When a project has multiple updates (May, July, Dec), we huertistic of priotizinig the latest  updates
     - Secondary: also also keep track of how the project evolved over time
   
   - **Relevant Information not missed**
     - If someone asks about project progression we need to pull the right chunks of info that actually answer the question - current progress vs how it differs from previous update.

2. **Web Search Capabilities**
   - **Priotization of key sites**
     - hueristic for priotizing our partner protocols (Molecule, Bio, Pump Science) and research collaborators (SENS Research Foundation, Fang Lab, Korolchuk Lab, Gorbunova Lab)
   - **Handling Conflicts**
     - Info lives everywhere - Discord, Forums, Research docs
     - Need to know which source to trust when they say different things

---

## 1. Knowledge Retrieval System

This proposal outlines the design and implementation of a knowledge retrieval system chatbot to support VitaDAO's community and token holders. The chatbot will integrate with large language models (LLMs), vector databases containing DAO documents and research data, and an internet search API to provide accurate, real-time responses to user inquiries.

The key functionalities of the chatbot include answering token economics and research-related questions, providing updates on research projects and IP assets, analyzing potential impact of research outcomes, and responding to governance and community participation queries. 

### **1. Objectives**

- **Enhance Token Holder Experience**: Provide fast, accurate, and accessible information about token economics, research impact, and governance to VITA token holders.
- **Support VitaDAO Member Engagement**: Enable broader community members to easily access information about research projects, governance, and participation opportunities.
- **Improve Research Transparency**: Make VitaDAO's research portfolio, IP assets, and project progress readily available in a conversational format.
- **Enable Data-Driven Decisions**: Help token holders understand the relationship between research outcomes and token value.

---

### **2. Scope**

The knowledge retrieval system will cover the following areas:
1. **Token and Research Analytics (RAG)**:
   - Real-time token metrics and blockchain activity
   - Research portfolio status and IP assets
   - Impact analysis of research outcomes
   
2. **Community Information**:
   - Governance processes and current proposals
   - Participation opportunities and community initiatives
   - Token holder rights and responsibilities

3. **External Updates**:
   - Latest research developments and milestones
   - Market conditions and token performance
   - Related longevity research news

### **2.1 Example Questions and Use Cases**

The chatbot will be capable of handling various types of queries from different user groups:

#### Token Holder & Community Questions
- "What is the current VITA token price and market cap?"
- "Show me recent blockchain activity for VITA"
- "How could Project X latest news affect token value?"
- "How can I participate in governance voting?"
- "What are the current voting proposals?"
- "What rights do I have as a token holder?"

#### Researcher Questions
- "What research projects is VitaDAO currently funding?"
- "Which labs/researchers have received funding?"
- "What's the typical funding amount for longevity research projects?"
- "How can I submit a research proposal?"
- "Show me all published papers from VitaDAO-funded research"

#### Longevity Community Questions
- "What are the most promising longevity research areas VitaDAO is funding?"
- "How can I learn more about the science behind VitaDAO's funded projects?"
- "What's VitaDAO's perspective (DeSci) on different longevity approaches?"
- "Can you explain the significance of Project X for aging research?"
- "How can I get involved?"


### **3. System Architecture**

The system will be composed of the following components:

#### 3.1 **Frontend (React Web Application)**
- **User Interface**: A responsive web interface allowing users to interact with the chatbot.
- **Chat Interface**: Users can submit text queries and receive responses in a conversational format.
- **User Authentication**: Secure login for internal users to access company policy content.

#### 3.2 **Backend (FastAPI)**
- **Request Processing**: Handles user queries, deciding the appropriate action based on the type of question.
- **LLM Integration**: Connects to a large language model for processing questions and generating responses.
- **Vector DB Integration**: Uses a vector database to store and retrieve company policy documents, leveraging a retrieval-augmented generation (RAG) approach.
- **Internet Search Integration**: Uses APIs to fetch the latest data on members or external topics from the internet.
- **Chat Log Management**: Logs all user interactions for auditing, training, and feedback purposes.
  
#### 3.3 **Databases**
- **Vector Database (e.g., Pinecone, Faiss, or Weaviate)**: Stores the embeddings of company documents, policies, and other knowledge sources for fast retrieval.
- **SQL Database**: Manages structured data like member information, chatbot logs, and user metadata.

#### 3.4 **Model Integration**
- **Retrieval-Augmented Generation (RAG)**:
  - First, the chatbot will attempt to retrieve relevant information from the vector database based on the user's query.
  - If the query relates to member status, it will query the internet search API.
  - If the query cannot be answered using the above, the chatbot will respond based on the base LLM.

### **4. System Flow & Decision Logic**

The backend will follow the decision logic outlined below for query handling:

**Flow Diagram:**
```plaintext
[User Query] 
     |
[Is Query about Token/Research Data?]
     |----[Yes]----> [Query Vector DB] ----> [Retrieve DAO Documents]
     |                             |
     |                             v
     |                          [Found?]----> [Return Answer]
     |                             |
     |                             v
     |                        [No] --> [LLM Base Answer]
     |
[Is Query about Latest Updates?]
     |----[Yes]----> [Query Internet Search API] --> [Retrieve Latest Data]
     |                      (Research/Market/Token)          |
     |                                                      v
     |                                                  [Return Updates]
     |
[Is Query about Impact Analysis?]
     |----[Yes]----> [Combine Vector DB + LLM] --> [Generate Analysis]
     |
     |
[Generic Query] --> [LLM Base Answer]
```

This flow handles:
1. Token and Research queries using stored DAO documents
2. Real-time updates using internet search
3. Impact analysis using combined data sources
4. General queries using base LLM knowledge


---

### **5. Tech Stack **

- **Frontend**: React
- **Backend**: FastAPI 
- **Vector Database**: Pinecone, Faiss
- **Internet Search API**: Integration with a reliable API (e.g., Perplexity, Tavily, Metaphor Api).
- **LLM**: OpenAI's GPT-4, Claude, Deepseek


## 2. ElizaOS Integration

We will create a Plugin & CharacterFile for VitaDAO in the ElizaOS Repository. This will allow all ElizaOS developers and Agents to access VitaDAO information with one line.

### I. Plugin Architecture

The plugin consists of three core components that work together to provide reliable VitaDAO information across the ElizaOS ecosystem:

1. **Provider**: Gathers information from VitaDAO's Knowledge Retrieval System (KRS)
2. **Evaluator**: Categorizes and validates information quality
3. **Actions**: Defines specific operations agents can perform with VitaDAO data

```typescript
export const vitadaoPlugin: Plugin = {
    name: "vitadao",
    description: "VitaDAO Knowledge Retrieval System integration",
    version: "1.0.0",
    
    providers: [vitadaoProvider],
    evaluators: [vitadaoEvaluator],
    actions: vitadaoActions,

    // Configuration for the plugin
    config: {
        required: ["vitaDaoApiKey", "vitaDaoEndpoint"],
        defaults: {
            krsEndpoint: "https://api.vitadao.com/agent"
        }
    }
};
```

### II. Provider Implementation

The Provider serves as linking for ElizaOS and VitaDAO's data so that all Agents in ElizaOS will have ability to answer following questions.

#### Data 
1. **VitaDAO Research Information**
   - Project updates and milestones
   - Published papers and findings
   - Research collaborations

2. **VitaDAO Governance Data**
   - Active proposals
   - Voting results
   - Community initiatives

   
3. **VitaDAO Token Economics**
   - Real-time market data
   - Historical performance
   - Token utility metrics

```typescript
export const vitadaoProvider: Provider = {
    name: "VITADAO_PROVIDER",
    description: "Provides VitaDAO information through VitaDAO Agent API",

    async get(runtime: AgentRuntime, message: Memory, state?: State) {
        if (!runtime.config.vitaDaoApiKey) {
            throw new Error("VitaDAO API key is not set.");
        }

        try {
            const payload = {
                messages: [
                    {
                        role: "user",
                        content: message.content
                    }
                ]
            };

            const response = await fetch(runtime.config.vitaDaoEndpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${runtime.config.vitaDaoApiKey}`
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            return {
                answer: data.answer,
                confidence: data.confidence,
                sources: data.sources,
                timestamp: Date.now()
            };
        } 
    }
};
```
   
### III. Evaluator Design

The Evaluator ensures information quality and relevance:

#### Evaluation Metrics
1. **Query Classification**
   - Research relevance
   - Token economics relevance
   - Governance relevance
   
2. **Data Quality**
   - Source verification
   - Timestamp validation
   - Confidence scoring

3. **Context Analysis**
   - User intent matching
   - Response appropriateness
   - Information completeness

```typescript
export const vitadaoEvaluator: Evaluator = {
    name: "VITADAO_EVALUATOR",
    description: "Evaluates VitaDAO responses",

    async handler(runtime: AgentRuntime, message: Memory) {
        const response = message.content;
        return {
            quality: {
                hasAnswer: Boolean(response.answer),
                confidence: response.confidence || 0
            },
            trustScore: response.confidence > 0.7 ? 1 : 0
        };
    }
};
```

### IV. Actions Framework

Actions define the specific ways agents can interact with VitaDAO data:

#### Core Actions
1. **Information Retrieval**
```typescript
{
  name: "FETCH_VITADAO_INFO",
  description: "Retrieves verified VitaDAO information",
  categories: ["research", "tokenomics", "governance"],
  trustLevel: "high"
}
```

2. **Update Monitoring**
```typescript
{
  name: "MONITOR_VITADAO_UPDATES",
  description: "Tracks changes in specified VitaDAO metrics",
  categories: ["project_updates", "token_metrics", "governance"],
  trustLevel: "high"
}
```

3. **Analysis Generation**
```typescript
{
  name: "ANALYZE_VITADAO_DATA",
  description: "Generates insights from VitaDAO data",
  categories: ["impact_analysis", "trend_analysis", "comparative_analysis"],
  trustLevel: "medium"
}
```
