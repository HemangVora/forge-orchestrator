"""Provider registry — maps capabilities to provider names, not implementations.

Example repository provider_preferences:
  {"coding": "claude-code", "ui": "kimi-code", "images": "higgs-field"}
"""

from app.domain.capabilities import Capability

PROVIDER_REGISTRY: dict[Capability, list[str]] = {
    Capability.CODING: ["claude-code", "kimi-code"],
    Capability.UI: ["kimi-code"],
    Capability.IMAGE: ["higgs-field"],
    Capability.REVIEW: ["claude-code"],
    Capability.TESTING: ["claude-code"],
}
