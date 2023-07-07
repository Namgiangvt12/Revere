import os
import importlib

folder_path = 'Scripts'

file_names = [file_name[:-3] for file_name in os.listdir(folder_path) if file_name.endswith('.py')]

modules = [importlib.import_module(f'{folder_path}.{file_name}') for file_name in file_names]

function_name = 'Crawling_data'

target_scripts = ['Alameda County.py', 'Alpine County.py' , 'Amador County.py']
# target_scripts = []

for module in modules:
    if hasattr(module, function_name):
        script_name = os.path.basename(module.__file__)
        if len(target_scripts) and (script_name in target_scripts) == False:
            continue
        function = getattr(module, function_name)
        if callable(function):
            function()
