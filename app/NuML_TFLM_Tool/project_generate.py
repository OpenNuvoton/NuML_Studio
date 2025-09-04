import argparse
import logging
import sys
import os
import pathlib
import git
import shutil
import subprocess
import tarfile
import stat

from git import RemoteProgress
from tqdm import tqdm

from .generic_codegen.generic_codegen import GenericCodegen
from .imgclass_codegen.imgclass_codegen import ImgClassCodegen
from .sdsgsensor_codegen.sdsgsensor_codegen import SdsGsensorCodegen

PROJECT_GEN_DIR_PREFIX = 'ProjGen_'

board_list = [
    # board name, MCU, BSP name, BSP URL
    # ['NuMaker-M467HJ', 'M467', 'm460BSP', 'git@github.com:OpenNuvoton/m460bsp.git'],
    # ['NuMaker-M467HJ', 'M467', 'm460bsp', 'https://github.com/OpenNuvoton/m460bsp.git'],
    ['NuMaker-M55M1', 'M55M1', 'M55M1BSP', 'https://github.com/OpenNuvoton/M55M1BSP.git'],
]

sds_list = ['ML_M55M1_CMSIS_SDS',
            "https://github.com/MaxCYCHEN/ML_M55M1_CMSIS_SDS.git",
            "M55M1BSP-3.01.002" # This is the used BSP version, it also the dir name in the SDS git repo
]

project_type_list = ['uvision5_armc6', 'make_gcc_arm', 'vscode']

application = {
    "generic"   : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "generic_template",
                    "example_tmpl_proj": "NN_ModelInference"
                  },
    "imgclass"  : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "imgclass_template",
                    "example_tmpl_proj": "NN_ImgClassInference"
                  },
    "objdet"  : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "objdet_template",
                    "example_tmpl_proj": "NN_ObjDetInference"
                  },
    "gsensor_sds"  : {
                    "board": ['NuMaker-M55M1'],
                    "example_tmpl_dir": "SDS", # This is from sds_list dir structure
                    "example_tmpl_proj": "NN_ModelInference_SDS" # This is from sds_list dir structure
                     },            
}

# git clone progress status
class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

# add project generate argument parser
def add_generate_parser(subparsers, _):
    """Include parser for 'generate' subcommand"""
    parser = subparsers.add_parser("generate", help="generate ml project")
    parser.set_defaults(func=project_generate)
    parser.add_argument("--model_file", help="specify tflte file", type=str, required=True)
    parser.add_argument("--output_path", help="specify output file path", required=True)
    parser.add_argument("--board", help="specify target board name", required=True)
    parser.add_argument("--project_type", help="specify project type uvision5_armc6/make_gcc_arm/vscode", default='make_gcc_arm')
    parser.add_argument("--templates_path", help="specify template path")
    parser.add_argument("--model_arena_size", help="specify the size of arena cache memory in bytes", default='0')
    parser.add_argument("--application", help="specify application scenario generic/imgclass/gsensor_sds", default='generic')

# download board BSP
def download_bsp(board_info, templates_path):
    bsp_path = os.path.join(templates_path, board_info[2])
    if os.path.isdir(bsp_path):
        return
    print(f'git clone BSP {board_info[3]} {templates_path}')
    git.Repo.clone_from(board_info[3], bsp_path, branch='master', recursive=False, progress=CloneProgress())

def download_sds_bsp(templates_path):
    bsp_path = os.path.join(templates_path, sds_list[0])
    if os.path.isdir(bsp_path):
        return
    print(f'git clone SDS BSP {sds_list[1]} {templates_path}')
    git.Repo.clone_from(
        sds_list[1], bsp_path, recursive=False, progress=CloneProgress())

