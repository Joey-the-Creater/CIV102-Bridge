
import numpy as np
import matplotlib.pyplot as plt

x_train = [52, 228, 392, 568, 732, 908]
x_start = 0
x_end = 1200
p_train = [182 / 2, 182 / 2, 135 / 2, 135 / 2, 135 / 2, 135 / 2]
real_x_train = [i + 120 for i in x_train]

start_moment = sum(real_x_train[i] * p_train[i] for i in range(6))
end_p = start_moment / 1200
start_p = 452 - end_p

# Shear force calculation
shear_force = [0, start_p]
for i in range(6):
    shear_force.append(shear_force[-1] - p_train[i])
shear_force.append(0)
print(shear_force)
# Bending moment calculation
bending_moment = [0]
for i in range(6):
    bending_moment.append(bending_moment[-1] + shear_force[i + 1] * (real_x_train[i] - (real_x_train[i - 1] if i > 0 else 0)))
    print(bending_moment[-1])
bending_moment.append(0)

# Convert bending moment to 10^4 Nmm
bending_moment = [bm / 10000 for bm in bending_moment]

# Plotting shear force diagram
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.step([0, x_start] + real_x_train + [x_end], shear_force, where='post')
plt.title('Shear Force Diagram')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Shear Force (N)')
plt.grid(True)

# Annotate shear force values
for i, (x, y) in enumerate(zip([0, x_start] + real_x_train + [x_end], shear_force)):
    plt.text(x, y, f'{y:.2f}', fontsize=8, verticalalignment='bottom')

# Plotting bending moment diagram
plt.subplot(2, 1, 2)
plt.plot([0] + real_x_train + [x_end], bending_moment)
plt.title('Bending Moment Diagram')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Bending Moment (10^4 Nmm)')
plt.grid(True)

# Annotate bending moment values
for i, (x, y) in enumerate(zip([0] + real_x_train + [x_end], bending_moment)):
    plt.text(x, y, f'{y:.2f}', fontsize=8, verticalalignment='bottom')

plt.tight_layout()
plt.show()


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
        I_total += I_rect + area * dy**2

    return I_total
rectangles = [(10, 0, 80, 1.27), (10, 1.27, 1.27, 75-1.27), (90-1.27, 1.27, 1.27, 75-1.27),(0,75,100,1.27),(10+1.27,75-1.27,5,1.27),(90-1.27-5,75-1.27,5,1.27)]
centroid = centroid_of_rectangles(rectangles)
print(f"Centroid of the rectangles is at: {centroid}")
I = second_moment_of_area(rectangles)/(10**6)
print(f"Second moment of area of the rectangles is: {I}10e6 mm^4")
print(max(bending_moment)*(75+1.27-centroid)/I,max(bending_moment)*(centroid)/I)