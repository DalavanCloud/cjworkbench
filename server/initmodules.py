# Initialize the list of available modules on startup
# For the moment, this consists of loading them from json files at startup

import os
import json
from cjworkbench.settings import BASE_DIR
from server.models import Module, WfModule, ParameterSpec, ParameterVal

import logging
logger = logging.getLogger(__name__)

# Top level call, (re)load module definitions from files
def init_modules():
    module_path = os.path.join(BASE_DIR, 'config/modules')

    # Get all json files in this directory (exclude dirs)
    modfiles = [f for f in os.listdir(module_path) if os.path.isfile(os.path.join(module_path, f)) and f.endswith(".json")]

    # Load all modules from files
    for f in modfiles:
        load_module_from_file(os.path.join(module_path, f))


# Create a module object by reading in the json description in a file
def load_module_from_file(fname):
    logger.info("Loading module " + fname)

    with open(fname) as json_data:
        try:
            d = json.load(json_data)
            load_module_from_dict(d)
        except ValueError as e:
            logger.error("Error loading Module definition file " + fname + ": " + str(e))


# Create a module from dictionary of properties, corresponding to the json in the config file
# testable entrypoint
def load_module_from_dict(d):
    if not 'name' in d:
        raise ValueError("Missing module name")
    if not 'id_name' in d:
        raise ValueError("Missing module id_name")
    id_name = d['id_name']

    # If we can find an existing module with the same id_name, use that
    matches = Module.objects.filter(id_name=id_name)
    if len(matches)>0:
        assert (len(matches) == 1)  # no duplicates please
        module = matches[0]
    else:
        module = Module()

    # save module data
    module.name=d['name']
    module.id_name=id_name
    module.dispatch=id_name
    module.save()

    # load params
    if 'parameters' in d:
        pspecs = [ load_parameter_spec(p, module) for p in d['parameters']]
    else:
        pspecs = []

    # delete all ParameterSpecs (and hence ParameterVals) for this module that were not in the new module description
    for ps in ParameterSpec.objects.filter(module=module):
        if ps not in pspecs: # relies on model == comaparing .id
            ps.delete()

    return module


# Load parameter spec from json def
# If it's a brand new parameter spec, add it to all existing WfModules
# Otherwise re-use existing spec object, and update all existing ParameterVal objects that point to it
def load_parameter_spec(d, module):
    # require name and id_name
    if not 'name' in d:
        raise ValueError("Missing parameter name")
    name = d['name']
    if not 'id_name' in d:
        raise ValueError("Missing parameter id_name")
    id_name = d['id_name']
    if not 'type' in d:
        raise ValueError("Missing parameter type")
    ptype = d['type']

    # Find any previous parameter specs with this id_name (including any we just loaded)
    oldspecs =  ParameterSpec.objects.filter(id_name=id_name, module=module)
    if len(oldspecs)>0:
        assert(len(oldspecs))==1  # ids should be unique
        pspec = oldspecs[0]
        pspec.name = name

        # reset to default defaults
        pspec.def_number = 0.0
        pspec.def_string = ''
        pspec.def_text = ''

        reloading = True
        type_changed = pspec.type != ptype
        pspec.type = ptype
    else:
        pspec = ParameterSpec(name=name, id_name=id_name, type=ptype, module=module)
        reloading = False

    # load default value
    if ptype == 'string':
        pspec.def_string=d['default']
    elif d['type'] == 'number':
        pspec.def_number=d['default']
    elif d['type'] == 'text':
        pspec.def_text=d['default']
    elif d['type'] == 'button':
        pass # no value
    elif d['type'] != None:
        raise ValueError("Unknown parameter type " + d['type'])
    pspec.save()

    # if parameter is newly added, add new ParameterVals to all existing modules
    if not reloading:
        for wfm in WfModule.objects.filter(module=module):
            pval = ParameterVal.objects.create(wf_module=wfm, parameter_spec=pspec)
            pval.init_from_spec()
            pval.save()

    # If the parameter is reloading and the type changed, reset existing vals to default values
    if reloading and type_changed:
        for pval in ParameterVal.objects.filter(parameter_spec=pspec):
            pval.init_from_spec()
            pval.save()

    return pspec


# Create a single ParameterSpec object from json def
# Must pass in parent module
def parse_parameter_spec(d, module):
    name = d['name']  # existence checked in load_parameter_spec
    id_name = d['id_name']

    if d['type'] == 'string':
        p = ParameterSpec(type=ParameterSpec.STRING, name=name, id_name=id_name, module=module, def_string=d['default'], def_number=0, def_text='')

    elif d['type'] == 'number':
        p = ParameterSpec(type=ParameterSpec.NUMBER, name=name, id_name=id_name, module=module, def_string='', def_number=d['default'], def_text='')

    elif d['type'] == 'text':
        p = ParameterSpec(type=ParameterSpec.TEXT, name=name, id_name=id_name, module=module, def_string='', def_number=0, def_text=d['default'])

    elif d['type'] == 'button':
        p = ParameterSpec(type=ParameterSpec.BUTTON, name=name, id_name=id_name, module=module, def_string='', def_number=0, def_text='')

    elif d['type'] != None:
        raise ValueError("Unknown parameter type " + d['type'])
    else:
        raise ValueError("Missing parameter type")

    p.save()
    return p


