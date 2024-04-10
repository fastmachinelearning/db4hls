-- create database to store DSE information (hls4ml)
CREATE DATABASE db4hls;
-- DROP DATABASE db4hls;
USE db4hls

CREATE TABLE model (
    model_id INT PRIMARY KEY AUTO_INCREMENT,
    -- Model information
    model_name VARCHAR(255)  
);

CREATE TABLE model_knobs (
    model_knobs_id INT PRIMARY KEY AUTO_INCREMENT,
    -- model_knobs n-to-1 model
    model_id INT UNIQUE NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model(model_id),
    -- hls4ml knobs 
    target_clock_period_unit VARCHAR(15),
    target_clock_period FLOAT,
    -- time_unit VARCHAR(15),
    part VARCHAR(255),
    io_type VARCHAR(255),
    backend VARCHAR(255)
);

CREATE TABLE model_qor (
    model_qor_id INT PRIMARY KEY AUTO_INCREMENT,
    -- model_qor n-to-1 model_knobs
    model_knobs_id INT UNIQUE NOT NULL,
    FOREIGN KEY (model_knobs_id) REFERENCES model_knobs(model_knobs_id),
    -- hls4ml/nn_utils information
    -- git_rev VARCHAR(255),
    -- git_url VARCHAR(512), 
    hls4ml_ver VARCHAR(255),
    -- HLS tool information
    hls_tool VARCHAR(255),
    hls_tool_ver VARCHAR(255),
    -- User information
    user_name VARCHAR(255),
    -- Host information
    host_name VARCHAR(255),
    host_cpu VARCHAR(255), 
    host_mem_unit VARCHAR(255),
    host_mem INT,
    -- HLS run information
    hls_fail INT,
    hls_error_message TEXT, 
    hls_execution_time_unit VARCHAR(15),
    hls_execution_time INT,
    -- Timing information
    estimated_clock_period FLOAT,
    best_latency FLOAT,
    worst_latency FLOAT,
    minimum_initiation_interval FLOAT,
    maximum_initiation_interval FLOAT,
    -- Resource information
    bram FLOAT, 
    dsp FLOAT,
    ff FLOAT,
    lut FLOAT,
    uram FLOAT
);

CREATE TABLE layer (
    layer_id INT PRIMARY KEY AUTO_INCREMENT,
    -- layer n-to-1 model
    model_id INT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model(model_id),
    -- Layer information
    layer_name VARCHAR(255),
    layer_type ENUM('Dense', 'InputLayer', 'Activation'),
    layer_subtype VARCHAR(255)
);
 
CREATE TABLE dense_layer (
    layer_id INT PRIMARY KEY,
    -- dense_layer inherits from layer
    FOREIGN KEY (layer_id) REFERENCES layer(layer_id),
    -- Dense layer information
    n_in INT,
    n_out INT
);

CREATE TABLE conv_2d_layer (
    layer_id INT PRIMARY KEY,
    -- conv_2d_layer inherits from layer
    FOREIGN KEY (layer_id) REFERENCES layer(layer_id)
    -- Conv2D layer layer information
);

CREATE TABLE layer_knobs (
    layer_knobs_id INT PRIMARY KEY AUTO_INCREMENT,
    -- hls4ml layer configuration
    reuse_factor INT,
    strategy VARCHAR(255)
    -- ,
    -- store_weights_in_bram BOOLEAN
);

CREATE TABLE dense_layer_knobs (
    layer_knobs_id INT PRIMARY KEY,
    -- dense_layer_knobs inherits from layer_knobs
    FOREIGN KEY (layer_knobs_id) REFERENCES layer_knobs(layer_knobs_id),
    -- dense_layer_knobs 1-to-n layer_knobs
    layer_id INT UNIQUE NOT NULL,
    FOREIGN KEY (layer_id) REFERENCES dense_layer(layer_id),
    -- hls4ml knobs
    q_precision_weight VARCHAR(255),
    q_precision_bias VARCHAR(255),
    q_precision_accum VARCHAR(255),
    q_precision_result VARCHAR(255)
) ;

