#!/bin/bash

#
# Copyright 2021 Simone Maestri. All rights reserved.
# Simone Maestri <simone.maestri@univr.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

RAW_READS_DIR=$1
RAW_READS_DIR_FULL=$(realpath $RAW_READS_DIR)

umask 0007

# Prepare the python environment
if [ `echo $PATH | grep "conda"` ]
then
    echo ""
    echo "You're personal Anaconda/Miniconda installation is in your PATH variable."
    echo "***Conda will be deactivated and your PATH modified***"
    echo "Once you are done working in the xprize directory, run 'source ~/.bashrc'"
    conda deactivate || :
    export PATH=`echo $PATH | tr ":" "\n" | grep -v "conda" | perl -pe 'chomp if eof' | tr "\n" ":"`
fi
export CONDA3PATH=/mnt/research/xprize23/miniconda3
module load Conda/3
source activate MetONTIIME_env

PIPELINE_DIR=$(realpath $( dirname "${BASH_SOURCE[0]}" ))
echo 1. Start Basecalling, output in basecalling.out
Rscript $PIPELINE_DIR/MinION_mobile_lab_noMet_NoMetONTIIME.R $PIPELINE_DIR/config_MinION_mobile_lab.R $RAW_READS_DIR_FULL > basecalling.out 2>&1
echo 2. Start Demultiplexed Analysis, output in demux_analysis.out
sh demux_analysis.sh $RAW_READS_DIR_FULL > demux_analysis.out 2>&1
echo 3. Start Postprocessing
sh demux_postprocessing.sh $RAW_READS_DIR
