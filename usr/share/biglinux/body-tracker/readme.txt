
Utilizando o pip
pip install mediapipe pynput tk playsound

No sistema é preciso instalar o tk
sudo pacman -S tk


Para instalar no BigLinux sem o pip:
sudo pacman -S tk python-mediapipe python-pynput python-playsound




Eye reference
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
