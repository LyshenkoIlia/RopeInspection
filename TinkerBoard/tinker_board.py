import subprocess
import time
import os
import ASUS.GPIO as GPIO 

REC_TIME = 5  # секунд до и после триггера
TRIGGER_PIN = 7 # Пример пина GPIO для сигнала

def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIGGER_PIN, GPIO.IN)
    pass

def check_trigger():
    # Имитация проверки. В реальности здесь будет: GPIO.input(TRIGGER_PIN)
    # Возвращает True, если пришел сигнал
    return False 

def run_buffer_stream():
    """
    Запускает FFmpeg в режиме кругового буфера.
    FFmpeg сам пишет видео в ОЗУ (в папку /tmp или /run/user, чтобы беречь флешку)
    и циклично нарезает его на куски по 1 секунде.
    """
    # Папка в оперативной памяти Tinker Board
    ram_dir = "/tmp/video_buffer"
    os.makedirs(ram_dir, exist_ok=True)
    
    # Команда запускает цикличную запись кусками по 1 секунде, храня последние 6 файлов
    # Используем аппаратный кодек h264_v4l2m2m для Tinker Board (RK3288/RK3399)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "v4l2", "-input_format", "yuyv422", "-i", "/dev/video0", # Ваша камера
        "-c:v", "h264_v4l2m2m", "-b:v", "2M", # Аппаратное сжатие
        "-f", "segment", "-segment_time", "1", 
        "-segment_wrap", "10", # Храним только 10 последних секунд (5 до + запас)
        "-segment_list_type", "m3u8", 
        f"{ram_dir}/part_%03d.ts"
    ]
    
    # Запускаем в фоне
    return subprocess.Popen(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def save_and_send_replay():
    print("Сигнал получен! Сохраняем 5 секунд до и пишем 5 секунд после...")
    
    # 1. Ждем 5 секунд, пока допишется видео ПОСЛЕ триггера
    time.sleep(REC_TIME)
    
    # 2. Склеиваем последние куски из /tmp в один готовый MP4
    # (FFmpeg делает это моментально без перекодирования)
    output_path = "/tmp/event_replay.mp4"
    
    # Команда склейки (concat) последних созданных .ts файлов
    # ... логика выбора файлов из /tmp ...
    
    print(f"Видео сохранено в {output_path}. Отправка на сервер...")
    # Здесь ваш код отправки (например, через библиотеку requests)

# Главный цикл
if __name__ == "__main__":
    init_gpio()
    buffer_process = run_buffer_stream()
    
    try:
        while True:
            if check_trigger():
                save_and_send_replay()
                # После отправки можно очистить буфер или продолжить цикл
            time.sleep(0.1) # Чтобы не загружать процессор ядра
    finally:
        buffer_process.terminate() # Корректно закрываем FFmpeg при выходе
