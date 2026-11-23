"""
app.py — Streamlit frontend for the FastAPI Auth + RBAC backend.

Run with:
    streamlit run frontend/app.py
"""

import streamlit as st
import api  # our helper module that talks to FastAPI

# ──────────────────────────────────────────────
# Page config (must be first Streamlit command)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Auth & RBAC Dashboard",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="auto",
)

# ──────────────────────────────────────────────
# Custom CSS for a modern look
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ---------- colour variables ---------- */
:root {
    --primary: #4F46E5;
    --primary-light: #6366F1;
    --success: #059669;
    --danger: #DC2626;
    --bg-card: #F8FAFC;
    --border: #E2E8F0;
    --text-muted: #64748B;
}

/* ---------- global tweaks ---------- */
.block-container { max-width: 860px; padding-top: 2rem; }

/* ---------- reusable card ---------- */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ---------- hero header ---------- */
.hero {
    text-align: center;
    padding: 2rem 0 1rem;
}
.hero h1 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 0.25rem;
}
.hero p {
    color: var(--text-muted);
    font-size: 1.05rem;
}

/* ---------- status badges ---------- */
.badge {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}
.badge-green  { background: #D1FAE5; color: #065F46; }
.badge-red    { background: #FEE2E2; color: #991B1B; }
.badge-blue   { background: #DBEAFE; color: #1E40AF; }
.badge-purple { background: #EDE9FE; color: #5B21B6; }

/* ---------- info row ---------- */
.info-row {
    display: flex;
    justify-content: space-between;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.95rem;
}
.info-row:last-child { border-bottom: none; }
.info-label { font-weight: 600; color: #334155; }
.info-value { color: #475569; }

/* ---------- section heading ---------- */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1E293B;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid var(--primary);
    display: inline-block;
}

/* ---------- sidebar styling ---------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4F46E5 0%, #6366F1 100%);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown label {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Session-state helpers
# ──────────────────────────────────────────────
def _init_state():
    """Ensure all keys exist in session_state so we never get KeyError."""
    defaults = {
        "token": None,
        "user": None,           # UserPublic dict from /users/me
        "page": "login",        # "login" | "register" | "dashboard"
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


def is_logged_in() -> bool:
    return st.session_state.token is not None and st.session_state.user is not None


def is_admin() -> bool:
    return is_logged_in() and st.session_state.user.get("role") == "admin"


def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.page = "login"


def _refresh_profile():
    """Re-fetch /users/me. If the token is invalid/expired, log out."""
    ok, data = api.get_current_user(st.session_state.token)
    if ok:
        st.session_state.user = data
    else:
        logout()
        st.warning("Session expired. Please log in again.")


# ──────────────────────────────────────────────
# LOGIN PAGE
# ──────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div class="hero">
        <h1>🔐 Auth & RBAC</h1>
        <p>Sign in to access your dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Login")

        username = st.text_input("Username or Email", key="login_user", placeholder="Enter your username or email")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

        col1, col2 = st.columns([1, 1])
        with col1:
            login_btn = st.button("🔑  Log In", use_container_width=True, type="primary")
        with col2:
            reg_btn = st.button("📝  Create Account", use_container_width=True)

        if login_btn:
            if not username or not password:
                st.error("Please fill in both fields.")
            else:
                with st.spinner("Authenticating…"):
                    ok, data = api.login_user(username, password)
                if ok:
                    st.session_state.token = data["access_token"]
                    # Immediately fetch the full profile
                    ok2, profile = api.get_current_user(st.session_state.token)
                    if ok2:
                        st.session_state.user = profile
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error(f"Login succeeded but profile fetch failed: {profile}")
                else:
                    st.error(f"Login failed: {data}")

        if reg_btn:
            st.session_state.page = "register"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# REGISTRATION PAGE
# ──────────────────────────────────────────────
def show_register():
    st.markdown("""
    <div class="hero">
        <h1>📝 Create Account</h1>
        <p>Register a new user account</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Registration")

        username = st.text_input("Username", key="reg_user", placeholder="At least 3 characters")
        email    = st.text_input("Email", key="reg_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="reg_pass", placeholder="At least 6 characters")
        confirm  = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Re-enter your password")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit_btn = st.button("✅  Register", use_container_width=True, type="primary")
        with col2:
            back_btn = st.button("⬅  Back to Login", use_container_width=True)

        if submit_btn:
            # client-side validation
            if not username or not email or not password or not confirm:
                st.error("All fields are required.")
            elif len(username) < 3:
                st.error("Username must be at least 3 characters.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                with st.spinner("Creating your account…"):
                    ok, data = api.register_user(username, email, password)
                if ok:
                    st.success(f"Account created for **{data['username']}**! You can now log in.")
                    st.balloons()
                else:
                    st.error(f"Registration failed: {data}")

        if back_btn:
            st.session_state.page = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# SIDEBAR (shown only when logged in)
# ──────────────────────────────────────────────
def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown("## 🔐 Auth & RBAC")
        st.markdown("---")
        st.markdown(f"**👤 {user['username']}**")
        role_emoji = "👑" if user["role"] == "admin" else "🙋"
        st.markdown(f"{role_emoji} Role: `{user['role']}`")
        st.markdown("---")

        st.markdown("### Navigation")
        if st.button("🏠  Dashboard", use_container_width=True):
            st.session_state.dash_tab = "profile"
            st.rerun()

        if is_admin():
            if st.button("⚙️  Admin Panel", use_container_width=True):
                st.session_state.dash_tab = "admin"
                st.rerun()

        st.markdown("---")
        if st.button("🚪  Logout", use_container_width=True):
            logout()
            st.rerun()


# ──────────────────────────────────────────────
# USER DASHBOARD
# ──────────────────────────────────────────────
def show_user_dashboard():
    user = st.session_state.user

    # Welcome banner
    st.markdown(f"""
    <div class="card" style="background:linear-gradient(135deg,#4F46E5,#6366F1);color:white;text-align:center;">
        <h2 style="margin:0;color:white;">Welcome back, {user['username']}! 👋</h2>
        <p style="margin:0.3rem 0 0;opacity:0.9;">Your personal dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("User ID", f"#{user['id']}")
    with col2:
        role_display = "Admin 👑" if user["role"] == "admin" else "User 🙋"
        st.metric("Role", role_display)
    with col3:
        status_display = "Active ✅" if user["is_active"] else "Inactive ❌"
        st.metric("Status", status_display)

    # Profile card
    st.markdown('<p class="section-title">📋 Profile Details</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        <div class="info-row"><span class="info-label">User ID</span><span class="info-value">#{user['id']}</span></div>
        <div class="info-row"><span class="info-label">Username</span><span class="info-value">{user['username']}</span></div>
        <div class="info-row"><span class="info-label">Email</span><span class="info-value">{user['email']}</span></div>
        <div class="info-row">
            <span class="info-label">Role</span>
            <span class="info-value"><span class="badge {'badge-purple' if user['role']=='admin' else 'badge-blue'}">{user['role']}</span></span>
        </div>
        <div class="info-row">
            <span class="info-label">Account Status</span>
            <span class="info-value"><span class="badge {'badge-green' if user['is_active'] else 'badge-red'}">{'Active' if user['is_active'] else 'Inactive'}</span></span>
        </div>
        <div class="info-row">
            <span class="info-label">Authentication</span>
            <span class="info-value"><span class="badge badge-green">Authenticated ✓</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Actions
    st.markdown('<p class="section-title">⚡ Actions</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🔒  Fetch Protected Content", use_container_width=True, type="primary"):
            with st.spinner("Requesting…"):
                ok, data = api.get_protected(st.session_state.token)
            if ok:
                st.success(data.get("message", str(data)))
            else:
                if "credentials" in str(data).lower() or "expired" in str(data).lower():
                    logout()
                    st.warning("Session expired. Redirecting to login…")
                    st.rerun()
                else:
                    st.error(data)

    with col_b:
        if st.button("🔄  Refresh Profile", use_container_width=True):
            with st.spinner("Refreshing…"):
                _refresh_profile()
            if is_logged_in():
                st.success("Profile refreshed.")
                st.rerun()


# ──────────────────────────────────────────────
# ADMIN DASHBOARD
# ──────────────────────────────────────────────
def show_admin_dashboard():
    user = st.session_state.user
    token = st.session_state.token

    st.markdown(f"""
    <div class="card" style="background:linear-gradient(135deg,#7C3AED,#A78BFA);color:white;text-align:center;">
        <h2 style="margin:0;color:white;">Admin Panel 👑</h2>
        <p style="margin:0.3rem 0 0;opacity:0.9;">Welcome, {user['username']} — you have full administrative access.</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch admin greeting from backend
    st.markdown('<p class="section-title">🛡️ Admin Verification</p>', unsafe_allow_html=True)
    if st.button("📡  Verify Admin Access", use_container_width=True):
        with st.spinner("Checking…"):
            ok, data = api.get_admin(token)
        if ok:
            st.success(data.get("message", str(data)))
        else:
            st.error(data)

    # Users table
    st.markdown('<p class="section-title">👥 Registered Users</p>', unsafe_allow_html=True)

    if st.button("🔄  Load / Refresh Users", use_container_width=True, type="primary"):
        with st.spinner("Fetching user list…"):
            ok, data = api.get_all_users(token)
        if ok:
            st.session_state["admin_users"] = data
        else:
            if "privileges" in str(data).lower():
                st.error("Your account does not have admin privileges.")
            else:
                st.error(data)

    users_data = st.session_state.get("admin_users")
    if users_data:
        st.metric("Total Users", len(users_data))

        # Build a clean table
        import pandas as pd
        df = pd.DataFrame(users_data)
        df = df[["id", "username", "email", "role", "is_active"]]
        df.columns = ["ID", "Username", "Email", "Role", "Active"]
        df["Active"] = df["Active"].map({True: "✅ Yes", False: "❌ No"})
        df["Role"]   = df["Role"].apply(lambda r: f"👑 {r}" if r == "admin" else f"🙋 {r}")

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Click **Load / Refresh Users** to fetch the user list from the backend.")


# ──────────────────────────────────────────────
# MAIN ROUTER
# ──────────────────────────────────────────────
def main():
    # If logged in, show sidebar + dashboard
    if is_logged_in():
        show_sidebar()

        # Determine which tab to show
        if "dash_tab" not in st.session_state:
            st.session_state.dash_tab = "profile"

        tab = st.session_state.dash_tab

        if tab == "admin" and is_admin():
            show_admin_dashboard()
        elif tab == "admin" and not is_admin():
            st.error("You do not have admin privileges.")
            show_user_dashboard()
        else:
            show_user_dashboard()

    else:
        # Not logged in — show login or register
        page = st.session_state.page
        if page == "register":
            show_register()
        else:
            show_login()


if __name__ == "__main__":
    main()
