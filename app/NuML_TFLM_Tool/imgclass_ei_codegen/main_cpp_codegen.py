"""
MainCCodegen for imgclass_ei project.
"""
import os
from jinja2 import Environment, FileSystemLoader

class MainCCodegen:
    """
    MainCCodegen is a class responsible for generating the main C++ code for a project using a template file. 
    """
    def code_gen(self, main_file, template_file, tensor_arena_size):
        """
        Generates code for the main file using a template file and a specified tensor arena size.
        """

        tmpl_dirname = os.path.dirname(template_file)
        tmpl_basename = os.path.basename(template_file)

        env =  Environment(loader=FileSystemLoader(tmpl_dirname), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(tmpl_basename)
        output = template.render(define_tensor_arena_size = tensor_arena_size)
        main_file.write(output)
