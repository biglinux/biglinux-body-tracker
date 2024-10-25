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
