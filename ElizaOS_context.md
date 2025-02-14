ElizaOS Context

### 1. **AgentRuntime**
The `AgentRuntime` is the core engine that manages the agent's lifecycle and execution environment. It is responsible for processing memory, managing state, and handling actions. It integrates 
different system components like actions, evaluators, providers, and memory systems to ensure that 
the agent functions smoothly.

#### Core Responsibilities:

1. **Message Processing & Memory Management**
```typescript
// Initialize memory managers for different types of data
const messageManager = runtime.getMemoryManager("messages");
const descriptionManager = runtime.getMemoryManager("descriptions");
const loreManager = runtime.getMemoryManager("lore");

// Store a new message in memory
await messageManager.createMemory({
    id: "msg_123",
    content: { 
        text: "Hello, how can I help you today?",
        timestamp: Date.now(),
        metadata: { sentiment: "positive" }
    },
    userId: "user_456",
    roomId: "room_789"
});

// Retrieve recent conversation context
const recentMessages = await messageManager.getMemories({
    roomId: "room_789",
    limit: 10,
    order: "desc"
});
```

2. **State Management**
```typescript
// Compose initial state with context
const state = await runtime.composeState(message, {
    additionalContext: "User is a software developer discussing TypeScript",
    environmentData: {
        timezone: "UTC-8",
        platform: "Discord",
        userPreferences: { language: "en" }
    }
});

// Update state with new message context
const updatedState = await runtime.updateRecentMessageState(state);
```

3. **Action Execution**
```typescript
// Define custom actions
const customActions = [
    {
        name: "generateImage",
        handler: async (prompt: string) => {
            // Image generation logic
        }
    },
    {
        name: "transcribeAudio",
        handler: async (audioFile: Buffer) => {
            // Audio transcription logic
        }
    }
];

// Initialize runtime with actions
const runtime = new AgentRuntime({
    // ... other config ...
    actions: customActions
});

// Process actions
await runtime.processActions(message, responses, state, async (newMessages) => {
    // Handle action results
    return processedMessages;
});
```

4. **Evaluation System**
```typescript
// Define custom evaluators
const customEvaluators = [
    {
        name: "sentimentAnalysis",
        evaluate: async (message: Message) => {
            return { sentiment: "positive", confidence: 0.89 };
        }
    },
    {
        name: "toxicityCheck",
        evaluate: async (message: Message) => {
            return { isToxic: false, score: 0.12 };
        }
    }
];

// Initialize runtime with evaluators
const runtime = new AgentRuntime({
    // ... other config ...
    evaluators: customEvaluators
});

// Evaluate message
const evaluation = await runtime.evaluate(message, state, true);
```

5. **Provider Integration**
```typescript
// Define custom providers
const customProviders = [
    {
        name: "weatherProvider",
        getData: async (location: string) => {
            return { temperature: 72, conditions: "sunny" };
        }
    },
    {
        name: "timeProvider",
        getData: async (timezone: string) => {
            return { currentTime: new Date().toISOString() };
        }
    }
];

// Initialize runtime with providers
const runtime = new AgentRuntime({
    // ... other config ...
    providers: customProviders
});
```

#### Complete Runtime Configuration Example:
```typescript
const runtime = new AgentRuntime({
    token: "auth_token_123",
    modelProvider: ModelProviderName.ANTHROPIC,
    character: {
        name: "TechAssistant",
        personality: "Helpful and knowledgeable tech expert",
        background: "Experienced in software development and system design"
    },
    databaseAdapter: new DatabaseAdapter({
        type: "postgres",
        url: process.env.DATABASE_URL
    }),
    conversationLength: 32,
    serverUrl: "http://localhost:7998",
    actions: customActions,
    evaluators: customEvaluators,
    providers: customProviders,
    memoryConfig: {
        messageRetention: "30d",
        maxMemories: 1000,
        vectorStore: "pinecone"
    }
});
```

