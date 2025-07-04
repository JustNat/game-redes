import socket
import threading
import pygame
import struct
import os
from dotenv import load_dotenv

load_dotenv()

host_port = int(os.getenv('PORT'))

WIDTH, HEIGHT = 1200, 800
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10
BALL_SPEED = 4

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

host_y = HEIGHT // 2
client_y = HEIGHT // 2

def reset_ball():
    return WIDTH // 2, HEIGHT // 2, -BALL_SPEED, BALL_SPEED

ball_x, ball_y, ball_dx, ball_dy = reset_ball()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", host_port))
sock.setblocking(False)

client_addr = None

def listen_client():
    global client_y, client_addr
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data:
                # client envia posição do paddle (int)
                (client_y_recv,) = struct.unpack('i', data)
                client_y = client_y_recv
                client_addr = addr
        except BlockingIOError:
            pass
        except Exception as e:
            print("Erro no recv:", e)

threading.Thread(target=listen_client, daemon=True).start()

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
    if keys[pygame.K_w] and host_y > 0:
        host_y -= 5
    if keys[pygame.K_s] and host_y < HEIGHT - PADDLE_HEIGHT:
        host_y += 5

    # Atualiza bola
    ball_x += ball_dx
    ball_y += ball_dy

    # Colisão com teto e chão
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_dy *= -1

    # Colisão com host paddle
    if ball_x <= 30 + PADDLE_WIDTH and host_y <= ball_y <= host_y + PADDLE_HEIGHT:
        ball_dx *= -1

    # Colisão com client paddle
    if ball_x + BALL_SIZE >= WIDTH - 40 and client_y <= ball_y <= client_y + PADDLE_HEIGHT:
        ball_dx *= -1

    # Reinicia bola se passar das bordas
    if ball_x < 0 or ball_x > WIDTH:
        ball_x, ball_y, ball_dx, ball_dy = reset_ball()

    # Envia estado para client: host_y (int), ball_x (float), ball_y (float)
    if client_addr:
        packet = struct.pack('i ff', host_y, ball_x, ball_y)
        try:
            sock.sendto(packet, client_addr)
        except Exception as e:
            print("Erro no sendto:", e)

    draw()

pygame.quit()
