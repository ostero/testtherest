import yaml

class Config:
    """
    Configuration holder for API keys and HTTP endpoints.
    """
    def __init__(
        self,
        openai_model: str = None,   
        llmkey: str = None,
    ):
        self.openai_model = openai_model
        self.llmkey = llmkey

    @classmethod
    def load_from_yaml(cls, filename: str = "api_key.yaml") -> "Config":
        """
        Load configuration from a YAML file.
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        providers = data.get("providers", {})
        openai_settings = providers.get("openai", {})
        openai_model = openai_settings.get("model")

        keys = data.get("keys", {})
        llmkey = keys.get("llm")
        http = data.get("http", {})
        return cls(openai_model=openai_model, llmkey=llmkey)

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.
        """
        return bool(
            self.openai_model and
            self.llmkey 
        )
