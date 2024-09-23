import requests, os

def get_deal_quotes(base_url, deal_id, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    association_url = f"{base_url}/crm/v4/objects/deals/{deal_id}/associations/quotes"
    response = requests.get(association_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        quote_ids = [item['toObjectId'] for item in data['results']]
        return quote_ids
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
def get_quote_details(base_url, token, quote_id):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    quote_url = f"{base_url}/crm/v4/objects/quotes/{quote_id}?properties=hs_title,hs_esign_date,hs_sign_status"
    response = requests.get(quote_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching quote details: {response.status_code} - {response.text}")
        return None
      
def get_quote_names(base_url, token, quote_ids):
    quote_names = []
    for quote_id in quote_ids:
        quote_details = get_quote_details(base_url, token, quote_id)
        if quote_details and 'properties' in quote_details and 'hs_title' in quote_details['properties']:
            quote_name = quote_details['properties']['hs_title']
            quote_names.append(quote_name)
        else:
            print(f"Could not retrieve name for quote ID {quote_id}")
    return quote_names
  
def get_quote_signed_dates_status(base_url, token, quote_ids):
    signed_dates = []
    signed_status = []
    for quote_id in quote_ids:
        quote_details = get_quote_details(base_url, token, quote_id)
        if quote_details and 'properties' in quote_details and 'hs_esign_date' in quote_details['properties']:
            signed_date = quote_details['properties']['hs_esign_date']
            signed_dates.append(signed_date)
        else:
            print(f"Could not retrieve signed date for quote ID {quote_id}")
        if quote_details and 'properties' in quote_details and 'hs_sign_status' in quote_details['properties']:
            signed_stat = quote_details['properties']['hs_sign_status']
            signed_status.append(signed_stat)
        else:
            print(f"Could not retrieve signed status for quote ID {quote_id}")
    return signed_dates, signed_status
      
def main(event):
  dId = event.get("inputFields").get("deal_id")
  token = os.getenv("RevOps")
  base_url = "https://api.hubapi.com"
  quoteIds = get_deal_quotes(base_url, dId, token)
  quoteNames = get_quote_names(base_url, token, quoteIds)
  quoteSignedDates, quoteSignedStatus = get_quote_signed_dates_status(base_url, token, quoteIds)
  processedQuoteSignedDates = []
  processedQuoteSignedStatus = []
  for i in range(len(quoteSignedStatus)):
    if quoteSignedStatus[i] == "ESIGN_COMPLETED" and quoteSignedDates[i] is not None:
      processedQuoteSignedDates.append(quoteSignedDates[i])
      processedQuoteSignedStatus.append(quoteSignedStatus[i])
  toBeProcessedManually = processedQuoteSignedStatus.count("ESIGN_COMPLETED")
  return {
    "outputFields": {
      "quoteIds": quoteIds,
      "quoteNames": quoteNames,
      "quoteSignStatus": quoteSignedStatus,
      "quoteSignedDates": quoteSignedDates,
      "processedQuoteSignedDates": processedQuoteSignedDates,
      "processedQuoteSignedStatus": processedQuoteSignedStatus,
      "toBeProcessedManually": toBeProcessedManually
    }
  }