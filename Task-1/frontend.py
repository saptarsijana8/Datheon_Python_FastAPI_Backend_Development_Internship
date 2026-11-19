# frontend.py
# Streamlit dashboard for the BookStore REST API.
# It talks to the FastAPI backend using the "requests" library.

import pandas as pd
import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"

# ---------- Page settings ----------
st.set_page_config(page_title="BookStore Dashboard", page_icon="📚", layout="wide")


# ---------- Helper functions (talk to the backend) ----------
def get_error_message(response):
    """Turn an error response from FastAPI into a readable message."""
    try:
        detail = response.json()["detail"]
    except Exception:
        return f"Something went wrong (status code {response.status_code})"

    # 404 and 400 errors have a simple text message
    if isinstance(detail, str):
        return detail

    # 422 validation errors have a list of problems
    messages = []
    for error in detail:
        field = error["loc"][-1]  # for example "price"
        messages.append(f"{field}: {error['msg']}")
    return " | ".join(messages)


def call_api(method, path, params=None, data=None):
    """Send a request to the backend. Returns (result, error_message)."""
    try:
        response = requests.request(
            method, BASE_URL + path, params=params, json=data, timeout=5
        )
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the backend. Start it with: uvicorn app.main:app --reload"
    except requests.exceptions.Timeout:
        return None, "The backend took too long to respond."

    if response.status_code >= 400:
        return None, get_error_message(response)
    return response.json(), None


def make_table(books):
    """Convert the list of books (from the API) into a table."""
    table = pd.DataFrame(books)
    table = table[["id", "title", "author", "price", "quantity"]]
    table.columns = ["ID", "Title", "Author", "Price (₹)", "Quantity"]
    return table


def show_flash_message():
    """Show a message that was saved before the page reloaded."""
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))


# ---------- Page 1: Dashboard ----------
def show_dashboard():
    st.title("📊 Dashboard Overview")

    books, error = call_api("GET", "/books")
    if error:
        st.error(error)
        return
    if not books:
        st.info("No books yet. Go to 'Add Book' to add your first one.")
        return

    # Calculate the summary numbers
    total_books = len(books)
    total_copies = sum(book["quantity"] for book in books)
    inventory_value = sum(book["price"] * book["quantity"] for book in books)
    average_price = sum(book["price"] for book in books) / total_books

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📚 Total Books", total_books)
    col2.metric("📦 Copies in Stock", total_copies)
    col3.metric("💰 Inventory Value", f"₹{inventory_value:,.2f}")
    col4.metric("🏷️ Average Price", f"₹{average_price:,.2f}")

    st.subheader("Stock per Book")
    table = make_table(books)
    st.bar_chart(table.set_index("Title")["Quantity"])

    st.subheader("⚠️ Low Stock (5 copies or fewer)")
    low_stock_books = [book for book in books if book["quantity"] <= 5]
    if low_stock_books:
        st.dataframe(make_table(low_stock_books), hide_index=True)
    else:
        st.success("All books are well stocked.")


# ---------- Page 2: View, search and filter ----------
def show_all_books():
    st.title("📖 All Books")

    st.subheader("🔍 Search and Filter")
    col1, col2 = st.columns(2)
    title = col1.text_input("Search by title")
    author = col2.text_input("Filter by author")

    col3, col4 = st.columns(2)
    min_price = col3.number_input("Minimum price (₹)", min_value=0.0, value=0.0, step=50.0)
    max_price = col4.number_input("Maximum price (₹)  (0 = no limit)", min_value=0.0, value=0.0, step=50.0)

    # Only send the filters the user actually filled in
    params = {}
    if title:
        params["title"] = title
    if author:
        params["author"] = author
    if min_price > 0:
        params["min_price"] = min_price
    if max_price > 0:
        params["max_price"] = max_price

    books, error = call_api("GET", "/books", params=params)
    if error:
        st.error(error)
        return

    st.subheader(f"Results: {len(books)} book(s) found")
    if books:
        st.dataframe(make_table(books), hide_index=True)
    else:
        st.warning("No books match your search.")


