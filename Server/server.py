# server/server.py

import socket
import threading
import json
import os

# Файл хранения данных
DATA_FILE = "users.json"

# Загружаем данные при старте
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

users_db = load_users()

####### ОБРАБОТКА ЗАПРОСОВ #######
# Разрешённые поля для инкремента

ALLOWED_INCREMENT_STATS = {
    "random_wins",
    "deaths",
    "deaths_from_black_hole",
    "crystals",
    "craft_cells",
    "lives", 
    "max_skips"
}

def handle_login(request):
    username = request["username"]
    password = request["password"]
    if username in users_db and users_db[username]["password"] == password:
        return {
            "status": "success",
            "message": "Авторизация успешна",
            "stats": users_db[username]["stats"]
        }
    else:
        return {"status": "error", "message": "Неверный логин или пароль"}

def handle_register(request):
    username = request["username"]
    password = request["password"]
    if username in users_db:
        return {"status": "error", "message": "Пользователь уже существует"}
    else:
        users_db[username] = {"password": password,
            "stats": {
                "lives": 2,
                "max_skips": 2,
                "random_wins": 0,
                "last_completed_level": 0,
                "deaths": 0,
                "deaths_from_black_hole": 0,
                "pressure_tolerance": 200,
                "crystals": 0,
                "craft_cells": 0,
                "fog_radius": 1,
                "fog_remember": False
            }
        }
        save_users(users_db)
        return {
            "status": "success",
            "message": "Регистрация успешна",
            "stats": users_db[username]["stats"]
        }

def handle_get_stats(request):
    username = request["username"]
    if username in users_db:
        return {
            "status": "success",
            "stats": users_db[username]["stats"]
        }
    else:
        return {"status": "error", "message": "Пользователь не найден"}

def handle_update_stats(request):
    username = request.get("username")
    stat_type = request.get("stat_type")
    value = request.get("value", 1)  # по умолчанию +1
    operation = request.get("operation", "increment")  # "increment" или "set"

    if not username or not stat_type:
        return {"status": "error", "message": "Требуется username и stat_type"}

    if username not in users_db:
        return {"status": "error", "message": "Пользователь не найден"}

    stats = users_db[username]["stats"]

    # --- Инкремент (по умолчанию) ---
    if operation == "increment":
        if stat_type not in ALLOWED_INCREMENT_STATS:
            return {"status": "error", "message": f"Нельзя инкрементировать '{stat_type}'"}
        current = stats.get(stat_type, 0)
        stats[stat_type] = current + value

    # --- Установка значения ---
    elif operation == "set":
        if stat_type == "fog_remember":
            stats[stat_type] = bool(value)
        else:
            stats[stat_type] = value

    else:
        return {"status": "error", "message": "Операция должна быть 'increment' или 'set'"}

    save_users(users_db)
    return {
        "status": "success",
        "message": f"Статистика '{stat_type}' обновлена",
        "stats": stats
    }

def handle_update_campaign_level(request):
    username = request["username"]
    level_id = int(request["level_id"]) 
    if username in users_db:
        current = users_db[username]["stats"].get("last_completed_level", 0)
        # Обновляем только если уровень новый и следующий по порядку
        if level_id == current + 1:
            users_db[username]["stats"]["last_completed_level"] = level_id
            save_users(users_db)
            return {
                "status": "success",
                "message": f"Уровень {level_id} завершён",
                "stats": users_db[username]["stats"]
            }
        else:
            return {"status": "error", "message": "Нельзя пропускать уровни"}
    else:
        return {"status": "error", "message": "Пользователь не найден"}

def handle_record_death(request):
    username = request["username"]
    if username in users_db:
        users_db[username]["stats"]["deaths"] += 1
        save_users(users_db)
        return {
            "status": "success",
            "message": "Смерть записана",
            "stats": users_db[username]["stats"]
        }
    else:
        return {"status": "error", "message": "Пользователь не найден"}

def handle_record_black_hole_death(request):
    username = request["username"]
    if username in users_db:
        users_db[username]["stats"]["deaths_from_black_hole"] += 1
        users_db[username]["stats"]["deaths"] += 1
        save_users(users_db)
        return {
            "status": "success",
            "message": "Смерть от чёрной дыры записана",
            "stats": users_db[username]["stats"]
        }
    else:
        return {"status": "error", "message": "Пользователь не найден"}
    
ACTION_HANDLERS = {
    "login": handle_login,
    "register": handle_register,
    "update_stats": handle_update_stats,
    "update_campaign_level": handle_update_campaign_level,
    "record_death": handle_record_death,
    "record_black_hole_death": handle_record_black_hole_death,
    "get_stats": handle_get_stats,
}

def handle_client(conn, addr):
    print(f"[SERVER] Подключение от {addr}")
    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:  # ← исправлено: проверяем, что данные получены
                break

            request = json.loads(data)
            action = request.get("action")
            username = request.get("username")

            # --- ГАРАНТИРУЕМ, ЧТО У ПОЛЬЗОВАТЕЛЯ ЕСТЬ ВСЕ НУЖНЫЕ ПОЛЯ ---
            if username and username in users_db:
                stats = users_db[username]["stats"]

                # Миграция: добавляем недостающие поля
                if "random_wins" not in stats:
                    stats["random_wins"] = 0
                if "last_completed_level" not in stats:
                    stats["last_completed_level"] = 0
                if "deaths" not in stats:
                    stats["deaths"] = 0
                if "deaths_from_black_hole" not in stats:
                    stats["deaths_from_black_hole"] = 0
                if "lives" not in stats:
                    stats["lives"] = 2
                if "max_skips" not in stats:
                    stats["max_skips"] = 2
                if "craft_cells" not in stats:
                    stats["craft_cells"] = 0
                if "crystals" not in stats:
                    stats["crystals"] = 0
                if "pressure_tolerance" not in stats:
                    stats["pressure_tolerance"] = 200
                if "fog_radius" not in stats:
                    stats["fog_radius"] = 1
                if "fog_remember" not in stats:
                    stats["fog_remember"] = False
                    

            # Обработка действия
            handler = ACTION_HANDLERS.get(action)
            if handler:
                response = handler(request)
            else:
                response = {"status": "error", "message": "Неизвестное действие"}

            conn.send(json.dumps(response).encode("utf-8"))

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        print(f"[SERVER] Соединение с {addr} закрыто")
####### СОБЫТИЯ #######

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(5)
    print("[SERVER] Сервер запущен на localhost:9999")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\n[SERVER] Выключение...")
        server.close()

if __name__ == "__main__":
    start_server()