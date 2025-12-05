from openai import OpenAI

class Planner:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        