import mediapipe as mp  # para capturar informações do rosto / to capture info about face
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
import numpy as np  # para realizar cálculos / to make calculations
import argparse  # para ler parâmetros do comando do terminal / to read parameters from terminal command
import matplotlib.pyplot as plt  # para traçar gráficos / to plot graphics
from collections import deque  # para traçar gráficos / to plot graphics
from videosource import WebcamSource  # importar arquivo para usar imagem da webcam / import file to use webcam image
import config # Import the configuration file config.py
import sys # Import the sys module to be able to read the first argument passed to the script
from pynput.mouse import Button, Controller  # para usar o mouse / to use mouse
import tkinter as tk  # para exibir dicas de ferramentas / to show tooltip
import time # Importa o módulo time para manipular a variavel tempo / Import the time module to manipulate the time variable
import cv2 # Importa o módulo OpenCV para manipular a imagem / Import the OpenCV module to manipulate the image
import math


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
    'avatar': {
        'type': int,
        'help': 'Show avatar image',
        'default': 0
    },
    'mouseDetectionMode': {
        'type': int,
        'help': 'Mouse detection mode 1 or 2 or 3',
        'default': 2
    },
    'startIsNeutral': {
        'type': bool,
        'help': 'Start position is neutral position True or False',
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
        'type': str,
        'help': 'Plot the face landmarks',
        'default': 'None'
    },
    'blinkToClick': {
        'type': int,
        'help': 'Blink to click',
        'default': 1
    },
    'leftEyeBlinkFunction': {
        'type': str,
        'help': 'Function to call on left eye blink',
        'default': 'leftClick'
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
        'default': 6
    },
    'slowMouseMoveX': {
        'type': int,
        'help': 'Slow mouse move X',
        'default': 6
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
        'type': int,
        'help': 'Automatically adjust brightness',
        'default': 1
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
    parser.add_argument(f'--{arg_name}', type=arg_details['type'], help=arg_details['help'], default=arg_details['default'])

# Analisar argumentos fornecidos
# Parse provided arguments
args = parser.parse_args()

# Armazenar argumentos fornecidos em uma lista
# Store provided arguments in a list
provided_args = []
for arg in vars(args):
    if f"--{arg}" in sys.argv:
        provided_args.append(arg)

# Função para atualizar argumentos com base em argumentos fornecidos e configurações
# Function to update arguments based on provided arguments and settings
def update_arg(args, arg_name, default_value, provided_args):
    conf_value = config.read_config(arg_name, section_name='General', default_value=None)

    if arg_name not in provided_args:
        if conf_value is not None:
            setattr(args, arg_name, conf_value)
    else:
        config.write_config(arg_name, str(getattr(args, arg_name)))

    arg_value = getattr(args, arg_name)

    if isinstance(default_value, int):
        arg_value = int(arg_value)
    elif isinstance(default_value, float):
        arg_value = float(arg_value)
    elif isinstance(default_value, bool):
        arg_value = bool(arg_value)

    setattr(args, arg_name, arg_value)

# Atualizar argumentos usando a função update_arg
# Update arguments using the update_arg function
for arg_name, arg_details in arg_info.items():
    update_arg(args, arg_name, arg_details['default'], provided_args)



#####################
# Início do código da dica de ferramenta / Tooltip code start
#####################
tkTooltip = tk.Tk()

# Exibir texto no centro da tela / Display text in the center of the screen
def tkTooltipChangeCenter(text, color, bg):
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
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor)
    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()



# Exibir texto usando tk / Show text using tk
def tkTooltipChange(text, color, bg, mouseX, mouseY):
    # Configurar variáveis para a dica de ferramenta
    # Set up variables for the tooltip
    tooltipText = text
    tooltipTextColor = color
    tooltipBgColor = bg
    tooltipFontSize = 20
    tooltipWidth = len(text) * tooltipFontSize
    tooltipHeight = tooltipFontSize + 14

    # Desabilitar a borda da janela / Disable window border
    tkTooltip.wm_overrideredirect(True)

    # Definir posição e tamanho da dica de ferramenta
    # Set tooltip position and size
    if mouse.position[0] > 300:
        mouseX = mouseX - tooltipWidth - 60

    if mouse.position[1] > 180:
        mouseY = mouseY - tooltipHeight - 60

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
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor)
    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()


# Função para exibir apenas um quadrado colorido como dica de ferramenta
# Function to only show a colored square as tooltip
def tkTooltipOnlyColor(color, bg, mouseX, mouseY, tooltipWidth, tooltipHeight):

    # Desabilitar a borda da janela / Disable window border
    tkTooltip.wm_overrideredirect(True)

    # Definir posição e tamanho da dica de ferramenta
    # Set tooltip position and size
    if mouse.position[0] > 300:
        mouseX = mouseX - tooltipWidth - 60

    if mouse.position[1] > 180:
        mouseY = mouseY - tooltipHeight - 60

    tkTooltip.geometry(
        f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}".format(
            tkTooltip.winfo_screenwidth(), tkTooltip.winfo_screenheight()
        )
    )

    # Configurar a cor de fundo do canvas como transparente
    # Configure canvas background color as transparent
    canvas = tk.Canvas(tkTooltip, width=tooltipWidth, height=tooltipHeight, borderwidth=2, bg=bg, highlightbackground=color, highlightthickness=2)
    canvas.pack()

    # Configurar a cor de fundo da dica de ferramenta
    # Configure tooltip background color
    tkTooltip.configure(background=bg)

    # Atualizar dica de ferramenta / Update tooltip
    tkTooltip.update()



