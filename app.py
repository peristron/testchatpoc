from __future__ import annotations

import hmac

import streamlit as st

from chat_client import ChatAPIError, Provider, stream_chat


st.set_page_config(
    page_title="AI Chat Gateway",
    layout="centered",
)


PROVIDERS = {
    "DeepSeek": Provider(
        name="DeepSeek",
        api_key_secret="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com",
        default_model="deepseek-v4-flash",
        model_secret="DEEPSEEK_MODEL",
    ),
    "Kimi": Provider(
        name="Kimi",
        api_key_secret="KIMI_API_KEY",
        base_url="https://api.moonshot.ai/v1",
        default_model="kimi-k2.6",
        model_secret="KIMI_MODEL",
    ),
}

PORTALS = {
    "DeepSeek": "https://chat.deepseek.com/",
    "Kimi": "https://www.kimi.com/",
    "Qwen": "https://chat.qwen.ai/",
    "GLM": "https://chatglm.cn/?lang=en",
}


def get_secret(name: str, default: str = "") -> str:
    """Read a Streamlit secret without failing when no secrets file exists."""
    try:
        value = st.secrets.get(name, default)
    except (FileNotFoundError, KeyError):
        return default
    return str(value).strip() if value is not None else default


def require_password() -> None:
    """Stop the app until the shared access password is supplied."""
    expected_password = get_secret("APP_PASSWORD")
    if not expected_password:
        st.error(
            "APP_PASSWORD is not configured. Add it to this app's Streamlit "
            "Community Cloud secrets."
        )
        st.stop()

    if st.session_state.get("authenticated", False):
        return

    st.title("AI Chat Gateway")
    st.caption("Enter the shared access password to continue.")

    with st.form("login_form", clear_on_submit=True):
        password = st.text_input("Access password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        if hmac.compare_digest(password, expected_password):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.stop()


def configured_providers() -> list[str]:
    return [
        name
        for name, provider in PROVIDERS.items()
        if get_secret(provider.api_key_secret)
    ]


def conversation_key(provider_name: str) -> str:
    return f"messages_{provider_name.lower()}"


def render_portals() -> None:
    with st.expander("Open official consumer chat sites"):
        st.caption(
            "These open the providers' own websites in a new tab. Their sign-in, "
            "chat history, subscriptions, and privacy terms are separate from this app."
        )
        columns = st.columns(2)
        for index, (name, url) in enumerate(PORTALS.items()):
            with columns[index % 2]:
                st.link_button(
                    f"Open {name}",
                    url,
                    use_container_width=True,
                )


def main() -> None:
    require_password()

    available = configured_providers()

    with st.sidebar:
        st.header("Chat settings")

        if available:
            provider_name = st.selectbox("API provider", available)
        else:
            provider_name = "DeepSeek"

        system_prompt = st.text_area(
            "System instructions",
            value="You are a helpful, accurate assistant.",
            height=110,
        )

        if st.button("Clear this chat", use_container_width=True):
            st.session_state[conversation_key(provider_name)] = []
            st.rerun()

        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()
        st.caption(
            "API requests use the app owner's configured provider account and may "
            "incur usage charges."
        )

    st.title("AI Chat Gateway")
    st.caption("A private Streamlit interface for your configured AI APIs.")
    render_portals()

    if not available:
        st.warning(
            "No provider API key is configured. Add DEEPSEEK_API_KEY to Streamlit "
            "secrets to enable in-app chat. The official portal links remain available."
        )
        st.stop()

    provider = PROVIDERS[provider_name]
    api_key = get_secret(provider.api_key_secret)
    model = get_secret(provider.model_secret, provider.default_model)
    key = conversation_key(provider_name)

    if key not in st.session_state:
        st.session_state[key] = []

    st.subheader(provider.name)
    st.caption(f"Model: `{model}`")

    for message in st.session_state[key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input(f"Message {provider.name}")
    if not prompt:
        return

    st.session_state[key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    request_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state[key],
    ]

    try:
        with st.chat_message("assistant"):
            response = st.write_stream(
                stream_chat(
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    messages=request_messages,
                )
            )
    except ChatAPIError as exc:
        st.session_state[key].pop()
        st.error(str(exc))
        return

    if response:
        st.session_state[key].append(
            {"role": "assistant", "content": str(response)}
        )
    else:
        st.session_state[key].pop()
        st.warning("The provider returned an empty response. Please try again.")


if __name__ == "__main__":
    main()
