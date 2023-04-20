import mediapipe as mp  # to capture info about face
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
import numpy as np  # to make calc
import argparse  # to read parameters from terminal commmand
import matplotlib.pyplot as plt  # to plot graphics
from collections import deque  # to plot graphics
from videosource import WebcamSource  # import file to use webcam image
import config
import sys

from pynput.mouse import Button, Controller  # To use mouse
import tkinter as tk  # To show tooltip
from playsound import playsound  # To play audio
import time
import cv2


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
    
    
    
#####################
# Tooltip code start
#####################
tkTooltip = tk.Tk()

# Show text using tk
def tkTooltipChange(text, color, bg, mouseX, mouseY):
    tooltipText = text
    tooltipTextColor = color
    tooltipBgColor = bg
    tooltipFontSize = 20
    tooltipWidth = len(text) * tooltipFontSize + 16
    tooltipHeight = tooltipFontSize + 14

    # Disable Window Border
    tkTooltip.wm_overrideredirect(True)

    # Width x Height + Left margin + Right margin
    if mouse.position[0] > 300:
        mouseX = mouseX - tooltipWidth - 60

    if mouse.position[1] > 180:
        mouseY = mouseY - tooltipHeight - 60

    tkTooltip.geometry(
        f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}".format(
            tkTooltip.winfo_screenwidth(), tkTooltip.winfo_screenheight()
        )
    )
    # How to close
    tkTooltip.configure(background="#000000")
    # tkTooltip.configure(background="#000000", borderwidth=2, relief="groove")
    # Font
    l = tk.Label(font=("Ubuntu Mono", tooltipFontSize))
    l.pack(expand=True)
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor)
    tkTooltip.update()


# Only show square colored
def tkTooltipOnlyColor(color, bg, mouseX, mouseY, tooltipWidth, tooltipHeight):
    # Disable Window Border
    tkTooltip.wm_overrideredirect(True)

    # Width x Height + Left margin + Right margin
    if mouse.position[0] > 300:
        mouseX = mouseX - tooltipWidth - 60

    if mouse.position[1] > 180:
        mouseY = mouseY - tooltipHeight - 60

    tkTooltip.geometry(
        f"{tooltipWidth}x{tooltipHeight}+{mouseX}+{mouseY}".format(
            tkTooltip.winfo_screenwidth(), tkTooltip.winfo_screenheight()
        )
    )

    # Configure a cor de fundo do canvas como transparente
    canvas = tk.Canvas(tkTooltip, width=tooltipWidth, height=tooltipHeight, borderwidth=2, bg=bg, highlightbackground=color, highlightthickness=2)
    canvas.pack()

    # How to close
    tkTooltip.configure(background=bg)
    tkTooltip.update()


##############################
# Read args from command line
##############################
parser = argparse.ArgumentParser()

for arg_name, arg_details in arg_info.items():
    parser.add_argument(f'--{arg_name}', type=arg_details['type'], help=arg_details['help'], default=arg_details['default'])

args = parser.parse_args()


provided_args = []
for arg in vars(args):
    if f"--{arg}" in sys.argv:
        provided_args.append(arg)

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

    setattr(args, arg_name, arg_value)

for arg_name, arg_details in arg_info.items():
    update_arg(args, arg_name, arg_details['default'], provided_args)



# Distance between points in axys x and y - 2D
def calculate_distance2D(top_indices, bottom_indices):
    top_pointsX = [landmarks_mean[index][0] for index in top_indices]
    bottom_pointsX = [landmarks_mean[index][0] for index in bottom_indices]
    top_pointsY = [landmarks_mean[index][1] for index in top_indices]
    bottom_pointsY = [landmarks_mean[index][1] for index in bottom_indices]
    top_mean = np.sum(top_pointsX + top_pointsY)
    bottom_mean = np.sum(bottom_pointsX + bottom_pointsY)
    distance = np.linalg.norm((bottom_mean + 2) - (top_mean + 2))

    return distance * 500

