# Streamlit Order Entry

A Streamlit order-entry app that reads customers, products, and order history from
Supabase and inserts confirmed orders. The app uses a server-checked password gate
before accessing the database.

## Files

- `app.py` — Streamlit interface and order workflow.
- `Database.py` — Supabase Data API queries and inserts.
- `Config.py` — Reads app settings from Streamlit secrets or a local `.env`.
- `requirements.txt` — Python package dependencies.
- `.env.example` — Placeholder configuration for local development.

## Run locally

1. Install Python and the packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set your own values:

   ```dotenv
   APP_PASSWORD=choose-a-strong-classroom-password
   SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   SUPABASE_SECRET_KEY=sb_secret_your_key
   ```

   Keep `.env` private; it is excluded by `.gitignore`.

3. Start the app:

   ```bash
   streamlit run app.py
   ```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), create an app from
   this repository and branch, using `app.py` as the entry point.
3. In the app's **Settings → Secrets**, add:

   ```toml
   APP_PASSWORD = "choose-a-strong-classroom-password"
   SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
   SUPABASE_SECRET_KEY = "sb_secret_your_key"
   ```

4. Restrict app access to the instructor and authorized viewers. Provide any
   password privately through the course submission system, not in this README.
5. After deployment, add the working application URL here:

   **Deployed app:** _Pending deployment_

## Testing

The source implements the checks below, but deployment-specific results must be
recorded after testing the hosted app. Do not mark a test as passed until it has
been performed against the deployed URL.

| Test | Result |
|---|---|
| Hosted app opens for an authorized viewer | Pending deployment |
| Customers and products load from Supabase | Pending hosted test |
| Quantity input rejects non-positive/non-whole values | Pending hosted test |
| Submit without confirmation inserts no order | Pending hosted test |
| Confirmed valid submission inserts exactly one order | Pending hosted test |
| Verification table retrieves the saved order by generated ID | Pending hosted test |
| Reruns and widget changes do not insert duplicate orders | Pending hosted test |
| Refresh keeps saved orders visible in order history | Pending hosted test |
| Customer filter and stored-price total work | Pending hosted test |

Add credential-free screenshots after testing:

- `screenshots/order-entry.png` — order-entry interface.
- `screenshots/verified-order.png` — retrieved saved-order verification.

## How it works

The selectboxes show customer and product names while their selected IDs are
retained for database calls. A number input restricts quantity to positive
integers. The review section displays the current displayed price and total;
the confirmation checkbox and submit button gate the insert. On submission,
the app fetches the current product price again and requires fresh confirmation
if it changed. The database supplies the generated order ID and the app performs
a separate query for that ID before showing the verified record. Order history
and its customer filter use records fetched from Supabase.

The app uses Streamlit for the web interface, pandas for table presentation,
the Supabase Python client for Data API calls, `python-dotenv` for local
configuration, and Python's `Decimal` for currency calculations.
