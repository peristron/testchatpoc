# AI Chat Gateway

A small password-protected Streamlit app for chatting through the DeepSeek API,
with optional Kimi API support and links to official consumer chat websites.

## What this app does

- Protects the app with a shared password stored in Streamlit secrets.
- Streams DeepSeek responses in a basic multi-turn chat interface.
- Enables Kimi in the same interface when a Kimi Open Platform key is added.
- Keeps separate in-memory chat history for each API provider.
- Opens DeepSeek, Kimi, Qwen, and GLM consumer portals in new browser tabs.

Consumer websites are not embedded or proxied. Their sessions, memberships,
history, and privacy terms remain separate from this Streamlit app.

## Repository contents

```text
.
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── .gitignore
├── app.py
├── chat_client.py
├── README.md
└── requirements.txt
```

## Local setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
4. Put your real values only in `.streamlit/secrets.toml`.
5. Run:

   ```bash
   streamlit run app.py
   ```

The real `.streamlit/secrets.toml` is ignored by Git and must never be committed.

## Deploy on Streamlit Community Cloud

1. Upload these files to a public GitHub repository.
2. In Streamlit Community Cloud, create a new app from that repository.
3. Set the entry point to `app.py`.
4. Open the app's **Settings > Secrets** and add:

   ```toml
   APP_PASSWORD = "your-long-unique-access-password"
   DEEPSEEK_API_KEY = "your-deepseek-api-key"
   DEEPSEEK_MODEL = "deepseek-v4-flash"
   ```

5. Save the secrets and reboot the app if Streamlit does not restart it.

## Optional Kimi API chat

Kimi's consumer membership does not provide API access. Create a separate API
key on the international Kimi Open Platform, then add these Cloud secrets:

```toml
KIMI_API_KEY = "your-kimi-open-platform-api-key"
KIMI_MODEL = "kimi-k2.6"
```

After the app restarts, Kimi appears in the API provider selector.

## Security notes

- A shared password is suitable for a small personal app, not for multiple users
  who need separate identities or permissions.
- Anyone who knows the shared password can spend the configured API account's
  balance.
- Rotate the password and API keys if they are exposed.
- Review provider data-handling terms before sending sensitive information.
- Streamlit session history is temporary and disappears when the session ends.
