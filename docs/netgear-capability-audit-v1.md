# NETGEAR Capability Audit v1
Date: 2026-09-19
Status: mixed — existing WAX prototype / other families Evidence Pending

## Family rule
Do not treat NETGEAR as one SNMP capability. Separate unmanaged/Plus from Smart/Managed and AP families.
Existing InfraVision evidence: WAX625 vendor can be identified by enterprise sysObjectID; model/firmware were not available through tested ENTITY-MIB objects. Official Zabbix Fastpath template uses NETGEAR private MIB but WAX625 compatibility is unverified.

## States
- WAX625/AP family: Prototype for vendor identity; model/firmware capability probe required.
- Smart/Managed switches: Evidence Pending; private MIB/official Fastpath candidate.
- Plus/unmanaged: do not promise SNMP; classify by actual family capability.

## Real-device gate
Collect sysObjectID/sysDescr, NETGEAR private subtree, exact hardware revision, model and firmware shown by UI. Probe official Fastpath model/serial/OS OIDs before selecting the official template.
