import pandas as pd
from openai import OpenAI
import json
import time
from parsers import extract_json_array
from prompts import os_enrichment_prompt
from constants import allowed_OS_families   

# a function to classify OS for a batch of model names with device type context
def classify_os_batch(models_with_device_type, gpt_client, os_prompt):
    prompt = os_prompt + "\n".join(models_with_device_type)
    response = gpt_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=900,
        messages=[
            {"role": "system", "content": "Return only valid JSON. No markdown."},
            {"role": "user", "content": prompt},
        ],
    )

    parsed = extract_json_array(response.choices[0].message.content)
    os_vals, conf_vals, just_vals = [], [], []

    for obj in parsed:
        os_family = obj.get("os_family", "Unknown")
        confidence = obj.get("confidence", "low")
        justification = obj.get("justification", "")

        if os_family not in allowed_OS_families:
            os_family = "Unknown"
        if confidence not in {"low", "medium", "high"}:
            confidence = "low"
        if not isinstance(justification, str):
            justification = str(justification)

        os_vals.append(os_family)
        conf_vals.append(confidence)
        just_vals.append(justification.strip())

    return os_vals, conf_vals, just_vals


# a function that uses the device type from the previous enrichment
def build_model_context(df, start, end):
    return [
        f"{row['model']} | device_type: {row['device_type']}"
        for _, row in df.iloc[start:end].iterrows()
    ]


# apply OS inference to full dataset by batches
def enrich_os_on_existing_df_gpt(df, gpt_client, os_prompt, batch_size=10):
    os_all, conf_all, just_all = [], [], []

    total_batches = (len(df) + batch_size - 1) // batch_size

    for i in range(0, len(df), batch_size):
        print(f"Processing by GPT OS batch {i // batch_size + 1}/{total_batches}")

        models_with_device_type = build_model_context(df, i, i + batch_size)

        os_vals, conf_vals, just_vals = classify_os_batch(models_with_device_type, gpt_client, os_prompt)

        os_all.extend(os_vals)
        conf_all.extend(conf_vals)
        just_all.extend(just_vals)

        time.sleep(0.2)

    df["os_family_byGPT"] = os_all
    df["os_confidence_byGPT"] = conf_all
    df["os_justification_byGPT"] = just_all

    return df