CREATE TABLE conv_2d_layer_knobs (
    layer_knobs_id INT PRIMARY KEY,
    -- conv_2d_layer_knobs 1-to-n layer_knobs
    layer_id INT UNIQUE NOT NULL,
    FOREIGN KEY (layer_id) REFERENCES conv_2d_layer(layer_id),
    -- conv_2d_layer_knobs inherits from layer_knobs
    FOREIGN KEY (layer_knobs_id) REFERENCES layer_knobs(layer_knobs_id)
    -- hls4ml knobs
);

CREATE TABLE layer_qor (
    layer_qor_id INT PRIMARY KEY AUTO_INCREMENT,
    -- layer_qor n-to-1 layer_knobs
    layer_knobs_id INT NOT NULL,
    FOREIGN KEY (layer_knobs_id) REFERENCES layer_knobs(layer_knobs_id),
    -- layer_qor n-to-1 model_qor 
    model_qor_id INT NOT NULL,
    FOREIGN KEY (model_qor_id) REFERENCES model_qor(model_qor_id),
    -- C++ function to HDL module information
    module_name VARCHAR(255),
    -- Timing information
    best_latency_clk FLOAT,
    worst_latency_clk FLOAT,
    minimum_initiation_interval_clk FLOAT,
    maximum_initiation_interval_clk FLOAT,
    best_latency_abs FLOAT,
    worst_latency_abs FLOAT,
    minimum_initiation_interval_abs FLOAT,
    maximum_initiation_interval_abs FLOAT,
    pipeline_type VARCHAR(255),
    -- Resource information
    bram FLOAT, 
    dsp FLOAT,
    ff FLOAT,
    lut FLOAT,
    uram FLOAT
);


-- 
-- -- CREATE TABLE layers (
-- --     layer_id INT PRIMARY KEY AUTO_INCREMENT,
-- --     qor_id INT UNIQUE,
-- --     -- hls4ml/nn_utils information
-- --     git_rev VARCHAR(255),
-- --     git_url VARCHAR(512),
-- --     -- Layer information
-- --     layer_name VARCHAR(255),
-- --     -- hls4ml layer configuration
-- --     reuse_factor INT,
-- --     strategy VARCHAR(255),
-- --     store_weights_in_bram BOOLEAN,
-- --     layer_type ENUM('dense'),
-- --     FOREIGN KEY (qor_id) REFERENCES qor(qor_id)
-- -- );
-- -- 
-- -- CREATE TABLE asic_qor (
-- --     qor_id INT PRIMARY KEY AUTO_INCREMENT,
-- --     -- Timing information
-- --     time_unit VARCHAR(15),
-- --     latency FLOAT,
-- --     initiation_interval FLOAT,
-- --     -- Power information
-- --     power_unit VARCHAR(15),
-- --     power FLOAT,
-- --     -- Area information
-- --     area_unit VARCHAR(15),
-- --     area FLOAT,
-- --     FOREIGN KEY (qor_id) REFERENCES qor(qor_id)
-- -- );
-- 
-- 
-- -- -- Start a transaction
-- -- START TRANSACTION;
-- -- -- Insert into the vehicles table
-- -- INSERT INTO layers (layer_name, git_rev, git_url, reuse_factor, io_type, strategy, clock_period, clock_period_unit, part_or_technology, q_precision, store_weights_in_bram, layer_type) VALUES ('fc1', '123abc678', 'git@github.com', 1, 'io_parallel', 'latency', 10, 'ns', '45nm', 'fixed<16,8>', 0, 'dense');
-- -- -- Get the layer_id of the inserted layer
-- -- SET @last_layer_id = LAST_INSERT_ID();
-- -- -- Insert into the cars table using the vehicle_id from vehicles
-- -- INSERT INTO dense_layers (layer_id, n_in, n_out, n_zeros, n_nonzeros, q_precision_weight, q_precision_bias, q_precision_result, q_precision_index) VALUES (@last_layer_id, 16, 32, 153, 359, 'ap_fixed<16,8>', 'ap_fixed<16,8>', 'ap_fixed<16,8>', 'ap_uint<1>');
-- -- -- Commit the transaction
-- -- COMMIT;