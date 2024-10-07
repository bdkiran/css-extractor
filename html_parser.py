from bs4 import BeautifulSoup
import random
import string
import json

def parse_html():
    with open('input/input.html', 'r') as f:
        webpage = f.read()
    soup = BeautifulSoup(webpage, features="html.parser")
    classes_map = {}
    for node in soup.find_all():
        if node.has_attr('class'):
            oldClasses = node['class']
            oldClassesString = ', '.join(oldClasses)
            # Find the class if it exists
            if oldClassesString in classes_map:
                node['class'] = classes_map[oldClassesString]
            else:
                new_class_name = ''.join(random.choices(string.ascii_uppercase, k=15))
                classes_map[oldClassesString] = new_class_name
                node['class'] = classes_map[oldClassesString]
    new_classes_list = []
    for oldClassesString, new_class_name in classes_map.items():
        new_classes_list.append({'newClass': new_class_name, 'oldClasses': oldClassesString})

    for node in soup.find_all():
        if node.has_attr('class'):
            break

    with open("output/output.html", "w") as file:
        file.write(str(soup))
        
    with open('input/input.json', 'w') as fout:
        json.dump(new_classes_list, fout)

parse_html()