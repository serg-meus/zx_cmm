from sys import argv

with open(argv[1], 'r') as file:
    data = file.read()
    data = data.replace(argv[2], argv[3])
    with open(argv[1] + '.tmp', 'w') as file:
        file.write(data)
