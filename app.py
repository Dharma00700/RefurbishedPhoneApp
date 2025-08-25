
from flask import Flask, request, redirect, flash, render_template_string
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "demo_secret"

class Phone:
    counter = 1
    def __init__(self, model, brand, base_price, stock, condition, specs="N/A"):
        self.id = Phone.counter
        Phone.counter += 1
        self.model = model
        self.brand = brand
        self.base_price = base_price
        self.stock = stock
        self.condition = condition
        self.specs = specs

inventory = []

def calculate_platform_prices(base_price):
    return {
        "X": round(base_price * 1.10, 2),
        "Y": round(base_price * 1.08 + 2, 2),
        "Z": round(base_price * 1.12, 2),
    }

def map_condition(platform, condition):
    condition_map = {
        "X": {"New": "New", "Good": "Good", "Scrap": "Scrap"},
        "Y": {"New": "3 stars", "Good": "2 stars", "Scrap": "1 star"},
        "Z": {"New": "New", "Good": "Good", "Scrap": "As New"}
    }
    return condition_map.get(platform, {}).get(condition, None)

@app.route("/", methods=["GET"])
def home():
    query = request.args.get("q", "").lower()
    condition_filter = request.args.get("condition", "")
    platform_filter = request.args.get("platform", "")
    filtered_inventory = inventory

    if query:
        filtered_inventory = [p for p in filtered_inventory if query in p.model.lower() or query in p.brand.lower()]
    if condition_filter:
        filtered_inventory = [p for p in filtered_inventory if p.condition == condition_filter]
    if platform_filter:
        filtered_inventory = [p for p in filtered_inventory if map_condition(platform_filter, p.condition) is not None]

    return render_template_string(TEMPLATE, inventory=filtered_inventory,
                                  query=query, condition_filter=condition_filter,
                                  platform_filter=platform_filter)

@app.route("/add", methods=["POST"])
def add_phone():
    try:
        model = request.form["model"]
        brand = request.form["brand"]
        base_price = float(request.form["base_price"])
        stock = int(request.form["stock"])
        condition = request.form["condition"]
        specs = request.form.get("specs", "N/A")

        if base_price <= 0 or stock < 0:
            flash("Invalid price or stock!", "danger")
            return redirect("/")

        phone = Phone(model, brand, base_price, stock, condition, specs)
        inventory.append(phone)
        flash("Phone added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect("/")

@app.route("/delete/<int:phone_id>")
def delete_phone(phone_id):
    global inventory
    inventory = [p for p in inventory if p.id != phone_id]
    flash("Phone deleted!", "info")
    return redirect("/")

@app.route("/bulk_upload", methods=["POST"])
def bulk_upload():
    file = request.files["file"]
    if file and file.filename.endswith(".csv"):
        csv_text = StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(csv_text)
        for row in reader:
            phone = Phone(row["model"], row["brand"], float(row["base_price"]),
                          int(row["stock"]), row["condition"], row.get("specs", "N/A"))
            inventory.append(phone)
        flash("Bulk upload successful!", "success")
    else:
        flash("Upload a valid CSV file!", "danger")
    return redirect("/")

@app.route("/list/<int:phone_id>/<platform>")
def list_on_platform(phone_id, platform):
    phone = next((p for p in inventory if p.id == phone_id), None)
    if not phone or phone.stock == 0:
        flash("Cannot list: phone out of stock.", "danger")
    else:
        prices = calculate_platform_prices(phone.base_price)
        mapped_condition = map_condition(platform, phone.condition)
        if mapped_condition is None:
            flash(f"{platform} does not support this condition!", "danger")
        else:
            if prices[platform] < 50:
                flash(f"Listing failed on {platform}: unprofitable (too high fees)", "danger")
            else:
                flash(f"Phone listed on {platform} at ${prices[platform]} [{mapped_condition}]", "success")
    return redirect("/")

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Refurbished Phone App</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
<div class="container py-4">
    <h2 class="mb-4">📱 Refurbished Phone Selling</h2>

    <form action="/add" method="post" class="mb-3 d-flex gap-2">
        <input type="text" name="model" placeholder="Model" required class="form-control">
        <input type="text" name="brand" placeholder="Brand" required class="form-control">
        <input type="number" step="0.01" name="base_price" placeholder="Base Price" required class="form-control">
        <input type="number" name="stock" placeholder="Stock" required class="form-control">
        <input type="text" name="specs" placeholder="Specifications" class="form-control">
        <select name="condition" class="form-control">
            <option>New</option>
            <option>Good</option>
            <option>Scrap</option>
        </select>
        <button class="btn btn-success">Add</button>
    </form>

    <form action="/bulk_upload" method="post" enctype="multipart/form-data" class="mb-4">
        <input type="file" name="file" required>
        <button class="btn btn-primary">Bulk Upload</button>
    </form>

    <form method="get" action="/" class="mb-3 d-flex gap-2">
        <input type="text" name="q" value="{{query}}" placeholder="Search by Model/Brand" class="form-control">
        <select name="condition" class="form-control">
            <option value="">All Conditions</option>
            <option value="New" {% if condition_filter=="New" %}selected{% endif %}>New</option>
            <option value="Good" {% if condition_filter=="Good" %}selected{% endif %}>Good</option>
            <option value="Scrap" {% if condition_filter=="Scrap" %}selected{% endif %}>Scrap</option>
        </select>
        <select name="platform" class="form-control">
            <option value="">All Platforms</option>
            <option value="X" {% if platform_filter=="X" %}selected{% endif %}>X</option>
            <option value="Y" {% if platform_filter=="Y" %}selected{% endif %}>Y</option>
            <option value="Z" {% if platform_filter=="Z" %}selected{% endif %}>Z</option>
        </select>
        <button class="btn btn-secondary">Filter</button>
    </form>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for cat, msg in messages %}
          <div class="alert alert-{{cat}}">{{msg}}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <table class="table table-striped">
        <tr>
            <th>ID</th><th>Model</th><th>Brand</th><th>Base Price</th>
            <th>Stock</th><th>Condition</th><th>Specs</th><th>Actions</th>
        </tr>
        {% for phone in inventory %}
        <tr>
            <td>{{phone.id}}</td>
            <td>{{phone.model}}</td>
            <td>{{phone.brand}}</td>
            <td>${{phone.base_price}}</td>
            <td>{{phone.stock}}</td>
            <td>{{phone.condition}}</td>
            <td>{{phone.specs}}</td>
            <td>
                <a href="/delete/{{phone.id}}" class="btn btn-sm btn-danger">Delete</a>
                <a href="/list/{{phone.id}}/X" class="btn btn-sm btn-info">List on X</a>
                <a href="/list/{{phone.id}}/Y" class="btn btn-sm btn-warning">List on Y</a>
                <a href="/list/{{phone.id}}/Z" class="btn btn-sm btn-secondary">List on Z</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
