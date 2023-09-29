# LinkedIn Job Scraper with OpenAI Language Model

This GitHub project combines Azure Functions, Azure Cosmos DB, and Azure Storage to scrape LinkedIn job listings and extract information using OpenAI's Language Model.

It is meant as a personal project to play around with the LinkedIn API and see what can be done with LLMs to extract insights from the free text that are the job listings.


## Disclaimer
LinkedIn's API is not public, and web scraping may violate its terms. Use this code at your own risk, ensuring compliance with LinkedIn's policies. It is meant for personal use only as a POC.

This is making use of https://github.com/tomquirk/linkedin-api, which is not hosted in PyPI and is installed from source. It will use your credentials to access the LinkedIn API, so review the code carefully before use.


## Prerequisites
- Azure subscription
- Azure Function App
- Azure Cosmos DB instance with a database `linkedinjobs` (right now the database and containers are hardcoded).
- Azure Storage account
- OpenAI API key
- Cookies for a logged in LinkedIn account. See this issue for more details https://github.com/tomquirk/linkedin-api/issues/331

You can use the free tier of azure for the Azure Function and Cosmos DB, but the Storage Account and the OpenAI API will incur in costs. 

## Setup

To run it locally you need:

1. Clone the repository.

2. Set up the environment to run azure functions, if running in VS Code, you should be prompted to setup for an azure function.

3. Upload cookies to the storage account to a container `config` and the file named `cookies_alternative.json`

3. Add the `local.settings.json` with the updated values for your resources.

4. Start the function with `func start`

5. Trigger the http endpoint `http://localhost:7071/api/orchestrators`

If everything runs correctly you can deploy it through VS Code itself, as well as uploading the settings.

### local.settings.json
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "YOUR_LOCAL_AZURE_STORAGE_CONNECTION_STRING",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY",
    "CosmosConnection": "YOUR_COSMOS_DB_CONNECTION_STRING",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "YOUR_APPLICATION_INSIGHTS_CONNECTION_STRING",
    "OrchestratorStatusUri": "YOUR_ORCHESTRATOR_STATUS_URI"
  }
}
```

Replace placeholders with your actual configuration values. Most of them are self-explanatory or standard for Azure Functions. `OrchestratorStatusUri` is a URL to send a POST request with the status of orchestrators after it finishes.

## Usage
The Azure Function will automatically query LinkedIn, process data, and store results in Cosmos DB. Use stored data as needed.

To customize how it works you can update the queries that are being made to LinkedIn in both the trigger for changing the keyworkds or the `linkedin.py` module for more fine grained control of the parameters.

For the post-processing done by the LLM, you will need to update both the prompts at `openai.py` and the models for the job summary at `models.py`

## Folder Structure
- `jobsearch/`: Modules for the different APIs used.
- `function/`: Durable entities and other functions.
- `function_app.py`: Main entry point of the azure functin.

## Contributing
Contributions are welcome. Create pull requests for improvements.

## License
This project is under the MIT License. See [LICENSE](LICENSE) for details.