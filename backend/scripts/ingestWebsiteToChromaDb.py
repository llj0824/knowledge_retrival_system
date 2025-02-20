import requests
from bs4 import BeautifulSoup
from chromadb import HttpClient, Settings
from sentence_transformers import SentenceTransformer
from urllib.parse import urlparse

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks with overlap"""
    return [text[i:i+chunk_size] 
            for i in range(0, len(text), chunk_size - overlap)]

def scrape_single_page(url):
    """Scrape content from a single URL without following links"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract main content
        title = soup.find("h1").text.strip() if soup.find("h1") else ""
        content_div = soup.find("div", class_="entry-content") or soup.find("main") or soup
        content = content_div.text.strip()
        
        return chunk_text(f"{title}\n{content}")
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def get_website_root(url):
    """Extract root domain to prevent crawling outside the entered site"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def main():
    # User interaction
    target_url = input("Enter website URL to process (e.g., https://vitadao.com/blog/): ").strip()
    if not target_url.startswith(('http://', 'https://')):
        target_url = f"https://{target_url}"
    
    print(f"\n🔍 Scraping content from: {target_url}")
    documents = scrape_single_page(target_url)
    
    if not documents:
        print("No content found. Exiting.")
        return
    
    # Generate embeddings
    print("🧠 Generating embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(documents)
    
    # Store in ChromaDB
    print("💾 Saving to ChromaDB...")
    client = HttpClient(settings=Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_db"
    ))
    collection = client.get_or_create_collection("vitadao_content")
    
    collection.add(
        ids=[str(i) for i in range(len(documents))],
        documents=documents,
        embeddings=embeddings.tolist()
    )
    
    print(f"✅ Successfully stored {len(documents)} chunks from {target_url}")
    
    # Simple query interface
    while True:
        query = input("\n🔎 Enter a search query (or 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            break
            
        query_embedding = model.encode([query]).tolist()[0]
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        print("\nTop results:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"{i+1}. {doc[:150]}...")

if __name__ == "__main__":
    main()