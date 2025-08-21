import yaml

class Config:
    """
    Configuration holder for API keys and HTTP endpoints.
    """
    def __init__(
        self,
        openai_model: str = None,   
        apikey: str = None,
        llmkey: str = None,
        src: str = None,
        dest: str = None,
        page: str = None,  # new field
    ):
        self.openai_model = openai_model
        self.apikey = apikey
        self.llmkey = llmkey
        self.src = src
        self.dest = dest
        self.page = page  # new field

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
        apikey = keys.get("api")
        llmkey = keys.get("llm")
        http = data.get("http", {})
        src = http.get("src")
        dest = http.get("dest")
        page = http.get("page")  # new field
        return cls(openai_model=openai_model, apikey=apikey, llmkey=llmkey, src=src, dest=dest, page=page)

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.
        """
        return bool(
            self.openai_model and
            self.apikey and
            self.llmkey and
            self.src and
            self.dest and
            self.page
        )