#####################
# Função para calcular a distância entre pontos em eixos x e y - 2D
# Function to calculate the distance between points in axes x and y - 2D
#####################
def calculate_distance2D(top_indices, bottom_indices):
    top_pointsX = np.array([landmarks_mean[index][0] for index in top_indices])
    bottom_pointsX = np.array([landmarks_mean[index][0] for index in bottom_indices])
    top_pointsY = np.array([landmarks_mean[index][1] for index in top_indices])
    bottom_pointsY = np.array([landmarks_mean[index][1] for index in bottom_indices])
    distance_x = np.sum(np.abs(np.sum(bottom_pointsX + 2) - np.sum(top_pointsX + 2)))
    distance_y = np.sum(np.abs(np.sum(bottom_pointsY + 2) - np.sum(top_pointsY + 2)))
    distance = np.sum(distance_x + distance_y)

    return distance * 500


#####################
# Função para calcular a distância entre pontos em eixos x, y e z - 3D
# Function to calculate the distance between points in axes x, y, and z - 3D
#####################
def calculate_distance3D(top_indices, bottom_indices):
    top_points = [landmarks_mean[index] for index in top_indices]
    bottom_points = [landmarks_mean[index] for index in bottom_indices]
    top_mean = np.sum(top_points)
    bottom_mean = np.sum(bottom_points)
    distance = np.linalg.norm((bottom_mean + 2) - (top_mean + 2))

    return distance * 500

#####################
# Função para obter a região dos olhos para detectar brilho
# Function to get the eyes region to detect brightness
#####################
def get_eyes_roi(frame, landmarks):
    height, width, _ = frame.shape
    eye_indices = [224, 444, 347, 229]
    # right_eye_indices = [362, 263, 466, 388]

    for index in eye_indices:
        pixelCordinates = _normalized_to_pixel_coordinates(landmarks[index].x, landmarks[index].y, width, height)
        if pixelCordinates != None:
            x, y = pixelCordinates
            eye_roy_array = []
            eye_roy_array.append((x, y))
            eye_roy_array = np.array(eye_roy_array)
            eye_roy_array_rect = cv2.boundingRect(eye_roy_array)
            eye_rois = frame[eye_roy_array_rect[1]:eye_roy_array_rect[1] + eye_roy_array_rect[3], eye_roy_array_rect[0]:eye_roy_array_rect[0] + eye_roy_array_rect[2]]
            return eye_rois



######################
# Parâmetros do Facemesh
# Facemesh parameters
######################
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(0, 255, 0))

mouse = Controller()  # Habilitar o controlador do mouse / Enable mouse controller

# Move o mouse para o centro da tela / Move mouse to the center of the screen
mouse.position = ((tkTooltip.winfo_screenwidth() / 2), (tkTooltip.winfo_screenheight() / 2))

######################
# Inicializar variáveis
# Init variables
######################
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
mouthCenterLeftOld = 0
mouthCenterRightOld = 0
confirmLeftClick = 1
confirmRightClick = 1
confirmLeftClickValue = 2
confirmRightClickValue = 2
tooltipWait = False
mouthCenterLeftOldLock = False
mouthCenterRightOldLock = False
leftClicked = False
rightClicked = False
mouseMode = 'left'
scrollMouse = False
standByClick = False
frameNumber = 0
mousetime = 0
mousePositionFrameX = 0
mousePositionFrameY = 0
maybeScreenLimitX = 0
maybeScreenLimitY = 0
clicktime = 0
clicktimewait = 0
mousePointXinBorder = False
mousePointYinBorder = False
zeroPointX = None
zeroPointY = None
zeroPointX2 = None
zeroPointY2 = None
mouseLeftClick = False
mouseRightClick = False
mouseLeftClickSensitivity = 0.8
mouseRightClickSensitivity = 0.8
disableClickInMovementValue = 5
mouseFast = False
leftEyeLine = []
rightEyeLine = []
line1 = []
line = []
pts_ear = deque(maxlen=64)
pts_plot = deque(maxlen=64)
pts_rightEye = deque(maxlen=64)
countFrames = 0
oldframeTime = 0
fpsRealMean = args.fps
source = WebcamSource(width=args.webcamx, height=args.webcamy, fps=args.fps, camera_id=args.webcamid)
gain = 400
fpsBrightness = 0
start_time = 0





