import os
import configparser
import argparse

def read_config(var_name=None, section_name='General', config_file='config.conf', default_value=None):
    """
    Read configuration settings from a file.

    Args:
        var_name (str): The name of the variable to be read. Default is None, which returns all variables in the section.
        section_name (str): The name of the section to read the variable from. Default is 'General'.
        config_file (str): The name of the configuration file. Default is 'config.conf'.

    Returns:
        The value of the specified variable, or a dictionary containing all variables in the specified section.
    """
    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Create the full path to the configuration file
    config_path = os.path.join(home_dir, '.config', 'biglinux-body-tracker', config_file)

    # Create a ConfigParser object and read the settings from the file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Check if the section exists
    if not config.has_section(section_name):
        raise ValueError(f'Section "{section_name}" not found in configuration file "{config_file}"')

    # If var_name is None, return a dictionary containing all variables in the section
    if var_name is None:
        return dict(config[section_name])

    # Otherwise, return the value of the specified variable
    if not config.has_option(section_name, var_name):
        return default_value

    return config[section_name][var_name]

def write_config(var_name, var_value, section_name='General', config_file='config.conf'):
    """
    Write configuration settings to a file.

    Args:
        var_name (str): The name of the variable to be updated.
        var_value (str): The new value of the variable.
        section_name (str): The name of the section in which to update the variable. Default is 'General'.
        config_file (str): The name of the configuration file. Default is 'config.conf'.
    """
    # Get the user's home directory
    home_dir = os.path.expanduser("~")

    # Create the full path to the configuration file
    config_path = os.path.join(home_dir, '.config', 'biglinux-body-tracker', config_file)

    # Create the directory if it doesn't exist
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except OSError as exc:
            # Handle the case where the directory can't be created
            if exc.errno != errno.EEXIST:
                raise

    # Create a new ConfigParser object
    config = configparser.ConfigParser()

    # Read the current settings from the file
    config.read(config_path)

    # Add the section if it doesn't exist
    if not config.has_section(section_name):
        config.add_section(section_name)

    # Update the specified variable with the new value
    config[section_name][var_name] = var_value

    # Write the updated settings back to the file
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def get_value(var_name, default_value=None, section_name='General', config_file='config.conf'):
    config_value = read_config(var_name, section_name, config_file)
    if config_value is not None:
        return config_value
    else:
        return default_value

# After this line only to debug
def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('--view', type=int, help='View variable')
    args = parser.parse_args()

    if args.view is not None:
        # Save the view value to the configuration file if it's provided through the command line
        write_config('view', str(args.view), 'General')

    # Get the view variable
    view_default = 0
    view = get_value('view', view_default)

    print(f"View: {view}")

if __name__ == '__main__':
    main()
