import mysql.connector
from mysql.connector import Error

def execute_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query successful ({})".format(cursor.lastrowid))
        return cursor.lastrowid
    except Error as e:
        print(f"Error: {e}")
        print(query, data)
        connection.rollback()
        return None
    finally:
        cursor.close()

def insert_into_model(connection, data):
    query = """
    INSERT INTO model (model_name)
    VALUES (%s)
    """
    print("model", data)
    return execute_query(connection, query, data)

def insert_into_layer(connection, data):
    query = """
    INSERT INTO layer (model_id, layer_name, layer_type, layer_subtype)
    VALUES (%s, %s, %s, %s)
    """
    print("layer", data)
    return execute_query(connection, query, data)

def insert_into_dense_layer(connection, data):
    query = """
    INSERT INTO dense_layer (layer_id, n_in, n_out)
    VALUES (%s, %s, %s)
    """
    print("dense_layer", data)
    return execute_query(connection, query, data)

def insert_into_layer_knobs(connection, data):
    query = """
    INSERT INTO layer_knobs (reuse_factor, strategy)
    VALUES (%s, %s)
    """
    print("layer_knobs", data)
    return execute_query(connection, query, data)

def insert_into_dense_layer_knobs(connection, data):
    query = """
    INSERT INTO dense_layer_knobs (layer_knobs_id, layer_id, q_precision_weight, q_precision_bias, q_precision_accum, q_precision_result)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    print("dense_layer_knobs", data)
    return execute_query(connection, query, data)

def insert_into_model_knobs(connection, data):
    query = """
    INSERT INTO model_knobs (model_id, target_clock_period_unit, target_clock_period, part, io_type, backend)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    print("model_knobs", data)
    return execute_query(connection, query, data)

def insert_into_model_qor(connection, data):
    query = """
    INSERT INTO model_qor (model_knobs_id, hls4ml_ver, hls_tool, hls_tool_ver, user_name, host_name, host_cpu, host_mem_unit, host_mem, hls_fail, hls_error_message, hls_execution_time_unit, hls_execution_time, estimated_clock_period, best_latency, worst_latency, minimum_initiation_interval, maximum_initiation_interval, bram, dsp, ff, lut, uram)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    print("model_qor", data)
    return execute_query(connection, query, data)

def insert_into_layer_qor(connection, data):
    query = """
    INSERT INTO layer_qor (layer_knobs_id, model_qor_id, module_name, best_latency_clk, worst_latency_clk, minimum_initiation_interval_clk, maximum_initiation_interval_clk, best_latency_abs, worst_latency_abs, minimum_initiation_interval_abs, maximum_initiation_interval_abs, pipeline_type, bram, dsp, ff, lut, uram)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    print("layer_qor", data)
    return execute_query(connection, query, data)
