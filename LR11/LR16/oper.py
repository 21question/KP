def simulate_concurrent_moves(isolation_level):
    # Параметры для теста
    book_id = 1
    from_branch_id = 1
    to_branch_id = 2
    quantity = 1

    # Создаем два потока для параллельного перемещения
    thread1 = Thread(target=move_books, args=(book_id, from_branch_id, to_branch_id, quantity, isolation_level))
    thread2 = Thread(target=move_books, args=(book_id, from_branch_id, to_branch_id, quantity, isolation_level))

    # Запускаем потоки
    thread1.start()
    thread2.start()

    # Ждем завершения
    thread1.join()
    thread2.join()

    # Проверяем результат
    conn = psycopg2.connect(
        dbname="library",
        user="postgres",
        password="password",
        host="localhost"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE book_id = %s AND branch_id = %s", (book_id, from_branch_id))
    result = cursor.fetchone()[0]
    print(f"Остаток в филиале-отправителе: {result}")
    conn.close()


# Тестирование с разными уровнями изоляции
print("Тест с READ COMMITTED:")
simulate_concurrent_moves(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)

print("\nТест с REPEATABLE READ:")
simulate_concurrent_moves(psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ)

print("\nТест с SERIALIZABLE:")
simulate_concurrent_moves(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)