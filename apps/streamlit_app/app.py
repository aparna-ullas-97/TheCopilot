import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Rubix AI", layout="wide")
st.title("Rubix AI")
st.caption("Knowledge assistant for Rubix docs, URLs, and official content")


def fetch_conversations():
    try:
        response = requests.get(f"{API_BASE_URL}/conversations", timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def fetch_conversation_detail(conversation_id: str):
    response = requests.get(f"{API_BASE_URL}/conversations/{conversation_id}", timeout=20)
    response.raise_for_status()
    return response.json()


def delete_conversation(conversation_id: str):
    response = requests.delete(f"{API_BASE_URL}/conversations/{conversation_id}", timeout=20)
    response.raise_for_status()
    return response.json()


def send_chat(message: str, conversation_id: str | None):
    payload = {
        "message": message,
        "conversation_id": conversation_id,
    }
    response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_sources():
    response = requests.get(f"{API_BASE_URL}/sources", timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_source_detail(source_id: str):
    response = requests.get(f"{API_BASE_URL}/sources/{source_id}", timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_source_chunks(source_id: str):
    response = requests.get(f"{API_BASE_URL}/sources/{source_id}/chunks", timeout=20)
    response.raise_for_status()
    return response.json()


def delete_source(source_id: str):
    response = requests.delete(f"{API_BASE_URL}/sources/{source_id}", timeout=20)
    response.raise_for_status()
    return response.json()


def reindex_source(source_id: str):
    response = requests.post(f"{API_BASE_URL}/sources/{source_id}/reindex", timeout=60)
    response.raise_for_status()
    return response.json()


def render_sources(sources):
    if not sources:
        return

    with st.expander("Sources"):
        for idx, src in enumerate(sources, start=1):
            st.markdown(f"**[{idx}] {src['title']}**")
            st.write(f"Type: {src['source_type']}")
            if src.get("url"):
                st.write(src["url"])
            if src.get("score") is not None:
                st.write(f"Score: {src['score']}")
            st.write(src["snippet"])
            st.divider()


def render_source_detail_panel():
    if not st.session_state.selected_source_id:
        st.info("Select a source from the sidebar to inspect it.")
        return

    try:
        source = fetch_source_detail(st.session_state.selected_source_id)
        chunks_data = fetch_source_chunks(st.session_state.selected_source_id)

        st.subheader("Source Details")
        st.markdown(f"**Title:** {source['title']}")
        st.markdown(f"**Type:** {source['source_type']}")
        st.markdown(f"**Trust Level:** {source['trust_level']}")
        if source.get("author"):
            st.markdown(f"**Author:** {source['author']}")
        if source.get("source_url"):
            st.markdown(f"**URL:** {source['source_url']}")
        st.markdown(f"**Created At:** {source['created_at']}")
        st.markdown(f"**Chunk Count:** {source['chunk_count']}")

        if source.get("metadata_json"):
            with st.expander("Metadata"):
                st.json(source["metadata_json"])

        with st.expander("Raw Text", expanded=False):
            st.text_area(
                "Raw Text",
                source["raw_text"],
                height=300,
                key=f"raw_text_{source['id']}",
            )

        with st.expander("Chunks", expanded=False):
            for chunk in chunks_data["chunks"]:
                st.markdown(f"**Chunk {chunk['chunk_index']}**")
                if chunk.get("token_count") is not None:
                    st.write(f"Token Count: {chunk['token_count']}")
                st.code(chunk["chunk_text"], language="text")
                st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Reindex Source", key=f"reindex_{source['id']}"):
                try:
                    result = reindex_source(source["id"])
                    st.success(result["message"])
                    st.rerun()
                except Exception as exc:
                    st.error(f"Reindex failed: {exc}")

        with col2:
            if st.button("Delete Source", key=f"delete_source_{source['id']}"):
                try:
                    delete_source(source["id"])
                    st.success("Source deleted")
                    st.session_state.selected_source_id = None
                    st.rerun()
                except Exception as exc:
                    st.error(f"Delete failed: {exc}")

    except Exception as exc:
        st.error(f"Could not load source details: {exc}")


if "active_conversation_id" not in st.session_state:
    st.session_state.active_conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_source_id" not in st.session_state:
    st.session_state.selected_source_id = None

if "main_tab" not in st.session_state:
    st.session_state.main_tab = "chat"


with st.sidebar:
    st.subheader("Navigation")

    nav_choice = st.radio(
        "Go to",
        ["Chat", "Sources"],
        index=0 if st.session_state.main_tab == "chat" else 1,
    )

    st.session_state.main_tab = nav_choice.lower()

    st.divider()

    if st.session_state.main_tab == "chat":
        st.subheader("Conversations")

        if st.button("New chat"):
            st.session_state.active_conversation_id = None
            st.session_state.messages = []
            st.rerun()

        conversations = fetch_conversations()

        for conv in conversations:
            title = conv.get("title") or "Chat"
            short_id = conv["id"][:6]

            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(f"{title} ({short_id})", key=f"open_conv_{conv['id']}"):
                    st.session_state.active_conversation_id = conv["id"]
                    detail = fetch_conversation_detail(conv["id"])
                    st.session_state.messages = detail["messages"]
                    st.rerun()

            with col2:
                if st.button("🗑", key=f"delete_conv_{conv['id']}"):
                    try:
                        delete_conversation(conv["id"])

                        if st.session_state.active_conversation_id == conv["id"]:
                            st.session_state.active_conversation_id = None
                            st.session_state.messages = []

                        st.rerun()
                    except Exception as exc:
                        st.error(f"Delete failed: {exc}")

    elif st.session_state.main_tab == "sources":
        st.subheader("Sources")

        try:
            sources = fetch_sources()

            for src in sources:
                title = src.get("title") or "Untitled"
                short_id = src["id"][:6]

                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button(
                        f"{title} ({src['source_type']}, {src['chunk_count']} chunks)",
                        key=f"open_source_{src['id']}",
                    ):
                        st.session_state.selected_source_id = src["id"]
                        st.rerun()

                with col2:
                    if st.button("🗑", key=f"delete_src_{src['id']}"):
                        try:
                            delete_source(src["id"])

                            if st.session_state.selected_source_id == src["id"]:
                                st.session_state.selected_source_id = None

                            st.rerun()
                        except Exception as exc:
                            st.error(f"Delete failed: {exc}")

        except Exception as exc:
            st.error(f"Could not load sources: {exc}")


if st.session_state.main_tab == "chat":
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                sources = msg.get("sources_used_json") or []
                render_sources(sources)

    user_input = st.chat_input("Ask Rubix AI...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            data = send_chat(user_input, st.session_state.active_conversation_id)
            st.session_state.active_conversation_id = data.get("conversation_id")

            detail = fetch_conversation_detail(st.session_state.active_conversation_id)
            st.session_state.messages = detail["messages"]

            with st.chat_message("assistant"):
                st.markdown(data["answer"])
                render_sources(data.get("sources", []))

            st.rerun()

        except Exception as exc:
            st.error(f"Request failed: {exc}")

elif st.session_state.main_tab == "sources":
    render_source_detail_panel()