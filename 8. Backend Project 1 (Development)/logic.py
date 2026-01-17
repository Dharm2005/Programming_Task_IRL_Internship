import re

def check_string(text, regex):
  result = []
  
  for i in range(len(text)):
    if text.startswith(regex,i):
      result.append({
        "match" : regex,
        "index" : i
      })
  
  return result 