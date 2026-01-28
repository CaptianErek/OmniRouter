import re
import json

test = """```json
{
  "extracted_fields": [
    {
      "category": "name",
      "field": "full_name",
      "value": "Dhruv Sharma",
      "confidence": 1.0,
      "evidence": "my name is Dhruv Sharma"
    },
    {
      "category": "Age (International standards)",
      "field": "current_age",
      "value": 20,
      "confidence": 1.0,
      "evidence": "my age is 20"
    },
    {
      "category": "facts",
      "field": "country_of_residence",
      "value": "India",
      "confidence": 1.0,
      "evidence": "I live in India"
    }
  ]
}
```"""

test = re.sub(r"```json|```","",test)
data = json.loads(test)
print(data["extracted_fields"])