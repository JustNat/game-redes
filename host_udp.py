import socket
import pygame
import pickle

WIDTH, HEIGHT = 1200, 800
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

host_y = HEIGHT // 2
client_y = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = -4, 4

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5555))
client_addr = None

def draw():
    win.fill((0, 0, 0))
    pygame.draw.rect(win, (255, 255, 255), (20, host_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(win, (100, 100, 255), (WIDTH - 30, client_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.ellipse(win, (255, 255, 255), (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    pygame.display.flip()

run = True
sock.setblocking(False)

while run:
    clock.tick(60)

    try:
        data, addr = sock.recvfrom(1024)
        client_y = pickle.loads(data)
        client_addr = addr
    except BlockingIOError:
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and host_y > 0:
        host_y -= 5
    if keys[pygame.K_s] and host_y < HEIGHT - PADDLE_HEIGHT:
        host_y += 5

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_dy *= -1

    if ball_x <= 30 and host_y < ball_y < host_y + PADDLE_HEIGHT:
        ball_dx *= -1
    if ball_x >= WIDTH - 40 and client_y < ball_y < client_y + PADDLE_HEIGHT:
        ball_dx *= -1

    if client_addr:
        game_state = pickle.dumps((host_y, ball_x, ball_y))
        sock.sendto(game_state, client_addr)

    draw()

pygame.quit()
