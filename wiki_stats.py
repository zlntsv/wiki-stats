#!/usr/bin/python3

import os
import sys
import math
import array
import statistics
from collections import deque

from matplotlib import rc

rc('font', family='Droid Sans', weight='normal', size=14)
import matplotlib.pyplot as plt


class WikiGraph:
    def load_from_file(self, filename):
        print('Загружаю граф из файла: ' + filename)
        with open(filename, encoding='utf-8') as f:
            header = f.readline().strip().split()
            if len(header) < 2:
                raise ValueError("Неверный формат файла (нет заголовка)")
            m = int(header[0])
            n_total = int(header[1])


            self._titles = []
            self._sizes = array.array('L', [0] * m)
            self._redirect = array.array('B', [0] * m)
            self._offset = array.array('L', [0] * (m + 1))
            self._links = array.array('L', [0] * n_total)

            current_link_index = 0
            for i in range(m):
                title = f.readline().strip()
                self._titles.append(title)
                parts = f.readline().split()
                if len(parts) < 3:
                    raise ValueError("Неверный формат описания статьи")
                size = int(parts[0])
                redir = int(parts[1])
                k = int(parts[2])
                self._sizes[i] = size
                self._redirect[i] = redir
                self._offset[i] = current_link_index
                for j in range(k):
                    link_target = int(f.readline().strip())
                    self._links[current_link_index] = link_target
                    current_link_index += 1

            self._offset[m] = current_link_index
        print('Граф загружен')

    def get_number_of_links_from(self, _id):
        # Число исходящих ссылок для статьи _id
        return self._offset[_id + 1] - self._offset[_id]

    def get_links_from(self, _id):
        start = self._offset[_id]
        end = self._offset[_id + 1]
        # Возвращаем список ссылок (номеров статей)
        return list(self._links[start:end])

    def get_id(self, title):
        # Поиск статьи по названию (возвращает индекс или -1)
        try:
            return self._titles.index(title)
        except ValueError:
            return -1

    def get_number_of_pages(self):
        return len(self._titles)

    def is_redirect(self, _id):
        return bool(self._redirect[_id])

    def get_title(self, _id):
        return self._titles[_id]

    def get_page_size(self, _id):
        return self._sizes[_id]


def hist(fname, data, bins, xlabel, ylabel, title, facecolor='green', alpha=0.5, transparent=True, **kwargs):
    plt.clf()
    plt.hist(data, bins=bins, facecolor=facecolor, alpha=alpha, **kwargs)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(fname, transparent=transparent)
    print("Гистограмма сохранена в", fname)


def bfs_path(graph, start_title, target_title):
    start_id = graph.get_id(start_title)
    target_id = graph.get_id(target_title)
    if start_id == -1 or target_id == -1:
        print("Одна из статей не найдена")
        return None
    m = graph.get_number_of_pages()
    visited = [False] * m
    pred = [-1] * m
    queue = deque()
    queue.append(start_id)
    visited[start_id] = True

    while queue:
        u = queue.popleft()
        if u == target_id:
            break
        for v in graph.get_links_from(u):
            if not visited[v]:
                visited[v] = True
                pred[v] = u
                queue.append(v)
    if not visited[target_id]:
        return None

    path = []
    cur = target_id
    while cur != -1:
        path.append(cur)
        cur = pred[cur]
    path.reverse()
    return path


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Использование: wiki_stats.py <файл с графом статей>')
        sys.exit(-1)

    filename = sys.argv[1]
    if not os.path.isfile(filename):
        print('Файл с графом не найден')
        sys.exit(-1)

    wg = WikiGraph()
    wg.load_from_file(filename)

    m = wg.get_number_of_pages()
    print("Количество статей:", m)


    # Если используется wiki-small.txt, ищем путь от "Python" до "Список_файловых_систем"
    # Если wiki.txt – ищем путь от "Python" до "Боль"
    if os.path.basename(filename) == "wiki_small.txt":
        start_title = "Python"
        target_title = "Список_файловых_систем"
    else:
        start_title = "Python"
        target_title = "Боль"

    print("Запускаем поиск в ширину")
    path_ids = bfs_path(wg, start_title, target_title)
    if path_ids is None:
        print("Путь не найден")
    else:
        print("Поиск закончен. Найден путь:")
        for pid in path_ids:
            print(wg.get_title(pid))


    out_links = [wg.get_number_of_links_from(i) for i in range(m)]
    min_out = min(out_links)
    max_out = max(out_links)
    count_min_out = out_links.count(min_out)
    count_max_out = out_links.count(max_out)
    avg_out = statistics.mean(out_links)
    stdev_out = statistics.stdev(out_links) if m > 1 else 0


    in_links = [0] * m
    in_redirects = [0] * m
    total_redirect_articles = 0
    for i in range(m):
        if wg.is_redirect(i):
            total_redirect_articles += 1
        for dest in wg.get_links_from(i):
            if wg.is_redirect(i):
                in_redirects[dest] += 1
            else:
                in_links[dest] += 1

    min_in = min(in_links)
    max_in = max(in_links)
    count_min_in = in_links.count(min_in)
    count_max_in = in_links.count(max_in)
    avg_in = statistics.mean(in_links)
    stdev_in = statistics.stdev(in_links) if m > 1 else 0

    min_in_redir = min(in_redirects)
    max_in_redir = max(in_redirects)
    count_min_in_redir = in_redirects.count(min_in_redir)
    count_max_in_redir = in_redirects.count(max_in_redir)
    avg_in_redir = statistics.mean(in_redirects)
    stdev_in_redir = statistics.stdev(in_redirects) if m > 1 else 0

    #Вывод статистики
    total_redirect_percent = (total_redirect_articles / m * 100) if m else 0
    print("Количество статей с перенаправлением: {} ({:.2f}%)".format(total_redirect_articles, total_redirect_percent))
    print("Минимальное количество ссылок из статьи:", min_out)
    print("Количество статей с минимальным количеством ссылок:", count_min_out)
    print("Максимальное количество ссылок из статьи:", max_out)
    print("Количество статей с максимальным количеством ссылок:", count_max_out)
    max_out_id = out_links.index(max_out)
    print("Статья с наибольшим количеством ссылок:", wg.get_title(max_out_id))
    print("Среднее количество ссылок в статье: {:.2f} (ср. откл. {:.2f})".format(avg_out, stdev_out))
    print("Минимальное количество внешних ссылок на статью:", min_in)
    print("Количество статей с минимальным количеством внешних ссылок:", count_min_in)
    print("Максимальное количество внешних ссылок на статью:", max_in)
    print("Количество статей с максимальным количеством внешних ссылок:", count_max_in)            
    max_in_id = in_links.index(max_in)
    print("Статья с наибольшим количеством внешних ссылок:", wg.get_title(max_in_id))
    print("Среднее количество внешних ссылок на статью: {:.2f} (ср. откл. {:.2f})".format(avg_in, stdev_in))
    print("Минимальное количество внешних перенаправлений на статью:", min_in_redir)
    print("Количество статей с минимальным количеством внешних перенаправлений:", count_min_in_redir)
    print("Максимальное количество внешних перенаправлений на статью:", max_in_redir)
    print("Количество статей с максимальным количеством внешних перенаправлений:", count_max_in_redir)
    max_in_redir_id = in_redirects.index(max_in_redir)
    print("Статья с наибольшим количеством внешних перенаправлений:", wg.get_title(max_in_redir_id))
    print("Среднее количество внешних перенаправлений на статью: {:.2f} (ср. откл. {:.2f})".format(avg_in_redir,
                                                                                                   stdev_in_redir))


