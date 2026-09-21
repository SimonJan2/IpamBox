# Services

The service catalog — what the network *serves*, not just what it's made of.

## Fields

| Field | Notes |
|---|---|
| **Name** | Service name (e.g. `CRM`, `File share`) |
| **Beneficiary** | Who consumes it — team, dept, customer |
| **Site / Site code** | Where it's anchored |
| **Doc path** | Link to runbooks or external docs |
| **Test info** | How to verify the service is healthy |
| **Notes** | Free text |

## Why track services in an IPAM?

When a subnet changes or a scan finds drift, the question is always "who
cares?" Linking services to sites gives you the blast radius: the circuits,
certificates, and assets of the same site are one hop away.

## Working with the list

Same affordances as every list — reorder, pin, tag, row color, inline edits,
history. Searchable from the palette under "Services", and usually populated
via [workbook import](/docs/import).
