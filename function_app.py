import azure.functions as func
import datetime
import json
import logging
import os
from openai import OpenAI

app = func.FunctionApp()

@app.route(route="Summarize", auth_level=func.AuthLevel.ANONYMOUS)
def Summarize(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Summarize function triggered.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error":"Request body must be valid JSON."}),
            status_code=400,
            mimetype="application/json"
        )
    
    text = req_body.get("text")

    if not text or not text.strip():
        return func.HttpResponse(
            json.dumps({"error":"Please provide a 'text' field to summarize."}),
            status_code=400,
            mimetype="application/json"
        )
    
    length = req_body.get("length", "medium").lower()

    length_instructions = {
        "short": "Summarize this in 1-2 concise sentences.",
        "medium": "Summarize this in a short paragraph (3-5 sentences).",
        "detailed": "Summarize this in detail, covering all key points, in multiple paragraphs if needed."
    }

    if length not in length_instructions:
        return func.HttpResponse(
            json.dumps({"error": "Invalid 'length' value. Must be 'short', 'medium', or 'detailed'."}),
            status_code=400,
            mimetype="application/json"
        )

    instruction = length_instructions[length]

    try:
        client = OpenAI(
            base_url = os.environ["AZURE_AI_ENDPOINT"],
            api_key = os.environ["AZURE_AI_KEY"]
        )

        deployment_name = os.environ["AZURE_AI_DEPLOYMENT"]

        response = client.chat.completions.create(
            model=deployment_name,
            messages = [
                {"role":"system","content":"You are a helpful assistant thet summarizes text concisely and accurately"},
                {"role":"user","content":f" text:\n\n{text}\n\n{instruction}"}
            ]
        )

        summary = response.choices[0].message.content

    except Exception as e:
        logging.error(f"Error calling AI model: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error":"Something went wrong while generating the summary."}),
            status_code=500,
            mimetype="application/json"
        ) 

    return func.HttpResponse(
        json.dumps({"summary":summary}),
        status_code=200,
        mimetype="application/json"
    )
    