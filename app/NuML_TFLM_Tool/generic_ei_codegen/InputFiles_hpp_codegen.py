import os
import json
import io
from PIL import Image
from random import randrange

from jinja2 import Environment, FileSystemLoader
import numpy as np
from edgeimpulse.experimental.data import (
    get_sample_ids,
    download_samples_by_ids,
)

DEBUG_LOG = False

def pull_ei_representative_data(api_key, specify_label = None, download_num = 4):
    # 1. Get sample IDs (optionally filter by category etc.)
    try:
        sample_infos = get_sample_ids( category="testing", api_key=api_key)
    except Exception as e:
        print("Error retrieving get_sample_ids:", str(e))
        return None

    if not sample_infos:
        print("Warning: No sample infos retrieved. Please check your API key and project settings.")
        return None

    # 2. Extract the IDs for unique label
    unique_samples = {}
    filename_list = []
    for info in sample_infos:
        if info.label not in unique_samples:
            unique_samples[info.label] = info.sample_id
            filename_list.append(info.filename)
    ids = list(unique_samples.values())

    if not ids:
        print("Warning: No any label (info.label) retrieved. Please check your project settings and data label.")
        return None

    # 2-1. Choose only one label if specified (e.g., "left") or randomly pick one samples
    if specify_label:
        try:
            sample_id = unique_samples[specify_label]
            ids = [sample_id]
        except KeyError:
            print(f"Label '{specify_label}' not found in unique_samples. Picking a random sample.")
            ids = ids[randrange(len(filename_list))]
    else:
        ids = ids[randrange(len(filename_list))]

    # 3. Download samples by IDs
    flattened_values = []
    samples = download_samples_by_ids(sample_ids=ids, api_key=api_key, show_progress=True)

    for sample in samples:
        print(f"Choose {specify_label} test data:")
        print("Filename:", sample.filename, "– Label:", sample.label, "– Id:", sample.sample_id)

        if isinstance(sample.data, str):
            sample_json = json.loads(sample.data)

            if DEBUG_LOG:
                with open(f"{sample.filename}", "w", encoding="utf-8") as f:
                    json.dump(sample_json, f)

            # convert the data to 1 dim
            values = sample_json.get("payload", {}).get("values", [])
            flattened_values = np.array(values).flatten().tolist()

        elif isinstance(sample.data, io.BytesIO):
            if sample.filename.endswith(('.png', '.jpg', '.jpeg')):  # Image, not implemented/tested on C++ fw yet 
                sample.data.seek(0)
                img = Image.open(sample.data)
                img_np = np.array(img)

                if DEBUG_LOG:
                    np.save("image_sample.npy", img_np)
                    img.save("image_sample.png")

                flattened_values = np.array(img_np).flatten().tolist()
            elif sample.filename.endswith(('.wav')):   # audio, not implemented/tested on C++ fw yet
                sample.data.seek(0)
                audio_bytes = sample.data.read()
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

                if DEBUG_LOG:
                    np.save("audio_sample.npy", audio_np)
                    with open("audio_sample.wav", "wb") as f:
                        f.write(audio_bytes)

                flattened_values = np.array(audio_np).flatten().tolist()        
            else:
                print("Unknown file type for", sample)
                sample_json = json.loads(sample.data.seek(0))

                if DEBUG_LOG:
                    with open("sample.json", "w", encoding="utf-8") as f:
                        json.dump(sample_json, f, indent=2)

                # convert the data to 1 dim
                values = sample_json.get("payload", {}).get("values", [])
                flattened_values = np.array(values).flatten().tolist()        
        else:
            print("Unknown data type for", sample)


    szwriteline = ', '.join(map(str, flattened_values))
    return szwriteline

class InputFilesHPPCodegen:
    def code_gen(self, gen_file, temp_file_path, inputdata_size_1d, ei_apikey, specify_label=None):


        tmpl_dirname = os.path.dirname(temp_file_path)
        tmpl_basename = os.path.basename(temp_file_path)
        env =  Environment(loader=FileSystemLoader(tmpl_dirname), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(tmpl_basename)

        # check ei_apikey
        define_input_test_data_str = None
        if not ei_apikey or len(ei_apikey) < 10:
            print("Invalid or missing Edge Impulse API key")
            # use default data (values), just get the length right
            gen_fake_data = [0.5] * inputdata_size_1d
            define_input_test_data_str = ', '.join(map(str, gen_fake_data))
        else:
            define_input_test_data_str = pull_ei_representative_data(ei_apikey, specify_label)
            if not define_input_test_data_str:
                print("Warning: Failed to pull representative data from Edge Impulse. Using default data (0.5) instead.")
                gen_fake_data = [0.5] * inputdata_size_1d
                define_input_test_data_str = ', '.join(map(str, gen_fake_data))

        output = template.render(define_input_test_data = define_input_test_data_str)
        gen_file.write(output)
