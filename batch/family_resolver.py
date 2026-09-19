"""Post-discovery family/template resolver for InfraVision.

This module is deliberately pure: it evaluates accumulated host evidence rather
than one Zabbix discovery event. That makes Vendor + Family decisions safe when
sysObjectID and sysDescr come from different discovery checks.
"""
from dataclasses import dataclass

from vendor_registry import active_vendor_template_rules


@dataclass(frozen=True)
class AssetEvidence:
    sysobjectid: str = ""
    sysdescr: str = ""


@dataclass(frozen=True)
class Resolution:
    rule_id: str
    vendor: str
    families: tuple[str, ...]
    template_name: str
    template_type: str
    confidence: str
    matched: tuple[str, ...]


def _contains(actual: str, expected: str) -> bool:
    return expected.lower() in (actual or "").lower()


def _match(source: str, value: str, evidence: AssetEvidence) -> bool:
    actual = evidence.sysobjectid if source == "sysobjectid" else evidence.sysdescr
    return _contains(actual, value)


def resolve_asset(evidence: AssetEvidence) -> list[Resolution]:
    """Resolve only rules whose vendor and configured family evidence all match."""
    results = []
    for rule in active_vendor_template_rules():
        if not _match(rule["match_check"], rule["match_value"], evidence):
            continue

        matched = [f"{rule['match_check']}:{rule['match_value']}"]
        family = rule.get("family_match")
        if family:
            family_hits = [
                value for value in family["values"]
                if _match(family["source"], value, evidence)
            ]
            if not family_hits:
                continue
            matched.extend(f"{family['source']}:{v}" for v in family_hits)

        confidence = "confirmed" if rule["expected_identity"]["vendor"] == "confirmed" else "probable"
        results.append(Resolution(
            rule_id=rule["id"],
            vendor=rule["canonical_vendor"],
            families=tuple(rule.get("families", [])),
            template_name=rule["template_name"],
            template_type=rule["template_type"],
            confidence=confidence,
            matched=tuple(matched),
        ))
    return results
