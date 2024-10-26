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
import cv2
import numpy as np
from PIL import Image

class VideoSource:
    def __init__(self, flip=False, display=False, dtype=np.uint8):
        self._name = "VideoSource"
        self._capture = None
        self._display = display
        self._dtype = dtype
        self._flip = flip

    def get_fps(self):
        return self._capture.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_image_size(self):
        width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return width, height

    def release(self):
        self._capture.release()
        cv2.destroyAllWindows()

    def __iter__(self):
        self._capture.isOpened()
        return self

    def __next__(self):
        ret, frame = self._capture.read()

        if self._flip:
            frame = cv2.flip(frame, 3)

        if not ret:
            raise StopIteration

        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise StopIteration

        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.asarray(Image.fromarray(cv2_im_rgb), dtype=self._dtype)

        return frame, frame_rgb

    def __del__(self):
        self.release()

    def gain(self, gain):

        Gain = self._capture.get(cv2.CAP_PROP_GAIN)
        Brightness = self._capture.get(cv2.CAP_PROP_BRIGHTNESS)
        Contrast = self._capture.get(cv2.CAP_PROP_CONTRAST)
        Gamma = self._capture.get(cv2.CAP_PROP_GAMMA)
        Backlight = self._capture.get(cv2.CAP_PROP_BACKLIGHT)

        if gain == 1:
            self._capture.set(cv2.CAP_PROP_GAIN, Gain + 2)
            self._capture.set(cv2.CAP_PROP_BRIGHTNESS, Brightness + 1)
            self._capture.set(cv2.CAP_PROP_CONTRAST, Contrast + 2)
            self._capture.set(cv2.CAP_PROP_GAMMA, Gamma + 1)
            self._capture.set(cv2.CAP_PROP_BACKLIGHT, Backlight + 1)
        elif gain == 0:
            self._capture.set(cv2.CAP_PROP_GAIN, Gain - 2)
            self._capture.set(cv2.CAP_PROP_BRIGHTNESS, Brightness - 1)
            self._capture.set(cv2.CAP_PROP_CONTRAST, Contrast - 2)
            self._capture.set(cv2.CAP_PROP_GAMMA, Gamma - 2)
            self._capture.set(cv2.CAP_PROP_BACKLIGHT, Backlight - 1)


    def show(self, frame, webcamx, webcamy):
        cv2.namedWindow("BigHeadTrack", cv2.WINDOW_GUI_NORMAL)
        cv2.imshow("BigHeadTrack", frame)
        cv2.resizeWindow("BigHeadTrack", webcamx, webcamy)


class WebcamSource(VideoSource):
    def __init__(
        self,
        camera_id=0,
        width=1024,
        height=768,
        fps=15,
        autofocus=0,
        absolute_focus=75,
        flip=True,
        display=False,
    ):
        super().__init__(flip, display)
        self._capture = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self._capture.set(cv2.CAP_PROP_GAIN, 0)
        self._capture.set(cv2.CAP_PROP_EXPOSURE, (1 / (fps / 10000)))
        self._capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self._capture.set(cv2.CAP_PROP_FPS, fps)
        self._capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        self._capture.set(cv2.CAP_PROP_FOCUS, absolute_focus / 255)


class FileSource(VideoSource):
    def __init__(self, file_path, flip=False, display=False):
        super().__init__(flip, display)
        self._capture = cv2.VideoCapture(str(file_path))

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

#####################
# Início do código da dica de ferramenta / Tooltip code start
#####################
import tkinter as tk
tkTooltip = tk.Tk()

# Exibir texto usando tk / Show text using tk
async def tkTooltipChange(text, color, bg, mouseX, mouseY):
    # Criar a janela da tooltip se ainda não foi criada
    # Create the tooltip window if it hasn't been created yet
    global tkTooltip
    if not tkTooltip:
        tkTooltip = tk.Toplevel()
        tkTooltip.transient(root) # Tornar a janela de tooltip "filha" da janela principal / Make the tooltip window a "child" of the main window
    
    # Desabilitar a borda da janela / Disable window border
    tkTooltip.wm_overrideredirect(True)


    # Configurar variáveis para a dica de ferramenta
    # Set up variables for the tooltip
    tooltipText = text
    tooltipTextColor = color
    tooltipBgColor = bg
    tooltipFontSize = 20
    if text == "":
        tooltipWidth = 20
        tooltipHeight = 20
    elif text == "hide":
        tooltipWidth = 0
        tooltipHeight = 0
    else:
        tooltipWidth = len(text) * tooltipFontSize
        tooltipHeight = tooltipFontSize + 14

    # Definir posição e tamanho da dica de ferramenta
    # Set tooltip position and size
    if mouseX > 300:
        mouseX = mouseX - tooltipWidth - 40
    else:
        mouseX = mouseX + tooltipWidth + 40

    if mouseY > 180:
        mouseY = mouseY - tooltipHeight - 40
    else:
        mouseY = mouseY + tooltipHeight + 40


    tkTooltip.wm_geometry(f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}")
    
    # Remover o widget Label anterior antes de criar um novo
    # Hide all the children of a widget. It is used
    # when the user wants to hide the tooltip.
    for child in tkTooltip.winfo_children():
        child.destroy()


    # Configurar e aplicar fonte e estilo da dica de ferramenta
    # Configure and apply font and style for the tooltip
    l = tk.Label(tkTooltip, font=("Ubuntu Mono", tooltipFontSize))
    l.pack(expand=True)
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor, width=tooltipWidth, height=tooltipHeight, borderwidth=2, highlightbackground=tooltipTextColor, highlightthickness=2)
    
    # Configurar aparência da dica de ferramenta
    # Configure tooltip appearance
    tkTooltip.configure(background=bg)

    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()


