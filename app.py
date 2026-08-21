import streamlit as st
import requests
import Backend
from Backend import (
    process_pdf,
    search_relevant_chunks,
    build_context,
    get_source_pages,
    ask_qwen,
)


# ============================================================
# CONFIGURARE PAGINĂ
# ============================================================

st.set_page_config(
    page_title="Forager",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False

if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "page_count" not in st.session_state:
    st.session_state.page_count = 0

if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   GENERAL
========================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #111512 !important;
    background-color: #111512 !important;
    background-image: none !important;
}

.stApp {
    color: #E7ECE8;
}

.block-container {
    max-width: 880px;
    padding-top: 1.6rem;
    padding-bottom: 8rem;
}

html,
body,
[class*="css"] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}


/* ==========================================================
   HEADER
========================================================== */

.forager-header {
    margin-bottom: 24px;
}

.forager-title {
    font-size: 2rem;
    font-weight: 650;
    color: #DDE9DF;
    letter-spacing: -0.04em;
    margin: 0;
    line-height: 1.1;
}

.forager-subtitle {
    color: #8E9A91;
    font-size: 0.92rem;
    margin-top: 7px;
}


/* ==========================================================
   FILE UPLOADER
========================================================== */

[data-testid="stFileUploader"] {
    background-color: #181D19;
    border: 1px solid #29332C;
    border-radius: 14px;
    padding: 8px 12px;
    margin-bottom: 14px;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: #181D19 !important;
    border: none !important;
    padding-top: 12px;
    padding-bottom: 12px;
}

[data-testid="stFileUploaderDropzone"] * {
    color: #C7D0C9 !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background-color: #416F50 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    font-weight: 500 !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background-color: #4E805E !important;
}


/* ==========================================================
   DOCUMENT STATUS
========================================================== */

.document-ready {
    display: inline-block;
    font-size: 0.81rem;
    color: #A7C9AE;
    background-color: #1A2A1F;
    border: 1px solid #294132;
    border-radius: 20px;
    padding: 5px 10px;
    margin-bottom: 20px;
}


/* ==========================================================
   USER MESSAGE - DREAPTA
========================================================== */

.user-message-wrapper {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    margin: 12px 0;
}

.user-message {
    max-width: 78%;
    background-color: #443251;
    color: #F1EAF6;
    border: 1px solid #604A70;
    border-radius: 16px 5px 16px 16px;
    padding: 12px 16px;
    font-size: 0.96rem;
    line-height: 1.55;
    overflow-wrap: anywhere;
}


/* ==========================================================
   FORAGER MESSAGE - STÂNGA
========================================================== */

.forager-message-wrapper {
    width: 100%;
    display: flex;
    justify-content: flex-start;
    margin: 12px 0 5px 0;
}

.forager-message {
    max-width: 78%;
    background-color: #1D2C22;
    color: #DCE8DE;
    border: 1px solid #2C4634;
    border-radius: 5px 16px 16px 16px;
    padding: 12px 16px;
    font-size: 0.96rem;
    line-height: 1.55;
    overflow-wrap: anywhere;
}


/* ==========================================================
   PAGE INFO
========================================================== */

.source-info {
    margin-top: 8px;
    padding-top: 7px;
    border-top: 1px solid rgba(190, 215, 195, 0.10);
    font-size: 0.76rem;
    color: #8FA092;
}


/* ==========================================================
   EXPANDER SURSE
========================================================== */

[data-testid="stExpander"] {
    max-width: 78%;
    background-color: #151C17 !important;
    border: 1px solid #29392F !important;
    border-radius: 12px !important;
    margin-top: 5px;
    margin-bottom: 14px;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    color: #A8C5AF !important;
    font-size: 0.82rem !important;
}

[data-testid="stExpander"] p {
    color: #D2DCD4 !important;
    font-size: 0.85rem !important;
    line-height: 1.55 !important;
}

[data-testid="stExpander"] hr {
    border-color: #29392F !important;
}


/* ==========================================================
   BOTTOM AREA
========================================================== */

[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div,
section[data-testid="stBottom"] {
    background: #111512 !important;
    background-color: #111512 !important;
    border: none !important;
    box-shadow: none !important;
}

div[data-testid="stBottomBlockContainer"] > div {
    background: #111512 !important;
    background-color: #111512 !important;
}


/* ==========================================================
   CHAT INPUT
========================================================== */

[data-testid="stChatInput"] {
    background: #181D19 !important;
    background-color: #181D19 !important;

    border: 1px solid #344238 !important;
    border-radius: 14px !important;

    box-shadow: none !important;
    overflow: hidden !important;
}


/* wrappers interne */

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #181D19 !important;
    background-color: #181D19 !important;

    border: none !important;
    box-shadow: none !important;
}


/* textarea */