# INT8 model compile by vela
def model_compile(board_info, output_path, vela_dir_path, model_file, model_arena_size):
    cur_work_dir = os.getcwd()
    os.chdir(output_path)
    vela_exe = os.path.join(vela_dir_path, 'vela-4_0_1.exe')
    vela_conf_file = os.path.join(vela_dir_path, 'default_vela.ini')
    vela_conifg_option = '--config='+vela_conf_file
    print(output_path)
    print(vela_conifg_option)
    print(model_file)
    print(model_arena_size)
    print(vela_exe)

    vela_cmd = [vela_exe, model_file, '--accelerator-config=ethos-u55-256', '--optimise=Performance', vela_conifg_option, '--memory-mode=Shared_Sram', '--system-config=Ethos_U55_High_End_Embedded', '--output-dir=.']

    if int(model_arena_size) > 0:
        vela_cmd.extend(['--arena-cache-size', model_arena_size])

    print(vela_cmd)
    ret = subprocess.run(vela_cmd)
    if ret.returncode == 0:
        print('vela compile done')
    else:
        print('Unable compile failee')
        return False

    os.chdir(cur_work_dir)
    return True

# parse vela summary file to get memory usage information
def vela_summary_parse(summary_file):
    usecols = ['sram_memory_used', 'off_chip_flash_memory_used']
    df = pandas.read_csv(summary_file, usecols=usecols)
    return df.iloc[0,0]*1024, df.iloc[0,1]*1024

# generate tflite cpp file
def generate_model_cpp(output_path, tflite2cpp_dir_path, model_file):
    cur_work_dir = os.getcwd()
    print(cur_work_dir)
    os.chdir(output_path)
    model2cpp_exe = os.path.join(tflite2cpp_dir_path, 'gen_model_cpp.exe')
    template_dir = os.path.join(tflite2cpp_dir_path, 'templates')
    model2cpp_cmd = [model2cpp_exe, '--tflite_path', model_file, '--output_dir','.', '--template_dir', template_dir, '-ns', 'arm', '-ns', 'app', '-ns', 'nn']
    print(model2cpp_cmd)

    ret = subprocess.run(model2cpp_cmd)
    if ret.returncode == 0:
        print('tflite2cpp done')
    else:
        print('Unable generate cpp')
        return False

    os.chdir(cur_work_dir)
    return True

