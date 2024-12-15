import numpy as np 
import cv2 
from matplotlib import pyplot as plt 

# Load the left and right images 
# in gray scale 
imgLeft = cv2.imread('image_l.png', 
					0) 
imgRight = cv2.imread('image_r.png', 
					0) 

# Detect the SIFT key points and 
# compute the descriptors for the 
# two images 
sift = cv2.xfeatures2d.SIFT_create() 
keyPointsLeft, descriptorsLeft = sift.detectAndCompute(imgLeft, 
													None) 

keyPointsRight, descriptorsRight = sift.detectAndCompute(imgRight, 
														None) 

# Create FLANN matcher object 
FLANN_INDEX_KDTREE = 0
indexParams = dict(algorithm=FLANN_INDEX_KDTREE, 
				trees=5) 
searchParams = dict(checks=50) 
flann = cv2.FlannBasedMatcher(indexParams, 
							searchParams) 


# Apply ratio test 
goodMatches = [] 
ptsLeft = [] 
ptsRight = [] 

for m, n in matches: 
	
	if m.distance < 0.8 * n.distance: 
		
		goodMatches.append([m]) 
		ptsLeft.append(keyPointsLeft[m.trainIdx].pt) 
		ptsRight.append(keyPointsRight[n.trainIdx].pt) 

		
ptsLeft = np.int32(ptsLeft) 
ptsRight = np.int32(ptsRight) 
F, mask = cv2.findFundamentalMat(ptsLeft, 
								ptsRight, 
								cv2.FM_LMEDS) 

# We select only inlier points 
ptsLeft = ptsLeft[mask.ravel() == 1] 
ptsRight = ptsRight[mask.ravel() == 1] 
