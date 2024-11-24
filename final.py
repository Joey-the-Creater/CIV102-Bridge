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
p_train = [135 / 2, 135 / 2, 135 / 2, 135 / 2,182 / 2, 182 / 2]
M_fail_tension=[0 for x in range(1201)]
M_fail_compression=[0 for x in range(1201)]
M_fail_buck=[0 for x in range(1201)]
V_fail_shear=[0 for x in range(1201)]
V_fail_glue=[0 for x in range(1201)]
V_fail_buck=[0 for x in range(1201)]
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
for train_position in range(-51,293):
    shear_force, bending_moment = calculate_shear_force_and_bending_moment(train_position)
    for i in range(1201):
        max_bending_moment[i] = max(max_bending_moment[i], bending_moment[i])
    for i in range(1201):
        if abs(shear_force[i])>abs(max_shear_force[i]):
            max_shear_force[i] = shear_force[i]
print(f"Max Bending Moment: {max(max_bending_moment)}",f"Max Shear Force: {min(max_shear_force)}" )
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
def shear_buckling_stress(a, h):
    tao_cr = (5* (math.pi**2) * young) / (12 * (1 - poisson ** 2))*((1.27/h)**2+(1.27/a)**2)
    return tao_cr

def first_moment_of_area(rectangles, h, verticel_glued_joints=None):
    centroid_y = centroid_of_rectangles(rectangles)
    first_moment = 0
    if verticel_glued_joints is None:
        for (x, y, width, height) in rectangles:
            area = width * height
            cy = y + height / 2
            if y + height <= h:
                first_moment += area * (centroid_y-cy)
            else:
                if y<h and y+height>h:
                    new_height=h-y
                    first_moment += width*new_height * (centroid_y-(y+new_height / 2))
    else:
        for (x, y, width, height) in verticel_glued_joints:
            area = width * height
            cy = y + height / 2
            first_moment += area * (centroid_y-cy)
    return first_moment
def shear_stress_failure(rectangles,hori_glue,vert_glue,V,pos):
    global FOS_shear_plate,FOS_glue, FOS_buck_4
    V=abs(V)
    I=second_moment_of_area(rectangles)
    for (y,b) in hori_glue:
        Q=first_moment_of_area(rectangles,y)
        shear=V*Q/(I*b)
        FOS_glue=min(FOS_glue,shear_strength_cemant/shear)
        if V_fail_glue[pos]==0:
            V_fail_glue[pos]=shear_strength_cemant/shear*V
        else:
            V_fail_glue[pos]=min(V_fail_glue[pos],shear_strength_cemant/shear*V)
        if shear>shear_strength_cemant:
            print(f"Beam at {y}mm in shear fail at glue")
    for (cross_sec,b) in vert_glue:
        Q=first_moment_of_area(rectangles,y,cross_sec)
        shear=V*Q/(I*b)
        FOS_glue=min(FOS_glue,shear_strength_cemant/shear)
        if V_fail_glue[pos]==0:
            V_fail_glue[pos]=shear_strength_cemant/shear*V
        else:
            V_fail_glue[pos]=min(V_fail_glue[pos],shear_strength_cemant/shear*V)
        if shear>shear_strength_cemant:
            print(f"Beam at {y}mm in shear fail at glue")
    cy=centroid_of_rectangles(rectangles)
    Q=first_moment_of_area(rectangles,cy)
    b=1.27*2
    I=second_moment_of_area(rectangles)
    shear=V*Q/(I*b)
    FOS_shear_plate=min(FOS_shear_plate,shear_strength_matboard/shear)
    V_fail_shear[pos]=shear_strength_matboard/shear*V
    for i in range(len(tao_shear_buck)):
        if pos<=diaphram_pos[i+1] and pos>=diaphram_pos[i]:
            tao_cr=tao_shear_buck[i]
            break
    FOS_buck_4=min(FOS_buck_4,tao_cr/shear)
    V_fail_buck[pos]=tao_cr/shear*V
    #if shear>shear_strength_matboard:
    #    print(f"Beam at {y}mm in shear fail at centroid")

