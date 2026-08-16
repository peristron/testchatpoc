from __future__ import annotations

import base64
import hmac
import json
from datetime import datetime, timezone

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
    "GLM Vision": Provider(
        name="GLM Vision",
        api_key_secret="GLM_API_KEY",
        base_url="https://api.z.ai/api/paas/v4",
        default_model="glm-4.6v-flash",
        model_secret="GLM_VISION_MODEL",
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


MAX_IMAGES_PER_MESSAGE = 3
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_TOTAL_IMAGE_BYTES = 10 * 1024 * 1024
SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg", "webp"]


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
        "url": "https://skywork.ai/?sk_fg=app",
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


def provider_supports_images(provider_name: str, model: str) -> bool:
    """Return whether the selected provider/model accepts image inputs."""
    normalized_model = model.lower()
    if provider_name == "GLM Vision":
        return "v" in normalized_model
    if provider_name == "Cohere":
        return "vision" in normalized_model or "command-a-plus" in normalized_model
    if provider_name == "Mistral":
        return any(
            family in normalized_model
            for family in (
                "mistral-small",
                "mistral-medium",
                "mistral-large",
                "ministral",
            )
        )
    return False


def encode_image(uploaded_file) -> dict[str, object]:
    """Convert a Streamlit upload to session-safe attachment data."""
    raw_data = uploaded_file.getvalue()
    return {
        "name": uploaded_file.name,
        "media_type": uploaded_file.type or "image/png",
        "size_bytes": len(raw_data),
        "data": base64.b64encode(raw_data).decode("ascii"),
    }


def message_for_api(
    message: dict[str, object], provider_name: str
) -> dict[str, object]:
    """Convert a stored display message to an API-compatible message."""
    attachments = message.get("attachments") or []
    if not attachments:
        return {"role": message["role"], "content": message["content"]}

    content: list[dict[str, object]] = [
        {"type": "text", "text": str(message["content"])}
    ]
    for attachment in attachments:
        data_url = (
            f"data:{attachment['media_type']};base64,{attachment['data']}"
        )
        if provider_name == "Mistral":
            image_url: object = data_url
        else:
            image_url = {"url": data_url}
        content.append({"type": "image_url", "image_url": image_url})

    return {"role": message["role"], "content": content}


def render_stored_message(message: dict[str, object]) -> None:
    """Render a chat message and any images kept in session memory."""
    st.markdown(str(message["content"]))
    for attachment in message.get("attachments") or []:
        try:
            image_data = base64.b64decode(str(attachment["data"]))
        except (KeyError, ValueError):
            continue
        st.image(image_data, caption=str(attachment.get("name", "Uploaded image")))


def exportable_message(message: dict[str, object]) -> dict[str, object]:
    """Remove image bytes while preserving useful attachment metadata."""
    exported = {
        "role": message["role"],
        "content": message["content"],
    }
    attachments = message.get("attachments") or []
    if attachments:
        exported["attachments"] = [
            {
                "name": attachment.get("name", "Uploaded image"),
                "media_type": attachment.get("media_type", ""),
                "size_bytes": attachment.get("size_bytes", 0),
            }
            for attachment in attachments
        ]
    return exported


def chat_as_markdown(
    provider_name: str, model: str, messages: list[dict[str, object]]
) -> str:
    """Create a readable transcript for one provider conversation."""
    lines = [f"# {provider_name} chat", "", f"Model: `{model}`", ""]
    for message in messages:
        role = "User" if message["role"] == "user" else "Assistant"
        lines.extend([f"## {role}", "", str(message["content"]), ""])
        attachments = message.get("attachments") or []
        if attachments:
            names = ", ".join(
                str(attachment.get("name", "Uploaded image"))
                for attachment in attachments
            )
            lines.extend([f"Attachments: {names}", ""])
    return "\n".join(lines)


def all_chats_as_json() -> str:
    """Create a portable export of every non-empty provider conversation."""
    conversations: dict[str, list[dict[str, object]]] = {}
    for provider_name in PROVIDERS:
        messages = st.session_state.get(conversation_key(provider_name), [])
        if messages:
            conversations[provider_name] = [
                exportable_message(message) for message in messages
            ]

    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "conversations": conversations,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


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
        "Each provider keeps a separate chat for this browser session. Switching "
        "providers does not delete the other conversations."
    )

    available = configured_providers()
    if not available:
        st.warning(
            "No provider API key is configured. Add at least one API key in "
            "Streamlit Community Cloud secrets."
        )
        return

    provider_state_key = "selected_api_provider"
    if st.session_state.get(provider_state_key) not in available:
        st.session_state[provider_state_key] = available[0]

    provider_name = st.selectbox(
        "API provider",
        available,
        key=provider_state_key,
    )
    saved_counts = [
        f"{name}: {len(st.session_state.get(conversation_key(name), []))}"
        for name in available
        if st.session_state.get(conversation_key(name), [])
    ]
    if saved_counts:
        st.caption("Saved this session | " + " | ".join(saved_counts))
    provider = PROVIDERS[provider_name]
    api_key = get_secret(provider.api_key_secret)
    model = get_secret(provider.model_secret, provider.default_model)
    key = conversation_key(provider_name)

    if key not in st.session_state:
        st.session_state[key] = []

    settings_column, model_column = st.columns([4, 1])
    with settings_column:
        system_prompt = st.text_area(
            "System instructions",
            value="You are a helpful, accurate assistant.",
            height=100,
        )
    with model_column:
        st.caption(f"Model: `{model}`")

    messages = st.session_state[key]
    action_columns = st.columns(3)
    with action_columns[0]:
        if st.button("Clear this chat", use_container_width=True):
            st.session_state[key] = []
            st.rerun()
    with action_columns[1]:
        st.download_button(
            "Download this chat",
            data=chat_as_markdown(provider_name, model, messages),
            file_name=f"{provider_name.lower().replace(' ', '-')}-chat.md",
            mime="text/markdown",
            disabled=not messages,
            use_container_width=True,
        )
    with action_columns[2]:
        st.download_button(
            "Download all chats",
            data=all_chats_as_json(),
            file_name="ai-gateway-chats.json",
            mime="application/json",
            disabled=not any(
                st.session_state.get(conversation_key(name), [])
                for name in PROVIDERS
            ),
            use_container_width=True,
        )
    st.caption(
        "Downloads include chat text and attachment names, but not the image files."
    )

    for message in messages:
        with st.chat_message(message["role"]):
            render_stored_message(message)

    uploaded_images = []
    image_enabled = provider_supports_images(provider_name, model)
    if image_enabled:
        nonce_key = f"upload_nonce_{provider_name.lower()}"
        if nonce_key not in st.session_state:
            st.session_state[nonce_key] = 0
        uploaded_images = st.file_uploader(
            "Attach screenshots or images",
            type=SUPPORTED_IMAGE_TYPES,
            accept_multiple_files=True,
            key=f"image_upload_{provider_name}_{st.session_state[nonce_key]}",
            help=(
                f"Up to {MAX_IMAGES_PER_MESSAGE} images, 5 MB each and 10 MB total. "
                "Images are sent to the selected API provider."
            ),
        )
        st.caption(
            "Attached images stay in this browser session and may be resent to the "
            "same provider with later messages to preserve context."
        )
    else:
        st.caption(
            "Image upload is unavailable for this provider's configured model."
        )

    prompt = st.chat_input(f"Message {provider.name}")
    if not prompt:
        return

    attachments: list[dict[str, object]] = []
    if uploaded_images:
        if len(uploaded_images) > MAX_IMAGES_PER_MESSAGE:
            st.error(f"Attach no more than {MAX_IMAGES_PER_MESSAGE} images at once.")
            return
        total_size = sum(len(upload.getvalue()) for upload in uploaded_images)
        if any(len(upload.getvalue()) > MAX_IMAGE_BYTES for upload in uploaded_images):
            st.error("Each image must be 5 MB or smaller.")
            return
        if total_size > MAX_TOTAL_IMAGE_BYTES:
            st.error("The combined image size must be 10 MB or smaller.")
            return
        attachments = [encode_image(upload) for upload in uploaded_images]

    user_message: dict[str, object] = {"role": "user", "content": prompt}
    if attachments:
        user_message["attachments"] = attachments

    messages.append(user_message)
    with st.chat_message("user"):
        render_stored_message(user_message)

    request_messages = [
        {"role": "system", "content": system_prompt},
        *[message_for_api(message, provider_name) for message in messages],
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
        messages.pop()
        st.error(str(exc))
        return

    if response:
        messages.append({"role": "assistant", "content": str(response)})
        if attachments:
            st.session_state[nonce_key] += 1
            st.rerun()
    else:
        messages.pop()
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
