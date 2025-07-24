import streamlit as st
import requests
from googletrans import Translator, LANGUAGES
from gtts import gTTS
from gtts.lang import tts_langs
import tempfile
import os
import re
import random
from streamlit_folium import st_folium
import folium

try:
    from streamlit_lottie import st_lottie
    LOTTIE_AVAILABLE = True
except ImportError:
    LOTTIE_AVAILABLE = False

# ---- API KEYS (replace with your own for production use!) ----
GROQ_API_KEY = ""
GROQ_MODEL = "llama3-70b-8192"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY") or "66rqaiQNC3XdRL7BZuFMmvnO33bKZNOp2209fmVhPuAe813HEzxjSd0h"
UNSPLASH_KEY = os.getenv("UNSPLASH_KEY") or ""

translator = Translator()
tts_supported = tts_langs()
translator_supported = {k.lower(): v.title() for k, v in LANGUAGES.items()}

ALL_LANGUAGE_CHOICES = [
    f"{name} ({code}){' (🔊 Voice)' if code in tts_supported else ' (📝 Text)'}"
    for code, name in sorted(translator_supported.items(), key=lambda x: x[1])
]

TIP_LIST = [
    "🎨 Enjoy a futuristic UI with animation & soft glow!",
    "🗺️ See your live city and location right here.",
    "✨ Try: 'Quantum physics in Kannada', 'Photosynthesis in Telugu'."
]

