import cv2

background = None

def run_avg(img, avgWeight):
    global background
    
    if background is None:
        # Initialize the background
        background = img.copy().astype("float")
        return
    
    # Compute the Weighted Average
    cv2.accumulateWeighted(img, background, avgWeight)

def segment(img, threshold=25):
    global background
    
    # Calculate absolute difference between background and current frame
    diff = cv2.absdiff(background.astype("uint8"), img)
    
    # Threshold the difference to obtain foreground
    thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
    
    # Obatin the contours in the thresholded image
    (cnts, _) = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Return None when no contours detected
    if len(cnts) == 0:
        return
    else:
        segmented = max(cnts, key=cv2.contourArea)
        return thresholded, segmented

def findEdge(segmented):
    # Initializing the variables
    max_x = 0
    max_y = 350
    left_x = 390
    right_x = 0
    min_y1 = 0
    min_y2 = 0
    for cor in segmented:
        # Taking each coordinates of the contour and comparing them
        x, y = cor[0]
        # To find the max point
        if (y < max_y):
            max_x = x
            max_y = y
        # To find the leftmost region
        if(x < left_x):
            left_x = x
            min_y1 = y
        # To find the rightmost region
        if(x > right_x):
            right_x = x
            min_y2 = y
    
    min_y = max((min_y1, min_y2))
    return max_x, max_y, left_x, right_x, min_y
