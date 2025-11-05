import streamlit as st
import pandas as pd
import urllib.parse
from PIL import Image
import os

# ================= CONFIG =================
st.set_page_config(
    page_title="🍱 Homemade Catering Menu", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= LOAD DATA FROM EXCEL =================
@st.cache_data
def load_data():
    try:
        # Load from Excel file
        df = pd.read_excel("catalog.xlsx")
        return df
    except FileNotFoundError:
        st.error("❌ Excel file 'catalog.xlsx' not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading Excel file: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# ================= INITIAL SETUP =================
if "cart" not in st.session_state:
    st.session_state.cart = []
if "customer_info" not in st.session_state:
    st.session_state.customer_info = {"name": "", "address": "", "phone": ""}

# ================= SIMPLE STYLING =================
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        padding: 10px 0;
    }
    .dish-card {
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: white;
    }
    .price-tag {
        color: #2E8B57;
        font-weight: bold;
        font-size: 1.2em;
    }
    </style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<h1 class="main-header">🍱 Homemade Catering Menu</h1>', unsafe_allow_html=True)

# ================= SECTION 1: CATALOG =================
st.markdown("## 🍽️ Our Menu")
st.markdown("Browse our delicious homemade dishes")

# Display all items in a clean grid - 3 columns
cols = st.columns(3)

for i, (_, row) in enumerate(df.iterrows()):
    with cols[i % 3]:
        # Dish card
        st.markdown(f"**{row['name']}**")
        
        # Image
        try:
            if os.path.exists(row["image"]):
                img = Image.open(row["image"])
            else:
                img_path = f"images/{row['image']}"
                img = Image.open(img_path)
            img = img.resize((250, 180))
            st.image(img, use_container_width=True)
        except:
            st.image("https://via.placeholder.com/250x180/4CAF50/white?text=Dish+Image", 
                    use_container_width=True)
        
        st.caption(f"{row['description']}")
        st.markdown(f'<p class="price-tag">₹{row["price"]}</p>', unsafe_allow_html=True)
        
        # Simple quantity and add to cart
        qty = st.number_input(
            "Quantity",
            min_value=0,
            max_value=20,
            value=0,
            key=f"qty_{row['id']}",
            step=1
        )
        
        if st.button("Add to Cart", key=f"add_{row['id']}", use_container_width=True):
            if qty > 0:
                # Check if item already in cart
                found = False
                for item in st.session_state.cart:
                    if item["name"] == row["name"]:
                        item["qty"] += qty
                        found = True
                        break
                
                if not found:
                    st.session_state.cart.append({
                        "name": row["name"],
                        "qty": qty,
                        "price": row["price"]
                    })
                
                st.success(f"Added {qty} x {row['name']}!")
                st.rerun()
            else:
                st.warning("Please select quantity")

st.markdown("---")

# ================= SECTION 2: CART =================
st.markdown("## 🛒 Your Cart")

if not st.session_state.cart:
    st.info("Your cart is empty. Add some delicious dishes from our menu above.")
else:
    total_amount = sum(item["qty"] * item["price"] for item in st.session_state.cart)
    total_items = sum(item["qty"] for item in st.session_state.cart)
    
    st.markdown(f"**Total Items:** {total_items} | **Total Amount:** ₹{total_amount}")
    
    # Show cart items
    for i, item in enumerate(st.session_state.cart):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.write(f"**{item['name']}**")
        with col2:
            st.write(f"Qty: {item['qty']}")
        with col3:
            st.write(f"₹{item['price']} each")
        with col4:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()
    
    st.markdown(f"### 💰 Cart Total: ₹{total_amount}")

st.markdown("---")

# ================= SECTION 3: ORDER VIA WHATSAPP =================
st.markdown("## 📤 Order Via WhatsApp")

if not st.session_state.cart:
    st.info("🛒 Add items to your cart first to place an order")
else:
    st.markdown("### 📝 Your Information")
    
    # Customer information form
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.customer_info["name"] = st.text_input(
            "Full Name *", 
            value=st.session_state.customer_info["name"],
            placeholder="Enter your full name"
        )
        st.session_state.customer_info["phone"] = st.text_input(
            "Phone Number *", 
            value=st.session_state.customer_info["phone"],
            placeholder="Your WhatsApp number"
        )
    with col2:
        st.session_state.customer_info["address"] = st.text_area(
            "Delivery Address *", 
            value=st.session_state.customer_info["address"],
            placeholder="Full delivery address with landmarks",
            height=100
        )
    
    # Check if customer info is complete
    missing_info = []
    if not st.session_state.customer_info["name"]: 
        missing_info.append("Full Name")
    if not st.session_state.customer_info["phone"]: 
        missing_info.append("Phone Number")
    if not st.session_state.customer_info["address"]: 
        missing_info.append("Delivery Address")
    
    if missing_info:
        st.error(f"❌ Please fill in all required information: {', '.join(missing_info)}")
    else:
        # Create order message
        order_lines = []
        order_lines.append("🍱 *NEW CATERING ORDER* 🍱")
        order_lines.append("")
        order_lines.append("*Customer Details:*")
        order_lines.append(f"👤 Name: {st.session_state.customer_info['name']}")
        order_lines.append(f"📞 Phone: {st.session_state.customer_info['phone']}")
        order_lines.append(f"🏠 Address: {st.session_state.customer_info['address']}")
        order_lines.append("")
        order_lines.append("*Order Summary:*")
        order_lines.append("─" * 25)
        
        for item in st.session_state.cart:
            item_total = item["qty"] * item["price"]
            order_lines.append(f"• {item['qty']} x {item['name']} = ₹{item_total}")
        
        order_lines.append("─" * 25)
        order_lines.append(f"*💰 TOTAL AMOUNT: ₹{total_amount}*")
        order_lines.append("")
        order_lines.append("Please confirm this order. Thank you! 🙏")
        
        message = "\n".join(order_lines)
        encoded_message = urllib.parse.quote(message)
        
        whatsapp_number = "919946294194"  # Replace with your number
        whatsapp_link = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
        
        st.markdown("### 📱 Send Your Order")
        st.markdown("Click the button below to send your order directly via WhatsApp:")
        
        st.markdown(f"""
        <div style="text-align: center;">
            <a href='{whatsapp_link}' target='_blank'>
                <button style='
                    background-color: #25D366; 
                    color: white; 
                    padding: 15px 30px; 
                    border: none; 
                    border-radius: 8px; 
                    font-size: 18px; 
                    font-weight: bold;
                    cursor: pointer;
                    margin: 10px 0;
                '>
                    📱 Send Order via WhatsApp
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Order preview
        with st.expander("📋 Preview Your Order"):
            st.text(message)

# ================= SECTION 4: FOOTER =================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>🍛 Homemade with love • 🚚 Free delivery above ₹500 • ⏰ Order 2 hours in advance</p>
        <p>Need help? Call us: 📞 +91-9876543210</p>
    </div>
    """,
    unsafe_allow_html=True
)