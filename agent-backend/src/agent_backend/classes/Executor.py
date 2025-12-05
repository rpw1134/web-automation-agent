from openai import AsyncClient

class Executor:
    def __init__(self, env_key: str):
        self.client = AsyncClient(api_key=env_key)
        
    def parse_functions(self, function_calls: list[str]):
        pass