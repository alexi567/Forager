import streamlit as st
import requests
import Backend


# ============================================================
# CONFIG
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

defaults = {
    "messages": [],
    "vector_store": None,
    "document_loaded": False,
    "current_file": None,
    "page_count": 0,
    "chunk_count": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --forest-dark: #163B2A;
    --forest: #3E6E4D;
    --forest-mid: #6E9270;
    --forest-soft: #DDE9D8;

    --purple-soft: #E8D8F4;
    --purple-text: #3F2F4C;

    --page-bg: #F8FAF4;
    --text-main: #263229;
    --text-soft: #778078;
}


/* ==========================================================
   PAGE BASE
========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 12% 16%,
            rgba(82, 124, 83, 0.10),
            transparent 26%
        ),
        radial-gradient(
            circle at 88% 30%,
            rgba(109, 145, 104, 0.09),
            transparent 24%
        ),
        linear-gradient(
            180deg,
            #FBFCF8 0%,
            #F1F6ED 100%
        ) !important;
}

.stApp {
    background: transparent !important;
}


/* ==========================================================
   FOREST BACKGROUND - LEFT
========================================================== */

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;

    left: 0;
    bottom: 0;

    width: 280px;
    height: 540px;

    z-index: 0;
    pointer-events: none;

    opacity: 0.14;

    background:

        radial-gradient(
            ellipse at 25% 100%,
            rgba(46, 89, 55, 0.42),
            transparent 68%
        ),

        linear-gradient(
            155deg,
            transparent 48%,
            #244D35 49% 51%,
            transparent 52%
        )
        5px 280px / 130px 175px no-repeat,

        linear-gradient(
            25deg,
            transparent 48%,
            #244D35 49% 51%,
            transparent 52%
        )
        5px 280px / 130px 175px no-repeat,

        linear-gradient(
            155deg,
            transparent 48%,
            #3F6B4B 49% 51%,
            transparent 52%
        )
        80px 190px / 155px 230px no-repeat,

        linear-gradient(
            25deg,
            transparent 48%,
            #3F6B4B 49% 51%,
            transparent 52%
        )
        80px 190px / 155px 230px no-repeat,

        linear-gradient(
            155deg,
            transparent 48%,
            #64866A 49% 51%,
            transparent 52%
        )
        155px 310px / 100px 135px no-repeat,

        linear-gradient(
            25deg,
            transparent 48%,
            #64866A 49% 51%,
            transparent 52%
        )
        155px 310px / 100px 135px no-repeat;
}


/* ==========================================================
   FOREST BACKGROUND - RIGHT
========================================================== */

[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;

    right: 0;
    bottom: 0;

    width: 310px;
    height: 580px;

    z-index: 0;
    pointer-events: none;

    opacity: 0.13;

    background:

        radial-gradient(
            ellipse at 75% 100%,
            rgba(46, 89, 55, 0.42),
            transparent 68%
        ),

        linear-gradient(
            205deg,
            transparent 48%,
            #244D35 49% 51%,
            transparent 52%
        )
        70px 220px / 160px 240px no-repeat,

        linear-gradient(
            -25deg,
            transparent 48%,
            #244D35 49% 51%,
            transparent 52%
        )
        70px 220px / 160px 240px no-repeat,

        linear-gradient(
            205deg,
            transparent 48%,
            #4D7757 49% 51%,
            transparent 52%
        )
        155px 300px / 125px 180px no-repeat,

        linear-gradient(
            -25deg,
            transparent 48%,
            #4D7757 49% 51%,
            transparent 52%
        )
        155px 300px / 125px 180px no-repeat,

        linear-gradient(
            205deg,
            transparent 48%,
            #6E9270 49% 51%,
            transparent 52%
        )
        10px 345px / 100px 140px no-repeat,

        linear-gradient(
            -25deg,
            transparent 48%,
            #6E9270 49% 51%,
            transparent 52%
        )
        10px 345px / 100px 140px no-repeat;
}


/* ==========================================================
   MAIN CONTAINER
========================================================== */

.block-container {
    max-width: 940px !important;

    padding-top: 0 !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
    padding-bottom: 120px !important;

    position: relative;
    z-index: 2;
}


