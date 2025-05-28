import yaml

class Config:
    def __init__(self, apikey='', src='', dest=''):
        self.apikey = apikey
        self.src = src
        self.dest = dest

    @classmethod
    def load_from_yaml(cls, filename='api_key.yaml'):
        with open(filename, 'r') as infile:
            data = yaml.safe_load(infile)
            http = data.get('http', {})
            return cls(
                apikey=data.get('apikey', '').rstrip(),
                src=http.get('src', ''),
                dest=http.get('dest', '')
            )

    def is_valid(self):
        return self.apikey != '' and self.src != '' and self.dest != ''