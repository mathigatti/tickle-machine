import cv2
import cv2.aruco as aruco

import numpy as np

def find_aruco_markers(image_path, aruco_dict_type=aruco.DICT_4X4_100, show=False):
    """
    Detects ArUco markers in an image and returns their bounding boxes.

    Parameters:
        image_path (str): Path to the input image.
        aruco_dict_type (int): Type of ArUco dictionary to use (default is DICT_6X6_250).

    Returns:
        list: A list of bounding boxes for each detected marker.
              Each bounding box is a list of 4 corner points.
    """
    # Load the input image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to load image from {image_path}")
        return []

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the ArUco dictionary and detector parameters
    aruco_dict = aruco.getPredefinedDictionary(aruco_dict_type)
    parameters = aruco.DetectorParameters()

    # Detect ArUco markers in the image
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, _ = detector.detectMarkers(gray)
    
    for i, id in enumerate(ids):
        print(id, corners[i])

    if show:
        if ids is not None:
            # Draw the detected markers and bounding boxes on the image
            for i in range(len(ids)):
                cv2.polylines(image, [np.int32(corners[i])], True, (0, 255, 0), 2)
            
            # Display the image with bounding boxes
            cv2.imshow("Detected ArUco Markers", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Return bounding boxes as a list of 4 corner points
            return [corner[0].tolist() for corner in corners]
        else:
            print("No ArUco markers detected.")
            return []
    
if __name__ == "__main__":
    # Path to the image
    import sys
    image_path = sys.argv[1]
    
    ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    }


    # Find ArUco markers in the image
    bounding_boxes = find_aruco_markers(image_path, ARUCO_DICT[sys.argv[2]])

    if bounding_boxes:
        print("Bounding boxes of detected markers:")
        for box in bounding_boxes:
            print(box)
