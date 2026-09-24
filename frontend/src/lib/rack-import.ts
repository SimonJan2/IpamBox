import type {
  FieldOption,
  ImportOption,
} from "@/components/smart-import-dialog";

// Bundle-aware field union for the smart importer's mapping selects —
// mirrors the *_IMPORT_FIELDS sets in rack_io.py (each sheet applies the
// overrides filtered to its own family).
export const RACK_IMPORT_FIELDS: FieldOption[] = [
  { value: "id", label: "ID (exact match)" },
  { value: "name", label: "Name" },
  { value: "site", label: "Site" },
  { value: "group", label: "Rack group" },
  { value: "group_position", label: "Position in group" },
  { value: "room", label: "Room" },
  { value: "height_u", label: "Height (U)" },
  { value: "width", label: "Rail width" },
  { value: "description", label: "Description" },
  { value: "notes", label: "Notes" },
  { value: "device_type", label: "Device type" },
  { value: "manufacturer", label: "Manufacturer" },
  { value: "model", label: "Model" },
  { value: "category", label: "Category" },
  { value: "serial_number", label: "Serial number" },
  { value: "mac_address", label: "MAC address" },
  { value: "rack", label: "Rack" },
  { value: "u_position", label: "U position" },
  { value: "u_height", label: "U height" },
  { value: "face", label: "Face" },
  { value: "carrier", label: "Carrier" },
  { value: "slot", label: "Slot" },
  { value: "slot_layout", label: "Slot layout" },
  { value: "watts", label: "Watts" },
  { value: "weight_kg", label: "Weight (kg)" },
  { value: "ips", label: "IPs (space-separated)" },
  { value: "device", label: "Device (interfaces/cables)" },
  { value: "kind", label: "Kind" },
  { value: "speed_mbps", label: "Speed (Mbps)" },
  { value: "connected_ip", label: "Connected IP" },
  { value: "a_device", label: "Cable A device" },
  { value: "a_interface", label: "Cable A interface" },
  { value: "b_device", label: "Cable B device" },
  { value: "b_interface", label: "Cable B interface" },
  { value: "color", label: "Cable color" },
  { value: "label", label: "Cable label" },
  { value: "length_m", label: "Cable length (m)" },
];

export const RACK_IMPORT_OPTIONS: ImportOption[] = [
  {
    kind: "select",
    param: "on_existing",
    label: "When a rack matches",
    defaultValue: "skip",
    choices: [
      { value: "skip", label: "Skip existing" },
      { value: "update", label: "Update matched" },
      { value: "merge", label: "Merge (add devices only)" },
    ],
  },
  {
    kind: "flag",
    param: "replace_devices",
    label: "Replace devices (un-rack occupants first)",
  },
  {
    kind: "flag",
    param: "force",
    label: "Force (commit valid rows despite errors)",
  },
];
