import tkinter as tk
from tkinter import messagebox
import itertools
import random
from collections import defaultdict

def load_dictionary(filepath="russian.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            anagram_dict = defaultdict(list)
            for line in f:
                word = line.strip().lower()
                if word:
                    key = ''.join(sorted(word))
                    anagram_dict[key].append(word)
            return anagram_dict
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл словаря '{filepath}' не найден.")
        return None

def find_meaningful_anagrams(word, anagram_dict):
    # Сортируем буквы входного слова
    sorted_word = ''.join(sorted(word.lower()))
    # Возвращаем все слова из группы, исключая исходное
    return [w for w in anagram_dict.get(sorted_word, []) if w != word.lower()]

def find_number_permutations(number_str):  # Ищет анаграммы чисел
					   # TODO: подумать насчёт нулей
    perms = [''.join(p) for p in itertools.permutations(number_str)]
    return sorted(list(set(perms)))

# --- Функции для игры в анаграммы ---

def scramble_word(word):	# Рандомим слово и шаффлим
    letters = list(word)
    if len(set(letters)) == 1:  # Все буквы одинаковые, перемешивать нечего
        return word
    while letters == list(word):
        random.shuffle(letters)
    return ''.join(letters)

def play_anagram_game(): # Отдельная функция для игры в анаграммы
    global game_window, dictionary, game_rounds, current_round, word_lengths, score, answers, scrambled_word, correct_word, answer_entry, answer_button, ans

    if dictionary is None:
        messagebox.showerror("Ошибка", "Словарь не загружен!")
        return

    game_window = tk.Toplevel(main_window)  # Создаем новое окно поверх главного
    game_window.title("Игра в анаграммы")
    game_window.geometry("400x300")

    game_rounds = 6
    current_round = 0
    word_lengths = [4, 4, 5, 5, 6, 6]  # Длина слова для каждого раунда
    score = 0
    answers = [] #тут храним введенные ответы
    ans = [] #тут храним слова которые загадал код

    def start_round():
        global current_round, word_lengths, scrambled_word, correct_word, answer_label, answer_entry, answer_button, ans

        if current_round < game_rounds:
            word_length = word_lengths[current_round]
            all_words = [word for group in dictionary.values() for word in group]  # Преобразуем в плоский список
            valid_words = [word for word in all_words if len(word) == word_length]

            if not valid_words:
                messagebox.showerror("Ошибка", f"Нет слов длины {word_length} в словаре.")
                return

            correct_word = random.choice(valid_words)
            ans.append(correct_word)
            scrambled_word = scramble_word(correct_word)

            # Очищаем элементы предыдущего раунда (если есть)
            for widget in game_window.winfo_children():
                widget.destroy()

            # Выводим перемешанное слово
            answer_label = tk.Label(game_window, text=f"Раунд {current_round + 1}/{game_rounds}\nСоберите слово из букв: {scrambled_word}")
            answer_label.pack(pady=10)

            # Поле ввода ответа
            answer_entry = tk.Entry(game_window)
            answer_entry.pack(pady=5)

            # Кнопка "Ответить"
            answer_button = tk.Button(game_window, text="Ответить", command=check_answer)
            answer_button.pack(pady=10)
        else:
            end_game()

    def check_answer():
        #проверем введённый ответ на зашавленное слово
        global current_round, score, answers, correct_word, answer_entry

        player_answer = answer_entry.get().lower()
        answers.append(player_answer) #Сохраняем ответ

        # Находим другие анаграммы для проверки, вдруг человек ввёл другую анаграмму слова
        correct_anagrams = find_meaningful_anagrams(correct_word, dictionary)

        if player_answer == correct_word: #Если мы прям угадали слово от компа
            score += 1
            messagebox.showinfo("Верно!", "Вы угадали слово!!")

        elif player_answer in correct_anagrams: #Если мы ввели другую анаграмму слова, которая имеет право на жизнь
            score += 1
            messagebox.showinfo("Частично верно!", f"Это другая анаграмма! Загаданное слово было: {correct_word}")
        else:
            messagebox.showinfo("Неверно", f"Неправильно. Правильный ответ: {correct_word}") #Если прям совсем не угадали слово
        current_round += 1
        start_round()

    def end_game():
        """Завершает игру и показывает результаты."""
        global score, answers, game_window, ans

        results_text = f"Ваш результат: {score}/{game_rounds}\n"
        results_text += "Ответы:\n"
        for i in range(game_rounds):    # Выводим все ответы, которые мы вводили и слова, которые загадывал комп
            results_text += f"Раунд {i + 1}: Ваш ответ - {answers[i]}, Правильный ответ - {ans[i]}\n"

        messagebox.showinfo("Игра окончена", results_text)
        game_window.destroy()

    start_round() # Запускаем первый раунд

# --- Функции для словаря ---
def process_input():
    """Обрабатывает ввод пользователя для поиска анаграмм в словаре."""
    input_text = entry.get()
    if not input_text:
        messagebox.showinfo("Ошибочка вышла...", "Повторите ввод!")
        return

    if input_text.isdigit() and len(input_text) >= 2:
        permutations = find_number_permutations(input_text)
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "Анаграммы числа:\n")
        for perm in permutations:
            result_text.insert(tk.END, perm + "\n")
    else:
        global dictionary

        if dictionary is None:
            messagebox.showerror("Ошибка", "Словарь не загружен!")
            return

        anagrams = find_meaningful_anagrams(input_text, dictionary)

        if anagrams:
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "Анаграммы:\n")
            for anagram in anagrams:
                result_text.insert(tk.END, anagram + "\n")
        else:
            messagebox.showinfo("Ой ой....", "Анаграммы не найдены...")

def open_dictionary():
    """Открывает окно словаря."""
    global dictionary_window, label, entry, button, result_text

    dictionary_window = tk.Toplevel(main_window)  # Создаем новое окно поверх главного
    dictionary_window.title("Словарь анаграмм")
    dictionary_window.geometry("400x300")

    label = tk.Label(dictionary_window, text="Введите слово или число:")
    label.pack(pady=10)

    entry = tk.Entry(dictionary_window)
    entry.pack(pady=5)

    button = tk.Button(dictionary_window, text="Найти анаграммы", command=process_input)
    button.pack(pady=10)

    result_text = tk.Text(dictionary_window, height=10, width=40)
    result_text.pack(pady=10)


# --- Главное окно ---

main_window = tk.Tk()
main_window.title("Анаграммы!!")
main_window.geometry("200x150")

# Кнопки главного меню
game_button = tk.Button(main_window, text="Игра", command=play_anagram_game)
game_button.pack(pady=20)

dictionary_button = tk.Button(main_window, text="Словарь", command=open_dictionary)
dictionary_button.pack(pady=20)

# Загружаем словарь один раз при запуске программы
dictionary = load_dictionary()

main_window.mainloop()
