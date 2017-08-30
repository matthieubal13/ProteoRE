import argparse
import re


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", required=True)
    parser.add_argument("-m", "--match", help="Exact macth")
    parser.add_argument("--protein_IDs", nargs=2, metavar=("IDs", "ncol"), help="Protein IDs to filter, separated by ';'")
    parser.add_argument("--protein_IDs_file", nargs=2, metavar=("IDs", "ncol"), help="File contains protein IDs to filter, tab format")
    parser.add_argument("--protein_names", nargs=2, metavar=("IDs", "ncol"), help="Protein names to filter, separated by ';'")
    parser.add_argument("--protein_names_file", nargs=2, metavar=("IDs", "ncol"), help="File contains protein names to filter, separated by ';'")
    parser.add_argument("--gene_names", nargs=2, metavar=("IDs", "ncol"), help="Gene names to filter, separated by ';'")
    parser.add_argument("--gene_names_file", nargs=2, metavar=("IDs", "ncol"), help="Gene names to filter, separated by ';'")
    #parser.add_argument("--fasta_headers", help="Fasta headers to filter, separated by ';'")
    #parser.add_argument("--fasta_headers_file", help="Fasta headers to filter, separated by ';'")
    parser.add_argument("--peptides", nargs=3, metavar=("VALUE", "ncol", "EQUATION"), help="Peptides to filter, separated by ';'")
    parser.add_argument("--iBAQ", nargs=3, metavar=("VALUE", "COLUMN NUMBER", "EQUATION"))
    parser.add_argument("--number_of_proteins", nargs=3, metavar=("VALUE", "ncol", "EQUATION"))
    parser.add_argument("--intensity", nargs=3, metavar=("VALUE", "ncol", "EQUATION"))
    parser.add_argument("--q_value", nargs=3, metavar=("value", "ncol", "equation"))
    parser.add_argument("--score", nargs=3, metavar=("VALUE", "ncol", "EQUATION"))
    #parser.add_argument("--identification_type")
    parser.add_argument("-o", "--output", default="output.txt")
    parser.add_argument("--trash_file", default="trash_MQfilter.txt")

    args = parser.parse_args()

    filters(args)

    # python filter2.py -i "/projet/galaxydev/galaxy/tools/proteore_uc1/proteinGroups_Maud.txt" --protein_IDs "A2A288:A8K2U0" --peptides 2 "=" -o "test-data/output_MQfilter.txt"
    

def isnumber(format, n):
    float_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")
    int_format = re.compile("^[\-]?[1-9][0-9]*$")
    test = ""
    if format == "int":
        test = re.match(int_format, n)
    elif format == "float":
        test = re.match(float_format, n)
    if test:
        return True
    else:
        return False

def filters(args):
    MQfilename = args.input
    MQfile = readMQ(MQfilename)
    prot_IDs = None
    prot_names = None
    gene_names = None
    prot_IDs_ncol = None
    prot_names_ncol = None
    gene_names_ncol = None
    if args.protein_IDs_file:
        prot_IDs = readOption(args.protein_IDs_file[0])
        prot_IDs_ncol = args.protein_IDs_file[1]
    elif args.protein_IDs:
        prot_IDs = args.protein_IDs[0]
        prot_IDs_ncol = args.protein_IDs[1]
    if args.protein_names_file:
        prot_names = readOption(args.protein_names_file[0])
        prot_names_ncol = args.protein_names_file[1]
    elif args.protein_names:
        prot_names = args.protein_names[0]
        prot_names_ncol = args.protein_names[1]
    if args.gene_names_file:
        gene_names = readOption(args.gene_names_file[0])
        gene_names_ncol = args.gene_names_file[1]
    elif args.gene_names:
        gene_names = args.gene_names[0]
        gene_names_ncol = args.gene_names[1]
    results = filter_kw(MQfile, prot_IDs, prot_IDs_ncol, prot_names, prot_names_ncol, gene_names, gene_names_ncol, args.match)
    if args.peptides:
        if isnumber("int", args.peptides[0]):
            results = filter_pep(results[0], results[1], args.peptides[0], args.peptides[1], args.peptides[2])
        else:
            raise ValueError("Please enter an integer in filter of Peptides")
    if args.number_of_proteins:
        if isnumber("int", args.number_of_proteins[0]):
            results = filter_noProt(results[0], results[1], args.number_of_proteins[0], args.number_of_proteins[1], args.number_of_proteins[2])
        else:
            raise ValueError("Please enter an integer in filter of Number of proteins")
    if args.q_value:
        if isnumber("float", args.q_value[0]):
            results = filter_qVal(results[0], results[1], args.q_value[0], args.q_value[1], args.q_value[2])
        else:
            raise ValueError("Please enter a number in filter of Number of proteins")
    if args.score:
        if isnumber("float", args.score[0]):
            results = filter_score(results[0], results[1], args.score[0], args.score[1], args.score[2])
        else:
            raise ValueError("Please enter a number in filter of Score")
    if args.intensity:
        if isnumber("float", args.intensity[0]):
            results = filter_intensity(results[0], results[1], args.intensity[0], args.intensity[1], args.intensity[2])
        else:
            raise ValueError("Please enter a number in filter of Intensity")
    if args.iBAQ:
        if isnumber("float", args.iBAQ[0]):
            results = filter_iBAQ(results[0], results[1], args.iBAQ[0], args.iBAQ[1], args.iBAQ[2])
        else:
            raise ValueError("Please enter a number in filter of iBAQ")

    # Write results to output
    output = open(args.output, "w")
    output.write("".join(results[0]))
    output.close()

    # Write deleted lines to trash_file
    trash = open(args.trash_file, "w")
    #print("".join(results[1]))
    trash.write("".join(results[1]))
    trash.close()