def prepare_proj_resource(board_info, project_path, templates_path, vela_model_file, vela_model_cc_file, example_tmpl_dir, example_tmpl_proj):
    print('copy resources to autogen project directory')

    bsp_lib_src_path = os.path.join(templates_path, board_info[2], 'Library')
    bsp_lib_dest_path = os.path.join(project_path, board_info[2], 'Library')
    print('copy bsp library to autogen project directory')
    """ Temp del for testing
    """
    shutil.copytree(bsp_lib_src_path, bsp_lib_dest_path, dirs_exist_ok = True)

    bsp_thirdparty_src_path = os.path.join(templates_path, board_info[2], 'ThirdParty')
    bsp_thirdparty_dest_path = os.path.join(project_path, board_info[2], 'ThirdParty')

    bsp_thirdparty_tflite_micro_src_path = os.path.join(bsp_thirdparty_src_path, 'tflite_micro')
    bsp_thirdparty_tflite_micro_dest_path = os.path.join(bsp_thirdparty_dest_path, 'tflite_micro')
    print('copy BSP ThirdParty tflite_micro ...')
    shutil.copytree(bsp_thirdparty_tflite_micro_src_path, bsp_thirdparty_tflite_micro_dest_path, dirs_exist_ok = True)

    bsp_thirdparty_fatfs_src_path = os.path.join(bsp_thirdparty_src_path, 'FatFs')
    bsp_thirdparty_fatfs_dest_path = os.path.join(bsp_thirdparty_dest_path, 'FatFs') 
    print('copy BSP ThirdParty FatFs ...')
    shutil.copytree(bsp_thirdparty_fatfs_src_path, bsp_thirdparty_fatfs_dest_path, dirs_exist_ok = True)

    bsp_thirdparty_openmv_src_path = os.path.join(bsp_thirdparty_src_path, 'openmv')
    bsp_thirdparty_openmv_dest_path = os.path.join(bsp_thirdparty_dest_path, 'openmv')
    print('copy BSP ThirdParty openmv ...')
    shutil.copytree(bsp_thirdparty_openmv_src_path, bsp_thirdparty_openmv_dest_path, dirs_exist_ok = True)

    bsp_thirdparty_ml_evk_src_path = os.path.join(bsp_thirdparty_src_path, 'ml-embedded-evaluation-kit')
    bsp_thirdparty_ml_evk_dest_path = os.path.join(bsp_thirdparty_dest_path, 'ml-embedded-evaluation-kit')
    print('copy BSP ThirdParty ml-embedded-evaluation-kit ...')
    shutil.copytree(bsp_thirdparty_ml_evk_src_path, bsp_thirdparty_ml_evk_dest_path, dirs_exist_ok = True)
    # copy .cc to .cpp
    ml_evk_source_dir = os.path.join(bsp_thirdparty_ml_evk_dest_path, 'source', 'application', 'api', 'common', 'source')

    # Loop through all files in the directory
    for filename in os.listdir(ml_evk_source_dir):
        if filename.endswith('.cc'):
            # Construct full file path
            old_file = os.path.join(ml_evk_source_dir, filename)
            new_file = os.path.join(ml_evk_source_dir, filename.replace('.cc', '.cpp'))

            # copy the file
            shutil.copyfile(old_file, new_file)
            print(f'copy {old_file} to {new_file}')

    ml_evk_source_dir = os.path.join(bsp_thirdparty_ml_evk_dest_path, 'source', 'math')

    # Loop through all files in the directory
    for filename in os.listdir(ml_evk_source_dir):
        if filename.endswith('.cc'):
            # Construct full file path
            old_file = os.path.join(ml_evk_source_dir, filename)
            new_file = os.path.join(ml_evk_source_dir, filename.replace('.cc', '.cpp'))

            # copy the file
            shutil.copyfile(old_file, new_file)
            print(f'copy {old_file} to {new_file}')


    ml_evk_source_dir = os.path.join(bsp_thirdparty_ml_evk_dest_path, 'source', 'profiler')

    # Loop through all files in the directory
    for filename in os.listdir(ml_evk_source_dir):
        if filename.endswith('.cc'):
            # Construct full file path
            old_file = os.path.join(ml_evk_source_dir, filename)
            new_file = os.path.join(ml_evk_source_dir, filename.replace('.cc', '.cpp'))

            # copy the file
            shutil.copyfile(old_file, new_file)
            print(f'copy {old_file} to {new_file}')


    bsp_patch_src_path = os.path.join(templates_path, board_info[1], 'BSP_patch')
    bsp_dest_path = os.path.join(project_path, board_info[2])
    if os.path.exists(bsp_patch_src_path):
        print('copy bsp library patch to autogen project directory')
        shutil.copytree(bsp_patch_src_path, bsp_dest_path, dirs_exist_ok = True)

    example_template_path = os.path.join(templates_path, board_info[1], board_info[0], example_tmpl_dir)
    example_project_path = os.path.join(bsp_dest_path, 'SampleCode', 'MachineLearning')
    example_project_src_path = os.path.join(example_template_path, example_tmpl_proj)

    print(example_template_path)
    print(example_project_src_path)
    print(example_project_path)

    print('copy example template project to autogen MachineLearning example folder')
    example_project_path = os.path.join(example_project_path, example_tmpl_proj)
    shutil.copytree(example_project_src_path, example_project_path, dirs_exist_ok = True)
    
    example_project_model_cpp_file = os.path.join(example_project_path, 'Model', 'NN_Model_INT8.tflite.cpp')
    example_project_model_dir = os.path.join(example_project_path, 'Model')
    shutil.copyfile(vela_model_cc_file, example_project_model_cpp_file)
    shutil.copy(vela_model_file, example_project_model_dir)

    print('copy link script')
    link_script_keil_src_file = os.path.join(templates_path, board_info[1], board_info[0], example_tmpl_dir, 'link_script', 'armcc', 'armcc.scatter')
    link_script_keil_dest_file = os.path.join(example_project_path, 'KEIL', 'armcc.scatter')
    shutil.copyfile(link_script_keil_src_file, link_script_keil_dest_file)

    link_script_gcc_src_file = os.path.join(templates_path, board_info[1], board_info[0], example_tmpl_dir, 'link_script', 'gcc', 'gcc.ld')
    link_script_gcc_dest_file = os.path.join(example_project_path, 'GCC', 'gcc.ld')
    shutil.copyfile(link_script_gcc_src_file, link_script_gcc_dest_file)

    print('copy progen records to autogen project directory')
    progen_src_path = os.path.join(templates_path, board_info[1], board_info[0], example_tmpl_dir, 'progen')
    progen_dest_path = os.path.join(example_project_path, '..')

    shutil.copytree(os.path.join(progen_src_path, 'tools'), os.path.join(progen_dest_path, 'tools'), dirs_exist_ok = True)
    shutil.copyfile(os.path.join(progen_src_path, 'project.yaml'), os.path.join(progen_dest_path, 'project.yaml'))
    
    # vscode setting
    vscode_set_path = os.path.join(templates_path, board_info[1], board_info[0], 'vscode_set')
    vscode_set_project_path = bsp_dest_path

    print(vscode_set_path)
    print(vscode_set_project_path)

    print('copy .vscode to project folder')
    shutil.copytree(vscode_set_path, vscode_set_project_path, dirs_exist_ok=True)

    return example_project_path


