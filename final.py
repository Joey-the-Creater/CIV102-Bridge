import numpy as np
import matplotlib.pyplot as plt
import math

compressive_strength = 6
tensile_strength = 30
shear_strength_matboard = 4
young = 4000
poisson = 0.2
shear_strength_cemant = 2
x_train = [52, 228, 392, 568, 732, 908]
x_start = 0
x_end = 1200
p_train = [400/6]*6
FOS_tension=100
FOS_compression=100
FOS_shear_plate=100
FOS_glue=100
FOS_buck_1=100
FOS_buck_2=100
FOS_buck_3=100
FOS_buck_4=100
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
    for i in range(1,1201):
        bending_moment[i]=bending_moment[i-1]+shear_all[i-1]

    return shear_all, bending_moment

# Initialize envelope functions
max_shear_force = [0 for x in range(x_end + 1)]
max_bending_moment = [0 for x in range(x_end + 1)]
# Calculate envelope functions
for train_position in range(-52,293):
    shear_force, bending_moment = calculate_shear_force_and_bending_moment(train_position)
    for i in range(1201):
        max_bending_moment[i] = max(max_bending_moment[i], bending_moment[i])
    for i in range(1201):
        if abs(shear_force[i])>abs(max_shear_force[i]):
            max_shear_force[i] = shear_force[i]
print(max(max_bending_moment),max(max_shear_force))
def local_buckling_stress(b, t, boundary_condition):
    k=0
    if boundary_condition == 'type 1':
        k = 4.0
    elif boundary_condition == 'type 2':
        k = 0.425
    elif boundary_condition == 'type 3':
        k = 6
    sigma_cr = (k * (math.pi ** 2) * young) / (12 * (1 - poisson ** 2)) * ((t / b) ** 2)
    return sigma_cr

def check_failure(component,pos):
    rectangle=cross_section(component,pos)
    flexural_stress_failure(rectangle,pos)
    shear_stress_failure(rectangle,pos)
    pass
def find_glued_joint(rectangles):
    glued_joints = []
    y_pos=[]
    for (x, y, width, height) in rectangles:
        y_pos.append(y+height)
    for y in y_pos:
        for i in range(len(rectangles)-1):
            for j in range(i+1,len(rectangles)):
                if (rectangles[i][1]+rectangles[i][3]==y and rectangles[j][1]==y) or (rectangles[i][1]==y and rectangles[j][1]+rectangles[j][3]==y):
                    glued_joints.append(y)
    return [75]
def find_width_at_a_given_height(rectangles,height):
    width_up=0
    width_down=0
    for i in range(len(rectangles)):
        if rectangles[i][1]+rectangles[i][3]==height:
            width_up+=rectangles[i][2]
        if rectangles[i][1]==height:
            width_down+=rectangles[i][2]
    return min(width_up,width_down)

def first_moment_of_area(rectangles, h):
    centroid_y = centroid_of_rectangles(rectangles)
    first_moment = 0

    for (x, y, width, height) in rectangles:
        area = width * height
        cy = y + height / 2
        if y + height <= h:
            first_moment += area * (centroid_y-cy)
        else:
            if y<h and y+height>h:
                new_height=h-y
                first_moment += width*new_height * (centroid_y-(y+new_height / 2))
    return first_moment
def shear_stress_failure(rectangles,crit_pos,V):
    global FOS_shear_plate,FOS_glue
    V=abs(V)
    for y in crit_pos:
        Q=first_moment_of_area(rectangles,y)
        b=find_width_at_a_given_height(rectangles,y)
        I=second_moment_of_area(rectangles)
        shear=V*Q/(I*b)
        FOS_glue=min(FOS_glue,shear_strength_cemant/shear)
        if shear>shear_strength_cemant:
            print(f"Beam at {y}mm in shear fail at glue")
    cy=centroid_of_rectangles(rectangles)
    Q=first_moment_of_area(rectangles,cy)
    b=0
    for i in range(len(rectangles)):
        if rectangles[i][1]<cy and rectangles[i][1]+rectangles[i][3]>cy:
            b+=rectangles[i][2]
    I=second_moment_of_area(rectangles)
    shear=V*Q/(I*b)
    FOS_shear_plate=min(FOS_shear_plate,shear_strength_matboard/shear)
    #if shear>shear_strength_matboard:
    #    print(f"Beam at {y}mm in shear fail at centroid")

