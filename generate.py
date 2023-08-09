import os
import random
import string
import sqlite3
import signal
import sys

DB_FILE = "combinations.db"
conn = None  # Initialize the conn variable in the global scope

def create_database():
    global conn  # Use the global conn variable
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS combinations (combination TEXT PRIMARY KEY)''')
    conn.commit()

def get_existing_combinations():
    c = conn.cursor()
    c.execute('''SELECT combination FROM combinations''')
    existing_combinations = set([row[0] for row in c.fetchall()])
    return existing_combinations

def insert_combinations(combination_list):
    c = conn.cursor()
    c.executemany("INSERT INTO combinations (combination) VALUES (?)", [(c,) for c in combination_list])
    conn.commit()

def generate_combinations(chunk_size, existing_combinations):
    characters = "abcdef0123456789"
    dashes = [8, 13, 18, 23]

    while True:
        combinations = []
        while len(combinations) < chunk_size:
            combination = ''.join(random.choices(characters, k=32))
            for pos in dashes:
                combination = combination[:pos] + '-' + combination[pos:]

            if combination not in existing_combinations:
                combinations.append(combination)

        yield combinations

def signal_handler(sig, frame):
    print("\nStopping the script...")
    if conn is not None:
        conn.close()  # Close the database connection before exiting
    sys.exit(0)

def write_to_files(combinations_per_file, chunk_size, conn):  # Pass conn as an argument
    total_combinations_written = 0
    for combinations in generate_combinations(chunk_size, get_existing_combinations()):
        if not combinations:
            break

        filename = f"output_files/output_{total_combinations_written + 1}.txt"
        with open(filename, 'w') as file:
            for combination in combinations:
                file.write(combination + '\n')

        insert_combinations(combinations)
        total_combinations_written += len(combinations)

        print(f"Total combinations written: {total_combinations_written}")

    print("Script completed successfully.")

def append_to_log(combinations):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executemany("INSERT INTO combinations (combination) VALUES (?)", [(c,) for c in combinations])
    conn.commit()
    conn.close()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handle KeyboardInterrupt (Ctrl+C)

    create_database()
    existing_combinations = get_existing_combinations()

    combinations_per_file = 100000
    chunk_size = 100000

    total_combinations_written = 0
    file_number = 1

    for combinations_chunk in generate_combinations(chunk_size, existing_combinations):
        if not combinations_chunk:
            break

        combinations_written = 0
        filename = f"output_files/output_{file_number}.txt"
        with open(filename, 'w') as file:
            for combination in combinations_chunk:
                file.write(combination + '\n')
                combinations_written += 1

                if combinations_written >= combinations_per_file:
                    break

        total_combinations_written += combinations_written
        append_to_log(combinations_chunk[:combinations_written])

        print(f"Total combinations written: {total_combinations_written}")

        file_number += 1  # Increment the file_number for the next file

    print("Script completed successfully.")