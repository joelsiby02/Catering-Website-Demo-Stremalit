import pandas as pd

# Sample product data — customize this for your client's menu
data = [
    {
        "id": 1,
        "name": "Chicken Biryani",
        "description": "Aromatic basmati rice with spiced chicken and herbs.",
        "price": 180,
        "category": "Main Course",
        "image": "https://example.com/images/chicken_biryani.jpg"
    },
    {
        "id": 2,
        "name": "Paneer Butter Masala",
        "description": "Creamy paneer curry cooked in buttery tomato gravy.",
        "price": 150,
        "category": "Main Course",
        "image": "https://example.com/images/paneer_butter_masala.jpg"
    },
    {
        "id": 3,
        "name": "Gulab Jamun",
        "description": "Sweet milk-solid dumplings soaked in sugar syrup.",
        "price": 70,
        "category": "Dessert",
        "image": "https://example.com/images/gulab_jamun.jpg"
    }
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Save as CSV and Excel
df.to_csv("catalog.csv", index=False)
df.to_excel("catalog.xlsx", index=False)

print("✅ Catalog files created: catalog.csv & catalog.xlsx")
