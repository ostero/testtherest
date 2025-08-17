import yaml

class Config:
    """
    Configuration holder for API keys and HTTP endpoints.
    """
    def __init__(
        self,
        ollama_model: str = None,
        openai_model: str = None,   
        apikey: str = None,
        llmkey: str = None,
        src: str = None,
        dest: str = None,
    ):
        self.ollama_model = ollama_model
        self.openai_model = openai_model
        self.apikey = apikey
        self.llmkey = llmkey
        self.src = src
        self.dest = dest

    @classmethod
    def load_from_yaml(cls, filename: str = "api_key.yaml") -> "Config":
        """
        Load configuration from a YAML file.
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        providers = data.get("providers", {})
        ollama_settings = providers.get("ollama", {})
        ollama_model = ollama_settings.get("model")
        openai_settings = providers.get("openai", {})
        openai_model = openai_settings.get("model")

        keys = data.get("keys", {})
        apikey = keys.get("api")
        llmkey = keys.get("llm")
        http = data.get("http", {})
        src = http.get("src")
        dest = http.get("dest")
        return cls(ollama_model=ollama_model, openai_model=openai_model, apikey=apikey, llmkey=llmkey, src=src, dest=dest)

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.
        """
        return bool(
            self.ollama_model and
            self.openai_model and
            self.apikey and
            self.llmkey and
            self.src and
            self.dest
        )
