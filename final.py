import numpy as np
import matplotlib.pyplot as plt

compressive_strength = 30
tensile_strength = 6
shear_strength_matboard = 4
young = 4000
poisson = 0.2
shear_strength_cemant = 2
x_train = [52, 228, 392, 568, 732, 908]
x_start = 0
x_end = 1200
p_train = [182 / 2, 182 / 2, 135 / 2, 135 / 2, 135 / 2, 135 / 2]

# Function to calculate shear force and bending moment at a given train position
def calculate_shear_force_and_bending_moment(train_position):
    real_x_train = [i + train_position for i in x_train]
    start_moment = sum(real_x_train[i] * p_train[i] for i in range(6))
    end_p = start_moment / 1200
    start_p = sum(p_train) - end_p
    shear_all=[0]*1201
    # Shear force calculation
    shear_force = [start_p]
    shear_positions = [0]
    for i in range(6):
        shear_force.append(shear_force[-1] - p_train[i])
        shear_positions.append(real_x_train[i])
    shear_force.append(0)
    shear_positions.append(1200)
    for pos in range(1201):
        if pos < real_x_train[0]:
            shear_all[pos] = start_p
        elif pos >= real_x_train[-1]:
            shear_all[pos] = -end_p
        else:
            for j in range(5):
                if real_x_train[j] <= pos < real_x_train[j + 1]:
                    shear_all[pos] = shear_force[j + 1]
                    break
    # Bending moment calculation
    bending_moment = [0]*1201
    for i in range(1,1200):
        bending_moment[i]=bending_moment[i-1]+shear_all[i]

    return shear_all, bending_moment

# Initialize envelope functions
max_shear_force = [0 for x in range(x_end + 1)]
max_bending_moment = [0 for x in range(x_end + 1)]

# Calculate envelope functions
for train_position in range(-52,292):
    shear_force, bending_moment = calculate_shear_force_and_bending_moment(train_position)
    for i in range(1201):
        max_bending_moment[i] = max(max_bending_moment[i], bending_moment[i])
    for i in range(1201):
        if abs(shear_force[i])>abs(max_shear_force[i]):
            max_shear_force[i] = shear_force[i]
def check_failure(component,pos):
    rectangle=cross_section(component,pos)
    flexural_stress(rectangle,pos)
    pass
def flexural_stress(rectangles,pos)：
    I=second_moment_of_area(rectangles)
    height=0
    stress_at_top=max_bending_moment[pos]*(75+1.27-height)/I
    stress_at_bottom=max_bending_moment[pos]*(height)/I
    if stress_at_top>compressive_strength:
        print(f"Top of the beam at {pos}mm in compression fail")
    if stress_at_bottom>tensile_strength:
        print(f"Bottom of the beam at {pos}mm in tension fail")
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
def cross_section(component, position):
    """
    Find the cross-section rectangle at a given position along the bridge.
    
    Parameters:
    component (list of tuples): List of components, each defined by (x, y, width, height, start_pos, end_pos).
    position (float): Position along the bridge.
    
    Returns:
    list of tuples: List of rectangles at the given position.
    """
    cross_section_rectangles = []
    
    for (x, y, width, height, start_pos, end_pos) in component:
        if start_pos <= position <= end_pos:
            cross_section_rectangles.append((x, y, width, height))
    
    return cross_section_rectangles
#x_pos,y_pos,width,height,starting pos along the bridge, ending pos along the bridge
component = [(10, 0, 80, 1.27,0,1200), (10, 1.27, 1.27, 75-1.27,0,1200), 
                (90-1.27, 1.27, 1.27, 75-1.27,0,1200),(0,75,100,1.27,0,1200),
                (10+1.27,75-1.27,5,1.270,1200),(90-1.27-5,75-1.27,5,1.27,0,1200)]
centroid = centroid_of_rectangles(rectangles)
print(f"Centroid of the rectangles is at: {centroid}mm")
I = second_moment_of_area(rectangles)
print(f"Second moment of area of the rectangles is: {I/(10**6)} 10e6 mm^4")
print(f"Flexural Stress at the top: {max(bending_moment)*(75+1.27-centroid)/I}MPa",f"Flexural Stress at the bottom: {max(bending_moment)*(centroid)/I}MPa")
#N mm*mm/mm^4