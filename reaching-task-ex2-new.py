import pygame
import sys
import random
import math
import numpy as np
import matplotlib.pyplot as plt

# Game parameters
SCREEN_X, SCREEN_Y = 2560,1600 # your screen resolution
WIDTH, HEIGHT = SCREEN_X // 1  , SCREEN_Y // 1#WIDTH, HEIGHT = SCREEN_X // 1.5  , SCREEN_Y // 1.5 # be aware of monitor scaling on windows (150%)
CIRCLE_SIZE = 20
TARGET_SIZE = CIRCLE_SIZE
TARGET_RADIUS = 300
MASK_RADIUS = 0.75 * TARGET_RADIUS

START_POSITION = (WIDTH // 2, HEIGHT // 2)
START_ANGLES = [0, 30, 120, -110]
PERTUBATION_ANGLE = 30
MOUSE_PERTUBATION_ANGLE = 30
TIME_LIMIT = 1000 # time limit in ms
INTERFERENCE_ANGLE = -45

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Reaching Game")

# Initialize game metrics
test_mode = True
score = 0
attempts = 0
new_target = None
start_time = 0
exp_setup = 'interference_b1' 

if exp_setup == 'baseline':
    pertubations = [' sudden \n perturbation', ' no \n perturbation', ' sudden \n perturbation', ' no \n perturbation']
    START_ANGLE = START_ANGLES[0]

    if test_mode:
        timestamps_changes = [1,5,10,15,20,25]
        timestamps_changes_full = [0,5,10,15,20,25]
    else: 
        timestamps_changes = [1,40,80,120,160,200]
        timestamps_changes_full = [0,40,80,120,160,200]

elif exp_setup == 'interference_b1' or exp_setup == 'interference_b2':
    pertubations = ['sudden \n perturbation', 'no \n perturbation', 'no \n perturbation',  'interference', 'no \n perturbation', 'no \n perturbation',  'sudden \n perturbation', 'no \n perturbation']
    
    if test_mode:
        timestamps_changes = [1,5,10,15,20,25,30,35,40,45]
        timestamps_changes_full = [0,5,10,15,20,25,30,35,40,45]
    else: 
        timestamps_changes = [1,20,60,80,100,140,160,180,220,240]
        timestamps_changes_full = [0,20,60,80,100,140,160,180,220,240]


ATTEMPTS_LIMIT = timestamps_changes[len(timestamps_changes)-1]+1

new_target = None
start_target = 0
move_faster = False
clock = pygame.time.Clock()

# Initialize game modes
mask_mode = False
target_mode = 'fix'  # Mode for angular shift of target: random, fix, dynamic
pertubation_mode = False
pertubation_type = 'sudden' # Mode for angular shift of control: random, gradual or sudden
perturbation_angle = math.radians(MOUSE_PERTUBATION_ANGLE)  # Angle between mouse_pos and circle_pos

error_angles = []  # List to store error angles
target_angles = []
perturbation_angles = []
circle_end_angles = []


def calculate_angle(centerX, centerY, targetX, targetY, pointX, pointY):
    # Calculate vectors
    v_CP = (pointX - centerX, pointY - centerY)
    v_CT = (targetX - centerX, targetY - centerY)


    # length
    l_CP = math.sqrt(v_CP[0]**2 + v_CP[1]**2)
    l_CT = math.sqrt(v_CT[0]**2 + v_CT[1]**2)

    # dot prod

    product_CP_CT = v_CP[0]*v_CT[0] + v_CP[1]*v_CT[1]


    # angle
    angle = math.acos(product_CP_CT/(l_CP*l_CT))
    
    # in deg
    angle_deg = math.degrees(angle)

    # rotation direction
    cross_product = v_CT[0]*v_CP[1] - v_CT[1]*v_CP[0]
    if cross_product < 0:
        angle_deg = angle_deg * (-1)


    return angle_deg

# Function to generate a new target position
def generate_target_position():
    if target_mode == 'random':
        angle = random.uniform(0, 2 * math.pi)

    elif target_mode == 'fix':
        angle = start_target

    new_target_x = WIDTH // 2 + TARGET_RADIUS * math.sin(angle)
    new_target_y = HEIGHT // 2 + TARGET_RADIUS * -math.cos(angle) # zero-angle at the top
    return [new_target_x, new_target_y]

# Function to check if the current target is reached
def check_target_reached():
    if new_target:
        distance = math.hypot(circle_pos[0] - new_target[0], circle_pos[1] - new_target[1])
        return distance <= CIRCLE_SIZE // 2
    return False

# Function to check if player is at starting position and generate new target
def at_start_position_and_generate_target(mouse_pos):
    distance = math.hypot(mouse_pos[0] - START_POSITION[0], mouse_pos[1] - START_POSITION[1])
    if distance <= CIRCLE_SIZE:
        return True
    return False

# Main game loop
running = True
show_end_position = False
while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Press 'esc' to close the experiment
                running = False
            elif event.key == pygame.K_4: # Press '4' to test pertubation_mode
                pertubation_mode = True
            elif event.key == pygame.K_5: # Press '5' to end pertubation_mode
                pertubation_mode = False
            
    # Design experiment
    
    if exp_setup == 'baseline': 
        if attempts == 1:
            pertubation_mode = False
        elif attempts == timestamps_changes[1]:
            pertubation_mode = True
            pertubation_type = 'sudden'
        elif attempts == timestamps_changes[2]:
            pertubation_mode = False
        elif attempts == timestamps_changes[3]:
            pertubation_mode = True
            pertubation_type = 'sudden'
        elif attempts == timestamps_changes[4]:
            pertubation_mode = False
        elif attempts >= ATTEMPTS_LIMIT:
            running = False

    elif exp_setup == 'interference_b1': 
        start_target = math.radians(START_ANGLES[1])
        if attempts == 1:
            pertubation_mode = False
        elif attempts == timestamps_changes[1]:
            pertubation_mode = True
            pertubation_type = 'sudden'
            perturbation_angle = math.radians(PERTUBATION_ANGLE)
        elif attempts == timestamps_changes[2]:
            pertubation_mode = False
        elif attempts == timestamps_changes[3]:
            pertubation_mode = False
        elif attempts == timestamps_changes[4]:
            pertubation_mode = True
            pertubation_type = 'sudden'
            perturbation_angle = math.radians(INTERFERENCE_ANGLE)
        elif attempts == timestamps_changes[5]:
            pertubation_mode = False
        elif attempts == timestamps_changes[6]:
            pertubation_mode = False
        elif attempts == timestamps_changes[7]:
            pertubation_mode = True
            pertubation_type = 'sudden'
            perturbation_angle = math.radians(PERTUBATION_ANGLE)
        elif attempts == timestamps_changes[8]:
            pertubation_mode = False
        elif attempts >= ATTEMPTS_LIMIT:
            running = False
    
    elif exp_setup == 'interference_b2': 
        if attempts == 0:
            start_target = math.radians(START_ANGLES[2])
            pertubation_mode = False
        elif attempts == timestamps_changes[1]:
            pertubation_mode = True
            pertubation_type = 'sudden'
            perturbation_angle = math.radians(PERTUBATION_ANGLE)
        elif attempts == timestamps_changes[2]:
            pertubation_mode = False
        elif attempts == timestamps_changes[3]:
            start_target = math.radians(START_ANGLES[3])
            pertubation_mode = False
        elif attempts == timestamps_changes[4]:
            pertubation_mode = True
            pertubation_type = 'sudden'
            perturbation_angle = math.radians(INTERFERENCE_ANGLE)
        elif attempts == timestamps_changes[5]:
            pertubation_mode = False
        elif attempts == timestamps_changes[6]:
            start_target = math.radians(START_ANGLES[2])
            pertubation_mode = False
        elif attempts == timestamps_changes[7]:
            pertubation_mode = True
            pertubation_type = 'sudden'
            perturbation_angle = math.radians(PERTUBATION_ANGLE)
        elif attempts == timestamps_changes[8]:
            pertubation_mode = False
        elif attempts >= ATTEMPTS_LIMIT:
            running = False

    # Hide the mouse cursor
    pygame.mouse.set_visible(False)
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Calculate distance from START_POSITION to mouse_pos
    deltax = mouse_pos[0] - START_POSITION[0]
    deltay = mouse_pos[1] - START_POSITION[1]
    distance = math.hypot(deltax, deltay)
    
    pert_angle = 0

    if pertubation_mode:
        # TASK1: CALCULATE perturbed_mouse_pos
        if pertubation_type=='sudden':
            pert_angle = perturbation_angle
            
        elif pertubation_type=='gradual':
            k = (attempts - timestamps_changes[1]) // 5 + 1
            pert_angle = - perturbation_angle/10 * k
            
        #font = pygame.font.Font(None, 36)
        #score_text = font.render(f"Pert_angle: {math.degrees(pert_angle)}", True, WHITE)
        #screen.blit(score_text, (1000, 200))

        perturbed_mouse_pos = [
            np.cos(pert_angle)*deltax - np.sin(pert_angle)*deltay + START_POSITION[0],
            np.sin(pert_angle)*deltax + np.cos(pert_angle)*deltay + START_POSITION[1]
        ]
            
        circle_pos = perturbed_mouse_pos
    
    else:
        circle_pos = pygame.mouse.get_pos()

    
    # Check if target is hit or missed
    # hit if circle touches target's center
    if check_target_reached():
        score += 1
        attempts += 1
        targetX = new_target[0]
        targetY = new_target[1]
        new_target = None  # Set target to None to indicate hit
        
        start_time = 0  # Reset start_time after hitting the target

        # CALCULATE AND SAVE ERRORS between target and circle end position for a hit
        error_angle = calculate_angle(START_POSITION[0],START_POSITION[1],targetX,targetY,circle_pos[0],circle_pos[1])#np.arcsin((circle_pos[0] - START_POSITION[0])/distance)
        if not move_faster:
            error_angles.append((error_angle))
        else:
            error_angles.append(np.nan)
        
        perturbation_angles.append(math.degrees(pert_angle))
        target_angles.append(math.degrees(start_target))
        circle_end_angles.append(math.degrees(start_target + error_angle))

    #miss if player leaves the target_radius + 1% tolerance
    elif new_target and math.hypot(circle_pos[0] - START_POSITION[0], circle_pos[1] - START_POSITION[1]) > TARGET_RADIUS*1.01:

        targetX = new_target[0]
        targetY = new_target[1]
        attempts += 1
        new_target = None  # Set target to None to indicate miss
        start_time = 0  # Reset start_time after missing the target

        # CALCULATE AND SAVE ERRORS between target and circle end position for a miss
        error_angle = calculate_angle(START_POSITION[0],START_POSITION[1],targetX,targetY,circle_pos[0],circle_pos[1]) #np.arcsin((circle_pos[0] - START_POSITION[0])/distance)

        if not move_faster:
            error_angles.append((error_angle))
        else:
            error_angles.append(np.nan)
        
        perturbation_angles.append(math.degrees(pert_angle))
        target_angles.append(math.degrees(start_target))
        circle_end_angles.append(math.degrees(start_target + error_angle))

    # Check if player moved to the center and generate new target
    if not new_target and at_start_position_and_generate_target(mouse_pos):
        new_target = generate_target_position()
        move_faster = False
        start_time = pygame.time.get_ticks()  # Start the timer for the attempt

    # Check if time limit for the attempt is reached
    current_time = pygame.time.get_ticks()
    if start_time != 0 and (current_time - start_time) > TIME_LIMIT:
        move_faster = True
        start_time = 0  # Reset start_time
        
    # Show 'MOVE FASTER!'
    if move_faster:
        font = pygame.font.Font(None, 36)
        text = font.render('MOVE FASTER!', True, RED)
        text_rect = text.get_rect(center=(START_POSITION))
        screen.blit(text, text_rect)

# Generate playing field
    # Draw current target
    if new_target:
        pygame.draw.circle(screen, BLUE, new_target, TARGET_SIZE // 2)

    # Draw circle cursor
    if mask_mode:
        if distance < MASK_RADIUS:
            pygame.draw.circle(screen, WHITE, circle_pos, CIRCLE_SIZE // 2)
    else:
        pygame.draw.circle(screen, WHITE, circle_pos, CIRCLE_SIZE // 2)
    
    # Draw start position
    pygame.draw.circle(screen, WHITE, START_POSITION, 5)

    # Show score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Show attempts
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Attempts: {attempts}", True, WHITE)
    screen.blit(score_text, (10, 30))

    # Update display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()

print(error_angles)
print(target_angles)
print(perturbation_angles)
print(circle_end_angles)

data_array = np.array([error_angles, target_angles, perturbation_angles, circle_end_angles])

np.savetxt("task2.csv",data_array,delimiter =", ")

## TASK 2, CALCULATE, PLOT AND SAVE ERRORS from error_angles
error_angles = np.array(error_angles)
att_nr=np.linspace(0,len(error_angles),len(error_angles))
# points are connected between nan values
mask = np.isfinite(error_angles.astype(np.double))


timestamps_changes = np.array(timestamps_changes)

error_segments = []
mean_values = []
mov_var_list = []

# Loop to create segments and calculate mean error angle and movement variability

for i in range(len(timestamps_changes) - 1):

    start_index = int(timestamps_changes[i])
    end_index = int(timestamps_changes[i + 1])
    segment = error_angles[start_index:end_index]
    segment = np.array(segment)

    mean_value_seg = np.nanmean(segment)
    mov_var_seg = np.nanstd(segment)
    
    error_segments.append(segment)
    mean_values.append(mean_value_seg)
    mov_var_list.append(mov_var_seg)


for i, segment in enumerate(error_segments):
    print(f"Segment {i + 1}: {segment}")

for i, mean_value in enumerate(mean_values):
    print(f"Mean value for Segment {i + 1}: {mean_value}")

for i, mov_var in enumerate(mov_var_list):
    print(f"Movement Variability for Segment {i + 1}: {mov_var}")


plt.figure(figsize=(16,8))
plt.plot(att_nr[mask],error_angles[mask], linestyle = 'dashed')

plt.scatter(att_nr,error_angles)
plt.xlabel('#Attempt')
plt.ylabel('Error Angle (degrees)')
plt.xlim(0,ATTEMPTS_LIMIT)
plt.ylim(np.nanmin(error_angles)-1, np.nanmax(error_angles+5))
for change in range(1, len(timestamps_changes)-1):
    plt.axvline(x=timestamps_changes[change], color='red')
    plt.text(timestamps_changes[change], np.nanmax(error_angles)+4, pertubations[change -1], color = 'red',rotation=0, va='top')


for i, mean_value in enumerate(mean_values):
    plt.axhline(mean_value, color='green', linestyle='dotted', xmin=timestamps_changes_full[i] / len(att_nr), xmax=timestamps_changes_full[i + 1] / len(att_nr))
    plt.axhline(mean_value - mov_var_list[i], color='red', linestyle='dotted', xmin=timestamps_changes_full[i] / len(att_nr), xmax=timestamps_changes_full[i + 1] / len(att_nr))
    plt.axhline(mean_value + mov_var_list[i], color='red', linestyle='dotted', xmin=timestamps_changes_full[i] / len(att_nr), xmax=timestamps_changes_full[i + 1] / len(att_nr))

plt.savefig('reaching_task_graph_new.png')
plt.show()

sys.exit()
