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