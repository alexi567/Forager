from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import requests


# Prag absolut de relevanta.
# Scor mai mic = rezultat mai relevant.
ABSOLUTE_THRESHOLD = 1.55

# Diferenta maxima acceptata fata de cel mai bun rezultat.
RELATIVE_MARGIN = 0.35

# Model pentru embeddings pe CPU
EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# Modelul LLM din Ollama
LLM_MODEL = "qwen3:8b"


class LocalSentenceTransformerEmbeddings(Embeddings):
    def __init__(self):
        print("Incarc modelul de embeddings pe CPU...")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
            device="cpu"
        )

        print("Modelul de embeddings este pregatit.")

    def embed_documents(self, texts):
        embeddings = self.model.encode(
            texts,
            batch_size=16,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def embed_query(self, text):
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return embedding.tolist()


# Pastram modelul incarcat o singura data
_embeddings = None


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = LocalSentenceTransformerEmbeddings()

    return _embeddings


def process_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)

    documents = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):
        page_text = page.extract_text()

        if not page_text:
            continue

        chunks = text_splitter.split_text(
            page_text
        )

        for chunk_number, chunk in enumerate(
            chunks,
            start=1
        ):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "page": page_number,
                        "chunk": chunk_number
                    }
                )
            )

    if not documents:
        raise ValueError(
            "Nu am putut extrage text din acest PDF."
        )

    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        documents,
        embeddings
    )

    return (
        vector_store,
        len(reader.pages),
        len(documents)
    )


def search_relevant_chunks(
    vector_store,
    question,
    k=6
):
    # Cautam primele k rezultate impreuna cu scorurile FAISS
    results_with_scores = (
        vector_store.similarity_search_with_score(
            question,
            k=k
        )
    )

    if not results_with_scores:
        return [], []

    # Primul rezultat este cel mai relevant
    best_score = results_with_scores[0][1]

    # Prag relativ fata de cel mai bun rezultat
    relative_threshold = (
        best_score + RELATIVE_MARGIN
    )

    # Pastram doar rezultatele care indeplinesc
    # AMBELE conditii:
    # 1. sunt sub pragul absolut
    # 2. nu sunt mult mai slabe decat cel mai bun rezultat
    filtered_results = [
        (document, score)
        for document, score in results_with_scores
        if (
            score <= ABSOLUTE_THRESHOLD
            and score <= relative_threshold
        )
    ]

    return (
        results_with_scores,
        filtered_results
    )


def build_context(filtered_results):
    context_parts = []

    for document, score in filtered_results:
        page_number = document.metadata.get(
            "page",
            "?"
        )

        context_parts.append(
            f"[Pagina {page_number}]\n"
            f"{document.page_content}"
        )

    return "\n\n".join(
        context_parts
    )


def get_source_pages(filtered_results):
    pages = {
        document.metadata.get("page")
        for document, score in filtered_results
        if document.metadata.get("page") is not None
    }

    return sorted(pages)


def ask_qwen(question, context):

    # ------------------------------------------------
    # DETECTARE LIMBA INTREBARII
    # ------------------------------------------------

    question_lower = question.lower().strip()

    romanian_words = {
        "care", "este", "sunt", "ce", "cum", "unde",
        "cand", "când", "cat", "cât", "cine", "de ce",
        "despre", "document", "documentul",
        "pot", "poate", "am", "are", "avem",
        "vreau", "exista", "există",
        "spune", "explica", "explică",
        "capitala", "frantei", "franței",
        "roaming", "rezilia", "abonament",
        "pagina", "pagini"
    }

    words = set(
        question_lower
        .replace("?", "")
        .replace("!", "")
        .replace(".", "")
        .replace(",", "")
        .split()
    )

    # Daca gasim cuvinte romanesti sau diacritice,
    # consideram intrebarea in romana.
    has_romanian_word = bool(
        words.intersection(romanian_words)
    )

    has_romanian_diacritics = any(
        char in question_lower
        for char in "ăâîșşțţ"
    )

    is_romanian = (
        has_romanian_word
        or has_romanian_diacritics
    )

    # ------------------------------------------------
    # INSTRUCTIUNEA DE LIMBA
    # ------------------------------------------------

    if is_romanian:

        language_instruction = """
LANGUAGE: ROMANIAN

You MUST write the entire final answer in Romanian.

Even if:
- the PDF is in English,
- the context is in English,
- technical terms are in English,

the explanatory answer MUST be in Romanian.

If the requested information is not present,
return exactly:

Nu pot găsi această informație în document.
"""

    else:

        language_instruction = """
LANGUAGE: ENGLISH

You MUST write the entire final answer in English.

If the requested information is not present,
return exactly:

I cannot find this information in the document.
"""

    # ------------------------------------------------
    # PROMPT
    # ------------------------------------------------

    prompt = f"""
You are a document question-answering assistant.

{language_instruction}

STRICT CONTENT RULES:

1. Use ONLY the information provided in CONTEXT.
2. Do not use general knowledge.
3. Do not invent facts.
4. If the information is only partially available,
   state only what the document supports.
5. If the document does not contain the answer,
   use the exact missing-information sentence
   specified above.
6. Do not mention page numbers in your answer.
7. Return only the final answer.

CONTEXT:

{context}

QUESTION:

{question}

FINAL ANSWER:
"""

    # ------------------------------------------------
    # CERERE CATRE OLLAMA
    # ------------------------------------------------

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        },
        timeout=300
    )

    response.raise_for_status()

    answer = response.json()["response"].strip()

    # ------------------------------------------------
    # PROTECTIE SUPLIMENTARA PENTRU FALLBACK
    # ------------------------------------------------

    english_fallbacks = [
        "I cannot find this information in the document.",
        '"I cannot find this information in the document."',
        "I cannot find this information in the document"
    ]

    romanian_fallback = (
        "Nu pot găsi această informație în document."
    )

    if is_romanian and answer in english_fallbacks:
        answer = romanian_fallback

    return answer