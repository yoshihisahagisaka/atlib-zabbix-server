# Fortinet Family Capability Audit v1

Date: 2026-09-19
Status: mixed — FortiGate Prototype / FortiSwitch Evidence Pending / FortiAP Evidence Pending

## FortiGate
- Existing InfraVision audit found the official Zabbix "FortiGate by SNMP" template supplies model, firmware and serial inventory.
- Fortinet publishes FortiGate MIB documentation and product MIBs.
- Keep the existing post-discovery family guard; do not broaden from FortiGate to all Fortinet products.
- State: Prototype until one production/test FortiGate validates identity fields and template compatibility.

## FortiSwitch
Primary Fortinet documentation confirms:
- standalone FortiSwitch supports SNMP monitoring and Fortinet/FortiSwitch MIBs;
- Fortinet publishes a model-to-sysObjectID table;
- sysObjectID is different per FortiSwitch model.

Implication:
- Model can potentially be resolved deterministically from sysObjectID using Fortinet's official mapping.
- Firmware/serial sources should be confirmed from the MIB or a real device before an adapter is finalized.
- State: Evidence Pending.

## FortiAP
Primary Fortinet documentation confirms:
- FortiAP families support SNMP queries/traps in supported FortiOS/FortiAP versions;
- FortiAP MIB + Fortinet Core MIB are the authoritative MIB sources;
- management topology/version matters. Historical/current docs note controller-based SNMP behavior and limitations around local standalone mode.

Implication:
- Do not assume every FortiAP is directly pollable in the same way.
- Treat controller-managed vs direct/standalone behavior as a capability dimension.
- State: Evidence Pending.

## Family separation
Never use Fortinet enterprise root alone to select a family-specific template.
Canonical family must be one of:
- FortiGate
- FortiSwitch
- FortiAP
- other/unknown Fortinet

## Real-device gates
FortiGate:
- validate official Zabbix template inventory model/firmware/serial.

FortiSwitch:
- capture sysObjectID/sysDescr;
- map sysObjectID to official model table;
- inspect FortiSwitch/Core MIB identity and firmware objects.

FortiAP:
- record management mode/controller;
- capture sysObjectID/sysDescr where directly available;
- inspect FortiAP/Core MIB identity and firmware objects.

## Commercial behavior
Unknown Fortinet family or unsupported polling topology does not block Base monitoring. Report only defensible identity/security intelligence and keep detailed applicability Unknown until evidence is sufficient.
