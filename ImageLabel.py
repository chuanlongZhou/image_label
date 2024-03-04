import cv2
import numpy as np
import os

LINEWIDTH = 1

def draw_and_close_shape(event, x, y, flags, param):
    image_obj = param["image_obj"]
    shape = param["shape"]
    img = image_obj.img
    
    if event == cv2.EVENT_LBUTTONDOWN:
        image_obj.drawing = True
        image_obj.current_points = [(x, y)] # Start a new shape

    elif event == cv2.EVENT_MOUSEMOVE and image_obj.drawing:
        # print("Drawing")
        if shape == "box":
            # Draw a box
            # cv2.rectangle(img, image_obj.current_points[0], (x, y), (0, 255, 0), LINEWIDTH)
            pass
        elif shape == "drawing":
            cv2.line(image_obj.img, image_obj.current_points[-1], (x, y), (0, 255, 0), LINEWIDTH)
            image_obj.current_points.append((x, y))

    elif event == cv2.EVENT_LBUTTONUP and image_obj.drawing:
        print("Close shape")
        image_obj.drawing = False
        
        if shape == "box":
            # Draw a box
            cv2.rectangle(img, image_obj.current_points[0], (x, y), (0, 255, 0), LINEWIDTH)
            # add the box to the list of polygons
            image_obj.polygons.append([image_obj.current_points[0], (x, image_obj.current_points[0][1]), (x, y), (image_obj.current_points[0][0], y)])

        elif shape == "drawing":
            # Close the shape and add it to the list of polygons
            cv2.line(image_obj.img, image_obj.current_points[-1], image_obj.current_points[0], (0, 255, 0), LINEWIDTH)
            image_obj.current_points.append(image_obj.current_points[0]) # Complete the loop
            
            # fill the polygon with green color
            # cv2.fillPoly(img, np.array([current_points]), (0,255,0))
            image_obj.polygons.append(image_obj.current_points)
            
        image_obj.current_points = [] # Reset points for the next shape

    elif event == cv2.EVENT_RBUTTONDOWN and image_obj.polygons:
        print("Undo")
        # Undo: Remove the last polygon and redraw the image
        image_obj.polygons.pop()
        print('current polygons: ', len(image_obj.polygons))
        
        image_obj.img = image_obj.load_image()
        
        for polygon in image_obj.polygons:
            for i in range(len(polygon)-1):
                cv2.line(image_obj.img, polygon[i], polygon[i+1], (0, 255, 0), LINEWIDTH)
                
    cv2.imshow(image_obj.window_name, img)
    
class ImageLabel:
    def __init__(self, path, window_name="Image", label="dense-plume", shape="box"):
        self.path = os.path.join(path, 'images', window_name)
        self.main_path = path
        self.mask_path = os.path.join(path, 'masks', label, window_name)
        self.label = label
        self.window_name = window_name
        self.img = self.load_image()
        
        # control drawing status
        self.shape = shape
        self.drawing = False
        self.points = [] # List to store points of the shape
        self.current_points = [] # List to store points of the current shape
        self.polygons = [] # List to store all polygons
    
    def load_image(self):
        return cv2.imread(self.path)
    
    def show_loop(self):
        # labeling loop
        window_name, img = self.window_name, self.img
        
        # Create a black image, a window and bind the function to window
        cv2.imshow(window_name, img)
        cv2.moveWindow(window_name, 500, 500)
        
        cv2.setMouseCallback(window_name, draw_and_close_shape, 
                             param={
                                 "image_obj": self,
                                 "shape": self.shape
                                 })

        while True:
            # Enter ESC to save the mask
            if cv2.waitKey(1) & 0xFF == 27:
                print('Save mask')
                # save current image to masks path
                img = self.img
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                for polygon in self.polygons:
                    cv2.fillPoly(mask, np.array([polygon]), (255))
                cv2.imwrite(self.mask_path, mask)
                # write the filename to txt file
                with open(os.path.join(self.main_path, f'{self.label}_labeled.txt'), 'a+') as f:
                    f.write(self.window_name + '\n')
                break
            
            # press 's' to skip the image
            if cv2.waitKey(1) & 0xFF == ord('s'):
                print('skip image')
                with open(os.path.join(self.main_path, f'{self.label}_skipped.txt'), 'a+') as f:
                    f.write(self.window_name + '\n')
                break
            
            # press 'Enter' to exit
            if cv2.waitKey(1) & 0xFF == 13:
                break

        cv2.destroyAllWindows()
