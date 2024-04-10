# Author: Chang Sun, GDG

import re
from pathlib import Path

import h5py as h5
from lxml import etree
import yaml

def match_vivado_funcname(gp, vivado_func_names):
    cls_name = gp['cls_name']
    template_args = gp['template_args']
    r = re.search(r'[^\s]*config[^\s]+', template_args)
    config_name = r.group(0) if r is not None else None
    layer_name = gp['layer_name']
    found = None
    for func_name in vivado_func_names:
        if not re.match(f'^{cls_name}_|_{cls_name}_', func_name):
            continue
        if config_name and not re.search(f'_{config_name}_|_{config_name}$', func_name):
            continue
        assert found is None, f'Found multiple matches for {layer_name}: {found}, {func_name}'
        found = func_name
    assert found is not None, f'Found no matches for {layer_name}'
    return layer_name, found

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
    def ignore_unknown(self, node):
        return None

SafeLoaderIgnoreUnknown.add_constructor('', SafeLoaderIgnoreUnknown.ignore_unknown)

def parse_hls4ml_prj(path:Path):
    # TODO Why are we using .rpt and not .xml reports from Vivado HLS?
    with open(path / 'hls4ml_config.yml') as f:
        conf = yaml.load(f, Loader=yaml.BaseLoader)
    project_name = conf['ProjectName']
    top_file = path / f'firmware/{project_name}.cpp'
    csynth_rpt = path / f'{project_name}_prj/solution1/syn/report/{project_name}_csynth.rpt'

    with open(top_file) as f:
        top_file_content = f.read()

    with open(csynth_rpt) as f:
        top_rpt = f.read()

    top_file_m = re.compile(r'nnet::(?P<cls_name>[\w+_]+)<(?P<template_args>[^>]+)>\([^\)]+\); // (?P<layer_name>\w+)(?=\n)')
    latency_block_pattern = """
={64}
== Performance Estimates
={64}
(.+)
={64}
== Utilization Estimates
={64}
"""

    resource_block_pattern = """
={64}
== Utilization Estimates
={64}
(.+)
={64}
== Interface
={64}
"""

    latency_m = re.compile(r"\|(?P<Instance>[\w_]+)\s*\|(?P<Module>[\w_]+)\s*\|\s*(?P<latency_clk_min>\d+)\s*\|\s*(?P<latency_clk_max>\d+)\s*\|\s*(?P<layency_abs_min>[\d\.]+ \w+)\s*\|\s*(?P<layency_abs_max>[\d\.]+ \w+)\s*\|\s*(?P<interval_clk_min>\d+)\s*\|\s*(?P<interval_clk_max>\d+)\s*\|\s*(?P<pipeline>\w+)\s*\|")
    resource_m = re.compile(r"\|(?P<Instance>[\w_]+)\s*\|(?P<Module>[\w_]+)\s*\|\s*(?P<bram>\d+)\s*\|\s*(?P<dsp>\d+)\s*\|\s*(?P<ff>\d+)\s*\|\s*(?P<lut>\d+)\s*\|\s*(?P<uram>\d+)\s*\|")

    latency_blocks = re.findall(latency_block_pattern, top_rpt, re.DOTALL)
    assert len(latency_blocks) == 1, f'Found {len(latency_blocks)} latency blocks'

    resource_blocks = re.findall(resource_block_pattern, top_rpt, re.DOTALL)
    assert len(resource_blocks) == 1, f'Found {len(resource_blocks)} resource blocks'

    latency_block:str = latency_blocks[0]
    latency_dict = {gp['Module']: gp.groupdict() for gp in latency_m.finditer(latency_block)}
    if not latency_dict:
        raise ValueError('No latency block found. Did you inline everything?')
    latency_dict_readable = {}
    for gp in top_file_m.finditer(top_file_content):
        lname, vname = match_vivado_funcname(gp, latency_dict.keys())
        latency_dict_readable[lname] = latency_dict[vname]
        del latency_dict[vname]

    resource_block:str = resource_blocks[0]
    print(resource_block)
    resource_dict = {gp['Module']: gp.groupdict() for gp in resource_m.finditer(resource_block)}
    if not resource_dict:
        raise ValueError('No resource block found. Did you inline everything?')
    resource_dict_readable = {}
    for gp in top_file_m.finditer(top_file_content):
        lname, vname = match_vivado_funcname(gp, resource_dict.keys())
        resource_dict_readable[lname] = resource_dict[vname]
        del resource_dict[vname]

    return latency_dict_readable, resource_dict_readable

