import sys
import os
import pandas

def main():
    
    tax_file_list = sys.argv[1:]
    
    tax_dict = {}
    for f in tax_file_list:
        tax_df = pandas.read_csv(f,sep="\t")
        tax_filter_df = tax_df[tax_df["Consensus"] >= 0.9]        
        tax_dict[f] = tax_filter_df
    
    for i in range(len(tax_dict.keys())): 
        line = list(tax_dict.keys())[i].split("/")[-1]

        main_df = tax_dict[list(tax_dict.keys())[i]]
        uniq_taxa = set(main_df["Taxon"])

        line = line + "\t" + str(len(uniq_taxa))

        for j in range(i+1,len(tax_dict.keys())):
            next_df = tax_dict[list(tax_dict.keys())[j]]
            next_taxa = set(next_df["Taxon"])
            overlap = uniq_taxa.intersection(next_taxa)

            line = line + "\t" + str(len(overlap))

        print(line)
main()
