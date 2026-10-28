"""Supabase API helper functions. Every .execute() is an HTTP request to the Data API."""
from datetime import date
from functools import lru_cache

from supabase import create_client

from Config import get_settings

ORDER_SELECT = "*, customers(name), products(product_name)"  # embeds names via foreign keys


@lru_cache(maxsize=1)
def get_client():
    url, key = get_settings()
    return create_client(url, key)


def get_customers():
    return get_client().table("customers").select("*").order("customer_id").execute().data


def get_products():
    return get_client().table("products").select("*").order("product_id").execute().data


def get_product(product_id):
    """Fetch one product (used to read the CURRENT price at submission time)."""
    rows = get_client().table("products").select("*").eq("product_id", int(product_id)).execute().data
    return rows[0] if rows else None


def create_order(customer_id, product_id, quantity, unit_price):
    """Insert one order; the database generates order_id. Raises if not confirmed."""
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number.")
    response = get_client().table("orders").insert({
        "customer_id": int(customer_id),
        "product_id": int(product_id),
        "quantity": quantity,
        "order_date": date.today().isoformat(),
        "unit_price": unit_price,
    }).execute()
    if not response.data:
        raise RuntimeError("The database did not confirm the insertion.")
    return response.data[0]


def get_order(order_id):
    """Separate query for one saved order (used for verification)."""
    rows = (get_client().table("orders").select(ORDER_SELECT)
            .eq("order_id", int(order_id)).execute().data)
    return rows[0] if rows else None


def get_orders():
    """All orders, newest first, with customer and product names."""
    return (get_client().table("orders").select(ORDER_SELECT)
            .order("order_id", desc=True).execute().data)