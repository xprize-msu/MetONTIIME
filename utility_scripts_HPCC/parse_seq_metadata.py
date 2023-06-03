import sys
import os
import pandas

### Parameter Set Defintions (DO NOT CHANGE) ###
parameter_sets = {
    "18S": {'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax.qza", 'M': "20", 'I': "0.92"},
    "16S": {'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-seqs.qza",'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax.qza", 'M': "20", 'I': "0.92"},
    "12S": {'S': "/mnt/research/xprize23/eDNA_databases/12S_databases/12S_Singapore_merged.derep.segments.clean.seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/12S_databases/12S_Singapore_merged.derep.segments.tax.qza", 'M': "3", 'I': "0.98"},
    "18S_alt": {'S': "/mnt/research/xprize23/eDNA_databases/18S_databases/18S_Singapore_merged.derep.segments.clean.seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/18S_databases/18S_Singapore_merged.derep.segments.tax.qza", 'M': "3", 'I': "0.98"},
    "COI": {'S': "/mnt/research/xprize23/eDNA_databases/COI_insect_database/COI.derep.segments.clean.seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/COI_insect_database/COI.derep.segments.tax.qza", 'M': "3", 'I': "0.98"},
}

def main ():

    # Read Metadata
    metadata_file = sys.argv[1]
    metadata_df = pandas.read_csv(metadata_file)

    # Isolate key columns and display output
    metadata_select = metadata_df.loc[:, metadata_df.columns.isin(["barcode gene targeted","barcode_set","barcoding_kit","flow_chemistry"])]
    print ("Sample Summary:\n")
    print(metadata_select)

    # Start the analysis shell script
    commands = []
    commands.append("RAW_READS_DIR=$1") # Script will take one input which is the root file of the anlysis folder from MinION_MobileLab.sh

    # Start of the processing shell scripts
    processing = []
    processing.append("mkdir taxonomy_output")

    # Augment Dataframe
    row_n = metadata_df.shape[1]
    metadata_df_aug = metadata_df.assign(path=["NA"]*row_n)
    pwd=os.getcwd()

    # Write commands for each barcode
    for index, row in metadata_select.iterrows():
        barcode = row["barcode_set"]
        generic_barcode = "BC" + barcode.split("NB")[-1]
        
        primer_set = row["barcode gene targeted"]
        primer_pars = parameter_sets[primer_set]

        # Check
        #print(generic_barcode)
        #print(primer_set)
        #print(primer_pars)
  
        analysis_path = "${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis"
   
        # Write analysis commands
        commands.append("mkdir " + analysis_path) # Create subdirectory for analysis
        commands.append("cp ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + " .fast*" + analysis_path) # Copy data files
        commands.append("sh MetONTIIME.sh -w " + analysis_path  +  "-f " + analysis_path + "/manifest.txt \ ")
        commands.append("    -s " + primer_pars["S"] + " -t " + primer_pars["T"] + " -n 64 -c VSEARCH -m " + primer_pars["M"] + " -q 0.80 -i " + primer_pars["I"])

        # Write processing commands
        processing.append("unzip " + analysis_path + "/taxonomy.qza -d " + analysis_path + "/taxonomy.qza_DIR")
        processing.append("grep -v -E 'Unassigned|uncultured|environmental|unidentified|unclassified|unverified' " + analysis_path + "/taxonomy.qza_DIR/taxonomy.tsv > taxonomy_output/" + generic_barcode + ".taxonomy.filtered.tsv")  
        
        # Update metadata
        metadata_df_aug.loc[metadata_df_aug["barcode_set"]==barcode,"path"] = pwd + "/taxomy_output/" + generic_barcode + ".taxonomy.filtered.tsv"
        
        
        if primer_set == "18S":
            generic_barcode = generic_barcode + "_18Salt"
            primer_pars = parameter_sets["18S_alt"]
            commands.append("mkdir " + analysis_path) # Create subdirectory for analysis
            commands.append("cp ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + " .fast*" + analysis_path) # Copy data files
            commands.append("sh MetONTIIME.sh -w " + analysis_path  +  "-f " + analysis_path + "/manifest.txt \ ")
            commands.append("    -s " + primer_pars["S"] + " -t " + primer_pars["T"] + " -n 64 -c VSEARCH -m " + primer_pars["M"] + " -q 0.80 -i " + primer_pars["I"])

            processing.append("unzip " + analysis_path + "/taxonomy.qza -d " + analysis_path + "/taxonomy.qza_DIR")
            processing.append("grep -v -E 'Unassigned|uncultured|environmental|unidentified|unclassified|unverified' " + analysis_path + "/taxonomy.qza_DIR/taxonomy.tsv > taxonomy_output/" + generic_barcode + ".taxonomy.filtered.tsv")  
        
            metadata_df_aug.loc[metadata_df_aug["barcode_set"]==barcode,"path"] = pwd + "/taxomy_output/" + generic_barcode + ".taxonomy.filtered.tsv"


    output = open("demux_analysis.sh","w")
    output.write("\n".join(commands))
    output.close()

    output = open("demux_postprocessing.sh","w")
    output.write("\n".join(commands))
    output.close()

    metadata_df_aug.to_csv("metadata_file"+.augmented)

main()
