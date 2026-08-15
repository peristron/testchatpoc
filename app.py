from __future__ import annotations

import hmac

import streamlit as st

from chat_client import ChatAPIError, Provider, stream_chat


st.set_page_config(
    page_title="Chinese AI Gateway",
    layout="wide",
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
    "Qwen": Provider(
        name="Qwen",
        api_key_secret="QWEN_API_KEY",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        default_model="qwen-plus",
        model_secret="QWEN_MODEL",
    ),
    "GLM": Provider(
        name="GLM",
        api_key_secret="GLM_API_KEY",
        base_url="https://api.z.ai/api/paas/v4",
        default_model="glm-5.1",
        model_secret="GLM_MODEL",
    ),
    "MiniMax": Provider(
        name="MiniMax",
        api_key_secret="MINIMAX_API_KEY",
        base_url="https://api.minimax.io/v1",
        default_model="MiniMax-M2.7",
        model_secret="MINIMAX_MODEL",
    ),
}


PORTALS = [
    {
        "name": "DeepSeek",
        "company": "DeepSeek",
        "url": "https://chat.deepseek.com/",
        "description": "General chat, reasoning, writing, and coding.",
        "availability": "International portal",
    },
    {
        "name": "Kimi",
        "company": "Moonshot AI",
        "url": "https://www.kimi.com/",
        "description": "Long-context chat, research, files, and agentic work.",
        "availability": "International portal",
    },
    {
        "name": "Qwen Chat",
        "company": "Alibaba",
        "url": "https://chat.qwen.ai/",
        "description": "Multilingual chat, reasoning, coding, and multimodal tools.",
        "availability": "International portal",
    },
    {
        "name": "Z.ai Chat",
        "company": "Zhipu AI",
        "url": "https://chat.z.ai/",
        "description": "GLM-powered chat, reasoning, research, and agents.",
        "availability": "International portal",
    },
    {
        "name": "MiniMax Agent",
        "company": "MiniMax",
        "url": "https://agent.minimax.io/",
        "description": "General chat and multi-step agent tasks.",
        "availability": "International portal",
    },
    {
        "name": "Doubao",
        "company": "ByteDance",
        "url": "https://www.doubao.com/chat/",
        "description": "Chat, writing, search, images, and creative tools.",
        "availability": "China-focused; regional sign-in may apply",
    },
    {
        "name": "Yuanbao",
        "company": "Tencent",
        "url": "https://yuanbao.tencent.com/",
        "description": "Tencent's consumer assistant for chat and research.",
        "availability": "China-focused; regional sign-in may apply",
    },
    {
        "name": "ERNIE",
        "company": "Baidu",
        "url": "https://ernie.baidu.com/",
        "description": "Baidu's assistant for chat, creation, and web search.",
        "availability": "China-focused; regional sign-in may apply",
    },
    {
        "name": "iFlytek Spark",
        "company": "iFlytek",
        "url": "https://xinghuo.xfyun.cn/desk",
        "description": "Chinese-language chat, writing, and productivity tools.",
        "availability": "China-focused; regional sign-in may apply",
    },
    {
        "name": "StepFun",
        "company": "StepFun",
        "url": "https://www.stepfun.com/",
        "description": "Multimodal chat, search, creation, and agent tools.",
        "availability": "China-focused; regional sign-in may apply",
    },
    {
        "name": "SenseChat",
        "company": "SenseTime",
        "url": "https://chat.sensetime.com/",
        "description": "General-purpose chat and knowledge assistance.",
        "availability": "China-focused; regional sign-in may apply",
    },
]


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

    st.title("Chinese AI Gateway")
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
    st.subheader("Official consumer chat portals")
    st.write(
        "Open any provider's own chat website. No API key is needed, although "
        "the provider may require its normal account, subscription, or regional access."
    )
    st.info(
        "Portal chats open in a new browser tab. Their accounts, conversations, "
        "billing, and privacy terms remain separate from this Streamlit app."
    )

    columns = st.columns(3)
    for index, portal in enumerate(PORTALS):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"#### {portal['name']}")
                st.caption(portal["company"])
                st.write(portal["description"])
                st.caption(portal["availability"])
                st.link_button(
                    f"Open {portal['name']}",
                    portal["url"],
                    use_container_width=True,
                )


def render_api_chat() -> None:
    st.subheader("API chat")
    st.caption(
        "Chat inside this app using API credentials stored in Streamlit secrets."
    )

    available = configured_providers()
    if not available:
        st.warning(
            "No provider API key is configured. Add at least one API key in "
            "Streamlit Community Cloud secrets."
        )
        return

    provider_name = st.selectbox("API provider", available)
    provider = PROVIDERS[provider_name]
    api_key = get_secret(provider.api_key_secret)
    model = get_secret(provider.model_secret, provider.default_model)
    key = conversation_key(provider_name)

    if key not in st.session_state:
        st.session_state[key] = []

    settings_column, action_column = st.columns([4, 1])
    with settings_column:
        system_prompt = st.text_area(
            "System instructions",
            value="You are a helpful, accurate assistant.",
            height=100,
        )
    with action_column:
        st.caption(f"Model: `{model}`")
        if st.button("Clear chat", use_container_width=True):
            st.session_state[key] = []
            st.rerun()

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


def main() -> None:
    require_password()

    with st.sidebar:
        st.header("Chinese AI Gateway")
        st.write(
            "Use official consumer portals without API keys, or chat directly "
            "through APIs you have configured."
        )
        st.divider()
        if st.button("Sign out", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.caption(
            "API requests may incur charges on the app owner's provider accounts."
        )

    st.title("Chinese AI Gateway")
    st.caption("Official chat portals and private API access in one place.")

    portals_tab, api_tab = st.tabs(["Official chat portals", "API chat"])
    with portals_tab:
        render_portals()
    with api_tab:
        render_api_chat()


if __name__ == "__main__":
    main()
