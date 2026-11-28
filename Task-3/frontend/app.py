"""Streamlit dashboard for the Users & Notes API.

All data comes from the FastAPI backend over HTTP (see api_client.py).
This file never touches the database directly.
"""

import html
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import streamlit as st

from api_client import DEFAULT_BASE_URL, APIClient, APIError

st.set_page_config(page_title="Notes Manager", page_icon="📝", layout="wide")

PAGES = {"Dashboard": "🏠  Dashboard", "Users": "👥  Users", "Notes": "📝  Notes"}
PALETTE = ["#6366F1", "#EC4899", "#14B8A6", "#F59E0B", "#8B5CF6", "#10B981", "#EF4444", "#0EA5E9"]
PREVIEW_LENGTH = 220
NOTES_PER_PAGE = 12
SORT_NOTES = ["Newest first", "Oldest first", "Recently edited", "Title A–Z"]

# Colours are semi-transparent greys so the design works in both light and dark mode.
CSS = """
.block-container {max-width: 1200px; padding-top: 2rem;}
footer {visibility: hidden;}
.hero {background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 55%, #EC4899 100%); color: #fff;
  padding: 1.8rem 2.2rem; border-radius: 20px; margin-bottom: 1.4rem; box-shadow: 0 10px 30px rgba(99,102,241,.28);}
.hero h1 {color: #fff !important; margin: 0; padding: 0; font-size: 2.1rem;}
.hero p {margin: .4rem 0 0; opacity: .92; font-size: 1.05rem;}
.stat {display: flex; align-items: center; gap: 1rem; padding: 1.1rem 1.3rem; border-radius: 16px;
  background: rgba(127,127,127,.08); border: 1px solid rgba(127,127,127,.2);}
.stat-icon {width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.6rem;}
.stat-value {font-size: 1.9rem; font-weight: 800; line-height: 1.1;}
.stat-label {opacity: .7; font-size: .9rem;}
[class*="st-key-card_"] {border: 1px solid rgba(127,127,127,.25); border-radius: 16px; padding: 1rem 1.15rem;
  background: rgba(127,127,127,.06); transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;}
[class*="st-key-card_"]:hover {transform: translateY(-3px); box-shadow: 0 8px 22px rgba(0,0,0,.14); border-color: #6366F1;}
.accent {height: 5px; border-radius: 99px; margin-bottom: .8rem;}
.note-title {font-size: 1.12rem; font-weight: 700; margin-bottom: .35rem; word-break: break-word;}
.note-body {opacity: .85; line-height: 1.5; margin-bottom: .8rem; word-break: break-word;}
.muted {opacity: .5; font-style: italic;}
.note-meta {display: flex; align-items: center; gap: .45rem; font-size: .82rem; opacity: .8; flex-wrap: wrap;}
.avatar {border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: #fff; font-weight: 700; flex-shrink: 0;}
.badge {background: rgba(99,102,241,.16); color: #6366F1; padding: 2px 10px; border-radius: 999px; font-size: .75rem; font-weight: 700;}
.user-head {display: flex; align-items: center; gap: .8rem; margin-bottom: .7rem;}
.user-name {font-weight: 700; font-size: 1.1rem;}
.user-sub {opacity: .65; font-size: .85rem; word-break: break-all;}
.empty {text-align: center; padding: 2.6rem 1rem; border: 2px dashed rgba(127,127,127,.35); border-radius: 18px; margin: .5rem 0 1rem;}
.empty .big {font-size: 2.6rem;}
.empty .title {font-size: 1.15rem; font-weight: 700; margin-top: .3rem;}
.empty .sub {opacity: .65;}
.brand {font-size: 1.35rem; font-weight: 800; margin-bottom: .8rem;}
.status {display: inline-flex; align-items: center; gap: .45rem; font-size: .82rem; padding: 3px 12px; border-radius: 999px; background: rgba(16,185,129,.15); color: #10B981; font-weight: 600;}
.status::before {content: ""; width: 8px; height: 8px; border-radius: 50%; background: #10B981;}
.stButton > button, .stLinkButton > a {border-radius: 10px; font-weight: 600; transition: transform .1s ease;}
.stButton > button:hover {transform: translateY(-1px);}
"""


