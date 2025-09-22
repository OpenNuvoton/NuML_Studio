"""
A script to generate Edge Impulse (EI) projects for specific boards by cloning necessary
BSPs, copying templates, and updating model parameters.
"""
import os
import time
import shutil
import stat
import fileinput
from pathlib import Path

import git
from git import RemoteProgress
from tqdm import tqdm

from .generic_ei_codegen.generic_ei_codegen import GenericEICodegen
from .imgclass_ei_codegen.imgclass_ei_codegen import ImgclassEICodegen
from .kws_ei_codegen.kws_ei_codegen import KwsEICodegen

PROJECT_GEN_DIR_PREFIX = 'EI_ProjGen_'

board_list = [
    # board name, MCU, BSP name, BSP URL
    # ['NuMaker-M467HJ', 'M467', 'm460BSP', 'git@github.com:OpenNuvoton/m460bsp.git'],
    # ['NuMaker-M467HJ', 'M467', 'm460bsp', 'https://github.com/OpenNuvoton/m460bsp.git'],
    ['NuMaker-M55M1', 'M55M1', 'M55M1BSP', 'https://github.com/OpenNuvoton/M55M1BSP.git'],
]

ei_proj_list = ['ML_M55M1_SampleCode',
            "https://github.com/OpenNuvoton/ML_M55M1_SampleCode.git",
            "M55M1BSP-3.01.002" # This is the used BSP version, it also the dir name in the SDS git repo
]

application = {
    "generic"  : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "NuEdgeWise",
                    "example_tmpl_proj": "ModelInference_EdgeImpulse"
                     },
    "kws"  : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "NuEdgeWise",
                    "example_tmpl_proj": "KeywordSpotting_EdgeImpulse"
                     },
    "imgclass"  : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "NuEdgeWise",
                    "example_tmpl_proj": "ImgClassInference_EdgeImpulse"
                     },
}

# git clone progress status
class CloneProgress(RemoteProgress):
    """
    A class that extends the `RemoteProgress` class to provide a progress bar
    for tracking the progress of a remote operation, such as cloning a repository.
    """
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

# add project generate argument parser
def add_ei_generate_parser(subparsers, _):
    """Include parser for 'generate' subcommand"""
    parser = subparsers.add_parser("generate_ei", help="generate ml project")
    parser.set_defaults(func=ei_project_generate)
    parser.add_argument("--ei_sdk_path", help="specify the new EI SDK for model-parameters & tflite-model", type=str, required=True)
    parser.add_argument("--output_path", help="specify output file path", required=True)
    parser.add_argument("--board", help="specify target board name", required=True)
    parser.add_argument("--templates_path", help="specify template path")
    parser.add_argument("--application", help="specify application scenario generic/kws/imgclass", default='generic')
    parser.add_argument("--api_key_path", help="specify the Edge Impulse API key file path", default='API_key.txt')
    parser.add_argument("--specify_label", help="specify the label to pull test data from Edge Impulse", default=None)

def get_ei_apikey(key_path):
    """
    Reads and retrieves an API key from a specified file.
    """
    ei_api_key = None
    try:
        with open(key_path, 'r', encoding='utf-8') as file:
            ei_api_key = file.readline().strip()
    except OSError:
        print(f"Could not open API key file: {key_path}")
        return None

    if not ei_api_key:
        print("API key is missing or empty in the specified file.")
        return None

    return ei_api_key

# download board BSP
def download_bsp(board_info, templates_path):
    """
    Clone the Board Support Package (BSP) repository for the specified board if it does not already exist.
    """
    bsp_path = os.path.join(templates_path, board_info[2])
    if os.path.isdir(bsp_path):
        return
    print(f'git clone BSP {board_info[3]} {templates_path}')
    git.Repo.clone_from(board_info[3], bsp_path, branch='master', recursive=False, progress=CloneProgress())

