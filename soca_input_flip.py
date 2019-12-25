'''

Simple Input Convert for SOCA: https://awslabs.github.io/scale-out-computing-on-aws/
- - - - - -
Convert PBS, LSF, SLURM or SGE jobs.
'''

import argparse
import sys
import os
import re


def parameters(scheduler):
    params = {
        "parameter_scheduler": {"lsf": "#BSUB", "pbs": "#PBS", "slurm": "#SBATCH", "sge": "#$"},
        "parameter_job_queue": {"lsf": "-q", "pbs": "-q", "slurm": "-q", "sge": "-q"},
        "parameter_job_nodes": {"lsf": "-n", "pbs": "-l nodes=", "slurm": "-N", "sge": "__NONE__"},
        "parameter_job_process_count": {"lsf": "-n", "pbs": "-l ppn=", "slurm": "-n", "sge": "__NONE__"},
        "parameter_job_walltime": {"lsf": "-W", "pbs": "-l walltime=", "slurm": "-t", "sge": "-l h_rt"},
        "parameter_job_std_err": {"lsf": "-e", "pbs": "-e", "slurm": "-e", "sge": "-o"},
        "parameter_job_std_out": {"lsf": "-o", "pbs": "-o", "slurm": "-e", "sge": "-o"},
        "parameter_job_copy_environment": {"lsf": "__NONE__", "pbs": "-V", "slurm": "--export=", "sge": "-V"},
        "parameter_job_event_notification": {"lsf": "-B", "pbs": "-m abe", "slurm": "--mail-type=", "sge": "-m abe"},
        "parameter_job_email_address": {"lsf": "-u", "pbs": "-M", "slurm": "--mail-user=", "sge": "-M"},
        "parameter_job_name": {"lsf": "-J", "pbs": "-N", "slurm": "--job-name=", "sge": "-N"},
        "parameter_job_working_directory": {"lsf": "__NONE__", "pbs": "__NONE__", "slurm": "--workdir=", "sge": "-wd"},
        "parameter_job_memory_size": {"lsf": "-M", "pbs": "-l mem=", "slurm": "--mem=", "sge": "-l mem_free="},
        "parameter_job_dependency": {"lsf": "-w", "pbs": "-d", "slurm": "--depends=", "sge": "-hold_jid"},
        "parameter_job_project": {"lsf": "__NONE__", "pbs": "-P", "slurm": "--wckey", "sge": "-P"},
        "parameter_job_array": {"lsf": "-J", "pbs": "-P", "slurm": "--array=", "sge": "-t"},
        "parameter_job_begin_time": {"lsf": "-b", "pbs": "-A", "slurm": "--begin=", "sge": "-a"},
        "parameter_quality_of_service": {"lsf": "__NONE__", "pbs": "-l qos=", "slurm": "--qos=", "sge": "__NONE__"},
        "environment_job_id": {"lsf": "$LSB_JOBID", "pbs": "$PBS_JOBID", "slurm": "$SLURM_JOBID", "sge": "$JOB_ID"},
        "environment_submit_directory": {"lsf": "$LSB_SUBCWD", "pbs": "$PBS_O_WORKDIR", "slurm": "SLURM_SUBMIT_DIR", "sge": "$SGE_O_WORKDIR"},
        "environment_node_list": {"lsf": "$LSB_NODES", "pbs": "$PBS_NODEFILE", "slurm": "$SLURM_JOB_NODELIST", "sge": "$PE_HOSTFILE"},
        "environment_nodes_list_alt": {"lsf": "$LSB_DJOB_HOSTFILE", "pbs": "$PBS_NODEFILE", "slurm": "$SLURM_JOB_NODELIST", "sge": "$PE_HOSTFILE"},
        "environment_submit_host": {"lsf": "$LSB_SUB_HOST", "pbs": "$PBS_O_HOST", "slurm": "$SLURM_SUBMIT_HOST", "sge": "$SGE_O_HOST"}
    }
    return {key: value[scheduler] for (key, value) in params.items()}


if __name__ == "__main__":
    ALLOWED_VALUES = ["slurm", "lsf", "sge", "pbs"]
    PREFIX_COMMENTED_LINES = "#(REPLACED) "
    input_text = []
    replaced_text = []
    output_text = []
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', nargs='?', required=True, help="Source of your input file (lsf, sge or slurm)")
    parser.add_argument('-t', '--target', nargs='?', default="pbs", help="Target of your input file (lsf, sge or slurm)")
    parser.add_argument('-i', '--input', nargs='?', required=True, help="path to the file you want to translate")
    arg = parser.parse_args()
    scheduler = str(arg.source).lower()
    target = str(arg.target).lower()
    if scheduler not in ALLOWED_VALUES:
        print("Scheduler must be one of these value (case insensitive): " + " ".join(ALLOWED_VALUES))
        sys.exit(1)

    if target not in ALLOWED_VALUES:
        print("Target must be one of these value (case insensitive): " + " ".join(ALLOWED_VALUES))
        sys.exit(1)

    if target == scheduler:
        print("Target and Scheduler must be different")
        sys.exit(1)

    # Convert input file into array
    input_file = os.path.abspath(arg.input)
    try:
        with open(input_file) as fp:
            for line in fp:
                input_text.append(line.strip().split('\n')[0])
            fp.close()

    except FileNotFoundError as e:
        print("Unable to locate: " + input_file)
        sys.exit(1)
    except Exception as e:
        print("Error while reading: " + input_file + '. Trace: ' + str(e))
        sys.exit(1)

    # Retrieve parameters
    source_mapping = parameters(scheduler)
    target_mapping = parameters(target)

    # Convert input file and replace patterns
    for line in input_text:
        is_changed = False
        source_line = line
        for k, v in source_mapping.items():
            index = 0
            if v.startswith("$"):
                pattern = "\\" + v
            else:
                pattern = v

            find_pattern = re.search(pattern, line)
            if find_pattern:
                if 'parameter' in k:
                    if line.startswith("#") is True:
                        line = line.replace(v, target_mapping[k])
                        is_changed = True
                if 'environment' in k:
                    is_changed = True
                    line = line.replace(v, target_mapping[k])
            index += 1

        if is_changed is True:
            output_text.append(PREFIX_COMMENTED_LINES + source_line + '\n' + line)
        else:
            output_text.append(line)

    # Print Converted Code
    print("\n".join(output_text))