@dataclass
class Ctx:
    """Everything a page needs: the API client and the data fetched for this run."""

    client: APIClient
    users: list[dict]
    notes: list[dict]
    owners: dict[int, dict] = field(init=False)

    def __post_init__(self) -> None:
        self.owners = {u["id"]: u for u in self.users}

    def owner_name(self, user_id: int) -> str:
        return self.owners.get(user_id, {}).get("username", "unknown")


# ---------- helpers ----------
def esc(text: Any) -> str:
    """Escape user text for safe use inside HTML (and stop '$' from turning into LaTeX)."""
    return html.escape(str(text)).replace("$", "&#36;").replace("\n", "<br>")


def flash(kind: str, message: str) -> None:
    """Queue a toast that is shown after the st.rerun() that follows a successful action."""
    st.session_state["flash"] = (kind, message)


def show_flash() -> None:
    kind, message = st.session_state.pop("flash", (None, None))
    if kind:
        st.toast(message, icon={"success": "✅", "error": "❌", "info": "ℹ️"}[kind])


def attempt(action: Callable[..., Any], *args: Any) -> tuple[bool, Any]:
    """Run an API call. On failure show the error and return (False, None)."""
    try:
        return True, action(*args)
    except APIError as exc:
        st.error(exc.message)
        return False, None


def go(page: str) -> None:
    st.session_state["page"] = page


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def time_ago(value: str) -> str:
    seconds = int((datetime.now(timezone.utc).replace(tzinfo=None) - parse_time(value)).total_seconds())
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60} min ago"
    if seconds < 86400:
        return f"{seconds // 3600} h ago"
    if seconds < 7 * 86400:
        return f"{seconds // 86400} d ago"
    return parse_time(value).strftime("%d %b %Y")


def is_edited(note: dict) -> bool:
    return (parse_time(note["updated_at"]) - parse_time(note["created_at"])).total_seconds() > 1


def user_label(user: dict) -> str:
    return f"{user['username']} ({user['email']})"


def avatar(name: str, user_id: int, size: int = 38) -> str:
    color = PALETTE[user_id % len(PALETTE)]
    letters = esc(name.strip()[:2].upper() or "?")
    return (
        f'<span class="avatar" style="width:{size}px;height:{size}px;background:{color};'
        f'font-size:{size * 0.4:.0f}px">{letters}</span>'
    )


def stat_card(icon: str, value: Any, label: str, color: str) -> str:
    return (
        f'<div class="stat"><div class="stat-icon" style="background:{color}26;color:{color}">{icon}</div>'
        f'<div><div class="stat-value">{value}</div><div class="stat-label">{label}</div></div></div>'
    )


def empty_state(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="empty"><div class="big">{icon}</div><div class="title">{esc(title)}</div>'
        f'<div class="sub">{esc(subtitle)}</div></div>',
        unsafe_allow_html=True,
    )


def note_html(note: dict, ctx: Ctx) -> str:
    owner_id = note["user_id"]
    content = note["content"]
    shown = content if len(content) <= PREVIEW_LENGTH else content[:PREVIEW_LENGTH].rstrip() + "…"
    body = f'<div class="note-body">{esc(shown)}</div>' if shown else '<div class="note-body muted">No content</div>'
    edited = '<span class="badge">edited</span>' if is_edited(note) else ""
    return (
        f'<div class="accent" style="background:{PALETTE[owner_id % len(PALETTE)]}"></div>'
        f'<div class="note-title">{esc(note["title"])}</div>{body}'
        f'<div class="note-meta">{avatar(ctx.owner_name(owner_id), owner_id, 24)}'
        f"<span>{esc(ctx.owner_name(owner_id))}</span><span>·</span>"
        f'<span>{time_ago(note["created_at"])}</span>{edited}</div>'
    )