The `AgentRuntime` serves as the orchestrator that brings together all these components to create a cohesive, intelligent agent system. It manages the flow of information between components while maintaining state consistency and proper memory management.

### 2. **Adapter**
Adapters serve as the interface layer between the agent and external data sources, handling data persistence, retrieval, and transformation. They abstract away the complexity of different storage backends and provide a consistent API for the agent's operations.

#### Core Responsibilities:

1. **Data Persistence**
- Store and retrieve conversation histories
- Manage agent state and memory
- Handle relationship data between users/agents
- Persist goals and objectives

2. **Data Transformation**
- Convert between application models and storage formats
- Handle serialization/deserialization
- Transform embeddings for vector storage

3. **Query Operations**
- Perform semantic searches using embeddings
- Filter and paginate results
- Execute complex joins across related data

#### Example Implementations:

**Base Adapter Interface:**
```typescript
interface DatabaseAdapter {
  // Memory Operations
  createMemory(memory: Memory): Promise<void>;
  searchMemories(params: SearchParams): Promise<Memory[]>;
  
  // Relationship Management
  createRelationship(params: RelationshipParams): Promise<void>;
  getRelationships(userId: string): Promise<Relationship[]>;
  
  // Goal Tracking
  createGoal(goal: Goal): Promise<void>;
  updateGoalStatus(goalId: string, status: GoalStatus): Promise<void>;
}
```

**PostgreSQL Implementation:**
```typescript
class PostgresDatabaseAdapter implements DatabaseAdapter {
  private pool: Pool;

  constructor(connectionString: string) {
    this.pool = new Pool({ connectionString });
  }

  async createMemory(memory: Memory): Promise<void> {
    const { id, content, embedding, userId, roomId } = memory;
    await this.pool.query(`
      INSERT INTO memories (id, content, embedding, user_id, room_id)
      VALUES ($1, $2, $3, $4, $5)
    `, [id, JSON.stringify(content), embedding, userId, roomId]);
  }

  async searchMemories(params: SearchParams): Promise<Memory[]> {
    const { embedding, threshold, limit } = params;
    const result = await this.pool.query(`
      SELECT *, (1 - (embedding <=> $1)) as similarity
      FROM memories
      WHERE similarity > $2
      ORDER BY similarity DESC
      LIMIT $3
    `, [embedding, threshold, limit]);
    return result.rows;
  }
}
```

**SQLite Implementation:**
```typescript
class SQLiteAdapter implements DatabaseAdapter {
  private db: Database;

  constructor(dbPath: string) {
    this.db = new Database(dbPath);
  }

  async createMemory(memory: Memory): Promise<void> {
    this.db.prepare(`
      INSERT INTO memories (id, content, embedding, user_id, room_id)
      VALUES (?, ?, ?, ?, ?)
    `).run(memory.id, JSON.stringify(memory.content), 
          memory.embedding, memory.userId, memory.roomId);
  }

  async searchMemories(params: SearchParams): Promise<Memory[]> {
    return this.db.prepare(`
      SELECT *, vector_similarity(embedding, ?) as similarity
      FROM memories
      WHERE similarity > ?
      ORDER BY similarity DESC
      LIMIT ?
    `).all(params.embedding, params.threshold, params.limit);
  }
}
```

#### Usage Example:

```typescript
// Initialize adapter
const adapter = new PostgresDatabaseAdapter(process.env.DATABASE_URL);

// Store a memory
await adapter.createMemory({
  id: "mem_123",
  content: { text: "Hello world" },
  embedding: new Float32Array(1536),
  userId: "user_1",
  roomId: "room_1"
});

// Search similar memories
const memories = await adapter.searchMemories({
  embedding: queryEmbedding,
  threshold: 0.8,
  limit: 10
});
```

This architecture allows for:
- Easy swapping of storage backends
- Consistent data access patterns
- Separation of concerns between storage and business logic
- Simplified testing through mock adapters

### 3. **Actions**
Actions represent the tasks or operations that an agent can perform. They define what the agent can do, from interacting with smart contracts to generating NFTs or processing files.

