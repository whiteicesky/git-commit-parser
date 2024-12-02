import os
import toml
import zlib
from datetime import datetime
from visualizer import Visualizer

def parse_object(object_hash, description=None):
    object_path = os.path.join(config['settings']['repo_path'], '.git', 'objects', object_hash[:2], object_hash[2:])

    with open(object_path, 'rb') as file:
        raw_object_content = zlib.decompress(file.read())
        header, raw_object_body = raw_object_content.split(b'\x00', maxsplit=1)
        object_type, content_size = header.decode().split(' ')

        object_dict = {}

        if object_type == 'commit':
            object_dict['label'] = f'"[commit] {object_hash[:6]}"'
            object_dict['children'] = parse_commit(raw_object_body)

        elif object_type == 'tree':
            object_dict['label'] = f'"[tree] {object_hash[:6]}"'
            object_dict['children'] = parse_tree(raw_object_body)

        elif object_type == 'blob':
            object_dict['label'] = f'"[blob] {object_hash[:6]}"'
            object_dict['children'] = []

        if description is not None:
            object_dict['label'] += f' : {description}'

        return object_dict

def parse_tree(raw_content):
    children = []
    rest = raw_content
    while rest:
        mode, rest = rest.split(b' ', maxsplit=1)
        name, rest = rest.split(b'\x00', maxsplit=1)
        sha1, rest = rest[:20].hex(), rest[20:]
        children.append(parse_object(sha1, description=name.decode()))
    return children

def parse_commit(raw_content):
    content = raw_content.decode()
    content_lines = content.split('\n')

    commit_data = {}
    commit_data['tree'] = content_lines[0].split()[1]
    content_lines = content_lines[1:]

    commit_data['parents'] = []
    while content_lines[0].startswith('parent'):
        commit_data['parents'].append(content_lines[0].split()[1])
        content_lines = content_lines[1:]

    while content_lines[0].strip():
        key, *values = content_lines[0].split()
        commit_data[key] = ' '.join(values)
        content_lines = content_lines[1:]

    commit_data['message'] = '\n'.join(content_lines[1:]).strip()

    commit_date = datetime.utcfromtimestamp(int(commit_data['author'].split()[-2]))

    # Фильтрация коммитов по дате
    if commit_date < config['settings']['date_filter']:
        return []

    return [parse_object(commit_data['tree'])] + \
           [parse_object(parent) for parent in commit_data['parents']]

def get_last_commit():
    head_path = os.path.join(config['settings']['repo_path'], '.git', 'refs', 'heads', config['settings']['branch'])
    with open(head_path, 'r') as file:
        return file.read().strip()

def generate_uml(filename):
    def recursive_write(file, tree, seen):
        label = tree['label']
        for child in tree['children']:
            if (label, child["label"]) not in seen:
                file.write(f'    {label} --> {child["label"]}\n')
                seen.add((label, child["label"]))
                recursive_write(file, child, seen)

    last_commit = get_last_commit()
    tree = parse_object(last_commit)
    with open(filename, 'w') as file:
        file.write('@startuml\n')
        recursive_write(file, tree, set())
        file.write('@enduml')

with open('config.toml', 'r') as f:
    config = toml.load(f)

config['settings']['date_filter'] = datetime.strptime(config['settings']['date_filter'], "%Y-%m-%d")

generate_uml('graph.puml')

with open('graph.puml', 'r') as f:
    print(f.read())

visualizer_path = os.path.join(config['settings']['visualizer_path'])
visualizer = Visualizer(visualizer_path)
try:
    visualizer.render_puml('graph.puml')
except Exception as e:
    print(f"Ошибка выполнения команды визуализации: {e}")
