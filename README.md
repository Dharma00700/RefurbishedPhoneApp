# Refurbished Phone Selling Application

This is a Flask-based assignment project to manage and simulate selling refurbished phones.

## Features
- Add / Delete phones
- Bulk CSV upload
- Search and filter by brand, model, condition, or platform
- Automated platform pricing with fees
- Dummy platform integration (mock listing)
- Prevents unprofitable or out-of-stock listings

## Run Instructions
1. Create virtual environment (optional):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate # Mac/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open in browser:
   ```
   http://127.0.0.1:5000
   ```

Upload the provided `phones.csv` using the Bulk Upload option to demo inventory.

