import requests
from bs4 import BeautifulSoup
import time


def get_wikipedia_links(url, base_url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверить на ошибки HTTP
        soup = BeautifulSoup(response.text, 'html.parser')

        links = set()

        # Поиск ссылок в основном содержимом статьи
        for a in soup.select('#bodyContent a[href^="/wiki/"]'):
            href = a.get('href')
            if ":" not in href:
                full_url = base_url + href
                links.add(full_url)

        return links

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении {url}: {e}")
        return []


def is_valid_wikipedia_url(url, base_url):
    """Проверяет, является ли URL ссылкой на другую статью Википедии на том же языке."""
    parsed_url = urlparse(url)
    parsed_base_url = urlparse(base_url)

    # Проверка домена
    if parsed_url.netloc != parsed_base_url.netloc:
        return False

    # Проверка языка (первые две буквы домена)
    if parsed_url.netloc[:2] != parsed_base_url.netloc[:2]:
        return False

    # Проверка пути
    return parsed_url.path.startswith('/wiki/') and ':' not in parsed_url.path


def find_first_path(start_url, end_url, rate_limit):
    visited = set()
    stack = [(start_url, [start_url])]
    requests_made = 0

    print()

    while stack:
        current_url, path = stack.pop()

        if current_url == end_url:
            return path

        if len(path) > 5:
            # print(f"Переходов между ссылками больше 5")
            continue

        if current_url not in visited:
            visited.add(current_url)
            links = get_wikipedia_links(current_url, base_url="https://en.wikipedia.org")
            requests_made += 1


            if requests_made >= rate_limit:
                # Добавляем задержку, чтобы соблюсти ограничение скорости
                time.sleep(1)  # Ограничение количества запросов

                requests_made = 0

            for link in links:
                if link not in visited:
                    stack.append((link, path + [link]))

    return None


def save_path_to_file(path, filename):
    """Сохраняет путь в файл."""
    if path:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(" -> ".join(path))
        print(f"Путь сохранен в файл: {filename}")
    else:
        print(f"Путь не найден, файл {filename} не создан.")

        source_file = open('parse.txt', 'w')
        for i in range(0, 30):
            if i % 10 == 0 and i > 0:
                print(f"iteration #{i}", file=source_file, flush=True)
            else:
                print(f"iteration #{i}", file=source_file)
            time.sleep(1)

        source_file.close()


def main(url1, url2, limit1):
    """Основная функция для поиска пути и записи в файлы."""
    print("Поиск пути от url1 к url2")
    path_start_to_end = find_first_path(url1, url2, limit1)

    if path_start_to_end:
        print(f"Путь от {url1} к {url2}:")
        print(" -> ".join(path_start_to_end))  # Форматированный вывод пути
    else:
        print(f"Путь от {url1} к {url2} не найден за {5} переходов.")

    print("Поиск пути от url2 к url1")
    path_end_to_start = find_first_path(url2, url1, limit1)

    if path_end_to_start:
        print(f"Путь от {url2} к {url1}:")
        print(" -> ".join(path_end_to_start))  # Форматированный вывод пути

    else:
        print(f"Путь от {url2} к {url1} не найден за {5} переходов.")


# Входные данные
start_url = "https://en.wikipedia.org/wiki/Six_degrees_of_separation"  # url1
end_url = "https://en.wikipedia.org/wiki/American_Broadcasting_Company"  # url2
rate_limit = 10

# Запуск скрипта
main(start_url, end_url, rate_limit)
