import os
import configparser
import argparse


def read_config(var_name=None, section_name='General', config_file='config.conf', default_value=None):
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, '.config', 'biglinux-body-tracker')

    # Check if the config directory exists
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    config_path = os.path.join(config_dir, config_file)

    # Check if the config file exists, if not, create it with [General]
    if not os.path.exists(config_path):
        config = configparser.ConfigParser()
        config[section_name] = {}
        config[section_name]['var_name'] = 'var_value'
        with open(config_path, 'w') as configfile:
            config.write(configfile)

    config = configparser.ConfigParser()
    config.read(config_path)

    if not config.has_section(section_name):
        raise ValueError(f'Section "{section_name}" not found in configuration file "{config_file}"')

    if var_name is None:
        return dict(config[section_name])

    if not config.has_option(section_name, var_name):
        return default_value

    return config[section_name][var_name]


def write_config(var_name, var_value, section_name='General', config_file='config.conf'):
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, '.config', 'biglinux-body-tracker')
    config_path = os.path.join(config_dir, config_file)

    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    config = configparser.ConfigParser()
    config.read(config_path)

    if not config.has_section(section_name):
        config.add_section(section_name)

    config[section_name][var_name] = var_value

    with open(config_path, 'w') as configfile:
        config.write(configfile)


def get_value(var_name, default_value=None, section_name='General', config_file='config.conf'):
    config_value = read_config(var_name, section_name, config_file)
    if config_value is not None:
        return config_value
    else:
        return default_value


def main():
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('--view', type=int, help='View variable')
    args = parser.parse_args()

    if args.view is not None:
        write_config('view', str(args.view), 'General')

    view_default = 0
    view = get_value('view', view_default)

    print(f"View: {view}")

