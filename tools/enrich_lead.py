import os
from apify_client import ApifyClient
from typing import List, Dict

def enrich_lead(args: dict) -> dict:
    """
    Enrich LinkedIn profiles using the Apify LinkedIn Profile Scraper.
    Takes an array of LinkedIn profile URLs and returns enriched profile data.
    """
    profile_urls = args.get("profileUrls", [])
    print(f"enrich_lead: {profile_urls}")
    
    if not profile_urls:
        return {"error": "No profile URLs provided"}
    
    # Get API token from environment variable
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        return {"error": "APIFY_API_TOKEN environment variable not set"}
    
    try:
        # Initialize the ApifyClient
        client = ApifyClient(api_token)
        
        # Run the Actor and wait for it to finish
        print("Starting LinkedIn Profile Scraper...")
        run = client.actor("2SyF0bVxmgGr8IVCZ").call(run_input={"profileUrls": profile_urls})
        
        # Fetch results from the run's dataset
        print(f"Scraping completed. Dataset ID: {run['defaultDatasetId']}")
        enriched_profiles = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            enriched_profiles.append(item)
        
        return {
            "status": "success",
            "enriched_profiles": enriched_profiles
        }
        
    except Exception as e:
        print(f"Error in enrich_lead: {str(e)}")
        return {"error": f"Failed to enrich profiles: {str(e)}"}