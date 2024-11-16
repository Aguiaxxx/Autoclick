import cv2
import numpy as np
import pyautogui
import mss
import time
import tkinter as tk
from tkinter import filedialog

# Função para capturar a tela
def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        screenshot = np.array(sct.grab(monitor))
        return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

# Função para o usuário selecionar a área na tela
def select_area():
    print("Capturando tela para seleção...")
    screen = capture_screen()
    file_path = "screenshot_temp.png"
    cv2.imwrite(file_path, screen)
    
    # Use o OpenCV para exibir a tela capturada
    ref_point = []

    def click_and_crop(event, x, y, flags, param):
        # Detecta cliques do mouse
        if event == cv2.EVENT_LBUTTONDOWN:
            ref_point.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            ref_point.append((x, y))
            cv2.rectangle(temp_image, ref_point[0], ref_point[1], (0, 255, 0), 2)
            cv2.imshow("Selecione a área", temp_image)

    temp_image = screen.copy()
    cv2.imshow("Selecione a área", temp_image)
    cv2.setMouseCallback("Selecione a área", click_and_crop)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(ref_point) == 2:
        x1, y1 = ref_point[0]
        x2, y2 = ref_point[1]
        cropped = screen[y1:y2, x1:x2]
        return cropped
    else:
        print("Nenhuma área selecionada!")
        return None

# Função para localizar a imagem de referência na tela
def find_image_on_screen(template, threshold=0.8):
    screen = capture_screen()
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        template_height, template_width = template.shape[:2]
        center_x = max_loc[0] + template_width // 2
        center_y = max_loc[1] + template_height // 2
        return center_x, center_y
    return None

# Função para realizar o clique
def click_on_location(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()

# Bot principal
def bot(template, interval=1, threshold=0.8):
    while True:
        position = find_image_on_screen(template, threshold)
        if position:
            print(f"Imagem encontrada em: {position}. Clicando...")
            click_on_location(*position)
        else:
            print("Imagem não encontrada...")
        time.sleep(interval)

# Fluxo principal
if __name__ == "__main__":
    print("Iniciando seleção de área...")
    selected_area = select_area()
    if selected_area is not None:
        print("Área selecionada com sucesso!")
        template_path = "template_selected.png"
        cv2.imwrite(template_path, selected_area)

        # Pergunta ao usuário se deseja iniciar o bot
        print("Deseja iniciar o bot? (s/n)")
        if input().lower() == "s":
            template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
            bot(template)
        else:
            print("Bot cancelado.")
    else:
        print("Seleção de área falhou. Tente novamente.")