# Exibir texto no centro da tela / Display text in the center of the screen
async def tkTooltipChangeCenter(text, color, bg):
    # Configurar variáveis para a dica de ferramenta
    # Set up variables for the tooltip
    tooltipText = text
    tooltipTextColor = color
    tooltipBgColor = bg
    tooltipFontSize = 20
    tooltipWidth = int(len(text) * tooltipFontSize / 2)
    tooltipHeight = tooltipFontSize * 2 + 20
    mouseX = int((tkTooltip.winfo_screenwidth() / 2) - tooltipWidth / 2)
    mouseY = int((tkTooltip.winfo_screenheight() / 2) - tooltipHeight / 2)


    # Desabilitar a borda da janela / Disable window border
    tkTooltip.wm_overrideredirect(True)

    tkTooltip.geometry(
        f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}".format(
            tkTooltip.winfo_screenwidth(), tkTooltip.winfo_screenheight()
        )
    )
    # Configurar aparência da dica de ferramenta
    # Configure tooltip appearance
    tkTooltip.configure(background=bg)

    # Configurar e aplicar fonte
    # Configure and apply font
    l = tk.Label(font=("Ubuntu Mono", tooltipFontSize))
    l.pack(expand=True)
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor, width=tooltipWidth, height=tooltipHeight, borderwidth=2, highlightbackground=color, highlightthickness=2)
    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()

# Initialize mouse controller
mouse = Controller()

# Function to get screen size using xrandr
def get_screen_size():
    try:
        # Execute xrandr command and capture output
        result = subprocess.run(["xrandr"], capture_output=True, text=True)
        output = result.stdout

        # Filter the line containing the current resolution
        resolution_line = next((line for line in output.splitlines() if '*' in line), None)

        if resolution_line:
            # Find resolution in WxH format, e.g., "1920x1080"
            resolution = next((word for word in resolution_line.split() if 'x' in word), None)
            
            if resolution:
                width, height = map(int, resolution.split('x'))
                return width, height

        # Return default values if resolution detection fails
        return 1920, 1080
    except Exception as e:
        print(f"Error obtaining screen resolution with xrandr: {e}")
        return 1920, 1080  # Default value in case of error

# Get screen size
screen_width, screen_height = get_screen_size()

# Move mouse to the center of the screen
mouse.position = (screen_width / 2, screen_height / 2)

# Global variables to store the last known mouse position
last_known_x = None
last_known_y = None

# Variables for caching mouse position
cached_mouse_position = (0, 0)
last_mouse_update_time = 0

# Function to get the current mouse position compatible with Xorg and Wayland
def get_mouse_position():
    global last_known_x, last_known_y, cached_mouse_position, last_mouse_update_time
    current_time = time.time()
    
    # Update mouse position once per two seconds
    if current_time - last_mouse_update_time > 2:
        if os.getenv('XDG_SESSION_TYPE') == 'wayland':
            try:
                result = subprocess.run(["kdotool", "getmouselocation", "--shell"], capture_output=True, text=True)
                output = result.stdout
                position = {}

                for line in output.splitlines():
                    if line.startswith("X="):
                        position['X'] = int(line.split('=')[1].strip())
                    elif line.startswith("Y="):
                        position['Y'] = int(line.split('=')[1].strip())

                if 'X' in position and 'Y' in position:
                    last_known_x, last_known_y = position['X'], position['Y']
                cached_mouse_position = (last_known_x, last_known_y)
            except Exception as e:
                print(f"Error obtaining mouse position with kdotool: {e}")
        else:
            last_known_x, last_known_y = mouse.position
            cached_mouse_position = (last_known_x, last_known_y)
        
        last_mouse_update_time = current_time
    
    return cached_mouse_position

