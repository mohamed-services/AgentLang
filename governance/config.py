"""
AgentLang Council configuration.
To enable/disable an agent, flip its 'enabled' flag.
Phase 1 agents are active; Phase 2/3 agents are stubs ready to activate.
"""

from __future__ import annotations

AGENTS: list[dict] = [
    # ── Phase 1 ──────────────────────────────────────────────────────────────
    {
        "id": "anthropic",
        "name": "Claude",
        "company": "Anthropic",
        "model": "claude-opus-4-6",
        "api_key_env": "ANTHROPIC_API_KEY",
        "agent_class": "anthropic_agent.AnthropicAgent",
        "phase": 1,
        "enabled": True,
    },
    {
        "id": "openai",
        "name": "GPT-4o",
        "company": "OpenAI",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
        "agent_class": "openai_agent.OpenAIAgent",
        "phase": 1,
        "enabled": True,
    },
    {
        "id": "google",
        "name": "Gemini",
        "company": "Google",
        "model": "gemini-2.0-flash",
        "api_key_env": "GOOGLE_API_KEY",
        "agent_class": "google_agent.GoogleAgent",
        "phase": 1,
        "enabled": True,
    },
    {
        "id": "xai",
        "name": "Grok",
        "company": "xAI",
        "model": "grok-2-latest",
        "api_key_env": "XAI_API_KEY",
        "agent_class": "xai_agent.XAIAgent",
        "phase": 1,
        "enabled": True,
    },
    # ── Phase 2 ──────────────────────────────────────────────────────────────
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "company": "DeepSeek",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "agent_class": "deepseek_agent.DeepSeekAgent",
        "phase": 2,
        "enabled": False,
    },
    {
        "id": "alibaba",
        "name": "Qwen",
        "company": "Alibaba",
        "model": "qwen-max",
        "api_key_env": "ALIBABA_API_KEY",
        "agent_class": "alibaba_agent.AlibabaAgent",
        "phase": 2,
        "enabled": False,
    },
    {
        "id": "meta",
        "name": "Llama",
        "company": "Meta",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "api_key_env": "TOGETHER_API_KEY",
        "agent_class": "together_agent.TogetherAgent",
        "phase": 2,
        "enabled": False,
    },
    {
        "id": "mistral",
        "name": "Mistral",
        "company": "Mistral AI",
        "model": "mistral-large-latest",
        "api_key_env": "MISTRAL_API_KEY",
        "agent_class": "mistral_agent.MistralAgent",
        "phase": 2,
        "enabled": False,
    },
    {
        "id": "cohere",
        "name": "Command",
        "company": "Cohere",
        "model": "command-r-plus",
        "api_key_env": "COHERE_API_KEY",
        "agent_class": "cohere_agent.CohereAgent",
        "phase": 2,
        "enabled": False,
    },
    # ── Phase 3 ──────────────────────────────────────────────────────────────
    {
        "id": "microsoft",
        "name": "Phi",
        "company": "Microsoft",
        "model": "microsoft/Phi-3.5-MoE-instruct",
        "api_key_env": "TOGETHER_API_KEY",
        "agent_class": "together_agent.TogetherAgent",
        "phase": 3,
        "enabled": False,
    },
    {
        "id": "nvidia",
        "name": "Nemotron",
        "company": "Nvidia",
        "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "api_key_env": "TOGETHER_API_KEY",
        "agent_class": "together_agent.TogetherAgent",
        "phase": 3,
        "enabled": False,
    },
    {
        "id": "amazon",
        "name": "Nova",
        "company": "Amazon",
        "model": "amazon.nova-pro-v1:0",
        "api_key_env": "AWS_ROLE_ARN",   # OIDC-based; handled in bedrock_agent
        "agent_class": "bedrock_agent.BedrockAgent",
        "phase": 3,
        "enabled": False,
    },
    {
        "id": "ibm",
        "name": "Granite",
        "company": "IBM",
        "model": "ibm/granite-34b-code-instruct",
        "api_key_env": "IBM_API_KEY",
        "agent_class": "ibm_agent.IBMAgent",
        "phase": 3,
        "enabled": False,
    },
    # ── Tracked Abstentions (no public API / restricted access) ───────────────
    {
        "id": "samsung",
        "name": "TRM",
        "company": "Samsung",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "No public API available",
    },
    {
        "id": "apple",
        "name": "AFM",
        "company": "Apple",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "No public API available",
    },
    {
        "id": "bytedance",
        "name": "Doubao",
        "company": "ByteDance",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "Restricted access",
    },
    {
        "id": "minimax",
        "name": "M2",
        "company": "Minimax",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "No public API available",
    },
    {
        "id": "zhipu",
        "name": "GLM",
        "company": "Zhipu AI",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "No public API available",
    },
    {
        "id": "moonshot",
        "name": "Kimi",
        "company": "Moonshot AI",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "No public API available",
    },
    {
        "id": "baidu",
        "name": "ERNIE",
        "company": "Baidu",
        "model": None,
        "api_key_env": None,
        "agent_class": None,
        "phase": None,
        "enabled": False,
        "abstain_reason": "Restricted access",
    },
]

# Voting thresholds
APPROVAL_THRESHOLD = 0.5          # approvals / (approvals + rejections) must exceed this
SUPERMAJORITY_THRESHOLD = 2 / 3   # required for changes to governance/ or .github/

# Directories whose changes trigger the super-majority requirement
PROTECTED_PREFIXES = ("governance/", ".github/")
MAX_DIFF_CHARS = 16_000           # ~4000 tokens; diff truncated beyond this

# Comment marker used to identify bot comments for idempotent updates
VOTE_COMMENT_MARKER = "<!-- agentlang-vote-comment -->"
SUMMARY_COMMENT_MARKER = "<!-- agentlang-summary-comment -->"
VALIDATION_COMMENT_MARKER = "<!-- agentlang-validation-comment -->"
README_COMMENT_MARKER = "<!-- agentlang-readme-comment -->"