def readOption(filename):
    f = open(filename, "r")
    file = f.read()
    #print(file)
    filter_list = file.split("\n")
    #print(filter_list)
    filters = ""
    for i in filter_list:
        filters += i + ":"
    filters = filters[:-1]
    #print(filters)
    return filters

def readMQ(MQfilename):
    # Read MQ file
    mqfile = open(MQfilename, "r")
    mq = mqfile.readlines()
    # Remove empty lines (contain only space or new line or "")
    [mq.remove(blank) for blank in mq if blank.isspace() or blank == ""]     
    return mq

def filter_kw(MQfile,  prot_ids = None, prot_IDs_ncol = None, prot_names = None, prot_names_ncol = None, gene_names = None, gene_names_ncol = None, match = None):
    mq = MQfile
    #print(len(mq))
    # Extract columns name
    #columns = mq[0].rstrip().replace('"', "").split("\t")
    #print("columns: ", columns)
    # Major protein id
    #if "Majority protein IDs" in columns:
    if prot_ids:
        if prot_IDs_ncol and isnumber("int", prot_IDs_ncol.replace("c", "")):
            id_index = int(prot_IDs_ncol.replace("c", "")) - 1 #columns.index("Majority protein IDs")
        else:
            raise ValueError("Please specify the column where you would like to apply protein IDs filter with valid format")

    # Protein name
    if prot_names_ncol and isnumber("int", prot_names_ncol.replace("c", "")): #"Protein names" in columns:
        prot_name_index = int(prot_names_ncol.replace("c", "")) - 1 #columns.index("Protein names")
    else:
        raise ValueError("Please specify the column where you would like to apply protein names filter with valid format")

    # Gene names
    if gene_names_ncol and isnumber("int", gene_names_ncol.replace("c", "")): #"Gene names" in columns:
        gene_name_index = int(gene_names_ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply gene names filter with valid format")

    # Filter by keywords
    prot_ids = prot_ids.upper().split(":")
    [prot_ids.remove(blank) for blank in prot_ids if blank.isspace() or blank == ""]
    prot_names = prot_names.upper().split(":")
    [prot_names.remove(blank) for blank in prot_names if blank.isspace() or blank == ""]
    gene_names = gene_names.upper().split(":")
    [gene_names.remove(blank) for blank in gene_names if blank.isspace() or blank == ""]
        
    filtered_lines = []
    filtered_lines.append(mq[0])
    for line in mq[1:]:    
        prot_id = line.split("\t")[id_index].replace('"', "").split(";")#[0] not use here as the other ids might be in the filter?       
        prot_name = line.split("\t")[prot_name_index].replace('"', "").split(";")#[0] 
        gene_name = line.split("\t")[gene_name_index].replace('"', "").split(";")#[0]
        one_id_line = line.replace(line.split("\t")[id_index], prot_id[0]) # Take only first protein IDs
        one_id_line = one_id_line.replace(line.split("\t")[gene_name_index], gene_name[0]) # Take only first gene name
        one_id_line = one_id_line.replace(line.split("\t")[prot_name_index], prot_name[0]) # Take only first protein name
        #print(prot_id[0])
      
        if match != "false":
            # Filter protein IDs
            if prot_ids and any (pid.upper() in prot_ids for pid in prot_id):
                #ids = prot_ids.split(":")
                #print(prot_ids.split(":"))
                #if prot_id in ids:
                filtered_lines.append(one_id_line)
                mq.remove(line)
            # Filter protein names
            elif prot_names and any (pn.upper() in prot_names for pn in prot_name):
                filtered_lines.append(one_id_line)
                mq.remove(line)
            # Filter gene names
            elif gene_names and any (gn.upper() in gene_names for gn in gene_name):
                filtered_lines.append(one_id_line)
                mq.remove(line)
            else:
                mq[mq.index(line)] = one_id_line
        else:
            #print(prot_names.upper().split(":"), prot_name, [ft in pid.upper() for pid in prot_id for ft in prot_ids.upper().split(":")])
            # Filter protein IDs
            if prot_ids and any (ft in pid.upper() for pid in prot_id for ft in prot_ids):
                #ids = prot_ids.split(":")
                print(prot_ids)
                #print(prot_ids.split(":"))
                print(prot_id)
                #if prot_id in ids:
                filtered_lines.append(one_id_line)
                mq.remove(line)
            # Filter protein names
            elif prot_names and any (ft in pn.upper() for pn in prot_name for ft in prot_names):
                filtered_lines.append(one_id_line)
                mq.remove(line)
            # Filter gene names
            elif gene_names and any (ft in gn.upper() for gn in gene_name for ft in gene_names):
                filtered_lines.append(one_id_line)
                mq.remove(line)
            else:
                mq[mq.index(line)] = one_id_line
    return mq, filtered_lines #output, trash_file

def filter_pep(MQfile, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    # Extract columns name
    #columns = mq[0].rstrip().replace('"', "").split("\t")
    #print("columns: ", columns)

    # Number of protein column index
    """if "Peptides" in columns:
        pep_index = columns.index("Peptides")
    else:
        raise ValueError("Could not find 'Peptides' column in input file")"""
    
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        pep_index = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply peptide filter with valid format")

    # Filter number of protein
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        filtered_prots.append(mq[0])
    for prot in mq[1:]:
        filter_value = int(filter_value)
        pep = prot.split("\t")[pep_index].replace('"', "")
        if opt == "<":
            if not int(pep) < filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == "<=":
            if not int(pep) <= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">":
            #print(prot.number_of_prots, filter_value, int(prot.number_of_prots) > filter_value)
            if not int(pep) > filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">=":
            if not int(pep) >= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        else:
            if not int(pep) == filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
    return mq, filtered_prots #output, trash_file

def filter_noProt(MQfile, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    # Extract columns name
    #columns = mq[0].rstrip().replace('"', "").split("\t")
    #print("columns: ", columns)

    # Number of protein column index
    """if "Number of proteins" in columns:
        no_prot_index = columns.index("Number of proteins")
    else:
        raise ValueError("Could not find 'Number of proteins' column in input file")"""
        
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        no_prot_index = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply number of protein filter with valid format")

    # Filter number of protein
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        filtered_prots.append(mq[0])
    for prot in mq[1:]:
        filter_value = int(filter_value)
        number_of_prots = prot.split("\t")[no_prot_index].replace('"', "")
        if opt == "<":
            if not int(number_of_prots) < filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == "<=":
            if not int(number_of_prots) <= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">":
            #print(prot.number_of_prots, filter_value, int(prot.number_of_prots) > filter_value)
            if not int(number_of_prots) > filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">=":
            if not int(number_of_prots) >= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        else:
            if not int(number_of_prots) == filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
    return filtered_prots, mq #output, trash_file

def filter_qVal(MQfile, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    # Extract columns name
    #columns = mq[0].rstrip().replace('"', "").split("\t")
    #print("columns: ", columns)

    # Number of protein column index
    """if "Q-value" in columns:
        qVal_index = columns.index("Q-value")
    else:
        raise ValueError("Could not find 'Q-value' column in input file")"""
        
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        qVal_index = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply Q-value filter with valid format")

    # Filter number of protein
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        filtered_prots.append(mq[0])
    for prot in mq[1:]:
        filter_value = float(filter_value)
        qVal = prot.split("\t")[qVal_index].replace('"', "")
        if opt == "<":
            if not float(qVal) < filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == "<=":
            if not float(qVal) <= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">":
            #print(prot.number_of_prots, filter_value, int(prot.number_of_prots) > filter_value)
            if not float(qVal) > filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">=":
            if not float(qVal) >= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        else:
            if not float(qVal) == filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
    return mq, filtered_prots #output, trash_file         
        
def filter_score(MQfile, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    # Extract columns name
    #columns = mq[0].rstrip().replace('"', "").split("\t")
    #print("columns: ", columns)

    # Number of protein column index
    """if "Score" in columns:
        score_index = columns.index("Score")
    else:
        raise ValueError("Could not find 'Score' column in input file")"""
        
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        score_index = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply Score filter with valid format")

    # Filter number of protein
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        filtered_prots.append(mq[0])
    for prot in mq[1:]:
        filter_value = float(filter_value)
        score = prot.split("\t")[score_index].replace('"', "")
        if opt == "<":
            if not float(score) < filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == "<=":
            if not float(score) <= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">":
            #print(prot.number_of_prots, filter_value, int(prot.number_of_prots) > filter_value)
            if not float(score) > filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">=":
            if not float(score) >= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        else:
            if not float(score) == filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
    return mq, filtered_prots #output, trash_file 

def filter_inten(MQfile, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    # Extract columns name
    #columns = mq[0].rstrip().replace('"', "").split("\t")
    #print("columns: ", columns)

    # Number of protein column index
    """if "Intensity" in columns:
        inten_index = columns.index("Intensity")
    else:
        raise ValueError("Could not find 'Intensity' column in input file")"""
        
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        inten_index = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply Intensity filter with valid format")

    # Filter number of protein
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        filtered_prots.append(mq[0])
    for prot in mq[1:]:
        filter_value = int(filter_value)
        inten = prot.split("\t")[inten_index].replace('"', "")
        if opt == "<":
            if not int(inten) < filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == "<=":
            if not int(inten) <= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">":
            #print(prot.number_of_prots, filter_value, int(prot.number_of_prots) > filter_value)
            if not int(inten) > filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        elif opt == ">=":
            if not int(inten) >= filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
        else:
            if not int(inten) == filter_value:
                filtered_prots.append(prot)
                mq.remove(prot)
    return mq, filtered_prots #output, trash_file

def filter_iBAQ(MQfile, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    #columns = MQfile[1]

    """column = int(column) - 1
    print(mq[0].split("\t")[column])"""
    
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        column = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where you would like to apply iBAQ/iBAQ ratio filter with valid format")

    # Filter number of protein
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        filtered_prots.append(mq[0])

    for prot in mq[1:]:
        filter_value = float(filter_value)
        #print(filter_value, opt)
        iBAQ = prot.split("\t")[column].replace('"', "")
        if iBAQ.replace(".", "", 1).isdigit():
            if opt == "<":
                if not float(iBAQ) < filter_value:
                    filtered_prots.append(prot)
                    mq.remove(prot)
            elif opt == "<=":
                if not float(iBAQ) <= filter_value:
                    filtered_prots.append(prot)
                    mq.remove(prot)
            elif opt == ">":
                print(iBAQ, filter_value, float(iBAQ) > filter_value)
                if not float(iBAQ) > filter_value:
                    filtered_prots.append(prot)
                    mq.remove(prot)
            elif opt == ">=":
                if not float(iBAQ) >= filter_value:
                    filtered_prots.append(prot)
                    mq.remove(prot)
            else:
                if not float(iBAQ) == filter_value:
                    filtered_prots.append(prot)
                    mq.remove(prot)
        #else:
            #mq[mq.index(prot)][column] == "N/A"
    return mq, filtered_prots #output, trash_file 

if __name__ == "__main__":
    options()