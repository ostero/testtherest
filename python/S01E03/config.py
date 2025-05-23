import yaml

class Config:
    """
    Configuration holder for API keys and HTTP endpoints.
    """
    def __init__(
        self,
        apikey: str = None,
        llmkey: str = None,
        src: str = None,
        dest: str = None,
        auth: dict = None
    ):
        self.apikey = apikey
        self.llmkey = llmkey
        self.src = src
        self.dest = dest
        self.auth = auth or {}

    @classmethod
    def load_from_yaml(cls, filename: str = "api_key.yaml") -> "Config":
        """
        Load configuration from a YAML file.
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        keys = data.get("keys", {})
        apikey = keys.get("api")
        llmkey = keys.get("llm")
        http = data.get("http", {})
        src = http.get("src")
        dest = http.get("dest")
        auth = http.get("auth", {})
        return cls(apikey=apikey, llmkey=llmkey, src=src, dest=dest, auth=auth)

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.
        """
        return bool(
            self.apikey and
            self.llmkey and
            self.src and
            self.dest and
            self.auth.get("username") and
            self.auth.get("password")
        )