# Function to set the mouse position compatible with Xorg and Wayland
def set_mouse_position(delta_x, delta_y):
    global last_known_x, last_known_y, cached_mouse_position, last_mouse_update_time
    if os.getenv('XDG_SESSION_TYPE') == 'wayland':
        current_x, current_y = get_mouse_position()
        new_x = current_x + delta_x
        new_y = current_y + delta_y
        if last_known_x is not None and last_known_y is not None:
            # Ensure the new position does not exceed screen boundaries
            new_x = max(0, min(new_x, screen_width - 1))
            new_y = max(0, min(new_y, screen_height - 1))
        mouse.position = (new_x, new_y)
        
        # Save caches changes in mouse position until detected again with kdotool
        cached_mouse_position = (new_x, new_y)
    else:
        mouse.move(delta_x, delta_y)

# Function to perform mouse actions
def make_action(action):
    globals()['action'] = action
    mouse_position = get_mouse_position()
    
    if action == 'pressLeft':
        asyncio.run(tkTooltipChange('', "#000000", "#00b600", mouse_position[0], mouse_position[1]))
        mouse.press(Button.left)

    elif action == 'releaseLeft':
        mouse.release(Button.left)
        asyncio.run(tkTooltipChange('hide', "#000000", "#00b600", mouse_position[0], mouse_position[1]))
        globals()['waitFrames'] = int(fpsRealMean / 6)

    elif action == 'showOptions1':
        asyncio.run(tkTooltipChange('', "#000000", "#b6b63d", mouse_position[0], mouse_position[1]))
        globals()['stopCursor'] = True

    elif action == 'releaseOptions1':
        asyncio.run(tkTooltipChange('hide', "#000000", "#b6b63d", mouse_position[0], mouse_position[1]))
        globals()['stopCursor'] = False

    elif action == 'pressRight':
        asyncio.run(tkTooltipChange('', "#000000", "#b6b63d", mouse_position[0], mouse_position[1]))
        mouse.press(Button.right)

    elif action == 'releaseRight':
        asyncio.run(tkTooltipChange('hide', "#000000", "#b6b63d", mouse_position[0], mouse_position[1]))
        mouse.release(Button.right)
        globals()['waitFrames'] = int(fpsRealMean / 2)

    elif action == 'clickLeft':
        mouse.press(Button.left)
        mouse.release(Button.left)
        globals()['waitFrames'] = int(fpsRealMean / 2)

    elif action == 'clickRight':
        mouse.press(Button.right)
        mouse.release(Button.right)
        globals()['waitFrames'] = int(fpsRealMean / 2)

    elif action == 'enableCursor':
        globals()['stopCursor'] = False
        globals()['action'] = ''

    elif action == 'scrollV':
        if globals()['action'] == 'scrollV':
            globals()['stopCursor'] = False
            globals()['action'] = ''
            globals()['waitFrames'] = int(fpsRealMean / 2)
        else:
            globals()['stopCursor'] = True
            globals()['action'] = 'scrollV'
            globals()['waitFrames'] = int(fpsRealMean / 2)

    elif action == 'toggleKeyboard':
        subprocess.run(["qdbus", "org.onboard.Onboard", "/org/onboard/Onboard/Keyboard", "org.onboard.Onboard.Keyboard.ToggleVisible"])

#####################
# Função para calcular a distância entre pontos em eixos x e y - 2D
# Function to calculate the distance between points in axes x and y - 2D
#####################
def calculate_distance2D(var_name, top_indices, bottom_indices):
    # Get the X and Y coordinates of the top and bottom points
    top_pointsX = np.array([landmarks[index][0] for index in top_indices])
    bottom_pointsX = np.array([landmarks[index][0] for index in bottom_indices])
    top_pointsY = np.array([landmarks[index][1] for index in top_indices])
    bottom_pointsY = np.array([landmarks[index][1] for index in bottom_indices])
    # Calculate the distance between the top and bottom points
    distance_x = np.sum(np.sum(bottom_pointsX + 2) - np.sum(top_pointsX + 2))
    distance_y = np.sum(np.sum(bottom_pointsY + 2) - np.sum(top_pointsY + 2))
    if distance_x < 0:
        distance_x = 0
    if distance_y < 0:
        distance_y = 0
    if var_name == 'kiss':
        distance = (np.sum(distance_x + distance_y) / globals()['irisDistance'] - 1) * 50

    elif var_name == 'leftEye':
        distance = (np.sum(distance_x + distance_y) / globals()['overLeftEye'] ) * 50 - 9
        # if globals()['overLeftEye'] < 0:
        #     globals()['overLeftEye'] = 0
        if distance < 0:
            distance = 0
        # print(f"Distance L: {distance} distance X: {distance_x} distance Y: {distance_y}")

    elif var_name == 'rightEye':
        distance = (np.sum(distance_x + distance_y) / globals()['overRightEye'] ) * 50 - 9
        # if globals()['overRightEye'] < 0:
        #     globals()['overRightEye'] = 0
        if distance < 0:
            distance = 0
        # print(f"Distance R: {distance} distance X: {distance_x} distance Y: {distance_y}")


    else:
        distance = np.sum(distance_x + distance_y)
    # Save the distance in a global variable
    globals()[var_name] = distance
    # Save the running average of the distance in a global variable
    var_name_old = (var_name + 'Old')

    if not var_name_old in globals():

        globals()[var_name + 'Mean'] = distance
        globals()[var_name + 'Normalized'] = distance
        globals()[var_name + 'Old'] = distance
        globals()[var_name + 'Confirmation'] = 1
        globals()[var_name + 'Clicked'] = False



