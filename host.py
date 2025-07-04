import socket
import threading
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

conn = None

def handle_client():
    global client_y
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            client_y = pickle.loads(data)
        except:
            break

def start_server():
    global conn
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(1)
    print("Aguardando cliente...")
    conn, addr = server.accept()
    print("Cliente conectado:", addr)
    threading.Thread(target=handle_client, daemon=True).start()
 
start_server()

print('Entrando no menu')
menu_active = True
while menu_active:
    clock.tick(60)
    win.fill((20, 20, 20))
    font = pygame.font.SysFont("Arial", 28)
    msg1 = font.render("Cliente conectado!", True, (255, 255, 255))
    msg2 = font.render("Pressione [ESPAÇO] para iniciar o jogo", True, (200, 200, 200))
    win.blit(msg1, (WIDTH//2 - msg1.get_width()//2, HEIGHT//2 - 50))
    win.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2 + 10))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu_active = False
            pygame.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            menu_active = False

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

    # atualiza bola (host controla)
    ball_x += ball_dx
    ball_y += ball_dy

    # colisão com topo e fundo
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_dy *= -1

    # colisão com paddles
    if ball_x <= 30 and host_y < ball_y < host_y + PADDLE_HEIGHT:
        ball_dx *= -1
    if ball_x >= WIDTH - 40 and client_y < ball_y < client_y + PADDLE_HEIGHT:
        ball_dx *= -1

    if conn:
        try:
            data = pickle.dumps((host_y, ball_x, ball_y))
            conn.sendall(data)
        except:
            pass

    draw()
pygame.quit()
