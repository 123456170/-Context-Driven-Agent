# Context-Driven Agents with Elasticsearch

A fast and scalable framework for building context-driven AI agents using Elasticsearch. This project enables you to create intelligent agents that retrieve relevant context from Elasticsearch to provide accurate, context-aware responses.

## Features

- **No API Key Required**: Works out of the box with context-only responses
- **Optional LLM Integration**: Add OpenAI integration when needed
- **Fast Context Retrieval**: Leverage Elasticsearch for efficient document search and retrieval
- **Easy Setup**: Simple configuration and deployment
- **Extensible Architecture**: Modular design for easy customization
- **Multi-turn Conversations**: Support for context-aware dialogue
- **Document Management**: Add, search, and manage documents easily

## Architecture

```
┌─────────────────────┐
│   User Query        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  Context-Driven Agent       │
│  (LangChain)                │
└──────────┬──────────────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌──────────────────┐    ┌────────────────┐
│ Elasticsearch    │    │  OpenAI LLM    │
│ (Context Store)  │    │  (Generation)  │
└──────────────────┘    └────────────────┘
           │                      │
           └──────────┬───────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ Final Response   │
            └──────────────────┘
```

## Prerequisites

- Python 3.8+
- Elasticsearch 8.0+ (optional for LLM - only for context-only mode)

## Installation

### 1. Clone and Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your settings (only ELASTICSEARCH settings are required, OpenAI is optional):

```env
# Required
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX_NAME=documents

# Optional - only if you want to use LLM-based responses
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7

# Optional - Elasticsearch Authentication
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
```

### 4. Start Elasticsearch

Using Docker (recommended):

```bash
docker run -d \
  -p 9200:9200 \
  -e discovery.type=single-node \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

Or use your existing Elasticsearch installation.

## Usage

### Basic Usage (No API Key Required)

```python
from src.retrievers import ElasticsearchRetriever
from src.agents import ContextDrivenAgent
from dotenv import load_dotenv

load_dotenv()

# Initialize retriever
retriever = ElasticsearchRetriever(
    host="localhost",
    port=9200,
    index_name="documents"
)

# Add documents
retriever.add_document("Your document content here", metadata={"source": "example"})

# Initialize agent (context-only mode - no API key needed!)
agent = ContextDrivenAgent(retriever=retriever, use_llm=False)

# Process queries with Elasticsearch context
response = agent.process_query("Your question here", use_context=True)
print(response)
```

### Advanced Usage (With OpenAI LLM)

```python
# Initialize agent with LLM (requires OPENAI_API_KEY in .env)
agent = ContextDrivenAgent(retriever=retriever, use_llm=True)

# Get LLM-enhanced responses
response = agent.process_query("Your question here", use_context=True)
print(response)
```

### Examples

Run the provided examples:

```bash
# Example 1: Basic setup and queries
python examples/example_basic.py

# Example 2: Document indexing and search
python examples/example_search.py

# Example 3: Multi-turn conversations
python examples/example_conversation.py
```

## Project Structure

```
.
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── context_driven_agent.py      # Main agent implementation
│   ├── retrievers/
│   │   ├── __init__.py
│   │   └── elasticsearch_retriever.py   # Elasticsearch integration
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                  # Configuration and settings
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py                   # Utility functions
│   └── __init__.py
├── examples/
│   ├── example_basic.py                 # Basic usage example
│   ├── example_search.py                # Search operations
│   └── example_conversation.py          # Multi-turn conversations
├── data/
│   └── (place your data files here)
├── .env.example                         # Example environment variables
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## API Reference

### ElasticsearchRetriever

#### `add_document(content, metadata=None, doc_id=None)`
Add a document to the Elasticsearch index.

**Parameters:**
- `content` (str): Document content
- `metadata` (dict, optional): Document metadata
- `doc_id` (str, optional): Custom document ID

**Returns:** Document ID

#### `search(query, top_k=5, filters=None)`
Search for documents in Elasticsearch.

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of results to return
- `filters` (dict, optional): Additional filters

**Returns:** List of search results with scores

#### `delete_document(doc_id)`
Delete a document from the index.

#### `clear_index()`
Clear all documents from the index.

### ContextDrivenAgent

#### `process_query(query, use_context=True)`
Process a user query with optional context from Elasticsearch.

**Parameters:**
- `query` (str): User query
- `use_context` (bool): Whether to include Elasticsearch context

**Returns:** Agent response

#### `get_conversation_history()`
Get the conversation history.

**Returns:** List of conversation turns

#### `clear_history()`
Clear the conversation history.

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `ELASTICSEARCH_HOST`: Elasticsearch server host (default: localhost)
- `ELASTICSEARCH_PORT`: Elasticsearch server port (default: 9200)
- `ELASTICSEARCH_INDEX_NAME`: Index name for documents (default: documents)
- `ELASTICSEARCH_USER`: Elasticsearch username (optional)
- `ELASTICSEARCH_PASSWORD`: Elasticsearch password (optional)
- `LLM_MODEL`: LLM model name (default: gpt-3.5-turbo)
- `TEMPERATURE`: LLM temperature (default: 0.7)

## Advanced Usage

### Custom Index Mappings

```python
# The retriever automatically creates an index with default mappings
# To use custom mappings, extend ElasticsearchRetriever:

class CustomRetriever(ElasticsearchRetriever):
    def _ensure_index_exists(self):
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "content": {"type": "text"},
                            "title": {"type": "keyword"},
                            # Add your custom mappings here
                        }
                    }
                }
            )
```

### Batch Processing

```python
from src.utils import batch_documents

documents = ["doc1", "doc2", "doc3", ...]
batches = batch_documents(documents, batch_size=100)

for batch in batches:
    for doc in batch:
        retriever.add_document(doc)
```

## Troubleshooting

### Elasticsearch Connection Error
- Ensure Elasticsearch is running on the configured host and port
- Check ELASTICSEARCH_HOST and ELASTICSEARCH_PORT in .env

### ModuleNotFoundError
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Make sure you're in the correct Python environment

### OpenAI API Error (when using LLM)
- Verify your OPENAI_API_KEY is correct
- Ensure you have sufficient API quota
- Note: The agent works fine without OpenAI - it will use context-only mode

### No Results from Search
- Verify documents are properly indexed
- Check if search query terms match document content
- Review Elasticsearch logs for indexing errors

## Best Practices

1. **Index Management**
   - Regularly backup your Elasticsearch indices
   - Use appropriate refresh intervals for your use case
   - Monitor index size and performance

2. **Context Quality**
   - Ensure indexed documents are relevant and high-quality
   - Use meaningful metadata for filtering
   - Keep context windows appropriate for your use case

3. **LLM Usage**
   - Monitor API costs and rate limits
   - Use temperature appropriately (lower for factual, higher for creative)
   - Implement retry logic for API calls

4. **Security**
   - Never commit .env files with real API keys
   - Use environment variables for sensitive data
   - Enable Elasticsearch authentication in production

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

MIT License

## Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Elasticsearch](https://www.elastic.co/)
- LLM services by [OpenAI](https://openai.com/)
