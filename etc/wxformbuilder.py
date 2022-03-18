'''
Created on 2022/03/18

@author: is2225
'''
import os
import os.path
import sys
import subprocess

ST_FORM_ROOT = "wxform"
ST_PROJ_NAME = "wsform_project"
ST_PY_NAME = "form"

def get_proj_contents(src_path, file_name):
    contents = []
    contents.append('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>')
    contents.append('<wxFormBuilder_Project>')
    contents.append('<FileVersion major="1" minor="16" />')
    contents.append('<object class="Project" expanded="1">')
    contents.append('<property name="class_decoration">; </property>')
    contents.append('<property name="code_generation">Python</property>')
    contents.append('<property name="disconnect_events">1</property>')
    contents.append('<property name="disconnect_mode">source_name</property>')
    contents.append('<property name="disconnect_php_events">0</property>')
    contents.append('<property name="disconnect_python_events">0</property>')
    contents.append('<property name="embedded_files_path">res</property>')
    contents.append('<property name="encoding">UTF-8</property>')
    contents.append('<property name="event_generation">connect</property>')
    contents.append('<property name="file">{0}</property>'.format(file_name))
    contents.append('<property name="first_id">1000</property>')
    contents.append('<property name="help_provider">none</property>')
    contents.append('<property name="image_path_wrapper_function_name"></property>')
    contents.append('<property name="indent_with_spaces"></property>')
    contents.append('<property name="internationalize">0</property>')
    contents.append('<property name="name">MyProject3</property>')
    contents.append('<property name="namespace"></property>')
    contents.append('<property name="path">{0}</property>'.format(src_path))
    contents.append('<property name="precompiled_header"></property>')
    contents.append('<property name="relative_path">1</property>')
    contents.append('<property name="skip_lua_events">1</property>')
    contents.append('<property name="skip_php_events">1</property>')
    contents.append('<property name="skip_python_events">1</property>')
    contents.append('<property name="ui_table">UI</property>')
    contents.append('<property name="use_array_enum">0</property>')
    contents.append('<property name="use_enum">0</property>')
    contents.append('<property name="use_microsoft_bom">0</property>')
    contents.append('</object>')
    contents.append('</wxFormBuilder_Project>')
    return "\n".join(contents)

def run():
    if not sys.argv and len(sys.argv) < 3:
        return
    
    folder = sys.argv[1]
    if not os.path.exists(folder):
        return
    src_folder = os.path.join(folder, 'src')
    if not os.path.exists(src_folder):
        return
    
    exe_path = sys.argv[2]
    if not os.path.isfile(exe_path):
        return
    
    wxform_folder = os.path.join(folder, ST_FORM_ROOT)
    if not os.path.exists(wxform_folder):
        os.mkdir(wxform_folder)
    
    wxform_proj = os.path.join(wxform_folder, ST_PROJ_NAME)
    if not os.path.isfile(wxform_proj):
        with open(wxform_proj, 'wt') as f:
            f.write(get_proj_contents(src_folder, ST_PY_NAME))
    
    if os.path.isfile(wxform_proj):
        subprocess.run([exe_path, wxform_proj])
        
if __name__ == '__main__':
    run()