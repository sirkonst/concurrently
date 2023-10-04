import os
import sys

sys.path.insert(0, os.path.abspath('..'))

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'concurrently'
copyright = '2016, Konstantin Enchant'
author = 'Konstantin Enchant'

version = '2.0'
release = '2.0'

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

html_static_path = ['_static']

htmlhelp_basename = 'concurrentlydoc'
