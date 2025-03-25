from collections import defaultdict
from datetime import datetime

sales = [
    {"agent_code": "A101", "product": "LifeCover-Plus", "amount": 1200.0},
    {"agent_code": "A102", "product": "Health-Protect", "amount": 900.0},
    {"agent_code": "A101", "product": "LifeCover-Plus", "amount": 1000.0},
    {"agent_code": "A103", "product": "Health-Protect", "amount": 600.0},
    {"agent_code": "A102", "product": "LifeCover-Plus", "amount": 800.0}
]

def aggregate_sales():
    totals_by_agent = defaultdict(float)
    totals_by_product = defaultdict(float)

    for sale in sales:
        totals_by_agent[sale["agent_code"]] += sale["amount"]
        totals_by_product[sale["product"]] += sale["amount"]

    print(f"[{datetime.now()}] Aggregated sales report:")
    print("Total Sales by Agent:")
    for agent, total in totals_by_agent.items():
        print(f"  - {agent}: ${total:.2f}")

    print("Total Sales by Product:")
    for product, total in totals_by_product.items():
        print(f"  - {product}: ${total:.2f}")

if __name__ == '__main__':
    aggregate_sales()
