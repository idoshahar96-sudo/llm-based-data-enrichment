import pandas as pd
from google import genai
import time
from parsers import extract_json_array
from prompts import os_enrichment_prompt
from constants import allowed_OS_families
from os_enrichment_gpt import build_model_context

## a function to classify OS for a batch of model names using Gemini
def classify_os_batch_gemini(models_with_device_type, gemini_client):
    prompt = os_enrichment_prompt + "\n".join(models_with_device_type)

    response = gemini_client.models.generate_content(
    model=GEMINI_MODEL,
    contents=prompt
    )

    parsed = extract_json_array(response.text)
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


# apply OS inference to full dataset by batches
def enrich_os_on_existing_df_gemini(df, batch_size=10, max_retries=10, gemini_client=None):
    df = df.copy()

    df["os_family_byGemini"] = None
    df["os_confidence_byGemini"] = None
    df["os_justification_byGemini"] = None

    total_batches = (len(df) + batch_size - 1) // batch_size

    for i in range(0, len(df), batch_size):
        batch_idx = i // batch_size + 1
        print(f"Processing gemini batch {batch_idx}/{total_batches}")

        batch_df = df.iloc[i:i + batch_size]

        # Skip already-enriched rows (resume-safe)
        if batch_df["os_family_byGemini"].notna().all():
            print("Batch already enriched, skipping")
            continue

        models_with_device_type = build_model_context(df, i, i + batch_size)
        for attempt in range(max_retries):
            try:
                os_vals, conf_vals, just_vals = classify_os_batch_gemini(models_with_device_type, gemini_client)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print("Final failure on batch, stopping early")
                    return df
                wait = 2 ** attempt
                print(f"Gemini overloaded, retrying in {wait}s...")
                time.sleep(wait)

        df.loc[batch_df.index, "os_family_byGemini"] = os_vals
        df.loc[batch_df.index, "os_confidence_byGemini"] = conf_vals
        df.loc[batch_df.index, "os_justification_byGemini"] = just_vals
        time.sleep(1.0)

    return df
