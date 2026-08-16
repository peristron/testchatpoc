from __future__ import annotations

import hmac

import streamlit as st

from chat_client import ChatAPIError, Provider, stream_chat


st.set_page_config(
    page_title="AI Gateway",
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
        default_model="glm-4.7-flash",
        model_secret="GLM_MODEL",
    ),
    "MiniMax": Provider(
        name="MiniMax",
        api_key_secret="MINIMAX_API_KEY",
        base_url="https://api.minimax.io/v1",
        default_model="MiniMax-M2.7",
        model_secret="MINIMAX_MODEL",
    ),
    "Mistral": Provider(
        name="Mistral",
        api_key_secret="MISTRAL_API_KEY",
        base_url="https://api.mistral.ai/v1",
        default_model="mistral-small-latest",
        model_secret="MISTRAL_MODEL",
    ),
    "Cohere": Provider(
        name="Cohere",
        api_key_secret="COHERE_API_KEY",
        base_url="https://api.cohere.ai/compatibility/v1",
        default_model="command-a-plus-05-2026",
        model_secret="COHERE_MODEL",
    ),
    "SEA-LION": Provider(
        name="SEA-LION",
        api_key_secret="SEALION_API_KEY",
        base_url="https://api.sea-lion.ai/v1",
        default_model="aisingapore/Gemma-SEA-LION-v4-27B-IT",
        model_secret="SEALION_MODEL",
    ),
}


