"""
Streamlit Chat UI for Multi-Agent Chat System.

This application provides a user-friendly chat interface for interacting
with AI agents that can query different database schemas.
"""
import os
import csv
import io
import streamlit as st
import requests
import json
from typing import Dict, List, Optional

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Chat AI Multi-Agente",
    page_icon="🤖",
    layout="wide"
)


def init_session_state():
    """Initialize Streamlit session state."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None
    if "faq_suggestions" not in st.session_state:
        st.session_state.faq_suggestions = {}
    if "active_page" not in st.session_state:
        st.session_state.active_page = "chat"


def _extract_markdown_table(text: str) -> Optional[List[Dict[str, str]]]:
    lines = text.splitlines()
    start_index: Optional[int] = None

    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "|" in line.strip().strip("|"):
            if i + 1 < len(lines):
                separator = lines[i + 1].strip()
                if separator.startswith("|") and set(separator.replace("|", "").strip()) <= set("- :"):
                    start_index = i
                    break

    if start_index is None:
        return None

    header_line = lines[start_index].strip()
    if start_index + 1 >= len(lines):
        return None

    data_lines: List[str] = []
    for j in range(start_index + 2, len(lines)):
        row = lines[j]
        if not row.strip().startswith("|"):
            break
        data_lines.append(row.strip())

    if not data_lines:
        return None

    def split_row(row: str) -> List[str]:
        return [cell.strip() for cell in row.strip().strip("|").split("|")]

    headers = split_row(header_line)
    if not headers:
        return None

    rows: List[Dict[str, str]] = []
    for row_line in data_lines:
        cells = split_row(row_line)
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))

    if not rows:
        return None

    return rows


def _render_csv_download_from_text(text: str, key_suffix: str) -> None:
    table = _extract_markdown_table(text)
    if not table:
        return

    headers = list(table[0].keys())
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in table:
        writer.writerow([row.get(col, "") for col in headers])

    data = buffer.getvalue().encode("utf-8-sig")
    st.download_button(
        "Scarica tabella in CSV",
        data=data,
        file_name="risultati_chat.csv",
        mime="text/csv",
        key=f"download_csv_{key_suffix}",
    )


def login_page():
    """Display login/registration page."""
    st.title("🤖 Chat AI Multi-Agente")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Registrazione"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Accedi")
            
            if submit:
                if not username or not password:
                    st.error("Inserisci username e password.")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/auth/login",
                            json={"username": username, "password": password}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.session_id = data["session_id"]
                            st.session_state.username = data["username"]
                            st.success(data["message"])
                            st.rerun()
                        else:
                            error = response.json().get("detail", "Errore durante il login.")
                            st.error(error)
                    except Exception as e:
                        st.error(f"Errore di connessione: {str(e)}")
    
    with tab2:
        st.subheader("Registrazione")
        with st.form("register_form"):
            username = st.text_input("Username", key="reg_username")
            password = st.text_input("Password (minimo 6 caratteri)", type="password", key="reg_password")
            password_confirm = st.text_input("Conferma Password", type="password")
            submit = st.form_submit_button("Registrati")
            
            if submit:
                if not username or not password:
                    st.error("Inserisci username e password.")
                elif len(password) < 6:
                    st.error("La password deve essere di almeno 6 caratteri.")
                elif password != password_confirm:
                    st.error("Le password non coincidono.")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/auth/register",
                            json={"username": username, "password": password}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.session_id = data["session_id"]
                            st.session_state.username = data["username"]
                            st.success(data["message"])
                            st.rerun()
                        else:
                            error = response.json().get("detail", "Errore durante la registrazione.")
                            st.error(error)
                    except Exception as e:
                        st.error(f"Errore di connessione: {str(e)}")


def get_agents() -> List[Dict]:
    """Get list of available agents."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/agents")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_conversations() -> List[Dict]:
    """Get list of user conversations (most recent first)."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/chat/conversations",
            headers={"X-Session-ID": st.session_state.session_id},
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def get_faq_suggestions(agent_name: str, limit: int = 50) -> List[Dict]:
    """Get FAQ suggestions for the given agent based on recent user questions."""
    if not agent_name or not st.session_state.session_id:
        return []

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/chat/faq_suggestions",
            params={"agent_name": agent_name, "limit": limit},
            headers={"X-Session-ID": st.session_state.session_id},
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def get_admin_agents() -> List[Dict]:
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/admin/agents",
            headers={"X-Session-ID": st.session_state.session_id},
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def load_conversation_messages(conversation_id: int):
    """Load messages from a conversation."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/chat/conversations/{conversation_id}/messages",
            headers={"X-Session-ID": st.session_state.session_id}
        )
        
        if response.status_code == 200:
            messages = response.json()
            st.session_state.messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
    except Exception as e:
        st.error(f"Errore nel caricamento della conversazione: {str(e)}")


