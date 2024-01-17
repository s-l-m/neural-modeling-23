import pygame
import sys
import random
import math
import numpy as np
import matplotlib.pyplot as plt

# Game parameters
SCREEN_X, SCREEN_Y = 3024, 1964 # your screen resolution
WIDTH, HEIGHT = SCREEN_X // 1.5  , SCREEN_Y // 1.5 # be aware of monitor scaling on windows (150%)
CIRCLE_SIZE = 20
TARGET_SIZE = CIRCLE_SIZE
TARGET_RADIUS = 300
MASK_RADIUS = 0.75 * TARGET_RADIUS
ATTEMPTS_LIMIT = 120
START_POSITION = (WIDTH // 2, HEIGHT // 2)
START_ANGLE = 0
PERTUBATION_ANGLE= 30
TIME_LIMIT = 1000 # time limit in ms

GRADUAL_PERT_ATT_NO = 10
SUDDEN_PERT_ATT_NO = 80

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
score = 0
attempts = 0
new_target = None
start_time = 0

new_target = None
start_target=math.radians(START_ANGLE)
move_faster = False 
clock = pygame.time.Clock()

# Initialize game modes
mask_mode= True
target_mode = 'fix'  # Mode for angular shift of target: random, fix, dynamic
pertubation_mode= False
pertubation_type= 'sudden' # Mode for angular shift of control: random, gradual or sudden
perturbation_angle = math.radians(PERTUBATION_ANGLE)  # Angle between mouse_pos and circle_pos

error_angles = []  # List to store error angles


# Function to generate a new target position
def generate_target_position():
    if target_mode == 'random':
        angle = random.uniform(0, 2 * math.pi)

    elif target_mode == 'fix':   
        angle=start_target;  

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
    if attempts == 1:
        pertubation_mode = False
    elif attempts == GRADUAL_PERT_ATT_NO:
       pertubation_mode = True
       pertubation_type = 'gradual' 
    elif attempts == 60:
        pertubation_mode = False
    elif attempts == SUDDEN_PERT_ATT_NO:
        pertubation_mode = True    
        pertubation_type = 'sudden'         
    elif attempts == 100:
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
            k = (attempts - GRADUAL_PERT_ATT_NO) // 5 + 1
            pert_angle = -perturbation_angle/10 * k
            
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Pert_angle: {math.degrees(pert_angle)}", True, WHITE)
        screen.blit(score_text, (1000, 200))

        perturbed_mouse_pos = [ 
            np.cos(pert_angle)*deltax + -np.sin(pert_angle)*deltay + START_POSITION[0],
            np.sin(-pert_angle)*deltax + np.cos(-pert_angle)*deltay + START_POSITION[1]
        ]
            
        circle_pos = perturbed_mouse_pos
    
    else:
        circle_pos = pygame.mouse.get_pos()
    
    # Check if target is hit or missed
    # hit if circle touches target's center
    if check_target_reached():
        score += 1
        attempts += 1
        new_target = None  # Set target to None to indicate hit
        
        start_time = 0  # Reset start_time after hitting the target

        # CALCULATE AND SAVE ERRORS between target and circle end position for a hit
        error_angle = np.arcsin(deltax/distance) - pert_angle
        if not move_faster:
            error_angles.append(np.degrees(error_angle))
        else: 
            error_angles.append(np.nan)

    #miss if player leaves the target_radius + 1% tolerance
    elif new_target and math.hypot(circle_pos[0] - START_POSITION[0], circle_pos[1] - START_POSITION[1]) > TARGET_RADIUS*1.01:
        attempts += 1
        new_target = None  # Set target to None to indicate miss
        start_time = 0  # Reset start_time after missing the target

        # CALCULATE AND SAVE ERRORS between target and circle end position for a miss
        error_angle = np.arcsin(deltax/distance) - pert_angle
        
        if not move_faster:
            error_angles.append(np.degrees(error_angle))
        else:
            error_angles.append(np.nan)

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
## TASK 2, CALCULATE, PLOT AND SAVE ERRORS from error_angles
error_array = np.array(error_angles)

min_error = np.nanmin(error_array)
max_error = np.nanmax(error_array)

errors_unpert = error_angles[0:GRADUAL_PERT_ATT_NO]
errors_gradpert = error_angles[GRADUAL_PERT_ATT_NO:60]
errors_unpert_2 = error_angles[60:SUDDEN_PERT_ATT_NO]
errors_suddpert = error_angles[SUDDEN_PERT_ATT_NO:100]
errors_unpert_3 = error_angles[100:120]

plt.plot(error_angles, 'ro--')
plt.vlines([GRADUAL_PERT_ATT_NO, 60, SUDDEN_PERT_ATT_NO, 100, 120], min_error, max_error)
plt.hlines(np.nanmean(errors_unpert), 0, GRADUAL_PERT_ATT_NO, colors='g', linestyles='dashed')
plt.hlines(np.nanmean(errors_gradpert), GRADUAL_PERT_ATT_NO, 60, colors='g', linestyles='dashed')
plt.hlines(np.nanmean(errors_unpert_2), 60, SUDDEN_PERT_ATT_NO, colors='g', linestyles='dashed')
plt.hlines(np.nanmean(errors_suddpert), SUDDEN_PERT_ATT_NO, 100, colors='g', linestyles='dashed')
plt.hlines(np.nanmean(errors_unpert_3), 100, 120, colors='g', linestyles='dashed')
plt.ylabel('Error angle (degrees)')
plt.xlabel('#Attempt')
plt.grid()
plt.show()

sys.exit()