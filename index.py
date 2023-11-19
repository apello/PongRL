
import pygame

# Initialize module
pygame.init()

# Initial values
window_width,window_height=1000,600
window = pygame.display.set_mode((window_width,window_height))

# Colors
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)

# Set title
pygame.display.set_caption('Ping Pong Game')

font = pygame.font.Font(None, 32)
title = font.render("Ping Pong Game", True, WHITE, BLACK)
title_container = title.get_rect()
title_container.center = (window_width/2, 30)

# Game information
TOTAL_POINTS = 10
ai_points = 0
player_points = 0

# Set text
print(pygame.font.get_fonts())

# Pong ball information
ball_radius = 15
ball_location_x, ball_location_y = window_width/2-ball_radius, window_height/2-ball_radius

ball_vel_x, ball_vel_y = 7,7 # Speed of ball

# Pong paddle information
paddle_width, paddle_height = 20, 120
left_paddle_y = right_paddle_y = window_height/2 - paddle_height/2
left_paddle_x, right_paddle_x = 50-paddle_width/2,  window_width - paddle_width - 50
left_paddle_vel = right_paddle_vel = 0

# Main game loop
run = True
while run:

    # End game if either player or AI wins
    if ai_points == TOTAL_POINTS or player_points == TOTAL_POINTS:
        run = False

    # Refill background to clear previous movement
    window.fill(BLACK)

    # Add titles
    window.blit(title, title_container)


    # Create titles for point totals
    ai_points_title = font.render("AI: "+str(ai_points), True, WHITE, BLACK)
    ai_points_title_container = title.get_rect()
    ai_points_title_container.center = (100, 30)

    player_points_title = font.render("Player: "+str(player_points), True, WHITE, BLACK)
    player_points_title_container = title.get_rect()
    player_points_title_container.center = (window_width-20, 30)

    window.blit(ai_points_title, ai_points_title_container)
    window.blit(player_points_title, player_points_title_container)

    # Loop through stored user actions, i.e., user clicks
    for event in pygame.event.get():
        # End game when player closes window
        if event.type == pygame.QUIT:
            run = False
        # If user clicks up or down arrow key, change velocity of paddle
        elif event.type == pygame.KEYDOWN:
            # Up arrow key
            if event.key == pygame.K_UP:
                right_paddle_vel = -5
            # Down arrow key
            elif event.key == pygame.K_DOWN:
                right_paddle_vel = 5
            # W key
            elif event.key == pygame.K_w:
                left_paddle_vel = -5
            # S key
            elif event.key == pygame.K_s:
                left_paddle_vel = 5
                

        # Once user releases key, stop paddles
        if event.type == pygame.KEYUP:
            right_paddle_vel = 0
            left_paddle_vel = 0


    # Keep ball within window dimensions

    # If ball hits bottom of screen, bounce up
    if ball_location_y <= 0 + ball_radius or ball_location_y >= window_height - ball_radius:
        ball_vel_y *= -1

    # If ball hits left of screen, return to center of screen and go the other way
    if ball_location_x <= 0 + ball_radius:
        ball_location_x, ball_location_y = window_width/2-ball_radius, window_height/2-ball_radius
        ball_vel_x *= -1
        ball_vel_y *= -1

        player_points += 1


    # If ball hits right of screen, return to center of screen and go the other way
    if ball_location_x >= window_width - ball_radius:
        ball_location_x, ball_location_y = window_width/2-ball_radius, window_height/2-ball_radius
        ball_vel_x *= -1
        ball_vel_y *= -1

        ai_points += 1

    # Move ball 
    ball_location_x += ball_vel_x
    ball_location_y += ball_vel_y

    # Move paddle
    right_paddle_y += right_paddle_vel
    left_paddle_y += left_paddle_vel

    # Keep paddle within window dimensions
    if left_paddle_y >= window_height - paddle_height:
        left_paddle_y = window_height - paddle_height

    if left_paddle_y <= 0:
        left_paddle_y = 0

    if right_paddle_y >= window_height - paddle_height:
        right_paddle_y = window_height - paddle_height

    if right_paddle_y <= 0:
        right_paddle_y = 0

    # Paddle/Ball collisions
    if left_paddle_x <= ball_location_x <= left_paddle_x + paddle_width:
        if left_paddle_y <= ball_location_y <= left_paddle_y + paddle_height:
            ball_location_x = left_paddle_x + paddle_width
            ball_vel_x *= -1

    if right_paddle_x <= ball_location_x <= right_paddle_x + paddle_width:
        if right_paddle_y <= ball_location_y <= right_paddle_y + paddle_height:
            ball_location_x = right_paddle_x - paddle_width
            ball_vel_x *= -1



    # Draw pong ball and paddles
    pygame.draw.circle(window, BLUE, (ball_location_x, ball_location_y), ball_radius)
    pygame.draw.rect(window, WHITE, pygame.Rect(left_paddle_x, left_paddle_y, paddle_width, paddle_height))
    pygame.draw.rect(window, WHITE, pygame.Rect(right_paddle_x, right_paddle_y, paddle_width, paddle_height))

    pygame.display.update()




    