def chat_page():
    """Display main chat page."""
    # Sidebar
    with st.sidebar:
        st.title("🤖 Chat AI")
        st.markdown(f"**Utente:** {st.session_state.username}")
        
        if st.button("Logout"):
            st.session_state.session_id = None
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Agent selector
        st.subheader("Seleziona Agente")
        agents = get_agents()
        
        if agents:
            agent_options = {agent["name"]: agent["description"] for agent in agents}
            selected_agent = st.selectbox(
                "Agente",
                options=list(agent_options.keys()),
                format_func=lambda x: f"{x.capitalize()} - {agent_options[x]}"
            )
            
            # If agent changed, clear messages and start new conversation
            if selected_agent != st.session_state.current_agent:
                st.session_state.current_agent = selected_agent
                st.session_state.messages = []
                st.session_state.conversation_id = None
        else:
            st.error("Impossibile caricare gli agenti.")
            selected_agent = None
        
        st.markdown("---")
        
        # New conversation button
        if st.button("Nuova Conversazione"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

        # Recent conversations selector (last 10 distinct questions for current user)
        st.subheader("Conversazioni recenti")
        conversations = get_conversations()

        if conversations:
            # Build list of distinct conversations by (title, agent)
            recent_conversations = []
            seen_keys = set()
            current_agent = st.session_state.get("current_agent")
            for conv in conversations:
                if current_agent and conv.get("agent_name") != current_agent:
                    continue
                title = (conv.get("title") or "").strip()
                key = (title.lower(), conv.get("agent_name"))
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                recent_conversations.append(conv)
                if len(recent_conversations) >= 10:
                    break

            if recent_conversations:
                # Map conversation id to display label
                conv_ids = [conv["id"] for conv in recent_conversations]
                conv_labels = {
                    None: "(Nuova conversazione)",
                    **{
                        conv["id"]: f"{(conv['title'] or '(senza titolo)')[:60]} - {conv['agent_name']}"
                        for conv in recent_conversations
                    },
                }

                # Options include a placeholder for new conversation (None)
                options = [None] + conv_ids

                # Keep selectbox in sync with current conversation when possible
                if st.session_state.conversation_id in conv_ids:
                    default_index = conv_ids.index(st.session_state.conversation_id) + 1
                else:
                    # Default to "new conversation" placeholder
                    default_index = 0

                selected_conv_id = st.selectbox(
                    "Ultime domande",
                    options=options,
                    index=default_index,
                    format_func=lambda cid: conv_labels.get(cid, str(cid)),
                )

                selected_conv = next(
                    (c for c in recent_conversations if c["id"] == selected_conv_id),
                    None,
                )

                # Button to re-run the selected question as a new search
                if selected_conv is not None and selected_conv_id is not None:
                    if st.button("Riesegui questa domanda", key="rerun_selected_question"):
                        st.session_state.pending_prompt = selected_conv.get("title") or ""
                        st.session_state.current_agent = selected_conv.get("agent_name")
                        st.session_state.conversation_id = None
                        st.session_state.messages = []
                        st.rerun()

                # When user picks a different conversation, load its messages
                if selected_conv_id != st.session_state.conversation_id:
                    st.session_state.conversation_id = selected_conv_id

                    if selected_conv_id is None:
                        # Explicit new conversation: clear messages only
                        st.session_state.messages = []
                    else:
                        # Align current agent with conversation's agent
                        if selected_conv is not None:
                            st.session_state.current_agent = selected_conv["agent_name"]

                        load_conversation_messages(selected_conv_id)

                    st.rerun()
            else:
                st.caption("Nessuna conversazione trovata.")
        else:
            st.caption("Nessuna conversazione trovata.")

        st.markdown("---")

        # FAQ suggestions for current agent
        st.subheader("FAQ suggerite")
        current_agent = st.session_state.get("current_agent")

        if not current_agent:
            st.caption("Seleziona un agente per generare le FAQ.")
        else:
            if "faq_suggestions" not in st.session_state:
                st.session_state.faq_suggestions = {}

            faq_for_agent = st.session_state.faq_suggestions.get(current_agent)

            if st.button("Genera/aggiorna FAQ", key="generate_faq"):
                faq_for_agent = get_faq_suggestions(current_agent)
                st.session_state.faq_suggestions[current_agent] = faq_for_agent

            if faq_for_agent:
                for idx, faq in enumerate(faq_for_agent):
                    question = (faq.get("question") or "").strip() or f"FAQ {idx + 1}"
                    answer = (faq.get("answer") or "").strip()

                    with st.expander(question):
                        if answer:
                            st.markdown(answer)

                        if st.button(
                            "Usa questa FAQ",
                            key=f"use_faq_{current_agent}_{idx}",
                        ):
                            st.session_state.pending_prompt = question
                            st.session_state.conversation_id = None
                            st.session_state.messages = []
                            st.rerun()
            else:
                st.caption("Nessuna FAQ disponibile. Premi 'Genera/aggiorna FAQ'.")

        if st.session_state.username == "admin":
            st.markdown("---")
            st.subheader("Pannello Admin")
            st.caption("Gestisci gli agenti dal pannello dedicato.")
            if st.button("Apri pannello Admin", key="open_admin_panel"):
                st.session_state.active_page = "admin"
                st.rerun()

    # Main chat area
    st.title(f"💬 Chat con {st.session_state.current_agent.capitalize() if st.session_state.current_agent else 'Agente'}")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    last_assistant: Optional[Dict[str, str]] = None
    for msg in reversed(st.session_state.messages):
        if msg.get("role") == "assistant":
            last_assistant = msg
            break
    if last_assistant and isinstance(last_assistant.get("content"), str):
        key_suffix = str(st.session_state.get("conversation_id") or "current")
        _render_csv_download_from_text(last_assistant["content"], key_suffix)
    
    # Chat input (supports auto-rerun from pending_prompt)
    pending_prompt = st.session_state.get("pending_prompt")
    user_input = st.chat_input("Scrivi un messaggio...")
    if pending_prompt:
        prompt = pending_prompt
        st.session_state.pending_prompt = None
    else:
        prompt = user_input

    if prompt:
        if not st.session_state.current_agent:
            st.error("Seleziona un agente prima di inviare un messaggio.")
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Stream agent response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Make streaming request
                response = requests.post(
                    f"{API_BASE_URL}/api/chat/stream",
                    json={
                        "agent_name": st.session_state.current_agent,
                        "message": prompt,
                        "conversation_id": st.session_state.conversation_id
                    },
                    headers={"X-Session-ID": st.session_state.session_id},
                    stream=True
                )
                
                if response.status_code == 200:
                    # Process SSE stream
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  # Remove 'data: ' prefix
                                
                                try:
                                    data = json.loads(data_str)
                                    
                                    if data["type"] == "conversation_id":
                                        st.session_state.conversation_id = data["id"]
                                    elif data["type"] == "content":
                                        full_response += data["content"]
                                        message_placeholder.markdown(full_response + "▌")
                                    elif data["type"] == "done":
                                        message_placeholder.markdown(full_response)
                                    elif data["type"] == "error":
                                        st.error(f"Errore: {data['error']}")
                                        full_response = f"❌ Errore: {data['error']}"
                                        message_placeholder.markdown(full_response)
                                except json.JSONDecodeError:
                                    pass
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    error = response.json().get("detail", "Errore durante la richiesta.")
                    st.error(error)
                    
            except Exception as e:
                st.error(f"Errore di connessione: {str(e)}")


def admin_page():
    """Render dedicated admin management dashboard."""
    if st.session_state.username != "admin":
        st.warning("Accesso riservato agli amministratori.")
        if st.button("Torna alla chat", key="admin_back_to_chat"):
            st.session_state.active_page = "chat"
            st.rerun()
        return

    with st.sidebar:
        st.title("🔐 Admin")
        st.markdown(f"**Utente:** {st.session_state.username}")

        if st.button("Torna alla chat", key="back_to_chat"):
            st.session_state.active_page = "chat"
            st.rerun()

        if st.button("Logout", key="admin_logout"):
            st.session_state.session_id = None
            st.session_state.username = None
            st.session_state.messages = []
            st.session_state.active_page = "chat"
            st.rerun()

        st.markdown("---")
        st.caption("Gestisci gli agenti, schedulazioni e strumenti consentiti.")

    st.title("Pannello di amministrazione")

    # Tabs for different admin sections
    tab1, tab2 = st.tabs(["Gestione Agenti", "📅 Schedulazioni"])

    # ========================================
    # TAB 1: Agent Management
    # ========================================
    with tab1:
        st.markdown(
            """
            Utilizza questa pagina per aggiornare le impostazioni degli agenti disponibili
            nell'applicazione.
            """
        )

        agents = get_admin_agents()

        if not agents:
            st.info("Nessun agente disponibile oppure impossibile recuperare i dati.")
            if st.button("Riprova", key="reload_admin_agents"):
                st.rerun()
            return

        agent_names = [a["name"] for a in agents]
        selected_agent_name = st.selectbox(
            "Seleziona un agente da modificare",
            options=agent_names,
        )

        selected_agent = next((a for a in agents if a["name"] == selected_agent_name), None)

        if selected_agent is None:
            st.error("Agente non trovato.")
            return

        col_info, col_actions = st.columns([1, 2])
        with col_info:
            st.markdown("### Dettagli correnti")
            st.json({
                "ID": selected_agent.get("id"),
                "Descrizione": selected_agent.get("description"),
                "System prompt": selected_agent.get("system_prompt"),
                "Attivo": selected_agent.get("is_active"),
                "Tools": selected_agent.get("tool_names"),
            })

        with col_actions:
            st.markdown("### Modifica agente")
            form_key = f"admin_agent_form_{selected_agent['id']}"
            with st.form(form_key):
                new_description = st.text_input(
                    "Descrizione",
                    value=selected_agent.get("description") or "",
                )
                new_prompt = st.text_area(
                    "System prompt",
                    value=selected_agent.get("system_prompt") or "",
                    height=220,
                )
                new_active = st.checkbox(
                    "Agente attivo",
                    value=selected_agent.get("is_active", True),
                )
                new_tool_names = st.text_input(
                    "Tools (nomi separati da virgola)",
                    value=selected_agent.get("tool_names") or "",
                )

                submitted = st.form_submit_button("Salva modifiche")

                if submitted:
                    payload = {
                        "description": new_description,
                        "system_prompt": new_prompt,
                        "is_active": new_active,
                        "tool_names": new_tool_names,
                    }
                    try:
                        resp = requests.put(
                            f"{API_BASE_URL}/api/admin/agents/{selected_agent['id']}",
                            json=payload,
                            headers={"X-Session-ID": st.session_state.session_id},
                        )
                        if resp.status_code == 200:
                            st.success("Agente aggiornato con successo.")
                            st.rerun()
                        else:
                            error_msg = resp.json().get("detail", "Errore durante l'aggiornamento dell'agente.")
                            st.error(error_msg)
                    except Exception as e:
                        st.error(f"Errore di connessione: {str(e)}")

        st.markdown("---")
        st.caption(
            "Suggerimento: assicurati di mantenere sincronizzati prompt e tools con le funzionalità disponibili lato backend."
        )

    # ========================================
    # TAB 2: Scheduled Tasks Management
    # ========================================
    with tab2:
        st.markdown("### Schedulazioni Report Automatici")
        st.caption("Configura l'esecuzione automatica di query e l'invio di report via email.")

        # Get scheduled tasks
        schedules = get_schedules()

        # Show create button
        col_btn1, col_btn2 = st.columns([1, 5])
        with col_btn1:
            if st.button("➕ Nuova Schedulazione", key="new_schedule_btn"):
                st.session_state.schedule_action = "create"
                st.rerun()
        with col_btn2:
            if st.button("🔄 Aggiorna", key="refresh_schedules"):
                st.rerun()

        # Create/Edit form
        if st.session_state.get("schedule_action") in ["create", "edit"]:
            action = st.session_state.schedule_action
            schedule_id = st.session_state.get("edit_schedule_id")

            st.markdown("---")
            st.markdown(f"### {'Nuova' if action == 'create' else 'Modifica'} Schedulazione")

            # Get existing data if editing
            existing_data = {}
            if action == "edit" and schedule_id:
                existing_data = next((s for s in schedules if s["id"] == schedule_id), {})

            with st.form("schedule_form"):
                name = st.text_input(
                    "Nome schedulazione *",
                    value=existing_data.get("name", ""),
                    placeholder="es. Report vendite mensile"
                )

                description = st.text_area(
                    "Descrizione",
                    value=existing_data.get("description", ""),
                    placeholder="Descrizione opzionale della schedulazione"
                )

                # Agent selection
                agent_list = get_agents()
                agent_names = [a["name"] for a in agent_list]
                current_agent = existing_data.get("agent_name", agent_names[0] if agent_names else "")
                agent_idx = agent_names.index(current_agent) if current_agent in agent_names else 0

                agent_name = st.selectbox(
                    "Agente *",
                    options=agent_names,
                    index=agent_idx,
                )

                prompt = st.text_area(
                    "Domanda/Query *",
                    value=existing_data.get("prompt", ""),
                    placeholder="es. Quali sono i prodotti più venduti nel mese precedente?",
                    height=100
                )

                # Cron expression with presets
                st.markdown("**Frequenza esecuzione ***")
                freq_preset = st.selectbox(
                    "Preset frequenza",
                    options=[
                        "Custom (cron expression)",
                        "Ogni giorno alle 09:00",
                        "Ogni lunedì alle 09:00",
                        "Primo lunedì del mese alle 09:00",
                        "Primo giorno del mese alle 09:00"
                    ],
                )

                # Map presets to cron
                cron_presets = {
                    "Ogni giorno alle 09:00": "0 9 * * *",
                    "Ogni lunedì alle 09:00": "0 9 * * 1",
                    "Primo lunedì del mese alle 09:00": "0 9 * * 1#1",
                    "Primo giorno del mese alle 09:00": "0 9 1 * *",
                }

                if freq_preset == "Custom (cron expression)":
                    cron_expression = st.text_input(
                        "Cron expression",
                        value=existing_data.get("cron_expression", "0 9 * * *"),
                        help="Formato: minuto ora giorno mese giorno_settimana"
                    )
                else:
                    cron_expression = cron_presets[freq_preset]
                    st.code(cron_expression, language="text")

                # Email recipients
                emails_str = existing_data.get("recipient_emails", [])
                if isinstance(emails_str, list):
                    emails_str = ", ".join(emails_str)

                recipient_emails = st.text_input(
                    "Email destinatari (separati da virgola) *",
                    value=emails_str,
                    placeholder="email1@example.com, email2@example.com"
                )

                is_active = st.checkbox(
                    "Schedulazione attiva",
                    value=existing_data.get("is_active", True)
                )

                col_submit, col_cancel = st.columns([1, 5])
                with col_submit:
                    submitted = st.form_submit_button("💾 Salva")
                with col_cancel:
                    if st.form_submit_button("❌ Annulla"):
                        st.session_state.schedule_action = None
                        st.rerun()

                if submitted:
                    # Validate
                    if not name or not agent_name or not prompt or not recipient_emails:
                        st.error("Compila tutti i campi obbligatori (*)")
                    else:
                        # Parse emails
                        emails_list = [e.strip() for e in recipient_emails.split(",")]

                        payload = {
                            "name": name,
                            "description": description,
                            "agent_name": agent_name,
                            "prompt": prompt,
                            "cron_expression": cron_expression,
                            "recipient_emails": emails_list,
                            "is_active": is_active,
                        }

                        try:
                            if action == "create":
                                resp = create_schedule(payload)
                            else:
                                resp = update_schedule(schedule_id, payload)

                            if resp:
                                st.success(f"Schedulazione {'creata' if action == 'create' else 'aggiornata'} con successo!")
                                st.session_state.schedule_action = None
                                st.rerun()
                            else:
                                st.error("Errore durante il salvataggio.")
                        except Exception as e:
                            st.error(f"Errore: {str(e)}")

        # Show schedules table
        st.markdown("---")
        st.markdown("### Schedulazioni Configurate")

        if not schedules:
            st.info("Nessuna schedulazione configurata. Clicca su '➕ Nuova Schedulazione' per iniziare.")
        else:
            for schedule in schedules:
                with st.expander(
                    f"{'✅' if schedule['is_active'] else '❌'} {schedule['name']} - {schedule['agent_name']}",
                    expanded=False
                ):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.markdown(f"**Descrizione:** {schedule.get('description') or 'N/A'}")
                        st.markdown(f"**Prompt:** {schedule['prompt']}")
                        st.markdown(f"**Cron:** `{schedule['cron_expression']}`")
                        st.markdown(f"**Email:** {', '.join(schedule['recipient_emails'])}")
                        st.markdown(f"**Stato:** {'🟢 Attiva' if schedule['is_active'] else '🔴 Disattivata'}")
                        
                        if schedule.get("last_run_at"):
                            st.markdown(f"**Ultima esecuzione:** {schedule['last_run_at']}")
                            st.markdown(f"**Status:** {schedule.get('last_run_status', 'N/A')}")
                            if schedule.get("last_run_error"):
                                st.error(f"Errore: {schedule['last_run_error']}")
                        
                        if schedule.get("next_run_at"):
                            st.markdown(f"**Prossima esecuzione:** {schedule['next_run_at']}")

                    with col2:
                        if st.button("✏️ Modifica", key=f"edit_{schedule['id']}"):
                            st.session_state.schedule_action = "edit"
                            st.session_state.edit_schedule_id = schedule['id']
                            st.rerun()

                        if st.button("🧪 Test", key=f"test_{schedule['id']}"):
                            with st.spinner("Esecuzione test in corso..."):
                                result = test_schedule(schedule['id'])
                                if result:
                                    if result.get("status") == "success":
                                        st.success("Test completato con successo! Email inviata.")
                                    else:
                                        st.error(f"Test fallito: {result.get('error', 'Errore sconosciuto')}")
                                    st.rerun()

                        if st.button("🗑️ Elimina", key=f"delete_{schedule['id']}"):
                            if delete_schedule(schedule['id']):
                                st.success("Schedulazione eliminata.")
                                st.rerun()
                            else:
                                st.error("Errore durante l'eliminazione")


def get_schedules() -> List[Dict]:
    """Get list of scheduled tasks."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/admin/schedules",
            headers={"X-Session-ID": st.session_state.session_id},
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def create_schedule(payload: Dict) -> bool:
    """Create a new schedule."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/admin/schedules",
            json=payload,
            headers={"X-Session-ID": st.session_state.session_id},
        )
        return response.status_code == 200
    except Exception:
        return False


def update_schedule(schedule_id: int, payload: Dict) -> bool:
    """Update an existing schedule."""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/admin/schedules/{schedule_id}",
            json=payload,
            headers={"X-Session-ID": st.session_state.session_id},
        )
        return response.status_code == 200
    except Exception:
        return False


def delete_schedule(schedule_id: int) -> bool:
    """Delete a schedule."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/admin/schedules/{schedule_id}",
            headers={"X-Session-ID": st.session_state.session_id},
        )
        return response.status_code == 200
    except Exception:
        return False


def test_schedule(schedule_id: int) -> Optional[Dict]:
    """Test a schedule manually."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/admin/schedules/{schedule_id}/test",
            headers={"X-Session-ID": st.session_state.session_id},
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def main():
    """Main application entry point."""
    init_session_state()
    
    # Check if user is logged in
    if st.session_state.session_id is None:
        login_page()
    else:
        active_page = st.session_state.get("active_page", "chat")
        if active_page == "admin" and st.session_state.username == "admin":
            admin_page()
        else:
            st.session_state.active_page = "chat"
            chat_page()


if __name__ == "__main__":
    main()
