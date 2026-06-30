# Smart Retail Inventory & Dynamic Pricing Engine

A lightweight, high-performance retail inventory solution featuring an automated, volume-based tiered pricing engine. Built with Python, Flask, and an embedded relational SQLite database, this system dynamically calculates bulk-order incentives at runtime while enforcing strict state machine tracking and zero-underdraft ledger integrity.

---

## Key Features

* **Dynamic Pricing Engine:** Server-side evaluation of item quantities that dynamically applies volume-based tiered discounts (e.g., up to 20–25% off) instantly before any checkout execution.
* **Asynchronous Preview Pipeline:** Uses client-side JavaScript (Fetch API) to intercept user inputs and run non-blocking backend queries, updating unit prices and total costs in real time without refreshing the page.
* **Atomic State Mutation:** Enforces robust, isolated transactional updates (`UPDATE items SET stock_level = stock_level - Qty`) to ensure race conditions cannot cause stock levels to desynchronize.
* **Zero-Overdraft Database Integrity:** Implements a strict SQL table-level `CHECK (stock_level >= 0)` constraint, serving as an absolute backend safeguard against inventory underflow.

---

##  Architecture & Database Design

The application utilizes an embedded SQLite architecture with two highly relational tables coupled via foreign key constraints:

### 1. Items (`items`)
* Serves as the primary source of truth for current inventory states.
* Fields: `id` (TEXT, PK), `name` (TEXT), `base_price` (REAL), `stock_level` (INTEGER with a `CHECK >= 0` constraint).

### 2. Pricing Tiers (`pricing_tiers`)
* Defines structural boundary levels for volume-based pricing incentives.
* Fields: `item_id` (TEXT, FK referencing `items.id`), `min_quantity` (INTEGER), `discount_percentage` (REAL).

---

##  Tech Stack

* **Backend Engine:** Python 3 (Flask RESTful API configuration)
* **Database Layer:** SQLite (Relational structure and transactional integrity)
* **Frontend Dashboard:** HTML5, CSS3 (Bootstrap 5 Grid & Component System), Vanilla JavaScript (ES6+ Asynchronous Fetch Modules)

---

##  Production REST API Endpoints

### 1. Fetch Live Inventory Monitor
* **Endpoint:** `GET /api/items`
* **Response:** Returns an array of current inventory items along with real-time stock balances.

### 2. Live Price Evaluation 
* **Endpoint:** `POST /api/calculate-price`
* **Payload:** `{"item_id": "prod_001", "quantity": 12}`
* **Response:** Evaluates bulk pricing tiers on the fly and returns discounted unit and total costs.

### 3. Atomic Transaction Checkout
* **Endpoint:** `POST /api/checkout`
* **Payload:** `{"item_id": "prod_003", "quantity": 5}`
* **Response:** Mutates inventory state and executes atomic reduction or handles exception rollback.

---

## Getting Started & Local Deployment

To run this application cleanly on your local machine:

1. Clone the repository:
   ```bash
   git clone [https://github.com/TypicalW/Smart-Inventory.git](https://github.com/TypicalW/Smart-Inventory.git)
   cd Smart-Inventory
