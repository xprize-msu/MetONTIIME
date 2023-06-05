import sys
import pandas

def main ():
    basecalling_file = "basecalling.out"

    basecalling_lines = [ln.strip() for ln in open(basecalling_file,"r").readlines()]
    
    total_reads_ln = filter(lambda x: "Number of basecalled reads" in x, basecalling_lines)
    filter_reads_ln = filter(lambda x: "pass reads (qual >= 9.0 and length >= 0)" in x, basecalling_lines)
    barcode_assign_ln = filter(lambda x: "Number of reads assigned to BC" in x, basecalling_lines)

    #print([i for i in total_reads_ln])
    #print([i for i in filter_reads_ln])
    #print([i for i in barcode_assign_ln])

    total_reads_str = [i for i in total_reads_ln][0]
    total_reads = total_reads_str.split(":")[-1].strip()
    filter_reads_str = [i for i in filter_reads_ln][0]
    filter_reads = filter_reads_str.split(" ")[1].replace(",","").strip("")

    outlines = []
    outlines.append("TotalSampleReads,ReadsAfterQualityFiler,ReadsAssignedtoBarcodes+LengthFilter,Barcode")
    for ln in barcode_assign_ln:
        text,value = ln.split(":")
        barcode = text.split(" ")[-1].strip()
        outlines.append(",".join([total_reads,filter_reads,value.strip(),"NB"+barcode[-2:]]))
    #print("\n".join(outlines))

    # Going to try to added to the metadata file, but keep the outlines in case we need to create seperate file
    metadata_file = sys.argv[1]
    metadata_df = pandas.read_csv(metadata_file) # This should be the augmented metadata file created in setup
    
    supplemental_df = pandas.DataFrame([ln.split(",") for ln in outlines[1:]])
    supplemental_df = supplemental_df.set_axis(outlines[0].split(","), axis=1, inplace=False)
    print(supplemental_df)
    
    # Merge dataframae and export
    bion_metadata_file = metadata_df.merge(supplemental_df, left_on='barcode_set', right_on='Barcode')
    bion_metadata_file.to_csv(metadata_file+".bionf")

main()
