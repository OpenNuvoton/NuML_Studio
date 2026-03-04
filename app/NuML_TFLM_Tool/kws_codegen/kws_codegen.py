import os

from .kwsModel_hpp_codegen import kwsModelHppCodegen
from .kwsModel_cpp_codegen import kwsModelCppCodegen
from .Labels_cpp_codegen import LabelsCppCodegen
from .main_cpp_codegen import MainCCodegen

class KwsCodegen:
    def __init__(self, model, project, vela_summary, **kwargs):
        self.model = model
        self.project = project
        self.vela_summary = vela_summary
        self.extra = kwargs

    @classmethod
    def from_args(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def code_gen(self):
        print('Run kws class codegen...')
        print(f"model:{self.model}")
        print(f"project:{self.project}")
        for key, value in self.extra.items():
            print(f"extra param:{key}, {value}")

        template_path = os.path.dirname(os.path.abspath(__file__))  # use explicit path

        #Generate kwsModel.hpp file
        kwsModel_hpp_file_path = os.path.join(self.project, 'Model', 'include', 'kwsModel.hpp')
        kwsModel_hpp_temp_file_path = os.path.join(template_path, 'kwsModel_hpp_tmpl.jinja2')
        print(f'kwsModel.hpp template path {kwsModel_hpp_temp_file_path}')
        print(f'kwsModel.hpp file path {kwsModel_hpp_file_path}')

        try:
            kwsModel_hpp_file = open(kwsModel_hpp_file_path, "w")
        except OSError:
            print("Could not open kwsModel.hpp file")
            return 'unable_generate'

        with kwsModel_hpp_file:
            kwsModel_hpp_codegen = kwsModelHppCodegen()
            kwsModel_hpp_codegen.code_gen(kwsModel_hpp_file, kwsModel_hpp_temp_file_path, self.model)

        #Generate kwsModel.cpp file
        kwsModel_cpp_file_path = os.path.join(self.project, 'Model', 'kwsModel.cpp')
        kwsModel_cpp_temp_file_path = os.path.join(template_path, 'kwsModel_cpp_tmpl.jinja2')
        print(f'kwsModel.cpp template path {kwsModel_cpp_temp_file_path}')
        print(f'kwsModel.cpp file path {kwsModel_cpp_file_path}')

        try:
            kwsModel_cpp_file = open(kwsModel_cpp_file_path, "w")
        except OSError:
            print("Could not open kwsModel.cpp file")
            return 'unable_generate'

        with kwsModel_cpp_file:
            kwsModel_cpp_codegen = kwsModelCppCodegen()
            kwsModel_cpp_codegen.code_gen(kwsModel_cpp_file, kwsModel_cpp_temp_file_path, self.model)

        #Generate Labels.cpp file
        Labels_cpp_file_path = os.path.join(self.project, 'Model', 'Labels.cpp')
        Labels_cpp_temp_file_path = os.path.join(template_path, 'Labels_cpp_tmpl.jinja2')
        print(f'Labels.cpp template path {Labels_cpp_temp_file_path}')
        print(f'Labels.cpp file path {Labels_cpp_file_path}')

        try:
            Lables_cpp_file = open(Labels_cpp_file_path, "w")
        except OSError:
            print("Could not open Labels.cpp file")
            return 'unable_generate'

        with Lables_cpp_file:
            Labels_codegen = LabelsCppCodegen()
            Labels_codegen.code_gen(Lables_cpp_file, Labels_cpp_temp_file_path, self.model)

        #Generate main.cpp file
        main_file_path = os.path.join(self.project, 'main.cpp')
        main_temp_file_path = os.path.join(template_path, 'main_cpp_tmpl.jinja2')
        print(f'template path {main_temp_file_path}')
        print(f'main file path {main_file_path}')

        try:
            main_file = open(main_file_path, "w")
        except OSError:
            print("Could not open main file")
            return 'unable_generate'

        with main_file:
            main_codegen = MainCCodegen()
            main_codegen.code_gen(main_file, main_temp_file_path, self.vela_summary)
