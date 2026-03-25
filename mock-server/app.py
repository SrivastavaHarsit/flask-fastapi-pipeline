import json
import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# Load customer data once at startup
data_path = os.path.join(os.path.dirname(__file__), "data", "customers.json")
with open(data_path, "r") as f:
    customers = json.load(f)


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/customers")
def get_customers():
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    start = (page - 1) * limit
    end = start + limit

    return jsonify({
        "data": customers[start:end],
        "total": len(customers),
        "page": page,
        "limit": limit
    })


@app.route("/api/customers/<customer_id>")
def get_customer(customer_id):
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return jsonify(customer)

    return jsonify({"error": "Customer not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
