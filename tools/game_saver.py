from genericpath import isdir, isfile
from logging import log
import sys
import os
import subprocess
import tkinter
import tkinter.filedialog
import time
import json

def prompt_file(title_text):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    saved_dir_path = os.path.join(dir_path, ".")
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.askopenfilename(parent=top, title=title_text, initialdir=saved_dir_path, multiple=True)
    top.destroy()
    if (file_name):
        file_name = file_name[0]
    return file_name

def throw_error_no_file(file, name):
    if (file == ""):
        print(f"Error: no {name} selected")
        sys.exit(1)
    else:
        print(f"Selected {file}")

def get_param_value(string_input):
    if (string_input in sys.argv):
        id = sys.argv.index(string_input) + 1
        if (id < len(sys.argv)):
            return sys.argv[id]
    return ""

def get_parameters():
    server = get_param_value("-s")
    fantom_client = get_param_value("-f")
    inspector_client = get_param_value("-i")

    if (server == ""):
        server = prompt_file("Select a server file")
        throw_error_no_file(server, "server")
    if (fantom_client == ""):
        fantom_client = prompt_file("Select a fantom client file")
        throw_error_no_file(fantom_client, "fantom client")
    if (inspector_client == ""):
        inspector_client = prompt_file("Select an inspector client file")
        throw_error_no_file(inspector_client, "inspector client")
    return server, fantom_client, inspector_client

def open_file_stream():
    date = time.ctime(time.time())
    date = date.replace(" ", "_")
    date = date.replace(":", "-")
    save_dir = os.path.realpath("saved_games")
    if (not os.path.isdir(save_dir)):
        os.mkdir(save_dir)
    path_file = os.path.join(save_dir, f"{date}.poai")
    f = open(path_file, "w+")
    return f

def open_logger():
    log_dir = os.path.realpath("logs")
    if (not os.path.isdir(log_dir)):
        sys.exit(1)
    path_logger = os.path.join(log_dir, "game.log")
    f = open(path_logger, "r")
    return f

def log_to_json(logger_data):
    data = {}
    fantom_color = "the fantom is "
    debug_delimiter = ":: DEBUG ::"
    info_delimiter = ":: INFO ::"

    read_json_lines = False
    json_turns = []
    json_turn = ""

    for log_line in logger_data:
        log_line = log_line.rstrip()
        if (fantom_color in log_line):
            data["fantom"] = log_line.split(fantom_color)[-1]
        if (info_delimiter in log_line):
            if (read_json_lines):
                json_turns.append(json.loads(json_turn))
            read_json_lines = False
        if (read_json_lines == True):
            json_turn += log_line
        if (debug_delimiter in log_line):
            read_json_lines = True
            json_turn = ""
            json_turn += log_line.split(debug_delimiter, 1)[1]

    data["turns"] = json_turns
    final_data = json.dumps(data)
    return final_data

def main():
    server, fantom_client, inspector_client = get_parameters()
    f = open_file_stream()
    ouput_server = subprocess.Popen(["python3", server], shell=True, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(0.1)
    output_fantom = subprocess.Popen(["python3", fantom_client], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    time.sleep(0.1)
    output_inspector = subprocess.Popen(["python3", inspector_client], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    while True:
        # check if either sub-process has finished
        ouput_server.poll()
        output_fantom.poll()
        output_inspector.poll()
        if ouput_server.returncode is not None or output_fantom.returncode is not None or output_inspector.returncode is not None:
            break
    logger = open_logger()
    log_lines = logger.readlines()
    f.write(log_to_json(log_lines))
    f.close()
    ##print(lines_to_save)

if __name__ == "__main__":
    main()

