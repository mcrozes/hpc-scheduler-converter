# SOCA Input Flip

Here is a simple script which convert your existing scheduler input files into other schedulers syntax. If no target is defined, the script will automatically convert the input file into PBS as this is the default scheduler used by [Scale-Out Computing on AWS](https://awslabs.github.io/scale-out-computing-on-aws/)

# Supported schedulers
- lsf
- pbs
- slurm
- sge

# Usage

```bash
# LSF --> PBS
python soca_input_flip -s lsf -t pbs -i test_input.lsf

# SGE --> SLURM
python soca_input_flip -s sge -t slurm -i test_input.sge

# SLURM --> PBS
python soca_input_flip --source slurm --target pbs --input test_input.slurm

# etc ... 
```

# Keep track of what's being changed

Any modified lines are commented out and prefixed with `REPLACED` tag to simplify future debugging or troubleshooting.

```
#!/bin/bash
#(REPLACED) #BSUB -J job_name # job name
#PBS -N job_name # job name
#(REPLACED) #BSUB -W 01:00 # wall-clock time (hrs:mins)
#PBS -l walltime=01:00 # wall-clock time (hrs:mins)
#(REPLACED) #BSUB -n 64 # number of tasks in job
#PBS -l nodes= 64 # number of tasks in job
```


# Disclaimer
I have developed this script based on my needs and tried to make it as generic as possible. With that said, you probably want to double check the output(s) generated being generated :). 

Feel free to report any potential issues/inconsistencies by submitting a Github Issue or a Pull Request.