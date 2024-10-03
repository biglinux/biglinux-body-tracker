import subprocess
import threading
import asyncio # Importa o módulo asyncio para manipular a variavel tempo / Import the asyncio module to manipulate the time variable
import time # Importa o módulo time para manipular a variavel tempo / Import the time module to manipulate the time variable
import os # Importa o módulo os para manipular o sistema operacional / Import the os module to manipulate the operating system
import sys # Import the sys module to be able to read the first argument passed to the script
import argparse  # para ler parâmetros do comando do terminal / to read parameters from terminal command
import configparser # Importa o módulo configparser para manipular o arquivo de configuração / Import the configparser module to manipulate the configuration file
import math # Importa o módulo math para manipular cálculos matemáticos / Import the math module to manipulate math calculations
import numpy as np  # para realizar cálculos / to make calculations
import tkinter as tk  # para exibir dicas de ferramentas / to show tooltip
from PIL import Image # Importa o módulo Image para manipular a imagem / Import the Image module to manipulate the image
from pynput.mouse import Button, Controller  # para usar o mouse / to use mouse
import cv2 # Importa o módulo OpenCV para manipular a imagem / Import the OpenCV module to manipulate the image
import mediapipe as mp  # para capturar informações do rosto / to capture info about face
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates

def read_config(var_name=None, section_name='General', config_file='config.conf', default_value=None):
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, '.config', 'biglinux-body-tracker')

    config_path = os.path.join(config_dir, config_file)

    config = configparser.ConfigParser()
    config.read(config_path)

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



#####################
# Definir argumentos e suas propriedades para serem usados pelo argparse
# Define arguments and their properties to be used by argparse
#####################
arg_info = {
    'view': {
        'type': int,
        'help': 'Show webcam image',
        'default': 0
    },
    'mouseDetectionMode': {
        'type': int,
        'help': 'Mouse detection mode 1 or 2 or 3 or 4',
        'default': 4
    },
    'startIsNeutral': {
        'type': bool,
        'help': 'Start position is neutral position True or False',
        'default': True
    },
    'enableLeftEye': {
        'type': bool,
        'help': 'Use left eye blink True or False',
        'default': True
    },
    'enableRightEye': {
        'type': bool,
        'help': 'Use right eye blink True or False',
        'default': True
    },
    'leftEyeBlinkFunction': {
        'type': str,
        'help': 'clickLeft or clickCenter or clickRight or drag or doubleClick or scrollV or scrollH or ',
        'default': 'clickLeft'
    },
    'enableKiss': {
        'type': bool,
        'help': 'Use kiss True or False',
        'default': True
    },
    'webcamid': {
        'type': int,
        'help': 'Webcam ID',
        'default': 0
    },
    'webcamx': {
        'type': int,
        'help': 'Webcam X resolution',
        'default': 1024
    },
    'webcamy': {
        'type': int,
        'help': 'Webcam Y resolution',
        'default': 768
    },
    'fps': {
        'type': int,
        'help': 'Frames per second',
        'default': 15
    },
    'plot': {
        'type': int,
        'help': 'Plot the face landmarks',
        'default': '0'
    },
    'blinkToClick': {
        'type': int,
        'help': 'Blink to click',
        'default': 1
    },
    'minimalMouseMoveY': {
        'type': int,
        'help': 'Minimal mouse move Y',
        'default': 3
    },
    'minimalMouseMoveX': {
        'type': int,
        'help': 'Minimal mouse move X',
        'default': 3
    },
    'slowMouseMoveY': {
        'type': int,
        'help': 'Slow mouse move Y',
        'default': 9
    },
    'slowMouseMoveX': {
        'type': int,
        'help': 'Slow mouse move X',
        'default': 9
    },
    'mouseSpeedX': {
        'type': int,
        'help': 'Mouse speed X',
        'default': 40
    },
    'mouseSpeedY': {
        'type': int,
        'help': 'Mouse speed Y',
        'default': 40
    },
    'autoBrightness': {
        'type': bool,
        'help': 'Automatically adjust brightness',
        'default': True
    },
    'mouthScroll': {
        'type': int,
        'help': 'Enable mouth scrolling',
        'default': 0
    },
}



##############################
# Ler argumentos da linha de comando
# Read args from command line
##############################
parser = argparse.ArgumentParser()

# Adicionar argumentos ao analisador
# Add arguments to the parser
for arg_name, arg_details in arg_info.items():
    parser.add_argument(f'--{arg_name}', type=str, help=arg_details['help'], default=str(arg_details['default']))

# Analisar argumentos fornecidos
# Parse provided arguments
args = parser.parse_args()

# Armazenar argumentos fornecidos em uma lista
# Store provided arguments in a list
provided_args = []
for arg in vars(args):
    if f"--{arg}" in sys.argv:
        provided_args.append(arg)

