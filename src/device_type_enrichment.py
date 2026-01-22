import pandas as pd
from openai import OpenAI
import time
from parsers import extract_json_array
from prompts import device_type_enrichment_prompt
from constants import allowed_device_type

# a function to classify device types for a batch of model names
def classify_device_types_batch(models_batch, gpt_client):
    prompt = device_type_enrichment_prompt + "\n".join(models_batch)
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

    device_types = []
    confidences = []
    justifications = []

    for obj in parsed:
        dt = obj.get("device_type", "Unknown")
        conf = obj.get("confidence", "low")
        just = obj.get("justification", "")

        if dt not in allowed_device_type:
            dt = "Unknown"
        if conf not in {"low", "medium", "high"}:
            conf = "low"
        if not isinstance(just, str):
            just = str(just)

        device_types.append(dt)
        confidences.append(conf)
        justifications.append(just.strip())

    return device_types, confidences, justifications


# apply the device classification to the full dataset
def classify_all_device_types(df, gpt_client, batch_size=10):
    models = df["model"].astype(str).tolist()

    device_types_all = []
    confidences_all = []
    justifications_all = []

    total_batches = (len(models) + batch_size - 1) // batch_size

    for i in range(0, len(models), batch_size):
        batch = models[i:i + batch_size]
        print(f"Processing by GPT device type batch {i // batch_size + 1}/{total_batches}")

        dts, confs, justs = classify_device_types_batch(batch, gpt_client)

        device_types_all.extend(dts)
        confidences_all.extend(confs)
        justifications_all.extend(justs)

        time.sleep(0.2)

    return (
        pd.Series(device_types_all, index=df.index),
        pd.Series(confidences_all, index=df.index),
        pd.Series(justifications_all, index=df.index),
    )

