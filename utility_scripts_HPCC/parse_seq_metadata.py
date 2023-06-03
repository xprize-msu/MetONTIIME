import sys
import pandas

### Parameter Set Defintions (DO NOT CHANGE) ###
parameter_sets = {
    "18S": {'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax.qza", 'M': "20", 'I': "0.92"},
    "16S": {'S': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-seqs.qza",'T': "/mnt/research/xprize23/eDNA_databases/SILVA_SSU/silva-138-99-tax.qza", 'M': "20", 'I': "0.92"},
    "12S": {'S': "/mnt/research/xprize23/eDNA_databases/12S_databases/12S_Singapore_merged.derep.segments.clean.seqs.qza", 'T': "/mnt/research/xprize23/eDNA_databases/12S_databases/12S_Singapore_merged.derep.segments.tax.qza", 'M': "3", 'I': "0.98"},
    "18S_alt": {'S': "/mnt/research/xprize23/eDNA_databases/18S_databases/", 'T': "/mnt/research/xprize23/eDNA_databases/18S_databases/", 'M': "3", 'I': "0.98"},
    "COI": {'S': "/mnt/research/xprize23/eDNA_databases/COI_insect_database/", 'T': "/mnt/research/xprize23/eDNA_databases/COI_insect_database/", 'M': "3", 'I': "0.98"},
}

def main ():

    # Read Metadata
    metadata_file = sys.argv[1]
    metadata_df = pandas.read_csv(metadata_file)

    # Isolate key columns and display output
    metadata_select = metadata_df.loc[:, metadata_df.columns.isin(["barcode gene targeted","barcode_set","barcoding_kit","flow_chemistry"])]
    print ("Sample Summary:\n")
    print(metadata_select)

    # Start the analsys shell script
    commands = []
    commands.append("RAW_READS_DIR=$1") # Script will take one input which is the root file of the anlysis folder from MinION_MobileLab.sh

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

        # Write a command to make an output directory
        commands.append("mkdir ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis") # Create subdirectory for analysis
        commands.append("cp ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + " .fast* ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode + "_analysis") # Copy data files
        commands.append("sh MetONTIIME.sh -w ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis -f ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis/manifest.txt \ ")
        commands.append("    -s " + primer_pars["S"] + " -t " + primer_pars["T"] + " -n 64 -c VSEARCH -m " + primer_pars["M"] + " -q 0.80 -i " + primer_pars["I"])
        
        if primer_set == "18S":
            generic_barcode = generic_barcode + "_18Salt"
            primer_pars = parameter_sets["18S_alt"]
            commands.append("mkdir ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis") # Create subdirectory for analysis
            commands.append("cp ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + " .fast* ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode + "_analysis") # Copy data files
            commands.append("sh MetONTIIME.sh -w ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis -f ${RAW_READS_DIR}_analysis/analysis/" + generic_barcode  + "_analysis/manifest.txt \ ")
            commands.append("    -s " + primer_pars["S"] + " -t " + primer_pars["T"] + " -n 64 -c VSEARCH -m " + primer_pars["M"] + " -q 0.80 -i " + primer_pars["I"])
         
    output = open("demux_analysis.sh","w")
    output.write("\n".join(commands))
    output.close()
main()
