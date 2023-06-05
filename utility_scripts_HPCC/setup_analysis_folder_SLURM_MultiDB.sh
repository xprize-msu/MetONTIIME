ln -s /mnt/research/xprize23/gitclones/MetONTIIME/Launch_MinION_mobile_lab_DemuxAnalysis.sh .
ln -s /mnt/research/xprize23/gitclones/MetONTIIME/MinION_mobile_lab_noMet_NoMetONTIIME.R .
ln -s /mnt/research/xprize23/gitclones/MetONTIIME/MetONTIIME_OTU100.sh .
cp /mnt/research/xprize23/gitclones/MetONTIIME/config_MinION_mobile_lab_XPRIZE23_FLO_MIN114_SQK_NBD114_24_AllBarcodes.R .
ln -s config_MinION_mobile_lab_XPRIZE23_FLO_MIN114_SQK_NBD114_24_AllBarcodes.R config_MinION_mobile_lab.R
python /mnt/research/xprize23/gitclones/MetONTIIME/utility_scripts_HPCC/parse_seq_metadata_SLURM_MultiID_MultiDB.py $1