# Função para atualizar os argumentos com base nos argumentos fornecidos e nas configurações
# Function to update arguments based on provided arguments and settings
# Read the configuration file and get the value for this argument
def update_arg(args, arg_name, default_value, provided_args):

    conf_value = read_config(arg_name, section_name='General', default_value=None)

    # If the argument is provided in the command line, use that value
    if arg_name not in provided_args:
        # If a value was found in the configuration file, use that value
        if conf_value is not None:
            setattr(args, arg_name, conf_value)
    else:
        # If the argument is provided in the command line, write it to the configuration file
        write_config(arg_name, str(getattr(args, arg_name)))

    # Get the value of the argument
    arg_value = getattr(args, arg_name)

    # If the argument is a boolean, convert to boolean
    if default_value is bool:
        arg_value = arg_value.lower() in ['true', 't', 'yes', 'y', '1']
    else:
        # If the argument is not a boolean, convert to the desired type
        arg_value = default_value(arg_value)

    # Set the value of the argument
    setattr(args, arg_name, arg_value)

# Atualizar argumentos usando a função update_arg
# Update arguments using the update_arg function
for arg_name, arg_details in arg_info.items():
    update_arg(args, arg_name, arg_details['type'], provided_args)

if not args.enableLeftEye:
    leftEye = 1
    leftEyeOld = 1
    leftEyeMean = 1
    leftEyeNormalized = 1

if not args.enableRightEye:
    rightEye = 1
    rightEyeOld = 1
    rightEyeMean = 1
    rightEyeNormalized = 1



######################
# Iniciar variáveis
# Init variables
######################
overLeftEye = 0
overRightEye = 0
action = ''
mousePointYabsOld = 0
mousePointXabsOld = 0
mousePointXApply = 0
mousePointYApply = 0
leftEyeBlinkOld = 0
leftEyeBlink = 0
rightEyeBlink = 0
irisDistance = 1
kiss = 1
confirmationTimeout = 0
eyesOpen = 5
waitFrames = 10
clicked = False
leftClickedConstant = False
scrollModeVertical = False
scrollModeHorizontal = False
changeLeftMove = False
leftMoved = 'no'
changeRightMove = False
rightMoved = 'no'
stopCursor = False
slowMove = 10
rightEyeBlinkOld = 0
leftEyeBlinkOld = 0
leftEyeMean = 0
rightEyeMean = 0
mouthCenterLeftOld = 0
mouthCenterRightOld = 0
tooltipWait = False
mouthCenterLeftOldLock = False
mouthCenterRightOldLock = False
leftClicked = False
rightClicked = False
standByClick = False
frameNumber = 0
mousePositionFrameX = 0
mousePositionFrameY = 0
maybeScreenLimitX = 0
maybeScreenLimitY = 0
clicktime = 0
zeroPointX = None
zeroPointY = None
zeroPointX2 = None
zeroPointY2 = None
mouseLeftClick = False
mouseRightClick = False
line1 = []
line = []
countFrames = 0
oldframeTime = 0
fpsRealMean = args.fps
gain = 400
fpsBrightness = 0

# Get images from webcam
with open('videosource.py') as file:
    exec(file.read())
source = WebcamSource(width=args.webcamx, height=args.webcamy, fps=args.fps, camera_id=args.webcamid)


#####################
# Função para obter a região dos olhos para detectar brilho (ROI)
# Function to get the eyes region to detect brightness (ROI)
#####################
def get_eyes_roi(frame, landmarks):
    height, width, _ = frame.shape
    left_eye_indices = [224, 193, 128, 229]
    right_eye_indices = [444, 449, 251, 441]

    # Função para obter a ROI de um olho com base nos índices
    # Function to get the ROI of an eye based on the indices
    def get_eye_roi(indices):
        eye_roy_array = []
        for index in indices:
            pixelCoordinates = _normalized_to_pixel_coordinates(landmarks[index].x, landmarks[index].y, width, height)
            if pixelCoordinates is not None:
                x, y = pixelCoordinates
                eye_roy_array.append((x, y))
        eye_roy_array = np.array(eye_roy_array)
        eye_roy_array_rect = cv2.boundingRect(eye_roy_array)
        return frame[eye_roy_array_rect[1]:eye_roy_array_rect[1] + eye_roy_array_rect[3],
                     eye_roy_array_rect[0]:eye_roy_array_rect[0] + eye_roy_array_rect[2]]

    # Obter ROIs para ambos os olhos
    # Get ROIs for both eyes
    left_eye_roi = get_eye_roi(left_eye_indices)
    right_eye_roi = get_eye_roi(right_eye_indices)

    # Retornar a ROI com a menor área
    # Return the ROI with the smallest area
    if left_eye_roi.size < right_eye_roi.size:
        return left_eye_roi
    else:
        return right_eye_roi
