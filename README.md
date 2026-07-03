# 📝 AI Text Summarizer API

> An Azure Function that turns long text into concise, AI-generated summaries — with adjustable length, built-in validation, and full observability.

Built as part of **Week 2 — Use Case 1**: developing and deploying AI-powered applications on Azure.

---

## ✨ Features

- 🚀 **Serverless HTTP API** — built on Azure Functions, scales automatically
- 🤖 **AI-powered summarization** — powered by `o4-mini` via Azure AI Foundry
- 📏 **Adjustable summary length** — `short`, `medium`, or `detailed`
- 🛡️ **Graceful error handling** — clear, structured JSON errors for invalid input
- 📊 **Full observability** — request/response logging via Application Insights
- 🔒 **Secrets kept out of source control** — credentials never touch the repo

---

## 🏗️ Architecture

```
        Client
          │
          ▼
 ┌─────────────────────┐
 │   Azure Function      │   HTTP Trigger · Python · Linux Consumption Plan
 │   /api/summarize       │
 └─────────┬────────────┘
           │
           ▼
 ┌─────────────────────┐
 │  Azure AI Foundry      │   o4-mini deployment
 └─────────┬────────────┘
           │
           ▼
     JSON Response

           │
           ▼
 ┌─────────────────────┐
 │ Application Insights   │   Logs, telemetry, monitoring
 └─────────────────────┘
```

| Layer | Technology |
|---|---|
| **Compute** | Azure Functions (Consumption plan, Python 3.13, Linux) |
| **AI Model** | `o4-mini` via Azure AI Foundry |
| **SDK** | OpenAI Python SDK (pointed at Foundry's `/openai/v1/` endpoint) |
| **Monitoring** | Application Insights |
| **Source Control** | GitHub |

---

## 📡 API Reference

### `POST /api/summarize`

#### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `text` | `string` | ✅ Yes | The text to summarize |
| `length` | `string` | ❌ No | `"short"` · `"medium"` · `"detailed"` — defaults to `"medium"` |

#### Example Request

```json
{
  "text": "Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure...",
  "length": "short"
}
```

#### ✅ Success Response — `200 OK`

```json
{
  "summary": "Azure Functions is a serverless compute service that runs event-triggered code without requiring infrastructure provisioning, scaling automatically and billing only for compute used."
}
```

#### ⚠️ Error Responses — `400 Bad Request`

```json
{ "error": "Request body must be valid JSON." }
```
```json
{ "error": "Please provide a 'text' field to summarize." }
```
```json
{ "error": "Invalid 'length' value. Must be 'short', 'medium', or 'detailed'." }
```

#### 🔥 Error Response — `500 Internal Server Error`

```json
{ "error": "Something went wrong while generating the summary." }
```

---

## 🧠 Key Implementation Decisions

- **Length as a prompt instruction, not a token cap** — `length` maps to a natural-language instruction (e.g. *"Summarize this in 1–2 concise sentences"*) prepended to the prompt, producing more natural results than restricting output tokens alone.
- **Instruction-before-content prompt ordering** — the summarization instruction comes *before* the source text in the prompt, so the model has clear guidance before it starts processing potentially long input.
- **Explicit input validation** — invalid JSON, missing `text`, and invalid `length` values are all caught and return clear, structured `400` errors instead of generic failures.
- **Zero-touch telemetry** — the function uses Python's built-in `logging` module, which Azure Functions forwards to Application Insights automatically, with no extra plumbing required.
- **Secrets stay local/cloud-only** — credentials are never hardcoded. Locally they live in `local.settings.json` (gitignored); in Azure they live as Application Settings.

---

## 📁 Project Structure

```
.
├── function_app.py       # Function code — HTTP trigger + summarization logic
├── requirements.txt      # Python dependencies (azure-functions, openai)
├── host.json               # Azure Functions host configuration
├── local.settings.json     # Local-only secrets (gitignored — not in repo)
└── .gitignore
```

---

## 🖥️ Running Locally

**1. Set up your environment**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure your credentials**

Create `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_AI_ENDPOINT": "https://<your-resource>.services.ai.azure.com/openai/v1/",
    "AZURE_AI_KEY": "<your-key>",
    "AZURE_AI_DEPLOYMENT": "o4-mini"
  }
}
```

**3. Run it**
```bash
func start
```

**4. Test it**
```powershell
Invoke-RestMethod -Uri "http://localhost:7071/api/Summarize" `
  -Method Post -ContentType "application/json" `
  -Body '{"text": "your text here", "length": "short"}'
```

---

## ☁️ Deployment

Deployed to **Azure Functions** (Consumption plan) via:

```bash
func azure functionapp publish <your-function-app-name>
```

Application Insights is linked automatically at the Function App level — existing `logging.info` / `logging.error` calls flow straight into it with zero extra configuration.

> 🔐 **Note:** The live endpoint URL is intentionally not published in this README to prevent unauthorized use and unexpected AI usage costs.

---

## 🔭 Possible Future Enhancements

- ⏱️ Add response timing metadata to the JSON output
- 🔑 Add stronger auth/rate limiting for production use
- 📄 Support summarizing uploaded documents (PDF/DOCX), not just raw text

---

<p align="center"><i>Built with 🐍 Python, ☁️ Azure Functions, and 🤖 Azure AI Foundry</i></p>
