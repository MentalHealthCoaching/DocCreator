import os
import configparser

class TemplateManager:
    """
    A class to manage document templates and their associated variables.
    Attributes:
        config (Config): Configuration object containing settings.
        templates_dir (str): Directory where templates are stored.
    Methods:
        get_template_names():
            Retrieves a list of template filenames with a .docx extension.
        get_template_variables(template_name):
            Retrieves a dictionary of variables from the .ini file associated with the given template.
    """
    def __init__(self, config):
        self.config = config
        self.templates_dir = config.get_templates_dir()

    def get_template_names(self):
        return [f for f in os.listdir(self.templates_dir) if f.endswith('.docx')]

    def get_template_variables(self, template_name):
        ini_file = os.path.join(self.templates_dir, f"{os.path.splitext(template_name)[0]}.ini")
        if os.path.exists(ini_file):
            config = configparser.ConfigParser()
            config.read(ini_file, encoding='utf-8')
            return dict(config['Variables'])
        return {}
