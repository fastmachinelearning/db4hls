import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import itertools
import subprocess

import pytest
from hls4ml import __version__
from pathlib import Path

from connection_config import * # MySQL connection configuration
from helpers import * # Extract information from synthesis run
from queries import * # SQL queries as python functions
from vivado_dense_layer import run_vivado_dense_layer

from extract_layer_info import parse_hls4ml_prj

def cartesian_product(a_min, a_max, b_min, b_max):
    a_range = range(a_min, a_max + 1)
    b_range = range(b_min, b_max + 1)
    return list(itertools.product(a_range, b_range))

design_space = cartesian_product(2, 8, 2, 8)

@pytest.mark.parametrize('n_in, n_out', design_space)
def test_dense(n_in, n_out):
#def main():
#    n_in = 4
#    n_out = 4
    # Run Vivado HLS for a single dummy layer, not too much configuration
    # here, just get the results for the db
    model_name, hls_model, report, vivado_hls_xml, vivado_hls_log, hls4ml_project_dir = run_vivado_dense_layer(n_in, n_out)

    try:
        # Connect to the MySQL database
        connection = create_db_connection(connection_config_dict)
        if connection is None:
            return

        ### model ###
        model_data = (model_name, )
        model_id = insert_into_model(connection, model_data)

        hls4ml_project_path = Path(hls4ml_project_dir).absolute()
        layer_latency_info, layer_resource_info = parse_hls4ml_prj(hls4ml_project_path)

        if model_id:
            hls_model_config = hls_model.config.config
            target_clock_period_unit = 'ns' # TODO hardcoded
            target_clock_period = hls_model.config.config.get('ClockPeriod')
            part = hls_model_config.get('Part')
            io_type = hls_model.config.config.get('IOType')
            backend = hls_model_config.get('Backend')
            ### model_knobs ###
            model_knobs_data = (model_id, target_clock_period_unit, target_clock_period, part, io_type, backend, )
            model_knobs_id = insert_into_model_knobs(connection, model_knobs_data)
            if (model_knobs_id):
                hls_tool = 'Vivado HLS'
                hls4ml_ver = __version__
                hls_tool_ver = subprocess.getoutput(get_version_cmd(vivado_hls_xml))
                user_name = subprocess.getoutput(get_user())
                host_name = subprocess.getoutput(get_host_name())
                host_cpu = subprocess.getoutput(get_host_cpu())
                host_mem_unit = subprocess.getoutput(get_host_mem_unit())
                host_mem = subprocess.getoutput(get_host_mem())
                hls_fail = report.get('CSynthesisReport') is None
                hls_error_message = subprocess.getoutput(get_hls_error_msg_cmd(vivado_hls_log))
                hls_execution_time_unit = subprocess.getoutput(get_hls_execution_time_unit_cmd(vivado_hls_log))
                hls_execution_time_str = subprocess.getoutput(get_hls_execution_time_cmd(vivado_hls_log))
                hls_execution_time = int(hls_execution_time_str) if hls_execution_time_str != '' else -1
                #
                estimated_clock_period = report['CSynthesisReport']['EstimatedClockPeriod']
                best_latency = report['CSynthesisReport']['BestLatency']
                worst_latency = report['CSynthesisReport']['WorstLatency']
                minimum_initiation_interval = report['CSynthesisReport']['IntervalMin']
                maximum_initiation_interval = report['CSynthesisReport']['IntervalMax']
                bram = report['CSynthesisReport']['BRAM_18K']
                dsp = report['CSynthesisReport']['DSP']
                ff = report['CSynthesisReport']['FF']
                lut = report['CSynthesisReport']['LUT']
                uram =  report['CSynthesisReport']['URAM']
                ### model_qor ###
                model_qor_data = (model_knobs_id,
                                  hls4ml_ver,
                                  hls_tool, hls_tool_ver, user_name, host_name, host_cpu,
                                  host_mem_unit, host_mem,
                                  hls_fail, hls_error_message,
                                  hls_execution_time_unit, hls_execution_time,
                                  estimated_clock_period, best_latency, worst_latency,
                                  minimum_initiation_interval, maximum_initiation_interval,
                                  bram, dsp, ff, lut, uram)
                model_qor_id = insert_into_model_qor(connection, model_qor_data)

        if model_id:
            layers = hls_model.get_layers().mapping
            for layer_name in layers:
                layer_attributes = layers.get(layer_name).attributes
                layer_type = layer_attributes.get('class_name')
                layer_subtype = layer_attributes.get('activation') if layer_type == 'Activation' else ''
                ### layer ###
                layer_data = (model_id, layer_name, layer_type, layer_subtype)
                layer_id = insert_into_layer(connection, layer_data)
                if layer_id:
                    if layer_type == 'Dense':
                        n_in = layer_attributes.get('n_in')
                        n_out = layer_attributes.get('n_out')
                        ### dense_layer ###
                        dense_layer_data = (layer_id, n_in, n_out)
                        dense_layer_id = insert_into_dense_layer(connection, dense_layer_data)
                        dense_layer_id = layer_id # TODO: dense_layer inherit from layer, execute_query does not return id
                        if dense_layer_id:
                            reuse_factor = layer_attributes.get('reuse_factor')
                            strategy = layer_attributes.get('strategy')
                            ### layer_knobs ###
                            layer_knobs_data = (reuse_factor, strategy)
                            layer_knobs_id = insert_into_layer_knobs(connection, layer_knobs_data)
                            if layer_knobs_id:
                                q_precision_weight = layer_attributes.get('weight_t').precision.definition_cpp()
                                q_precision_bias = layer_attributes.get('bias_t').precision.definition_cpp()
                                q_precision_accum = layer_attributes.get('accum_t').precision.definition_cpp()
                                q_precision_result = layer_attributes.get('precision')
                                ### dense_layer_knobs ###
                                dense_layer_knobs_data = (layer_knobs_id, layer_id, q_precision_weight, q_precision_bias, q_precision_accum, q_precision_result)
                                dense_layer_knobs_id = insert_into_dense_layer_knobs(connection, dense_layer_knobs_data)
                    if layer_name in layer_latency_info and layer_name in layer_resource_info:
                        module_name = layer_latency_info[layer_name]['Module']
                        best_latency_clk = layer_latency_info[layer_name]['latency_clk_min']
                        worst_latency_clk = layer_latency_info[layer_name]['latency_clk_max']
                        minimum_initiation_interval_clk = layer_latency_info[layer_name]['interval_clk_min']
                        maximum_initiation_interval_clk = layer_latency_info[layer_name]['interval_clk_max']
                        best_latency_abs = layer_latency_info[layer_name]['latency_clk_min'].replace(" ns", "")
                        worst_latency_abs = layer_latency_info[layer_name]['latency_clk_max'].replace(" ns", "")
                        minimum_initiation_interval_abs = layer_latency_info[layer_name]['latency_clk_min'].replace(" ns", "")
                        maximum_initiation_interval_abs = layer_latency_info[layer_name]['latency_clk_max'].replace(" ns", "")
                        pipeline_type = layer_latency_info[layer_name]['pipeline']
                        bram = layer_resource_info[layer_name]['bram']
                        dsp = layer_resource_info[layer_name]['dsp']
                        ff = layer_resource_info[layer_name]['ff']
                        lut = layer_resource_info[layer_name]['lut']
                        uram = layer_resource_info[layer_name]['uram']
                        ### layer_qor ###
                        layer_qor_data = (layer_knobs_id, model_qor_id,
                                          module_name,
                                          best_latency_clk, worst_latency_clk, minimum_initiation_interval_clk, maximum_initiation_interval_clk,
                                          best_latency_abs, worst_latency_abs, minimum_initiation_interval_abs, maximum_initiation_interval_abs,
                                          pipeline_type,
                                          bram, dsp, ff, lut, uram)
                        layer_qor_id = insert_into_layer_qor(connection, layer_qor_data)
    finally:
        # Close the database connection
        if connection.is_connected():
            connection.close()
            print("MySQL connection closed")

    import os
    import shutil
    shutil.rmtree(hls4ml_project_dir)
    try:
        os.remove(hls4ml_project_dir + '.tar.gz')
    except FileNotFoundError:
        pass  # Ignore the error and continue execution
#if __name__ == "__main__":
#    main()