[data-testid="stChatInput"] textarea,
textarea[data-testid="stChatInputTextArea"] {
    background: #181D19 !important;
    background-color: #181D19 !important;

    color: #F1F5F2 !important;
    -webkit-text-fill-color: #F1F5F2 !important;

    caret-color: #87B994 !important;

    border: none !important;
    box-shadow: none !important;

    opacity: 1 !important;
}


/* focus */

[data-testid="stChatInput"] textarea:focus,
textarea[data-testid="stChatInputTextArea"]:focus {
    background: #181D19 !important;
    background-color: #181D19 !important;

    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;

    outline: none !important;
    box-shadow: none !important;
}


/* placeholder */

[data-testid="stChatInput"] textarea::placeholder,
textarea[data-testid="stChatInputTextArea"]::placeholder {
    color: #829087 !important;
    -webkit-text-fill-color: #829087 !important;

    opacity: 1 !important;
}


/* ==========================================================
   SEND BUTTON
========================================================== */

[data-testid="stChatInput"] button {
    background: #416F50 !important;
    background-color: #416F50 !important;

    color: white !important;

    border: none !important;
    border-radius: 9px !important;

    margin-right: 4px !important;
}

[data-testid="stChatInput"] button:hover {
    background: #4C805D !important;
}

[data-testid="stChatInput"] button svg {
    color: white !important;
    fill: white !important;
}


/* ==========================================================
   STREAMLIT CLEANUP
========================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background-color: transparent !important;
}

[data-testid="stHeader"] {
    background-color: transparent !important;
}


/* ==========================================================
   MOBILE
========================================================== */