#### Core Components
Each action consists of:
- `name`: Unique identifier for the action
- `similes`: Alternative names that trigger the same action
- `description`: Detailed explanation of the action's purpose
- `validate`: Function to check if the action is appropriate
- `handler`: Implementation of the action's behavior
- `examples`: Sample usage patterns

#### Example Actions

1. **Token Swap Action**
```typescript
const executeSwap: Action = {
  name: "EXECUTE_SWAP",
  similes: ["SWAP_TOKENS", "TOKEN_SWAP", "TRADE_TOKENS"],
  description: "Executes a token swap after validating trust score and parameters",
  validate: async (runtime: IAgentRuntime, message: Memory) => {
    const hasValidTokens = await runtime.validateTokenPair(message.params.tokenA, message.params.tokenB);
    return hasValidTokens;
  },
  handler: async (runtime: IAgentRuntime, message: Memory) => {
    // Validate trust score
    const trustScore = await runtime.getProvider('trustScore').evaluateSwap(message.params);
    if (trustScore < runtime.getMinimumTrustThreshold()) {
      return false;
    }
    
    // Execute the swap
    const result = await runtime.getProvider('dex').executeSwap({
      tokenA: message.params.tokenA,
      tokenB: message.params.tokenB,
      amount: message.params.amount,
      slippage: message.params.slippage || 0.5
    });
    
    return result.success;
  }
};
```

2. **Document Processing Action**
```typescript
const processDocument: Action = {
  name: "PROCESS_DOCUMENT",
  similes: ["ANALYZE_DOCUMENT", "READ_DOCUMENT", "PARSE_DOCUMENT"],
  description: "Processes and analyzes uploaded documents for relevant information",
  validate: async (runtime: IAgentRuntime, message: Memory) => {
    const validTypes = ['pdf', 'txt', 'doc'];
    return message.attachments?.some(a => validTypes.includes(a.type));
  },
  handler: async (runtime: IAgentRuntime, message: Memory) => {
    const docService = runtime.getProvider('document');
    
    // Extract text
    const text = await docService.extractText(message.attachments[0]);
    
    // Analyze content
    const analysis = await runtime.getProvider('ai').analyze(text);
    
    // Store results
    await runtime.memory.store({
      type: 'document_analysis',
      content: analysis,
      reference: message.attachments[0].id
    });
    
    return true;
  }
};
```

#### Key Responsibilities

1. **Input Validation**
   - Verify required parameters
   - Check for appropriate permissions
   - Validate data formats and types

2. **Resource Management**
   - Handle external service connections
   - Manage memory and storage
   - Clean up resources after execution

3. **State Management**
   - Track action progress
   - Maintain consistency
   - Handle concurrent operations

4. **Security**
   - Validate trust scores
   - Check authorization
   - Protect sensitive data

These actions form the foundation of agent capabilities, enabling complex interactions while maintaining security and reliability.

### 4. **Provider**
Providers are essential components that deliver dynamic data to the agent from external sources. They act as bridges between the agent and various external systems, ensuring decisions are made with up-to-date information.

#### Core Responsibilities:
1. **Data Fetching & Integration**
   - Retrieve real-time data from external APIs
   - Format data for agent consumption
   - Handle caching and data freshness
   
2. **Context Management**
   - Maintain conversation context
   - Track user interactions
   - Provide temporal awareness

3. **Error Handling & Reliability**
   - Implement retry mechanisms
   - Provide fallback data
   - Handle API timeouts gracefully

#### Examples:

**1. Market Data Provider:**
```typescript
class MarketDataProvider {
  private cache: Map<string, { data: any, timestamp: number }> = new Map();
  private CACHE_TTL = 60000; // 1 minute

  async fetchTokenPrice(runtime: IAgentRuntime, symbol: string) {
    // Check cache first
    const cached = this.cache.get(symbol);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.data;
    }

    try {
      const price = await runtime.api.getPriceData(symbol);
      this.cache.set(symbol, { data: price, timestamp: Date.now() });
      return price;
    } catch (error) {
      console.error(`Failed to fetch price for ${symbol}:`, error);
      return cached?.data || null; // Fallback to cached data if available
    }
  }
}
```

