import os
import requests
import yfinance as yf
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# --- Schemas for Strict Validation ---
class OrderSchema(BaseModel):
    order_id: str = Field(description="The unique numeric Order ID (e.g., '1001')")

class InventorySchema(BaseModel):
    product_name: str = Field(description="Industrial product name to search (e.g., 'Sensor')")

class MaterialSchema(BaseModel):
    symbol: str = Field(description="Market symbol: Copper='HG=F', Gold='GC=F', Aluminum='ALI=F'")

class WeatherSchema(BaseModel):
    city: str = Field(description="City name to assess transport risk (e.g., 'Karachi')")

class CurrencySchema(BaseModel):
    amount: float = Field(description="Numeric amount to convert (e.g., 500.0)")
    from_curr: str = Field(default="USD", description="3-letter source currency")
    to_curr: str = Field(default="PKR", description="3-letter target currency")

# --- Updated Tools ---
@tool(args_schema=OrderSchema)
def fetch_order_status(order_id: str) -> str:
    """Retrieves status and risk score for a specific Order ID."""
    orders = {
        "1001": {"status": "Shipped", "customer": "Alice", "risk_score": 12},
        "1002": {"status": "Processing", "customer": "Bob", "risk_score": 45},
        "1003": {"status": "Pending", "customer": "Charlie", "risk_score": 8}
    }
    order = orders.get(order_id)
    return f"Order {order_id}: {order['status']}, Risk: {order['risk_score']}" if order else "Not found."

@tool(args_schema=InventorySchema)
def search_inventory(product_name: str) -> str:
    """Checks stock levels for industrial products."""
    inventory = {"Ultra-Wide Monitor": 15, "Industrial Sensor": 85}
    count = next((v for k, v in inventory.items() if product_name.lower() in k.lower()), 0)
    return f"Stock for '{product_name}': {count} units."

@tool(args_schema=OrderSchema)
def audit_order_security(order_id: str) -> str:
    """Runs a security audit. High risk (>30) requires manual review."""
    scores = {"1001": 12, "1002": 45, "1003": 8}
    score = scores.get(order_id, 0)
    recommend = "HOLD" if score > 30 else "PROCEED"
    return f"Audit {order_id}: {recommend} (Score: {score})"

@tool(args_schema=MaterialSchema)
def get_material_price(symbol: str) -> str:
    """Fetches real-time market price for raw materials."""
    try:
        price = yf.Ticker(symbol).fast_info['last_price']
        return f"Price for {symbol}: ${price:.2f} USD."
    except Exception as e: return f"Market Error: {str(e)}"

@tool(args_schema=WeatherSchema)
def get_shipping_weather(city: str) -> str:
    """Assess transport risks via OpenWeatherMap."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        return f"Weather in {city}: {res['main']['temp']}°C, {res['weather'][0]['description']}."
    except: return "Weather data unavailable."

@tool(args_schema=CurrencySchema)
def convert_currency(amount: float, from_curr: str = "USD", to_curr: str = "PKR") -> str:
    """Converts industrial currency amounts accurately."""
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}/{amount}"
    try:
        res = requests.get(url).json()
        return f"{amount} {from_curr} is {res['conversion_result']:,.2f} {to_curr}."
    except Exception as e: return f"FX Error: {str(e)}"