@media (max-width: 700px) {

    .block-container {
        padding-left: 14px;
        padding-right: 14px;
        padding-top: 1.1rem;
        padding-bottom: 7rem;
    }

    .forager-title {
        font-size: 1.7rem;
    }

    .forager-subtitle {
        font-size: 0.86rem;
    }

    .forager-message,
    .user-message {
        max-width: 90%;
        font-size: 0.94rem;
        padding: 11px 14px;
    }

    [data-testid="stExpander"] {
        max-width: 90%;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# FUNCȚII UI
# ============================================================

def escape_html(text):
    text = str(text)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
        .replace("\n", "<br>")
    )


def show_user_message(message):
    safe_message = escape_html(message)

    html = (
        '<div class="user-message-wrapper">'
        '<div class="user-message">'
        f'{safe_message}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def show_forager_message(message, pages=None):
    safe_message = escape_html(message)

    source_html = ""

    if pages:

        page_text = ", ".join(
            str(page)
            for page in pages
        )

        label = (
            "Pagina"
            if len(pages) == 1
            else "Pagini"
        )

        source_html = (
            '<div class="source-info">'
            f'{label}: {page_text}'
            '</div>'
        )

    html = (
        '<div class="forager-message-wrapper">'
        '<div class="forager-message">'
        f'{safe_message}'
        f'{source_html}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def show_sources(sources):
    if not sources:
        return

    pages = sorted(
        {
            source["page"]
            for source in sources
            if isinstance(
                source["page"],
                int
            )
        }
    )

    if pages:

        pages_text = ", ".join(
            str(page)
            for page in pages
        )

        label = (
            f"Vezi sursele · paginile "
            f"{pages_text}"
        )

    else:

        label = "Vezi sursele"

    with st.expander(label):

        for index, source in enumerate(
            sources,
            start=1
        ):

            page = source.get(
                "page",
                "?"
            )

            text = source.get(
                "text",
                ""
            )

            st.markdown(
                f"**Fragment {index} · "
                f"pagina {page}**"
            )

            st.write(
                text
            )

            if index < len(sources):
                st.divider()


# ============================================================
# HEADER
# ============================================================

header_html = (
    '<div class="forager-header">'
    '<div class="forager-title">'
    'Forager'
    '</div>'
    '<div class="forager-subtitle">'
    'Chat with your documents.'
    '</div>'
    '</div>'
)

st.markdown(
    header_html,
    unsafe_allow_html=True,
)


# ============================================================
# PDF UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Încarcă un document PDF",
    type=["pdf"],
    label_visibility="collapsed",
)


# ============================================================
# PROCESARE PDF
# ============================================================

if uploaded_file is not None:

    file_identifier = (
        f"{uploaded_file.name}_"
        f"{uploaded_file.size}"
    )

    if (
        st.session_state.current_file
        != file_identifier
    ):

        try:

            with st.spinner(
                "Procesez documentul..."
            ):

                (
                    vector_store,
                    page_count,
                    chunk_count
                ) = Backend.process_pdf(
                    uploaded_file
                )

            st.session_state.vector_store = (
                vector_store
            )

            st.session_state.page_count = (
                page_count
            )

            st.session_state.chunk_count = (
                chunk_count
            )

            st.session_state.document_loaded = (
                True
            )

            st.session_state.current_file = (
                file_identifier
            )

            st.session_state.messages = []

            st.rerun()

        except Exception as e:

            st.session_state.vector_store = None

            st.session_state.document_loaded = (
                False
            )

            st.session_state.current_file = None

            st.error(
                f"Nu am putut procesa "
                f"documentul: {e}"
            )


# ============================================================
# PDF ELIMINAT
# ============================================================

if (
    uploaded_file is None
    and st.session_state.current_file is not None
):

    st.session_state.vector_store = None
    st.session_state.document_loaded = False
    st.session_state.current_file = None
    st.session_state.page_count = 0
    st.session_state.chunk_count = 0
    st.session_state.messages = []


# ============================================================
# STATUS DOCUMENT
# ============================================================

if st.session_state.document_loaded:

    status_html = (
        '<div class="document-ready">'
        'Document încărcat · '
        f'{st.session_state.page_count} pagini'
        '</div>'
    )

    st.markdown(
        status_html,
        unsafe_allow_html=True,
    )


# ============================================================
# ISTORIC CHAT
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        show_user_message(
            message["content"]
        )

    elif message["role"] == "assistant":

        show_forager_message(
            message["content"],
            message.get("pages")
        )

        show_sources(
            message.get(
                "sources",
                []
            )
        )


# ============================================================
# CHAT
# ============================================================

if (
    st.session_state.document_loaded
    and st.session_state.vector_store is not None
):

    question = st.chat_input(
        "Întreabă ceva despre document..."
    )

    if question:

        # ----------------------------------------------------
        # ÎNTREBARE USER
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        show_user_message(
            question
        )


        try:

            # ------------------------------------------------
            # CĂUTARE RELEVANTĂ
            # ------------------------------------------------

            (
                all_results,
                filtered_results
            ) = Backend.search_relevant_chunks(
                st.session_state.vector_store,
                question
            )


            # ------------------------------------------------
            # FĂRĂ REZULTATE
            # ------------------------------------------------

            if not filtered_results:

                question_lower = question.lower()

                romanian_words = [
                    "care", "este", "sunt", "ce", "cum",
                    "unde", "cand", "când", "cat", "cât",
                    "cine", "despre", "pot", "poate",
                    "vreau", "are", "am", "exista", "există",
                    "capitala", "frantei", "franței"
                ]

                words = (
                    question_lower
                    .replace("?", "")
                    .replace("!", "")
                    .replace(".", "")
                    .replace(",", "")
                    .split()
                )

                is_romanian = (
                    any(
                        word in romanian_words
                        for word in words
                    )
                    or any(
                        char in question_lower
                        for char in "ăâîșț"
                    )
                )

                if is_romanian:
                    answer = (
                        "Nu pot găsi această informație "
                        "în document."
                    )
                else:
                    answer = (
                        "I cannot find this information "
                        "in the document."
                    )

                pages = []
                sources = []
            # ------------------------------------------------
            # AVEM REZULTATE
            # ------------------------------------------------

            else:

                context = Backend.build_context(
                    filtered_results
                )

                pages = Backend.get_source_pages(
                    filtered_results
                )

                sources = []

                for (
                    document,
                    score
                ) in filtered_results:

                    sources.append(
                        {
                            "page":
                                document.metadata.get(
                                    "page",
                                    "?"
                                ),

                            "text":
                                document.page_content,

                            "score":
                                float(score),
                        }
                    )


                # --------------------------------------------
                # QWEN
                # --------------------------------------------

                with st.spinner(
                    "Forager caută în document..."
                ):

                    answer = Backend.ask_qwen(
                        question,
                        context
                    )


            # ------------------------------------------------
            # SALVARE RĂSPUNS
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role":
                        "assistant",

                    "content":
                        answer,

                    "pages":
                        pages,

                    "sources":
                        sources,
                }
            )


            # ------------------------------------------------
            # AFIȘARE
            # ------------------------------------------------

            show_forager_message(
                answer,
                pages
            )

            show_sources(
                sources
            )


        # ----------------------------------------------------
        # OLLAMA OFFLINE
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            error_message = (
                "Nu mă pot conecta la Ollama. "
                "Verifică dacă Ollama rulează."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "pages": [],
                    "sources": [],
                }
            )

            show_forager_message(
                error_message
            )


        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            error_message = (
                "Modelul a răspuns prea greu. "
                "Încearcă din nou."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "pages": [],
                    "sources": [],
                }
            )

            show_forager_message(
                error_message
            )


        # ----------------------------------------------------
        # ALTE ERORI
        # ----------------------------------------------------

        except Exception as e:

            error_message = (
                f"A apărut o eroare: {e}"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "pages": [],
                    "sources": [],
                }
            )

            show_forager_message(
                error_message
            )


# ============================================================
# CHAT DEZACTIVAT
# ============================================================

else:

    st.chat_input(
        "Încarcă un PDF pentru a începe...",
        disabled=True,
    )