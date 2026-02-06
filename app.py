"""Simple Flask web interface for Context-Driven Agent."""

from flask import Flask, render_template, request, jsonify
import sys
sys.path.insert(0, ".")

from src.agents import ContextDrivenAgent
from src.retrievers import ElasticsearchRetriever
from src.config import settings
from dotenv import load_dotenv
import logging

# Setup
load_dotenv()
logging.getLogger("elastic_transport").setLevel(logging.ERROR)

app = Flask(__name__)

# Initialize agent
try:
    retriever = ElasticsearchRetriever(
        host=settings.elasticsearch.host,
        port=settings.elasticsearch.port,
        index_name=settings.elasticsearch.index_name,
        username=settings.elasticsearch.user,
        password=settings.elasticsearch.password,
    )
except Exception:
    # Fallback to in-memory retriever
    class InMemoryRetriever:
        def __init__(self):
            self.documents = {
                "doc1": "Python is a high-level programming language",
                "doc2": "Elasticsearch is a distributed search engine",
                "doc3": "Context-driven agents improve response quality with retrieval"
            }
            self.doc_counter = 3
        
        def search(self, query: str, top_k: int = 5):
            results = []
            query_lower = query.lower()
            for doc_id, content in list(self.documents.items())[:top_k]:
                if query_lower in content.lower() or len(results) < top_k:
                    results.append({
                        "id": doc_id,
                        "content": content,
                        "score": 0.85,
                        "metadata": {}
                    })
            return results[:top_k]
        
        def add_document(self, content: str, metadata=None, doc_id=None):
            doc_id = doc_id or f"doc-{self.doc_counter}"
            self.doc_counter += 1
            self.documents[doc_id] = content
            return doc_id
    
    retriever = InMemoryRetriever()

agent = ContextDrivenAgent(retriever=retriever, use_llm=False)


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask the agent a question."""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    try:
        response = agent.process_query(query, use_context=True)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-document', methods=['POST'])
def add_document():
    """Add a new document."""
    data = request.json
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'error': 'Empty content'}), 400
    
    try:
        doc_id = agent.add_document(content)
        return jsonify({'id': doc_id, 'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    """Search for documents."""
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    try:
        results = agent.search_documents(query, top_k=5)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history."""
    history = agent.get_conversation_history()
    return jsonify({'history': history})


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history."""
    agent.clear_history()
    return jsonify({'status': 'cleared'})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Context-Driven Agent - Web Interface")
    print("="*60)
    print("\n🌐 Opening http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(debug=True, port=5000)
