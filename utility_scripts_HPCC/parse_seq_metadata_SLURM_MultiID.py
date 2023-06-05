import sys
import os
import pandas

### Parameter Set Defintions (DO NOT CHANGE) ###
parameter_sets = {
    #"18S": {"Time": "240", "Mem": "256GB", "N": "64", 'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax.qza", 'M': "20", 'I': "0.92"},
    # New 18S filtered for primers and eukarya    
    "18S": {"Time": "120", "Mem": "128GB", "N": "64", 'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-eukaya-derepONLY-seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax-derepONLY.qza", 'M': "20", 'I': ["0.92","0.95","0.98"]},
    "16S": {"Time": "120", "Mem": "96GB", "N": "64", 'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-eukaya-derepONLY-seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax-derepONLY.qza", 'M': "20", 'I': "0.92"},
    "12S": {"Time": "120", "Mem": "64GB", "N": "32", 'S': "/mnt/research/xprize23/eDNA_databases/12S_databases/12S_Singapore_merged.derepONLY.clean.seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/12S_databases/12S_Singapore_merged.derep.tax.qza", 'M': "3", 'I': "0.98"},
    "COI": {"Time": "180", "Mem": "256GB", "N": "64", 'S': "/mnt/research/xprize23/eDNA_databases/COI_insect_database/COI.derepONLY.clean.seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/COI_insect_database/COI.derep.tax.qza", 'M': "3", 'I': "0.98"},
}

def main ():

    # Read Metadata
    metadata_file = sys.argv[1]
    metadata_df = pandas.read_csv(metadata_file)

    # Isolate key columns and display output
    metadata_select = metadata_df.loc[:, metadata_df.columns.isin(["barcode gene targeted","barcode_set","barcoding_kit","flow_chemistry","target_read_length"])]
    print ("Sample Summary:\n")
    print(metadata_select)

    # Start the analysis shell script
    commands = []
    commands.append("RAW_READS_DIR=$1") # Script will take one input which is the root file of the anlysis folder from MinION_MobileLab.sh
    commands.append("source /mnt/research/xprize23/launch_MetONTIIME_env.sh")

    # Start of the processing shell scripts
    processing = []
    processing.append("RAW_READS_DIR=$1")
    processing.append("mkdir taxonomy_output")

    # Augment Dataframe
    row_n = metadata_df.shape[0]
    metadata_df_aug = metadata_df.assign(path=["NA"]*row_n)
    metadata_df_aug = metadata_df.assign(taxid_protocol=["NA"]*row_n)
    pwd=os.getcwd()

    # Write commands for each barcode
    skip_list = [] # Record barcodes and skip ones already done (because multiple primer runs may be pooled under the same BC)
    for index, row in metadata_select.iterrows():
        barcode = row["barcode_set"]
        generic_barcode = "BC" + barcode.split("NB")[-1]
        
        primer_set = row["barcode gene targeted"]
        primer_pars = parameter_sets[primer_set]

        # Check
        #print(generic_barcode)
        #print(primer_set)
        #print(primer_pars)

        if not barcode in skip_list:
            skip_list.append(barcode)
   
            # Write on command per id_percent
            for id in primer_pars["I"]:
                analysis_path = "${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_" + id  + "_analysis"

                # Write analysis commands
                commands.append("mkdir " + analysis_path) # Create subdirectory for analysis
                commands.append("cp ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + ".fast* " + analysis_path) # Copy data files
                wrapper_command = '"sh MetONTIIME_OTU100.sh -w ' + analysis_path  +  " -f " + analysis_path + "/manifest.txt -s " + primer_pars["S"] + " -t " + primer_pars["T"] + " -n " +  primer_pars["N"] + " -c VSEARCH -m " + primer_pars["M"] + " -q 0.80 -i " + id + '"'
                commands.append("sbatch --reservation=xprize --mem " +  primer_pars["Mem"] + " --cpus-per-task " +  primer_pars["N"] + " --time " +  primer_pars["Time"] + " --wrap " + wrapper_command)

                # Write processing commands
                processing.append("unzip " + analysis_path + "/taxonomy.qza -d " + analysis_path + "/taxonomy.qza_DIR")
                processing.append("grep -v -E 'Unassigned|uncultured|environmental|unidentified|unclassified|unverified' " + analysis_path + "/taxonomy.qza_DIR/*/data/taxonomy.tsv > taxonomy_output/" + generic_barcode + "_" + id + ".taxonomy.filtered.tsv")  
        
                # Update metadata
                metadata_df_aug.loc[metadata_df_aug["barcode_set"]==barcode,"path"] = pwd + "/taxonomy_output/" + generic_barcode + "_" + id + ".taxonomy.filtered.tsv"
                metadata_df_aug.loc[metadata_df_aug["barcode_set"]==barcode,"taxid_protocol"] = "Database:" + primer_pars["S"] + ";" + primer_pars["T"] + ";Method:VSEARCH;Matches" + primer_pars["M"] + ";QueryCoverage:0.80;Identity%:" + "::".join(primer_pars["I"])
        
    output = open("demux_analysis.sh","w")
    output.write("\n".join(commands))
    output.close()

    output = open("demux_postprocessing.sh","w")
    output.write("\n".join(processing))
    output.close()

    metadata_df_aug.to_csv(metadata_file+".augmented")

main()
