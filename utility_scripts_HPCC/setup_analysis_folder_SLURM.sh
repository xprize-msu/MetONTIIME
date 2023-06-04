ln -s /mnt/research/xprize23/gitclones/MetONTIIME/Launch_MinION_mobile_lab_DemuxAnalysis.sh .
ln -s /mnt/research/xprize23/gitclones/MetONTIIME/MinION_mobile_lab_noMet_NoMetONTIIME.R .
ln -s /mnt/research/xprize23/gitclones/MetONTIIME/MetONTIIME.sh .
cp /mnt/research/xprize23/gitclones/MetONTIIME/config_MinION_mobile_lab_XPRIZE23_FLO_MIN114_SQK_NBD114_24_dbSILVA_id92.R .
ln -s /mnt/research/xprize23/gitclones/MetONTIIME/config_MinION_mobile_lab_XPRIZE23_FLO_MIN114_SQK_NBD114_24_dbSILVA_id92.R config_MinION_mobile_lab.R
python /mnt/research/xprize23/gitclones/MetONTIIME/utility_scripts_HPCC/parse_seq_metadata_SLURM.py $1
