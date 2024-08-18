import numpy as np
import matplotlib.pyplot as plt
import jpeglib
from jpeglib import DCTJPEG

def zz_index_8x8(i: int):
    """
    Calculates x and y index for zig-zag traversal for the i-th index for a 8x8 matrix
    
    Args:
    - i: index
    
    Returns: x and y index for zig-zag traversal for the i-th index
    """
    ROW_STARTS = [1,2,4,7,11,16,22,29,37,44,50,55,59,62,64,65]
    
    diagonal = 0
    for index, item in enumerate(ROW_STARTS):
        if not i >= item-1:
            diagonal = index-1
            break
        
    diagnoal_index = i-(ROW_STARTS[diagonal]-1)
        
    if diagonal%2 == 0:
        # upward diagnoal
        diagonal_start_x = diagonal if diagonal < 8 else 7
        diagonal_start_y = 0 if diagonal < 8 else diagonal-7
        return (diagonal_start_x - diagnoal_index, diagonal_start_y + diagnoal_index)
    else:
        # downward diagnoal
        diagonal_start_x = 0 if diagonal < 8 else diagonal-7
        diagonal_start_y = diagonal if diagonal < 8 else 7
        return (diagonal_start_x + diagnoal_index, diagonal_start_y - diagnoal_index)

def pce(img: jpeglib.DCTJPEG, dct_coefficient_range: range, max_dct_abs_value: int = 15):
    """
    Estimate the first quantization matrix for a double-compressed image.
    
    Args:
    - img: jpeglib image object
    
    Returns: Quantization matrix
    """
    
    # assure JPEG image has 64 coefficients per block
    assert np.prod(img.Y.shape[2:]) == 64, "Number of DCT coefficients per block has to be 64"
    
    # Create cropped version to sample from    
    img.write_dct("temp.jpeg")
    img_spatial = jpeglib.read_spatial("temp.jpeg")
    
    shape_spatial = img_spatial.spatial.shape
    assert shape_spatial[0] > 16 and shape_spatial[1] > 16, "Image is too small to be cropped and re-compressed"
    
    cropped_spatial = img_spatial.spatial[4:shape_spatial[0]-4,4:shape_spatial[1]-4,:]
    img_spatial_cropped = img_spatial
    img_spatial_cropped.spatial = cropped_spatial
    img_spatial_cropped.width-=8
    img_spatial_cropped.height-=8
    
    # Create img_0 (DCT coefficients sampled without compression)
    img_spatial_cropped.write_spatial("img_0.jpeg", qt=100)
    img_0 = jpeglib.read_dct("img_0.jpeg")
    
    # Create img_q2 (DCT coefficients sampled with only second compression)
    # img_spatial_cropped.write_spatial("img_q2.jpeg", qt=img.qt)
    # img_q2 = jpeglib.read_dct("img_q2.jpeg")
    
    max_quantization_step = 255
    q1 = np.full((8,8), np.nan)
    
    for dct_coefficient in dct_coefficient_range:
        # get coordinates for the DCT coefficient and the qt step
        x, y = zz_index_8x8(dct_coefficient)
        
        # calculate histogram for DCT coefficient in the original image
        img_Y_single_c_histogram, _ = np.histogram(img.Y[:,:,x,y], bins=np.arange(-max_dct_abs_value, max_dct_abs_value + 2) - 0.5)
        
        # get quantization step of the qt in the original image
        q2_i = img.qt[0][zz_index_8x8(dct_coefficient)]
        
        l_max = np.inf
        for i in range(max_quantization_step):
            q1_i = i+1 # quantization step is always >=1, index i starts from zero
                        
            # First quantization step
            # DCT coefficients in img_0 are int quantized form, but with quantization step 1
            c1_Y_single_c = np.round(img_0.Y[:,:,x,y] / q1_i).astype(int)
            c1_Y_single_c *= q1_i
            
            # TODO: introduce truncation errors
            
            # Second quantization step
            c2_Y_single_c = np.round(c1_Y_single_c / q2_i).astype(int)
            # do not multiply with q2 since the compared values are already quantized
            
            c2_Y_single_c_histogram, _ = np.histogram(c2_Y_single_c, bins=np.arange(-max_dct_abs_value, max_dct_abs_value + 2) - 0.5)
                        
            l = np.sum(abs(c2_Y_single_c_histogram-img_Y_single_c_histogram))
            if l < l_max:
                l_max = l
                q1[zz_index_8x8(dct_coefficient)]=q1_i
                w_histogram = c2_Y_single_c_histogram
         
        # TODO: print if debug is enabled        
        #print(f"DCT_coefficient: {dct_coefficient}; Q1: {q1[zz_index_8x8(dct_coefficient)]}, L: {l_max}")
        #print(img_Y_single_c_histogram)
        #print(w_histogram)
        
    return q1