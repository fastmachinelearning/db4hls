import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import hls4ml
import tensorflow as tf

def run_vivado_dense_layer(inputs, outputs):
    WORKSPACE_DIR = 'workspace'
    LAYER_DIR = '/dense'

    def tuple_to_string(elements: tuple) -> str:
        str1 = "_"
        return str1.join([str(elem) for elem in elements])

    def get_output_dir(input_shape: tuple, units: int, reuse_factor: int, strategy: str, precision: str) -> str:
        output_dir = WORKSPACE_DIR + '/'
        output_dir += LAYER_DIR + '/'
        output_dir += 'i_' + tuple_to_string(input_shape)
        output_dir += '_o_' + tuple_to_string((units,))
        output_dir += '_rf_' + str(reuse_factor)
        output_dir += '_s_' + strategy
        output_dir += '_p_' + precision
        return output_dir

    INPUT_SHAPE = (inputs, )
    UNITS = outputs
    REUSE_FACTOR = 1
    PRECISION = 'ap_fixed<16,8>'
    STRATEGY = 'latency'
    PART = 'xczu9eg-ffvb1156-2-e'

    # Create model
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(name='fc1', input_shape=INPUT_SHAPE, units=UNITS))
    model.compile()
    # Configure hls4ml model
    cfg = hls4ml.utils.config_from_keras_model(model, granularity='name')
    cfg['Model'] = {}
    cfg['Model']['ReuseFactor'] = REUSE_FACTOR
    cfg['Model']['Strategy'] = STRATEGY
    cfg['Model']['Precision'] = PRECISION
    cfg['LayerName']['fc1']['ReuseFactor'] = REUSE_FACTOR
    cfg['LayerName']['fc1']['Strategy'] = STRATEGY
    cfg['LayerName']['fc1']['Precision'] = PRECISION
    output_dir = get_output_dir(INPUT_SHAPE, UNITS, REUSE_FACTOR, STRATEGY, PRECISION)
    hls_model = hls4ml.converters.convert_from_keras_model(model=model,
                                                           hls_config=cfg,
                                                           io_type='io_parallel',
                                                           output_dir=output_dir,
                                                           part=PART)
    _ = hls_model.compile()

    # Run synthesis
    report = hls_model.build(reset=True, csim=False, synth=True, cosim=False, validation=False, export=False, vsynth=False, fifo_opt=False)
    vivado_hls_xml = output_dir + '/myproject_prj/solution1/syn/report/csynth.xml'
    vivado_hls_log = output_dir + '/vivado_hls.log'
    
    return 'basic_dense', hls_model, report, vivado_hls_xml, vivado_hls_log, output_dir