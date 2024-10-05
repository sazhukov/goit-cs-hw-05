import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter

import matplotlib.pyplot as plt
import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return ""


# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


# Функція для редукції
def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


# Виконання MapReduce
def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    # Якщо задано список слів для пошуку, враховувати тільки ці слова
    if search_words:
        words = [word for word in words if word in search_words]

    # Виконуємо паралельний маппінг використавши ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Виконуємо паралельну редукцію використавши ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


# Візуалізація результатів
def visualize_top_words(result, top_n=10):
    # Визначення топ-N найчастіше використовуваних слів
    top_words = Counter(result).most_common(top_n)

    # Розділення даних на слова та їх частоти
    words, counts = zip(*top_words)

    # Створення графіка
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color='skyblue')
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top_n} Most Frequent Words')
    plt.gca().invert_yaxis()  # Перевернути графік, щоб найбільші значення були зверху
    plt.show()


if __name__ == '__main__':
    # Вхідний текст для обробки
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"  # Текст із книги "Аліса в Країні Чудес"
    text = get_text(url)

    # Виконання MapReduce на вхідному тексті
    result = map_reduce(text)

    # Візуалізація топ-10 найчастіше використовуваних слів
    visualize_top_words(result, top_n=10)
