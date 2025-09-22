"""
A class to handle generic Edge Impulse (EI) code generation.
"""
import os
import re
from .InputFiles_hpp_codegen import InputFilesHPPCodegen
from .main_cpp_codegen import MainCCodegen


class GenericEICodegen:
    """
    A class to handle generic Edge Impulse (EI) code generation.
    """
    def __init__(self, project, ei_apikey, **kwargs):
        self.project = project
        self.ei_apikey = ei_apikey
        self.specify_label = kwargs.get('specify_label', None)
        self.ei_c_model_fname = kwargs.get('ei_c_model_fname', None)
        self.tensor_arena_size = 0 # important to codegen, will be set when read from EI model source file
        self.extra = kwargs

    @classmethod
    def from_args(cls, *args, **kwargs):
        """
        Create an instance of the class using the provided arguments and keyword arguments.
        This method acts as a wrapper around the class constructor, allowing
        the creation of an instance by passing positional and keyword arguments.
        """
        return cls(*args, **kwargs)

    def get_input_data_size_1d(self):
        """
        Calculates the total input data size in a 1D format by reading and parsing 
        the 'model_variables.h' file for specific parameters.
        """
        inputdata_file_path = os.path.join(self.project, 'edgeimpulse_model', 'model-parameters', 'model_variables.h')

        raw_sample_count = 0
        raw_sample_per_frame = 0
        with open(inputdata_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and 'raw_sample_count' in line:
                    parts = line.split()
                    try:
                        raw_sample_count = int(parts[-1].split(",")[0])
                    except ValueError:
                        print(f"ValueError: raw_sample_count: {parts[-1]} is not an integer")
                    continue

                if '=' in line and 'raw_samples_per_frame' in line:
                    parts = line.split()
                    try:
                        raw_sample_per_frame = int(parts[-1].split(",")[0])
                    except ValueError:
                        print(f"ValueError: raw_samples_per_frame: {parts[-1]} is not an integer")
                    continue

        return raw_sample_count * raw_sample_per_frame

    def proj_search_replace(self, file_path_list, search_text, replace_text):
        """
        Searches for a specific file in a given directory, reads its content, and replaces occurrences 
        of a specified text with a replacement text.
        """
        proj_path = None
        for root, _, files in os.walk(file_path_list[0]):
            for file in files:
                if file.endswith(file_path_list[1]):
                    proj_path = os.path.join(root, file)
                    break
        if not proj_path.endswith(file_path_list[1]):
            print(f"Could not find {file_path_list[1]} file in {file_path_list[0]} folder")
            return 1

        try:
            with open(proj_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(proj_path, 'w', encoding='utf-8') as f:
                for line in lines:
                    if search_text in line:
                        line = line.replace(search_text, replace_text)
                    f.write(line)
        except OSError:
            print(f"Could not open {proj_path} file")
            return 2

        return 0

    def update_proj_files(self):
        """
        Updates project files by replacing a specific placeholder text with the user-specified filename.
        """

        search_text = 'tflite_learn_672337_3.cpp'
        replace_text = self.ei_c_model_fname
        file_path_list = []

        # Update Keil .uvprojx file (change the template EI model cpp to the user specified one)
        file_path_list = [os.path.join(self.project, 'KEIL'), '.uvprojx']
        if self.proj_search_replace(file_path_list, search_text, replace_text):
            return 1

        # Update Vscode .yml file (change the template EI model cpp to the user specified one)
        file_path_list = [os.path.join(self.project, 'VSCode'), '.cproject.yml']
        if self.proj_search_replace(file_path_list, search_text, replace_text):
            return 1

        return 0

    def update_compiled_model_files(self):
        """
        Updates the compiled Edge Impulse model source file by modifying the tensor arena declaration.
        This method performs the following tasks:
        1. Reads the `kTensorArenaSize` value from the Edge Impulse model source file.
        2. Updates the tensor arena declaration in the source file to use the new size and Nuvoton-specific attributes.
        3. Comments out the original tensor arena declaration if it exists.
        """

        ei_c_model_src_path = os.path.join(self.project, 'edgeimpulse_model', 'tflite-model', self.ei_c_model_fname)

        # read the kTensorArenaSize value from the EI model source file (bcs this ei compiled value doesn't have variable declaration)
        try:
            with open(ei_c_model_src_path, 'r', encoding='utf-8') as file:
                matches = []
                for line in file:
                    # Match the line with the pattern `constexpr int kTensorArenaSize = <value>;`
                    match = re.search(r'constexpr int kTensorArenaSize = (\d+);', line)
                    if match:
                        # Append the matched value to the list
                        matches.append(int(match.group(1)))
                # Return the last match if there are any matches
                if matches:
                    self.tensor_arena_size = int(matches[-1])
                    print(f"Find tensor_arena_size: {self.tensor_arena_size}")
                else:
                    print(f"Error \"constexpr int kTensorArenaSize\" not found, please check: {ei_c_model_src_path}")
                    return 1
        except FileNotFoundError:
            print(f"File not found: {ei_c_model_src_path}")
            return 1
        except Exception as e:
            print(f"An error occurred: {e}")
            return 1


        # update EI model source file for the kTensorArenaSize array
        nvt_stamp = '/* Nuvoton Update. */\n'

        # Nuvoton style for tensor arena declaration
        line_mem_define_new = '#define EI_CLASSIFIER_ALLOCATION_STATIC'
        line_tensor_new = f'uint8_t tensor_arena[{self.tensor_arena_size}]	__attribute__((aligned(16), section(".bss.NoInit.activation_buf_sram")));'
        line_tensor_pattern = re.compile(r'^\}\s*//\s*namespace\s+tflite\s*$')
        line_tensor_added = False

        # comment out the original tensor arena declaration if it exists
        line_comment_out_pattern = re.compile(r'^\s*uint8_t\s+tensor_arena\[kTensorArenaSize\]\s+ALIGN\(16\);\s*$')
        line_comment_out_added = False

        try:
            with open(ei_c_model_src_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            updated_lines = []
            for line in lines:
                if line_tensor_pattern.match(line) and not line_tensor_added:
                    # Add the new line after the namespace block
                    updated_lines.append(line)
                    updated_lines.append('\n')
                    updated_lines.append(nvt_stamp)
                    updated_lines.append(line_mem_define_new + '\n')
                    updated_lines.append(line_tensor_new + '\n')
                    line_tensor_added = True
                elif line_comment_out_pattern.match(line) and not line_comment_out_added:
                    updated_lines.append("// " + line)
                    updated_lines.append(nvt_stamp)
                    line_comment_out_added = True
                else:
                    updated_lines.append(line)

            # Write the updated content back to the file
            with open(ei_c_model_src_path, 'w', encoding='utf-8') as file:
                file.writelines(updated_lines)

            if line_tensor_added and line_comment_out_added:
                print("Update compiled model success.")
            else:
                print("Warning!! Update compiled model fail.")    

        except FileNotFoundError:
            print(f"File not found: {ei_c_model_src_path}")
            return 2
        except Exception as e:
            print(f"An error occurred: {e}")
            return 2

        return 0

    def code_gen(self):
        """
        Generates the InputFiles.hpp file using a Jinja2 template and metadata from the EI model.
        This method performs the following steps:
        """
        print('Run generic EI codegen...')
        #for key, value in self.extra.items():
        #    print(f"extra param: {key}, {value}")

        template_path = os.path.dirname(os.path.abspath(__file__))

        # Generate InputFiles.hpp file
        inputdata_file_path = os.path.join(self.project, 'InputFiles.hpp')
        inputdata_temp_file_path = os.path.join(template_path, 'InputFiles_hpp_tmpl.jinja2')
        print(f'Gen file Path {inputdata_file_path}')
        print(f'Template Path {inputdata_temp_file_path}')

        inputdata_size_1d = self.get_input_data_size_1d()  # get input data size 1D from EI model metadata

        try:
            gen_file = open(inputdata_file_path, "w", encoding="utf-8")
        except OSError:
            print(f"Could not open {inputdata_file_path} file")
            return 'unable_generate'

        with gen_file:
            codegen = InputFilesHPPCodegen()
            codegen.code_gen(gen_file, inputdata_temp_file_path, inputdata_size_1d, self.ei_apikey, self.specify_label)   


        print(f'Update project files for EI model: {self.ei_c_model_fname}')
        # Update project files (Keil .uvprojx and Vscode .json)
        if self.update_proj_files():
            return 'unable_generate'

        if 'compiled' in self.ei_c_model_fname:  # if the ei_learn model is compiled (the compiled model cpp file is not empty)

            # Update compiled EI model file
            if self.update_compiled_model_files():
                return 'unable_generate'

            # Generate main.cpp file (bcs tensor_arena's size is known after read from EI model source file)
            main_file_path = os.path.join(self.project, 'main.cpp')
            main_temp_file_path = os.path.join(template_path, 'main_cpp_tmpl.jinja2')
            print(f'Gen file Path {main_file_path}')
            print(f'Template Path {main_temp_file_path}')

            try:
                gen_file = open(main_file_path, "w", encoding="utf-8")
            except OSError:
                print(f"Could not open {main_file_path} file")
                return 'unable_generate'
            with gen_file:
                codegen = MainCCodegen()
                codegen.code_gen(gen_file, main_temp_file_path, self.tensor_arena_size)

            # copy tensor_arena header file
            tensor_arena_header_dst = os.path.join(self.project, 'export_tensor_arena.h')
            tensor_arena_header_src = os.path.join(template_path, 'export_tensor_arena.h')
            try:
                with open(tensor_arena_header_src, 'r', encoding='utf-8') as src_file:
                    with open(tensor_arena_header_dst, 'w', encoding='utf-8') as dst_file:
                        dst_file.write(src_file.read())
            except OSError:
                print(f"Could not copy {tensor_arena_header_src} to {tensor_arena_header_dst}")
                return 'unable_generate'


        return 'success_generate'
