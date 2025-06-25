import psycopg2
from threading import Thread
import time


def move_books(book_id, from_branch_id, to_branch_id, quantity, isolation_level):
    conn = psycopg2.connect(
        dbname="library",
        user="postgres",
        password="password",
        host="localhost"
    )
    conn.set_isolation_level(isolation_level)
    cursor = conn.cursor()

    try:
        # Начало транзакции
        cursor.execute("BEGIN")

        # Проверка наличия достаточного количества книг
        cursor.execute(
            "SELECT quantity FROM stock WHERE book_id = %s AND branch_id = %s FOR UPDATE",
            (book_id, from_branch_id)
        )
        current_quantity = cursor.fetchone()[0]

        if current_quantity < quantity:
            raise Exception("Недостаточно книг в филиале-отправителе")

        # Уменьшение количества у отправителя
        cursor.execute(
            "UPDATE stock SET quantity = quantity - %s WHERE book_id = %s AND branch_id = %s",
            (quantity, book_id, from_branch_id)
        )

        # Увеличение количества у получателя
        cursor.execute(
            "INSERT INTO stock (book_id, branch_id, quantity) VALUES (%s, %s, %s) "
            "ON CONFLICT (book_id, branch_id) DO UPDATE SET quantity = stock.quantity + %s",
            (book_id, to_branch_id, quantity, quantity)
        )

        # Логирование перемещения
        cursor.execute(
            "INSERT INTO movements (book_id, quantity, from_branch_id, to_branch_id) "
            "VALUES (%s, %s, %s, %s)",
            (book_id, quantity, from_branch_id, to_branch_id)
        )

        # Фиксация транзакции
        conn.commit()
        print(f"Перемещено {quantity} книг из филиала {from_branch_id} в филиал {to_branch_id}")

    except Exception as e:
        conn.rollback()
        print(f"Ошибка при перемещении: {e}")
    finally:
        conn.close()