def flexural_stress_failure(rectangles,pos):
    global FOS_tension,FOS_compression
    global strength_buck_1,strength_buck_2,strength_buck_3
    global FOS_buck_1,FOS_buck_2,FOS_buck_3
    I=second_moment_of_area(rectangles)
    cy=centroid_of_rectangles(rectangles)
    stress_at_top=abs(max_bending_moment[pos]*(height_of_bridge-cy)/I)
    stress_at_bottom=abs(max_bending_moment[pos]*(cy)/I)
    #print(f"Flexural Stress at the top: {stress_at_top}MPa",f"Flexural Stress at the bottom: {stress_at_bottom}MPa")
    try:
        FOS_tension=min(FOS_tension,tensile_strength/stress_at_bottom)
        M_fail_tension[pos]=tensile_strength/stress_at_bottom*max_bending_moment[pos]
    except:
        FOS_tension=FOS_tension
    try:
        FOS_compression=min(FOS_compression,compressive_strength/stress_at_top)
        M_fail_compression[pos]=compressive_strength/stress_at_top*max_bending_moment[pos]
    except:
        FOS_compression=FOS_compression
    try:
        FOS_buck_1=min(FOS_buck_1,strength_buck_1/stress_at_top)
        FOS_buck_2=min(FOS_buck_2,strength_buck_2/stress_at_top)
        FOS_buck_3=min(FOS_buck_3,strength_buck_3/stress_at_top)
        M_fail_buck[pos]=min(strength_buck_1/stress_at_top*max_bending_moment[pos],strength_buck_2/stress_at_top*max_bending_moment[pos],strength_buck_3/stress_at_top*max_bending_moment[pos])

    except:
        FOS_buck_1=FOS_buck_1
        FOS_buck_2=FOS_buck_2
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
    for pos in range(0,1200):
        rectangle=cross_section(component,pos)
        flexural_stress_failure(rectangle,pos)
        cross_sec_hori_glue=[]
        cross_sec_vert_glue=[]
        for (height, thickness, start_pos, end_pos) in hori_glued_joints:
            if start_pos <= pos <= end_pos:
                cross_sec_hori_glue.append((height, thickness))
        for (cross_sec, thickness, start_pos, end_pos) in vert_glued_joints:
            if start_pos <= pos <= end_pos:
                cross_sec_vert_glue.append((cross_sec,thickness))
        shear_stress_failure(rectangle,cross_sec_hori_glue,cross_sec_vert_glue,max_shear_force[pos],pos)
