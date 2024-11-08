# BigLinux Body Tracker

This is the **BigLinux Body Tracker**, a Python-based application that allows users to control the mouse cursor with facial gestures. It is designed to help users with limited mobility by using computer vision and facial recognition techniques to interact with the system.

## Features

- **Mouse Control with Facial Gestures**: Control your mouse by blinking, moving your face, or other facial gestures.
- **Support for Multiple Detection Modes**: Four different mouse detection modes are available to optimize movement and usability.
- **Configuration Management**: The application reads and writes configuration parameters to a configuration file.
- **Real-time Webcam Image Display**: View webcam feed along with facial landmark detection.
- **Automatic Brightness Adjustment**: Brightness is automatically adjusted based on the lighting detected from the eyes' region.

## Requirements

To use the BigLinux Body Tracker, the following dependencies are required:

- **Python 3.6+**
- **OpenCV** (`cv2`) for image processing
- **Mediapipe** (`mediapipe`) for facial landmark detection
- **Numpy** (`numpy`) for numerical calculations
- **Tkinter** (`tkinter`) for tooltips
- **Pynput** (`pynput`) for mouse control
- **Pillow** (`PIL`) for image processing
- **Matplotlib** (Optional, for plotting blink data)

You can install the dependencies using:

```sh
pip install opencv-python mediapipe numpy pynput Pillow matplotlib
```

## Installation

On BigLinux, simply install the `biglinux-body-tracker` package.

For other distributions:

Download the release file from the repository. The `.tar.gz` version needs to be extracted, and then run the `big_head_tracker` file. This is the recommended method since it ensures faster startup.

Alternatively, you can use `big-head-tracker.run` which doesn't require extraction, but it takes longer to start.

### Development Installation

To install for development purposes, clone the repository:

```sh
git clone https://github.com/yourusername/biglinux-body-tracker.git
cd biglinux-body-tracker/usr/share/biglinux/body-tracker
./install_pip_deps.sh [options]
```

You may need to install `tk` with:

```sh
sudo pacman -S tk
```
or
```sh
sudo apt install tk
```

### Compatibility

- Works on **Xorg** for all desktop environments, with better quality installing **xinput** and **xdotool**.
- For **Wayland**, improve quality on **KDE Plasma**, installing `kdotool` from [kdotool GitHub repository](https://github.com/jinliu/kdotool).

## Usage

To run the program, execute:

```sh
./run.sh [options]
```

### Command-line Arguments

The program accepts several command-line arguments to customize its behavior. Below are some important options:

- `--view [0|1|2]`: Show webcam image (`0` - no display, `1` - webcam view, `2` - avatar mode)
- `--mouseDetectionMode [1|2|3|4]`: Mouse detection mode (`1` to `4`)
- `--enableLeftEye [True|False]`: Enable left eye blink detection
- `--enableRightEye [True|False]`: Enable right eye blink detection
- `--webcamx [int]`: Webcam X resolution (default `1024`)
- `--webcamy [int]`: Webcam Y resolution (default `768`)
- `--fps [int]`: Frames per second (default `15`)

Example command:

```sh
python body_tracker.py --view 1 --mouseDetectionMode 2 --enableLeftEye True
```

## Configuration

The application saves configuration files in `~/.config/biglinux-body-tracker/config.conf`. Parameters can be modified by editing the configuration file or passing them as command-line arguments.

### Example Configuration File

```ini
[General]
view = 1
mouseDetectionMode = 2
enableLeftEye = True
enableRightEye = False
```

## Facial Landmarks

The facial landmarks are detected using MediaPipe's Face Mesh. Specific landmarks such as the eyes and mouth are used to track blinking or other gestures to control mouse actions like click, double-click, and drag.

### Facial Landmarks Reference

There are **468 landmark points** across the entire face. For detailed information and images of the landmark positions, please visit the following link:

[Augmented Face Mesh Indices](https://github.com/ManuelTS/augmentedFaceMeshIndices)

#### Lips
- **Points**: 61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 185, 40, 39, 37, 0, 267, 269, 270, 409, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 191, 80, 81, 82, 13, 312, 311, 310, 415
- **Upper Outer**: [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
- **Lower Outer**: [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
- **Upper Inner**: [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
- **Lower Inner**: [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

#### Left Eye
- **Points**: 33, 7, 163, 144, 145, 153, 154, 155, 133, 246, 161, 160, 159, 158, 157, 173
- **Upper0**: [466, 388, 387, 386, 385, 384, 398]
- **Lower0**: [263, 249, 390, 373, 374, 380, 381, 382, 362]
- **Upper1**: [467, 260, 259, 257, 258, 286, 414]
- **Lower1**: [359, 255, 339, 254, 253, 252, 256, 341, 463]
- **Upper2**: [342, 445, 444, 443, 442, 441, 413]
- **Lower2**: [446, 261, 448, 449, 450, 451, 452, 453, 464]
- **Lower3**: [372, 340, 346, 347, 348, 349, 350, 357, 465]
- **Eyebrow Upper**: [383, 300, 293, 334, 296, 336, 285, 417]
- **Eyebrow Lower**: [265, 353, 276, 283, 282, 295]
- **Iris**: [468, 469, 470, 471, 472]
  - **Center Point**: 468
  - **Right Point**: 469
  - **Top Point**: 470
  - **Left Point**: 471
  - **Bottom Point**: 472

#### Right Eye
- **Points**: 263, 249, 390, 373, 374, 380, 381, 382, 362, 466, 388, 387, 386, 385, 384, 398
- **Upper0**: [246, 161, 160, 159, 158, 157, 173]
- **Lower0**: [33, 7, 163, 144, 145, 153, 154, 155, 133]
- **Upper1**: [247, 30, 29, 27, 28, 56, 190]
- **Lower1**: [130, 25, 110, 24, 23, 22, 26, 112, 243]
- **Upper2**: [113, 225, 224, 223, 222, 221, 189]
- **Lower2**: [226, 31, 228, 229, 230, 231, 232, 233, 244]
- **Lower3**: [143, 111, 117, 118, 119, 120, 121, 128, 245]
- **Eyebrow Upper**: [156, 70, 63, 105, 66, 107, 55, 193]
- **Eyebrow Lower**: [35, 124, 46, 53, 52, 65]
- **Iris**: [473, 474, 475, 476, 477]
  - **Center Point**: 473
  - **Right Point**: 474
  - **Top Point**: 475
  - **Left Point**: 476
  - **Bottom Point**: 477

#### Face Oval
- **Points**: 10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10

## Mouse Control Modes

- **Mode 1**: Controls the mouse by tracking the facial position changes (basic movements).
- **Mode 2**: Utilizes more advanced gestures to control mouse behavior.
- **Mode 3**: Uses facial angles for precise movement tracking.
- **Mode 4**: Combines different inputs for enhanced control.

## License

This project is licensed under the [GPLv3 License](LICENSE).

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue to discuss improvements or suggest new features.

## Acknowledgments

This project uses [MediaPipe](https://github.com/google/mediapipe) for facial tracking, [OpenCV](https://opencv.org/) for image processing, and [Pynput](https://github.com/moses-palmer/pynput) for mouse control. Many thanks to the open-source community!

## Contact

If you have any questions or suggestions, feel free to contact us through the GitHub Issues page.

---

Enjoy using **BigLinux Body Tracker** and help make technology more accessible to everyone!
