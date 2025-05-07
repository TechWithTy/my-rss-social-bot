import yaml
import os
from src.data.examples.example_config_dict import example_config_data

def save_to_yaml(data: dict, filename: str = "config.yaml"):
    """
    Saves the given dictionary as a YAML file in the _configs root folder.
    :param data: Dictionary containing configuration parameters.
    :param filename: Name of the output YAML file.
    """
    try:
        # Ensure the _configs directory exists
        config_dir = "_configs"
        os.makedirs(config_dir, exist_ok=True)

        # Define the full path
        file_path = os.path.join(config_dir, filename)

        with open(file_path, "w") as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

        print(f"YAML file saved at: {file_path}")
    except Exception as e:
        print(f"Error saving YAML file: {e}")




# Call the function to save the YAML file
save_to_yaml(example_config_data, "config.yaml")