def cycle():
    max_FOS_compression=0
    def check(component):
        rectangle=cross_section(component,0)
        shear_max=max(max_shear_force)
        bending_max=max(max_bending_moment)
        cy=centroid_of_rectangles(rectangle)
        I=second_moment_of_area(rectangle)
        Q=first_moment_of_area(rectangle,cy)
        Q_top=first_moment_of_area(rectangle,height)
        Q_up=first_moment_of_area(rectangle,height+1.27)
        FOS_compression=compressive_strength/(bending_max*(height_of_bridge+1.27*2-cy)/I)
        FOS_tension=tensile_strength/(bending_max*(cy)/I)
        FOS_shear_plate=shear_strength_matboard/(shear_max*Q/(I*1.27*2))
        FOS_glue=shear_strength_cemant/(max([shear_max*Q_top/(I*(1.27+connection)*2),shear_max*Q_up/(I*bottom)]))
        FOS_buck_1=strength_buck_1/(bending_max*(height_of_bridge+1.27*2-cy)/I)
        FOS_buck_2=strength_buck_2/(bending_max*(height_of_bridge+1.27*2-cy)/I)
        FOS_buck_3=strength_buck_3/(bending_max*(height_of_bridge+1.27*2-cy)/I)
        FOS_buck_4=tao_shear_buck[0]/(shear_max*Q/(I*1.27*2))

        return FOS_tension,FOS_compression,FOS_shear_plate,FOS_glue,FOS_buck_1,FOS_buck_2,FOS_buck_3,FOS_buck_4
    for top in range(150,99,-1):
        print(top)
        for height in range(120,49,-1):
            for bottom in range(top-1,30,-1):
                for connection in range(10,2,-1):
                    FOS_tension=100
                    FOS_compression=100
                    FOS_shear_plate=100
                    FOS_glue=100
                    FOS_buck_1=100
                    FOS_buck_2=100
                    FOS_buck_3=100
                    FOS_buck_4=100
                    height_of_bridge=height+1.27*2
                    #x_pos,y_pos,width,height,starting pos along the bridge, ending pos along the bridge
                    component=[(0,0,bottom,1.27,0,1200),
                    (50,1.27,1.27,height-1.27,0,1200),
                    (50,1.27,1.27,height-1.27,0,1200),
                    (0,height-1.27,connection,1.27,0,1200), 
                    (0,height-1.27,connection,1.27,0,1200), 
                    (0,height,bottom,1.27,0,1200),
                    (0,height+1.27,top,1.27,0,1200)]
                    if sum([i[2]*i[3] for i in component]) > 600:
                        continue
                    #Height, thickness of the connection (The program can determine Q at the height, so we don't need to hard code the components that are in connection), 
                    # begining position along the bridge, ending position along the bridge
                    hori_glued_joints =[(height,(connection+1.27)*2,0,1200),(height+1.27,bottom,0,1200)]
                    #Cross-sectional component, thickness of the connection, begining position along the bridge, ending position along the bridge
                    vert_glued_joints = []

                    diaphram_pos=[0,200,400,800,1000,1200]
                    tao_shear_buck=[]
                    cy=centroid_of_rectangles(cross_section(component,0))
                    for i in range(len(diaphram_pos)-1):
                        tao_shear_buck.append(shear_buckling_stress(diaphram_pos[i+1]-diaphram_pos[i],height_of_bridge))
                    strength_buck_1=local_buckling_stress(bottom-1.27*2,1.27*2,'type 1')
                    strength_buck_2=local_buckling_stress((top-bottom)/2,1.27,'type 2')
                    strength_buck_3=local_buckling_stress(height-cy,1.27,'type 3')
                    FOS_tension,FOS_compression,FOS_shear_plate,FOS_glue,FOS_buck_1,FOS_buck_2,FOS_buck_3,FOS_buck_4=check(component)
                    max_FOS_compression=max(FOS_compression,max_FOS_compression)
                    if FOS_tension>2 and FOS_compression>2 and FOS_shear_plate>2 and FOS_glue>2 and FOS_buck_1>2 and FOS_buck_2>2 and FOS_buck_3>2 and FOS_buck_4>2:
                        print(f"Height: {height}mm",f"Bottom: {bottom}mm",f"Connection: {connection}mm")
                        print(f"Area: {sum([i[2]*i[3] for i in component])}mm^2")
                        print(f"Second moment of area: {second_moment_of_area(cross_section(component,0))}")
                        print(f"Strength of buckling type 1: {strength_buck_1}MPa")
                        print(f"Strength of buckling type 2: {strength_buck_2}MPa")
                        print(f"Strength of buckling type 3: {strength_buck_3}MPa")
                        print(f"Strength of shear buckling: {tao_shear_buck}MPa")
                        print(f"FOS for tension: {FOS_tension}")
                        print(f"FOS for compression: {FOS_compression}")
                        print(f"FOS for shear at plate: {FOS_shear_plate}")
                        print(f"FOS for shear at glue: {FOS_glue}")
                        print(f"FOS for buckling type 1: {FOS_buck_1}")
                        print(f"FOS for buckling type 2: {FOS_buck_2}")
                        print(f"FOS for buckling type 3: {FOS_buck_3}")
                        print(f"FOS for buckling type 4: {tao_shear_buck}MPa")
        print(max_FOS_compression)
            
