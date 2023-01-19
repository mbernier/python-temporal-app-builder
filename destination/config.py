
import configparser

def config(config_item):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config["temporal.io"][config_item]


