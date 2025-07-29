import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import urllib.parse

CSV_FILE = "orders.csv"
YOUR_PHONE = "9140939949"  # Your WhatsApp number

def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "Order ID", "Product", "Quantity", "Unit Price", "Subtotal",
            "Name", "Phone", "Address", "Pincode", "Reference By", "Timestamp"
        ])
        df.to_csv(CSV_FILE, index=False)

def save_orders_to_csv(order_rows):
    initialize_csv()
    df_existing = pd.read_csv(CSV_FILE, dtype={"Phone": str})
    df_new = pd.DataFrame(order_rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_csv(CSV_FILE, index=False)

rakhi_catalog = {
    "IMG_20250707_221915": {
        "title": "Elegant Thread Rakhi",
        "price": 120,
        "discount": 30,
        "image": "https://res.cloudinary.com/dx35lfv49/image/upload/v1753726754/IMG_20250707_221915.jpg"
    },
    "IMG_20250707_222238": {
        "title": "Traditional Beads Rakhi",
        "price": 120,
        "discount": 10,
        "image": "https://res.cloudinary.com/dx35lfv49/image/upload/v1753726756/IMG_20250707_222238.jpg"
    },
    "IMG_20250707_222103": {
        "title": "Simple Grace Rakhi",
        "price": 80,
        "discount": 10,
        "image": "https://res.cloudinary.com/dx35lfv49/image/upload/v1753726757/IMG_20250707_222103.jpg"
    },
    "IMG_20250707_222735": {
        "title": "Royal Red Rakhi",
        "price": 80,
        "discount": 10,
        "image": "https://res.cloudinary.com/dx35lfv49/image/upload/v1753726761/IMG_20250707_222735.jpg"
    },
    "IMG_20250707_222554": {
        "title": "Pearl Designer Rakhi",
        "price": 120,
        "discount": 20,
        "image": "https://res.cloudinary.com/dx35lfv49/image/upload/v1753726762/IMG_20250707_222554.jpg"
    },
}

rakhi_catalog = dict(sorted(rakhi_catalog.items(), key=lambda x: -x[1]['discount']))

st.set_page_config(page_title="Saaurabh Collections", layout="wide")

if "user_phone" not in st.session_state:
    with st.form("login_form"):
        st.title("🔐 Login to Saaurabh Collections")
        user_phone = st.text_input("Enter your phone number")
        login_submit = st.form_submit_button("Login")
    if login_submit:
        if user_phone:
            st.session_state.user_phone = str(user_phone).strip()
            st.rerun()
        else:
            st.warning("📱 Please enter a valid phone number.")
    st.stop()

st.sidebar.markdown(f"📱 Logged in as: `{st.session_state.user_phone}`")
if st.sidebar.button("🔓 Logout"):
    st.session_state.clear()
    st.rerun()

selected_tab = st.sidebar.radio("Navigate", ["🛍️ Shop", "📦 My Orders"])

if "cart" not in st.session_state:
    st.session_state.cart = {}

if selected_tab == "🛍️ Shop":
    st.title("🛍️ Saaurabh Collections")
    cols = st.columns(3)

    for i, (key, item) in enumerate(rakhi_catalog.items()):
        with cols[i % 3]:
            final_price = int(item["price"] * (1 - item["discount"] / 100))
            st.image(item["image"], use_column_width=True)  # ✅ Use backward-compatible option
            st.markdown(f"**{item['title']}**")
            st.markdown(f"~~₹{item['price']}~~ 🎉 **{item['discount']}% OFF** → ₹{final_price}")
            qty = st.number_input(f"Qty for {key}", min_value=1, max_value=10, value=1, key=f"qty_{key}")
            if st.button(f"🛒 Add to Cart", key=f"add_{key}"):
                if key in st.session_state.cart:
                    st.session_state.cart[key]["quantity"] += qty
                else:
                    st.session_state.cart[key] = {
                        "title": item["title"],
                        "price": final_price,
                        "quantity": qty
                    }
                st.success(f"Added {qty} x {item['title']} to cart")

    if st.session_state.cart:
        st.markdown("---")
        st.header("🧾 Your Cart")
        total_price = 0
        for pid, details in st.session_state.cart.items():
            subtotal = details["price"] * details["quantity"]
            total_price += subtotal
            st.write(f"{details['title']} × {details['quantity']} = ₹{subtotal}")
        st.write(f"### Grand Total: ₹{total_price}")

        with st.form("checkout_form"):
            st.subheader("📦 Checkout")
            name = st.text_input("Your Name")
            address = st.text_area("Delivery Address")
            pincode = st.text_input("Pincode")
            reference_by = st.text_input("Reference By")
            submit = st.form_submit_button("Place Order")

        if submit:
            if not name or not address or not pincode:
                st.error("Please complete all fields.")
            else:
                order_id = str(uuid.uuid4())[:8]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                phone_number = str(st.session_state.user_phone).strip()
                orders = []
                for pid, details in st.session_state.cart.items():
                    orders.append({
                        "Order ID": order_id,
                        "Product": details["title"],
                        "Quantity": details["quantity"],
                        "Unit Price": details["price"],
                        "Subtotal": details["price"] * details["quantity"],
                        "Name": name,
                        "Phone": phone_number,
                        "Address": address,
                        "Pincode": pincode,
                        "Reference By": reference_by,
                        "Timestamp": timestamp
                    })

                save_orders_to_csv(orders)

                msg = f"*Order ID:* {order_id}\n*Name:* {name}\n*Phone:* {phone_number}\n*Pincode:* {pincode}\n*Address:* {address}\n"
                if reference_by:
                    msg += f"*Reference By:* {reference_by}\n"
                for d in orders:
                    msg += f"- {d['Product']} × {d['Quantity']} = ₹{d['Subtotal']}\n"
                msg += f"\n*Total:* ₹{total_price}"
                wa_link = f"https://wa.me/{YOUR_PHONE}?text={urllib.parse.quote(msg)}"

                st.success("✅ Order placed!")
                st.markdown(f"[📲 Send order via WhatsApp]({wa_link})", unsafe_allow_html=True)
                st.session_state.cart = {}
    else:
        st.info("🛒 Your cart is empty.")

elif selected_tab == "📦 My Orders":
    st.title("📦 Your Orders")

    initialize_csv()
    df_all = pd.read_csv(CSV_FILE, dtype={"Phone": str})
    df_all["Phone"] = df_all["Phone"].astype(str).str.strip()
    user_phone = str(st.session_state.user_phone).strip()
    df = df_all[df_all["Phone"] == user_phone]

    if df.empty:
        st.info("No orders found.")
    else:
        st.success(f"Total orders: {df['Order ID'].nunique()} | Items: {len(df)}")
        grouped = df.groupby("Order ID")
        for oid, group in grouped:
            st.markdown(f"### 🧾 Order ID: `{oid}`")
            st.markdown(
                f"**Name:** {group.iloc[0]['Name']} | **Pincode:** {group.iloc[0]['Pincode']} | **Address:** {group.iloc[0]['Address']}")
            if group.iloc[0]["Reference By"]:
                st.markdown(f"**Reference By:** {group.iloc[0]['Reference By']}")
            st.write(group[["Product", "Quantity", "Unit Price", "Subtotal", "Timestamp"]])
