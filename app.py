import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
DB_FILE = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            base_price REAL NOT NULL,
            stock_level INTEGER NOT NULL CHECK (stock_level >= 0)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pricing_tiers (
            item_id TEXT,
            min_quantity INTEGER NOT NULL,
            discount_percentage REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (id)
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO items (id, name, base_price, stock_level)
            VALUES (?, ?, ?, ?)
        """, [
            ("prod_001", "Mechanical Keyboard", 100.0, 50),
            ("prod_002", "Wireless Ergonomic Mouse", 50.0, 120),
            ("prod_003", "Type-C Hub Adapter", 25.0, 15)
        ])
        
        cursor.executemany("""
            INSERT INTO pricing_tiers (item_id, min_quantity, discount_percentage)
            VALUES (?, ?, ?)
        """, [
            ("prod_001", 10, 0.10),
            ("prod_001", 20, 0.20),
            ("prod_002", 15, 0.15),
            ("prod_003", 5,  0.25)
        ])
        
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/items", methods=["GET"])
def get_items():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, base_price, stock_level FROM items")
    rows = cursor.fetchall()
    conn.close()
    
    items = [{"id": r[0], "name": r[1], "base_price": r[2], "stock_level": r[3]} for r in rows]
    return jsonify(items)

@app.route("/api/calculate-price", methods=["POST"])
def calculate_price():
    data = request.json or {}
    item_id = data.get("item_id")
    quantity = int(data.get("quantity", 0))
    
    if quantity <= 0:
        return jsonify({"total_price": 0.0, "discount_applied": 0.0})
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT base_price FROM items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
        
    base_price = item[0]
    
    cursor.execute("""
        SELECT discount_percentage FROM pricing_tiers 
        WHERE item_id = ? AND ? >= min_quantity 
        ORDER BY min_quantity DESC LIMIT 1
    """, (item_id, quantity))
    
    tier = cursor.fetchone()
    discount = tier[0] if tier else 0.0
    conn.close()
    
    unit_price = base_price * (1.0 - discount)
    total_price = unit_price * quantity
    
    return jsonify({
        "unit_price": round(unit_price, 2),
        "total_price": round(total_price, 2),
        "discount_applied": round(discount * 100, 2)
    })

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.json or {}
    item_id = data.get("item_id")
    quantity = int(data.get("quantity", 0))
    
    if quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT base_price, stock_level FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            return jsonify({"error": "Item not found"}), 404
            
        base_price, current_stock = item
        
        if current_stock < quantity:
            return jsonify({"error": f"Insufficient stock. Only {current_stock} available."}), 400
            
        cursor.execute("""
            SELECT discount_percentage FROM pricing_tiers 
            WHERE item_id = ? AND ? >= min_quantity 
            ORDER BY min_quantity DESC LIMIT 1
        """, (item_id, quantity))
        tier = cursor.fetchone()
        discount = tier[0] if tier else 0.0
        
        total_price = (base_price * (1.0 - discount)) * quantity
        
        cursor.execute("""
            UPDATE items 
            SET stock_level = stock_level - ? 
            WHERE id = ?
        """, (quantity, item_id))
        
        conn.commit()
        return jsonify({
            "success": True, 
            "message": "Purchase successful!", 
            "total_paid": round(total_price, 2)
        })
        
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({"error": "Database integrity constraint violated."}), 400
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)