def add_custom_styles():
    bg_url = "https://image.slidesdocs.com/responsive-images/background/artificial-intelligence-future-technology-illustration-powerpoint-background_78c699b78b__960_540.jpg"
    st.markdown(f"""
    <style>
    body {{
      background: url('{bg_url}') no-repeat center center fixed !important;
      background-size: cover !important;
      min-height:100vh;
      font-family:'Montserrat',sans-serif;
      position: relative;
    }}
    body::after {{
      content: "";
      position: fixed;
      left:0;top:0;width:100vw;height:100vh;z-index:-1;
      pointer-events: none;
      background: linear-gradient(110deg, #071824bb 12%, #7166e899 92%);
      mix-blend-mode: multiply;
      opacity: 0.88;
    }}
    .stApp {{
      background: rgba(17,22,39,0.82);
      min-height:100vh;
      color: #efeefd;
      box-shadow: 0 0 100px 30px #2bc3f177 inset;
      font-family:'Montserrat',sans-serif;
    }}
    .title {{
      font-family:'Montserrat',sans-serif;
      font-size:2.7em;
      font-weight:900;
      color:#fff;
      text-align:center;
      margin:0 0 18px 0;
      letter-spacing:.8px;
      background: linear-gradient(98deg,#00e3ff 11%,#ff9800 91%);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
      background-clip:text;
      text-shadow:0 3px 33px #141a2d66;
    }}
    .ai-tips {{
      background: rgba(0,255,185,0.13);
      color: #ffe28c;
      border-radius:22px;
      padding:13px 25px;
      font-size:1.21em;
      font-family:'Montserrat', sans-serif;
      font-weight: 800;
      text-align:center;
      max-width:550px;
      margin:12px auto 17px auto;
      border:1.6px solid #00b0ee44;
      box-shadow:0 2px 9px #1ad4ff44;
      animation: tipswap 4s infinite alternate;
    }}
    @keyframes tipswap {{
      0%{{box-shadow:0 2px 19px #ffe6c43b;}}
      100%{{box-shadow:0 7px 32px #7efffb3d;}}
    }}
    .section-title-accent {{
      font-size:1.33em;
      font-weight:900;
      letter-spacing:1.3px;
      padding: 0 7px 0 0;
      display:inline-block;
      background:linear-gradient(92deg,#00eaff 21%,#ffb963 100%);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
      text-shadow:0 2px 19px #6b9db1ba;
      margin-bottom:7px;
    }}
    .glass-wrap {{
      background: rgba(41,51,92,0.89);
      border-radius:24px;
      box-shadow:0 10px 38px 6px #05d7ff19;
      margin:19px auto 12px auto;
      max-width:970px;
      padding:26px 33px 17px 28px;
      border:1.5px solid #ffcd683a;
      backdrop-filter: blur(8px) saturate(122%);
      transition: box-shadow 0.38s, transform 0.19s;
      perspective: 600px;
    }}
    .glass-wrap:hover {{
      box-shadow:0 0 66px 15px #00eaffcc,0 0 26px 9px #ffc34d30;
      transform: scale(1.018) rotateY(2.7deg) rotateX(1.5deg);
    }}
    .shimmer {{
      background: linear-gradient(90deg, #23294c 25%, #28356f 50%, #23294c 75%);
      background-size: 400% 100%;
      animation: shimmer 1.2s infinite;
      border-radius: 14px;
      height: 52px;
      margin:12px 0 9px 0;
    }}
    @keyframes shimmer {{
      0%   {{ background-position: -400px 0; }}
      100% {{ background-position: 400px 0; }}
    }}
    .avatar-ai {{
      border-radius:50%;
      box-shadow:0 0 36px 4px #17efe57a, 0 0 76px 0 #00ffa766;
      margin:9px auto 0 auto; display:block;
      border:3px solid #704ae8cc;
      width:95px; height:95px;
      background: linear-gradient(120deg,#0bf0e4 45%,#f6d54e 92%);
      animation: aiavatarfloat 2.6s ease-in-out infinite alternate;
      cursor: pointer;
    }}
    @keyframes aiavatarfloat {{
      0%   {{ transform: translateY(-8px) scale(1.01);  }}
      100% {{ transform: translateY(7.5px) scale(1.075); }}
    }}
    .ai-avatar-tooltip {{
      text-align:center;
      margin-top:7px;
      font-size:1em;
      color:#ffd666cc;
      letter-spacing:.7px;
    }}
    .footer-caption {{
      text-align:center;
      color:#ffe7bb;
      font-family:'Montserrat',sans-serif;
      font-size:1.09em;
      margin-top:13px;
      font-weight:500;
      letter-spacing:.2px;
    }}
    .footer-caption .ai-emoji {{
      animation: pulseaiemoji 2.7s infinite;
      font-size:1.22em;
      filter: drop-shadow(0 2px 6px #ffe965b9);
      margin-right:7px;
    }}
    @keyframes pulseaiemoji {{
      0% {{ scale:1; filter: drop-shadow(0 2px 6px #ffefbb85);}}
      100%{{ scale:1.10; filter: drop-shadow(0 5px 12px #ffeb9187);}}
    }}
    .stButton>button {{
      background:linear-gradient(90deg,#00eefe 17%,#ffba69 96%);
      color: #fff; border:none; border-radius:17px;
      font-size: 1.13em;font-weight:800;
      padding:12px 27px;
      margin-bottom:5px;margin-top:12px;cursor:pointer;
      box-shadow:0 0 18px 2px #00c3ff36;
      transition:box-shadow 0.195s, background 0.16s, transform 0.15s;
      outline:0;
      position:relative;
      overflow:hidden;
    }}
    .stButton>button:active {{
      background:linear-gradient(90deg,#ffc54d 4%,#01e5ff 93%);
      box-shadow:0 0 66px 11px #00d1ffd0;
      transform:scale(0.98);
    }}
    .user-bubble, .ai-bubble {{
      margin:12px 2px;padding:10px 20px;border-radius:18px;
      max-width:83%;display:inline-block;
      font-size:1.08em;line-height:1.54;
    }}
    .user-bubble {{background:#19fcdf33;color:#fffcc0;margin-left:26%;text-align:right;}}
    .ai-bubble   {{background:#4257fa2d;color:#ede6ff;}}
    .toast-pop {{
      position:fixed;bottom:35px;right:25px;
      background:linear-gradient(89deg,#1be7ba 6%,#ffde98 92%);
      color:#242433;box-shadow:0 8px 38px #32eeff5a;
      border-radius:12px;font-size:1.13em;padding:12px 26px;z-index:999;
      animation:toast-in .8s cubic-bezier(.24,1.22,.78,1) 1;
    }}
    @keyframes toast-in {{
      from {{transform:translateX(128px) scale(.7);opacity:0; }}
      to   {{transform:translateX(0) scale(1);opacity:1; }}
    }}
    .progress-glow {{
      margin:19px 0 13px 0;height:9px;
      background:linear-gradient(90deg,#16f1ff,#ffc661);
      border-radius:8px;box-shadow:0 0 17px 4px #19e6ffa9;
      position:relative;overflow:hidden;
    }}
    .progress-glow-bar {{
      width:0%;height:100%;
      animation:barprog 2.9s cubic-bezier(.25,.1,.37,1.52) infinite alternate;
      background:linear-gradient(90deg,#ffe969,#06fde9);
    }}
    @keyframes barprog {{
      0%{{width:22%;}}
      100%{{width:96%;}}
    }}
    details.adv-panel {{
      margin:14px 0 0 0;
      background: linear-gradient(98deg,#06cdfc14 2%,#ffc75a2c 94%);
      border-radius:17px;padding:15px 17px;
      box-shadow:0 2px 15px #0afcf218;
      border:1.2px solid #fbc05ac0;
      font-size:1.08em;
      color:#ffe29c;
      font-family:'Montserrat';
    }}
    summary.adv-title {{
      font-weight:900; font-size:1.09em; color:#fff6b5; letter-spacing:.7px; cursor:pointer;
    }}
    </style>
    """, unsafe_allow_html=True)

