# Добро пожаловать в vulnerable flask server

## Введение
Добро пожаловать в репозиторий проекта vuln_server! Этот проект направлен на оттачивание навыков пентестинга веб-приложений. Так же он может применяться при собеседовании на позицию junior-pentester для оценки навыков.

## Уязвимости
В рамках нашего проекта были исследованы следующие уязвимости:

- **Server-Side Template Injection (SSTI)**: Уязвимость, позволяющая атакующему внедрять шаблонный код в серверный шаблон, что может привести к выполнению произвольного кода на сервере.
- **Vulnerable Password Management**: Уязвимость, связанная с ненадежным управлением паролями, что может привести к их легкому подбору или утечке.

## Технологии
В приложении использовались следующие технологии:
- **Json Web Token** для авторизации
- **SQLite** для хранения информации
- **Flask** для создания веб-приложения

## Запуск
С использованием docker:
Скачайте проект, откройте терминал в корневой папке проекта и напишите команды "docker build -t <tag_name> . ", "docker run -d -p 5000:5000 --name <container_name> <tag_name>". Для взаимодействия с приложением перейдите по ссылке http://localhost:5000/
C использование Idle:
Запустите файл main.py, убедившись в том, что все библиотеки из requirement.txt установлены в виртуальном окружении.

## Прохождение
<details>
  <summary>Нажмите, чтобы открыть меню</summary>
  - Заходим на сайт, оцениваем функциональность.
  - Регистрируемся и пробуем оставить пост.
  - Пробуем нажать на раздел пригласи друга, понимаем, что для авторизации используются jwt.
  - Фаззим приложение и на ручке /.config находим файл, подсказывающий нам правила задания паролей на сервере.
  - Открываем hashcat и вводим следующую команду "./hashcat -a3 -m 16500 jwt.txt enc_key_for_production_?d?d?d?d?d?d?d?d --increment", где: jwt.txt файл с токеном, a3 режим bruteforce, -m 16500 режим взлома JWT.
  - С полученным ключом меняем и переподписываем токен (необходимо также добавить поле "is_administrator":True).
  - Получаем доступ к функциональности пригласить друга. Так как на этапе разведки можно заметить, что используется flask, а также значение test_user отображается на странице, пробуем протестировать сайт на наличие SSTI с помощью {{7*7}}.
  - Используем payloads для получения reverse shell. Задание выполнено!
</details>

## Заключение
Призываю сообщество помочь в улучшении моего приложения. Если будут идеи, пожалуйста, создайте Issue или отправьте Pull Request.

Спасибо за интерес к проекту!
