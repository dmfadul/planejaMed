import json

class Config:
    def __init__(self, config_file='instance/config_file.json'):
        self.config_file = config_file
        self.load(config_file)

    def load(self, config_file):
        with open(config_file, 'r') as file:
            self.config = json.load(file)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is default:
                break
        return value

    def set(self, key, value):
        keys = key.split('.')
        print(keys[:-1], self.config)
        config_section = self.config
        for k in keys[:-1]:
            if k not in config_section:
                config_section[k] = {}
            config_section = config_section[k]
        config_section[keys[-1]] = value

        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=4)