def add_emojis(text):
    emojis = {
        "title": "🤖", "generated_info": "📜", "translation": "🌍",
        "button": "🔄", "language": "🗣️", "creator": "💡"
    }
    for name, emoji in emojis.items():
        text = text.replace(f"{{{name}_emoji}}", emoji)
    return text

def get_language_code(lang_display):
    match = re.search(r"\(([^)]+)\)", lang_display)
    if match:
        return match.group(1).strip().lower()
    return "en"

def is_voice_supported(code):
    return code in tts_supported

def llama70b(history):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": history
    }
    try:
        r = requests.post(GROQ_URL, json=data, headers=headers, timeout=90)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        else:
            try: err = r.json()
            except Exception: err = r.text
            return f"Error: {err}"
    except Exception as e:
        return f"Exception: {e}"

def translate_text(text, code):
    try:
        result = translator.translate(text, dest=code.lower())
        return result.text
    except Exception as e:
        return f"Translation error: {e}"

def synthesize_speech(text, code):
    try:
        tts = gTTS(text=text, lang=code.lower())
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            audio_bytes = open(fp.name, "rb").read()
        os.unlink(fp.name)
        return audio_bytes
    except Exception as e:
        print(f"Voice error ({code}): {e}")
        return None

def fetch_pexels_video(query):
    if not PEXELS_API_KEY:
        return None
    headers = {'Authorization': PEXELS_API_KEY}
    params = {'query': query, 'per_page': 1}
    try:
        resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params, timeout=12)
        data = resp.json()
        if data.get('videos') and data['videos'][0]['video_files']:
            mp4s = [f for f in data['videos'][0]['video_files'] if f['file_type'] == 'video/mp4']
            if mp4s:
                mp4s.sort(key=lambda x: x['width'] * x['height'], reverse=True)
                return mp4s[0]['link']
    except Exception as e:
        print(f"Pexels video error: {e}")
    return None

def fetch_best_image(query):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    if PEXELS_API_KEY:
        headers = {"Authorization": PEXELS_API_KEY}
        try:
            r = requests.get(url, headers=headers, timeout=12)
            data = r.json()
            if data.get('photos'):
                return data['photos'][0]['src']['original']
        except Exception as e:
            print(f"Image error: {e}")
    if UNSPLASH_KEY:
        try:
            url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
            r = requests.get(url, timeout=12)
            data = r.json()
            return data.get('urls', {}).get('regular')
        except Exception as e:
            print(f"Unsplash image error: {e}")
    return None