def ei_tesnor_size_update(model_parameters_dir_path, tflite_model_dir_path, mul_factor = 1.2):
    """
    Updates the tensor arena size in the model parameters and TensorFlow Lite model header files.
    """
    # find the tensor arena size in model-parameters and update it
    tensor_arena_size = 0
    model_parameters_tensor_info_file = 'model_metadata.h'
    for file_name in os.listdir(model_parameters_dir_path):
        if file_name == model_parameters_tensor_info_file:
            file_path = os.path.join(model_parameters_dir_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '#define' in line and 'EI_CLASSIFIER_TFLITE_LARGEST_ARENA_SIZE' in line:
                        parts = line.split()
                        try:
                            size = int(parts[-1])
                            tensor_arena_size = size
                            break
                        except ValueError:
                            print(f"ValueError: size: {size} is not an integer")

    # large the original size
    if tensor_arena_size > 0:
        tensor_arena_size = int(mul_factor * tensor_arena_size)          
        print(f"Update ARENA_SIZE to {tensor_arena_size} bytes")
    else:
        print(f"ARENA_SIZE not found in {model_parameters_tensor_info_file}")
        return

    # update the tensor arena size in model-parameters .h files
    for file_name in os.listdir(model_parameters_dir_path):
        if file_name.endswith('.h'):
            file_path = os.path.join(model_parameters_dir_path, file_name)
            lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '#define' in line and 'ARENA_SIZE' in line.upper():
                        parts = line.split()
                        #line = f"#define EI_CLASSIFIER_TENSOR_ARENA_SIZE {tensor_arena_size}\n"
                        parts[-1] = str(tensor_arena_size)
                        line = " ".join(parts) + "\n"
                    lines.append(line)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            with fileinput.FileInput(file_path, inplace=True, encoding='utf-8') as file:
                for line in file:
                    if '#define' in line and 'ARENA_SIZE' in line.upper():
                        parts = line.split()
                        parts[-1] = str(tensor_arena_size)
                        line = " ".join(parts) + "\n"
                    print(line, end='')

    # update the tensor arena size in tflite-model .h files
    for file_name in os.listdir(tflite_model_dir_path):
        if file_name.endswith('.h'):
            file_path = os.path.join(tflite_model_dir_path, file_name)
            lines = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '#define' in line and 'ARENA_SIZE' in line.upper():
                        parts = line.split()
                        parts[-1] = str(tensor_arena_size)
                        line = " ".join(parts) + "\n"

                    if '=' in line and 'ARENA_SIZE' in line.upper():
                        parts = line.split()
                        parts[-1] = str(tensor_arena_size) + ';' # C's style
                        line = " ".join(parts) + "\n"

                    lines.append(line)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

def add_long_path_prefix(path: str) -> str:
    # Always normalize to absolute path with backslashes
    abs_path = os.path.abspath(path)
    abs_path = abs_path.replace("/", "\\")   # ensure backslashes only
    if abs_path.startswith("\\\\?\\"):
        return abs_path
    return "\\\\?\\" + abs_path

def prepare_ei_proj_resource(board_info, project_path, templates_path, new_ei_sdk_path, example_tmpl_dir, example_tmpl_proj, example_proj_list):
    """
    Prepares the resources for an Edge Impulse (EI) project by copying necessary files and directories 
    to the autogenerated project directory.
    """
    print('copy resources to autogen project directory')

    bsp_lib_src_path = os.path.join(templates_path, board_info[2], 'Library')
    bsp_lib_dest_path = os.path.join(project_path, board_info[2], 'Library')
    print('copy bsp library to autogen project directory')
    shutil.copytree(add_long_path_prefix(bsp_lib_src_path), add_long_path_prefix(bsp_lib_dest_path), dirs_exist_ok = True)

    bsp_thirdparty_src_path = os.path.join(templates_path, board_info[2], 'ThirdParty')
    bsp_thirdparty_dest_path = os.path.join(project_path, board_info[2], 'ThirdParty')

    bsp_thirdparty_fatfs_src_path = os.path.join(bsp_thirdparty_src_path, 'FatFs')
    bsp_thirdparty_fatfs_dest_path = os.path.join(bsp_thirdparty_dest_path, 'FatFs') 
    print('copy BSP ThirdParty FatFs ...')
    shutil.copytree(add_long_path_prefix(bsp_thirdparty_fatfs_src_path), add_long_path_prefix(bsp_thirdparty_fatfs_dest_path), dirs_exist_ok = True)

    bsp_thirdparty_openmv_src_path = os.path.join(bsp_thirdparty_src_path, 'openmv')
    bsp_thirdparty_openmv_dest_path = os.path.join(bsp_thirdparty_dest_path, 'openmv')
    print('copy BSP ThirdParty openmv ...')
    shutil.copytree(add_long_path_prefix(bsp_thirdparty_openmv_src_path), add_long_path_prefix(bsp_thirdparty_openmv_dest_path), dirs_exist_ok = True)

    bsp_thirdparty_ml_evk_src_path = os.path.join(bsp_thirdparty_src_path, 'ml-embedded-evaluation-kit')
    bsp_thirdparty_ml_evk_dest_path = os.path.join(bsp_thirdparty_dest_path, 'ml-embedded-evaluation-kit')
    print('copy BSP ThirdParty ml-embedded-evaluation-kit ...')
    shutil.copytree(add_long_path_prefix(bsp_thirdparty_ml_evk_src_path), add_long_path_prefix(bsp_thirdparty_ml_evk_dest_path), dirs_exist_ok = True)

    bsp_patch_src_path = os.path.join(templates_path, board_info[1], 'BSP_patch')
    bsp_dest_path = os.path.join(project_path, board_info[2])

    if os.path.exists(bsp_patch_src_path):
        print('copy bsp library patch to autogen project directory')
        shutil.copytree(add_long_path_prefix(bsp_patch_src_path), add_long_path_prefix(bsp_dest_path), dirs_exist_ok = True)

    # copy whole EI project from ML_SampleCode ei_proj_list
    example_template_path = os.path.join(templates_path, example_proj_list[0], example_proj_list[2], 'SampleCode', example_tmpl_dir, example_tmpl_proj)
    example_project_path = os.path.join(bsp_dest_path, 'SampleCode', example_tmpl_dir, example_tmpl_proj)
    if os.path.exists(example_project_path):  # remove read only attribute
        remove_read_only(example_project_path)
    else:
        remove_read_only(example_template_path)
    print(f"example_template_path: {example_template_path}")
    print(f"example_project_path: {example_project_path}")
    print('copy example template project to autogen MachineLearning example folder')
    shutil.copytree(add_long_path_prefix(example_template_path), add_long_path_prefix(example_project_path), dirs_exist_ok=True)

    # copy .vscode for vscode cmsis project setting
    vscode_set_path = os.path.join(templates_path, board_info[1], board_info[0], 'vscode_set')
    vscode_set_project_path = bsp_dest_path
    print(f"vscode_set_path: {vscode_set_path}")
    print(f"vscode_set_project_path: {vscode_set_project_path}")
    print('copy .vscode to project folder')
    shutil.copytree(add_long_path_prefix(vscode_set_path), add_long_path_prefix(vscode_set_project_path), dirs_exist_ok=True)

    # copy edgeimpulse sdk
    example_template_path = Path(templates_path, example_proj_list[0], example_proj_list[2], 'ThirdParty', 'edgeimpulse')
    example_project_path = Path(bsp_dest_path, 'ThirdParty', 'edgeimpulse')
    print(f"example_template_path: {example_template_path}")
    print(f"example_project_path: {example_project_path}")
    print('copy edgeimpulse sdk...')
    shutil.copytree(add_long_path_prefix(example_template_path), add_long_path_prefix(example_project_path), dirs_exist_ok=True)

    # copy the user's new model folders
    example_project_path = os.path.join(bsp_dest_path, 'SampleCode', example_tmpl_dir, example_tmpl_proj)
    example_model_parameters_src_dir = os.path.join(new_ei_sdk_path, 'model-parameters')
    example_tflite_model_src_dir = os.path.join(new_ei_sdk_path, 'tflite-model')
    print(f"example_project_path: {example_project_path}")
    print(f"example_model_parameters_dir: {example_model_parameters_src_dir}")
    print(f"example_tflite_model_dir: {example_tflite_model_src_dir}")

    print('copy the new model...')
    # remove the dst model dir first, bcs for new version, the model/parameters files name maybe changed
    example_project_edgeimpulse_dir = os.path.join(example_project_path, 'edgeimpulse_model')

    try:
        shutil.rmtree(example_project_edgeimpulse_dir)
    except OSError as e:
        print(f"Error rmtree {example_project_edgeimpulse_dir}: {e}")

    shutil.copytree(add_long_path_prefix(example_model_parameters_src_dir), add_long_path_prefix(os.path.join(example_project_edgeimpulse_dir, 'model-parameters')), dirs_exist_ok=True)
    shutil.copytree(add_long_path_prefix(example_tflite_model_src_dir), add_long_path_prefix(os.path.join(example_project_edgeimpulse_dir, 'tflite-model')), dirs_exist_ok=True)

    # find the name of tflite_learn_compiled model
    compiled_model_filename =None
    for _, _, files in os.walk(os.path.join(example_project_edgeimpulse_dir, 'tflite-model')):
        for file in files:
            if 'tflite_learn' in file and file.endswith('.cpp'):
                compiled_model_filename = file
                break
    print(f"EI compiled model (EON or not): {compiled_model_filename}")

    # update the tensor arena size of EI's model (It needs larger size for real HW)
    start_time = time.time()
    ei_tesnor_size_update(os.path.join(example_project_edgeimpulse_dir, 'model-parameters'), os.path.join(example_project_edgeimpulse_dir, 'tflite-model'))
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"execution_time: {execution_time}s")

    return example_project_path, compiled_model_filename