/* ==========================================================
   HEADER
========================================================== */

.forager-header {
    position: sticky;
    top: 0;

    z-index: 999;

    margin-left: -24px;
    margin-right: -24px;

    padding:
        24px
        32px
        22px
        32px;

    background:
        rgba(248, 250, 244, 0.94);

    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);

    border-bottom:
        1px solid
        rgba(49, 79, 57, 0.10);
}

.forager-header::after {
    content: "▲  ▲   ▲";

    position: absolute;

    right: 34px;
    bottom: 18px;

    font-size: 28px;
    letter-spacing: 4px;

    color:
        rgba(46, 93, 58, 0.14);

    pointer-events: none;
}

.forager-title {
    color:
        var(--forest-dark);

    font-size:
        2.35rem;

    font-weight:
        750;

    letter-spacing:
        -0.05em;

    line-height:
        1;
}

.forager-subtitle {
    color:
        #69776D;

    font-size:
        0.98rem;

    margin-top:
        8px;
}


/* ==========================================================
   FILE UPLOADER
========================================================== */

[data-testid="stFileUploader"] {
    margin-top:
        26px;

    margin-bottom:
        14px;

    padding:
        12px
        18px;

    background:
        rgba(255, 255, 255, 0.88);

    border:
        1px solid
        #CBD9C6;

    border-radius:
        18px;

    box-shadow:
        0 5px 20px
        rgba(42, 72, 48, 0.04);
}

[data-testid="stFileUploaderDropzone"] {
    min-height:
        72px;

    background:
        transparent !important;

    border:
        none !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background:
        var(--forest) !important;

    color:
        white !important;

    border:
        none !important;

    border-radius:
        10px !important;

    font-weight:
        600 !important;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background:
        #315D40 !important;
}


/* ==========================================================
   STATUS
========================================================== */

.document-ready {
    display:
        inline-flex;

    align-items:
        center;

    margin:
        7px
        0
        24px
        0;

    padding:
        7px
        12px;

    border-radius:
        999px;

    background:
        #EDF5E8;

    border:
        1px solid
        #D4E4CE;

    color:
        #4B7057;

    font-size:
        0.81rem;
}


/* ==========================================================
   USER MESSAGE
========================================================== */

.user-message-wrapper {
    width:
        100%;

    display:
        flex;

    justify-content:
        flex-end;

    margin:
        17px
        0;
}

.user-message {
    max-width:
        68%;

    padding:
        13px
        17px;

    border-radius:
        20px
        20px
        5px
        20px;

    background:
        linear-gradient(
            135deg,
            #F0E5F8,
            #E1CFF1
        );

    border:
        1px solid
        #D9C3EA;

    color:
        var(--purple-text);

    font-size:
        0.97rem;

    line-height:
        1.55;

    box-shadow:
        0 4px 14px
        rgba(98, 68, 125, 0.05);

    overflow-wrap:
        anywhere;
}


/* ==========================================================
   FORAGER MESSAGE
========================================================== */

.forager-message-wrapper {
    width:
        100%;

    display:
        flex;

    justify-content:
        flex-start;

    margin:
        17px
        0
        6px
        0;
}

.forager-message {
    max-width:
        78%;

    padding:
        15px
        18px;

    border-radius:
        5px
        20px
        20px
        20px;

    background:
        linear-gradient(
            135deg,
            #F1F6EC,
            #E5EFE0
        );

    border:
        1px solid
        #D3E2CE;

    color:
        #29362D;

    font-size:
        0.97rem;

    line-height:
        1.62;

    box-shadow:
        0 4px 16px
        rgba(47, 82, 55, 0.04);

    overflow-wrap:
        anywhere;
}


/* ==========================================================
   SOURCES
========================================================== */

[data-testid="stExpander"] {
    max-width:
        78%;

    margin-top:
        3px;

    margin-bottom:
        14px;

    background:
        rgba(246, 249, 242, 0.96);

    border:
        1px solid
        #D9E5D5;

    border-radius:
        12px;

    overflow:
        hidden;
}

[data-testid="stExpander"] summary {
    color:
        #4A6751;

    font-size:
        0.82rem;
}