**2. Weather Provider:**
```typescript
class WeatherProvider {
  async getWeatherContext(runtime: IAgentRuntime, location: string) {
    try {
      const weather = await runtime.api.getWeatherData(location);
      return {
        temperature: weather.temp,
        conditions: weather.conditions,
        forecast: weather.forecast.slice(0, 3), // Next 3 days
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      return {
        error: "Weather data temporarily unavailable",
        lastUpdated: new Date().toISOString()
      };
    }
  }
}
```

**3. Enhanced Wallet Provider:**
```typescript
class WalletProvider {
  private readonly REFRESH_INTERVAL = 300000; // 5 minutes
  private lastUpdate: number = 0;
  private cachedPortfolio: any = null;

  async fetchPortfolioValue(runtime: IAgentRuntime) {
    const now = Date.now();
    
    // Return cached data if within refresh interval
    if (this.cachedPortfolio && (now - this.lastUpdate) < this.REFRESH_INTERVAL) {
      return this.cachedPortfolio;
    }

    try {
      const portfolio = await this.getPortfolio(runtime);
      
      // Calculate additional metrics
      const portfolioWithMetrics = {
        totalUsd: portfolio.totalUsd,
        totalSol: portfolio.totalSol,
        items: portfolio.items,
        metrics: {
          dailyChange: this.calculateDailyChange(portfolio),
          topHoldings: this.getTopHoldings(portfolio.items, 3),
          riskScore: this.calculateRiskScore(portfolio.items)
        },
        lastUpdated: now
      };

      this.cachedPortfolio = portfolioWithMetrics;
      this.lastUpdate = now;
      
      return portfolioWithMetrics;
    } catch (error) {
      console.error('Portfolio fetch failed:', error);
      return this.cachedPortfolio || {
        error: 'Unable to fetch portfolio data',
        lastUpdated: now
      };
    }
  }

  private calculateDailyChange(portfolio: any) {
    // Implementation for daily change calculation
    return 0;
  }

  private getTopHoldings(items: any[], count: number) {
    return items
      .sort((a, b) => b.valueUsd - a.valueUsd)
      .slice(0, count);
  }

  private calculateRiskScore(items: any[]) {
    // Implementation for risk score calculation
    return 0;
  }
}
```

**4. User Activity Provider:**
```typescript
class UserActivityProvider {
  async getUserContext(runtime: IAgentRuntime, userId: string) {
    const [
      recentMessages,
      transactions,
      preferences
    ] = await Promise.all([
      this.getRecentMessages(runtime, userId),
      this.getRecentTransactions(runtime, userId),
      this.getUserPreferences(runtime, userId)
    ]);

    return {
      messageCount: recentMessages.length,
      lastActive: recentMessages[0]?.timestamp,
      tradingActivity: {
        volume24h: transactions.reduce((sum, tx) => sum + tx.amount, 0),
        favoriteTokens: this.extractFavoriteTokens(transactions)
      },
      preferences: preferences,
      lastUpdated: new Date().toISOString()
    };
  }
}
```

#### Best Practices:

1. **Implement Caching**
   - Use appropriate TTL for different data types
   - Implement cache invalidation strategies
   - Provide fallback mechanisms

2. **Handle Rate Limits**
   - Implement backoff strategies
   - Queue requests when necessary
   - Monitor API usage

3. **Error Recovery**
   - Graceful degradation
   - Meaningful error messages
   - Fallback data sources

4. **Data Validation**
   - Validate input parameters
   - Sanitize external data
   - Type checking and validation

These providers enable agents to make informed decisions based on real-time data while maintaining reliability and performance.

### 5. **Evaluators**
Evaluators are sophisticated components that assess, analyze, and extract information from conversations and actions. They play a crucial role in maintaining the agent's intelligence and contextual awareness.