def remove_read_only(folder_path):
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

def prepare_vscode_sds_proj_resource(board_info, project_path, templates_path, vela_model_file, vela_model_cc_file, example_tmpl_dir, example_tmpl_proj):
    print('copy resources to autogen project directory')

    bsp_lib_src_path = os.path.join(templates_path, board_info[2], 'Library')
    bsp_lib_dest_path = os.path.join(project_path, board_info[2], 'Library')
    print('copy bsp library to autogen project directory')
    shutil.copytree(bsp_lib_src_path, bsp_lib_dest_path, dirs_exist_ok=True)

    bsp_thirdparty_src_path = os.path.join(
        templates_path, board_info[2], 'ThirdParty')
    bsp_thirdparty_dest_path = os.path.join(
        project_path, board_info[2], 'ThirdParty')

    bsp_thirdparty_tflite_micro_src_path = os.path.join(
        bsp_thirdparty_src_path, 'tflite_micro')
    bsp_thirdparty_tflite_micro_dest_path = os.path.join(
        bsp_thirdparty_dest_path, 'tflite_micro')
    print('copy BSP ThirdParty tflite_micro ...')
    shutil.copytree(bsp_thirdparty_tflite_micro_src_path,
                    bsp_thirdparty_tflite_micro_dest_path, dirs_exist_ok=True)

    bsp_thirdparty_fatfs_src_path = os.path.join(
        bsp_thirdparty_src_path, 'FatFs')
    bsp_thirdparty_fatfs_dest_path = os.path.join(
        bsp_thirdparty_dest_path, 'FatFs')
    print('copy BSP ThirdParty FatFs ...')
    shutil.copytree(bsp_thirdparty_fatfs_src_path,
                    bsp_thirdparty_fatfs_dest_path, dirs_exist_ok=True)

    bsp_thirdparty_openmv_src_path = os.path.join(
        bsp_thirdparty_src_path, 'openmv')
    bsp_thirdparty_openmv_dest_path = os.path.join(
        bsp_thirdparty_dest_path, 'openmv')
    print('copy BSP ThirdParty openmv ...')
    shutil.copytree(bsp_thirdparty_openmv_src_path,
                    bsp_thirdparty_openmv_dest_path, dirs_exist_ok=True)

    bsp_thirdparty_ml_evk_src_path = os.path.join(
        bsp_thirdparty_src_path, 'ml-embedded-evaluation-kit')
    bsp_thirdparty_ml_evk_dest_path = os.path.join(
        bsp_thirdparty_dest_path, 'ml-embedded-evaluation-kit')
    print('copy BSP ThirdParty ml-embedded-evaluation-kit ...')
    shutil.copytree(bsp_thirdparty_ml_evk_src_path,
                    bsp_thirdparty_ml_evk_dest_path, dirs_exist_ok=True)

    bsp_patch_src_path = os.path.join(
        templates_path, board_info[1], 'BSP_patch')
    bsp_dest_path = os.path.join(project_path, board_info[2])
    if os.path.exists(bsp_patch_src_path):
        print('copy bsp library patch to autogen project directory')
        shutil.copytree(bsp_patch_src_path, bsp_dest_path, dirs_exist_ok=True)

    # copy whole sds vscode project from downloaded SDS BSP
    example_template_path = os.path.join(
        templates_path, sds_list[0], sds_list[2], 'SampleCode', example_tmpl_dir, example_tmpl_proj)
    example_project_path = os.path.join(
        bsp_dest_path, 'SampleCode', 'MachineLearning', example_tmpl_proj)
    if os.path.exists(example_project_path):  # remove read only attribute
        remove_read_only(example_project_path)
    else:
        remove_read_only(example_template_path)
    print(example_template_path)
    print(example_project_path)
    print('copy example template project to autogen MachineLearning example folder')
    shutil.copytree(example_template_path,
                    example_project_path, dirs_exist_ok=True)

    # copy .vscode for vscode cmsis project setting
    example_vsset_path = os.path.join(
        templates_path, sds_list[0], '.vscode')
    example_project_vsset_path = os.path.join(
        bsp_dest_path, '.vscode')
    print(example_vsset_path)
    print(example_project_vsset_path)
    print('copy .vscode setting to autogen MachineLearning example folder')
    shutil.copytree(example_vsset_path,
                    example_project_vsset_path, dirs_exist_ok=True)

    # copy Library\SDS-Framework of sds vscode project from downloaded SDS BSP
    example_template_path = os.path.join(
        templates_path, sds_list[0], sds_list[2], 'Library', 'SDS-Framework')
    example_project_path = os.path.join(
        bsp_dest_path, 'Library', 'SDS-Framework')
    print(example_template_path)
    print(example_project_path)
    print('copy SDS-Framework...')
    shutil.copytree(example_template_path,
                    example_project_path, dirs_exist_ok=True)

    # copy ThirdParty\MPU6500 of sds vscode project from downloaded SDS BSP
    example_template_path = os.path.join(
        templates_path, sds_list[0], sds_list[2], 'ThirdParty', 'MPU6500')
    example_project_path = os.path.join(
        bsp_thirdparty_dest_path, 'MPU6500')
    print(example_template_path)
    print(example_project_path)
    print('copy SDS-Framework...')
    shutil.copytree(example_template_path,
                    example_project_path, dirs_exist_ok=True)

    # copy the new model
    example_project_path = os.path.join(
        bsp_dest_path, 'SampleCode', 'MachineLearning', example_tmpl_proj)
    example_project_model_cpp_file = os.path.join(
        example_project_path, 'Model', 'NN_Model_INT8.tflite.cpp')
    example_project_model_dir = os.path.join(example_project_path, 'Model')

    print(example_project_model_cpp_file)
    print(example_project_model_dir)

    print('copy the new model...')
    shutil.copyfile(vela_model_cc_file, example_project_model_cpp_file)
    shutil.copy(vela_model_file, example_project_model_dir)

    return example_project_path