[data-testid="stExpander"] p {
    color:
        #344339;

    font-size:
        0.86rem;

    line-height:
        1.55;
}


/* ==========================================================
   BOTTOM AREA
========================================================== */

[data-testid="stBottom"] {
    background:
        linear-gradient(
            180deg,
            rgba(246, 249, 242, 0) 0%,
            rgba(246, 249, 242, 0.92) 30%,
            rgba(246, 249, 242, 1) 70%
        ) !important;

    border:
        none !important;
}

[data-testid="stBottomBlockContainer"] {
    background:
        transparent !important;
}

[data-testid="stBottom"] > div {
    background:
        transparent !important;
}


/* ==========================================================
   CHAT INPUT - FIX COMPLET
========================================================== */

/* container principal */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1px solid #AFC7AA !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 24px rgba(43, 74, 49, 0.08) !important;
}


/* wrapper intern BaseWeb */
[data-testid="stChatInput"] div[data-baseweb="textarea"] {
    background: #FFFFFF !important;
    color: #243229 !important;
}


/* wrapper intern */
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: #FFFFFF !important;
    color: #243229 !important;
}


/* selector folosit de Streamlit pentru textarea */
[data-testid="stChatInputTextArea"] {
    background: #FFFFFF !important;
    color: #243229 !important;
    -webkit-text-fill-color: #243229 !important;
    caret-color: #2F6845 !important;
    opacity: 1 !important;
}


/* textarea standard */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;

    color: #243229 !important;
    -webkit-text-fill-color: #243229 !important;

    caret-color: #2F6845 !important;

    opacity: 1 !important;

    font-size: 0.97rem !important;
    font-weight: 400 !important;
}


/* când tastezi */
[data-testid="stChatInput"] textarea:focus {
    background: #FFFFFF !important;

    color: #243229 !important;
    -webkit-text-fill-color: #243229 !important;

    caret-color: #2F6845 !important;
}


/* text introdus */
textarea[data-testid="stChatInputTextArea"] {
    color: #243229 !important;
    -webkit-text-fill-color: #243229 !important;
    background-color: #FFFFFF !important;
}


/* placeholder */
textarea[data-testid="stChatInputTextArea"]::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: #89958C !important;
    -webkit-text-fill-color: #89958C !important;
    opacity: 1 !important;
}


/* contenteditable - pentru compatibilitate */
[data-testid="stChatInput"] [contenteditable="true"] {
    background: #FFFFFF !important;

    color: #243229 !important;
    -webkit-text-fill-color: #243229 !important;

    caret-color: #2F6845 !important;
}


/* evităm ca Streamlit să pună culoare dark pe elementele interne */
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] span,
[data-testid="stChatInput"] p {
    color: #243229 !important;
}


/* buton send */
[data-testid="stChatInput"] button {
    background: #47785A !important;
    color: white !important;

    border: none !important;

    border-radius: 12px !important;
}


/* icon buton */
[data-testid="stChatInput"] button svg {
    fill: white !important;
    color: white !important;
}


/* fundalul zonei de jos */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] > div {
    background: transparent !important;
}/* override final - intenționat la final */
textarea[data-testid="stChatInputTextArea"],
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    color: #1D2921 !important;
    -webkit-text-fill-color: #1D2921 !important;
}
/* ==========================================================
   SEND BUTTON
========================================================== */

[data-testid="stChatInput"] button {
    background:
        #47785A !important;

    color:
        white !important;

    border-radius:
        12px !important;
}

[data-testid="stChatInput"] button:hover {
    background:
        #355F45 !important;
}

[data-testid="stChatInput"] button *,
[data-testid="stChatInput"] button svg {
    color:
        white !important;

    fill:
        white !important;
}


/* ==========================================================
   CLEANUP
========================================================== */

#MainMenu,
footer {
    visibility:
        hidden;
}

[data-testid="stHeader"] {
    background:
        transparent !important;
}


/* ==========================================================
   MOBILE
========================================================== */

