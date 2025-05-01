from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import base64
import requests
import json
import tempfile

app = FastAPI()

API_KEY = "oj1xWjuWMuDtSVf9O9dF16vwIxMPSlV0ONRGH5NYeHD3gI8ydt"

@app.post("/identify")
async def identify_plant_api(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        encoded_string = base64.b64encode(contents).decode("utf-8")

        payload = {
            "images": [encoded_string],
            "latitude": 49.207,
            "longitude": 16.608,
            "similar_images": True
        }

        headers = {
            "Api-Key": API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://plant.id/api/v3/identification",
            headers=headers,
            data=json.dumps(payload)
        )

        response.raise_for_status()
        result = response.json()
        plant_name, probability = extract_plant_name_from_api_response(result)

        return {
            "plant_name": plant_name,
            "confidence": round(probability * 100, 2),
            "confidence_level": classify_confidence(probability)
        }

    except requests.exceptions.RequestException as e:
        return JSONResponse(status_code=500, content={"error": f"API request error: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error: {str(e)}"})

def extract_plant_name_from_api_response(api_response):
    suggestions = api_response["result"]["classification"]["suggestions"]
    highest = max(suggestions, key=lambda x: x["probability"])
    return highest["name"], highest["probability"]

def classify_confidence(prob):
    if prob >= 0.7:
        return "High"
    elif prob >= 0.5:
        return "Moderate"
    else:
        return "Low"