# Distance between points in axys x and y and z - 3D
def calculate_distance3D(top_indices, bottom_indices):
    top_points = [landmarks_mean[index] for index in top_indices]
    bottom_points = [landmarks_mean[index] for index in bottom_indices]
    top_mean = np.sum(top_points)
    bottom_mean = np.sum(bottom_points)
    distance = np.linalg.norm((bottom_mean + 2) - (top_mean + 2))
    #print(distance)

    return distance * 500


# Get eyes region to detec brightness
def get_eyes_roi(frame, landmarks):
    height, width, _ = frame.shape
    eye_indices = [224, 444, 347, 229]
    # right_eye_indices = [362, 263, 466, 388]
    eye_roy_array = []

    for index in eye_indices:
        x, y = _normalized_to_pixel_coordinates(landmarks[index].x, landmarks[index].y, width, height)
        eye_roy_array.append((x, y))

    eye_roy_array = np.array(eye_roy_array)
    eye_roy_array_rect = cv2.boundingRect(eye_roy_array)

    eye_rois = frame[eye_roy_array_rect[1]:eye_roy_array_rect[1] + eye_roy_array_rect[3], eye_roy_array_rect[0]:eye_roy_array_rect[0] + eye_roy_array_rect[2]]

    return eye_rois


######################
# Facemesh parameters
######################
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(0, 255, 0))

mouse = Controller()  # Enable mouse controller

######################
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
clicktime = 0
clicktimewait = 0
zeroPointX = None
zeroPointY = None
mouseLeftClick = False
mouseRightClick = False
mouseLeftClickSensitivity = 0.8
mouseRightClickSensitivity = 0.8
disableClickInMovementValue = 5
mouseFast = False
confirmLeftClickValue = 2
confirmRightClickValue = 2
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