def note_card(ctx: Ctx, note: dict, scope: str, actions: bool = False) -> None:
    """One note as a styled card. With actions=True it also shows Edit and Delete buttons."""
    with st.container(key=f"card_{scope}_note_{note['id']}"):
        st.markdown(note_html(note, ctx), unsafe_allow_html=True)
        if actions:
            col_edit, col_delete, _ = st.columns([1, 1, 1.4])
            if col_edit.button("✏️ Edit", key=f"edit_{scope}_{note['id']}", width="stretch"):
                edit_note_dialog(ctx, note)
            if col_delete.button("🗑️ Delete", key=f"delete_{scope}_{note['id']}", width="stretch"):
                delete_note_dialog(ctx, note)


def password_strength(password: str) -> tuple[float, str]:
    points = sum(
        [
            len(password) >= 8,
            len(password) >= 12,
            bool(re.search(r"[a-z]", password)) and bool(re.search(r"[A-Z]", password)),
            bool(re.search(r"\d", password)),
            bool(re.search(r"[^A-Za-z0-9]", password)),
        ]
    )
    label = ["Very weak", "Weak", "Fair", "Good", "Strong", "Excellent"][points] if password else "Type a password"
    return points / 5, label


# ---------- dialogs (pop-up windows) ----------
@st.dialog("Create a new user")
def new_user_dialog(ctx: Ctx) -> None:
    username = st.text_input("Username", placeholder="e.g. alice")
    email = st.text_input("Email", placeholder="alice@example.com")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm password", type="password")

    strength, strength_label = password_strength(password)
    st.progress(strength, text=f"Password strength: {strength_label}")
    checks = {
        "Username has 3 to 50 characters": 3 <= len(username.strip()) <= 50,
        "Email address looks valid": bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip())),
        "Password has at least 8 characters": len(password) >= 8,
        "Passwords match": bool(password) and password == confirm,
    }
    for label, passed in checks.items():
        st.markdown(f"{'✅' if passed else '⚪'} {label}")

    # The button is not disabled on purpose: a disabled button can swallow the click that
    # also commits the last text field. Problems are reported when it is pressed.
    if st.button("Create user", type="primary", width="stretch"):
        if not all(checks.values()):
            st.error("Please fix the items marked with ⚪ above.")
        else:
            ok, created = attempt(ctx.client.create_user, username.strip(), email.strip(), password)
            if ok:
                flash("success", f"User '{created['username']}' created.")
                st.rerun()


@st.dialog("Write a new note", width="large")
def new_note_dialog(ctx: Ctx, default_user_id: int | None = None) -> None:
    if not ctx.users:
        st.warning("A note needs an owner. Create a user first.")
        return
    ids = [u["id"] for u in ctx.users]
    owner = st.selectbox(
        "Owner", ctx.users, index=ids.index(default_user_id) if default_user_id in ids else 0, format_func=user_label
    )
    title = st.text_input("Title", max_chars=200, placeholder="Give your note a title")
    content = st.text_area("Content", height=180, max_chars=10_000, placeholder="Write something…")
    st.caption(f"{len(content):,} / 10,000 characters")
    if st.button("Create note", type="primary", width="stretch"):
        if not title.strip():
            st.error("Title cannot be empty.")
        else:
            ok, created = attempt(ctx.client.create_note, owner["id"], title.strip(), content)
            if ok:
                flash("success", f"Note '{created['title']}' created for {owner['username']}.")
                st.rerun()


