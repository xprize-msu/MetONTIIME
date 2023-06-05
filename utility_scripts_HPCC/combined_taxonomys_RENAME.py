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

def do_update_split_taxa(taxa_dict):
    update_split_taxa = []
    for taxa_level in ["d","k","p","c","o","f","g","s"]:
        if taxa_level in taxa_dict:
            update_split_taxa.append(taxa_level + "__" + taxa_dict[taxa_level])
    return update_split_taxa

def do_update_taxa(row):
    taxa = row["Taxon"]
    id = row["id"]

    split_taxa = taxa.split(";")

    taxa_dict = {}
    for t in split_taxa:
        if len(t.split("__")) > 1:
            taxa_dict[t.split("__")[0]] = t.split("__")[1]

    update_status="No change"
    # Correct species and genus
    if "s" in taxa_dict:
          
        # Remove species if in the "un" group
        if any([x in taxa_dict["s"] for x in ["uncultured","environmental","unidentified","unclassified","unverified"]]):
            taxa_dict["s"] = ""
            update_status="Species in uncultured|environmental|unidentified|unclassified|unverified"

        # Replace genus name with first part of species name if genus==family==order
        elif "_" in taxa_dict["s"]:
            genus_from_species = taxa_dict["s"].split("_")[0]
            species_from_species = taxa_dict["s"].split("_")[1]

            # Replace existing genus with existing genus if existing genus = family = order
            if taxa_dict["g"] == taxa_dict["f"] and taxa_dict["g"] == taxa_dict["o"]:
                taxa_dict["g"] = genus_from_species
                update_status="Replaced genus=family=order with scientific name genus"
         
    intermediate_taxa = do_update_split_taxa(taxa_dict)
    intermediate_status = update_status

    if id == 0.92:
        taxa_dict["s"] = ""
        taxa_dict["g"] = ""
        update_split_taxa = do_update_split_taxa(taxa_dict)
        return row["Feature ID"],";".join(intermediate_taxa),intermediate_status,";".join(update_split_taxa),"id=0.92, filter genus and species"
        #row["Updated Taxon"] = ";".join(update_split_taxa)
        #row["Update Status"] = "id=0.92, filter genus and species"
    elif id == 0.95:
        taxa_dict["s"] = ""
        update_split_taxa = do_update_split_taxa(taxa_dict)
        return row["Feature ID"],";".join(intermediate_taxa),intermediate_status,";".join(update_split_taxa),"id=0.95, filter species"
        #row["Updated Taxon"] = ";".join(update_split_taxa)
        #row["Update Status"] = "id=0.95, filter species"
    else:
        update_split_taxa = do_update_split_taxa(taxa_dict)
        return row["Feature ID"],";".join(intermediate_taxa),intermediate_status,";".join(update_split_taxa),update_status
        #row["Updated Taxon"] = ";".join(update_split_taxa)
        #row["Update Status"] = update_status

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

    # Correct taxonomy
    #filter_df["Updated Taxon"] = "MISSING"
    #filter_df["Update Status"] = "MISSING"

    # Update dataframe taxa
    update_taxa = filter_df.apply(do_update_taxa,axis=1,result_type="expand")
    update_taxa.columns = ['Update Feature ID', 'Intermediate Taxon', 'Intermediate Record', 'Update Taxon', 'Update Record']

    update_df = filter_df.merge(update_taxa, left_on='Feature ID', right_on='Update Feature ID')

    # Write dataframe
    update_df.to_csv("combined_taxonomy_DeDupAndUpdatedNames.tsv",sep="\t")
    
main()
