import socket
import pygame
import pickle

WIDTH, HEIGHT = 600, 400
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

host_y = HEIGHT // 2
client_y = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host_ip = "192.168.1.42"  # 🔁 Substitua pelo IP real do host
sock.connect((host_ip, 5555))
sock.setblocking(False)

def draw():
    win.fill((0, 0, 0))
    pygame.draw.rect(win, (255, 255, 255), (20, host_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.rect(win, (100, 100, 255), (WIDTH - 30, client_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.ellipse(win, (255, 255, 255), (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    pygame.display.flip()

run = True

while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and client_y > 0:
        client_y -= 5
    if keys[pygame.K_DOWN] and client_y < HEIGHT - PADDLE_HEIGHT:
        client_y += 5

    try:
        sock.send(pickle.dumps(client_y))
    except:
        pass

    try:
        data = sock.recv(1024)
        host_y, ball_x, ball_y = pickle.loads(data)
    except BlockingIOError:
        pass

    draw()

pygame.quit()
