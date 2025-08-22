import yaml

class Config:
    """
    Configuration holder for API keys and HTTP/data endpoints.
    """
    def __init__(
        self,
        openai_model: str = None,   
        apikey: str = None,
        llmkey: str = None,
        data_dir: str = None,  # new field
        pdf: str = None,
        questions: str = None,
        dest: str = None,
    ):
        self.openai_model = openai_model
        self.apikey = apikey
        self.llmkey = llmkey
        self.data_dir = data_dir  # new field
        self.pdf = pdf
        self.questions = questions
        self.dest = dest

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

        data_section = data.get("data", {})
        data_dir = data_section.get("data_dir")
        pdf = data_section.get("pdf")
        questions = data_section.get("questions")

        http = data.get("http", {})
        dest = http.get("dest")

        return cls(
            openai_model=openai_model,
            apikey=apikey,
            llmkey=llmkey,
            data_dir=data_dir,
            pdf=pdf,
            questions=questions,
            dest=dest
        )

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.
        """
        return bool(
            self.openai_model and
            self.apikey and
            self.data_dir and
            self.llmkey and
            self.pdf and
            self.questions and
            self.dest
        )
