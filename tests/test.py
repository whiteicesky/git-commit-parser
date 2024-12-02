import unittest
import os
import time
import main
from visualizer import Visualizer


class TestGitGraph(unittest.TestCase):

    def setUp(self):
        """Подготовка тестового окружения"""
        # Убедимся, что файл config.toml существует и используется корректно
        config_path = os.path.join(os.getcwd(), 'config.toml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Не найден файл конфигурации: {config_path}")

        # Удаляем предыдущие сгенерированные файлы (если они существуют)
        if os.path.exists('graph.puml'):
            os.remove('graph.puml')
        if os.path.exists('graph.png'):
            os.remove('graph.png')

    def test_generate_puml(self):
        """Тест генерации файла graph.puml"""
        # Запускаем генерацию графа
        main.generate_uml('graph.puml')

        # Проверяем, что файл graph.puml был создан
        self.assertTrue(os.path.exists('graph.puml'), "Файл graph.puml не был создан")

        # Проверяем, что файл не пустой
        with open('graph.puml', 'r') as f:
            content = f.read().strip()
            self.assertGreater(len(content), 0, "Файл graph.puml пуст")

    def test_generate_png(self):
        """Тест визуализации в график PNG"""
        # Создаем файл puml (если он еще не был создан)
        if not os.path.exists('graph.puml'):
            main.generate_uml('graph.puml')

        # Инициализируем визуализатор
        visualizer = Visualizer("C:/Python/homework2/plantuml.jar")

        try:
            # Запускаем визуализацию
            visualizer.render_puml('graph.puml')

            # Проверяем, что файл graph.png был создан
            self.assertTrue(os.path.exists('graph.png'), "Файл graph.png не был создан")

            # Проверяем, что файл не пустой
            file_size = os.path.getsize('graph.png')
            self.assertGreater(file_size, 0, "Файл graph.png пуст")

        except Exception as e:
            self.fail(f"Ошибка при визуализации графа: {e}")

    def test_parse_object(self):
        """Тест функции parse_object для обработки git объектов"""
        # Пример хеша объекта (для теста можно использовать любой валидный хеш)
        object_hash = "c202d0d9fd7aaa075f0271aea3b2a286d4a8742a"

        # Проверяем результат работы функции parse_object
        result = main.parse_object(object_hash)

        # Проверяем, что результат содержит 'label' и 'children'
        self.assertIn("label", result)
        self.assertIn("children", result)

        # Проверяем, что label соответствует ожидаемому значению
        self.assertEqual(result["label"], f'"[commit] {object_hash[:6]}"')

    def test_get_last_commit(self):
        """Тест функции get_last_commit"""
        last_commit = main.get_last_commit()
        self.assertIsNotNone(last_commit, "Последний коммит не был найден")
        self.assertIsInstance(last_commit, str, "Последний коммит не является строкой")

    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем сгенерированные файлы
        if os.path.exists('graph.puml'):
            os.remove('graph.puml')
        if os.path.exists('graph.png'):
            os.remove('graph.png')


if __name__ == "__main__":
    unittest.main()
