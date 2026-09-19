"""InfraVision vendor/template resolver registry.

Keep device-identification knowledge separate from discovery orchestration.
A new vendor/family should normally be added here (and, when needed, as a
Zabbix template), not by adding branching logic to setup_discovery.py.
"""

VENDOR_TEMPLATE_RULES = [
    {
        "id": "fortinet-fortigate",
        "name": "Fortinet FortiGate",
        "canonical_vendor": "Fortinet",
        "match_check": "sysobjectid",
        "match_operator": "contains",
        "match_value": "1.3.6.1.4.1.12356",
        "template_type": "zabbix_official",
        "template_name": "FortiGate by SNMP",
        "families": ["FortiGate"],
        "verified_models": [],
        "expected_identity": {"vendor": "confirmed", "model": "confirmed", "firmware": "confirmed"},
        "scope": "network_security",
        "enabled": True,
        "notes": "Official Zabbix 7.4 template provides model, firmware and serial. First production use still requires one-device validation.",
    },
    {
        "id": "netgear",
        "name": "NETGEAR",
        "canonical_vendor": "NETGEAR",
        "match_check": "sysobjectid",
        "match_operator": "contains",
        "match_value": "1.3.6.1.4.1.4526",
        "template_type": "atlib_identification",
        "template_name": "MSP - NETGEAR Device Identification",
        "families": [],
        "verified_models": ["WAX625"],
        "expected_identity": {
            "vendor": "confirmed",
            "model": "unknown",
            "firmware": "unknown",
        },
        "scope": "network",
        "enabled": True,
        "notes": "Current standard/private OID set identifies vendor; WAX625 model/FW gap remains.",
    },
    {
        "id": "brother",
        "name": "Brother",
        "canonical_vendor": "Brother",
        "match_check": "sysobjectid",
        "match_operator": "contains",
        "match_value": "1.3.6.1.4.1.2435",
        "template_type": "atlib_identification",
        "template_name": "MSP - Brother Device Identification",
        "families": [],
        "verified_models": ["MFC-L3780CDW"],
        "expected_identity": {
            "vendor": "confirmed",
            "model": "confirmed",
            "firmware": "confirmed",
        },
        "scope": "out_of_scope_printer",
        "enabled": False,
        "notes": "Verified technically, but laser MFPs are outside the current InfraVision network-equipment EoL/CVE automation scope.",
    },
    {
        "id": "ubiquiti-unifi",
        "name": "Ubiquiti UniFi",
        "canonical_vendor": "Ubiquiti",
        "match_check": "sysdescr",
        "match_operator": "contains",
        "match_value": "Ubiquiti UniFi",
        "template_type": "atlib_identification",
        "template_name": "MSP - Ubiquiti UniFi Device Identification",
        "families": ["UniFi"],
        "verified_models": ["UCG-Ultra"],
        "expected_identity": {
            "vendor": "confirmed",
            "model": "confirmed",
            "firmware": "confirmed",
        },
        "scope": "network",
        "enabled": True,
        "notes": "Some devices expose generic Net-SNMP sysObjectID, so sysDescr is required.",
    },
]


def validate_registry(rules: list[dict] | None = None) -> None:
    """Fail fast on unsafe/ambiguous registry metadata."""
    rules = VENDOR_TEMPLATE_RULES if rules is None else rules
    ids = set()
    for rule in rules:
        required = {
            "id", "name", "canonical_vendor", "match_check", "match_operator",
            "match_value", "template_type", "template_name", "expected_identity", "enabled",
        }
        missing = required - set(rule)
        if missing:
            raise ValueError(f"vendor rule {rule.get('id', '<unknown>')} missing: {sorted(missing)}")
        if rule["id"] in ids:
            raise ValueError(f"duplicate vendor rule id: {rule['id']}")
        ids.add(rule["id"])
        if rule["match_check"] not in {"sysobjectid", "sysdescr"}:
            raise ValueError(f"{rule['id']}: unsupported match_check={rule['match_check']}")
        # Zabbix Discovery Action currently implements Received value LIKE/contains.
        if rule["match_operator"] != "contains":
            raise ValueError(f"{rule['id']}: unsupported match_operator={rule['match_operator']}")
        if rule["template_type"] not in {"zabbix_official", "atlib_identification"}:
            raise ValueError(f"{rule['id']}: unsupported template_type={rule['template_type']}")
        for field in ("vendor", "model", "firmware"):
            if rule["expected_identity"].get(field) not in {"confirmed", "probable", "unknown"}:
                raise ValueError(f"{rule['id']}: invalid expected_identity.{field}")


def active_vendor_template_rules() -> list[dict]:
    """Return only rules in the current automation scope."""
    validate_registry()
    return [rule for rule in VENDOR_TEMPLATE_RULES if rule.get("enabled", True)]
