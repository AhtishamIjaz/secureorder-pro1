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
    # Fallback no-op decorator when langchain_core is not installed
    def tool(func=None, **kwargs):
        if func is None:
            def _wrap(f):
                return f
            return _wrap
        return func

# Logic Base: Single Source of Truth
# We store our data in a structured dictionary that mimics a real SQL database.
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


@tool
def request_place_order(order_payload: dict) -> dict:
    """Create a pending place-order action (human approval required)."""
    # The actual execution will be performed by a human operator in the approval queue
    return {"type": "action_request", "action": "place_order", "payload": order_payload}


@tool
def request_cancel_order(order_id: str) -> dict:
    """Create a pending cancel-order action (human approval required)."""
    return {"type": "action_request", "action": "cancel_order", "payload": {"order_id": order_id}}