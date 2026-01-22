import pandas as pd
from openai import OpenAI
from google import genai
import os
from dotenv import load_dotenv

from validation import validate_os_consistency
from evaluation import coverage_rate, usable_confidence_rate, agreement_rate
from constants import allowed_device_type, allowed_OS_families
from prompts import device_type_enrichment_prompt, os_enrichment_prompt, os_enrichment_prompt_improved
from parsers import extract_json_array
from device_type_enrichment import classify_all_device_types
from os_enrichment_gpt import enrich_os_on_existing_df_gpt
from os_enrichment_gemini import enrich_os_on_existing_df_gemini

def main():

    # load environment and API keys
    load_dotenv()
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is missing. Check .env location/name."
    assert os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY is missing. Check .env location/name."
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    gpt_client = OpenAI()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    # load input data
    df = pd.read_csv("data/50_cps_models.csv")

    # apply the device type enrichment
    df["device_type"], df["device_type_confidence"], df["device_type_justification"] = classify_all_device_types(df, gpt_client)

    # saving the dataframe after device type enrichment
    df=df.sort_values(by=["device_type","device_type_confidence"])
    df.to_csv("output\Cps_Models_DeviceType_enrichment_byGPT.csv", index=False)
    df.groupby("device_type_confidence").size().sort_values(ascending=False).rename("count").reset_index()

    # OS Enrichment Using GPT
    df = enrich_os_on_existing_df_gpt(df, gpt_client, os_prompt=os_enrichment_prompt)
    df = df.sort_values(by=["os_family_byGPT","os_confidence_byGPT"])
    df.groupby("os_confidence_byGPT").size().sort_values(ascending=False).rename("count").reset_index()
    
    #validate the OS family values for GPT enrichment
    validated_os = df.apply(
        lambda r: validate_os_consistency(
            r["device_type"],
            r["os_family_byGPT"]),axis=1)
    changed_mask = df["os_family_byGPT"] != validated_os
    df.loc[changed_mask, "os_family_byGPT"] = validated_os[changed_mask]

    # improve the prompt of the OS enrichment
    df = enrich_os_on_existing_df_gpt(df, gpt_client=gpt_client, os_prompt=os_enrichment_prompt_improved)
    df.to_csv("output\Cps_Models_DeviceType+OsEnrichment_byGPT.csv",index=False)

    # OS Enrichment Using Gemini
    GEMINI_MODEL = "gemini-2.5-flash"
    df= enrich_os_on_existing_df_gemini(df, gemini_client=gemini_client)

    df = df.sort_values(by=["os_family_byGemini","os_confidence_byGemini"])
    df.to_csv("output\Cps_Models_DeviceType+OsEnrichment_byGemini.csv",index=False)
    df.groupby("os_confidence_byGemini").size().sort_values(ascending=False).rename("count").reset_index()

    #validate the OS family values for Gemini enrichment
    validated_os = df.apply(
        lambda r: validate_os_consistency(
            r["device_type"],
            r["os_family_byGemini"]),axis=1)
    changed_mask = df["os_family_byGemini"] != validated_os
    df.loc[changed_mask, "os_family_byGemini"] = validated_os[changed_mask]

    # evaluate the two models by KPIs
    coverage_gpt = coverage_rate(df["os_family_byGPT"])
    coverage_gemini = coverage_rate(df["os_family_byGemini"])
    usable_gpt = usable_confidence_rate(df["os_confidence_byGPT"])
    usable_gemini = usable_confidence_rate(df["os_confidence_byGemini"])

    agreement = agreement_rate(
        df["os_family_byGPT"],
        df["os_family_byGemini"]
    )

    model_metrics = pd.DataFrame({
        "Metric": ["Coverage rate (OS ≠ Unknown)", "Usable confidence rate (medium+high)"],
        "GPT": [coverage_gpt, usable_gpt],
        "Gemini": [coverage_gemini, usable_gemini]
    })
    agreement_table = pd.DataFrame({"Metric": ["Model agreement rate"], "Value": [agreement]})
    output_path = "output/models_comparison.xlsx"
    output_path = "output/models_comparison.xlsx"
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        model_metrics.to_excel(writer, sheet_name="Model metrics", index=False)
        agreement_table.to_excel(writer, sheet_name="Agreement", index=False)

if __name__ == "__main__":
    main()



