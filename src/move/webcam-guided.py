import cv2
import cv2.aruco as aruco
import numpy as np
from time import sleep

# Define a helper to append a line to coords.txt
def send_coord(coord):
    """
    coord is a tuple or list of 3 floats (tip, left, right).
    Example: (-5.,0.,+5.)
    """
    with open("coords.txt", "w") as f:
        # Convert the tuple to a string like (-5.0, 0.0, 5.0)
        f.write(f"({coord[0]},{coord[1]},{coord[2]})\n")

def coord_ready():
    with open("coords.txt", "r") as f:
        return len(f.read()) == 0

# Tolerances (tweak to your needs).
area_tolerance = 200
pos_tolerance = 20

def dynamic_step(error, min_step=1.0, max_step=50.0, factor=0.1):
    """
    Given some 'error' (distance from target in pixels, or difference in area),
    we scale that error by 'factor' to get a step value. 
    
    We then clamp that step between 'min_step' and 'max_step'.

    Returns the computed step (float).
    """
    step = error * factor
    step = max(min_step, min(step, max_step))
    return step

def move(area, position, target_area, target_position):
    """
    Moves the object closer to 'target_position' in the image plane and
    adjusts its distance (via its observed 'area') to approach 'target_area'.
    
    Instead of sending commands to motors directly, we append a 3D coordinate
    (tip, left_base, right_base) to a file called coords.txt. 
    
    Positive means giving rope; negative means taking rope.
    """

    # TODO: fix naming of variables and comments to make sense

    # Default "no move" instruction
    tip_move = 0.
    left_move = 0.
    right_move = 0.

    # Calculate differences
    area_diff = abs(area - target_area)
    diff_y    = abs(position[1] - target_position[1])  # referencing code that uses position[1] for "left-right"
    diff_x    = abs(position[0] - target_position[0])  # referencing code that uses position[0] for "front-back"

    # 1) Check if the object is at the desired "size" (area). 
    #    - If area < target_area: object is too far => pull all ropes (negative).
    #    - If area > target_area: object is too close => give all ropes (positive).
    if abs(area - target_area) > area_tolerance:
        step = dynamic_step(area_diff, min_step=1.0, max_step=20.0, factor=0.3)

        if area < target_area:
            # Pull from all motors
            tip_move   = -step
            left_move  = -step
            right_move = -step
        else:
            # Give rope from all motors
            tip_move   = +step
            left_move  = +step
            right_move = +step

    # 2) If the area is within tolerance, fix the X-position (left-right).
    #    - If current x < target x => object is too far left => 
    #      pull from right (negative) and let rope from left (positive).
    #    - If current x > target x => object is too far right => 
    #      pull from left (negative) and let rope from right (positive).
    elif abs(position[1] - target_position[1]) > pos_tolerance:
        step = dynamic_step(diff_y, min_step=1.0, max_step=15.0, factor=0.1)
        if position[1] < target_position[1]:
            # Move object to the right
            left_move  = -step
            right_move = +step
        else:
            # Move object to the left
            left_move  = +step
            right_move = -step

    # 3) Then fix the Y-position (front-back).
    #    - If y < target y => object is "above"/"up" => let rope from tip (positive).
    #    - If y > target y => object is "below"/"down" => pull rope from tip (negative).
    elif abs(position[0] - target_position[0]) > pos_tolerance:
        step = dynamic_step(diff_x, min_step=1.0, max_step=15.0, factor=0.2)
        if position[0] < target_position[0]:
            # Let rope (object moves down)
            tip_move = -step
        else:
            # Pull rope (object moves up)
            tip_move = +step

    # 4) If everything is within tolerance, we do nothing 
    #    (the moves remain (0,0,0)).

    # Finally, append the resulting coordinate
    move_coord = (tip_move, left_move, right_move)
    send_coord(move_coord)

def find_aruco_markers(frame, aruco_dict_type=aruco.DICT_4X4_100, show=True):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.getPredefinedDictionary(aruco_dict_type)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)

    if ids is not None:
        for i, id in enumerate(ids):
            x_min = int(min(corners[i][0][:, 0]))
            y_min = int(min(corners[i][0][:, 1]))
            width = int(max(corners[i][0][:, 0]) - x_min)
            height = int(max(corners[i][0][:, 1]) - y_min)
            area = width * height            

            if show:
                # Draw the detected markers and bounding boxes on the frame
                for i in range(len(ids)):
                    cv2.polylines(frame, [np.int32(corners[i])], True, (0, 255, 0), 2)

                # Display the frame with bounding boxes
                cv2.imshow("Detected ArUco Markers", frame)

            return { "position": (x_min, y_min), "width": width, "height": height, "area": area }

    else:
        print("No ArUco markers detected.")

if __name__ == "__main__":
    ARUCO_DICT = {
        "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
        "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
        "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
        "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
        "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    }
    selected_dict = ARUCO_DICT["DICT_4X4_100"]

    # Open the USB webcam (index 2)
    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("Error: Could not open USB webcam. Check the index.")
        exit()

    with open("coords.txt", "w") as f:
        # Convert the tuple to a string like (-5.0, 0.0, 5.0)
        f.write("")

    positions = [(239, 222, 1500), (300, 222, 2000), (300, 180, 1500), (239, 180, 2000)]
    i = 0
    target_position = positions[0]

    show = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame from webcam.")
            break

        data = find_aruco_markers(frame, aruco_dict_type=selected_dict, show=show)
        # Display the frame
        if show:
            cv2.imshow("Webcam Feed", frame)
        if data and coord_ready():
            area = data["area"]
            position = data["position"]

            print("target:", position + (area,))
            print("status:", target_position)
            print("\n")
            if (abs(area - target_position[-1]) < area_tolerance 
                and abs(target_position[0] - position[0]) < pos_tolerance 
                and abs(target_position[1] - position[1]) < pos_tolerance):
                print("Target reached!")
                i+=1
                target_position = positions[i%len(positions)]

            # Otherwise, keep moving
            move(area, position, target_position[-1], target_position[:2])
        else:
            sleep(1)

    cap.release()
    cv2.destroyAllWindows()
