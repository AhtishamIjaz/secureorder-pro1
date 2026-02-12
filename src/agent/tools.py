import os
import requests
import yfinance as yf
from langchain_core.tools import tool

# --- 1. Order & Inventory Tools ---

@tool
def fetch_order_status(order_id: str) -> str:
    """Retrieves status and risk score for a specific Order ID."""
    # Mock Database
    orders = {
        "1001": {"status": "Shipped", "customer": "Alice", "risk_score": 12},
        "1002": {"status": "Processing", "customer": "Bob", "risk_score": 45},
        "1003": {"status": "Pending", "customer": "Charlie", "risk_score": 8}
    }
    order = orders.get(order_id)
    if order:
        return f"Order {order_id} for {order['customer']}: Status is {order['status']}, Risk Score: {order['risk_score']}."
    return f"Order {order_id} not found in the industrial database."

@tool
def search_inventory(product_name: str) -> str:
    """Checks stock levels for industrial products."""
    inventory = {
        "Ultra-Wide Monitor": 15,
        "Wireless Mouse": 0,
        "Mechanical Keyboard": 12,
        "Industrial Sensor": 85
    }
    # Case-insensitive search
    count = next((v for k, v in inventory.items() if product_name.lower() in k.lower()), None)
    if count is not None:
        return f"Current stock for '{product_name}': {count} units."
    return f"Product '{product_name}' not found in inventory records."

@tool
def audit_order_security(order_id: str) -> str:
    """Runs a security audit. High risk (>30) requires manual review."""
    orders = {"1001": 12, "1002": 45, "1003": 8}
    score = orders.get(order_id)
    if score is None: return "Order ID not found for audit."
    
    if score > 30:
        return f"Audit for {order_id}: HIGH RISK (Score: {score}). Recommendation: HOLD SHIPPING."
    return f"Audit for {order_id}: LOW RISK (Score: {score}). Recommendation: PROCEED."

# --- 2. Market & External Data Tools ---

@tool
def get_material_price(symbol: str) -> str:
    """
    Fetches real-time market price for raw materials.
    Common symbols: Copper='HG=F', Aluminum='ALI=F', Gold='GC=F'.
    """
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info['last_price']
        return f"The current market price for {symbol} is ${price:.2f} USD."
    except Exception as e:
        return f"Error fetching price for {symbol}: {str(e)}"

@tool
def get_shipping_weather(city: str) -> str:
    """Fetches current weather to assess transport risks (OpenWeatherMap)."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key: return "Weather API key not configured."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        temp = res['main']['temp']
        desc = res['weather'][0]['description']
        return f"Weather in {city}: {temp}°C with {desc}. Check for transport delays if raining."
    except Exception:
        return f"Could not retrieve weather for {city}. Connectivity issue."

# --- 3. Financial Utility Tool (The "Math-Safe" Version) ---

@tool
def convert_currency(amount: float, from_curr: str = "USD", to_curr: str = "PKR") -> str:
    """
    Converts currency amounts. 
    'amount' MUST be a number (e.g., 100.0), not a math string.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    
    # SAFETY: Force cast to float in case the AI sends a string like "100"
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return "ERROR: The 'amount' provided was not a valid number. Please calculate the result first."

    if not api_key: return "Currency API key missing."
    
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}/{amount}"
    try:
        data = requests.get(url).json()
        result = data['conversion_result']
        return f"{amount} {from_curr} is approximately {result:,.2f} {to_curr}."
    except Exception as e:
        return f"Currency conversion failed: {str(e)}"