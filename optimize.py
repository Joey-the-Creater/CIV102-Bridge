def centroid_of_rectangles(rectangles):
    """
    Calculate the centroid of multiple rectangles.
    
    Parameters:
    rectangles (list of tuples): List of rectangles, each defined by (x, y, width, height).
    
    Returns:
    tuple: (x, y) coordinates of the centroid.
    """
    total_area = 0
    cy_total = 0

    for (x, y, width, height) in rectangles:
        area = width * height
        cy = y + height / 2
        total_area += area
        cy_total += cy * area

    centroid_y = cy_total / total_area

    return centroid_y
def second_moment_of_area(rectangles):
    """
    Calculate the second moment of area (I) for multiple rectangles.
    
    Parameters:
    rectangles (list of tuples): List of rectangles, each defined by (x, y, width, height).
    
    Returns:
    float: Second moment of area (I).
    """
    I_total = 0
    centroid_y = centroid_of_rectangles(rectangles)

    for (x, y, width, height) in rectangles:
        area = width * height
        cy = y + height / 2
        dy = cy - centroid_y
        I_rect = (width * height**3) / 12
        I_total += I_rect + area * dy**2 #parallel axis theorem

    return I_total
min_top=100
min_shape=None
min_height=100
min_bottom=100
min_area=650
for height in range(50,150):
    for bottom in range(10,100):
        rectangles=[(0,0,bottom,1.27),(50,1.27,1.27,height-1.27),(50,1.27,1.27,height-1.27),
                    (0,height-1.27,5,1.27), (0,height-1.27,5,1.27), (0,height,100,1.27),(0,height+1.27,100,1.27)]
        y=height+1.27-centroid_of_rectangles(rectangles)
        area=sum([width*height for x,y,width,height in rectangles])
        if area<600:
            if y/second_moment_of_area(rectangles)<min_top:
                min_top=y/second_moment_of_area(rectangles)
                min_shape=rectangles
                min_height=height
                min_bottom=bottom
                min_area=area
print(min_top)
print(min_shape)
print(min_height)
print(min_bottom)
print(min_area)
print(centroid_of_rectangles(min_shape))
print(second_moment_of_area(min_shape))