######################################
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
        # Auto adjust Brightness Contrast Gama
        ######################################
        if args.autoBrightness == 1:
            fpsBrightness += 1        
        frameTime = time.time()
        fpsReal = int(1 / (frameTime - oldframeTime))
        fpsRealMean = (fpsReal + (fpsRealMean * 10)) / 11
        oldframeTime = frameTime

        ############################
        # Work in face mesh result
        ############################
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:

            #################################################################
            # Auto adjust Brightness Contrast Gama and Gain using eye region
            #################################################################
            if fpsBrightness > 5:
                # Process facemesh results
                results = face_mesh.process(frame_rgb)
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    brightness_values = []

                    brightness = np.average(get_eyes_roi(frame_rgb, landmarks))
                    brightness_values.append(brightness)

                    brightness_average = np.mean(brightness_values)
                    #print(brightness_average)

                    if brightness_average < 170:
                        gain = 1
                        source.gain(gain)
                    elif brightness_average > 200:
                        gain = 0
                        source.gain(gain)
                    else:
                        fpsBrightness = 0
                        
            ############################################
            # View show webcam, avatar only show points
            ############################################
            if args.avatar == 1:
                avatar = np.zeros(
                    shape=[args.webcamy, args.webcamx, 3], dtype=np.uint8)
                showInCv = avatar
            else:
                showInCv = frame

            ############################################
            # Create landmarks and landmarks_mean
            ############################################
            if results.multi_face_landmarks is not None:
                face_landmarks = results.multi_face_landmarks[0]
                if frameNumber > 1:
                    landmarks = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])
                    landmarks_mean = (landmarks + landmarks_mean) / 2

                if frameNumber < 2:
                    frameNumber += 1
                    landmarks_mean = np.array([(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark])
                else:
                    mouseMoveX = np.linalg.norm(landmarks_mean[6][0] - landmarks_mean[6][2]) * args.mouseSpeedX * 10
                    mouseMoveY = np.linalg.norm(landmarks_mean[6][1] - landmarks_mean[6][2]) * args.mouseSpeedY * 10
                    if zeroPointX == None:
                        zeroPointX = mouseMoveX
                        zeroPointY = mouseMoveY

                    mousePointX = mouseMoveX - zeroPointX
                    mousePointY = mouseMoveY - zeroPointY

                    mousePointXabs = abs(mousePointX)
                    mousePointYabs = abs(mousePointY)

                    if slowMove > 9:
                        slowMove = slowMove - 1

                    # Mouse acceleration
                    if (mousePointXabs > args.minimalMouseMoveX or mousePointYabs > args.minimalMouseMoveY) and slowMove < 10:
                        if mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                            mousePointXApply = mousePointX * mousePointXabs / (args.slowMouseMoveX)
                            mousePointYApply = mousePointY * mousePointYabs / (args.slowMouseMoveY)
                            slowMove = 11
                        else:
                            mousePointXApply = mousePointX * mousePointXabs / (args.slowMouseMoveX)
                            mousePointYApply = mousePointY * mousePointYabs / (args.slowMouseMoveY)

                        if stopCursor == False:
                            mouse.move(int(mousePointXApply), int(mousePointYApply))

                            # Change zeroPointX when mouse on limit screen
                            if mousePositionFrameX == mouse.position[0] and mousePointXabs > 1:
                                zeroPointX = zeroPointX - ((zeroPointX - mouseMoveX) * 0.1)

                            # Change zeroPointY when mouse on limit screen
                            if mousePositionFrameY == mouse.position[1] and mousePointYabs > 1:
                                zeroPointY = zeroPointY - ((zeroPointY - mouseMoveY) * 0.1)

                            mousePositionFrameX = mouse.position[0]
                            mousePositionFrameY = mouse.position[1]

                    ############################
                    # Blink to mouse click start
                    ############################
                    if args.blinkToClick == True:
                        
                        if rightClicked == True:

                            if changeRightMove == True and rightMoved == 'right':
                                tkTooltipOnlyColor("#000000", "#ffff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeRightMove = False

                            elif changeRightMove == True and rightMoved == 'left':
                                tkTooltipOnlyColor("#000000", "#00ff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeRightMove = False

                            if mousePointX > args.minimalMouseMoveX and rightMoved != 'right':
                                rightMoved = 'right'
                                changeRightMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX < - args.minimalMouseMoveX and rightMoved != 'left':
                                rightMoved = 'left'
                                changeRightMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()


                            elif rightMoved == 'no':
                                tkTooltipOnlyColor("#000000", "#ff0000", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)

#                            print(f"x {int(mousePointX)}")
#                            print(f"y {int(mousePointYApply)}")


                        if leftClickedConstant == True:
                            tkTooltipOnlyColor("#000000", "#00ff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)

                        if leftClicked == True:

                            if changeLeftMove == True and leftMoved == 'right':
                                tkTooltipOnlyColor("#000000", "#ffff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            elif changeLeftMove == True and leftMoved == 'left':
                                tkTooltipOnlyColor("#000000", "#00ff00", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            elif changeLeftMove == True and leftMoved == 'bottom':
                                tkTooltipOnlyColor("#000000", "#2266ff", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                changeLeftMove = False

                            if mousePointX > args.slowMouseMoveX and leftMoved != 'right':
                                leftMoved = 'right'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointX < - args.slowMouseMoveX and leftMoved != 'left':
                                leftMoved = 'left'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                            elif mousePointY > args.slowMouseMoveY and leftMoved != 'bottom':
                                leftMoved = 'bottom'
                                changeLeftMove = True
                                tkTooltip.destroy()
                                tkTooltip = tk.Tk()

                        # Calculate using 2d information about 3 top points and 3 bottom points
                        rightEyeBlink = calculate_distance2D([385, 386, 387], [373, 374, 380])

                        # Calculate using 2d information about 3 top points and 3 bottom points
                        leftEyeBlink = calculate_distance2D([158, 159, 160], [163, 145, 144])

                        # In stand by click stop to refresh normalized value
                        if standByClick == False:
                            rightEyeNormalized = np.mean([rightEyeBlink, rightEyeBlinkOld])
                            leftEyeNormalized = np.mean([leftEyeBlink, leftEyeBlinkOld])
                            rightEyeBlinkOld = ((rightEyeBlinkOld * fpsRealMean) + rightEyeBlink) / (fpsRealMean + 1)
                            leftEyeBlinkOld = ((leftEyeBlinkOld * fpsRealMean) + leftEyeBlink) / (fpsRealMean + 1)

                        # Disable click if close two eyes
                        if leftEyeBlink < leftEyeBlinkOld * 0.6 and rightEyeBlink < rightEyeBlinkOld * 0.6:
                            standByClick = True
                        else:
                            if rightEyeBlink < rightEyeBlinkOld * 0.5 and (standByClick == False or confirmRightClick > 1) and leftClicked == False and rightClicked == False and mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                confirmRightClick += 1
                                standByClick = True

                                if confirmRightClick >= fpsRealMean / 6:
                                    stopCursor = True
                                    tooltipWait = False
                                    rightClicked = True
                                    scrollModeVertical = False
                                    scrollModeHorizontal = False
                                    leftClickedConstant = False
                                    if rightMoved != 'no':
                                        rightMoved = 'clean'
                                    leftMoved = 'no'

                                    #tkTooltipOnlyColor("#ff0000", "#ff0000", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                            else:
                                confirmRightClick = 1
                                if rightEyeBlink > rightEyeNormalized and rightClicked == True:
                                    if rightMoved == 'no':
                                        mouse.press(Button.right)
                                        mouse.release(Button.right)
                                        stopCursor = False
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                    if rightMoved == 'right':
                                        scrollModeVertical = True
                                    if rightMoved == 'left':
                                        scrollModeHorizontal = True
                                    if rightMoved == 'clean':
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                        stopCursor = False
                                        rightMoved = 'no'
                                    rightClicked = False
                                    standByClick = False
                                    tooltipWait = False

                            if leftEyeBlink < leftEyeBlinkOld * 0.5 and (standByClick == False or confirmLeftClick > 1) and leftClicked == False and rightClicked == False and mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                confirmLeftClick += 1
                                standByClick = True

                                if confirmLeftClick >= fpsRealMean / 6:
                                    stopCursor = True
                                    tooltipWait = False
                                    leftClicked = True
                                    scrollModeVertical = False
                                    scrollModeHorizontal = False
                                    leftClickedConstant = False
                                    rightMoved = 'no'
                                    leftMoved = 'no'
                                    tkTooltipOnlyColor("#000000", "#00b21f", mouse.position[0] + 30, mouse.position[1] + 30, 20, 20)
                                    # tkTooltipChange("L", "#00b21f", "#000000", mouse.position[0] + 30, mouse.position[1] + 30)

                                    # playsound('click.wav', block=False)
                            else:
                                confirmLeftClick = 1
                                if leftClicked == False and rightClicked == False:
                                    standByClick = False

                                elif leftEyeBlink > leftEyeNormalized and leftClicked == True:
                                    if leftMoved == 'no':
                                        mouse.press(Button.left)
                                        mouse.release(Button.left)
                                        stopCursor = False
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                    if leftMoved == 'right':
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                        mouse.press(Button.left)
                                        mouse.release(Button.left)
                                        mouse.press(Button.left)
                                        mouse.release(Button.left)
                                        stopCursor = False
                                        leftMoved = 'no'
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                    if leftMoved == 'left':
                                        mouse.press(Button.left)
                                        stopCursor = False
                                        leftClickedConstant = True
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                    if leftMoved == 'bottom':
                                        zeroPointX = mouseMoveX
                                        zeroPointY = mouseMoveY
                                        mouse.press(Button.middle)
                                        mouse.release(Button.middle)
                                        stopCursor = False
                                        leftMoved = 'no'
                                        tkTooltip.destroy()
                                        tkTooltip = tk.Tk()
                                    leftClicked = False
                                    standByClick = False
                                    tooltipWait = False
                                    tkTooltip.destroy()
                                    tkTooltip = tk.Tk()


                            if ((leftEyeBlink < leftEyeNormalized * 0.8) or (rightEyeBlink < rightEyeNormalized * 0.8)) and (mousePointXabs < 3 or mousePointYabs < 3) and leftClicked == False and rightClicked == False:
                                if zeroPointX > mousePointX: zeroPointX = zeroPointX - ((zeroPointX - mouseMoveX) * 0.1)
                                else:
                                    zeroPointX = zeroPointX - ((mouseMoveX - zeroPointX) * 0.1)

                                if zeroPointY > mousePointY:
                                    zeroPointY = zeroPointY - ((zeroPointY - mouseMoveY) * 0.1)
                                else:
                                    zeroPointY = zeroPointY - ((mouseMoveY - zeroPointY) * 0.1)

                            ####################
                            # Scroll mode Vertical
                            ####################
                            if scrollModeVertical == True and mousePointYabs > args.minimalMouseMoveY and slowMove < 10:
                                scrollValueX = mousePointYApply / (fpsRealMean / 2)
                                if scrollValueX < 1 and scrollValueX > 0:
                                    scrollValueX = 1
                                elif scrollValueX > -1 and scrollValueX < 0:
                                    scrollValueX = -1
                                mouse.scroll(0, - scrollValueX)
                                slowMove = 10 + (fpsRealMean / 10)
                                print(mousePointYApply)

                            ####################
                            # Scroll mode Horizontal
                            ####################
                            if scrollModeHorizontal == True and mousePointXabs > args.minimalMouseMoveX and slowMove < 10:
                                scrollValueY = mousePointXApply / (fpsRealMean / 2)
                                if scrollValueY < 1 and scrollValueY > 0:
                                    scrollValueY = 1
                                elif scrollValueY > -1 and scrollValueY < 0:
                                    scrollValueY = -1
                                mouse.scroll(scrollValueY, 0)
                                slowMove = 10 + (fpsRealMean / 10)
                                print(mousePointYApply)


                            ####################
                            # Scroll with mouth
                            ####################
                            if args.mouthScroll == 1:
                                mouthCenterLeft = np.linalg.norm(landmarks_mean[214] - landmarks_mean[87]) * 1000
                                if mouthCenterLeftOldLock == False and mouthCenterRightOldLock == False:
                                    if mouthCenterLeftOld == 0:
                                        mouthCenterLeftOld = mouthCenterLeft
                                    else:
                                        mouthCenterLeftOld = ((mouthCenterLeftOld * fpsRealMean) + mouthCenterLeft) / (fpsRealMean + 1)

                                if mouthCenterLeft * 1.1 < mouthCenterLeftOld and standByClick == False and (mousePointXabs < 2 or mousePointYabs < 2):
                                    mouthCenterLeftOldLock = True
                                    mouse.scroll(0, ((mouthCenterLeftOld - mouthCenterLeft) / 3))

                                else:
                                    mouthCenterLeftOldLock = False

                                mouthCenterRight = np.linalg.norm(landmarks_mean[434] - landmarks_mean[317]) * 1000
                                if mouthCenterRightOldLock == False and mouthCenterLeftOldLock == False:
                                    if mouthCenterRightOld == 0:
                                        mouthCenterRightOld = mouthCenterRight
                                    else:
                                        mouthCenterRightOld = ((mouthCenterRightOld * fpsRealMean) + mouthCenterRight) / (fpsRealMean + 1)

                                if mouthCenterRight * 1.05 < mouthCenterRightOld and standByClick == False and (mousePointXabs < 2 or mousePointYabs < 2):
                                    mouthCenterRightOldLock = True
                                    mouse.scroll(0, ((mouthCenterRight - mouthCenterRightOld) / 3))
                                else:
                                    mouthCenterRightOldLock = False

                    ##############################
                    # Print info in screen
                    ##############################
                    if args.avatar > 0 or args.view > 0:

                        cv2.rectangle(showInCv, (0, 0), (300, 300), (0, 0, 0), -1)

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
                            # Center horizontal line
                            cv2.line(showInCv, (0, (int(args.webcamy / 2))), (args.webcamx, (int(args.webcamy / 2))), (255, 255, 255), 1)
                            cv2.line(showInCv, (0, (int(args.webcamy / 2) + 1)), (args.webcamx, (int(args.webcamy / 2) + 1)), (0, 0, 0), 1)

                            # Center vertical line
                            cv2.line(showInCv, ((int(args.webcamx / 2), 0)), ((int(args.webcamx / 2), args.webcamx)), (255, 255, 255), 1)
                            cv2.line(showInCv, ((int(args.webcamx / 2) + 1, 0)), ((int(args.webcamx / 2) + 1, args.webcamx)), (0, 0, 0), 1)

                        ##############################
                        # Show points in avatar
                        ##############################
                        if args.avatar > 0:
                            # Left Eye Upper0 / Right Eye Lower0
                            for id in [246, 161, 160, 159, 158, 157, 173, 33, 7, 163, 144, 145, 153, 154, 155, 133, 263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (155, 155, 155), 1)

                            # Left Eye Top
                            for id in [158, 159, 160]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Left Eye Bottom
                            for id in [144, 145, 163]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                            # Right Eye Top
                            for id in [385, 386, 387]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Right Eye Bottom
                            for id in [373, 374, 380]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                            # Right Nose and iris
                            for id in [1, 468, 473]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (55, 255, 55), 1)

                            # Face Oval
                            for id in [10, 338, 338, 297, 297, 332, 332, 284, 284, 251, 251, 389, 389, 356, 356, 454, 454, 323, 323, 361, 361, 288, 288, 397, 397, 365, 365, 379, 379, 378, 378, 400, 400, 377, 377, 152, 152, 148, 148, 176, 176, 149, 149, 150, 150, 136, 136, 172, 172, 58, 58, 132, 132, 93, 93, 234, 234, 127, 127, 162, 162, 21, 21, 54, 54, 103, 103, 67, 67, 109, 109, 10]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 0), 1)

                            # Lips Top Inner
                            for id in [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Lips Bottom Inner
                            for id in [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                            # Lips Top Outer
                            for id in [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                            # Lips Bottom Outer
                            for id in [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]:
                                cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                        ##############################
                        # Show webcam
                        ##############################
                        for face_landmarks in results.multi_face_landmarks:
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

                        if args.plot == 'leftEye':
                            pts_plot.append(leftEyeBlink)
                            min_value = -0.003
                            max_value = 0.015
                            if countFrames > 70:
                                line1 = plotting_ear(pts_plot, line1, min_value, max_value)
                            countFrames += 1

                        elif args.plot == 'rightEye':
                            pts_plot.append(rightEyeBlink)
                            min_value = -0.003
                            max_value = 0.015
                            if countFrames > 70:
                                line1 = plotting_ear(pts_plot, line1, min_value, max_value)
                            countFrames += 1

        #######################################################################
        # Auto adjust Brightness Contrast Gama and Gain if not detect landmarks
        #######################################################################
        else:
            if args.autoBrightness == 1:
                fpsBrightness += 1
                if fpsBrightness > 5:
                    brightnessAverage = np.average(frame)
                    print(brightnessAverage)
                    if brightnessAverage < 150:
                        gain = 1
                        source.gain(gain)
                    elif brightnessAverage > 180:
                        gain = 0
                        source.gain(gain)
                    else:
                        fpsBrightness = 0
