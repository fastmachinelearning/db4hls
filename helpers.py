def get_version_cmd(xml_file: str) -> str:
    return 'xmllint --xpath "/profile/ReportVersion/Version/text()" "' + xml_file + '"'

def get_version_if_fail_cmd() -> str:
    return 'vivado_hls -version | head -n 1 | awk \'{print $11}\' | sed \'s/v//\''

def get_user() -> str:
    return 'echo $USER'

def get_host_name() -> str:
    return 'hostname'

def get_host_cpu() -> str:
    return 'lscpu | grep \"Model name:\" | awk \'{$1=$2=\"\"; print $0}\' | xargs'

def get_host_mem() -> str:
    return 'cat /proc/meminfo | grep MemTotal: | awk \'{print $2}\' | xargs'

def get_host_mem_unit() -> str:
    return 'cat /proc/meminfo | grep MemTotal: | awk \'{print $3}\' | xargs'

def get_hls_execution_time_cmd(log_file: str) -> str:
    return 'grep "C/RTL SYNTHESIS COMPLETED IN" \'' + log_file + \
           '\' | awk \'{print $6}\' | awk -F\'[h|m|s]\' \'{ print ($1 * 3600) + ($2 * 60) + $3 }\''

def get_hls_execution_time_unit_cmd(log_file: str) -> str:
    return 'echo \'s\''

def get_hls_error_msg_cmd(log_file: str) -> str:
    return 'grep "\(ERROR\|Killed\)" \'' + log_file + '\''