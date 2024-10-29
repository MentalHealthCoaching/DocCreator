import configparser

class ConfigManager:
    """
    ConfigManager is a class responsible for managing configuration settings from a configuration file.
    Attributes:
        config (ConfigParser): An instance of ConfigParser to read configuration files.
    Methods:
        __init__(config_file):
            Initializes the ConfigManager with the given configuration file.
        get(section, key):
            Retrieves the value for a given section and key from the configuration file.
        get_templates_dir():
            Returns the directory path for templates from the configuration file.
        get_signers_dir():
            Returns the directory path for signers from the configuration file.
        get_public_key_path():
            Returns the file path for the public key from the configuration file.
        get_private_key_path():
            Returns the file path for the private key from the configuration file.
        get_output_dir():
            Returns the directory path for output files from the configuration file.
        get_verification_url():
            Returns the verification URL from the configuration file.
        get_logging_config():
            Returns a dictionary containing logging configuration settings.
        get_nextcloud_config():
            Returns a dictionary containing Nextcloud configuration settings.
    """
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get(self, section, key):
        return self.config.get(section, key)

    def get_templates_dir(self):
        return self.get('Paths', 'templates_dir')

    def get_signers_dir(self):
        return self.get('Paths', 'signers_dir')

    def get_public_key_path(self):
        return self.get('Paths', 'public_key')

    def get_private_key_path(self):
        return self.get('Paths', 'private_key')

    def get_output_dir(self):
        return self.get('Paths', 'output_dir')

    def get_verification_url(self):
        return self.get('Verification', 'url')

    def get_logging_config(self):
        return {
            'log_file': self.get('Logging', 'log_file'),
            'log_level': self.get('Logging', 'log_level')
        }

    def get_nextcloud_config(self):
        return {
            'enabled': self.get('Nextcloud', 'enabled').lower() == 'true',
            'url': self.get('Nextcloud', 'url'),
            'username': self.get('Nextcloud', 'username'),
            'password': self.get('Nextcloud', 'password'),
            'upload_pattern': self.get('Nextcloud', 'upload_pattern')
        }
