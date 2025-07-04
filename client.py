import socket
import threading
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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 5555)) 
def receive_data():
    global host_y, ball_x, ball_y
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            host_y, ball_x, ball_y = pickle.loads(data)
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

menu_active = True
while menu_active:
    win.fill((20, 20, 20))
    font = pygame.font.SysFont("Arial", 28)
    msg = font.render("Aguardando o host iniciar o jogo...", True, (255, 255, 255))
    win.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()

    if (ball_x, ball_y) != (WIDTH // 2, HEIGHT // 2):
        menu_active = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

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
    if keys[pygame.K_UP]:
        client_y -= 5
    if keys[pygame.K_DOWN]:
        client_y += 5

    try:
        data = pickle.dumps(client_y)
        client.sendall(data)
    except:
        pass

    draw()
pygame.quit()