#####################
# Função para calcular a distância entre pontos em eixos x, y e z - 3D
# Function to calculate the distance between points in axes x, y, and z - 3D
#####################
def calculate_distance3D(var_name, top_indices, bottom_indices, distance_value, confirm_value, action_start, action_end):
    # Calculate the distance between the top and bottom points
    top_points = [landmarks[index] for index in top_indices]
    bottom_points = [landmarks[index] for index in bottom_indices]
    top_mean = np.sum(top_points)
    bottom_mean = np.sum(bottom_points)
    distance = np.linalg.norm((bottom_mean + 2) - (top_mean + 2)) * 500
    # Save the distance in a global variable
    globals()[var_name] = distance
    # Save the running average of the distance in a global variable
    var_name_old = (var_name + 'Old')
    var_name_normalized = (var_name + 'Normalized')
    var_name_mean = (var_name + 'Mean')

    if var_name_old in globals():
        globals()[var_name + 'Normalized'] = (distance + globals()[var_name + 'Mean']) / 2
        globals()[var_name + 'Old'] = (globals()[var_name + 'Old'] * fpsRealMean + distance) / (fpsRealMean + 1)
        globals()[var_name + 'Normalized'] = (distance + globals()[var_name + 'Old']) / 2
    else:
        globals()[var_name + 'Mean'] = distance
        globals()[var_name + 'Normalized'] = distance
        globals()[var_name + 'Old'] = distance

#####################
# Function to verify false clicks
#####################
def verify_false_click(var_name, distance_value, confirm_value, action_start, action_end):
    var_confirmation = globals()[f"{var_name}Confirmation"]
    distance = globals()[var_name]

    if globals()['confirmationTimeout'] == 0 and not globals()['clicked']:
        globals()[f"{var_name}Old"] = (globals()[f"{var_name}Old"] * fpsRealMean / 2 + distance) / (fpsRealMean / 2 + 1)
    
    globals()[f"{var_name}Mean"] = (distance + globals()[f"{var_name}Mean"]) / 2
    globals()[f"{var_name}Normalized"] = (distance + globals()[f"{var_name}Old"]) / 2

    var_mean = globals()[f"{var_name}Mean"]
    var_old = globals()[f"{var_name}Old"]
    var_normalized = globals()[f"{var_name}Normalized"]

    if not globals()[f"{var_name}Clicked"] and not globals()['clicked'] and eyesOpen >= 3 and waitFrames == 0:
        if (eyesOpen and distance < var_old * distance_value and not standByClick and 
            ((mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY) or 
             (rightMoved not in ['no', 'null']) or 
             (leftMoved not in ['no', 'null']))):
            
            globals()[f"{var_name}Confirmation"] += 1
            globals()['confirmationTimeout'] = int(fpsRealMean / 3) + confirm_value
            var_confirmation += 1

            if ((var_confirmation >= 1 + confirm_value and eyesOpen == 10) or 
                (var_confirmation >= int(fpsRealMean / 7) + confirm_value and eyesOpen == 5) or 
                (var_confirmation >= int(fpsRealMean / 4) + confirm_value and eyesOpen == 3)) and not globals()['clicked']:
                
                if action_start != 'wait':
                    make_action(action_start)
                
                globals()['clicked'] = True
                globals()[f"{var_name}Clicked"] = True

    if globals()[f"{var_name}Clicked"]:
        if var_mean > var_old * distance_value and distance > var_old * distance_value:
            globals()[f"{var_name}Confirmation"] = 1
            globals()[f"{var_name}Clicked"] = False
            globals()['clicked'] = False
            make_action(action_end)

    if eyesOpen == 0:
        globals()[f"{var_name}Confirmation"] = 1

######################
# Facemesh parameters
######################
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(0, 255, 0))

# Move mouse to the center of the screen
mouse.position = (screen_width / 2, screen_height / 2)

