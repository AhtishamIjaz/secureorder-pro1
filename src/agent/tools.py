import os
import requests
import yfinance as yf

try:
    try:
        from langchain_core.tools import tool
    except Exception:
        # Fallback no-op decorator when langchain_core is not installed
        def tool(func=None, **kwargs):
            if func is None:
                def _wrap(f):
                    return f
                return _wrap
            return func
except Exception:
    def tool(func=None, **kwargs):
        if func is None:
            def _wrap(f):
                return f
            return _wrap
        return func

# --- Logic Base: Single Source of Truth ---
DATABASE = {
    "orders": {
        "1001": {"status": "Shipped", "customer": "Alice", "eta": "2026-02-15", "items": ["Ultra-Wide Monitor"]},
        "1002": {"status": "Processing", "customer": "Bob", "eta": "2026-02-18", "items": ["Mechanical Keyboard"]},
        "1003": {"status": "Pending", "customer": "Charlie", "eta": "2026-02-20", "items": ["Wireless Mouse"]},
    },
    "inventory": [
        {"id": "p1", "name": "Ultra-Wide Monitor", "stock": 5, "price": "$450"},
        {"id": "p2", "name": "Mechanical Keyboard", "stock": 12, "price": "$120"},
        {"id": "p3", "name": "Wireless Mouse", "stock": 0, "price": "$80"},
    ]
}

# --- Original Tools ---

@tool
def fetch_order_status(order_id: str) -> dict:
    """Return structured order info for a given order ID."""
    order = DATABASE["orders"].get(order_id)
    if order:
        return {
            "type": "order",
            "order": {
                "order_id": order_id,
                "status": order.get("status"),
                "customer": order.get("customer"),
                "eta": order.get("eta"),
                "items": order.get("items", []),
            },
            "text": f"Order {order_id}: Status is '{order['status']}', ETA is {order['eta']}. Items: {', '.join(order['items'])}."
        }
    return {"type": "error", "message": f"Order ID {order_id} not found"}

@tool
def search_inventory(product_name: str) -> dict:
    """Return structured inventory search results."""
    if not product_name:
        items = DATABASE.get("inventory", [])
    else:
        items = [p for p in DATABASE["inventory"] if product_name.lower() in p["name"].lower()]
    if items:
        return {"type": "inventory_search", "items": items, "text": f"Found {len(items)} items."}
    return {"type": "inventory_search", "items": [], "text": f"No products found matching '{product_name}'."}

@tool
def audit_order_security(order_id: str) -> dict:
    """Return a structured security audit for an order."""
    order = DATABASE["orders"].get(order_id)
    if not order:
        return {"type": "security_audit", "order_id": order_id, "status": "not_found", "risk_score": None, "findings": []}

    risk_score = 0
    reasons = []
    if any("Monitor" in item for item in order.get("items", [])):
        risk_score += 40
        reasons.append("High-value electronics detected")
    if order.get("status") == "Pending":
        risk_score += 30
        reasons.append("Order is in unverified 'Pending' state")

    status = "SECURE" if risk_score < 50 else "WARNING: REQUIRES REVIEW"
    return {
        "type": "security_audit",
        "order_id": order_id,
        "status": status,
        "risk_score": risk_score,
        "findings": reasons,
        "text": f"Audit {order_id}: {status} (score={risk_score})"
    }

# --- NEW Enhancement Tools ---

@tool
def get_material_price(ticker: str) -> str:
    """
    Fetch live price for industrial materials using Yahoo Finance.
    Examples: 'HG=F' (Copper), 'ALI=F' (Aluminum), 'GC=F' (Gold).
    """
    try:
        data = yf.Ticker(ticker)
        # fast_info gives the most recent market price
        price = data.fast_info['last_price']
        return f"Live market update: The price for {ticker} is ${price:.2f}."
    except Exception:
        return f"Error: Could not retrieve live price for {ticker}. Please check the symbol."

@tool
def get_shipping_weather(city: str) -> str:
    """
    Check current weather conditions in a city to predict shipping or production delays.
    Requires OPENWEATHER_API_KEY in environment variables.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key not found in server settings."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        condition = response['weather'][0]['description']
        temp = response['main']['temp']
        return f"Weather Report for {city}: {condition.capitalize()}, {temp}°C. Check for potential logistics delays if conditions are severe."
    except Exception:
        return f"Error: Could not fetch weather data for {city}."

@tool
def convert_currency(amount: float, from_curr: str, to_curr: str) -> str:
    """
    Convert an amount from one currency to another (e.g., USD to PKR).
    Requires EXCHANGE_RATE_API_KEY in environment variables.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        return "Error: ExchangeRate API key not found in server settings."

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}/{amount}"
    try:
        response = requests.get(url).json()
        result = response['conversion_result']
        return f"Currency Conversion: {amount} {from_curr} is approximately {result:.2f} {to_curr}."
    except Exception:
        return "Error: Currency conversion service is currently unavailable."

# --- Human-in-the-Loop Tools ---

@tool
def request_place_order(order_payload: dict) -> dict:
    """Create a pending place-order action (human approval required)."""
    return {"type": "action_request", "action": "place_order", "payload": order_payload}

@tool
def request_cancel_order(order_id: str) -> dict:
    """Create a pending cancel-order action (human approval required)."""
    return {"type": "action_request", "action": "cancel_order", "payload": {"order_id": order_id}}