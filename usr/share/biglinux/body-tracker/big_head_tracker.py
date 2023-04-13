import mediapipe as mp  # to capture info about face
import numpy as np  # to make calc
import argparse  # to read parameters from terminal commmand
import matplotlib.pyplot as plt  # to plot graphics
from collections import deque  # to plot graphics
from videosource import WebcamSource  # import file to use webcam image


from pynput.mouse import Button, Controller  # To use mouse
import tkinter as tk  # To show tooltip
from playsound import playsound  # To play audio
import time
import cv2

#####################
# Tooltip code start
#####################
tkTooltip = tk.Tk()


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
    tkTooltip.configure(background="#000000", borderwidth=2, relief="groove")
    # Font
    l = tk.Label(font=("Ubuntu Mono", tooltipFontSize))
    l.pack(expand=True)
    l.config(text=tooltipText, fg=tooltipTextColor, bg=tooltipBgColor)
    tkTooltip.update()


##############################
# Read args from command line
##############################
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--view", type=int, help="Show webcam image", default=0)
parser.add_argument("--avatar", type=int, help="Show avatar image", default=0)
parser.add_argument("--webcamid", type=int,
                    help="Number of webcam in /dev/video", default=0)
parser.add_argument("--webcamx", type=int,
                    help="Width of webcam image", default=1024)
parser.add_argument("--webcamy", type=int,
                    help="Height of webcam image", default=768)
parser.add_argument("--fps", type=int,
                    help="Frames per second", default=15)
parser.add_argument("--plot", type=str,
                    help="Plot graphic, use leftEye or rightEye", default='None')
parser.add_argument("--blinkToClick", type=int,
                    help="Blink eyes to click in mouse use 0 or 1", default=1)
parser.add_argument("--leftEyeBlinkFunction", type=str,
                    help="Select left Eye Blink usage", default='leftClick')
parser.add_argument("--minimalMouseMoveY", type=int,
                    help="Movement needed to start move mouse", default=3)
parser.add_argument("--minimalMouseMoveX", type=int,
                    help="Movement needed to start move mouse", default=3)
parser.add_argument("--slowMouseMoveY", type=int,
                    help="Movement needed to start move mouse", default=6)
parser.add_argument("--slowMouseMoveX", type=int,
                    help="Movement needed to start move mouse", default=6)
parser.add_argument("--mouseSpeedX", type=int,
                    help="Horizontal speed of mouse moviment", default=40)
parser.add_argument("--mouseSpeedY", type=int,
                    help="Vertical speed of mouse moviment", default=40)
parser.add_argument("--autoBrightness", type=int,
                    help="Automatic change webcam brightness, contrast and gamma", default=1)
parser.add_argument("--mouthScroll", type=int,
                    help="Moving the mouth left or right moves the scroll", default=0)

args = parser.parse_args()


######################
# Facemesh parameters
######################
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
mp_face_mesh_connections = mp.solutions.face_mesh_connections
drawing_spec = mp_drawing.DrawingSpec(
    thickness=1, circle_radius=0, color=(0, 255, 0))

mouse = Controller()  # Enable mouse controller