##########################
# Initialize facemesh for detecting facial points
##########################
with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    refine_landmarks=True,
    max_num_faces=1,
    min_detection_confidence=0.2,
    min_tracking_confidence=0.2,
) as face_mesh:
    for idx, (frame, frame_rgb) in enumerate(source):

        ##############################
        # Auto adjust Brightness, Contrast, Gamma
        ##############################
        if args.autoBrightness:
            fpsBrightness += 1

            if fpsBrightness > fpsRealMean:
                results = face_mesh.process(frame_rgb)
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    eyes_roi_value = get_eyes_roi(frame_rgb, landmarks)

                    if eyes_roi_value is not None:
                        brightness = np.average(eyes_roi_value)
                        brightness_average = brightness  # Assuming single value

                        if brightness_average < 150:
                            gain = 1
                            source.gain(gain)
                        elif brightness_average > 200:
                            gain = 0
                            source.gain(gain)
                        fpsBrightness = 0
                else:
                    # No face detected; continue processing and trying to detect a face
                    print("No face detected, trying again...")
            
        frameTime = time.time()
        fpsReal = int(1 / (frameTime - oldframeTime))
        fpsRealMean = (fpsReal + (fpsRealMean * 10)) / 11
        oldframeTime = frameTime

        ############################
        # Process Facemesh results
        ############################
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:

            ############################
            # Create landmarks
            ############################
            face_landmarks = results.multi_face_landmarks[0]
            
            if frameNumber > 1:
                landmarks = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])
            if frameNumber < fpsRealMean:
                frameNumber += 1
            else:
                if waitFrames > 0:
                    waitFrames -= 1
                if confirmationTimeout > 0:
                    confirmationTimeout -= 1

                ##############################################
                # Mouse movement detection mode 1
                ##############################################
                if args.mouseDetectionMode == 1:
                    mouseMoveX = np.linalg.norm(landmarks[6][0] - landmarks[6][2]) * args.mouseSpeedX * 10
                    mouseMoveY = np.linalg.norm(landmarks[6][1] - landmarks[6][2]) * args.mouseSpeedY * 10

                    if zeroPointX2 is None:
                        zeroPointX = mouseMoveX
                        zeroPointY = mouseMoveY
                        zeroPointX2 = mouseMoveX
                        zeroPointY2 = mouseMoveY
                        mousePointXabs = 0
                        mousePointYabs = 0

                    mousePointX = mouseMoveX - zeroPointX2
                    mousePointY = mouseMoveY - zeroPointY2

                    mousePointXabsOld = mousePointXabs
                    mousePointYabsOld = mousePointYabs
                    mousePointXabs = abs(mousePointX)
                    mousePointYabs = abs(mousePointY)

                    if slowMove > 9:
                        slowMove -= 1

                    if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                        if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                            mousePointXApply = mousePointX * mousePointXabs / args.slowMouseMoveX
                            mousePointYApply = mousePointY * mousePointYabs / args.slowMouseMoveY
                            slowMove = 11
                        else:
                            mousePointXApply = mousePointX * mousePointXabs / args.slowMouseMoveX
                            mousePointYApply = mousePointY * mousePointYabs / args.slowMouseMoveY

                        if not stopCursor:
                            set_mouse_position(int(mousePointXApply), int(mousePointYApply))

                            mouse_position = get_mouse_position()
                            if mousePositionFrameX == mouse_position[0] and mousePointXabs > 1:
                                zeroPointX2 -= (zeroPointX2 - mouseMoveX) * 0.1

                            if mousePositionFrameY == mouse_position[1] and mousePointYabs > 1:
                                zeroPointY2 -= (zeroPointY2 - mouseMoveY) * 0.1

                            mousePositionFrameX, mousePositionFrameY = mouse_position

                ##############################################
                # Mouse movement detection mode 2
                ##############################################
                elif args.mouseDetectionMode == 2:
                    mouseMoveX = - ((landmarks[6][0] + landmarks[352][0] + 2) - (landmarks[6][0] + landmarks[123][0] + 2)) * args.mouseSpeedX * 5
                    mouseMoveY = - ((landmarks[6][1] + landmarks[352][1] + 2) - (landmarks[6][1] + landmarks[123][1] + 2)) * args.mouseSpeedY * 5

                    if zeroPointX2 is None:
                        zeroPointX = mouseMoveX
                        zeroPointY = mouseMoveY
                        zeroPointX2 = mouseMoveX
                        zeroPointY2 = mouseMoveY

                    if args.startIsNeutral:
                        mousePointX = mouseMoveX - zeroPointX2
                        mousePointY = mouseMoveY - zeroPointY2
                    else:
                        mousePointX = mouseMoveX
                        mousePointY = mouseMoveY

                    mousePointXabs = abs(mousePointX)
                    mousePointYabs = abs(mousePointY)

                    if slowMove > 9:
                        slowMove -= 1

                    if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                        if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                            mousePointXApply = mousePointX * mousePointXabs / args.slowMouseMoveX
                            mousePointYApply = mousePointY * mousePointYabs / args.slowMouseMoveY
                            slowMove = 11
                        else:
                            mousePointXApply = mousePointX * mousePointXabs / args.slowMouseMoveX
                            mousePointYApply = mousePointY * mousePointYabs / args.slowMouseMoveY

                        if not stopCursor:
                            mouse_position = get_mouse_position()
                            if mousePositionFrameX == mouse_position[0] and abs(mousePointXApply) > args.minimalMouseMoveX:
                                maybeScreenLimitX += 1
                            else:
                                maybeScreenLimitX = 0
                            
                            if maybeScreenLimitX >= 3:
                                mousePointXApply = 0
                                mousePointXabs = 0

                            if mousePositionFrameY == mouse_position[1] and abs(mousePointYApply) > args.minimalMouseMoveY:
                                maybeScreenLimitY += 1
                            else:
                                maybeScreenLimitY = 0
                            
                            if maybeScreenLimitY >= 3:
                                mousePointYApply = 0
                                mousePointYabs = 0

                            mousePositionFrameX, mousePositionFrameY = mouse_position
                            set_mouse_position(int(mousePointXApply), int(mousePointYApply))

                ##############################################
                # Mouse movement detection mode 3
                ##############################################
                elif args.mouseDetectionMode == 3:
                    mouseMoveX = ((math.atan((landmarks[1][0] + ((landmarks[454][0] + landmarks[473][0] + landmarks[152][0]) / 3)) + 
                                             (landmarks[1][0] + ((landmarks[234][0] + landmarks[468][0] + landmarks[10][0]) / 3))) * 
                                  180 / math.pi * 2.2) * 100) - 12000

                    mouseMoveY = ((math.atan((landmarks[1][1] - ((landmarks[152][1] + landmarks[473][1] + landmarks[34][1]) / 3)) + 
                                             (landmarks[1][1] + ((landmarks[10][1] + landmarks[468][1] + landmarks[264][1]) / 3))) * 
                                  180 / math.pi * 2.2) * 100) - 10000

                    if zeroPointX2 is None:
                        zeroPointX = mouseMoveX
                        zeroPointY = mouseMoveY
                        zeroPointX2 = mouseMoveX
                        zeroPointY2 = mouseMoveY

                    mousePointX = (mouseMoveX + mousePositionFrameX * 6) / 7
                    mousePointY = (mouseMoveY + mousePositionFrameY * 6) / 7

                    mousePointXabs = abs(mousePointX)
                    mousePointYabs = abs(mousePointY)

                    if slowMove > 9:
                        slowMove -= 1

                    if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                        if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                            mousePointXApply = mousePointX
                            mousePointYApply = mousePointY
                        else:
                            mousePointXApply = mousePointX
                            mousePointYApply = mousePointY

                        if not stopCursor:
                            mouse_position = get_mouse_position()
                            mousePositionFrameX, mousePositionFrameY = mouse_position
                            mouse.position = (mousePointXApply, mousePointYApply)

                ##############################################
                # Mouse movement detection mode 4
                ##############################################
                elif args.mouseDetectionMode == 4:
                    mouseMoveX = (math.atan((landmarks[1][0] + ((landmarks[454][0] + landmarks[473][0] + landmarks[152][0]) / 3))) * 3)
                    mouseMoveX = mouseMoveX ** 4 * 4

                    mouseMoveY = (math.atan((landmarks[1][1] + ((landmarks[152][1] + landmarks[473][1] + landmarks[34][1]) / 3))) * 3)
                    mouseMoveY = mouseMoveY ** 4 * 4

                    if zeroPointX2 is None:
                        zeroPointX = mouseMoveX
                        zeroPointY = mouseMoveY
                        zeroPointX2 = mouseMoveX
                        zeroPointY2 = mouseMoveY
                        mousePointXabs = 0
                        mousePointYabs = 0

                    mousePointX = mouseMoveX - zeroPointX2
                    mousePointY = mouseMoveY - zeroPointY2

                    mousePointXabsOld = mousePointXabs
                    mousePointYabsOld = mousePointYabs
                    mousePointXabs = abs(mousePointX)
                    mousePointYabs = abs(mousePointY)

                    if slowMove > 9:
                        slowMove -= 1

                    if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                        if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                            mousePointXApply = mousePointX * mousePointXabs / args.slowMouseMoveX
                            mousePointYApply = mousePointY * mousePointYabs / args.slowMouseMoveY
                            slowMove = 11
                        else:
                            mousePointXApply = mousePointX * mousePointXabs / args.slowMouseMoveX
                            mousePointYApply = mousePointY * mousePointYabs / args.slowMouseMoveY

                        if not stopCursor:
                            set_mouse_position(int(mousePointXApply), int(mousePointYApply))

                            mouse_position = get_mouse_position()
                            if mousePositionFrameX == mouse_position[0] and mousePointXabs > 1:
                                zeroPointX2 -= (zeroPointX2 - mouseMoveX) * 0.1

                            if mousePositionFrameY == mouse_position[1] and mousePointYabs > 1:
                                zeroPointY2 -= (zeroPointY2 - mouseMoveY) * 0.1

                            mousePositionFrameX, mousePositionFrameY = mouse_position

                ##############################################
                # Check if using the right eye
                ##############################################
                if args.enableRightEye:
                    calculate_distance2D('overRightEye', [258, 257, 259], [254, 253, 252])
                    calculate_distance2D('rightEye', [385, 386, 387], [373, 374, 380])

                if args.enableLeftEye:
                    calculate_distance2D('overLeftEye', [28, 27, 29], [22, 23, 24])
                    calculate_distance2D('leftEye', [158, 159, 160], [153, 145, 144])

                if args.enableKiss:
                    calculate_distance2D('irisDistance', [469], [476])
                    calculate_distance2D('kiss', [178, 80, 41], [318, 415, 272])

                # Check eye conditions to set eyesOpen state
                if ((leftEye < leftEyeMean * 0.68 and rightEye < rightEyeMean * 0.68) or 
                    (leftEye < leftEyeNormalized * 0.4 and rightEye < rightEyeNormalized * 0.4)) and not clicked:
                    eyesOpen = 0
                    waitFrames = int(fpsRealMean)
                else:
                    if eyesOpen == 0:
                        eyesOpen = 3

                if eyesOpen > 0 and leftEye > leftEyeNormalized * 0.8 and rightEye > rightEyeNormalized * 0.8 and not clicked:
                    if (leftEye > leftEyeOld * 0.85 and rightEye > rightEyeOld * 0.85 and 
                        mousePointXabs <= 1 and mousePointYabs <= 1 and 
                        mousePointXabsOld <= 1 and mousePointYabsOld <= 1):
                        eyesOpen = 10
                    else:
                        eyesOpen = 5

                    if ((leftEye < leftEyeNormalized * 0.7 and rightEye < rightEyeNormalized * 0.7 and not clicked) or 
                        (mousePointYabsOld > mousePointYabs and not clicked) or 
                        (mousePointXabsOld > mousePointXabs and not clicked)):
                        eyesOpen = 3

                if args.enableRightEye:
                    # verify_false_click('rightEye', 0.7, 0, 'showOptions1', 'releaseOptions1')
                    verify_false_click('rightEye', 0.7, 0, 'pressRight', 'releaseRight')

                if args.enableLeftEye:
                    verify_false_click('leftEye', 0.7, 0, 'pressLeft', 'releaseLeft')

                if args.enableKiss:
                    verify_false_click('kiss', 0.7, 1, 'scrollV', 'wait')

                if action == 'scrollV' and mousePointYabs > args.minimalMouseMoveY:
                    globals()['stopCursor'] = True
                    print(f"mousepoint {mousePointYabs}")
                    print(f"args.minimalMouseMoveY {args.minimalMouseMoveY}")

                    scrollValueX = mousePointYApply / fpsRealMean
                    if 0 < scrollValueX < 1:
                        scrollValueX = 1
                    elif -1 < scrollValueX < 0:
                        scrollValueX = -1
                    mouse.scroll(0, -scrollValueX)
                    globals()['slowMove'] = 10 + (fpsRealMean / 10)
                elif action == 'showOptions1':
                    mouse_position = get_mouse_position()
                    if mousePointXApply < -args.minimalMouseMoveX * 3:
                        asyncio.run(tkTooltipChange('Double Click', "#000000", "#ff00ff", mouse_position[0], mouse_position[1]))
                    elif mousePointXApply > args.minimalMouseMoveX * 3:
                        asyncio.run(tkTooltipChange('Hold', "#000000", "#afaaaf", mouse_position[0], mouse_position[1]))
                    elif mousePointYApply > args.minimalMouseMoveY * 2:
                        asyncio.run(tkTooltipChange('Middle Button', "#000000", "#4440ff", mouse_position[0], mouse_position[1]))
                    elif mousePointYApply < -args.minimalMouseMoveY * 2:
                        asyncio.run(tkTooltipChange('Show Keyboard', "#000000", "#626634", mouse_position[0], mouse_position[1]))
                    elif action == 'pressLeft':
                        asyncio.run(tkTooltipChange('', "#000000", "#008eff", mouse_position[0], mouse_position[1]))

                ##############################
                # Display information on screen
                ##############################
                if args.view != 0:
                    ##############################
                    # Exibir informações na tela
                    # Print info on screen
                    ##############################
                    if args.view == 2:
                        avatar = np.zeros(
                            shape=[args.webcamy, args.webcamx, 3], dtype=np.uint8)
                        showInCv = avatar
                    else:
                        showInCv = frame

                    cv2.rectangle(showInCv, (0, 0), (300, 300), (0, 0, 0), -1)

                    # Exibir texto com informações na tela
                    # Display text with information on the screen
                    cv2.putText(showInCv, f"FPS {int(fpsReal)}", (20, 40),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

                    cv2.putText(showInCv, f"Left Eye  {int(leftEye)}", (20, 80),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

                    cv2.putText(showInCv, f"Right Eye {int(rightEye)}", (20, 120),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

                    cv2.putText(showInCv, f"Horizontal {int(mousePointX)}", (20, 160),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

                    cv2.putText(showInCv, f"Vertical {int(mousePointY)}", (20, 200),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

                    if args.view > 0:
                        # Linha horizontal central
                        # Center horizontal line
                        cv2.line(showInCv, (0, (int(args.webcamy / 2))), (args.webcamx, (int(args.webcamy / 2))), (255, 255, 255), 1)
                        cv2.line(showInCv, (0, (int(args.webcamy / 2) + 1)), (args.webcamx, (int(args.webcamy / 2) + 1)), (0, 0, 0), 1)

                        # Linha vertical central
                        # Center vertical line
                        cv2.line(showInCv, ((int(args.webcamx / 2), 0)), ((int(args.webcamx / 2), args.webcamx)), (255, 255, 255), 1)
                        cv2.line(showInCv, ((int(args.webcamx / 2) + 1, 0)), ((int(args.webcamx / 2) + 1, args.webcamx)), (0, 0, 0), 1)

                    ##############################
                    # Mostrar pontos no avatar
                    # Show points on avatar
                    ##############################
                    if args.view == 2:
                        # Left Eye Upper0 / Right Eye Lower0
                        # Olho esquerdo parte superior0 / Olho direito parte inferior0
                        for id in [246, 161, 160, 159, 158, 157, 173, 33, 7, 163, 144, 145, 153, 154, 155, 133, 263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (155, 155, 155), 1)

                        # Left Eye Top
                        # Olho esquerdo parte superior
                        for id in [158, 159, 160]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Left Eye Bottom
                        # Olho esquerdo parte inferior
                        for id in [144, 145, 163]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                        # Right Eye Top
                        # Olho direito parte superior
                        for id in [385, 386, 387]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Right Eye Bottom
                        # Olho direito parte inferior
                        for id in [373, 374, 380]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                        # Nose and iris
                        # Nariz e íris
                        for id in [1, 468, 473]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (55, 255, 55), 1)

                        # Face Oval
                        # Oval do rosto
                        for id in [10, 338, 338, 297, 297, 332, 332, 284, 284, 251, 251, 389, 389, 356, 356, 454, 454, 323, 323, 361, 361, 288, 288, 397, 397, 365, 365, 379, 379, 378, 378, 400, 400, 377, 377, 152, 152, 148, 148, 176, 176, 149, 149, 150, 150, 136, 136, 172, 172, 58, 58, 132, 132, 93, 93, 234, 234, 127, 127, 162, 162, 21, 21, 54, 54, 103, 103, 67, 67, 109, 109, 10]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (0, 255, 0), 1)

                        # Lips Top Inner
                        for id in [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Lips Bottom Inner
                        # Desenha círculos para os pontos de referência internos do lábio inferior
                        for id in [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (0, 255, 255), 1)


                        # Lips Top Outer
                        # Desenha círculos para os pontos de referência externos do lábio superior
                        for id in [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Lips Bottom Outer
                        # Desenha círculos para os pontos de referência externos do lábio inferior
                        for id in [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]:
                            cv2.circle(showInCv, (int(landmarks[id][0] * args.webcamx), int(landmarks[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                    ##############################
                    # Show webcam
                    ##############################
                    # Mostra a imagem da câmera com os pontos de referência do rosto
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh_connections.FACEMESH_IRISES,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec,
                    )
                    source.show(showInCv, args.webcamx, args.webcamy)

                    ##############################
                    # Plot graphic
                    ##############################
                    if args.plot == 1:  # Check if the user wants to plot the left eye
                        if countFrames == 10:
                            import matplotlib.pyplot as plt  # para traçar gráficos / to plot graphics
                            from collections import deque  # para traçar gráficos / to plot graphics
                            pts_plot = deque(maxlen=64)
                            pts_plot.append(leftEye)  # Append the blink value to the list of points to be plotted
                            min_value = -0.003
                            max_value = 0.015
                        if countFrames > 70:  # Wait some frames before plotting to avoid initial spikes
                            line1 = plotting_ear(pts_plot, line1, min_value, max_value)  # Call function to plot the graph
                        countFrames += 1

                    elif args.plot == 2:  # Check if the user wants to plot the right eye
                        if countFrames == 10:
                            import matplotlib.pyplot as plt  # para traçar gráficos / to plot graphics
                            from collections import deque  # para traçar gráficos / to plot graphics
                            pts_plot.append(rightEyeBlink)  # Append the blink value to the list of points to be plotted
                            min_value = -0.003
                            max_value = 0.015
                            pts_plot = deque(maxlen=64)
                        if countFrames > 70:  # Wait some frames before plotting to avoid initial spikes
                            line1 = plotting_ear(pts_plot, line1, min_value, max_value)  # Call function to plot the graph
                        countFrames += 1
