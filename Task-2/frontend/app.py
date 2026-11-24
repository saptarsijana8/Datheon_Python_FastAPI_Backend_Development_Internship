"""
Streamlit frontend for the FastAPI JWT Authentication + RBAC project.

Run from the Task-2 directory:
    streamlit run frontend/app.py
"""

import html
import json
import streamlit as st
import api

st.set_page_config(
    page_title="Auth & RBAC",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background:
      radial-gradient(ellipse at 8% 8%, rgba(112,45,210,.22), transparent 28%),
      radial-gradient(ellipse at 92% 78%, rgba(137,54,225,.18), transparent 30%),
      #080711;
    color: #f5f2ff;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1280px; padding-top: 1.2rem; padding-bottom: 2rem; }
.st-key-auth_panel {
    max-width: 760px; margin: 1rem auto 0; padding: 1.7rem 2.2rem 1.5rem;
    background: linear-gradient(145deg,rgba(34,27,48,.94),rgba(13,11,21,.97));
    border: 1px solid rgba(181,132,235,.62); border-radius: 21px;
    box-shadow: 0 24px 90px rgba(92,35,170,.18), inset 0 1px rgba(255,255,255,.04);
}
.st-key-auth_panel h1, .st-key-auth_panel h2, .st-key-auth_panel h3 { font-size: 1.35rem !important; letter-spacing: -.3px !important; }
.st-key-auth_panel label, .st-key-auth_panel [data-testid="stMarkdownContainer"] p { font-size: .88rem; }
.st-key-auth_panel [data-testid="stTextInput"] input { min-height: 42px; font-size: .9rem; }
.st-key-auth_panel .stButton > button { min-height: 42px; font-size: .92rem; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#6520c8 0%,#47139c 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
h1,h2,h3,p,label { color: #f6f3ff; }
h1 { font-weight: 800 !important; letter-spacing: -1.5px; }
[data-testid="stTextInput"] input {
    background: rgba(20,17,34,.88); color: #f8f5ff;
    border: 1px solid #514568; border-radius: 12px; min-height: 48px;
}
[data-testid="stTextInput"] input:focus {
    border-color: #a56aff; box-shadow: 0 0 0 1px #a56aff;
}
.stButton > button {
    border-radius: 12px; min-height: 46px; font-weight: 650;
    border: 1px solid #8151cb; background: rgba(28,22,44,.9);
    color: #eee6ff; transition: all .2s ease;
}
.stButton > button:hover { border-color: #c08aff; color: white; transform: translateY(-1px); }
.stButton > button[kind="primary"] {
    background: linear-gradient(100deg,#7139ed,#ae4ff0);
    border: 0; color: white;
}
.auth-heading { text-align:center; margin-bottom:1rem; }
.auth-icon { font-size:1.75rem; color:#a96bff; line-height:1.2; }
.auth-title {
    font-size: clamp(2rem,3.5vw,2.75rem); font-weight:800; letter-spacing:-1.2px;
    line-height:1.08; background:linear-gradient(90deg,#8150ff,#d06aff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:.25rem 0;
}
.auth-subtitle { color:#b8a9d0; font-size:.95rem; }
.notice {
    padding: .72rem .9rem; background:#f6f3ff; color:#191326;
    border-radius:11px; margin:.8rem 0 1rem; font-weight:500; font-size:.88rem;
}
.notice span { color:#7540df; font-weight:800; margin-right:.5rem; }
.panel {
    background:linear-gradient(145deg,rgba(31,25,47,.96),rgba(17,15,27,.98));
    border:1px solid #392b55; border-radius:20px; padding:1.35rem 1.5rem;
    min-height:145px; box-shadow:0 12px 35px rgba(0,0,0,.14);
}
.panel-label { color:#a99cbe; font-size:.9rem; margin-bottom:.8rem; }
.panel-value { color:#fff; font-size:1.65rem; font-weight:800; }
.panel-note { color:#7f7692; font-size:.85rem; margin-top:.45rem; }
.hero {
    padding:2rem 2.2rem; border-radius:25px;
    background:linear-gradient(110deg,#7134e5,#a44ef0);
    box-shadow:0 18px 50px rgba(111,48,210,.22); margin-bottom:1.2rem;
}
.hero-kicker { letter-spacing:3px; font-size:.8rem; font-weight:800; opacity:.82; }
.hero h1 { color:white !important; font-size:clamp(1.8rem,4vw,3rem); margin:.4rem 0; }
.hero p { color:#f1e7ff; margin:0; font-size:1.05rem; }
.pill {
    display:inline-block; border-radius:999px; padding:.45rem .85rem;
    margin:.8rem .35rem 0 0; background:rgba(53,20,112,.45);
    color:white; font-size:.82rem; font-weight:650;
}
.section-heading { font-size:1.25rem; font-weight:800; margin:1.3rem 0 .8rem; }
.profile-card {
    background:#fbfaff; color:#171329; border-radius:20px; padding:1.5rem 1.7rem;
}
.profile-card h3 { color:#171329 !important; margin-top:0; }
.profile-row {
    display:flex; justify-content:space-between; gap:1rem; padding:.9rem 0;
    border-bottom:1px solid #ece8f3; color:#77718a;
}
.profile-row:last-child { border-bottom:0; }
.profile-row strong { color:#19152b; text-align:right; overflow-wrap:anywhere; }
.token-card {
    background:linear-gradient(145deg,#191525,#11101b);
    border:1px solid #3b2c55; border-radius:20px; padding:1.5rem;
}
.token-preview {
    padding:1rem; margin:.9rem 0; border:1px solid #352b49;
    background:#211d2d; border-radius:13px; color:#d7c8f2;
    font-family:monospace; overflow-wrap:anywhere; font-size:.83rem;
}
div[data-testid="stAlert"] { border-radius:12px; }
footer { visibility:hidden; }
@media(max-width:700px) {
 .st-key-auth_panel { padding:1.25rem 1.1rem 1rem; margin-top:.35rem; }
 .auth-title { font-size:2rem; }
 .auth-subtitle { font-size:.85rem; }
 .block-container { padding:1rem; }
 .hero { padding:1.4rem; }
}
</style>
""", unsafe_allow_html=True)


# ---------- Session state ----------
def init_state():
    defaults = {
        "token": None,
        "user": None,
        "page": "login",
        "dash_tab": "profile",
        "show_token": False,
        "admin_users": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_logged_in():
    return bool(st.session_state.token and st.session_state.user)


def is_admin():
    return is_logged_in() and st.session_state.user.get("role") == "admin"


def logout():
    for key, value in {
        "token": None, "user": None, "page": "login",
        "dash_tab": "profile", "show_token": False, "admin_users": None,
    }.items():
        st.session_state[key] = value


def refresh_profile():
    ok, data = api.get_current_user(st.session_state.token)
    if ok:
        st.session_state.user = data
        return True
    logout()
    return False


def auth_header(title, subtitle, icon):
    st.markdown(f"""
    <div class="auth-heading">
      <div class="auth-icon">{icon}</div>
      <div class="auth-title">{title}</div>
      <div class="auth-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# ---------- Login ----------
def show_login():
    # Keep all widgets inside one real Streamlit container so the card
    # background, border and spacing wrap the complete form.
    left, center, right = st.columns([1, 2.25, 1])
    with center:
        with st.container(key="auth_panel"):
            auth_header("Auth &amp; RBAC", "Sign in to access your dashboard", "🔒")
            st.markdown(
                '<div class="notice"><span>ⓘ</span> Secure authentication with JWT &amp; role-based access control</div>',
                unsafe_allow_html=True,
            )
            st.markdown("### Login")
            username = st.text_input(
                "Username or Email",
                placeholder="Enter your username or email",
                key="login_user",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_pass",
            )
            remember_col, forgot_col = st.columns([1, 1])
            with remember_col:
                remember = st.checkbox(
                    "Remember me",
                    value=False,
                    help="This demo keeps your login for the current Streamlit session.",
                )
            with forgot_col:
                st.markdown(
                    '<p style="text-align:right;color:#a879ff;font-size:.84rem;padding-top:.25rem;">Forgot password?</p>',
                    unsafe_allow_html=True,
                )
            login_col, register_col = st.columns(2)
            with login_col:
                login_clicked = st.button("Log In", type="primary", use_container_width=True)
            with register_col:
                register_clicked = st.button("Create Account", use_container_width=True)

            if register_clicked:
                st.session_state.page = "register"
                st.rerun()

            if login_clicked:
                if not username.strip() or not password:
                    st.error("Please enter both your username/email and password.")
                else:
                    with st.spinner("Authenticating securely..."):
                        ok, data = api.login_user(username.strip(), password)
                    if ok:
                        token = data.get("access_token")
                        ok_profile, profile = api.get_current_user(token)
                        if ok_profile:
                            st.session_state.token = token
                            st.session_state.user = profile
                            st.session_state.page = "dashboard"
                            st.session_state.show_token = False
                            st.rerun()
                        else:
                            st.error(f"Login succeeded, but the profile could not be loaded: {profile}")
                    else:
                        st.error(f"Login failed: {data}")


# ---------- Registration ----------
def show_register():
    left, center, right = st.columns([1, 2.25, 1])
    with center:
        with st.container(key="auth_panel"):
            auth_header("Create Account", "Register a new user account", "▤")
            st.markdown(
                '<div class="notice"><span>ⓘ</span><b>Registration</b> &nbsp; Please complete all fields to create your account securely.</div>',
                unsafe_allow_html=True,
            )
            st.markdown("### Registration")
            username = st.text_input("Username", placeholder="At least 3 characters", key="reg_user")
            email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
            password = st.text_input(
                "Password", type="password",
                placeholder="At least 6 characters", key="reg_pass",
            )
            confirm = st.text_input(
                "Confirm Password", type="password",
                placeholder="Re-enter your password", key="reg_confirm",
            )
            if password:
                score = sum([
                    len(password) >= 8,
                    any(c.isupper() for c in password),
                    any(c.islower() for c in password),
                    any(c.isdigit() for c in password),
                    any(not c.isalnum() for c in password),
                ])
                label = "Weak" if score <= 2 else "Moderate" if score <= 3 else "Strong"
                st.caption(f"Password strength: {label}")
                st.progress(score / 5)

            st.caption(
                "New accounts receive the standard User role. Admin access is provisioned separately."
            )
            register_col, back_col = st.columns(2)
            with register_col:
                register_clicked = st.button("Register", type="primary", use_container_width=True)
            with back_col:
                back_clicked = st.button("Back to Login", use_container_width=True)

            if back_clicked:
                st.session_state.page = "login"
                st.rerun()

            if register_clicked:
                if not all([username.strip(), email.strip(), password, confirm]):
                    st.error("All fields are required.")
                elif len(username.strip()) < 3:
                    st.error("Username must contain at least 3 characters.")
                elif len(password) < 6:
                    st.error("Password must contain at least 6 characters.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating your account..."):
                        ok, data = api.register_user(username.strip(), email.strip(), password)
                    if ok:
                        st.success(
                            f"Account created for {data.get('username', username)}. You can now log in."
                        )
                        st.session_state.page = "login"
                    else:
                        st.error(f"Registration failed: {data}")

            st.markdown(
                '<p style="text-align:center;color:#988ba9;font-size:.76rem;margin:.8rem 0 0;">🔒 Secured with JWT · RBAC access control</p>',
                unsafe_allow_html=True,
            )


# ---------- Sidebar ----------
def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown("## 🔐 Auth & RBAC")
        st.caption("SECURE WORKSPACE")
        st.markdown("---")
        st.markdown(f"### {html.escape(user.get('username', 'User'))}")
        st.caption(user.get("email", ""))
        st.markdown(f"**🛡️ {user.get('role', 'user').title()} Role**")
        st.markdown("---")
        st.markdown("### NAVIGATION")
        if st.button("▦  Dashboard", use_container_width=True):
            st.session_state.dash_tab = "profile"
            st.rerun()
        if is_admin() and st.button("⚙️  Admin Panel", use_container_width=True):
            st.session_state.dash_tab = "admin"
            st.rerun()
        st.markdown("---")
        if st.button("↪  Logout", use_container_width=True):
            logout()
            st.rerun()


# ---------- Dashboard ----------
def show_dashboard():
    user = st.session_state.user
    safe_name = html.escape(str(user.get("username", "User")))
    safe_email = html.escape(str(user.get("email", "")))
    role = str(user.get("role", "user"))
    active = bool(user.get("is_active", False))
    st.markdown(f"""
    <div class="hero">
      <div class="hero-kicker">AUTHENTICATED SESSION</div>
      <h1>Welcome back, {safe_name}! 👋</h1>
      <p>Your personal dashboard</p>
      <span class="pill">✓ JWT verified</span>
      <span class="pill">✓ RBAC enabled</span>
      <span class="pill">● Session active</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="panel"><div class="panel-label">User ID</div><div class="panel-value">#{user.get("id", "—")}</div><div class="panel-note">Unique account identifier</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="panel"><div class="panel-label">Role</div><div class="panel-value">{html.escape(role.title())}</div><div class="panel-note">{"Administrative access" if role == "admin" else "Standard access"}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="panel"><div class="panel-label">Status</div><div class="panel-value" style="color:{"#49d6ae" if active else "#ff7777"}">● {"Active" if active else "Inactive"}</div><div class="panel-note">Account standing</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Account overview</div>', unsafe_allow_html=True)
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown(f"""
        <div class="profile-card">
          <h3>Profile Details <span style="float:right;color:#7540df;font-size:.8rem;">✓ Verified</span></h3>
          <div class="profile-row"><span>User ID</span><strong>#{user.get("id", "—")}</strong></div>
          <div class="profile-row"><span>Username</span><strong>{safe_name}</strong></div>
          <div class="profile-row"><span>Email</span><strong>{safe_email}</strong></div>
          <div class="profile-row"><span>Role</span><strong>{html.escape(role.title())}</strong></div>
          <div class="profile-row"><span>Account Status</span><strong>{"Active" if active else "Inactive"}</strong></div>
          <div class="profile-row"><span>Authentication</span><strong>Authenticated ✓</strong></div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        token = st.session_state.token or ""
        preview = token if st.session_state.show_token else (token[:28] + "..." + token[-12:] if len(token) > 45 else "•" * 24)
        st.markdown("""
        <div class="token-card">
          <h3>🔑 JWT Access Token</h3>
          <p style="color:#a79bb9;font-size:.9rem;">Token issued by the FastAPI backend for this authenticated session.</p>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="token-preview">{html.escape(preview)}</div>', unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            if st.button("Show / Hide Token", use_container_width=True):
                st.session_state.show_token = not st.session_state.show_token
                st.rerun()
        with t2:
            if st.button("Copy Token", use_container_width=True):
                st.code(token, language=None)
                st.info("Select and copy the token above. Avoid sharing it with anyone.")
        with st.expander("View token payload"):
            try:
                import base64
                payload_part = token.split(".")[1]
                payload_part += "=" * (-len(payload_part) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_part.encode()).decode())
                st.json(payload)
            except Exception:
                st.caption("The token payload could not be decoded in the browser.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Quick actions</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        if st.button("🔒  Test Protected Route", type="primary", use_container_width=True):
            ok, data = api.get_protected(st.session_state.token)
            if ok:
                st.success(data.get("message", str(data)))
            else:
                st.error(data)
    with b:
        if st.button("↻  Refresh Profile", use_container_width=True):
            if refresh_profile():
                st.success("Profile refreshed.")
                st.rerun()
            st.warning("Your session expired. Please log in again.")
            st.rerun()
    with c:
        if st.button("↪  Logout", use_container_width=True):
            logout()
            st.rerun()

    if is_admin():
        st.markdown('<div class="section-heading">Administrator tools</div>', unsafe_allow_html=True)
        if st.button("Verify Admin Access"):
            ok, data = api.get_admin(st.session_state.token)
            st.success(data.get("message", str(data))) if ok else st.error(data)
        if st.button("Load Registered Users"):
            ok, data = api.get_all_users(st.session_state.token)
            if ok:
                st.session_state.admin_users = data
            else:
                st.error(data)
        if st.session_state.admin_users is not None:
            st.dataframe(st.session_state.admin_users, use_container_width=True, hide_index=True)


def main():
    init_state()
    if is_logged_in():
        show_sidebar()
        show_dashboard()
    elif st.session_state.page == "register":
        show_register()
    else:
        show_login()


if __name__ == "__main__":
    main()
