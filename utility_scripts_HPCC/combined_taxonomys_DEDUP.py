import sys
import os
import pandas

def read_taxa_file_list(file_path):
    """
    Reads a text file where each line is foramt as 'file_path,id_threshold' and stores
    these pairs in a dictionary.
    """

    # Read the input file
    sample_lines = [line.strip() for line in open(file_path, "r").readlines()]

    # Store value in each line as in a dictionary
    file_and_ids = {}
    for ln in sample_lines:
        split_ln = ln.split(",")
        if len(split_ln) > 2:
           print("Warning: the following line has more than one values assocaited with it\n" + ln)
        file_and_ids[split_ln[0]] = split_ln[1].strip()

    return file_and_ids

def main():

    # Take a list of taxa files as input    
    files_and_ids = read_taxa_file_list(sys.argv[1])
    tax_file_list = list(files_and_ids.keys())

    # Read each taxonomy file into a dictionary as a dataframe     
    tax_dfs = []
    for f in tax_file_list:
        tax_df = pandas.read_csv(f,sep="\t")
        tax_df["file"] = f
        tax_df["id"] = float(files_and_ids[f])
        tax_dfs.append(tax_df)
    
    # Merge taxa, keep obsv with the highest id
    merge_df = pandas.concat(tax_dfs,ignore_index=True)
    filter_df = merge_df.drop(merge_df[merge_df['Taxon'] == 'Unassigned'].index)
    filter_df = filter_df.sort_values('id').drop_duplicates(subset='Feature ID', keep='last')
    
    # Check
    print(merge_df.shape)
    print(filter_df.shape)
    print(filter_df["id"].value_counts())
    print("Obsv Count")
    print((filter_df["Consensus"] > 0.9).sum())
    print((filter_df["Consensus"] > 0.8).sum())
    print((filter_df["Consensus"] > 0.7).sum())
    print("Taxa Count")
    print(len(filter_df.loc[filter_df["Consensus"] > 0.9,"Taxon"].unique()))
    print(len(filter_df.loc[filter_df["Consensus"] > 0.8,"Taxon"].unique()))
    print(len(filter_df.loc[filter_df["Consensus"] > 0.7,"Taxon"].unique()))

    # Write dataframe
    filter_df.to_csv("combined_taxonomy_filteredDeDup.tsv",sep="\t")
    
main()
