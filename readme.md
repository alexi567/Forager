#  Forager - Local LLM

Forager este o aplicație web care permite utilizatorului să încarce un document PDF și să pună întrebări despre conținutul acestuia.

Aplicația caută informațiile relevante din document și folosește un model LLM rulat local pentru a genera răspunsuri pe baza textului găsit.

## Tehnologii utilizate

* **Python** – limbajul principal folosit pentru dezvoltarea aplicației.
* **Streamlit** – folosit pentru interfața web, încărcarea PDF-ului și afișarea conversației.
* **Ollama** – permite rularea locală a modelului LLM.
* **Qwen 3 8B** – modelul LLM care generează răspunsurile.
* **FAISS** – caută fragmentele din document care sunt cele mai relevante pentru întrebare.
* **Sentence Transformers** – transformă textul în embeddings, adică reprezentări numerice care permit căutarea semantică.
* **PyMuPDF** – extrage textul din fișierele PDF.

## Cerințe

Pentru a rula aplicația ai nevoie de:

* Windows
* Python 3
* Git
* Ollama
* modelul `qwen3:8b` instalat în Ollama

## 1. Descărcarea proiectului

Deschide un terminal și clonează repository-ul:

```bash
git clone https://github.com/alexi567/Forager.git
```

Apoi intră în folderul proiectului:

```bash
cd Forager
```

Alternativ, proiectul poate fi descărcat de pe GitHub folosind opțiunea **Code → Download ZIP**, apoi arhiva trebuie extrasă.

## 2. Crearea mediului virtual

În folderul proiectului rulează:

```bash
python -m venv .venv
```

Apoi activează mediul virtual:

```bash
.venv\Scripts\activate
```

Dacă mediul virtual a fost activat corect, în terminal ar trebui să apară:

```text
(.venv)
```

## 3. Instalarea bibliotecilor Python

Rulează:

```bash
pip install -r requirements.txt
```

Această comandă va instala automat bibliotecile Python necesare proiectului.

## 4. Instalarea Ollama

Descarcă și instalează Ollama de pe site-ul oficial.

După instalare, verifică dacă Ollama funcționează:

```bash
ollama --version
```

## 5. Instalarea modelului Qwen 3 8B

Aplicația utilizează modelul **Qwen 3 8B**, care trebuie descărcat înainte de prima rulare.

Rulează:

```bash
ollama pull qwen3:8b
```

Poți verifica dacă modelul a fost instalat:

```bash
ollama list
```

În lista afișată ar trebui să apară:

```text
qwen3:8b
```

## 6. Pornirea aplicației

Asigură-te că mediul virtual este activ:

```bash
.venv\Scripts\activate
```

Apoi pornește aplicația:

```bash
streamlit run app.py
```

După pornire, Streamlit va afișa în terminal adresa la care poate fi accesată aplicația, de obicei:

```text
http://localhost:8501
```

Deschide adresa într-un browser.

## 7. Utilizarea aplicației

1. Încarcă un document PDF.
2. Așteaptă procesarea documentului.
3. Scrie o întrebare despre conținutul PDF-ului.
4. Aplicația caută fragmentele relevante din document.
5. Fragmentele găsite sunt trimise către Qwen 3 8B.
6. Modelul generează răspunsul pe baza contextului primit.
7. Sursele folosite pentru răspuns pot fi consultate în interfață.

## 8. Oprirea aplicației

Pentru a opri aplicația, mergi în terminalul în care rulează Streamlit și apasă:

```text
Ctrl + C
```

## Cum funcționează aplicația

Fluxul principal este:

```text
PDF
↓
Extragerea textului
↓
Împărțirea textului în fragmente
↓
Crearea embeddings
↓
Căutarea semantică folosind FAISS
↓
Selectarea fragmentelor relevante
↓
Trimiterea contextului către Qwen 3 8B
↓
Generarea răspunsului
```

Această arhitectură este cunoscută sub numele de **RAG (Retrieval-Augmented Generation)**.

Modelul nu primește întregul PDF la fiecare întrebare. Aplicația identifică mai întâi fragmentele relevante și le oferă modelului Qwen drept context pentru generarea răspunsului.

## Structura proiectului

```text
Forager/
│
├── app.py
├── requirements.txt
├── README.md
└── .venv/
```

* `app.py` – codul principal al aplicației.
* `requirements.txt` – bibliotecile Python necesare.
* `README.md` – documentația proiectului.
* `.venv` – mediul virtual Python local.

## Notă

Prima rulare poate dura mai mult deoarece modelul trebuie încărcat în memorie.

Aplicația și modelul LLM rulează local pe calculatorul utilizatorului prin Ollama.