def remove_read_only(folder_path):
    """
    Removes the read-only attribute from a folder and its contents, excluding specified directories.
    """
    dirs_to_skip = ["tmp", "out"]
    for root, dirs, files in os.walk(folder_path):
        # Remove directories to skip from the dirs list
        dirs[:] = [dir_name for dir_name in dirs if dir_name not in dirs_to_skip]

        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.chmod(dir_path, stat.S_IWRITE)
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.chmod(file_path, stat.S_IWRITE)
    # Remove read-only from the folder itself
    os.chmod(folder_path, stat.S_IWRITE)

# project generate main function
def ei_project_generate(args):
    """
    Generates an Edge Impulse (EI) project based on the provided arguments.
    """
    templates_path = args.templates_path
    application_usage = args.application

    if not application_usage in application:
        print("applicaiton not found! using generic instead")
        application_usage = "generic"

    application_param = application[application_usage]

    if templates_path is None:
        templates_path = os.path.join(os.path.dirname(__file__), 'templates')

    board_found = False

    for board_info in board_list:
        if board_info[0] == args.board:
            board_found = True
            download_bsp(board_info, templates_path)
            break

    if board_found is False:
        print("board not support")
        return 'unable_generate'

    # create ouput directory, if output directory is not exist
    if not os.path.exists(args.output_path):
        os.mkdir(args.output_path)

    # generated project directory
    project_path = os.path.join(args.output_path, PROJECT_GEN_DIR_PREFIX + args.board)
    if not os.path.exists(project_path):
        os.mkdir(project_path)

    # copy the EI's model dirs to output directory

    # prepare project resource
    example_tmpl_dir = application_param["example_tmpl_dir"]
    example_tmpl_proj = application_param["example_tmpl_proj"]
    example_proj_list = ei_proj_list # edge impulse template project
    project_example_path, ei_c_model_fname = prepare_ei_proj_resource(board_info, project_path, templates_path, args.ei_sdk_path, example_tmpl_dir, example_tmpl_proj, example_proj_list)
    print(f"Gen Project Example Path: {project_example_path}")

    # Generate mode.hpp/cpp or main.cpp
    ei_apikey = get_ei_apikey(args.api_key_path)
    if application_usage == 'generic':
        # For auto test data generation, we need API_KEY & which label
        codegen = GenericEICodegen.from_args(project_example_path, ei_apikey, app='generic', specify_label=args.specify_label, ei_c_model_fname = ei_c_model_fname)
    elif application_usage == 'imgclass':
        # For auto test data generation, we need API_KEY & which label
        codegen = ImgclassEICodegen.from_args(project_example_path, ei_apikey, app='imgclass', specify_label=args.specify_label, ei_c_model_fname = ei_c_model_fname)
    elif application_usage == 'kws':
        # For auto test data generation, we need API_KEY & which label
        codegen = KwsEICodegen.from_args(project_example_path, ei_apikey, app='imgclass', specify_label=args.specify_label, ei_c_model_fname = ei_c_model_fname)
    else:
        print("application not support")
        return 'unable_generate'

    if codegen.code_gen() == 'unable_generate':
        print("codegen failed")
        return 'unable_generate'

    print(f'Example project completed at {os.path.abspath(project_example_path)}')

    return project_example_path
    