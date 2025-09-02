import os

from .InputFiles_hpp_codegen import InputFilesHPPCodegen

class GenericEICodegen:
    def __init__(self, project, ei_apikey, **kwargs):
        self.project = project
        self.ei_apikey = ei_apikey
        self.specify_label = kwargs.get('specify_label', None)
        self.extra = kwargs

    @classmethod
    def from_args(cls, *args, **kwargs):
        return cls(*args, **kwargs)
    
    def get_input_data_size_1d(self):
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
    
    def code_gen(self):
        print('Run generic EI codegen...')
        #for key, value in self.extra.items():
        #    print(f"extra param: {key}, {value}")

        template_path = os.path.dirname(os.path.abspath(__file__))

        # Generate InputFiles.hpp file
        inputdata_file_path = os.path.join(self.project, 'InputFiles.hpp')
        inputdata_temp_file_path = os.path.join(template_path, 'InputFiles_hpp_tmpl.jinja2')
        print(f'Gen file Path {inputdata_file_path}')
        print(f'Template Path {inputdata_temp_file_path}')

        # get input data size 1D from EI model metadata
        inputdata_size_1d = self.get_input_data_size_1d()

        try:
            gen_file = open(inputdata_file_path, "w", encoding="utf-8")
        except OSError:
            print(f"Could not open {inputdata_file_path} file")
            return 'unable_generate'

        with gen_file:
            codegen = InputFilesHPPCodegen()
            codegen.code_gen(gen_file, inputdata_temp_file_path, inputdata_size_1d, self.ei_apikey, self.specify_label)

