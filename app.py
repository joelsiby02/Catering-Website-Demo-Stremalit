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
if "order_sent" not in st.session_state:
    st.session_state.order_sent = False
if "form_updated" not in st.session_state:
    st.session_state.form_updated = False

# ================= DARK MODE COMPATIBLE STYLING =================
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        padding: 15px 0;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .section-header {
        color: #2E8B57;
        border-bottom: 2px solid #2E8B57;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .dish-card {
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .price-tag {
        color: #2E8B57;
        font-weight: bold;
        font-size: 1.3em;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
        color: #155724;
    }
    .instruction-box {
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #1565c0;
    }
    .order-preview {
        background-color: #f0f2f6;
        border: 1px solid #dadce0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        white-space: pre-wrap;
        color: #1f2937;
    }
    .validate-btn {
        background-color: #FF6B35 !important;
        color: white !important;
        padding: 12px 25px !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border: none !important;
        margin: 10px 0;
    }
    
    /* Dark mode overrides */
    [data-theme="dark"] .dish-card {
        background-color: #1e1e1e;
        border-color: #444;
        color: white;
    }
    
    [data-theme="dark"] .order-preview {
        background-color: #2d2d2d;
        border-color: #555;
        color: #e0e0e0;
    }
    
    [data-theme="dark"] .stTextInput > div > div > input,
    [data-theme="dark"] .stTextArea > div > div > textarea {
        background-color: #1e1e1e !important;
        color: white !important;
        border-color: #555 !important;
    }
    
    [data-theme="dark"] .stTextInput > div > div > input::placeholder,
    [data-theme="dark"] .stTextArea > div > div > textarea::placeholder {
        color: #888 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<h1 class="main-header">🍱 Homemade Catering Menu</h1>', unsafe_allow_html=True)

# ================= SECTION 1: CATALOG =================
st.markdown('<h2 class="section-header">🍽️ Our Menu</h2>', unsafe_allow_html=True)

# Display all items in a clean grid - 3 columns
cols = st.columns(3)

for i, (_, row) in enumerate(df.iterrows()):
    with cols[i % 3]:
        with st.container():
            st.markdown('<div class="dish-card">', unsafe_allow_html=True)
            
            # Dish name
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
            
            # Description and price
            st.caption(f"{row['description']}")
            st.markdown(f'<div class="price-tag">₹{row["price"]}</div>', unsafe_allow_html=True)
            
            # Quantity and add to cart
            col_qty, col_btn = st.columns([1, 2])
            with col_qty:
                qty = st.number_input(
                    "Qty",
                    min_value=0,
                    max_value=20,
                    value=0,
                    key=f"qty_{row['id']}",
                    step=1,
                    label_visibility="collapsed"
                )
            with col_btn:
                if st.button("➕ Add to Cart", key=f"add_{row['id']}", use_container_width=True):
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
                        
                        st.success(f"✅ Added {qty} x {row['name']} to cart!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Please select quantity")
            
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================= SECTION 2: CART =================
st.markdown('<h2 class="section-header">🛒 Your Cart</h2>', unsafe_allow_html=True)

if not st.session_state.cart:
    st.info("🎯 Your cart is empty. Add some delicious dishes from our menu above.")
else:
    total_amount = sum(item["qty"] * item["price"] for item in st.session_state.cart)
    total_items = sum(item["qty"] for item in st.session_state.cart)
    
    # Cart header with empty cart button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**📦 Total Items:** {total_items} | **💰 Total Amount:** ₹{total_amount}")
    with col2:
        if st.button("🗑️ Empty Cart", use_container_width=True, type="secondary"):
            st.session_state.cart = []
            st.session_state.order_sent = False
            st.session_state.form_updated = False
            st.success("Cart emptied successfully!")
            st.rerun()
    
    # Cart items
    st.markdown("---")
    for i, item in enumerate(st.session_state.cart):
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
        with col2:
            st.markdown(f"**Qty:** {item['qty']}")
        with col3:
            st.markdown(f"**₹{item['price']}**")
        with col4:
            st.markdown(f"**₹{item['qty'] * item['price']}**")
        with col5:
            if st.button("❌ Remove", key=f"remove_{i}", use_container_width=True):
                st.session_state.cart.pop(i)
                st.session_state.order_sent = False
                st.session_state.form_updated = False
                st.success("Item removed from cart!")
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"# 💰 Final Total: ₹{total_amount}")

st.markdown("---")

# ================= SECTION 3: ORDER VIA WHATSAPP =================
st.markdown('<h2 class="section-header">📤 Order Via WhatsApp</h2>', unsafe_allow_html=True)

if not st.session_state.cart:
    st.info("🛒 Add items to your cart first to place an order")
else:
    # Show success message if order was already sent
    if st.session_state.order_sent:
        st.markdown("""
        <div class="success-box">
            <h3>✅ Order Sent Successfully!</h3>
            <p>Your order has been sent to us via WhatsApp. We'll confirm your order shortly.</p>
            <p>Thank you for choosing us! 🍛</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Place New Order", use_container_width=True):
            st.session_state.cart = []
            st.session_state.order_sent = False
            st.session_state.customer_info = {"name": "", "address": "", "phone": ""}
            st.session_state.form_updated = False
            st.rerun()
    
    else:
        # Customer information form
        st.markdown("### 📝 Your Information")
        
        # Use form to capture all inputs at once
        with st.form("customer_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(
                    "Full Name *", 
                    value=st.session_state.customer_info["name"],
                    placeholder="Enter your full name",
                    key="name_input"
                )
                phone = st.text_input(
                    "Phone Number *", 
                    value=st.session_state.customer_info["phone"],
                    placeholder="Your WhatsApp number",
                    key="phone_input"
                )
            with col2:
                address = st.text_area(
                    "Delivery Address *", 
                    value=st.session_state.customer_info["address"],
                    placeholder="Full delivery address with landmarks",
                    height=100,
                    key="address_input"
                )
            
            # Update & Validate button
            validate_clicked = st.form_submit_button("✅ Click OK", use_container_width=True)
            
            if validate_clicked:
                st.session_state.customer_info = {
                    "name": name,
                    "phone": phone, 
                    "address": address
                }
                st.session_state.form_updated = True
                st.success("✅ Information updated! Check the validation below.")
                st.rerun()
        
        # Check validation (only after form is submitted)
        missing_info = []
        if st.session_state.form_updated:
            if not st.session_state.customer_info["name"]: 
                missing_info.append("Full Name")
            if not st.session_state.customer_info["phone"]: 
                missing_info.append("Phone Number")
            if not st.session_state.customer_info["address"]: 
                missing_info.append("Delivery Address")
        
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
        order_lines.append("─" * 30)
        
        for item in st.session_state.cart:
            item_total = item["qty"] * item["price"]
            order_lines.append(f"• {item['qty']} x {item['name']} = ₹{item_total}")
        
        order_lines.append("─" * 30)
        order_lines.append(f"*💰 TOTAL AMOUNT: ₹{total_amount}*")
        order_lines.append("")
        order_lines.append("Please confirm this order. Thank you! 🙏")
        
        message = "\n".join(order_lines)
        encoded_message = urllib.parse.quote(message)
        
        # WhatsApp sending section
        st.markdown("### 📱 Send Your Order")
        
        if not st.session_state.form_updated:
            st.info("👆 **Click 'Update & Validate Information' after filling the form to enable WhatsApp ordering**")
            whatsapp_disabled = True
        elif missing_info:
            st.error(f"❌ Please fill in all required information: {', '.join(missing_info)}")
            whatsapp_disabled = True
        else:
            st.success("✅ All information complete! You can now send your order.")
            whatsapp_disabled = False
        
        # WhatsApp Button
        whatsapp_number = "919946294194"
        whatsapp_link = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
        
        if whatsapp_disabled:
            st.markdown("""
            <button disabled style='
                background-color: #cccccc !important; 
                color: #666666 !important; 
                padding: 15px 30px; 
                border-radius: 10px; 
                font-size: 18px; 
                font-weight: bold;
                border: none;
                width: 100%;
                cursor: not-allowed;
            '>
                📱 Fill All Information to Send Order
            </button>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <a href='{whatsapp_link}' target='_blank' style='text-decoration: none;'>
                <button style='
                    background-color: #25D366; 
                    color: white; 
                    padding: 15px 30px; 
                    border-radius: 10px; 
                    font-size: 18px; 
                    font-weight: bold;
                    border: none;
                    width: 100%;
                    cursor: pointer;
                '>
                    📱 Send Order via WhatsApp
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="instruction-box">
                <strong>How it works:</strong><br>
                • Click the green button above<br>
                • WhatsApp will open with your order ready<br>
                • Just tap <strong>SEND</strong> to complete your order<br>
                • Return here to see confirmation
            </div>
            """, unsafe_allow_html=True)
        
        # Order preview
        st.markdown("### 📋 Order Summary")
        st.markdown(f'<div class="order-preview">{message}</div>', unsafe_allow_html=True)

# ================= SECTION 4: FOOTER =================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 20px; font-size: 14px;'>
        <p>🍛 Homemade with Love • 🚚 Free Delivery Above ₹500 • ⏰ Order 2 Hours in Advance</p>
        <p>📞 Direct WhatsApp: +91-9946294194</p>
        <p style='margin-top: 10px;'>© 2024 Homemade Catering</p>
    </div>
    """,
    unsafe_allow_html=True
)