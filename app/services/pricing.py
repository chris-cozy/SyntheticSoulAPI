"""Versioned USD estimates, independent of routing and provider invoices.

Sources, checked 2026-10-11:
https://developers.openai.com/api/docs/pricing
https://developers.openai.com/api/docs/guides/decisions
https://developers.openai.com/api/docs/models/gpt-4o-mini
https://developers.openai.com/api/docs/models/gpt-4o
https://developers.openai.com/api/docs/models/gpt-5-mini
Rates are per million tokens. Unknown models/tiers remain explicitly unknown.
"""
from decimal import Decimal
from typing import Any

PRICING_VERSION = "openai-2026-10-11-v1"
PRICING_SOURCE = "https://developers.openai.com/api/docs/pricing"
MILLION = Decimal(1_000_000)
# Ordinary input, cache read, cache write, output.
RATES = {
    "gpt-6-luna": ("0.10", "0.01", "0.125", "0.50"),
    "gpt-6-sol": ("2.00", "0.20", "2.50", "10.00"),
    "gpt-6.1-sol": ("2.00", "0.10", "2.50", "10.00"),
    "gpt-6-astra": ("10.00", "1.00", "12.50", "50.00"),
    "gpt-4o-mini": ("0.15", "0.075", None, "0.60"),
    "gpt-4o": ("2.50", "1.25", None, "10.00"),
    "gpt-5-mini": ("0.25", "0.025", None, "2.00"),
}
SNAPSHOTS = {
    "gpt-4o-mini-2024-07-18": "gpt-4o-mini",
    "gpt-4o-2024-08-06": "gpt-4o", "gpt-4o-2024-11-20": "gpt-4o",
    "gpt-5-mini-2025-08-07": "gpt-5-mini",
}


def normalize_usage(raw: Any, *, decisions: bool = False) -> dict | None:
    if not isinstance(raw, dict):
        return None
    details = raw.get("input_tokens_details", raw.get("prompt_tokens_details")) or {}
    output_details = raw.get("output_tokens_details", raw.get("completion_tokens_details")) or {}
    if not isinstance(details, dict) or not isinstance(output_details, dict):
        return None
    values = {
        "input_tokens": raw.get("input_tokens", raw.get("prompt_tokens")),
        "output_tokens": raw.get("output_tokens", raw.get("completion_tokens", 0 if decisions else None)),
        "cached_tokens": details.get("cached_tokens", 0),
        "cache_write_tokens": details.get("cache_write_tokens", 0),
        "reasoning_tokens": output_details.get("reasoning_tokens", 0),
    }
    if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in values.values()):
        return None
    if values["cached_tokens"] + values["cache_write_tokens"] > values["input_tokens"]:
        return None
    if values["reasoning_tokens"] > values["output_tokens"]:
        return None
    return values


def estimate_cost(provider: str, endpoint: str, model: str | None, usage: dict | None,
                  tier: str = "default", regional: bool = False) -> dict:
    snapshot = {"version": PRICING_VERSION, "source": PRICING_SOURCE, "currency": "USD",
                "model": model, "endpoint": endpoint, "service_tier": tier, "regional": regional}
    if provider in {"ollama", "local"}:
        return {"cost_usd": "0", "known": True, "unknown_reason": None,
                "pricing": {**snapshot, "note": "Local API charge only; operating costs excluded."}}
    def unknown(reason):
        return {"cost_usd": None, "known": False, "unknown_reason": reason, "pricing": snapshot}
    if provider not in {"openai", "hosted"}:
        return unknown("unsupported_provider")
    if usage is None:
        return unknown("missing_or_invalid_usage")
    canonical = SNAPSHOTS.get(model, model)
    if canonical not in RATES:
        return unknown("unknown_model_pricing")
    if endpoint == "decisions":
        if canonical != "gpt-6-luna" or tier not in {"default", "standard", "auto"}:
            return unknown("unknown_decisions_pricing")
        # Decisions bills total input once; caches/output do not add charges.
        rate = Decimal("0.10") * (2 if usage["input_tokens"] > 272_000 else 1)
        if regional:
            rate *= Decimal("1.1")
        cost = Decimal(usage["input_tokens"]) * rate / MILLION
        snapshot.update({"context_band": "long" if usage["input_tokens"] > 272_000 else "short",
                         "input_rate": str(rate), "cache_read_rate": "0", "cache_write_rate": "0",
                         "output_rate": "0", "input_basis": "total_input_tokens"})
    elif endpoint in {"chat.completions", "chat_completions", "responses"}:
        if tier not in {"default", "standard", "auto", "batch", "flex", "fast", "priority", "ultrafast"}:
            return unknown("unknown_service_tier")
        modern = canonical.startswith("gpt-6")
        # Older models' nonstandard tier prices must be independently verified.
        if not modern and tier not in {"default", "standard", "auto", "batch"}:
            return unknown("unknown_model_tier_pricing")
        if tier == "ultrafast" and canonical not in {"gpt-6-astra", "gpt-6.1-sol"}:
            return unknown("unknown_model_tier_pricing")
        factor = Decimal("0.5") if tier in {"batch", "flex"} else Decimal(2) if tier in {"fast", "priority"} else Decimal(6) if tier == "ultrafast" else Decimal(1)
        if regional and modern:
            factor *= Decimal("1.1")
        rates = [Decimal(v) * factor if v is not None else None for v in RATES[canonical]]
        long = modern and usage["input_tokens"] > 272_000
        if long:
            rates = [r * (Decimal("1.5") if i == 3 else 2) if r is not None else None for i, r in enumerate(rates)]
        ordinary = usage["input_tokens"] - usage["cached_tokens"] - usage["cache_write_tokens"]
        if usage["cache_write_tokens"] and rates[2] is None:
            return unknown("unknown_cache_write_pricing")
        cost = (Decimal(ordinary) * rates[0] + Decimal(usage["cached_tokens"]) * rates[1]
                + Decimal(usage["cache_write_tokens"]) * (rates[2] or 0)
                + Decimal(usage["output_tokens"]) * rates[3]) / MILLION
        snapshot.update(dict(zip(("input_rate", "cache_read_rate", "cache_write_rate", "output_rate"),
                                 (str(r) if r is not None else None for r in rates))))
        snapshot["context_band"] = "long" if long else "short"
    else:
        return unknown("unknown_endpoint_pricing")
    return {"cost_usd": str(cost), "known": True, "unknown_reason": None, "pricing": snapshot}
