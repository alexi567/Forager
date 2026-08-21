import streamlit as st
import requests

from Backend import (
    process_pdf,
    search_relevant_chunks,
    build_context,
    get_source_pages,
    ask_qwen
)


st.set_page_config(
    page_title="PDF Assistant",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF Assistant")

st.write(
    "Încarcă un PDF și pune întrebări folosind doar informațiile din document."
)


# -----------------------------
# SESSION STATE
# -----------------------------

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# UPLOAD PDF
# -----------------------------

uploaded_file = st.file_uploader(
    "Încarcă un fișier PDF",
    type=["pdf"]
)


if uploaded_file is not None:

    current_file_id = (
        f"{uploaded_file.name}-{uploaded_file.size}"
    )

    # Procesam PDF-ul doar daca este un fisier nou
    if st.session_state.processed_file != current_file_id:

        with st.spinner(
            "Procesez PDF-ul și creez indexul semantic..."
        ):

            try:
                vector_store, pages, chunks = process_pdf(
                    uploaded_file
                )

                st.session_state.vector_store = vector_store
                st.session_state.processed_file = current_file_id

                # Stergem conversatia veche cand se incarca
                # un document nou
                st.session_state.messages = []

                st.success(
                    f"Document procesat cu succes: "
                    f"{pages} pagini, "
                    f"{chunks} fragmente."
                )

            except Exception as error:
                st.session_state.vector_store = None

                st.error(
                    "A apărut o eroare la procesarea PDF-ului."
                )

                st.error(
                    str(error)
                )

    else:
        st.success(
            f"Documentul {uploaded_file.name} este pregătit."
        )


# -----------------------------
# AFISAREA ISTORICULUI
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        # Afisam sursele pentru mesajele AI
        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):
            st.caption(
                "Surse: "
                + ", ".join(
                    f"pag. {page}"
                    for page in message["sources"]
                )
            )


# -----------------------------
# CHAT
# -----------------------------

if st.session_state.vector_store is not None:

    question = st.chat_input(
        "Scrie o întrebare despre document..."
    )

    if question:

        # Salvam intrebarea utilizatorului
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        # Afisam intrebarea
        with st.chat_message("user"):
            st.markdown(question)


        # Generam raspunsul
        with st.chat_message("assistant"):

            with st.spinner(
                "Caut în document și generez răspunsul..."
            ):

                try:

                    # -----------------------------
                    # RETRIEVAL
                    # -----------------------------

                    (
                        results_with_scores,
                        filtered_results
                    ) = search_relevant_chunks(
                        st.session_state.vector_store,
                        question
                    )


                    # -----------------------------
                    # NICIUN REZULTAT RELEVANT
                    # -----------------------------

                    if not filtered_results:

                        answer = (
                            "Nu am găsit această informație "
                            "în document."
                        )

                        st.markdown(answer)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": []
                            }
                        )


                    # -----------------------------
                    # EXISTA CONTEXT RELEVANT
                    # -----------------------------

                    else:

                        context = build_context(
                            filtered_results
                        )

                        answer = ask_qwen(
                            question,
                            context
                        )

                        source_pages = get_source_pages(
                            filtered_results
                        )


                        # -----------------------------
                        # AFISARE RASPUNS
                        # -----------------------------

                        st.markdown(
                            answer
                        )


                        # -----------------------------
                        # AFISARE SURSE
                        # -----------------------------

                        if source_pages:

                            st.caption(
                                "Surse: "
                                + ", ".join(
                                    f"pag. {page}"
                                    for page
                                    in source_pages
                                )
                            )


                        # -----------------------------
                        # SALVARE IN ISTORIC
                        # -----------------------------

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": source_pages
                            }
                        )


                        # -----------------------------
                        # FRAGMENTELE FOLOSITE
                        # -----------------------------

                        with st.expander(
                            "Vezi fragmentele folosite din PDF"
                        ):

                            for i, (
                                document,
                                score
                            ) in enumerate(
                                filtered_results,
                                start=1
                            ):

                                page_number = (
                                    document.metadata.get(
                                        "page",
                                        "?"
                                    )
                                )

                                st.markdown(
                                    f"### Fragment {i} "
                                    f"— pagina {page_number}"
                                )

                                st.write(
                                    document.page_content
                                )


                # -----------------------------
                # EROARE OLLAMA
                # -----------------------------

                except requests.exceptions.RequestException:

                    st.error(
                        "Nu mă pot conecta la Ollama."
                    )

                    st.error(
                        "Verifică dacă Ollama rulează "
                        "și dacă modelul qwen3:8b este instalat."
                    )


                # -----------------------------
                # ALTA EROARE
                # -----------------------------

                except Exception as error:

                    st.error(
                        "A apărut o eroare."
                    )

                    st.error(
                        str(error)
                    )


else:

    st.info(
        "Încarcă mai întâi un PDF "
        "pentru a începe conversația."
    )