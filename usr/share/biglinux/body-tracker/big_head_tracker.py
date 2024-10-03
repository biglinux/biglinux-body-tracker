# Import configurations
with open('config.py') as file:
    exec(file.read())

# Import GUI functionalities
with open('gui.py') as file:
    exec(file.read())

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
        mouse.press(Button.right)

    elif action == 'releaseRight':
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
# Function to calculate the distance between points in x and y axes - 2D
#####################
with open('calc_distance.py') as file:
    exec(file.read())

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
                    verify_false_click('rightEye', 0.7, 0, 'showOptions1', 'releaseOptions1')

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
                    with open('plot.py') as file:
                        exec(file.read())