def proj_gen(progen_path, project_type, project_dir_name):
    # update to uvision5_armc6
    if project_type == 'vscode':
        project_type = 'uvision5_armc6'

    cur_work_dir = os.getcwd()
    os.chdir(progen_path)

    python_dir = os.path.dirname(sys.executable)
    #For embeded python
    embedded_py_path = os.path.join(python_dir, 'runtime', 'python.exe')
    subprocess.run([embedded_py_path, '-m', 'project_generator', 'generate', '-f', 'project.yaml', '-p', project_dir_name, '-t', project_type])

    # Original python environment
    #progen_cmd = ['progen', 'generate', '-f', 'project.yaml', '-p', project_dir_name]
    #progen_cmd.append('-t')
    #progen_cmd.append(project_type)
    #ret = subprocess.run(progen_cmd)
    #if ret.returncode == 0:
    #    print('Success generation')
    #else:
    #    print('Unable generation')

    # copy project file to project folder
    toolchain_project = project_type + '_' + project_dir_name
    toolchain_project_src_dir = os.path.join('generated_projects', toolchain_project)

    if project_type == 'uvision5_armc6':
        toolchain_project_dest_dir = os.path.join(project_dir_name, 'KEIL')
    else:
        toolchain_project_dest_dir = os.path.join(project_dir_name, 'GCC')

    print(toolchain_project_src_dir)
    print(toolchain_project_dest_dir)

    shutil.copytree(toolchain_project_src_dir, toolchain_project_dest_dir, dirs_exist_ok = True)

    # delete progen files
    shutil.rmtree('generated_projects')
    shutil.rmtree('tools')
    os.remove('project.yaml')

    os.chdir(cur_work_dir)

