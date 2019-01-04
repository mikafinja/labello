from flask import Flask
from flask_bootstrap import Bootstrap
import yaml
import logging
import sys
import os.path
from . import fonts
from brother_ql.backends import backend_factory, guess_backend

local_config_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1]
local_config_path.append("config.local.yaml")
local_config_path = os.path.sep.join(local_config_path)
config_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1]
config_path.append("config.yaml")
config_path = os.path.sep.join(config_path)

try:
    with open(local_config_path, 'r') as fh:
        config = yaml.load(fh)

except FileNotFoundError:
    with open(config_path, 'r') as fh:
        config = yaml.load(fh)

# LOGGING
logger = logging.getLogger('labello')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(config['logging']['level'])
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

# initialize flask app
app = Flask(__name__)
if config['logging']['level'] == 10:
    app.debug = True
else:
    app.debug = False

# set config parameters
try:
    app.config['port'] = config['server']['port']
except:
    app.config['port'] = 5000

try:
    app.config['host'] = config['server']['host']
except:
    app.config['host'] = "::1"

# serve bootstrap from cdn or via labello
try:
    app.config['BOOTSTRAP_SERVE_LOCAL'] = config['website']['bootstrap_local']
except:
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# get margins
try:
    app.config['margins'] = config['label']['margins']
except:
    app.config['margins'] = {"top": 24, "bottom": 24, "left": 24, "right": 24}

# get font_spacing
try:
    app.config['font_spacing'] = config['label']['font_spacing']
except:
    app.config['font_spacing'] = 13

app.config['DEFAULT_PARSERS'] = [
    'flask.ext.api.parsers.JSONParser',
    'flask.ext.api.parsers.URLEncodedParser',
    'flask.ext.api.parsers.MultiPartParser'
]

app.config['WEBSITE'] = config['website']

node_path = os.path.dirname(os.path.abspath(__file__)).split(os.path.sep)[:-1]
node_path.append("node_modules")
app.config['node_path'] = os.path.sep.join(node_path)

# initialize bootstrap
bootstrap = Bootstrap(app)

# get and load fonts
font = fonts.Fonts()
for folder in config['fonts']:
    font.add_fonts(folder)
app.config['fonts'] = font.fontlist()
logger.debug(app.config['fonts'])

# setting up printer
try:
    backend = guess_backend(config['printer']['device'])
    logger.info(backend)
except ValueError:
    logger.error('Unable to select the proper backend. Check your config')
    sys.exit(20)

from . import web
