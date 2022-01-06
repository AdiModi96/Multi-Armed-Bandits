import os
import inspect

project_folder_path = os.path.abspath(os.path.join(inspect.getfile(inspect.currentframe()), '..', '..'))
src_folder_path = os.path.join(project_folder_path, 'src')
experiments_folder_path = os.path.join(project_folder_path, 'experiments')