@st.dialog("Edit note", width="large")
def edit_note_dialog(ctx: Ctx, note: dict) -> None:
    title = st.text_input("Title", value=note["title"], max_chars=200)
    content = st.text_area("Content", value=note["content"], height=200, max_chars=10_000)
    st.caption(f"Owner: {ctx.owner_name(note['user_id'])} · {len(content):,} / 10,000 characters")
    if st.button("Save changes", type="primary", width="stretch"):
        if not title.strip():
            st.error("Title cannot be empty.")
        else:
            ok, _ = attempt(ctx.client.update_note, note["id"], title.strip(), content)
            if ok:
                flash("success", "Note updated.")
                st.rerun()


@st.dialog("Delete this note?")
def delete_note_dialog(ctx: Ctx, note: dict) -> None:
    st.markdown(f"You are about to permanently delete **{esc(note['title'])}**. This cannot be undone.")
    col_cancel, col_delete = st.columns(2)
    if col_cancel.button("Cancel", width="stretch"):
        st.rerun()
    if col_delete.button("Yes, delete", type="primary", width="stretch"):
        ok, _ = attempt(ctx.client.delete_note, note["id"])
        if ok:
            flash("success", f"Note '{note['title']}' deleted.")
            st.rerun()


@st.dialog("User details", width="large")
def user_notes_dialog(ctx: Ctx, user: dict) -> None:
    ok, details = attempt(ctx.client.get_user, user["id"])  # the API returns the user with their notes
    if not ok:
        return
    st.markdown(
        f'<div class="user-head">{avatar(details["username"], details["id"], 52)}<div>'
        f'<div class="user-name">{esc(details["username"])}</div>'
        f'<div class="user-sub">{esc(details["email"])} · joined {parse_time(details["created_at"]):%d %b %Y}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"#### Notes ({len(details['notes'])})")
    if not details["notes"]:
        empty_state("🗒️", "No notes yet", f"{details['username']} hasn't written anything.")
    for note in sorted(details["notes"], key=lambda n: n["created_at"], reverse=True):
        note_card(ctx, note, "dialog")


# ---------- pages ----------
def page_header(title: str, subtitle: str, button_label: str, on_click: Callable[[], None]) -> None:
    col_title, col_button = st.columns([4, 1], vertical_alignment="center")
    col_title.title(title)
    col_title.caption(subtitle)
    if col_button.button(button_label, type="primary", width="stretch"):
        on_click()


def page_dashboard(ctx: Ctx) -> None:
    st.markdown(
        '<div class="hero"><h1>Welcome back 👋</h1>'
        "<p>Everything below is read live from your SQLite database through the FastAPI backend.</p></div>",
        unsafe_allow_html=True,
    )
    avg = f"{len(ctx.notes) / len(ctx.users):.1f}" if ctx.users else "–"
    for column, card in zip(
        st.columns(3),
        [stat_card("👥", len(ctx.users), "Total users", "#6366F1"),
         stat_card("📝", len(ctx.notes), "Total notes", "#EC4899"),
         stat_card("📊", avg, "Notes per user", "#14B8A6")],
    ):
        column.markdown(card, unsafe_allow_html=True)

    col_a, col_b, _ = st.columns([1, 1, 3])
    if col_a.button("＋ New user", width="stretch"):
        new_user_dialog(ctx)
    if col_b.button("＋ New note", width="stretch"):
        new_note_dialog(ctx)

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Recent notes")
        if not ctx.users:
            empty_state("👋", "No users yet", "Create the first user to get started.")
        elif not ctx.notes:
            empty_state("🗒️", "No notes yet", "Write the first note with the button above.")
        else:
            for note in sorted(ctx.notes, key=lambda n: n["created_at"], reverse=True)[:4]:
                note_card(ctx, note, "dash")
            st.button("View all notes →", on_click=go, args=("Notes",))
    with right:
        st.subheader("Notes per user")
        if ctx.users and ctx.notes:
            counts = Counter(n["user_id"] for n in ctx.notes)
            top = sorted(ctx.users, key=lambda u: counts.get(u["id"], 0), reverse=True)[:8]
            names = [u["username"] for u in top]
            if len(set(names)) != len(names):
                names = [f"{u['username']} #{u['id']}" for u in top]
            st.bar_chart(pd.DataFrame({"Notes": [counts.get(u["id"], 0) for u in top]}, index=names),
                         color="#6366F1", horizontal=True, height=240)
        else:
            st.caption("The chart appears once there are notes.")
        st.subheader("Activity, last 14 days")
        if ctx.notes:
            today = datetime.now(timezone.utc).date()
            days = [today - timedelta(days=offset) for offset in range(13, -1, -1)]
            per_day = Counter(parse_time(n["created_at"]).date() for n in ctx.notes)
            st.area_chart(pd.DataFrame({"Notes created": [per_day.get(d, 0) for d in days]},
                                       index=pd.to_datetime(days)), color="#8B5CF6", height=200)
        else:
            st.caption("The chart appears once there are notes.")


def user_card(ctx: Ctx, user: dict, note_count: int) -> None:
    with st.container(key=f"card_user_{user['id']}"):
        st.markdown(
            f'<div class="user-head">{avatar(user["username"], user["id"])}<div>'
            f'<div class="user-name">{esc(user["username"])}</div>'
            f'<div class="user-sub">{esc(user["email"])}</div></div></div>'
            f'<div class="note-meta"><span class="badge">{note_count} note{"" if note_count == 1 else "s"}</span>'
            f'<span>joined {time_ago(user["created_at"])}</span></div>',
            unsafe_allow_html=True,
        )
        col_view, col_add = st.columns(2)
        if col_view.button("View notes", key=f"view_{user['id']}", width="stretch"):
            user_notes_dialog(ctx, user)
        if col_add.button("＋ Note", key=f"add_{user['id']}", width="stretch"):
            new_note_dialog(ctx, user["id"])


def page_users(ctx: Ctx) -> None:
    page_header("Users", "People who own notes.", "＋ New user", lambda: new_user_dialog(ctx))
    if not ctx.users:
        empty_state("👤", "No users yet", "Click “New user” to create the first one.")
        return

    col_search, col_sort = st.columns([3, 1])
    query = col_search.text_input("Search users", placeholder="🔍  Search by name or email…", label_visibility="collapsed")
    order = col_sort.selectbox("Sort users", ["Newest first", "Name A–Z", "Most notes"], label_visibility="collapsed")

    counts = Counter(n["user_id"] for n in ctx.notes)
    shown = [u for u in ctx.users if query.lower() in f"{u['username']} {u['email']}".lower()]
    if order == "Name A–Z":
        shown.sort(key=lambda u: u["username"].lower())
    elif order == "Most notes":
        shown.sort(key=lambda u: counts.get(u["id"], 0), reverse=True)
    else:
        shown.sort(key=lambda u: u["id"], reverse=True)

    if not shown:
        empty_state("🔍", "No matching users", "Try a different search.")
        return
    st.caption(f"Showing {len(shown)} of {len(ctx.users)} users")
    for start in range(0, len(shown), 3):  # one row of three cards at a time keeps the grid aligned
        for column, user in zip(st.columns(3), shown[start:start + 3]):
            with column:
                user_card(ctx, user, counts.get(user["id"], 0))


def filter_and_sort_notes(ctx: Ctx, query: str, owner: dict | None, order: str) -> list[dict]:
    shown = [
        n for n in ctx.notes
        if query.lower() in f"{n['title']} {n['content']}".lower() and (owner is None or n["user_id"] == owner["id"])
    ]
    if order == "Oldest first":
        shown.sort(key=lambda n: n["created_at"])
    elif order == "Recently edited":
        shown.sort(key=lambda n: n["updated_at"], reverse=True)
    elif order == "Title A–Z":
        shown.sort(key=lambda n: n["title"].lower())
    else:
        shown.sort(key=lambda n: n["created_at"], reverse=True)
    return shown


def page_notes(ctx: Ctx) -> None:
    page_header("Notes", "Search, filter, edit and delete.", "＋ New note", lambda: new_note_dialog(ctx))
    if not ctx.notes:
        empty_state("🗒️", "No notes yet", "Click “New note” to write the first one." if ctx.users else "Create a user first, then add notes.")
        return

    col_search, col_user, col_sort, col_view = st.columns([3, 2, 2, 1.6])
    query = col_search.text_input("Search notes", placeholder="🔍  Search title or content…", label_visibility="collapsed")
    owner = col_user.selectbox("Filter by user", [None, *ctx.users], label_visibility="collapsed",
                               format_func=lambda u: "All users" if u is None else user_label(u))
    order = col_sort.selectbox("Sort notes", SORT_NOTES, label_visibility="collapsed")
    view = col_view.segmented_control("View", ["Cards", "Table"], default="Cards", label_visibility="collapsed") or "Cards"

    shown = filter_and_sort_notes(ctx, query, owner, order)
    if not shown:
        empty_state("🔍", "No matching notes", "Try a different search or filter.")
        return
    st.caption(f"Showing {len(shown)} of {len(ctx.notes)} notes")

    if view == "Table":
        selection = st.dataframe(
            [{"ID": n["id"], "Title": n["title"], "Owner": ctx.owner_name(n["user_id"]),
              "Content": n["content"][:80], "Updated": time_ago(n["updated_at"])} for n in shown],
            hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row",
        )
        if selection.selection.rows:
            note = shown[selection.selection.rows[0]]
            st.markdown(f"Selected: **{esc(note['title'])}**")
            col_edit, col_delete, _ = st.columns([1, 1, 4])
            if col_edit.button("✏️ Edit", key="table_edit", width="stretch"):
                edit_note_dialog(ctx, note)
            if col_delete.button("🗑️ Delete", key="table_delete", width="stretch"):
                delete_note_dialog(ctx, note)
        else:
            st.caption("Click a row to edit or delete it.")
        return

    limit = st.session_state.get("notes_limit", NOTES_PER_PAGE)
    visible = shown[:limit]
    for start in range(0, len(visible), 2):
        for column, note in zip(st.columns(2), visible[start:start + 2]):
            with column:
                note_card(ctx, note, "list", actions=True)
    if len(shown) > limit and st.button(f"Show more ({len(shown) - limit} remaining)", width="stretch"):
        st.session_state["notes_limit"] = limit + NOTES_PER_PAGE
        st.rerun()


# ---------- app shell ----------
def main() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    st.session_state.setdefault("api_url", DEFAULT_BASE_URL)
    st.session_state.setdefault("page", "Dashboard")

    with st.sidebar:
        st.markdown('<div class="brand">📝 Notes Manager</div>', unsafe_allow_html=True)
        st.radio("Navigation", list(PAGES), format_func=PAGES.get, key="page", label_visibility="collapsed")
        st.divider()
        status = st.empty()
        with st.expander("Backend settings"):
            st.text_input("API base URL", key="api_url")

    client = APIClient(st.session_state["api_url"])
    try:
        client.health()
    except APIError as exc:
        empty_state("🔌", "Backend not reachable", exc.message)
        st.code("uvicorn app.main:app --app-dir backend --reload", language="bash")
        st.button("Retry", type="primary")
        st.stop()

    with st.sidebar:
        status.markdown(f'<span class="status">Connected</span><br><span class="user-sub">{esc(client.base_url)}</span>',
                        unsafe_allow_html=True)
        st.link_button("Open API docs ↗", f"{client.base_url}/docs", width="stretch")

    show_flash()
    try:
        ctx = Ctx(client, client.list_users(), client.list_notes())
        {"Dashboard": page_dashboard, "Users": page_users, "Notes": page_notes}[st.session_state["page"]](ctx)
    except APIError as exc:
        st.error(f"The backend returned an error: {exc.message}")


if __name__ == "__main__":  # Streamlit runs the script as __main__
    main()
