import socket
import pygame
import struct
import threading
import os

load_dotenv()

WIDTH, HEIGHT = 1200, 800
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

host_ip = os.getenv('HOST_IP')
host_port = os.getenv('PORT')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)

client_y = HEIGHT // 2
host_y = HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2

def listen_host():
    global host_y, ball_x, ball_y
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data:
                host_y_recv, ball_x_recv, ball_y_recv = struct.unpack('i ff', data)
                host_y = host_y_recv
                ball_x = ball_x_recv
                ball_y = ball_y_recv
        except BlockingIOError:
            pass
        except Exception as e:
            print("Erro recv:", e)

threading.Thread(target=listen_host, daemon=True).start()

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

    packet = struct.pack('i', client_y)
    try:
        sock.sendto(packet, (host_ip, host_port))
    except Exception as e:
        print("Erro sendto:", e)

    draw()

pygame.quit()
