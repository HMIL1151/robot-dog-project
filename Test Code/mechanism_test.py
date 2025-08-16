import math
import pygame
import helper

pygame.init()

grid_color = (100, 100, 100)

screen_width = 600
screen_height = 400

servo_distance = 46
thigh_length = 40
calf_length = 150

servo_height = 100
foot_radius = 4

def from_screen_coords(coords):
    x, y = coords
    return (x - screen_width/2, y - servo_height)

def to_screen_coords(coords):
    x, y = coords
    return (x + screen_width/2, y + servo_height)
servo1_coords = (-servo_distance/2, 0)
servo2_coords = (servo_distance/2, 0)

servo1_screen_coords = to_screen_coords(servo1_coords)
servo2_screen_coords = to_screen_coords(servo2_coords)

foot_coords = (0, 150)
foot_display_coords = to_screen_coords(foot_coords)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mechanism Test")

# --- BEGIN: Workspace Map Calculation ---
workspace_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
for x in range(-screen_width, screen_width, 2):
    for y in range(0, screen_height, 2):
        foot_coords = (x, y)
        foot_circle = (foot_coords, calf_length)
        thigh_circle_1 = (servo1_coords, thigh_length)
        thigh_circle_2 = (servo2_coords, thigh_length)
        servo1_intersection_coords = helper.intersection_between_circles(foot_circle, thigh_circle_1)
        servo2_intersection_coords = helper.intersection_between_circles(foot_circle, thigh_circle_2)
        if servo1_intersection_coords and servo2_intersection_coords:
            screen_coords = to_screen_coords(foot_coords)
            workspace_surface.set_at((int(screen_coords[0]), int(screen_coords[1])), (0, 100, 255, 80))
# --- END: Workspace Map Calculation ---

running = True
dragging = False

while running:
    last_mouse_coords = 0, 0
    screen.fill((30, 30, 30))

    # Draw vertical lines
    for x in range(0, screen_width, 10):
        pygame.draw.line(screen, grid_color, (x, 0), (x, screen_height))

    # Draw horizontal lines
    for y in range(0, screen_height, 10):
        pygame.draw.line(screen, grid_color, (0, y), (screen_width, y))

    pygame.draw.circle(screen, (255, 0, 0), servo1_screen_coords, 4)
    pygame.draw.circle(screen, (255, 0, 0), servo2_screen_coords, 4)
    pygame.draw.circle(screen, (255, 0, 0), servo1_screen_coords, thigh_length, 1)
    pygame.draw.circle(screen, (255, 0, 0), servo2_screen_coords, thigh_length, 1)

    thigh_circle_1 = (from_screen_coords(servo1_screen_coords), thigh_length)
    thigh_circle_2 = (from_screen_coords(servo2_screen_coords), thigh_length)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            dist = math.hypot(mouse_x - foot_display_coords[0], mouse_y - foot_display_coords[1])
            if dist < foot_radius:
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            last_mouse_coords = mouse_x, mouse_y
            mouse_x, mouse_y = event.pos
            foot_display_coords = (mouse_x, mouse_y)
            foot_coords = from_screen_coords(foot_display_coords)

    
    

    foot_circle = (from_screen_coords(foot_display_coords), calf_length)

    servo1_intersection_coords = helper.intersection_between_circles(foot_circle, thigh_circle_1)
    servo2_intersection_coords = helper.intersection_between_circles(foot_circle, thigh_circle_2)

    if len(servo1_intersection_coords) == 0 or len(servo2_intersection_coords) == 0:
        mouse_x, mouse_y = last_mouse_coords
        foot_display_coords = (mouse_x, mouse_y)
        foot_coords = from_screen_coords(foot_display_coords)

    if servo1_intersection_coords and servo2_intersection_coords:

        servo1_intersection_angles = (
            helper.clockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[0]),
            helper.clockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[1])
        )
        servo2_intersection_angles = (
            helper.clockwise_angle_between_two_lines(servo2_coords, foot_coords, servo2_intersection_coords[0]),
            helper.clockwise_angle_between_two_lines(servo2_coords, foot_coords, servo2_intersection_coords[1])
        )

        if servo1_intersection_angles[0] < 180:
            servo1_intersection_point = servo1_intersection_coords[1]
        else:
            servo1_intersection_point = servo1_intersection_coords[0]

        if servo2_intersection_angles[0] < 180:
            servo2_intersection_point = servo2_intersection_coords[0]
        else:
            servo2_intersection_point = servo2_intersection_coords[1]


        servo1_angle = helper.counterclockwise_angle_between_two_lines(servo2_coords, servo1_intersection_point, servo1_coords)
        servo2_angle = helper.clockwise_angle_between_two_lines(servo1_coords, servo2_intersection_point, servo2_coords)

        pygame.draw.line(screen, (255, 0, 0), to_screen_coords(servo1_intersection_point), foot_display_coords, 2)
        pygame.draw.line(screen, (255, 0, 0), to_screen_coords(servo2_intersection_point), foot_display_coords, 2)

        pygame.draw.line(screen, (0, 255, 0), servo1_screen_coords, to_screen_coords(servo1_intersection_point), 2)
        pygame.draw.line(screen, (0, 255, 0), servo2_screen_coords, to_screen_coords(servo2_intersection_point), 2)

        print("Servo 1 Angle:", servo1_angle, "Servo 2 Angle:", servo2_angle)

    pygame.draw.circle(screen, (0, 255, 0), foot_display_coords, foot_radius)
    pygame.draw.circle(screen, (0, 255, 0), foot_display_coords, calf_length, 1)

    screen.blit(workspace_surface, (0, 0))




    
    #print("Counterclockwise Angles for Servo 1: ", helper.counterclockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[0]), " ", helper.counterclockwise_angle_between_two_lines(servo1_coords, foot_coords, servo1_intersection_coords[1]))

    #print("Foot Coordinates:", from_screen_coords(foot_display_coords))


    pygame.display.flip()


pygame.quit()
