import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="PrepAI",
    page_icon="🤖",
    layout="centered"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "voice_question" not in st.session_state:
    st.session_state.voice_question = ""

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main {
    padding-top: 2rem;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #777;
    margin-bottom: 35px;
}

.card {
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 20px;
}

.footer {
    text-align: center;
    color: #888;
    font-size: 14px;
    margin-top: 45px;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="title">🤖 PrepAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your AI Technical Interview Assistant</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------

st.markdown("### 💬 Ask your interview question")

question = st.text_area(
    "Type your question",
    placeholder="Example: What is overfitting?",
    height=100,
    label_visibility="collapsed"
)

# --------------------------------------------------
# VOICE INPUT
# --------------------------------------------------

st.markdown("### 🎙️ Or ask using your voice")

audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#ff4b4b",
    neutral_color="#6c757d",
    icon_size="2x"
)

# --------------------------------------------------
# PROCESS NEW RECORDING
# --------------------------------------------------

if audio_bytes and audio_bytes != st.session_state.audio_data:

    st.session_state.audio_data = audio_bytes

    with st.spinner("🎙️ Converting your voice to text..."):

        try:

            files = {
                "file": (
                    "question.wav",
                    audio_bytes,
                    "audio/wav"
                )
            }

            response = requests.post(
                "http://127.0.0.1:8000/transcribe",
                files=files,
                timeout=180
            )

            response.raise_for_status()

            data = response.json()

            if data.get("error"):
                st.error(f"❌ {data['error']}")

            else:

                st.session_state.voice_question = data.get(
                    "text",
                    ""
                )

        except requests.exceptions.Timeout:

            st.error(
                "❌ Transcription took too long. "
                "Please try a shorter recording."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to PrepAI API. "
                "Make sure FastAPI is running."
            )

        except Exception as e:

            st.error(f"❌ Transcription error: {e}")

# --------------------------------------------------
# SHOW TRANSCRIBED QUESTION
# --------------------------------------------------

if st.session_state.voice_question:

    st.markdown("### 📝 Your Question")

    st.info(
        st.session_state.voice_question
    )

# --------------------------------------------------
# ASK PREPAI
# --------------------------------------------------

st.markdown("")

if st.button(
    "🚀 Ask PrepAI",
    use_container_width=True
):

    if question.strip():

        final_question = question.strip()

    elif st.session_state.voice_question:

        final_question = st.session_state.voice_question

    else:

        st.warning(
            "Please type or speak an interview question first."
        )

        st.stop()

    with st.spinner(
        "🧠 PrepAI is researching and improving your answer..."
    ):

        try:

            response = requests.post(
                "http://127.0.0.1:8000/solve",
                json={
                    "question": final_question
                },
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            # ------------------------------------------
            # ANSWER
            # ------------------------------------------

            st.success("Answer generated successfully!")

            st.markdown("### 💡 Interview-Ready Answer")

            st.markdown(
                data["answer"]
            )

            # ------------------------------------------
            # METRICS
            # ------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "⭐ Interview Score",
                    f"{data['score']}/10"
                )

            with col2:

                st.metric(
                    "🔄 Agent Iterations",
                    data["iterations"]
                )

        except requests.exceptions.Timeout:

            st.error(
                "❌ PrepAI took too long to generate the answer."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to PrepAI API. "
                "Make sure FastAPI is running."
            )

        except Exception as e:

            st.error(
                f"❌ Error: {e}"
            )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    '<div class="footer">Built with ❤️ by Disha</div>',
    unsafe_allow_html=True
)