top=100
min_FOS=0
min_shape=None  
cur_FOS=[]
cur_strength=[]
for height in range(200,59,-20):
    print(height)
    print(min_FOS)
    for bottom in range(top-1,40,-1):
        for connection in range(20,2,-1):
            FOS_tension=1000
            FOS_compression=1000
            FOS_shear_plate=1000
            FOS_glue=1000
            FOS_buck_1=1000
            FOS_buck_2=1000
            FOS_buck_3=1000
            FOS_buck_4=1000
            height_of_bridge=height+1.27*2
            #x_pos,y_pos,width,height,starting pos along the bridge, ending pos along the bridge
            component=[(0,0,bottom,1.27,0,1200),
            (50,1.27,1.27,height-1.27,0,1200),
            (50,1.27,1.27,height-1.27,0,1200),
            (0,height-1.27,connection,1.27,0,1200), 
            (0,height-1.27,connection,1.27,0,1200), 
            (0,height,bottom,1.27,0,1200),
            (0,height+1.27,top,1.27,0,1200)]
            if sum([i[2]*i[3] for i in component]) > 600 or sum([i[2]*i[3] for i in component]) < 595:
                continue
            else:
                #Height, thickness of the connection (The program can determine Q at the height, so we don't need to hard code the components that are in connection), 
                # begining position along the bridge, ending position along the bridge
                hori_glued_joints =[(height,(connection+1.27)*2,0,1200),(height+1.27,bottom,0,1200)]
                #Cross-sectional component, thickness of the connection, begining position along the bridge, ending position along the bridge
                vert_glued_joints = []

                diaphram_pos=[0,200,400,800,1000,1200]
                tao_shear_buck=[]
                cy=centroid_of_rectangles(cross_section(component,0))
                for i in range(len(diaphram_pos)-1):
                    tao_shear_buck.append(shear_buckling_stress(diaphram_pos[i+1]-diaphram_pos[i],height_of_bridge))
                strength_buck_1=local_buckling_stress(bottom-1.27*2,1.27*2,'type 1')
                strength_buck_2=local_buckling_stress((top-bottom)/2,1.27,'type 2')
                strength_buck_3=local_buckling_stress(height-cy,1.27,'type 3')
                check_failure(component)
                if min_FOS<min([FOS_tension,FOS_compression,FOS_shear_plate,FOS_glue,FOS_buck_1,FOS_buck_2,FOS_buck_3,FOS_buck_4]):
                    min_FOS=min([FOS_tension,FOS_compression,FOS_shear_plate,FOS_glue,FOS_buck_1,FOS_buck_2,FOS_buck_3,FOS_buck_4])
                    min_shape=component
                    cur_FOS=[FOS_tension,FOS_compression,FOS_shear_plate,FOS_glue,FOS_buck_1,FOS_buck_2,FOS_buck_3,FOS_buck_4]
                    cur_strength=[strength_buck_1,strength_buck_2,strength_buck_3,tao_shear_buck]
print(min_FOS)
print(min_shape)
print(sum([i[2]*i[3] for i in min_shape]))
print(cur_FOS)
print(cur_strength)
print(centroid_of_rectangles(cross_section(min_shape,0)))
print(second_moment_of_area(cross_section(min_shape,0)))
print(first_moment_of_area(cross_section(min_shape,0),centroid_of_rectangles(cross_section(min_shape,0))))
'''
plt.figure(figsize=(12, 18))

# Plot V_fail_shear
plt.subplot(3, 2, 1)
plt.plot(range(1201), V_fail_shear, label='V_fail_shear')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Shear Force (N)')
plt.title('Shear Force Failure Envelope (Shear)')
plt.legend()
plt.grid(True)

# Plot V_fail_glue
plt.subplot(3, 2, 2)
plt.plot(range(1201), V_fail_glue, label='V_fail_glue')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Shear Force (N)')
plt.title('Shear Force Failure Envelope (Glue)')
plt.legend()
plt.grid(True)

# Plot V_fail_buck
plt.subplot(3, 2, 3)
plt.plot(range(1201), V_fail_buck, label='V_fail_buck')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Shear Force (N)')
plt.title('Shear Force Failure Envelope (Buckling)')
plt.legend()
plt.grid(True)

# Plot M_fail_compression
plt.subplot(3, 2, 4)
plt.plot(range(1201), M_fail_compression, label='M_fail_compression')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Bending Moment (N-mm)')
plt.title('Bending Moment Failure Envelope (Compression)')
plt.legend()
plt.grid(True)

# Plot M_fail_tension
plt.subplot(3, 2, 5)
plt.plot(range(1201), M_fail_tension, label='M_fail_tension')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Bending Moment (N-mm)')
plt.title('Bending Moment Failure Envelope (Tension)')
plt.legend()
plt.grid(True)

# Plot M_fail_buck
plt.subplot(3, 2, 6)
plt.plot(range(1201), M_fail_buck, label='M_fail_buck')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Bending Moment (N-mm)')
plt.title('Bending Moment Failure Envelope (Buckling)')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
'''