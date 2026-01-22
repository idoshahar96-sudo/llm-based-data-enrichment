### Device Type Enrichment
device_type_enrichment_prompt = """
You are an OT security analyst responsible for enriching CPS asset inventories.

Task:
For each CPS device model listed below, identify the most appropriate device type as it would
appear in a real OT/ICS asset inventory.
Important context:
- Device type attribution is generally stable and vendor-intended.
- Many CPS product families have a dominant, well-established role in industry practice.
- This task reflects asset inventory enrichment, not exhaustive functional analysis.

Guidelines:
- Prefer a specific, domain-aware category (product-family semantics) rather than a generic label.
- If a model could plausibly fit multiple roles, choose the most common primary role in practice.
- Use industry-standard defaults when a product family is strongly associated with a device type.
- Do not overuse "Other" as a fallback when a reasonable industry classification exists.
- Use "Other" only when the model clearly does not align with any listed category.
- Use "Unknown" only when you cannot reasonably infer the device type at all.

Confidence calibration guidance:
- Use "high" confidence when the device type is strongly and consistently associated
  with the vendor and product family.
- Use "medium" confidence when relying on common industry defaults or partial signals.
- Use "low" confidence when the inference is weak or indirect.
- "Other" and "Unknown" should generally be paired with "low" confidence.

Allowed device types (use only these exact values):
PLC, HMI, Industrial PC (IPC), Building Management Controller (BMS),
Power Distribution Unit (PDU), UPS, Power Controller,
Medical Infusion Pump, Medical Patient Monitor, Laboratory Analyzer, Nurse Call System,
Network Appliance, SCADA Server, Safety Controller, Sensor, Camera, Other, Unknown

Output format:
Return a JSON array of objects, one per model, in the same order.
Each object must have:
- "device_type": one of the allowed device types
- "confidence": one of ["low", "medium", "high"]
- "justification": short reasoning based on product-family semantics (1 sentence)

Return ONLY valid JSON. No markdown. No extra text.

Models:
"""


### OS Enrichment
os_enrichment_prompt = """
        You are an OT security analyst enriching CPS asset inventories with operating system information.
        
        Task:
        For each CPS device listed below, infer the most likely operating system *family*
        based on common vendor practices and typical deployments.
        
        Important context:
        - OS attribution is probabilistic and less stable than device type.
        - Device type information is already known and should be used to inform OS inference.
        - This task reflects asset intelligence enrichment, not definitive fingerprinting.
        
        Instructions:
        - Infer an OS family only when it is commonly associated with the product family
          and the provided device type.
        - Do not assume custom, lab-specific, or rare configurations.
        - If multiple OS families are plausible, choose the most common one and reduce confidence.
        - If the OS cannot be reasonably inferred, use "Unknown".
        
        Allowed OS families (use only these exact values):
        Linux, Windows Embedded, VxWorks, Unknown
        
        Output format:
        Return a JSON array of objects, one per entry, in the same order as provided.
        Each object must include:
        - "os_family": one of the allowed OS families
        - "confidence": one of ["low", "medium", "high"]
        - "justification": short factual reasoning based on vendor, product family,
          and the provided device type
        
        Return ONLY valid JSON. No markdown. No extra text.
        
        Devices (model | known device type):
        """ 


#improvement of the previous os_enrichment_prompt
os_enrichment_prompt_improved= """
        You are an OT security analyst enriching CPS asset inventories with operating system information.
        
        Task:
        For each CPS device listed below, infer the most likely operating system *family*
        based on common vendor practices and typical deployments.
        
        Important context:
        - OS attribution is probabilistic and less stable than device type.
        - Device type information is already known and should be used to inform OS inference.
        - This task reflects asset intelligence enrichment, not definitive fingerprinting.

        Additional guidance (industry OS priors):

        When no model-specific contradiction exists, you may rely on common industry defaults:
        - HMIs are commonly Windows Embedded.
        - Industrial PCs (IPC) commonly run Linux or Windows Embedded.
        - SCADA servers commonly run Windows Embedded or Linux.
        - Network appliances commonly run embedded Linux.
        - PLCs and safety controllers commonly run VxWorks or proprietary RTOS.
        - Building Management Controllers often run embedded Linux or proprietary firmware.
        
        If using such defaults, reflect this by setting confidence to "medium",
        unless the product line strongly indicates otherwise.

        Confidence calibration guidance:

        - Use "high" confidence when the OS family is strongly and consistently associated
          with the vendor and device type (e.g., mainstream HMIs, well-known PLC families).
        - Use "medium" confidence when relying on common industry defaults or device-type priors.
        - Use "low" confidence when the inference is weak, indirect, or based on limited signals.
        - "Unknown" should generally be paired with "low" confidence.

        Instructions:
        - Infer an OS family only when it is commonly associated with the product family
          and the provided device type.
        - Do not assume custom, lab-specific, or rare configurations.
        - If multiple OS families are plausible, choose the most common one and reduce confidence.
        - If the OS cannot be reasonably inferred, use "Unknown".
        - If the device type is known and a common OS family is strongly implied by industry practice,
            prefer assigning that OS family with "medium" confidence rather than defaulting to "Unknown".

        Allowed OS families (use only these exact values):
        Linux, Windows Embedded, VxWorks, Unknown
        
        Output format:
        Return a JSON array of objects, one per entry, in the same order as provided.
        Each object must include:
        - "os_family": one of the allowed OS families
        - "confidence": one of ["low", "medium", "high"]
        - "justification": short factual reasoning based on vendor, product family,
          and the provided device type 
        
        Return ONLY valid JSON. No markdown. No extra text.
        
        Devices (model | known device type):
        """ 
