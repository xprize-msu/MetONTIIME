import sys

def main ():
    basecalling_file = sys.argv[1]

    basecalling_lines = [ln.strip() for ln in open(basecalling_file,"r").readlines()]
    
    total_reads_ln = filter(lambda x: "Number of basecalled reads" in x, basecalling_lines)
    filter_reads_ln = filter(lambda x: "pass reads (qual >= 9.0 and length >= 0)" in x, basecalling_lines)
    barcode_assign_ln = filter(lambda x: "Number of reads assigned to BC" in x, basecalling_lines)

    #print([i for i in total_reads_ln])
    #print([i for i in filter_reads_ln])
    #print([i for i in barcode_assign_ln])

    total_reads_str = [i for i in total_reads_ln][0]
    total_reads = total_reads_str.split(":")[-1]
    filter_reads_str = [i for i in filter_reads_ln][0]
    filter_reads = filter_reads_str.split(" ")[1].replace(",","").strip()

    outlines = []
    outlines.append("TotalSampleReads,ReadsAfterQualityFiler,ReadsAssignedtoBarcodesAfterLengthFilter,Barcode\n")
    for ln in barcode_assign_ln:
        text,value = ln.split(":")
        barcode = text.split(" ")[-1]
        outlines.append(",".join([total_reads,filter_reads,value,"NB"+barcode[-2:]]))
    print("\n".join(outlines))
main()
