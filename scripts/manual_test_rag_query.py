"""Test RAG query end-to-end."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from knowledge.services.rag_service import RAGService

print('=== RAG QUERY TEST ===\n')

# Initialize RAG service
rag = RAGService()

# Test question about metro technical conditions
question = "Jakie sa wymagania dotyczace wentylacji w metrze?"

print(f'Question: {question}\n')
print('Searching for relevant chunks...')

# Process query
answer, sources, processing_time = rag.process_query(question, top_k=3)

print(f'\n--- ANSWER ---')
# Handle encoding issues in Windows console
try:
    print(answer)
except UnicodeEncodeError:
    # Write to file instead
    with open('rag_answer.txt', 'w', encoding='utf-8') as f:
        f.write(answer)
    print('[Answer saved to rag_answer.txt due to encoding issues]')

print(f'\n--- SOURCES ({len(sources)}) ---')
for i, source in enumerate(sources, 1):
    # Handle both similarity (vector-only) and rrf_score (hybrid search)
    score = source.get("similarity") or source.get("rrf_score", 0.0)
    score_type = "Similarity" if "similarity" in source else "RRF Score"
    print(f'\n[{i}] {score_type}: {score:.4f}')
    print(f'Metadata: {source["metadata"].get("document_title", "Unknown")}')
    print(f'Chunk type: {source["metadata"].get("chunk_type", "unknown")}')
    print(f'Text preview: {source["text"][:150]}...')

print(f'\n--- STATS ---')
print(f'Processing time: {processing_time:.2f}s')
print(f'Sources retrieved: {len(sources)}')

print('\n[SUCCESS] RAG query test complete!')
