import cv2
import predict
import segmentation
import maction
import mouse

if __name__ == "__main__":
    # Initialize Running Average Weight
    avgWeight = 0.5

    cam = cv2.VideoCapture(0)
    
    # Co ordinates for Region of Interest
    T = 2
    B = 350
    R = 300
    L = 690
    
    # Initialize no. of frames
    frame_no = 0
    
    #Mouse Actions
    actions = [
        'None',
        'Left Mouse Button',
        'Cursor Move',
        'Right Mouse Button',
        'Middle Mouse Button',
        'None',
        'Scroll'
    ]
    
    while(True):
        # Get the current frame
        (_, frame) = cam.read()
        
        #Resize and flip the frame
        (height, width) = frame.shape[:2]
        ratio = width / height
        w = 700
        h = int(w / ratio)
        
        frame = cv2.resize(frame, (w, h))
        frame = cv2.flip(frame, 1)
        
        clone = frame.copy()
        
        # Get the region of interest
        roi = frame[T:B, R:L]
        
        #Convert the roi to grayscale and apply Gaussian blur
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(7, 7), 0)
        
        if (frame_no < 30):
            # Use the first 30 frames to set the background
            segmentation.run_avg(gray, avgWeight)
        else:
            # Segment the hand region
            hand = segmentation.segment(gray)
            
            # Check for segmentaion
            if hand is not None:
                # Get the thresholded image and the segmented region
                (thresholded, segmented) = hand
                
                # Draw the required COntour over the screen
                cv2.drawContours(clone, [segmented + (R, T)], -1, (0, 0, 255))
                
                # Find the max point as well as the leftmost and rightmost region of the contour
                max_x, max_y, left_x, right_x, min_y = segmentation.findEdge(segmented)
                cv2.circle(clone, (max_x + R, max_y + T), 3, (255, 0, 0), -1)
                
                # Cropping a square from thresholded image with the required Contiur 
                max_y_copy = max_y
                min_y = min_y + 70
                diff1 = min_y - max_y
                diff2 = right_x - left_x
                
                if(diff1 > diff2): 
                    right_x = right_x + int((diff1 - diff2) / 2)
                    left_x = left_x - int((diff1 - diff2) / 2)
                else:
                    min_y = min_y + (diff2 - diff1)
                
                if(max_y <= 0):
                    max_y = 1
                if(right_x <= 0):
                    right_x = 1
                if(left_x <= 0):
                    left_x = 1
                
                # Passing the cropped thresholded image into the neural network
                predicted_val, pList = predict.predict(thresholded[max_y:min_y, left_x:right_x])
                
                cv2.putText(clone, "Action: " + actions[predicted_val],(10, 480), cv2.FONT_HERSHEY_COMPLEX, 1, (10, 10, 10), 2, cv2.LINE_AA)
                cv2.putText(clone, "Cursor Position: " + str(mouse.get_position()),(10, 440), cv2.FONT_HERSHEY_COMPLEX, 1, (10, 10, 10), 2, cv2.LINE_AA)
                cv2.putText(clone, "Action: " + actions[predicted_val],(10, 480), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(clone, "Cursor Position: " + str(mouse.get_position()),(10, 440), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                
                # Visual representation of the thresholded and the cropped region
                cv2.rectangle(thresholded,(left_x, max_y), (right_x, min_y), 100)
                cv2.imshow("Thresholded Image", thresholded)
                
                # Mouse Action based on the predicted outcome
                maction.mouseAction(pList, max_x, max_y_copy)
            
         # Represent the Region of Interest
        cv2.rectangle(clone, (L, T), (R, B), (0, 255, 0), 2)
            
        frame_no += 1
            
        # Show a video output
        cv2.imshow("Video Output", clone)
            
        #End the loop when 'f' is pressed
        end = cv2.waitKey(1) & 0xFF
        if end == ord('f'):
            break
            
    cam.release()
    cv2.destroyAllWindows()