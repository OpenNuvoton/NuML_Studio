import sys
import re
import pandas

FLASH_SIZE_LIMIT = 1.4 * 1024000

# parse vela summary file to get memory usage information


def vela_summary_parse(summary_file):
    """
    Parses a Vela summary CSV file to extract memory usage information.
    """
    usecols = ['sram_memory_used', 'off_chip_flash_memory_used']
    df = pandas.read_csv(summary_file, usecols=usecols)
    return df.iloc[0, 0]*1024, df.iloc[0, 1]*1024


class MainSDSCCodegen:
    """
    MainSDSCCodegen is a class responsible for generating C++ code sections for a main file based on 
    model memory usage and other parameters. It processes a template file and inserts auto-generated 
    sections based on specific keywords.
    """

    def __init__(self):
        self.model_sram_usage = None
        self.model_flash_usage = None
        # default values for frame per second and window time size for model input sample
        self.fps, self.win_time = 100, 2

        model_sd_list = ["Model in SD", self.add_model_load_section]
        activation_size_list = ["Activation size",
                                self.add_activation_size_section]
        number_input_sample_list = [
            "Number of input sample", self.add_number_input_sample_section]

        self.keyword_table = [model_sd_list,
                              activation_size_list, number_input_sample_list]

    def add_activation_size_section(self, main_cpp_file, sram_usage, flash_usage):
        """
        Adds a section to the main C++ file defining the activation buffer size.
        """
        activation_size = int(sram_usage * 1.4)
        activation_size &= ~(1024 - 1)
        activation_size = max(activation_size, 1024 * 1)  # Ensure at least 2KB
        sz_write_line = '#define ACTIVATION_BUF_SZ (' + \
            str(activation_size) + ')\n'

        main_cpp_file.write(sz_write_line)

    def add_model_load_section(self, main_cpp_file, sram_usage, flash_usage):
        """
        Adds a model load section directive to the main C++ file based on memory usage.
        """
        if flash_usage > FLASH_SIZE_LIMIT:
            sz_write_line = '#define __LOAD_MODEL_FROM_SD__\n'
        else:
            sz_write_line = '//#define __LOAD_MODEL_FROM_SD__\n'

        main_cpp_file.write(sz_write_line)

    def add_number_input_sample_section(self, main_cpp_file, frame_per_second=100, window_time_size=2):
        """
        Adds a section to the main C++ file defining the number of input samples
        for the MPU6500 sensor based on the specified frame rate and window size.
        """

        sz_write_line = f'#define INPUT_SAMPLE_NUMBER_MPU6500      {str(frame_per_second * window_time_size)}U\n'

        main_cpp_file.write(sz_write_line)

    def code_gen(self, main_file, template_file, vela_summary_file):
        """
        Generates code by processing a template file and writing to a main file.
        """

        # get model memory usage information from vela summary output file
        self.model_sram_usage, self.model_flash_usage = vela_summary_parse(
            vela_summary_file)
        print(self.model_sram_usage)
        print(self.model_flash_usage)

        while template_file:
            line = template_file.readline()
            if line == "":
                break
            main_file.write(line)
            if re.search("autogen section", line):
                for list_element in self.keyword_table:
                    if re.search(list_element[0], line):
                        if list_element[0] == "Number of input sample":
                            line = template_file.readline()
                            main_file.write(line)
                            list_element[1](
                                main_file, self.fps, self.win_time)
                        else:
                            line = template_file.readline()
                            main_file.write(line)
                            list_element[1](
                                main_file, self.model_sram_usage, self.model_flash_usage)