@media (max-width: 700px) {

    .block-container {
        padding-left:
            13px !important;

        padding-right:
            13px !important;

        padding-bottom:
            110px !important;
    }

    .forager-header {
        margin-left:
            -13px;

        margin-right:
            -13px;

        padding:
            18px
            16px
            16px
            16px;
    }

    .forager-header::after {
        display:
            none;
    }

    .forager-title {
        font-size:
            1.85rem;
    }

    .forager-subtitle {
        font-size:
            0.86rem;
    }

    [data-testid="stFileUploader"] {
        margin-top:
            18px;
    }

    .user-message {
        max-width:
            88%;

        font-size:
            0.93rem;
    }

    .forager-message {
        max-width:
            92%;

        font-size:
            0.93rem;
    }

    [data-testid="stExpander"] {
        max-width:
            92%;
    }

    [data-testid="stAppViewContainer"]::before {
        width:
            145px;

        height:
            330px;

        opacity:
            0.08;
    }

    [data-testid="stAppViewContainer"]::after {
        width:
            155px;

        height:
            350px;

        opacity:
            0.08;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def escape_html(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
        .replace("\n", "<br>")
    )


def show_user_message(message):
    safe = escape_html(message)

    html = (
        '<div class="user-message-wrapper">'
        '<div class="user-message">'
        f'{safe}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def show_forager_message(message):
    safe = escape_html(message)

    html = (
        '<div class="forager-message-wrapper">'
        '<div class="forager-message">'
        f'{safe}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


def show_sources(sources):
    if not sources:
        return

    pages = sorted(
        {
            source["page"]
            for source in sources
            if isinstance(source["page"], int)
        }
    )

    if pages:
        page_text = ", ".join(
            str(page)
            for page in pages
        )

        label = (
            f"Surse · paginile {page_text}"
        )
    else:
        label = "Surse"

    with st.expander(label):

        for index, source in enumerate(
            sources,
            start=1
        ):

            page = source["page"]

            st.markdown(
                f"**Fragment {index} · pagina {page}**"
            )

            st.write(
                source["text"]
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
    unsafe_allow_html=True
)


# ============================================================
# UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Încarcă un document PDF",
    type=["pdf"],
    label_visibility="collapsed"
)


# ============================================================
# PROCESS PDF
# ============================================================

if uploaded_file is not None:

    file_identifier = (
        f"{uploaded_file.name}_"
        f"{uploaded_file.size}"
    )

    if st.session_state.current_file != file_identifier:

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
                f"Nu am putut procesa documentul: {e}"
            )


# ============================================================
# REMOVE PDF
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
# STATUS
# ============================================================

if st.session_state.document_loaded:

    status_html = (
        '<div class="document-ready">'
        '✓&nbsp;&nbsp;Document încărcat · '
        f'{st.session_state.page_count} pagini'
        '</div>'
    )

    st.markdown(
        status_html,
        unsafe_allow_html=True
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        show_user_message(
            message["content"]
        )

    elif message["role"] == "assistant":

        show_forager_message(
            message["content"]
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

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        show_user_message(
            question
        )

        try:

            (
                all_results,
                filtered_results
            ) = Backend.search_relevant_chunks(
                st.session_state.vector_store,
                question
            )

            if not filtered_results:

                answer = (
                    "Nu pot găsi această "
                    "informație în document."
                )

                sources = []

            else:

                context = (
                    Backend.build_context(
                        filtered_results
                    )
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
                                float(score)
                        }
                    )

                with st.spinner(
                    "Forager caută în document..."
                ):

                    answer = Backend.ask_qwen(
                        question,
                        context
                    )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                }
            )

            show_forager_message(
                answer
            )

            show_sources(
                sources
            )

        except requests.exceptions.ConnectionError:

            error_message = (
                "Nu mă pot conecta la Ollama. "
                "Verifică dacă Ollama rulează."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                }
            )

            show_forager_message(
                error_message
            )

        except requests.exceptions.Timeout:

            error_message = (
                "Modelul a răspuns prea greu. "
                "Încearcă din nou."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                }
            )

            show_forager_message(
                error_message
            )

        except Exception as e:

            error_message = (
                f"A apărut o eroare: {e}"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                }
            )

            show_forager_message(
                error_message
            )


# ============================================================
# CHAT DISABLED
# ============================================================

else:

    st.chat_input(
        "Încarcă un PDF pentru a începe...",
        disabled=True
    )