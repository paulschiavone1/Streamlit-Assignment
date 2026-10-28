"""app.py - Streamlit order entry app backed by Supabase."""
import hmac
from decimal import Decimal

import pandas as pd
import streamlit as st

from Config import get_app_password
from Database import (create_order, get_customers, get_order, get_orders,
                      get_product, get_products)

st.set_page_config(page_title="Order Entry", page_icon="🧾", layout="wide")
CURRENCY = st.column_config.NumberColumn(format="$%.2f")


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"))


def set_msg(kind, text, order=None):
    """Store a message (and optional verified order) to display after the rerun."""
    st.session_state.msg = {"kind": kind, "text": text, "order": order}


def orders_to_df(orders):
    rows = []
    for o in orders:
        price, qty = money(o["unit_price"]), int(o["quantity"])
        rows.append({
            "Order ID": o["order_id"],
            "Customer": (o.get("customers") or {}).get("name", "(unknown)"),
            "Product": (o.get("products") or {}).get("product_name", "(unknown)"),
            "Quantity": qty,
            "Unit Price": float(price),
            "Total": float(price * qty),  # total uses the stored unit_price
            "Order Date": o["order_date"],
        })
    return pd.DataFrame(rows)


# ---------- Access control (runs before any database access) ----------
def password_gate():
    expected = get_app_password()
    if not expected:
        st.error("No app password is configured. Add APP_PASSWORD to the app's secrets.")
        st.stop()
    if st.session_state.get("authed"):
        return
    st.title("Order Entry")
    with st.form("login"):
        entered = st.text_input("Password", type="password")
        if st.form_submit_button("Enter"):
            if hmac.compare_digest(entered.encode(), expected.encode()):
                st.session_state.authed = True
                st.rerun()
            st.error("Incorrect password.")
    st.stop()


# ---------- Data loading ----------
def load_data():
    st.session_state.customers = get_customers()
    st.session_state.products = get_products()
    st.session_state.history = get_orders()


def refresh_data():  # button callback
    try:
        load_data()
        set_msg("info", "Data refreshed from Supabase.")
    except Exception as exc:
        set_msg("error", f"Could not refresh data ({type(exc).__name__}). Try again.")


# ---------- Order submission (runs only when the button is clicked) ----------
def submit_order():  # button callback: never runs on an ordinary rerun
    ss = st.session_state
    cid, pid, qty = ss.customer_id, ss.product_id, ss.quantity
    if not ss.confirm:
        set_msg("error", "Please check the confirmation box before submitting. No order was saved.")
        return
    if cid is None or pid is None:
        set_msg("error", "Select a customer and a product.")
        return
    if type(qty) is not int or qty <= 0:
        set_msg("error", "Quantity must be a positive whole number.")
        return
    try:
        current = get_product(pid)  # current price straight from Supabase
    except Exception as exc:
        set_msg("error", f"Could not check the product price ({type(exc).__name__}). Nothing was saved.")
        return
    if current is None:
        set_msg("error", "That product no longer exists. Refresh the data.")
        return
    shown = next(p for p in ss.products if p["product_id"] == pid)
    if money(current["price"]) != money(shown["price"]):
        shown["price"] = current["price"]  # show the updated price and require re-confirmation
        ss.confirm = False
        set_msg("warning", f"The price changed to ${money(current['price'])}. "
                           "Review the updated total and confirm again. No order was saved.")
        return
    try:
        saved = create_order(cid, pid, qty, current["price"])
    except Exception as exc:
        set_msg("error", f"The order could not be saved ({type(exc).__name__}). Nothing was saved.")
        return
    ss.confirm = False  # a second click now needs a fresh confirmation
    order_id = saved["order_id"]
    try:
        ss.history = get_orders()
    except Exception:
        pass  # history can be refreshed manually
    try:
        row = get_order(order_id)  # new query to verify the saved record
    except Exception:
        row = None
    if row:
        set_msg("success", f"Order {order_id} was saved and verified.", orders_to_df([row]))
    else:
        set_msg("warning", f"Order {order_id} was saved, but it could not be retrieved for "
                           "verification. Do not submit it again; check Order History.")


# ---------- Page ----------
password_gate()
st.title("🧾 Order Entry")
st.write("Create orders for existing customers. Data is read from and saved to Supabase, "
         "and every saved order is retrieved again to verify it.")

if "customers" not in st.session_state:
    try:
        load_data()
    except ValueError as exc:  # configuration message (never contains the key)
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"Could not load data from Supabase ({type(exc).__name__}). Check your settings.")
        st.stop()

st.button("🔄 Refresh Data", on_click=refresh_data)
ss = st.session_state

if not ss.customers or not ss.products:
    st.error("No customers or products are available from Supabase. Refresh the data or check the database.")
    st.stop()

left, right = st.columns(2)
with left:
    st.subheader("Customers")
    st.dataframe(pd.DataFrame(ss.customers)[["customer_id", "name"]].rename(
        columns={"customer_id": "Customer ID", "name": "Name"}), hide_index=True, use_container_width=True)
with right:
    st.subheader("Products")
    st.dataframe(pd.DataFrame(ss.products)[["product_id", "product_name", "category", "price"]].rename(
        columns={"product_id": "Product ID", "product_name": "Product", "category": "Category",
                 "price": "Price"}), hide_index=True, use_container_width=True,
        column_config={"Price": CURRENCY})

st.subheader("New Order")
cust_names = {c["customer_id"]: c["name"] for c in ss.customers}
prod_by_id = {p["product_id"]: p for p in ss.products}
if ss.get("customer_id") not in cust_names:
    ss.customer_id = next(iter(cust_names))
if ss.get("product_id") not in prod_by_id:
    ss.product_id = next(iter(prod_by_id))
st.selectbox("Customer", list(cust_names), format_func=lambda i: cust_names[i], key="customer_id")
st.selectbox("Product", list(prod_by_id), format_func=lambda i: prod_by_id[i]["product_name"], key="product_id")
st.number_input("Quantity", min_value=1, step=1, value=1, key="quantity")

# Review section
product = prod_by_id[ss.product_id]
price = money(product["price"])
qty = ss.quantity
st.markdown("**Review order**")
st.table(pd.DataFrame({"Customer": [cust_names[ss.customer_id]], "Product": [product["product_name"]],
                       "Quantity": [qty], "Unit Price": [f"${price}"], "Total": [f"${price * qty}"]}))
st.checkbox("I confirm this order", key="confirm")
st.button("Submit Order", type="primary", on_click=submit_order)

msg = ss.get("msg")
if msg:
    getattr(st, msg["kind"])(msg["text"])
    if msg["order"] is not None:
        st.markdown("**Verification (retrieved from Supabase)**")
        st.dataframe(msg["order"], hide_index=True, use_container_width=True,
                     column_config={"Unit Price": CURRENCY, "Total": CURRENCY})

# Order history with customer filter (extra credit)
st.subheader("Order History")
choice = st.selectbox("Filter by customer", [None] + list(cust_names),
                      format_func=lambda i: "All customers" if i is None else cust_names[i])
shown_orders = [o for o in ss.history if choice is None or o["customer_id"] == choice]
if shown_orders:
    st.dataframe(orders_to_df(shown_orders), hide_index=True, use_container_width=True,
                 column_config={"Unit Price": CURRENCY, "Total": CURRENCY})
    total_value = sum(money(o["unit_price"]) * int(o["quantity"]) for o in shown_orders)
    st.metric("Total value of these orders", f"${total_value:,.2f}")
else:
    st.info("No orders found.")