def fetch_default_youtube(query):
    topics = {
        "python": "https://www.youtube.com/embed/rfscVS0vtbw",
        "artificial intelligence": "https://www.youtube.com/embed/2ePf9rue1Ao",
        "machine learning": "https://www.youtube.com/embed/IpGxLWOIZy4",
        "biology": "https://www.youtube.com/embed/BjX4fHq-v3g",
        "science": "https://www.youtube.com/embed/X1eGxJdPMu8",
        "mathematics": "https://www.youtube.com/embed/Trvv7bSHy9Y",
        "neural network": "https://www.youtube.com/embed/aircAruvnKk"
    }
    for k, v in topics.items():
        if k in query.lower():
            return v
    return "https://www.youtube.com/embed/0p2RV5q5hOs"

def get_geolocation():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=6)
        data = res.json()
        if "loc" in data:
            lat, lon = data["loc"].split(",")
            return float(lat), float(lon), data
    except Exception as e:
        print("Geolocation error", e)
    return None, None, {}

def show_live_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=12, control_scale=True)
    folium.Marker([lat, lon], popup="You are here", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, width=700, height=400)

def show_toast(msg, icon="✔️"):
    st.markdown(f"<div class='toast-pop'>{icon}&nbsp;{msg}</div>", unsafe_allow_html=True)

