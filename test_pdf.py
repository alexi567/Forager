from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
import requests

pdf_path = "Space.pdf"

# 1. Citire PDF
reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text + "\n"

print(f"PDF-ul are {len(reader.pages)} pagini.")
print(f"Text total extras: {len(text)} caractere.")

# 2. Impartire in chunk-uri
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_text(text)

print(f"Numar total de chunk-uri: {len(chunks)}")

# 3. Embeddings cu Ollama
embeddings = OllamaEmbeddings(
    model="nomic-embed-text-v2-moe"
)

print("Generez embeddings...")

# 4. Construire index FAISS
vector_store = FAISS.from_texts(
    chunks,
    embeddings
)

print("Indexul FAISS a fost creat.")
print("\nPoti incepe sa pui intrebari despre PDF.")
print("Scrie 'exit' pentru a inchide aplicatia.")

# 5. Bucla de intrebari
while True:
    query = input("\nIntrebarea ta: ")

    if query.lower().strip() in ["exit", "quit", "q"]:
        print("Aplicatia s-a inchis.")
        break

    # 6. Cautare in PDF
    results = vector_store.similarity_search(
        query,
        k=3
    )

    # 7. Construire context
    context = "\n\n".join(
        result.page_content for result in results
    )

    # Optional: afisam contextul gasit
    print("\n--- CONTEXT GASIT IN PDF ---\n")
    print(context)

    # 8. Prompt pentru Qwen
    prompt = f"""
You are an assistant that answers questions about a PDF document.

IMPORTANT RULES:

1. Use ONLY the information contained in the CONTEXT below.
2. Do NOT use outside knowledge.
3. Do NOT invent information.
4. If the answer cannot be found in the context, respond exactly:
"I cannot find this information in the document."
5. Answer clearly and concisely.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    print("\nGenerez raspunsul cu Qwen...\n")

    # 9. Trimitere catre Ollama
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:8b",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        response.raise_for_status()

        # 10. Preluare raspuns
        answer = response.json()["response"]

        print("\n--- RASPUNS QWEN ---\n")
        print(answer)

    except requests.exceptions.RequestException as error:
        print("\nEroare la comunicarea cu Ollama:")
        print(error)