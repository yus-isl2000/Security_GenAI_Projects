import chromadb

# Initialize Chroma client with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Retrieve the collection
collection = chroma_client.get_collection(name="screenshot_texts")

# Define your query text
query_text = input("Enter your search query here>")

# Perform the query
results = collection.query(query_texts=[query_text], n_results=5)

# Display the results
for doc_id, document in zip(results['ids'][0], results['documents'][0]):
    print(f"Document ID: {doc_id}\nContent: {document}\n")




