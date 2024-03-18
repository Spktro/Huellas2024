# me - this DAT
# scriptOp - the OP which is cooking
# min and max values that the horizontal value can take
# press 'Setup Parameters' in the OP to call this function to re-create the parameters.

# for a 60deg fov, the horizontal value is 2*height*tan(30deg), which is 2*height*0.57735
TAN_ANGLE = 0.57735

def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('Custom')
	p = page.appendFloat('Resx', label='Image X resolution')
	p.default = 256
	# kinect position from lower left of screen.
	p = page.appendFloat('Kinectpos', label='Kinect position WxH (mts)', size=2)
	p.default = (0.9, 2.7)
	p = page.appendFloat('Minmaxgray', label='Min Max Gray values (0-1)', size=2)
	p.default = (0.104, 0.1958)
	p = page.appendFloat('Minmaxheight', label='Min Max Height values (mts)', size=2)
	p.default = (1, 2)
	p = page.appendFloat('Multvalue', label='X and Y multiplier', size=2)
	p.default = (1.09, 1.75)
	
	return

# called whenever custom pulse parameter is pushed
def onPulse(par):
	return

def onCook(scriptOp):
	scriptOp.clear()
	chop_input = scriptOp.inputs[0]
	max_x_value = scriptOp.par.Resx.eval()
	minmax_gray_values = scriptOp.parGroup.Minmaxgray.eval()
	minmax_height_values = scriptOp.parGroup.Minmaxheight.eval()
	mult_xy_values = scriptOp.parGroup.Multvalue.eval()
	kinect_pos = scriptOp.parGroup.Kinectpos.eval()
	
	# make linear function to convert gray values to height values, by using min gray value as min height value and max gray value as max height value
	slope = (minmax_height_values[1] - minmax_height_values[0]) / (minmax_gray_values[1] - minmax_gray_values[0])
	intercept = minmax_height_values[0] - slope * minmax_gray_values[0]
	# print(f"Slope: {slope}, Intercept: {intercept}")


	x_index_values = chop_input.chan(0).numpyArray()
	pix_values = chop_input.chan(1).numpyArray()
	has_hand = x_index_values[0] >0
	if has_hand:
		print(f"X values: {x_index_values}, Pixel values: {pix_values}")
	# convert pixel values to height values
		height_coords_in_mts = pix_values*slope + intercept

		# using height and x_index values, calculate the horizontal value
		width_ratio = x_index_values / max_x_value*2 - 1
		max_with_for_depth = height_coords_in_mts*TAN_ANGLE
		width_coords_in_mts = max_with_for_depth*width_ratio
		
		print(f"Pos in mts in ref to kinect, Width: {width_coords_in_mts}, Height: {height_coords_in_mts}")

		width_coords_in_mts = kinect_pos[0] - width_coords_in_mts*mult_xy_values[0]
		height_coords_in_mts = kinect_pos[1] + height_coords_in_mts*mult_xy_values[1]
		
		print(f"Pos in mts in ref to world, Width: {width_coords_in_mts}, Height: {height_coords_in_mts}")
		width_coords_channel = width_coords_in_mts
		height_coord_channel = height_coords_in_mts
	else:
		width_coords_channel = [-10]
		height_coord_channel = [-10]

	tx = scriptOp.appendChan('hands:width')
	ty = scriptOp.appendChan('hands:height')
	tx.vals = width_coords_channel
	ty.vals = height_coord_channel
	scriptOp.numSamples = len(width_coords_channel)

	return
