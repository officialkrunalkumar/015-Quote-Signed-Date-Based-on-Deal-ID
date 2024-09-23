import ast
from datetime import datetime
import time

def main(event):
  pqsd = event.get("inputFields").get("pqsd")
  finalPQSD = ast.literal_eval(pqsd)
  sorted_dates = sorted(finalPQSD, key=lambda date: datetime.fromisoformat(date[:-1]))
  if len(sorted_dates) > 1:
    finalDate = sorted_dates[-1]
  else:
    finalDate = sorted_dates[0]
  print(finalDate)
  datetime_obj = datetime.strptime(finalDate, "%Y-%m-%dT%H:%M:%SZ")
  timestamp_seconds = int(time.mktime(datetime_obj.timetuple()))
  hubspot_timestamp = timestamp_seconds * 1000
  return {
    "outputFields": {
      "ProcessedDate": hubspot_timestamp
    }
  }