def main():
    add_custom_styles()
    col_ai, col_t = st.columns([1, 8])
    with col_ai:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/4712/4712102.png",
            width=95,
            output_format="PNG",
            caption="",
            use_container_width=False,
        )
        st.markdown('<div class="avatar-ai" title="AI Assistant"></div>', unsafe_allow_html=True)
        st.markdown('<div class="ai-avatar-tooltip">AI Assistant</div>', unsafe_allow_html=True)
    with col_t:
        st.markdown(
            f'<div class="title">{add_emojis("AI Multilanguage Assistant {title_emoji}")}'
            f'</div>', unsafe_allow_html=True)
        if LOTTIE_AVAILABLE:
            st_lottie("https://assets7.lottiefiles.com/packages/lf20_3rwasyjy.json", width=108, key="ai_lottie")
        st.markdown(
            f'<div class="ai-tips" id="animatedtip">{random.choice(TIP_LIST)}</div>',
            unsafe_allow_html=True
        )

    st.markdown('<span class="section-title-accent">🌍 Your Live Location on Google Map</span>', unsafe_allow_html=True)
    lat, lon, geoinfo = get_geolocation()
    if lat and lon:
        show_live_map(lat, lon)
        st.info(f"🔹 Your detected city: **{geoinfo.get('city','')} ({geoinfo.get('country','')})** | IP: {geoinfo.get('ip','')}")
    else:
        st.warning("Couldn't detect your location. You might be behind a VPN or firewall.")

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'query_history' not in st.session_state:
        st.session_state['query_history'] = []

    # --- ADDITION: "How can I help you?" chatbot welcome ---
    if len(st.session_state['chat_history']) == 0:
        welcome_msg = "Hello! 👋 How can I help you today?"
        st.session_state['chat_history'].append({"role": "assistant", "content": welcome_msg})

    st.markdown('<span class="section-title-accent">🤔 Ask the AI Any Question or Have a Chat</span>', unsafe_allow_html=True)
    with st.form("prompt-form", clear_on_submit=False):
        query = st.text_input("🔎 Enter your message for the chat AI:")
        language_select = st.selectbox("🌐 Choose language (voice/text):", ALL_LANGUAGE_CHOICES, index=0)
        submit = st.form_submit_button("✨ Send", use_container_width=True)

    code = get_language_code(language_select)
    can_voice = is_voice_supported(code)

    with st.sidebar:
        st.header("📚 Query History")
        for q in st.session_state['query_history'][-8:][::-1]:
            st.markdown(f"- {q}")
        st.write("---")
        st.markdown("<span style='color:#fdc55e'>[More settings coming soon]</span>", unsafe_allow_html=True)

    # Main Chat Logic
    if submit and query:
        st.session_state['query_history'].append(query)
        st.session_state['chat_history'].append({"role": "user", "content": query})
        st.markdown("""
        <div class="progress-glow">
            <div class="progress-glow-bar"></div>
        </div>
        """, unsafe_allow_html=True)
        with st.spinner("AI is thinking..."):
            st.markdown('<div class="shimmer"></div>', unsafe_allow_html=True)
            # Build conversation history for Groq
            convo = [{"role": e["role"], "content": e["content"]} for e in st.session_state["chat_history"]]
            ai_answer = llama70b(convo)
            st.session_state['chat_history'].append({"role": "assistant", "content": ai_answer})

            # These assets are generated for the last assistant response
            translation = translate_text(ai_answer, code)
            img_url = fetch_best_image(query)
            video_url = fetch_pexels_video(query)
            yt_url = fetch_default_youtube(query)
            st.session_state['last_translation'] = translation
            st.session_state['last_img'] = img_url
            st.session_state['last_video'] = video_url
            st.session_state['last_yt'] = yt_url

    # Render Full Chat
    for entry in st.session_state['chat_history']:
        msg_cls = "user-bubble" if entry['role'] == "user" else "ai-bubble"
        st.markdown(f'<div class="{msg_cls}">{entry["content"]}</div>', unsafe_allow_html=True)

    # Output Cards
    if st.session_state.get('chat_history') and any(e['role'] == 'assistant' for e in st.session_state['chat_history']):
        cp1, cp2 = st.columns(2)
        with cp1:
            if st.button("📋 Copy Last AI Answer", key="copyai", use_container_width=True):
                st.session_state['copyai'] = st.session_state['chat_history'][-1]['content']
                show_toast("Copied last answer!")
            if st.button("📋 Copy Last Translation", key="copytrans", use_container_width=True):
                st.session_state['copytrans'] = st.session_state.get('last_translation', '')
                show_toast("Copied last translation!")
            last_ai = [e for e in st.session_state['chat_history'] if e['role'] == 'assistant']
            if last_ai:
                translation = st.session_state.get('last_translation', translate_text(last_ai[-1]['content'], code))
                st.markdown(
                    f"""<div class="glass-wrap translations">
                    <span class="language-caption">{add_emojis("{language_emoji}")} {translator_supported.get(code, code.upper())}</span><br>
                    <span style="font-size:1.07em;line-height:1.53;">{translation}</span></div>""",
                    unsafe_allow_html=True)
                if can_voice:
                    st.markdown('<div class="voice-glow">🔊 Voice Output (Play Below):</div>', unsafe_allow_html=True)
                    audio = synthesize_speech(translation, code)
                    if audio:
                        st.audio(audio, format='audio/mp3')
                    else:
                        st.info("Sorry, there was a problem generating voice for this text/language.")
                else:
                    st.info("Sorry, voice not available for this language.")
            st.markdown('<span class="section-title-accent">🎬 Related Video / Animation</span>', unsafe_allow_html=True)
            video_url = st.session_state.get('last_video')
            yt_url = st.session_state.get('last_yt')
            if video_url:
                st.video(video_url)
            elif yt_url:
                st.video(yt_url)
        with cp2:
            img_url = st.session_state.get('last_img')
            if img_url:
                st.image(img_url, caption="Related image", use_container_width=True)
            else:
                st.info("No related image found for your query.")

    st.markdown("""
    <details class="adv-panel">
        <summary class="adv-title">Advanced & Extras</summary>
        <ul>
            <li>🚀 <b>Tip</b>: Try rich, scientific, historic and language learning prompts.</li>
            <li>🦾 <b>Coming soon</b>: Theme switch, AI avatar emotions, even more media sources, and analytics!</li>
        </ul>
    </details>
    """, unsafe_allow_html=True)

    st.markdown(
        '''<div class="footer-caption">
            <span class="ai-emoji">🤖</span>
            Made with by Raghavendra N | Bright Minds Academy<br>
            <span>Contact: <a style="color:#ffe28c" href="mailto:info@brightmindsacademy.com">info@brightmindsacademy.com</a></span>
        </div>''',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
