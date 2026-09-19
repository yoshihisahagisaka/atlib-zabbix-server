# Allied Telesis Capability Audit v1
Date: 2026-09-19
Status: Evidence Pending

## Findings
Allied Telesis business switches/routers broadly document SNMP support. AlliedWare Plus documentation lists extensive Allied Telesis enterprise MIBs including AT-PRODUCT-MIB, AT-SYSINFO-MIB, AT-CHASSIS-MIB and AT-MIBVERSION-MIB.

## InfraVision assessment
Strong candidate for deterministic identity enrichment, but exact model/firmware/serial objects should be confirmed against a real SMB-family device before production mapping.

## Initial real-device targets
CentreCOM managed switches first; AlliedWare Plus router/security families second. Preserve OS/software family because lifecycle/CVE applicability may be AlliedWare Plus-version dependent.

## State
Evidence Pending. Prepare probe; no production resolver until real-device evidence.
