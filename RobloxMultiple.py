import os
import sys
import time
import psutil
import win32api
import win32event
import win32con
import winerror
import subprocess
import logging
from colorama import Fore, Style, init

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)

ROBLOX_MUTEX_NAME = "ROBLOX_singletonMutex"
ROBLOX_PROCESS_NAME = "RobloxPlayerBeta.exe"
ROBLOX_LAUNCHER_PATH = "C:/"


def log_with_delay(level, message, color=None, delay=1):
    if color:
        message = f"{color}{message}{Style.RESET_ALL}"

    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    time.sleep(delay)


def create_or_acquire_mutex(mutex_name):
    mutex = None
    try:
        mutex = win32event.CreateMutex(None, False, mutex_name)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            log_with_delay("info", f"[!] Мьютекс уже существует, попытка получения", Fore.LIGHTCYAN_EX)
            win32api.CloseHandle(mutex)
            mutex = win32event.OpenMutex(win32con.SYNCHRONIZE, False, mutex_name)
            if mutex is None:
                log_with_delay("error", "[!] Не удалось открыть мьютекс", Fore.RED)
                return None

        win32event.WaitForSingleObject(mutex, win32event.INFINITE)
        log_with_delay("info", f"[!] Мьютекс успешно захвачен", Fore.LIGHTGREEN_EX)
        return mutex
    except Exception as e:
        log_with_delay("error", f"[!] Ошибка при работе с мьютексом: {e}", Fore.RED)
        if mutex:
            win32api.CloseHandle(mutex)
        return None


def release_mutex(mutex):
    if mutex:
        try:
            win32event.ReleaseMutex(mutex)
            log_with_delay("info", "[!] Мьютекс успешно освобожден", Fore.LIGHTGREEN_EX)
            win32api.CloseHandle(mutex)
        except Exception as e:
            log_with_delay("error", f"[!] Ошибка при освобождении мьютекса: {e}", Fore.RED)


def is_roblox_running():
    try:
        for process in psutil.process_iter(["name"]):
            if process.info["name"] == ROBLOX_PROCESS_NAME:
                return True
    except psutil.Error as e:
        log_with_delay("error", f"[!] Ошибка проверки запущенных процессов: {e}", Fore.RED)
    return False


def start_roblox():
    log_with_delay("info", "[!] Roblox запускается, ожидайте", Fore.CYAN)
    try:
        subprocess.Popen([ROBLOX_LAUNCHER_PATH])
    except FileNotFoundError:
        log_with_delay("error", f"[!] Не удалось найти исполняемый файл Roblox: {ROBLOX_LAUNCHER_PATH}", Fore.RED)
    except Exception as e:
        log_with_delay("error", f"[!] Ошибка при запуске Roblox: {e}", Fore.RED)


def main():
    log_with_delay("info", "[!] Программа запущена, пытаемся перехватить мьютекс", Fore.LIGHTBLUE_EX)

    mutex = create_or_acquire_mutex(ROBLOX_MUTEX_NAME)
    if mutex is None:
        log_with_delay("error", "[!] Не удалось получить контроль над мьютексом", Fore.RED)
        return

    try:
        start_roblox()

        log_with_delay("info", "[!] Успешно! Разрешено запускать несколько экземпляров", Fore.LIGHTGREEN_EX)
        input(f"{Fore.CYAN}[!] Нажмите Enter для освобождения мьютекса: {Style.RESET_ALL}")
    finally:
        release_mutex(mutex)


if __name__ == "__main__":
    main()