import google.generativeai as genai

genai.configure(api_key="AIzaSyAEIalRaXgW3NQsNr-HD7T5DLOCyNuhApc") # Replace with your api key

for model in genai.list_models():
    print(model)