# ---------- Page 3: Add a book ----------
def show_add_book():
    st.title("➕ Add New Book")

    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        col1, col2 = st.columns(2)
        # No min_value here on purpose: the backend (Pydantic) does the validation
        price = col1.number_input("Price (₹)", value=0.0, step=10.0, format="%.2f")
        quantity = col2.number_input("Quantity", value=0, step=1)
        submitted = st.form_submit_button("Add Book")

    if submitted:
        new_book = {"title": title, "author": author, "price": price, "quantity": quantity}
        result, error = call_api("POST", "/books", data=new_book)
        if error:
            st.error(f"❌ Could not add book. {error}")
        else:
            st.success(f"✅ '{result['title']}' was added with ID {result['id']}")
            st.json(result)


# ---------- Page 4: Update a book ----------
def show_update_book():
    st.title("✏️ Update Book")

    books, error = call_api("GET", "/books")
    if error:
        st.error(error)
        return
    if not books:
        st.info("There are no books to update.")
        return

    # Let the user pick a book by ID
    labels = {book["id"]: f"ID {book['id']} - {book['title']}" for book in books}
    selected_id = st.selectbox("Select a book", list(labels.keys()), format_func=lambda i: labels[i])

    # Get that book's current details from the API
    book, error = call_api("GET", f"/books/{selected_id}")
    if error:
        st.error(error)
        return

    # The form is filled with the existing details
    with st.form(f"update_form_{selected_id}"):
        title = st.text_input("Title", value=book["title"], key=f"title_{selected_id}")
        author = st.text_input("Author", value=book["author"], key=f"author_{selected_id}")
        col1, col2 = st.columns(2)
        price = col1.number_input("Price (₹)", value=float(book["price"]), step=10.0,
                                  format="%.2f", key=f"price_{selected_id}")
        quantity = col2.number_input("Quantity", value=int(book["quantity"]), step=1,
                                     key=f"quantity_{selected_id}")
        submitted = st.form_submit_button("Save Changes")

    if submitted:
        updated_book = {"title": title, "author": author, "price": price, "quantity": quantity}
        result, error = call_api("PUT", f"/books/{selected_id}", data=updated_book)
        if error:
            st.error(f"❌ Could not update book. {error}")
        else:
            st.success(f"✅ Book {result['id']} updated successfully")
            st.json(result)


# ---------- Page 5: Delete a book ----------
def show_delete_book():
    st.title("🗑️ Delete Book")

    books, error = call_api("GET", "/books")
    if error:
        st.error(error)
        return
    if not books:
        st.info("There are no books to delete.")
        return

    labels = {book["id"]: f"ID {book['id']} - {book['title']}" for book in books}
    selected_id = st.selectbox("Select a book", list(labels.keys()), format_func=lambda i: labels[i])

    book, error = call_api("GET", f"/books/{selected_id}")
    if error:
        st.error(error)
        return

    # Show the book so the user knows what will be deleted
    st.write(f"**Title:** {book['title']}")
    st.write(f"**Author:** {book['author']}")
    st.write(f"**Price:** ₹{book['price']}  |  **Quantity:** {book['quantity']}")

    confirm = st.checkbox("Yes, I want to delete this book", key=f"confirm_{selected_id}")
    if st.button("🗑️ Delete Book", disabled=not confirm):
        result, error = call_api("DELETE", f"/books/{selected_id}")
        if error:
            st.error(f"❌ {error}")
        else:
            st.session_state["flash"] = "✅ " + result["message"]
            st.rerun()  # reload so the deleted book disappears from the list


# ---------- Main: sidebar and page navigation ----------
def main():
    st.sidebar.title("📚 BookStore")
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "📖 All Books", "➕ Add Book", "✏️ Update Book", "🗑️ Delete Book"],
    )

    # Show whether the backend is running
    _, backend_error = call_api("GET", "/")
    if backend_error:
        st.sidebar.error("Backend: offline")
    else:
        st.sidebar.success("Backend: connected")

    show_flash_message()

    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📖 All Books":
        show_all_books()
    elif page == "➕ Add Book":
        show_add_book()
    elif page == "✏️ Update Book":
        show_update_book()
    elif page == "🗑️ Delete Book":
        show_delete_book()


main()