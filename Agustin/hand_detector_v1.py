# me - this DAT
# scriptOp - the OP which is cooking
#script 3 center of mass

import numpy as np
import cv2


# press 'Setup Parameters' in the OP to call this function to re-create the parameters.
def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('Custom')
	p = page.appendTOP('Image', label='Video image')
	# how large a conotur has to be to be considered a hand
	p = page.appendFloat('Minarea', label='Min Area')
	p.default = 20
	p.min = 0.0
	# how close to the edge the hand has to be to be considered a touch
	p = page.appendFloat('Threstouch', label='Touch Threshold')
	p.default = 5
	p.min = 0.0
	return

# called whenever custom pulse parameter is pushed
def onPulse(par):
	return

def onCook(scriptOp):
	scriptOp.clear()
	active_image = scriptOp.par.Image.eval().numpyArray(delayed=True)
	min_area = scriptOp.par.Minarea.eval()
	touch_thres = scriptOp.par.Threstouch.eval()
	
	tx = scriptOp.appendChan('hands:x')
	tz = scriptOp.appendChan('hands:z')

	x_coord = []
	z_coord = []
	
	active_image *= 255
	active_image = active_image.astype('uint8')
	gray = cv2.cvtColor(active_image, cv2.COLOR_RGBA2GRAY)

	blurred = cv2.GaussianBlur(gray, (9, 9), 0)
	_, thresholded = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)
	contours, _ = cv2.findContours(thresholded, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	for i, contour in enumerate(contours):
		area = cv2.contourArea(contour)
		x, y, width, height = cv2.boundingRect(contour)
		if area > min_area and y <= touch_thres:
			mask = np.zeros_like(gray)
			cv2.drawContours(mask, [contour], -1, 255, -1)
			contour_pixels = gray[mask == 255]
			x_coord.append(x + width / 2)
			z_coord.append(contour_pixels.mean()/255)
			# print(f"mid_x: {mid_x}, average pixel value: {round(contour_pixels.mean(),2)}, min_y: {min_y}, max_y: {max_y}")

	# order pairs from left to right
	pairs = list(zip(x_coord, z_coord))
	pairs.sort()
	x_coord, z_coord = zip(*pairs)

	tx.vals = x_coord
	tz.vals = z_coord
	scriptOp.numSamples = len(x_coord)
	
	return
