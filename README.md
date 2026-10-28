# Streamlit Order Entry App

Web version of the order-entry program. Users choose a customer and product,
enter a quantity, review and confirm the order, and save it to Supabase. Each
saved order is queried again from the database for verification.

**Deployed app:** [Open the Streamlit order-entry app](https://app-assignment-2kzzmejvrzfhkzkvj3davp.streamlit.app/)

The app is password-protected. The access password should be provided privately
through the course submission system, not in this repository.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface and order workflow |
| `Database.py` | Supabase API queries and inserts |
| `Config.py` | Reads credentials from Streamlit secrets or local `.env` |
| `requirements.txt` | Required Python packages |
| `.env.example` | Placeholder values for local development |
| `.gitignore` | Excludes `.env` and `.streamlit/secrets.toml` |

## Run locally

1. Create and activate a virtual environment, then install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and replace the placeholders with your own
   Supabase URL, Supabase secret key, and app password.
3. Run the app:

   ```bash
   streamlit run app.py
   ```

Keep `.env` private; it is excluded by `.gitignore`.

## Streamlit Community Cloud secrets

The local `.env` file is not uploaded to Streamlit Community Cloud. In the
deployed app's **Settings → Secrets**, configure:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_SECRET_KEY = "sb_secret_your_key"
APP_PASSWORD = "your-classroom-password"
```

Save the secrets and restart/redeploy the app. Do not commit the real values to
GitHub. Restrict app access to authorized viewers and provide the password to
the instructor privately.

## How it works

- **Display:** Customers and products are loaded through the Supabase API and
  shown in readable tables with prices formatted as currency. **Refresh Data**
  reloads customers, products, and order history.
- **Validation:** Customer and product dropdowns display names while retaining
  their database IDs. Quantity is a positive whole-number input and is also
  checked before insertion.
- **Saving:** The insert runs only from the submit button callback and only
  after confirmation. The app reads the current product price again at
  submission; if it changed, the updated price is shown and confirmation is
  required again.
- **Verification:** After insertion, the generated order ID is used in a
  separate database query. The verification table shows the retrieved record
  and calculates the total from its stored `unit_price`. If verification fails,
  the app explains that the order was saved but could not be retrieved and does
  not automatically submit it again.
- **Access control:** A password gate reads `APP_PASSWORD` from secrets and runs
  before any database access. This is a classroom access control, not a
  production customer-login system.
- **Extra credit:** Order History includes a customer filter and displays the
  filtered orders' total value using stored sale prices.

The app uses Streamlit, pandas, the Supabase Python client, `python-dotenv`,
Python's `Decimal` for currency calculations, and `hmac.compare_digest` for
password comparison.

## Testing results

Record results after testing the deployed application. Do not mark tests passed
unless they have been run against the hosted URL.

| Test | Expected result | Result |
|---|---|---|
| Open deployed app | Loads after authorized access | Pending |
| View customers and products | Records retrieved from Supabase | Pending |
| Try invalid quantity | Input prevented or rejected | Pending |
| Submit without confirmation | No order inserted | Pending |
| Confirm and submit valid order | Exactly one order inserted | Pending |
| View verification table | New order retrieved from Supabase | Pending |
| Refresh or change another widget | No duplicate order inserted | Pending |
| Refresh order history | Saved order remains visible | Pending |
| Filter order history by customer | Only that customer's orders and their stored-price total appear | Pending |

Add credential-free screenshots after testing:

- `screenshots/order-entry.png` — order-entry interface.
- `screenshots/verified-order.png` — successfully verified order.

## References

- [Streamlit documentation](https://docs.streamlit.io/)
- [Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Supabase Python client](https://supabase.com/docs/reference/python/introduction)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pandas documentation](https://pandas.pydata.org/docs/)