# project generate main function
def project_generate(args):
    print(f"project type is {args.project_type}")
    templates_path = args.templates_path
    application_usage = args.application

    if not application_usage in application:
        print("applicaiton not found! using generic instead")
        application_usage = "generic"

    application_param = application[application_usage]

    if templates_path == None:
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

    if not args.project_type in project_type_list:
        print(f"Only support {project_type_list} projtect type")
        return 'unable_generate'

    # create ouput directory, if output directory is not exist
    if not os.path.exists(args.output_path):
        os.mkdir(args.output_path)

    # generated project directory
    project_path = os.path.join(args.output_path, PROJECT_GEN_DIR_PREFIX + args.board)
    if not os.path.exists(project_path):
        os.mkdir(project_path)

    # model compile by vela
    arena_size = args.model_arena_size
    vela_dir_path = os.path.join(os.path.dirname(__file__), '..', 'vela')

    ret = model_compile(board_info, args.output_path, vela_dir_path, os.path.abspath(args.model_file), arena_size)
    if ret == False:
        return 'unable_generate'

    vela_model_basename = os.path.splitext(os.path.basename(args.model_file))[0]
    vela_model_file_path = os.path.join(args.output_path, vela_model_basename + '_vela.tflite')
    vela_summary_file_path = os.path.join(args.output_path, vela_model_basename + '_summary_Ethos_U55_High_End_Embedded.csv')
    print(vela_model_file_path)

    # generate model cc file
    tflite2cpp_dir_path = os.path.join(os.path.dirname(__file__), '..', 'tflite2cpp')
    print(tflite2cpp_dir_path)
    generate_model_cpp(args.output_path, tflite2cpp_dir_path, os.path.abspath(vela_model_file_path)) 
    vela_model_cc_file = os.path.join(args.output_path, vela_model_basename + '_vela.tflite.cc')
    print(vela_model_cc_file)

    # prepare project resource
    example_tmpl_dir = application_param["example_tmpl_dir"]
    example_tmpl_proj = application_param["example_tmpl_proj"]
    if application_usage == 'gsensor_sds':
        project_example_path = prepare_vscode_sds_proj_resource(board_info, project_path, templates_path, vela_model_file_path, vela_model_cc_file, example_tmpl_dir, example_tmpl_proj)
    else:
        project_example_path = prepare_proj_resource(board_info, project_path, templates_path, vela_model_file_path, vela_model_cc_file, example_tmpl_dir, example_tmpl_proj)
    print(project_example_path)

    # Generate mode.hpp/cpp or main.cpp
    if application_usage == 'generic':
        codegen = GenericCodegen.from_args(vela_model_file_path, project_example_path, vela_summary_file_path, app='generic')
    elif application_usage == 'imgclass':
        codegen = ImgClassCodegen.from_args(vela_model_file_path, project_example_path, vela_summary_file_path, app='imagclass')
    elif application_usage == 'gsensor_sds':
        codegen = SdsGsensorCodegen.from_args(vela_model_file_path, project_example_path, vela_summary_file_path, app='gsensor_sds')
    
    codegen.code_gen()

    os.remove(vela_model_file_path)
    os.remove(vela_model_cc_file)


    if application_usage == 'gsensor_sds':  # sds project is already generated from copying SDS BSP
        print(
            f'Example project completed at {os.path.abspath(project_example_path)}')
    else:  # start generate project file (*.uvprojx, Makefile)
        progen_path = os.path.join(project_example_path, '..')
        proj_gen(progen_path, args.project_type, os.path.basename(project_example_path))
        print(f'Example project completed at {os.path.abspath(project_example_path)}')

    return project_example_path
    