#### Core Responsibilities:

1. **Fact Extraction and Validation**
```typescript
class FactEvaluator implements Evaluator {
  name = "FACT_EVALUATOR";
  description = "Extracts and validates factual information";
  
  async handler(runtime: IAgentRuntime, message: Memory) {
    const facts = await this.extractFacts(message.content);
    return facts.map(fact => ({
      claim: fact,
      type: this.classifyFactType(fact),
      confidence: this.calculateConfidence(fact),
      timestamp: Date.now()
    }));
  }
}
```

2. **Goal Tracking and Progress Assessment**
```typescript
class GoalEvaluator implements Evaluator {
  async handler(runtime: IAgentRuntime, message: Memory) {
    const goals = await runtime.getGoals();
    return goals.map(goal => ({
      id: goal.id,
      status: this.evaluateProgress(goal, message),
      completedObjectives: this.checkObjectives(goal),
      nextSteps: this.determineNextSteps(goal)
    }));
  }
}
```

3. **Trust and Safety Evaluation**
```typescript
class TrustScoreEvaluator implements Evaluator {
  async evaluateInteraction(params: InteractionParams) {
    const score = {
      userTrust: this.calculateUserTrustScore(params.userHistory),
      contentSafety: this.assessContentSafety(params.content),
      riskLevel: this.determineRiskLevel(params)
    };
    
    return {
      ...score,
      isApproved: score.userTrust > 0.7 && score.contentSafety > 0.8
    };
  }
}
```

4. **Contextual Memory Building**
```typescript
class MemoryEvaluator implements Evaluator {
  async handler(runtime: IAgentRuntime, message: Memory) {
    const context = await this.analyzeContext(message);
    
    return {
      shortTermMemory: this.extractRecentContext(context),
      longTermMemory: await this.buildLongTermMemory(context),
      relevance: this.calculateRelevanceScore(context)
    };
  }
}
```

5. **Sentiment and Emotion Analysis**
```typescript
class EmotionEvaluator implements Evaluator {
  async analyze(message: Memory) {
    return {
      sentiment: this.detectSentiment(message.content),
      emotions: this.identifyEmotions(message.content),
      intensity: this.measureEmotionalIntensity(message.content),
      suggestions: this.generateResponseSuggestions()
    };
  }
}
```

#### Integration Example:
```typescript
class AgentEvaluationSystem {
  private evaluators: Evaluator[] = [];

  async evaluate(message: Memory) {
    const results = await Promise.all(
      this.evaluators.map(async evaluator => {
        try {
          const isValid = await evaluator.validate(runtime, message);
          if (!isValid) return null;
          
          return {
            type: evaluator.name,
            result: await evaluator.handler(runtime, message)
          };
        } catch (error) {
          console.error(`Evaluator ${evaluator.name} failed:`, error);
          return null;
        }
      })
    );

    return results.filter(Boolean);
  }
}
```

#### Best Practices:
Each evaluator should focus on a specific aspect of evaluation while maintaining the ability to work together in the agent's evaluation pipeline. The results from these evaluators help the agent make informed decisions, maintain context, and provide appropriate responses.

### 6. **Character File**
Character files are the DNA of your AI agents, defining their entire personality, knowledge base, and interaction patterns. These JSON-structured configurations control how agents think, respond, and behave across different platforms.

#### Core Components

**1. Basic Identity**
```json
{
  "name": "TechSage",
  "modelProvider": "anthropic",
  "clients": ["discord", "telegram", "direct"],
  "bio": [
    "Leading AI researcher with 15 years in Silicon Valley",
    "Known for bridging complex tech concepts with practical applications",
    "Creator of the 'Tech Simplified' methodology"
  ]
}
```

