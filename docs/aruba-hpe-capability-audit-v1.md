# HPE Aruba Capability Audit v1
Date: 2026-09-19
Status: Evidence Pending

## Family separation
Aruba CX, ArubaOS-Switch, Instant On and wireless/controller families must not be conflated.
Existing Zabbix audit found official Aruba CX coverage to be product-family specific and insufficient to assume universal model/firmware inventory enrichment.

## InfraVision assessment
SNMP is available in Aruba switch families, but exact identity capability and management-mode constraints are family dependent.

## State
Evidence Pending. Wait for a real Aruba/HPE device, record OS/family and management mode, then inspect sysObjectID/sysDescr/ENTITY-MIB/private MIB before creating an adapter.
