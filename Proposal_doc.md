## **Engineering Documentation: VitaDAO AI Agent **

This document outlines the engineering architecture for VitaDAOs AI Agent. We will start with an AI system (aka knowledge retrival system) that will be the source of truth for VitaDao's tokenimics, Research IP, and ongoing project updates. The information will be grounded by the DAO's internal documents and web search to track latest updates to research projects of VitaDao. 

Then we will integrate with ElizaOS, a agent framework that speicalizes in community engagement by interacting across multiple platforms (twitter, discord, telegram, slack, etc) while maintaining consistent personalities and knowledge. We will do this by introducing a plugin-VitaDAO, so that all agents on ElizaOS will be able to reference VitaDAO for information related to VitaDAO, and more broadly longevity research and DeSci.

---

### **Rationale**

#### Q: Why build VitaDao's own AI system (Knowledge Retrieval System [KRS]) instead of building directly with ElizaOS?

**A:** This addresses a common concern about potential duplicate work. Here's why a separate KRS is essential:

1. **ElizaOS is for community engagement. It relies on downstream information. **
   - ElizaOS excels at community engagement and cross-platform interactions (Twitter, Discord, Telegram, Slack, etc.)
   - ElizaOS relies on data providers to get accurate information
   - Knowledge retrieval and accuracy is not ElizaOS's appeal.
   - We need to ensure accurate, verified responses before they flow into ElizaOS for community engagement

2. **Be at forefront of data provider for Agent economy on longevity and DeSci**
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
1. Knowledge Retreival System

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

The chatbot will be capable of handling various types of queries, including:

#### Token and Economic Questions
- "What is the current VITA token price?"
- "Explain VitaDAO's tokenomics model"
- "Show me recent blockchain activity for VITA"
- "What's the current market cap and circulation?"

#### Research and IP Questions
- "Can you explain the latest research proposal on longevity biomarkers?"
- "What's the current progress of Project X in our portfolio?"
- "Summarize the key findings from our latest completed research"
- "What IP assets does VitaDAO currently hold?"

#### Impact Analysis
- "How would successful completion of Project Y affect token value?"
- "What are the potential implications of this research for VitaDAO's portfolio?"
- "Explain the relationship between research outcomes and token utility"

#### General DAO Information
- "How does VitaDAO's governance process work?"
- "What are the current voting proposals?"
- "How can I participate in research discussions?"


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