**2. Personality & Knowledge Base**
```json
{
  "lore": [
    "Developed breakthrough algorithms during the AI winter",
    "Mentored 100+ tech startups to successful launches",
    "Known for saying 'Technology should serve humanity, not replace it'"
  ],
  "knowledge": [
    "Deep expertise in neural network architectures",
    "Comprehensive understanding of blockchain protocols",
    "Specialized in AI ethics and safety frameworks"
  ],
  "adjectives": [
    "analytical",
    "patient",
    "insightful",
    "pragmatic"
  ]
}
```

**3. Interaction Patterns**
```json
{
  "messageExamples": [
    {
      "user": "How do neural networks work?",
      "response": "Think of neural networks like a digital brain. Just as our neurons connect and communicate, artificial neurons process information in layers. Let me break it down with a simple example..."
    }
  ],
  "style": {
    "all": [
      "Use analogies to explain complex concepts",
      "Always provide practical examples",
      "Maintain a professional yet approachable tone"
    ],
    "chat": [
      "Ask clarifying questions when needed",
      "Break down complex explanations into steps"
    ],
    "post": [
      "Keep updates concise and insight-focused",
      "Include one actionable takeaway per post"
    ]
  }
}
```

**4. Technical Configuration**
```json
{
  "settings": {
    "model": "claude-3-opus-20240229",
    "voice": {
      "model": "en-US-neural",
      "url": "https://api.voice.provider/v1"
    },
    "embeddingModel": "text-embedding-3-large"
  }
}
```

#### Key Responsibilities

1. **Personality Consistency**
   - Maintains consistent character voice across all interactions
   - Ensures responses align with defined expertise and background
   - Preserves character-specific quirks and speaking patterns

2. **Knowledge Management**
   - Provides framework for organizing domain expertise
   - Supports fact-checking against defined knowledge base


#### Best Practices

1. **Bio and Lore Development**
   - Break background into modular, reusable pieces
   - Include both factual and personality-defining elements

2. **Style Guidelines**
   - Define clear communication boundaries
   - Include platform-specific behavior rules
   - Specify both permitted and prohibited actions

3. **Knowledge Structure**
   - Organize information in digestible chunks
   - Prioritize relevant domain expertise
   - Regular updates to maintain accuracy

### 7. **Plugins**
Plugins extend the functionality of Eliza agents by providing specialized tools. For example, an image generation plugin could allow the agent to create visuals based on text prompts, or a Solana plugin could enable the agent to interact with the Solana blockchain.

**Example:**
```typescript
export const imageGenerationPlugin: Plugin = {
  name: "imageGeneration",
  description: "Generate images",
  actions: [imageGeneration],
  evaluators: [],
  providers: []
};
```
This plugin adds image generation capabilities to the agent.

### How Everything Comes Together:
Eliza agents use these components together to create a sophisticated autonomous system. Here's how they work in a concrete scenario:

1. **Initialization & Configuration**
   - Agent is initialized with a character file defining personality, knowledge base, and interaction patterns
   - AgentRuntime is configured with necessary providers, evaluators, and actions
   - Database adapters are set up for persistent storage and memory management

2. **Runtime Operations**
   - The AgentRuntime orchestrates all components and manages the agent's lifecycle
   - Memory systems track conversations, descriptions, and contextual lore
   - State management ensures consistency across interactions
   - Database adapters handle data persistence and retrieval

3. **Action Execution**
   - Agent identifies and validates appropriate actions based on context
   - Actions are executed through specialized handlers
   - Trust scores and parameters are validated before execution
   - Results are stored and tracked for future reference

4. **Provider Integration**
   - Real-time data is fetched from relevant providers (market data, weather, user activity)
   - Providers implement caching and rate limiting for optimal performance
   - Multiple providers can work together to build comprehensive context
   - Fallback mechanisms ensure reliability

5. **Evaluation & Analysis**
   - Evaluators assess interactions for fact validation, goal progress, and trust scores
   - Sentiment and emotion analysis guide response patterns
   - Context is continuously built and refined through memory evaluation
   - Results influence future decision-making

6. **Plugin**
   - Specialized plugins extend core functionality
   - Custom actions, evaluators, and providers can be added through plugins
   - Plugins maintain modularity while adding capabilities