def flexural_stress_failure(rectangles,pos):
    global FOS_tension,FOS_compression
    global strength_buck_1,strength_buck_2,strength_buck_3
    global FOS_buck_1,FOS_buck_2,FOS_buck_3
    I=second_moment_of_area(rectangles)
    height=centroid_of_rectangles(rectangles)
    stress_at_top=abs(max_bending_moment[pos]*(75+1.27-height)/I)
    stress_at_bottom=abs(max_bending_moment[pos]*(height)/I)
    #print(f"Flexural Stress at the top: {stress_at_top}MPa",f"Flexural Stress at the bottom: {stress_at_bottom}MPa")
    try:
        FOS_tension=min(FOS_tension,compressive_strength/stress_at_top)
    except:
        FOS_tension=FOS_tension
    try:
        FOS_compression=min(FOS_compression,tensile_strength/stress_at_bottom)
    except:
        FOS_compression=FOS_compression
    try:
        FOS_buck_1=min(FOS_buck_1,strength_buck_1/stress_at_top)
    except:
        FOS_buck_1=FOS_buck_1
    try:
        FOS_buck_2=min(FOS_buck_2,strength_buck_2/stress_at_top)
    except:
        FOS_buck_2=FOS_buck_2
    try:
        FOS_buck_3=min(FOS_buck_3,strength_buck_3/abs(max_bending_moment[pos]*(75-height)/I))
    except:
        FOS_buck_3=FOS_buck_3
    #if stress_at_top>compressive_strength:
    #    print(f"Top of the beam at {pos}mm in compression fail")
    #if stress_at_bottom>tensile_strength:
    #    print(f"Bottom of the beam at {pos}mm in tension fail")
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
def check_failure(component):
    global strength_buck_1,strength_buck_2,strength_buck_3
    for pos in range(0,1200):
        rectangle=cross_section(component,pos)
        flexural_stress_failure(rectangle,pos)
        crit_pos=find_glued_joint(rectangle) #for glue
        shear_stress_failure(rectangle,crit_pos,max_shear_force[pos])
#x_pos,y_pos,width,height,starting pos along the bridge, ending pos along the bridge
component = [(10, 0, 80, 1.27,0,1200), (10, 1.27, 1.27, 75-1.27,0,1200), 
                (90-1.27, 1.27, 1.27, 75-1.27,0,1200),(0,75,100,1.27,0,1200),
                (10+1.27,75-1.27,5,1.27,0,1200),(90-1.27-5,75-1.27,5,1.27,0,1200)]
cy=centroid_of_rectangles(cross_section(component,0))
strength_buck_1=local_buckling_stress(77.46,1.27,'type 1')
strength_buck_2=local_buckling_stress(10,1.27,'type 2')
strength_buck_3=local_buckling_stress(75-cy,1.27,'type 3')
check_failure(component)
print(f"Second moment of area: {second_moment_of_area(cross_section(component,0))}")
print(f"FOS for tension: {FOS_tension}")
print(f"FOS for compression: {FOS_compression}")
print(f"FOS for shear at plate: {FOS_shear_plate}")
print(f"FOS for shear at glue: {FOS_glue}")
print(f"Strength of buckling type 1: {strength_buck_1}MPa",
          f"Strength of buckling type 2: {strength_buck_2}MPa",
          f"Strength of buckling type 3: {strength_buck_3}MPa")
print(f"FOS for buckling type 1: {FOS_buck_1}")
print(f"FOS for buckling type 2: {FOS_buck_2}")
print(f"FOS for buckling type 3: {FOS_buck_3}")
print(f"First Moment of Area at centroid: {first_moment_of_area(cross_section(component,0),cy)}")
print(f"First Moment of Area at 75mm: {first_moment_of_area(cross_section(component,0),75)}")