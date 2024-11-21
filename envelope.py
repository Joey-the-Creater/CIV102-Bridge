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
p_train = [400 / 6]*6

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
for train_position in range(-51,292):
    shear_force, bending_moment = calculate_shear_force_and_bending_moment(train_position)
    for i in range(1201):
        max_bending_moment[i] = max(max_bending_moment[i], bending_moment[i])
    for i in range(1201):
        if abs(shear_force[i])>abs(max_shear_force[i]):
            max_shear_force[i] = shear_force[i]
    if abs(max_bending_moment[556]-69260)<=0.01:
        print(train_position)
# Plotting envelope functions
plt.figure(figsize=(12, 6))
# Plotting maximum shear force envelope
x_pos=[i for i in range(x_end + 1)]
plt.subplot(2, 1, 1)
plt.plot([0]+x_pos+[1200], [0]+max_shear_force+[0])
plt.title('Maximum Shear Force Envelope')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Shear Force (N)')
plt.grid(True)
# Plotting maximum bending moment envelope
plt.subplot(2, 1, 2)
plt.plot(range(x_end + 1), max_bending_moment)
plt.title('Maximum Bending Moment Envelope')
plt.xlabel('Position along the bridge (mm)')
plt.ylabel('Bending Moment (Nmm)')
plt.grid(True)
# Marking the highest shear force on the graph
max_shear_force_value = max(max_shear_force, key=abs)
max_shear_force_position = max_shear_force.index(max_shear_force_value)
plt.subplot(2, 1, 1)
plt.plot(max_shear_force_position, max_shear_force_value, 'ro')
plt.text(max_shear_force_position, max_shear_force_value, f'({max_shear_force_position}, {max_shear_force_value})')
# Marking the highest bending moment on the graph
max_bending_moment_value = max(max_bending_moment)
max_bending_moment_position = max_bending_moment.index(max_bending_moment_value)
plt.subplot(2, 1, 2)
plt.plot(max_bending_moment_position, max_bending_moment_value, 'ro')
plt.text(max_bending_moment_position, max_bending_moment_value, f'({max_bending_moment_position}, {max_bending_moment_value})')
plt.tight_layout()
plt.show()