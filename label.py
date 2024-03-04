import argparse
import os
from ImageLabel import ImageLabel
from constant import LABELS

if __name__ == "__main__":
    # python label.py --path data/Chandrapur --label dense-plume
    
    parser = argparse.ArgumentParser(description='Label the plume')
    parser.add_argument('--path', type=str, help='Path to the image folder')
    parser.add_argument('--label', type=str, help='label type', choices=LABELS)
    parser.add_argument('--shape', type=str, help='shape type', default='drawing', choices=['box', 'drawing'])
    
    args = parser.parse_args()
    path = args.path
    label = args.label
    shape = args.shape
    
    os.makedirs(os.path.join(path,'masks', label), exist_ok=True)
    
    s = 0
    for image in os.listdir(os.path.join(path, 'images')):    
        x = ImageLabel(path, image, label, shape)
        if os.path.exists(x.mask_path):
            continue
        x.show_loop()
        s+=1
        if s == 10:
            break