######################
# Init variables
######################
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
source = WebcamSource(width=args.webcamx, height=args.webcamy,
                      fps=args.fps, camera_id=args.webcamid)
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
        #################################################
        # Auto adjust Brightness Contrast Gama and Gain
        #################################################
        if args.autoBrightness == 1:
            fpsBrightness += 1
            if fpsBrightness > 5:
                brightnessAverage = np.average(frame)
                if brightnessAverage < 150:
                    gain += 10
                    fpsBrightness = 0
                elif brightnessAverage > 180:
                    gain -= 10
                fpsBrightness = 0
            source.gain(gain)

        ############################
        # Work in face mesh result
        ############################
        results = face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            # 468 landmak points in all face, see this link to view images about landmark positions:
            # https://github.com/ManuelTS/augmentedFaceMeshIndices

            # Lips
            # 61, 146, 146, 91, 91, 181, 181, 84, 84, 17, 17, 314, 314, 405, 405, 321,
            # 321, 375, 375, 291, 61, 185, 185, 40, 40, 39, 39, 37, 37, 0, 0, 267, 267,
            # 269, 269, 270, 270, 409, 409, 291, 78, 95, 95, 88, 88, 178, 178, 87, 87, 14,
            # 14, 317, 317, 402, 402, 318, 318, 324, 324, 308, 78, 191, 191, 80, 80, 81,
            # 81, 82, 82, 13, 13, 312, 312, 311, 311, 310, 310, 415, 415, 308

            # Left eye
            # 33, 7, 7, 163, 163, 144, 144, 145, 145, 153, 153, 154, 154, 155, 155, 133,
            # 33, 246, 246, 161, 161, 160, 160, 159, 159, 158, 158, 157, 157, 173, 173,
            # 133

            # Right eye.
            # 263, 249, 249, 390, 390, 373, 373, 374, 374, 380, 380, 381, 381, 382, 382,
            # 362, 263, 466, 466, 388, 388, 387, 387, 386, 386, 385, 385, 384, 384, 398,
            # 398, 362

            # Face oval.
            # 10, 338, 338, 297, 297, 332, 332, 284, 284, 251, 251, 389, 389, 356, 356,
            # 454, 454, 323, 323, 361, 361, 288, 288, 397, 397, 365, 365, 379, 379, 378,
            # 378, 400, 400, 377, 377, 152, 152, 148, 148, 176, 176, 149, 149, 150, 150,
            # 136, 136, 172, 172, 58, 58, 132, 132, 93, 93, 234, 234, 127, 127, 162, 162,
            # 21, 21, 54, 54, 103, 103, 67, 67, 109, 109, 10

            # lipsUpperOuter: [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
            # lipsLowerOuter: [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
            # lipsUpperInner: [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
            # lipsLowerInner: [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
            # rightEyeUpper0: [246, 161, 160, 159, 158, 157, 173]
            # rightEyeLower0: [33, 7, 163, 144, 145, 153, 154, 155, 133]
            # rightEyeUpper1: [247, 30, 29, 27, 28, 56, 190]
            # rightEyeLower1: [130, 25, 110, 24, 23, 22, 26, 112, 243]
            # rightEyeUpper2: [113, 225, 224, 223, 222, 221, 189]
            # rightEyeLower2: [226, 31, 228, 229, 230, 231, 232, 233, 244]
            # rightEyeLower3: [143, 111, 117, 118, 119, 120, 121, 128, 245]
            # rightEyebrowUpper: [156, 70, 63, 105, 66, 107, 55, 193]
            # rightEyebrowLower: [35, 124, 46, 53, 52, 65]
            # rightEyeIris: [473, 474, 475, 476, 477]
            # leftEyeUpper0: [466, 388, 387, 386, 385, 384, 398]
            # leftEyeLower0: [263, 249, 390, 373, 374, 380, 381, 382, 362]
            # leftEyeUpper1: [467, 260, 259, 257, 258, 286, 414]
            # leftEyeLower1: [359, 255, 339, 254, 253, 252, 256, 341, 463]
            # leftEyeUpper2: [342, 445, 444, 443, 442, 441, 413]
            # leftEyeLower2: [446, 261, 448, 449, 450, 451, 452, 453, 464]
            # leftEyeLower3: [372, 340, 346, 347, 348, 349, 350, 357, 465]
            # leftEyebrowUpper: [383, 300, 293, 334, 296, 336, 285, 417]
            # leftEyebrowLower: [265, 353, 276, 283, 282, 295]
            # leftEyeIris: [468, 469, 470, 471, 472]

            # 468 Left Iris, center point
            # 469 Left Iris, right point
            # 470 Left Iris, top point
            # 471 Left Iris, left point
            # 472 Left Iris, bottom point

            # 473 Right Iris, center point
            # 474 Right Iris, right point
            # 475 Right Iris, top point
            # 476 Right Iris, left point
            # 477 Right Iris, bottom point

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
            face_landmarks = results.multi_face_landmarks[0]
            if frameNumber > 1:
                landmarks = np.array([(lm.x, lm.y, lm.z)
                                      for lm in face_landmarks.landmark])
                landmarks_mean = (landmarks + landmarks_mean) / 2

            if frameNumber < 2:
                frameNumber += 1
                landmarks_mean = np.array([(lm.x, lm.y, lm.z)
                                           for lm in face_landmarks.landmark])
            else:
                ###################################
                # Move mouse using iris
                ###################################
                # leftIrisLookingLeft = (np.linalg.norm(
                #     landmarks_mean[468][0]) - np.linalg.norm(landmarks_mean[130][0]))
                # leftIrisLookingRight = (np.linalg.norm(
                #     landmarks_mean[133][0]) - np.linalg.norm(landmarks_mean[468][0]))
                # leftIrisLookingTop = (np.linalg.norm(
                #     landmarks_mean[468][1]) - np.linalg.norm((landmarks_mean[133][1] + landmarks_mean[130][1]) / 2))
                # leftIrisLookingBottom = (np.linalg.norm(
                #     landmarks_mean[27]) - np.linalg.norm((landmarks_mean[133] + landmarks_mean[130]) / 2))
                # print(f"Iris Left: {leftIrisLookingLeft}")
                # print(f"Iris Top: {leftIrisLookingTop}")
                # mouseMoveX = leftIrisLookingLeft * 3000
                # mouseMoveY = leftIrisLookingTop * 3000

                mouseMoveX = np.linalg.norm(
                    landmarks_mean[6][0] - landmarks_mean[6][2]) * args.mouseSpeedX * 10
                mouseMoveY = np.linalg.norm(
                    landmarks_mean[6][1] - landmarks_mean[6][2]) * args.mouseSpeedY * 10
                if zeroPointX == None:
                    zeroPointX = mouseMoveX
                    zeroPointY = mouseMoveY

                mousePointX = mouseMoveX - zeroPointX
                mousePointXabs = abs(mousePointX)

                mousePointY = mouseMoveY - zeroPointY
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

                    if scrollMouse == False:
                        mouse.move(int(mousePointXApply), int(mousePointYApply))

                    # Change zeroPointX when mouse on limit screen
                    if mousePositionFrameX == mouse.position[0] and mousePointXabs > 1:
                        zeroPointX = zeroPointX - \
                            ((zeroPointX - mouseMoveX) * 0.1)

                    # Change zeroPointY when mouse on limit screen
                    if mousePositionFrameY == mouse.position[1] and mousePointYabs > 1:
                        zeroPointY = zeroPointY - \
                            ((zeroPointY - mouseMoveY) * 0.1)

                    mousePositionFrameX = mouse.position[0]
                    mousePositionFrameY = mouse.position[1]




                ############################
                # Blink to mouse click start
                ############################
                if args.blinkToClick == True:
                    #Normal
                    # leftEyeTopPoint1 = [landmarks[158][0] + landmarks[159][0] + landmarks[160][0] + landmarks[158][1] + landmarks[159][1] + landmarks[160][1]]
                    # leftEyeBottomPoint1 = [landmarks[163][0] + landmarks[145][0] + landmarks[144][0] + landmarks[163][1] + landmarks[145][1] + landmarks[144][1]]
                    #Mean
                    leftEyeTopPoint1 = [landmarks_mean[158][0] + landmarks_mean[159][0] + landmarks_mean[160][0] + landmarks_mean[158][1] + landmarks_mean[159][1] + landmarks_mean[160][1] + 2]
                    leftEyeBottomPoint1 = [landmarks_mean[163][0] + landmarks_mean[145][0] + landmarks_mean[144][0] + landmarks_mean[163][1] + landmarks_mean[145][1] + landmarks_mean[144][1] + 2]


                    # print(landmarks_mean[158][0])
                    # print(landmarks_mean[159][0])
                    # print(landmarks_mean[160][0])
                    # print(landmarks_mean[158][1])
                    # print(landmarks_mean[159][1])
                    # print(landmarks_mean[160][1])

                    # print(landmarks_mean[387][0])
                    # print(landmarks_mean[385][0])
                    # print(landmarks_mean[386][0])
                    # print(landmarks_mean[387][1])
                    # print(landmarks_mean[385][1])
                    # print(landmarks_mean[386][1])
                    # print(np.linalg.norm(leftEyeTopPoint1width) - np.linalg.norm(leftEyeBottomPoint1heigth))

                    leftEyeBlink = (np.linalg.norm(leftEyeBottomPoint1) - np.linalg.norm(leftEyeTopPoint1)) * 500  # use distance between leftEyeBottomPoint1 to LeftEyeTopPoint1 for detect blink left eye

                    #Normal
                    # rightEyeTopPoint1 = [landmarks[387][0] + landmarks[385][0] + landmarks[386][0] + landmarks[387][1] + landmarks[385][1] + landmarks[386][1]]
                    # rightEyeBottomPoint1 = [landmarks[374][0] + landmarks[380][0] + landmarks[373][0] + landmarks[374][1] + landmarks[380][1] + landmarks[373][1]]
                    #Mean
                    rightEyeTopPoint1 = [landmarks_mean[387][0] + landmarks_mean[385][0] + landmarks_mean[386][0] + landmarks_mean[387][1] + landmarks_mean[385][1] + landmarks_mean[386][1] + 2]
                    rightEyeBottomPoint1 = [landmarks_mean[374][0] + landmarks_mean[380][0] + landmarks_mean[373][0] + landmarks_mean[374][1] + landmarks_mean[380][1] + landmarks_mean[373][1] + 2]
                    rightEyeBlink = (np.linalg.norm(rightEyeBottomPoint1) - np.linalg.norm(rightEyeTopPoint1)) * 500  # same of left eye but to right eye

                    # In stand by click stop to refresh normalized value
                    if standByClick == False:
                        rightEyeNormalized = np.mean(
                            [rightEyeBlink, rightEyeBlinkOld])
                        leftEyeNormalized = np.mean(
                            [leftEyeBlink, leftEyeBlinkOld])

                    rightEyeBlinkOld = (
                        (rightEyeBlinkOld * args.fps) + rightEyeBlink) / (args.fps + 1)
                    leftEyeBlinkOld = (
                        (leftEyeBlinkOld * args.fps) + leftEyeBlink) / (args.fps + 1)

                    # Disable click if close two eyes
                    if leftEyeBlink < leftEyeNormalized * 0.9 and rightEyeBlink < rightEyeNormalized * 0.9:
                        standByClick = True
                        confirmLeftClick = 1
                        confirmRightClick = 1
                        tooltipWait = True
                        # tkTooltipChange("Wait", "#00b21f", "#000000",
                        #                 mouse.position[0] + 30, mouse.position[1] + 30)
                    else:
                        if tooltipWait == True:
                            tkTooltip.destroy()
                            tkTooltip = tk.Tk()

                        if rightClicked == True:
                            tkTooltipChange("R", "#00b21f", "#000000",
                                            mouse.position[0] + 30, mouse.position[1] + 30)
                            
                        if rightEyeBlink < rightEyeBlinkOld * 0.5 and (standByClick == False or confirmRightClick > 1) and leftClicked == False and rightClicked == False:
                            confirmRightClick += 1
                            standByClick = True

                            if confirmRightClick >= confirmRightClickValue and mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                mouse.press(Button.right)
                                tooltipWait = False
                                rightClicked = True
                                # playsound('click.wav', block=False)
                        else:
                            confirmRightClick = 1
                            if rightClicked == False and leftClicked == False:
                                standByClick = False

                            elif rightEyeBlink > rightEyeNormalized and rightClicked == True:
                                mouse.release(Button.right)
                                rightClicked = False
                                standByClick = False
                                tooltipWait = True

                        if leftClicked == True:
                            tkTooltipChange("L", "#00b21f", "#000000",
                                            mouse.position[0] + 30, mouse.position[1] + 30)

                        if leftEyeBlink < leftEyeBlinkOld * 0.5 and (standByClick == False or confirmLeftClick > 1) and leftClicked == False and rightClicked == False:
                            confirmLeftClick += 1
                            standByClick = True
                            if confirmLeftClick >= confirmLeftClickValue and mousePointXabs < args.slowMouseMoveX and mousePointYabs < args.slowMouseMoveY:
                                mouse.press(Button.left)
                                tooltipWait = False
                                leftClicked = True
                                # playsound('click.wav', block=False)
                        else:
                            confirmLeftClick = 1
                            if leftClicked == False and rightClicked == False:
                                standByClick = False

                            elif leftEyeBlink > leftEyeNormalized and leftClicked == True:
                                mouse.release(Button.left)
                                leftClicked = False
                                standByClick = False
                                tooltipWait = True

                        if ((leftEyeBlink < leftEyeNormalized * 0.8) or (rightEyeBlink < rightEyeNormalized * 0.8)) and (mousePointXabs < 3 or mousePointYabs < 3) and leftClicked == False and rightClicked == False:
                            if zeroPointX > mousePointX:
                                zeroPointX = zeroPointX - \
                                    ((zeroPointX - mouseMoveX) * 0.1)
                            else:
                                zeroPointX = zeroPointX - \
                                    ((mouseMoveX - zeroPointX) * 0.1)

                            if zeroPointY > mousePointY:
                                zeroPointY = zeroPointY - \
                                    ((zeroPointY - mouseMoveY) * 0.1)
                            else:
                                zeroPointY = zeroPointY - \
                                    ((mouseMoveY - zeroPointY) * 0.1)

                        ####################
                        # Scroll with mouth
                        ####################
                        if args.mouthScroll == 1:
                            mouthCenterLeft = np.linalg.norm(
                                landmarks_mean[214] - landmarks_mean[87]) * 1000
                            if mouthCenterLeftOldLock == False and mouthCenterRightOldLock == False:
                                if mouthCenterLeftOld == 0:
                                    mouthCenterLeftOld = mouthCenterLeft
                                else:
                                    mouthCenterLeftOld = (
                                        (mouthCenterLeftOld * args.fps) + mouthCenterLeft) / (args.fps + 1)

                            if mouthCenterLeft * 1.1 < mouthCenterLeftOld and standByClick == False and (mousePointXabs < 2 or mousePointYabs < 2):
                                mouthCenterLeftOldLock = True
                                mouse.scroll(
                                    0, ((mouthCenterLeftOld - mouthCenterLeft) / 3))

                            else:
                                mouthCenterLeftOldLock = False

                            mouthCenterRight = np.linalg.norm(
                                landmarks_mean[434] - landmarks_mean[317]) * 1000
                            if mouthCenterRightOldLock == False and mouthCenterLeftOldLock == False:
                                if mouthCenterRightOld == 0:
                                    mouthCenterRightOld = mouthCenterRight
                                else:
                                    mouthCenterRightOld = (
                                        (mouthCenterRightOld * args.fps) + mouthCenterRight) / (args.fps + 1)

                            if mouthCenterRight * 1.05 < mouthCenterRightOld and standByClick == False and (mousePointXabs < 2 or mousePointYabs < 2):
                                mouthCenterRightOldLock = True
                                mouse.scroll(
                                    0, ((mouthCenterRight - mouthCenterRightOld) / 3))
                            else:
                                mouthCenterRightOldLock = False

                ##############################
                # Print info in screen
                ##############################
                if args.avatar > 0 or args.view > 0:

                    frameTime = time.time()
                    fps = 1 / (frameTime - oldframeTime)
                    oldframeTime = frameTime

                    cv2.rectangle(showInCv, (0, 0), (300, 300), (0, 0, 0), -1)

                    cv2.putText(showInCv, f"FPS {int(fps)}", (20, 40),
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
                        cv2.line(showInCv, (0, (int(args.webcamy / 2))),
                                 (args.webcamx, (int(args.webcamy / 2))), (255, 255, 255), 1)
                        cv2.line(showInCv, (0, (int(args.webcamy / 2) + 1)),
                                 (args.webcamx, (int(args.webcamy / 2) + 1)), (0, 0, 0), 1)

                        # Center vertical line
                        cv2.line(showInCv, ((int(args.webcamx / 2), 0)),
                                 ((int(args.webcamx / 2), args.webcamx)), (255, 255, 255), 1)
                        cv2.line(showInCv, ((int(args.webcamx / 2) + 1, 0)),
                                 ((int(args.webcamx / 2) + 1, args.webcamx)), (0, 0, 0), 1)

                    ##############################
                    # Show points in avatar
                    ##############################
                    if args.avatar > 0:
                        # Left Eye Upper0 / Right Eye Lower0
                        for id in [246, 161, 160, 159, 158, 157, 173, 33, 7, 163, 144, 145, 153, 154, 155, 133, 263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (155, 155, 155), 1)

                        # Left Eye Top
                        for id in [160, 158, 159]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Left Eye Bottom
                        for id in [153, 145, 144]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                        # Right Eye Top
                        for id in [385, 386, 387]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Right Eye Bottom
                        for id in [373, 374, 380]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                        # Right Nose and iris
                        for id in [1, 468, 473]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (55, 255, 55), 1)

                        # Face Oval
                        for id in [10, 338, 338, 297, 297, 332, 332, 284, 284, 251, 251, 389, 389, 356, 356, 454, 454, 323, 323, 361, 361, 288, 288, 397, 397, 365, 365, 379, 379, 378, 378, 400, 400, 377, 377, 152, 152, 148, 148, 176, 176, 149, 149, 150, 150, 136, 136, 172, 172, 58, 58, 132, 132, 93, 93, 234, 234, 127, 127, 162, 162, 21, 21, 54, 54, 103, 103, 67, 67, 109, 109, 10]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 0), 1)

                        # Lips Top Inner
                        for id in [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Lips Bottom Inner
                        for id in [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

                        # Lips Top Outer
                        for id in [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (255, 0, 255), 1)

                        # Lips Bottom Outer
                        for id in [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]:
                            cv2.circle(showInCv, (int(landmarks_mean[id][0] * args.webcamx), int(
                                landmarks_mean[id][1] * args.webcamy)), 1, (0, 255, 255), 1)

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
                            line1 = plotting_ear(
                                pts_plot, line1, min_value, max_value)
                        countFrames += 1

                    elif args.plot == 'rightEye':
                        pts_plot.append(rightEyeBlink)
                        min_value = -0.003
                        max_value = 0.015
                        if countFrames > 70:
                            line1 = plotting_ear(
                                pts_plot, line1, min_value, max_value)
                        countFrames += 1