######################################
# Iniciar o facemesh para detectar pontos faciais
# Start facemesh to detect face points
######################################
with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    refine_landmarks=True,
    max_num_faces=1,
    min_detection_confidence=0.2,
    min_tracking_confidence=0.2,
) as face_mesh:
    for idx, (frame, frame_rgb) in enumerate(source):
        
        ######################################
        # Auto ajuste de brilho, contraste e gama
        # Auto adjust Brightness, Contrast, Gamma
        ######################################
        if args.autoBrightness == 1:
            fpsBrightness += 1        
        frameTime = time.time()
        fpsReal = int(1 / (frameTime - oldframeTime))
        fpsRealMean = (fpsReal + (fpsRealMean * 10)) / 11
        oldframeTime = frameTime


        ############################
        # Trabalhar no resultado do Facemesh
        # Work on face mesh result
        ############################
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:

            ##############################################################
            # Auto ajuste de brilho, contraste, gama e ganho usando a região dos olhos
            # Auto adjust Brightness, Contrast, Gamma, and Gain using eye region
            ##############################################################
            if fpsBrightness > 5:
                # Process facemesh results
                results = face_mesh.process(frame_rgb)
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    eyes_roi_value = get_eyes_roi(frame_rgb, landmarks)

                    if eyes_roi_value is not None:
                        
                        brightness_values = []
                        brightness = np.average(eyes_roi_value)
                        brightness_values.append(brightness)
                        brightness_average = np.mean(brightness_values)

                        if brightness_average < 150:
                            gain = 1
                            source.gain(gain)
                        elif brightness_average > 200:
                            gain = 0
                            source.gain(gain)
                        else:
                            fpsBrightness = 0
                        


            ############################################
            # Criar landmarks e landmarks_mean
            # Nesta parte do código, são criados os pontos de referência (landmarks) e sua média (landmarks_mean).
            # Os pontos de referência são usados para calcular o movimento do mouse, sua velocidade e aceleração.
            # A média dos pontos de referência é usada para calcular o movimento do mouse.

            # Create landmarks and landmarks_mean
            # In this part of the code, the reference points (landmarks) and their mean (landmarks_mean) are created.
            # The reference points are used to calculate the mouse movement, its speed and acceleration.
            # The average of the reference points is used to calculate the mouse movement.
            ############################################
            if results.multi_face_landmarks is not None:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Aguarda o primeiro frame para começar a gerar a média dos pontos de referência
                # Wait for the first frame to start generating the average of the reference points
                if frameNumber > 1:
                    landmarks = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])
                    landmarks_mean = (landmarks + landmarks_mean) / 2
                if frameNumber < fpsRealMean:
                    frameNumber += 1
                    landmarks_mean = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])

                else:


                    ############################################
                    # Modo de detecção do movimento do mouse da primeira versão, que utiliza a distancia entre os eixos de forma que não ignora a posição vertical e horizontal na camera.
                    # Mouse movement detection mode of the first version, which uses the distance between the axes so that it does not ignore the vertical and horizontal position in the camera.
                    ############################################
                    if args.mouseDetectionMode == 1:

                        # Calcula a movimentação horizontal a partir do eixo x e z do ponto 6 (nariz)
                        # Calculate horizontal movement from point 6 (nose) x and z axis
                        mouseMoveX = np.linalg.norm(landmarks_mean[6][0] - landmarks_mean[6][2]) * args.mouseSpeedX * 10

                        # Calcula a movimentação vertical a partir do eixo y e z do ponto 6 (nariz)
                        # Calculate vertical movement from point 6 (nose) y and z axis
                        mouseMoveY = np.linalg.norm(landmarks_mean[6][1] - landmarks_mean[6][2]) * args.mouseSpeedY * 10

                        # Estabelece o ponto neutro do mouse, a posição da cabeça aonde o mouse fica parado
                        # Establish the neutral point of the mouse, the position of the head where the mouse is stopped
                        if zeroPointX2 == None:
                            zeroPointX = mouseMoveX
                            zeroPointY = mouseMoveY
                            zeroPointX2 = mouseMoveX
                            zeroPointY2 = mouseMoveY

                        # Subtrai a posição atual da posição neutra
                        # Subtract the current position from the neutral position
                        mousePointX = mouseMoveX - zeroPointX2
                        mousePointY = mouseMoveY - zeroPointY2

                        # Cria as variaveis com valores positivos dos movimentos, tornando valores negativos positivos
                        # Create variables with positive values of movements, making negative values positive
                        mousePointXabs = abs(mousePointX)
                        mousePointYabs = abs(mousePointY)

                        # Inicio de verificações para diminuir a velocidade do mouse
                        # Start of checks to reduce mouse speed
                        if slowMove > 9:
                            slowMove = slowMove - 1

                        # Aplica diversas regras de aceleração e desaceleração do mouse
                        # Applies various rules of mouse acceleration and deceleration
                        if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                            if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                mousePointXApply = mousePointX * mousePointXabs / (args.slowMouseMoveX)
                                mousePointYApply = mousePointY * mousePointYabs / (args.slowMouseMoveY)
                                slowMove = 11
                            else:
                                mousePointXApply = mousePointX * mousePointXabs / (args.slowMouseMoveX)
                                mousePointYApply = mousePointY * mousePointYabs / (args.slowMouseMoveY)

                            if not stopCursor:

                                # Executa o comando para realmente mover o mouse
                                # Execute the command to actually move the mouse
                                mouse.move(int(mousePointXApply), int(mousePointYApply))

                                # Alterar zeroPointX quando o mouse estiver no limite da tela
                                # Change zeroPointX when mouse on limit screen
                                if mousePositionFrameX == mouse.position[0] and mousePointXabs > 1:
                                    zeroPointX2 = zeroPointX2 - ((zeroPointX2 - mouseMoveX) * 0.1)

                                # Alterar zeroPointY quando o mouse estiver no limite da tela
                                # Change zeroPointY when mouse on limit screen
                                if mousePositionFrameY == mouse.position[1] and mousePointYabs > 1:
                                    zeroPointY2 = zeroPointY2 - ((zeroPointY2 - mouseMoveY) * 0.1)

                            # Le a posição do mouse na tela para ser usada na próxima iteração
                            # Read the mouse position on the screen to be used in the next iteration
                            mousePositionFrameX = mouse.position[0]
                            mousePositionFrameY = mouse.position[1]



                    ############################################
                    # Modo de detecção do movimento do mouse da segunda versão, que utiliza apenas o angulo da cabeça e consegue ignorar a posição vertical e horizontal na camera.
                    # Mouse movement detection mode of the second version, which uses only the angle of the head and can ignore the vertical and horizontal position in the camera.
                    ############################################
                    if args.mouseDetectionMode == 2:

                        # Calcula a movimentação horizontal a partir do eixo x e z do ponto 6 (nariz)
                        # Calculate horizontal movement from point 6 (nose) x and z axis
                        # mouseMoveX = math.atan((landmarks_mean[1][0] - landmarks_mean[454][0]) + (landmarks_mean[1][0] - landmarks_mean[234][0])) * 180 
 

                        # Calcula a movimentação vertical a partir do eixo y e z do ponto 6 (nariz)
                        # Calculate vertical movement from point 6 (nose) y and z axis
                        # mouseMoveY = math.atan((landmarks_mean[1][1] - landmarks_mean[152][1]) + (landmarks_mean[1][1] - landmarks_mean[10][1])) * 180

                        mouseMoveX = - ((landmarks_mean[6][0] + landmarks_mean[352][0] + 2) - (landmarks_mean[6][0] + landmarks_mean[123][0] + 2)  * args.mouseSpeedX * 10)

                        # Calcula a movimentação vertical a partir do eixo y e z do ponto 6 (nariz)
                        # Calculate vertical movement from point 6 (nose) y and z axis
                        # mouseMoveY = ((math.atan((landmarks_mean[1][1] - ((landmarks_mean[152][1] + landmarks_mean[473][1]) / 2)) + (landmarks_mean[1][1] - ((landmarks_mean[234][1] + landmarks_mean[468][1]) / 2))) * 300))
                        mouseMoveY = - ((landmarks_mean[6][1] + landmarks_mean[352][1] + 2) - (landmarks_mean[6][1] + landmarks_mean[123][1] + 2)  * args.mouseSpeedY * 7)



                        # Estabelece o ponto neutro do mouse, a posição da cabeça aonde o mouse fica parado
                        # Establish the neutral point of the mouse, the position of the head where the mouse is stopped
                        if zeroPointX2 == None:
                            zeroPointX = mouseMoveX
                            zeroPointY = mouseMoveY
                            zeroPointX2 = mouseMoveX
                            zeroPointY2 = mouseMoveY

                        # Subtrai a posição atual da posição neutra
                        # Subtract the current position from the neutral position
                        if args.startIsNeutral:
                            mousePointX = mouseMoveX - zeroPointX2
                            mousePointY = mouseMoveY - zeroPointY2
                        else:
                            mousePointX = mouseMoveX
                            mousePointY = mouseMoveY

                        # Cria as variaveis com valores positivos dos movimentos, tornando valores negativos positivos
                        # Create variables with positive values of movements, making negative values positive
                        mousePointXabs = abs(mousePointX)
                        mousePointYabs = abs(mousePointY)

                        # Inicio de verificações para diminuir a velocidade do mouse
                        # Start of checks to reduce mouse speed
                        if slowMove > 9:
                            slowMove = slowMove - 1

                        # Aplica diversas regras de aceleração e desaceleração do mouse
                        # Applies various rules of mouse acceleration and deceleration
                        if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                            if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                mousePointXApply = mousePointX * mousePointXabs / (args.slowMouseMoveX)
                                mousePointYApply = mousePointY * mousePointYabs / (args.slowMouseMoveY)
                                slowMove = 11
                            else:
                                mousePointXApply = mousePointX * mousePointXabs / (args.slowMouseMoveX)
                                mousePointYApply = mousePointY * mousePointYabs / (args.slowMouseMoveY)

                            if not stopCursor:

                                # Alterar zeroPointX quando o mouse estiver no limite da tela
                                # Change zeroPointX when mouse on limit screen
                                if mousePositionFrameX == mouse.position[0] and abs(mousePointXApply) > args.minimalMouseMoveX:
                                    maybeScreenLimitX += 1
                                else:
                                    maybeScreenLimitX = 0
                                
                                if maybeScreenLimitX >= 3:
                                    mousePointXApply = 0
                                    mousePointXabs = 0

                                if mousePositionFrameY == mouse.position[1] and abs(mousePointYApply) > args.minimalMouseMoveY:
                                    maybeScreenLimitY += 1
                                else:
                                    maybeScreenLimitY = 0
                                
                                if maybeScreenLimitY >= 3:
                                    mousePointYApply = 0
                                    mousePointYabs = 0

                                # print(mouse.position[0], mousePointXApply)

                                mousePositionFrameX = mouse.position[0]
                                mousePositionFrameY = mouse.position[1]

                                # print(mousePointXApply)
                                mouse.move(int(mousePointXApply), int(mousePointYApply))



                    ##############################
                    # Modo de detecção que utiliza o angulo para estabelecer a posição absoluta do mouse, como um rastreio que tenta advinhar para onde está olhando, funciona mal ainda
                    # Detection mode that uses the angle to establish the absolute position of the mouse, like a tracking that tries to guess where it is looking, works badly yet
                    ##############################
                    if args.mouseDetectionMode == 3:

                        # Calcula a movimentação horizontal a partir do eixo x e z do ponto 6 (nariz)
                        # Calculate horizontal movement from point 6 (nose) x and z axis
                        mouseMoveX = ((math.atan((landmarks_mean[1][0] + ((landmarks_mean[454][0] + landmarks_mean[473][0] + landmarks_mean[152][0]) / 3)) + (landmarks_mean[1][0] + ((landmarks_mean[234][0] + landmarks_mean[468][0] + landmarks_mean[10][0]) / 3))) * 180 / math.pi * 2.2) * 100) - 12000

                        # Calcula a movimentação vertical a partir do eixo y e z do ponto 6 (nariz)
                        # Calculate vertical movement from point 6 (nose) y and z axis
                        mouseMoveY = ((math.atan((landmarks_mean[1][1] - ((landmarks_mean[152][1] + landmarks_mean[473][1] + landmarks_mean[34][1]) / 3)) + (landmarks_mean[1][1] + ((landmarks_mean[10][1] + landmarks_mean[468][1] + landmarks_mean[264][1]) / 3))) * 180 / math.pi * 2.2) * 100) - 10000

                        # print(mouseMoveY)

                        # Estabelece o ponto neutro do mouse, a posição da cabeça aonde o mouse fica parado
                        # Establish the neutral point of the mouse, the position of the head where the mouse is stopped
                        if zeroPointX2 == None:
                            zeroPointX = mouseMoveX
                            zeroPointY = mouseMoveY
                            zeroPointX2 = mouseMoveX
                            zeroPointY2 = mouseMoveY

                        # Subtrai a posição atual da posição neutra
                        # Subtract the current position from the neutral position
                        mousePointX = (mouseMoveX + mousePositionFrameX * 6) / 7
                        mousePointY = (mouseMoveY + mousePositionFrameY * 6) / 7

                        # Cria as variaveis com valores positivos dos movimentos, tornando valores negativos positivos
                        # Create variables with positive values of movements, making negative values positive
                        mousePointXabs = abs(mousePointX)
                        mousePointYabs = abs(mousePointY)

                        # Inicio de verificações para diminuir a velocidade do mouse
                        # Start of checks to reduce mouse speed
                        if slowMove > 9:
                            slowMove = slowMove - 1

                        # Aplica diversas regras de aceleração e desaceleração do mouse
                        # Applies various rules of mouse acceleration and deceleration
                        if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                            if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                mousePointXApply = mousePointX
                                mousePointYApply = mousePointY
                            else:
                                mousePointXApply = mousePointX
                                mousePointYApply = mousePointY

                            if not stopCursor:

                                print(mousePointXApply)

                                mousePositionFrameX = mouse.position[0]
                                mousePositionFrameY = mouse.position[1]


                                # mouse.move(int(mousePointXApply), int(mousePointYApply))
                                mouse.position = (mousePointXApply, mousePointYApply)




                    ############################
                    # Início do piscar para clicar com o mouse
                    # Blink to mouse click start
                    ############################
                    if args.blinkToClick:


                        # Verifica se no frame anterior o clique do botão direito foi ativado para apresentar o tooltip na tela
                        # Check if the right button click was activated in the previous frame to present the tooltip on the screen
                        if scrollModeVertical:
                            tkTooltipOnlyColor("#000000", "#777777", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)

                        if scrollModeHorizontal:
                            tkTooltipOnlyColor("#000000", "#761ef8", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)


                        if rightClicked:

                            # Altera a cor da tooltip com base na direção do movimento do mouse
                            # Change tooltip color based on mouse movement direction
                            if changeRightMove and rightMoved == 'right':
                                tkTooltipChange('Rolagem vertical', "#000000", "#777777", mouse.position[0], mouse.position[1])
                                # tkTooltipOnlyColor("#000000", "#777777", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeRightMove = False

                            elif changeRightMove and rightMoved == 'left':
                                tkTooltipChange('Rolagem horizontal', "#000000", "#761ef8", mouse.position[0], mouse.position[1])
                                # tkTooltipOnlyColor("#000000", "#761ef8", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeRightMove = False

                            # Atualiza a direção do movimento do mouse e reinicia a tooltip
                            # Update mouse movement direction and reset tooltip
                            if mousePointX - zeroPointX > args.minimalMouseMoveX and rightMoved == 'no':
                                rightMoved = 'right'
                                leftMoved = 'null'
                                changeRightMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX - zeroPointX < - args.minimalMouseMoveX and rightMoved == 'no':
                                rightMoved = 'left'
                                leftMoved = 'null'
                                changeRightMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX - zeroPointX < - args.minimalMouseMoveX * 3 and rightMoved == 'right':
                                rightMoved = 'no'
                                changeRightMove = False
                                stopCursor = False
                                rightClicked = False
                                standByClick = False
                                tooltipWait = False
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX - zeroPointX > args.minimalMouseMoveX * 3 and rightMoved == 'left':
                                rightMoved = 'no'
                                changeRightMove = False
                                stopCursor = False
                                rightClicked = False
                                standByClick = False
                                tooltipWait = False
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()


                            # Caso o movimento do mouse ainda não tenha sido determinado
                            # If mouse movement direction is not determined yet
                            elif rightMoved == 'no':
                                tkTooltipOnlyColor("#000000", "#ff0000", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)



                        # Verifica se no frame anterior o clique do botão esquerdo foi ativado para apresentar o tooltip na tela
                        # Check if the left button click was activated in the previous frame to present the tooltip on the screen
                        if leftClickedConstant:
                            tkTooltipOnlyColor("#000000", "#00ff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)

                        if leftClicked:

                            # Altera a cor da tooltip com base na direção do movimento do mouse
                            # Change tooltip color based on mouse movement direction
                            if changeLeftMove and leftMoved == 'right':
                                tkTooltipChange('Duplo Clique', "#000000", "#fff000", mouse.position[0], mouse.position[1])
                                # tkTooltipOnlyColor("#000000", "#ffff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            elif changeLeftMove and leftMoved == 'left':
                                tkTooltipChange('Segurando', "#000000", "#00ff00", mouse.position[0], mouse.position[1])
                                # tkTooltipOnlyColor("#000000", "#00ff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            elif changeLeftMove and leftMoved == 'bottom':
                                tkTooltipChange('Clique do meio', "#000000", "#2266ff", mouse.position[0], mouse.position[1])
                                # tkTooltipOnlyColor("#000000", "#2266ff", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            elif changeLeftMove and leftMoved == 'top':
                                
                                tkTooltipChangeCenter('Olhe para o centro da tela e abra o olho\npara ajustar a posição neutra', "#000000", "#f8961e")
                                # tkTooltipOnlyColor("#000000", "#f8961e", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            # Atualiza a direção do movimento do mouse e reinicia a tooltip
                            # Update mouse movement direction and reset tooltip
                            if mousePointX - zeroPointX > args.slowMouseMoveX and leftMoved == 'no':
                                leftMoved = 'right'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX - zeroPointX < - args.slowMouseMoveX and leftMoved == 'no':
                                leftMoved = 'left'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointY - zeroPointY > args.slowMouseMoveY and leftMoved == 'no':
                                leftMoved = 'bottom'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointY - zeroPointY < - args.slowMouseMoveY and leftMoved == 'no':
                                leftMoved = 'top'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX - zeroPointX < - args.minimalMouseMoveX * 3 and leftMoved == 'right':
                                leftMoved = 'no'
                                changeRightMove = False
                                stopCursor = False
                                leftClicked = False
                                standByClick = False
                                tooltipWait = False
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX - zeroPointX > args.minimalMouseMoveX * 3 and leftMoved == 'left':
                                leftMoved = 'no'
                                changeRightMove = False
                                stopCursor = False
                                leftClicked = False
                                standByClick = False
                                tooltipWait = False
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointY - zeroPointY < - args.minimalMouseMoveY * 3 and leftMoved == 'bottom':
                                leftMoved = 'no'
                                changeRightMove = False
                                stopCursor = False
                                leftClicked = False
                                standByClick = False
                                tooltipWait = False
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointY - zeroPointY > args.minimalMouseMoveY * 3 and leftMoved == 'top':
                                leftMoved = 'no'
                                changeRightMove = False
                                stopCursor = False
                                leftClicked = False
                                standByClick = False
                                tooltipWait = False
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()


                        # Calcular usando informações 2D sobre os 3 pontos superiores e 3 pontos inferiores dos olhos, menos 4 pixels por cada verificação
                        # Calculate using 2D information about 3 top points and 3 bottom points of the eyes, less 4 pixels for any point
                        rightEyeBlink = calculate_distance2D([385, 386, 387], [373, 374, 380]) - 12
                        leftEyeBlink = calculate_distance2D([158, 159, 160], [163, 145, 144]) - 12

                        # Em espera de clique, pare para atualizar o valor normalizado
                        # In stand by click, stop to refresh normalized value
                        if not standByClick and not rightClicked:
                            rightEyeNormalized = np.mean([rightEyeBlink, rightEyeBlinkOld])
                            rightEyeBlinkOld = ((rightEyeBlinkOld * fpsRealMean) + rightEyeBlink) / (fpsRealMean + 1)

                        if not standByClick and not leftClicked:
                            leftEyeNormalized = np.mean([leftEyeBlink, leftEyeBlinkOld])
                            leftEyeBlinkOld = ((leftEyeBlinkOld * fpsRealMean) + leftEyeBlink) / (fpsRealMean + 1)

                        # Desativar clique se fechar ambos os olhos
                        # Disable click if close both eyes
                        if not (leftEyeBlink < leftEyeBlinkOld * 0.63 and rightEyeBlink < rightEyeBlinkOld * 0.63):

                            # Clique com o botão direito do mouse se o olho direito estiver fechado
                            # Right mouse click if right eye is closed
                            if rightEyeBlink < rightEyeBlinkOld * 0.6 and (not standByClick or confirmRightClick > 0) and not leftClicked and not rightClicked and ((mousePointXabs < args.slowMouseMoveX * 2 and mousePointYabs < args.slowMouseMoveY * 2) or (leftMoved != 'no' and leftMoved != 'null') or (rightMoved != 'no' and rightMoved != 'null')):
                                confirmRightClick += 1

                                # Confirmar clique com o botão direito
                                # Confirm right click
                                if confirmRightClick >= fpsRealMean / 6 + confirmRightClickValue:
                                    stopCursor = True
                                    tooltipWait = False
                                    rightClicked = True
                                    scrollModeVertical = False
                                    scrollModeHorizontal = False
                                    leftClickedConstant = False
                                    zeroPointX = mousePointX
                                    zeroPointY = mousePointY
                                    if rightMoved != 'no':
                                        rightMoved = 'clean'
                                    leftMoved = 'no'
                                    confirmRightClick = 1
                                    confirmLeftClick = 1

                            else:
                                # Liberar o clique com o botão direito e processar a ação
                                # Release right click and process action
                                confirmRightClick = 1
                                if rightEyeBlink > rightEyeNormalized and rightClicked:

                                    # Ações com base na direção do movimento do mouse
                                    # Actions based on mouse movement direction
                                    if rightMoved == 'no':
                                        mouse.press(Button.right)
                                        mouse.release(Button.right)
                                        stopCursor = False
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                    elif rightMoved == 'right':
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                        scrollModeVertical = True
                                    elif rightMoved == 'left':
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                        scrollModeHorizontal = True
                                    elif rightMoved == 'clean':
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                        stopCursor = False
                                        rightMoved = 'no'
                                    rightClicked = False

                                    standByClick = False
                                    tooltipWait = False

                            # Clique com o botão esquerdo do mouse se o olho esquerdo estiver fechado
                            # Left mouse click if left eye is closed
                            if leftEyeBlink < leftEyeBlinkOld * 0.6 and (not standByClick or confirmLeftClick > 0) and not leftClicked and not rightClicked and ((mousePointXabs < args.slowMouseMoveX * 2 and mousePointYabs < args.slowMouseMoveY * 2) or (rightMoved != 'no' and rightMoved != 'null') or (leftMoved != 'no' and leftMoved != 'null')):
                                confirmLeftClick += 1

                                # Confirmar clique com o botão esquerdo
                                # Confirm left click
                                if confirmLeftClick >= fpsRealMean / 6 + confirmLeftClickValue:
                                    stopCursor = True
                                    tooltipWait = False
                                    leftClicked = True
                                    scrollModeVertical = False
                                    scrollModeHorizontal = False
                                    leftClickedConstant = False
                                    zeroPointX = mousePointX
                                    zeroPointY = mousePointY
                                    rightMoved = 'no'
                                    leftMoved = 'no'
                                    tkTooltipOnlyColor("#000000", "#00b21f", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                    confirmRightClick = 1
                                    confirmLeftClick = 1

                            else:
                                confirmLeftClick = 1
                                if not leftClicked and not rightClicked:
                                    standByClick = False


                                # Liberar o clique com o botão esquerdo e processar a ação
                                # Release left click and process action
                                elif leftEyeBlink > leftEyeNormalized and leftClicked:

                                    # Ações com base na direção do movimento do mouse
                                    # Actions based on mouse movement direction
                                    if leftMoved == 'no':
                                        mouse.press(Button.left)
                                        mouse.release(Button.left)
                                        stopCursor = False
                                    elif leftMoved == 'right':
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                        mouse.press(Button.left)
                                        mouse.release(Button.left)
                                        mouse.press(Button.left)
                                        mouse.release(Button.left)
                                        stopCursor = False
                                        leftMoved = 'no'
                                    elif leftMoved == 'bottom':
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                        mouse.press(Button.middle)
                                        mouse.release(Button.middle)
                                        stopCursor = False
                                        leftMoved = 'no'
                                    elif leftMoved == 'null':
                                        leftMoved = 'no'
                                        stopCursor = False
                                    elif leftMoved == 'left':
                                        mouse.press(Button.left)
                                        stopCursor = False
                                        leftClickedConstant = True
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                    elif leftMoved == 'top':
                                        # mouse.press(Button.left)
                                        stopCursor = False
                                        leftClickedConstant = False
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                        zeroPointX2 = mouseMoveX
                                        zeroPointY2 = mouseMoveY
                                        mouse.position = ((tkTooltip.winfo_screenwidth() / 2), (tkTooltip.winfo_screenheight() / 2))

                                    leftClicked = False
                                    standByClick = False
                                    tooltipWait = False
                                    tkTooltip.destroy()
                                    tkTooltip = tk.Tk()

                            # Movimento do cursor suave quando os olhos estiverem parcialmente fechados
                            # Smooth cursor movement when eyes are partially closed
                            if args.mouseDetectionMode == 3:
                                if ((leftEyeBlink < leftEyeNormalized * 0.8) or (rightEyeBlink < rightEyeNormalized * 0.8)) and (mousePointXabs < 3 or mousePointYabs < 3) and not leftClicked and not rightClicked:
                                    if zeroPointX > mousePointX: zeroPointX = zeroPointX - ((zeroPointX - mouseMoveX) * 0.1)
                                    else:
                                        zeroPointX = zeroPointX - ((mouseMoveX - zeroPointX) * 0.1)

                                    if zeroPointY > mousePointY:
                                        zeroPointY = zeroPointY - ((zeroPointY - mouseMoveY) * 0.1)
                                    else:
                                        zeroPointY = zeroPointY - ((mouseMoveY - zeroPointY) * 0.1)

                            ####################
                            # Modo de rolagem vertical
                            # Scroll mode Vertical
                            ####################
                            if scrollModeVertical and mousePointYabs > args.minimalMouseMoveY and slowMove < 10:
                                scrollValueX = mousePointYApply / (fpsRealMean / 2)
                                if scrollValueX < 1 and scrollValueX > 0:
                                    scrollValueX = 1
                                elif scrollValueX > -1 and scrollValueX < 0:
                                    scrollValueX = -1
                                mouse.scroll(0, - scrollValueX)
                                slowMove = 10 + (fpsRealMean / 10)
                                # print(mousePointYApply)

                            ####################
                            # Modo de rolagem horizontal
                            # Scroll mode Horizontal
                            ####################
                            if scrollModeHorizontal and mousePointXabs > args.minimalMouseMoveX and slowMove < 10:
                                scrollValueY = mousePointXApply / (fpsRealMean / 2)
                                if scrollValueY < 1 and scrollValueY > 0:
                                    scrollValueY = 1
                                elif scrollValueY > -1 and scrollValueY < 0:
                                    scrollValueY = -1
                                mouse.scroll(scrollValueY, 0)
                                slowMove = 10 + (fpsRealMean / 10)
                                # print(mousePointYApply)

                            # ####################
                            # # Rolagem com a boca
                            # # Scroll with mouth
                            # ####################
                            # if args.mouthScroll == 1:
                            #     mouthCenterLeft = np.linalg.norm(landmarks_mean[214] - landmarks_mean[87]) * 1000
                            #     if not mouthCenterLeftOldLock and not mouthCenterRightOldLock:
                            #         if mouthCenterLeftOld == 0:
                            #             mouthCenterLeftOld = mouthCenterLeft
                            #         else:
                            #             mouthCenterLeftOld = ((mouthCenterLeftOld * fpsRealMean) + mouthCenterLeft) / (fpsRealMean + 1)

                            #     # Detectar abertura da boca e rolar a tela
                            #     # Detect mouth opening and scroll the screen
                            #     if mouthCenterLeft * 1.1 < mouthCenterLeftOld and not standByClick and (mousePointXabs < 2 or mousePointYabs < 2):
                            #         mouthCenterLeftOldLock = True
                            #         mouse.scroll(0, ((mouthCenterLeftOld - mouthCenterLeft) / 3))

                            #     else:
                            #         mouthCenterLeftOldLock = False

                            #     mouthCenterRight = np.linalg.norm(landmarks_mean[434] - landmarks_mean[317]) * 1000
                            #     if not mouthCenterRightOldLock and not mouthCenterLeftOldLock:
                            #         if mouthCenterRightOld == 0:
                            #             mouthCenterRightOld = mouthCenterRight
                            #         else:
                            #             mouthCenterRightOld = ((mouthCenterRightOld * fpsRealMean) + mouthCenterRight) / (fpsRealMean + 1)

                            #     if mouthCenterRight * 1.05 < mouthCenterRightOld and not standByClick and (mousePointXabs < 2 or mousePointYabs < 2):
                            #         mouthCenterRightOldLock = True
                            #         mouse.scroll(0, ((mouthCenterRight - mouthCenterRightOld) / 3))
                            #     else:
                            #         mouthCenterRightOldLock = False

                    ##############################
                    # Exibir informações na tela
                    # Print info on screen
                    ##############################
                    if args.avatar > 0 or args.view > 0:
                        if args.avatar == 1:
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

                        cv2.putText(showInCv, f"Left Eye  {int(leftEyeBlink)}", (20, 80),
                                    cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)

                        cv2.putText(showInCv, f"Right Eye {int(rightEyeBlink)}", (20, 120),
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
                        if args.avatar > 0:
                            # Left Eye Upper0 / Right Eye Lower0
                            # Olho esquerdo parte superior0 / Olho direito parte inferior0
                            for id in [246, 161, 160, 159, 158, 157, 173, 33, 7, 163, 144, 145, 153, 154, 155, 133, 263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (155, 155, 155), 1)

                            # Left Eye Top
                            # Olho esquerdo parte superior
                            for id in [158, 159, 160]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Left Eye Bottom
                            # Olho esquerdo parte inferior
                            for id in [144, 145, 163]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                            # Right Eye Top
                            # Olho direito parte superior
                            for id in [385, 386, 387]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Right Eye Bottom
                            # Olho direito parte inferior
                            for id in [373, 374, 380]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                            # Nose and iris
                            # Nariz e íris
                            for id in [1, 468, 473]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (55, 255, 55), 1)

                            # Face Oval
                            # Oval do rosto
                            for id in [10, 338, 338, 297, 297, 332, 332, 284, 284, 251, 251, 389, 389, 356, 356, 454, 454, 323, 323, 361, 361, 288, 288, 397, 397, 365, 365, 379, 379, 378, 378, 400, 400, 377, 377, 152, 152, 148, 148, 176, 176, 149, 149, 150, 150, 136, 136, 172, 172, 58, 58, 132, 132, 93, 93, 234, 234, 127, 127, 162, 162, 21, 21, 54, 54, 103, 103, 67, 67, 109, 109, 10]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 0), 1)

                            # Lips Top Inner
                            for id in [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Lips Bottom Inner
                            # Desenha círculos para os pontos de referência internos do lábio inferior
                            for id in [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)


                            # Lips Top Outer
                            # Desenha círculos para os pontos de referência externos do lábio superior
                            for id in [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Lips Bottom Outer
                            # Desenha círculos para os pontos de referência externos do lábio inferior
                            for id in [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

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
                        # Plota gráfico com a variação da abertura dos olhos em relação ao tempo
                        def plotting_ear(pts_plot, line1, min_value, max_value):
                            global figure
                            pts = np.linspace(0, 1, 64)
                            if line1 == []:
                                plt.style.use("ggplot")
                                plt.ion()
                                figure, ax = plt.subplots()
                                line1, = ax.plot(pts, pts_plot)
                                plt.ylim(min_value, max_value)
                                plt.xlim(0, 1)
                                plt.ylabel(args.plot, fontsize=10)
                            else:
                                line1.set_ydata(pts_plot)
                                figure.canvas.draw()
                                figure.canvas.flush_events()
                            return line1

                        if args.plot == 'leftEye':  # Check if the user wants to plot the left eye
                            pts_plot.append(leftEyeBlink)  # Append the blink value to the list of points to be plotted
                            min_value = -0.003
                            max_value = 0.015
                            if countFrames > 70:  # Wait some frames before plotting to avoid initial spikes
                                line1 = plotting_ear(pts_plot, line1, min_value, max_value)  # Call function to plot the graph
                            countFrames += 1

                        elif args.plot == 'rightEye':  # Check if the user wants to plot the right eye
                            pts_plot.append(rightEyeBlink)  # Append the blink value to the list of points to be plotted
                            min_value = -0.003
                            max_value = 0.015
                            if countFrames > 70:  # Wait some frames before plotting to avoid initial spikes
                                line1 = plotting_ear(pts_plot, line1, min_value, max_value)  # Call function to plot the graph
                            countFrames += 1

        #######################################################################
        # Ajuste automático de brilho, contraste, gama e ganho se não detectar pontos de referência, este código é utilizado
        # para ajustar a câmera para que a detecção ocorra
        # Automatic adjustment of brightness, contrast, gamma and gain if it does not detect reference points, this code is used
        # to adjust the camera so that the detection occurs

        else:
            if args.autoBrightness == 1:
                fpsBrightness += 1
                if fpsBrightness > 5:
                    brightnessAverage = np.average(frame)
                    if brightnessAverage < 150:
                        gain = 1
                        source.gain(gain)
                    elif brightnessAverage > 180:
                        gain = 0
                        source.gain(gain)
                    else:
                        fpsBrightness = 0