PORTALS = [
    {
        "name": "DeepSeek",
        "company": "DeepSeek",
        "url": "https://chat.deepseek.com/",
        "description": "General chat, reasoning, writing, and coding.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "Kimi",
        "company": "Moonshot AI",
        "url": "https://www.kimi.com/",
        "description": "Long-context chat, research, files, and agentic work.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "Qwen Chat",
        "company": "Alibaba",
        "url": "https://chat.qwen.ai/",
        "description": "Multilingual chat, reasoning, coding, and multimodal tools.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "Z.ai Chat",
        "company": "Zhipu AI",
        "url": "https://chat.z.ai/",
        "description": "GLM-powered chat, reasoning, research, and agents.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "MiniMax Agent",
        "company": "MiniMax",
        "url": "https://agent.minimax.io/",
        "description": "General chat and multi-step agent tasks.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "Doubao",
        "company": "ByteDance",
        "url": "https://www.doubao.com/chat/",
        "description": "Chat, writing, search, images, and creative tools.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "Yuanbao",
        "company": "Tencent",
        "url": "https://yuanbao.tencent.com/",
        "description": "Tencent's consumer assistant for chat and research.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "ERNIE",
        "company": "Baidu",
        "url": "https://ernie.baidu.com/",
        "description": "Baidu's assistant for chat, creation, and web search.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "iFlytek Spark",
        "company": "iFlytek",
        "url": "https://xinghuo.xfyun.cn/desk",
        "description": " -language chat, writing, and productivity tools.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "StepFun",
        "company": "StepFun",
        "url": "https://www.stepfun.com/",
        "description": "Multimodal chat, search, creation, and agent tools.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "SenseChat",
        "company": "SenseTime",
        "url": "https://chat.sensetime.com/",
        "description": "General-purpose chat and knowledge assistance.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "Falcon Chat",
        "company": "Technology Innovation Institute (UAE)",
        "url": "https://chat.falconllm.tii.ae/",
        "description": "Official chat experience for TII's Falcon model family.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "Mistral Vibe",
        "company": "Mistral AI (France)",
        "url": "https://chat.mistral.ai/",
        "description": "Mistral's chat and productivity agent, formerly Le Chat.",
        "availability": "International portal; free tier available",
        "type": "Chat portal",
    },
    {
        "name": "Sakana Chat",
        "company": "Sakana AI (Japan)",
        "url": "https://chat.sakana.ai/",
        "description": "Official Japanese-language research chat experience.",
        "availability": "Japan-focused; availability may vary",
        "type": "Chat portal",
    },
    {
        "name": "Baixiaoying",
        "company": "Baichuan AI",
        "url": "https://ying.baichuan-ai.com/chat",
        "description": "Baichuan's consumer assistant for chat and search.",
        "availability": "Mainland asia only",
        "type": "Chat portal",
    },
    {
        "name": "InternLM Chat",
        "company": "Shanghai AI Laboratory",
        "url": "https://chat.intern-ai.org.cn/",
        "description": "Chat with InternLM, InternVL, and scientific reasoning models.",
        "availability": "asia-focused; regional sign-in may apply",
        "type": "Chat portal",
    },
    {
        "name": "Skywork",
        "company": "Skywork AI",
        "url": "https://skywork.ai/app",
        "description": "General chat plus research, documents, slides, and agents.",
        "availability": "International portal",
        "type": "Chat portal",
    },
    {
        "name": "AI21 Studio",
        "company": "AI21 Labs (Israel)",
        "url": "https://studio.ai21.com/",
        "description": "Official playground for Jamba chat models.",
        "availability": "Developer account required; no key pasted into this app",
        "type": "Developer playground",
    },
    {
        "name": "Cohere Playground",
        "company": "Cohere (Canada)",
        "url": "https://dashboard.cohere.com/playground/chat",
        "description": "Official playground for Command models; Aya availability depends on Cohere's current catalog.",
        "availability": "Free Cohere account required",
        "type": "Developer playground",
    },
    {
        "name": "ChatEXAONE Beta",
        "company": "LG AI Research (South Korea)",
        "url": "https://chat.exaone.ai/",
        "description": "Public beta work agent powered by the EXAONE model family.",
        "availability": "Korea-focused; account or regional access may apply",
        "type": "Developer playground",
    },
    {
        "name": "SEA-LION Playground",
        "company": "AI Singapore",
        "url": "https://playground.sea-lion.ai/",
        "description": "Explore models designed for Southeast Asian languages and contexts.",
        "availability": "Sign-in required",
        "type": "Developer playground",
    },
    {
        "name": "Sarvam Experience",
        "company": "Sarvam AI (India)",
        "url": "https://try.sarvam.ai/",
        "description": "Explore Sarvam's Indian-language voice, reasoning, and agent products.",
        "availability": "Contact details may be required",
        "type": "Product / model site",
    },
    {
        "name": "LightOn Paradigm",
        "company": "LightOn (France)",
        "url": "https://paradigm.lighton.ai/",
        "description": "Enterprise workspace for Paradigm chat, search, and agents.",
        "availability": "Existing customer or trial access required",
        "type": "Product / model site",
    },
    {
        "name": "Aleph Alpha",
        "company": "Aleph Alpha (Germany)",
        "url": "https://aleph-alpha.com/",
        "description": "Official product site for sovereign enterprise language-model solutions.",
        "availability": "No current public consumer playground",
        "type": "Product / model site",
    },
    {
        "name": "StableLM",
        "company": "Stability AI (UK)",
        "url": "https://github.com/Stability-AI/StableLM",
        "description": "Official open-model repository; no maintained first-party browser chat.",
        "availability": "Model access and self-hosting resources",
        "type": "Product / model site",
    },
    {
        "name": "Yi Models",
        "company": "01.AI",
        "url": "https://github.com/01-ai/Yi",
        "description": "Official Yi model repository; no current maintained consumer chat portal.",
        "availability": "Model access and self-hosting resources",
        "type": "Product / model site",
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

    st.title("AI Gateway")
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
    st.subheader("Official AI access portals")
    st.write(
        "Open a provider's own chat site, developer playground, or product demo. "
        "No API key is sent by this app, although the destination may require its "
        "normal account, subscription, invitation, or regional access."
    )
    st.info(
        "Portal chats open in a new browser tab. Their accounts, conversations, "
        "billing, and privacy terms remain separate from this Streamlit app."
    )

    portal_filter = st.radio(
        "Show",
        ["All", "Chat portal", "Developer playground", "Product / model site"],
        horizontal=True,
        label_visibility="collapsed",
    )
    visible_portals = (
        PORTALS
        if portal_filter == "All"
        else [portal for portal in PORTALS if portal["type"] == portal_filter]
    )

    columns = st.columns(3)
    for index, portal in enumerate(visible_portals):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"#### {portal['name']}")
                st.caption(f"{portal['company']} | {portal['type']}")
                st.write(portal["description"])
                st.caption(portal["availability"])
                st.link_button(
                    f"Visit {portal['name']}",
                    portal["url"],
                    use_container_width=True,
                )

    with st.expander("Coverage notes"):
        st.markdown(
            "- Tencent Hunyuan is represented by Yuanbao.\n"
            "- ChatGLM is represented by Z.ai Chat.\n"
            "- Step-1 and Step-2 are represented by StepFun.\n"
            "- Jamba is accessed through AI21 Studio.\n"
            "- Command and Aya are represented by Cohere's playground.\n"
            "- HyperCLOVA X's CLOVA X consumer service closed on April 9, 2026.\n"
            "- StableLM and Yi are linked to official model repositories because "
            "neither currently has a maintained first-party consumer chat portal."
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
        st.header("AI Gateway")
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

    st.title("AI Gateway")
    st.caption("Official chat portals and private API access in one place.")

    portals_tab, api_tab = st.tabs(["Official AI portals", "API chat"])
    with portals_tab:
        render_portals()
    with api_tab:
        render_api_chat()


if __name__ == "__main__":
    main()
