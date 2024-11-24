# Если лень все скачивать и настраивать, есть решение
В файле msg_split_test.ipynb находятся тесты связанные с source.htnl, где можно посмотреть на результат изменении max_len.

# команды
юнит тесты  python -m unittest unit_test.py

python msg_split.py --max-len=3072 ./source.html 
