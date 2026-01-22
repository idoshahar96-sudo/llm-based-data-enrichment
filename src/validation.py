import pandas as pd

# validation function to ensure consistency between device type and OS family
def validate_os_consistency(device_type, os_family):
    if device_type == "Industrial PC (IPC)":
        if os_family not in {"Linux", "Windows Embedded"}:
            return "Unknown"
    if device_type == "PLC":
        if os_family == "Windows Embedded":
            return "Unknown"
    if device_type == "HMI":
        if os_family == "VxWorks":
            return "Unknown"
    if device_type == "Medical Patient Monitor":
        if os_family == "Linux":
            return "Unknown"
    return os_family

