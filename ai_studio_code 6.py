import streamlit as st
import json
from openai import OpenAI

# 1. PAGE SETUP
st.set_page_config(page_title="AI Career Mind Analyst", page_icon="🚀", layout="wide")

# 2. CUSTOM CSS FOR A MODERN UI
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #1E88E5;
    }
    .skill-tag {
        display: inline-block;
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .road-map { font-style: italic; color: #555; }
    </style>
    """, unsafe_allow_html=True)

# 3. INITIALIZE SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! I am your AI Career Strategist. Tell me: What are you currently doing, and what is your biggest career frustration or dream?"}
    ]

if "analysis" not in st.session_state:
    st.session_state.analysis = {
        "skills": [],
        "values": [],
        "paths": [],
        "roadmap": "Awaiting your thoughts..."
    }

# 4. SIDEBAR - SETTINGS
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.info("Your data is analyzed in real-time to update the dashboard on the right.")
    if st.button("Clear History"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# 5. AI ENGINE (SYSTEM PROMPT)
SYSTEM_PROMPT = """
You are a Career Psychologist and Talent Analyst. 
Analyze the user's thoughts for:
1. Skills (Hard and Soft).
2. Core Values (e.g., freedom, high-income, social impact).
3. Best-fit career paths.
4. A concrete next step (Roadmap).

IMPORTANT: Your response must always follow this structure:
[CONVERSATION]
(Write your friendly, professional career advice here)

[DATA]
{
  "skills": ["Skill1", "Skill2"],
  "values": ["Value1", "Value2"],
  "paths": ["Career1", "Career2"],
  "roadmap": "Specific next action step"
}
"""

# 6. APP LAYOUT
st.title("🧠 Career Mind Analyst")
st.markdown("---")

col_chat, col_dash = st.columns([1.5, 1], gap="large")

# --- LEFT COLUMN: CHAT INTERFACE ---
with col_chat:
    st.subheader("Career Coaching")
    
    # Container for messages
    chat_box = st.container(height=500)
    for msg in st.session_state.messages:
        chat_box.chat_message(msg["role"]).write(msg["content"])

    # User Input
    if prompt := st.chat_input("Ex: I'm a teacher but I love data and want more flexibility..."):
        if not api_key:
            st.warning("Please enter your API Key in the sidebar.")
        else:
            client = OpenAI(api_key=api_key)
            
            # Add user message to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            chat_box.chat_message("user").write(prompt)

            # Get AI Response
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
            )
            
            full_res = response.choices[0].message.content
            
            # Parse response
            try:
                if "[DATA]" in full_res:
                    chat_part = full_res.split("[DATA]")[0].replace("[CONVERSATION]", "").strip()
                    json_part = full_res.split("[DATA]")[1].strip()
                    data = json.loads(json_part)
                    st.session_state.analysis = data
                else:
                    chat_part = full_res
            except Exception as e:
                chat_part = "I've analyzed that, but had trouble updating the dashboard. Let's continue!"
            
            # Update UI
            st.session_state.messages.append({"role": "assistant", "content": chat_part})
            chat_box.chat_message("assistant").write(chat_part)
            st.rerun()

# --- RIGHT COLUMN: DYNAMIC DASHBOARD ---
with col_dash:
    st.subheader("Analysis Dashboard")
    
    # Skills Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🛠️ Identified Skills**")
    if st.session_state.analysis["skills"]:
        html_skills = "".join([f'<span class="skill-tag">{s}</span>' for s in st.session_state.analysis["skills"]])
        st.markdown(html_skills, unsafe_allow_html=True)
    else:
        st.write("No skills detected yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Values Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🎯 Core Values & Drivers**")
    if st.session_state.analysis["values"]:
        for v in st.session_state.analysis["values"]:
            st.markdown(f"✅ {v}")
    else:
        st.write("Share your thoughts to see values.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paths Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**🚀 Suggested Career Paths**")
    if st.session_state.analysis["paths"]:
        for p in st.session_state.analysis["paths"]:
            st.success(p)
    else:
        st.write("Awaiting analysis...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Roadmap Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**📍 Growth Roadmap**")
    st.markdown(f'<div class="road-map">{st.session_state.analysis["roadmap"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("AI Career Mind Analyst v1.0 | Powered by OpenAI & Streamlit")