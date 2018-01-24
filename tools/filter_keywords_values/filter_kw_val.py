import argparse
import re


def options():
    """
    Parse options
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", required=True)
    parser.add_argument("-m", "--match", help="Exact macth")
    parser.add_argument("--kw", nargs="+", action="append", help="") #
    parser.add_argument("--kw_file", nargs="+", action="append", help="")
    parser.add_argument("--value", nargs="+", action="append", help="")
    parser.add_argument("-o", "--output", default="output.txt")
    parser.add_argument("--trash_file", default="trash_MQfilter.txt")

    args = parser.parse_args()

    filters(args)

    # python filter2.py -i "/projet/galaxydev/galaxy/tools/proteore_uc1/proteinGroups_Maud.txt"
    # --protein_IDs "A2A288:A8K2U0" --peptides 2 "=" -o "test-data/output_MQfilter.txt"


def isnumber(number_format, n):
    """
    Check if a variable is a float or an integer
    """
    float_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")
    int_format = re.compile("^[\-]?[1-9][0-9]*$")
    test = ""
    if number_format == "int":
        test = re.match(int_format, n)
    elif number_format == "float":
        test = re.match(float_format, n)
    if test:
        return True
#    else:
#        return False

def filters(args):
    """
    Filter the document
    """
    MQfilename = args.input.split(",")[0]
    header = args.input.split(",")[1]
    MQfile = readMQ(MQfilename)
    results = [MQfile, None]

    if args.kw:
        keywords = args.kw
        for k in keywords:
            results = filter_keyword(results[0], header, results[1], k[0], k[1], k[2])
    if args.kw_file:
        key_files = args.kw_file
        for kf in key_files:
            ids = readOption(kf[0])
            results = filter_keyword(results[0], header, results[1], ids, kf[1], kf[2])
    if args.value:
        for v in args.value:
            if isnumber("float", v[0]):
                results = filter_value(results[0], header, results[1], v[0], v[1], v[2])
            else:
                raise ValueError("Please enter a number in filter by value")

    # Write results to output
    output = open(args.output, "w")
    output.write("\n".join(results[0]))
    output.close()

    # Write deleted lines to trash_file
    trash = open(args.trash_file, "w")
    trash.write("\n".join(results[1]))
    trash.close()

def readOption(filename):
    f = open(filename, "r")
    file_content = f.read()
    filter_list = file_content.split("\n")
    filters = ""
    for i in filter_list:
        filters += i + ";"
    filters = filters[:-1]
    return filters

def readMQ(MQfilename):
    # Read MQ file
    mqfile = open(MQfilename, "r")
    mq = mqfile.readlines()
    # Remove empty lines (contain only space or new line or "")
    [mq.remove(blank) for blank in mq if blank.isspace() or blank == ""]
    return mq

def filter_keyword(MQfile, header, filtered_lines, ids, ncol, match):
    mq = MQfile
    if isnumber("int", ncol.replace("c", "")):
        id_index = int(ncol.replace("c", "")) - 1 #columns.index("Majority protein IDs")
    else:
        raise ValueError("Please specify the column where "
                         "you would like to apply the filter "
                         "with valid format")

    # Split list of filter IDs
    ids = ids.upper().split(";")
    # Remove blank IDs
    [ids.remove(blank) for blank in ids if blank.isspace() or blank == ""]
    # Remove space from 2 heads of IDs
    ids = [id.strip() for id in ids]


    if header == "true":
        header = mq[0]
        content = mq[1:]
    else:
        header = ""
        content = mq[:]

    if not filtered_lines: # In case there is already some filtered lines from other filters
        filtered_lines = []
        if header != "":
            filtered_lines.append(header)

    for line in content:
        line = line.replace("\n", "")
        id_inline = line.split("\t")[id_index].replace('"', "").split(";")
        one_id_line = line.replace(line.split("\t")[id_index], id_inline[0]) # Take only first IDs
        line = line + "\n"

        if match != "false":
            # Filter protein IDs
            if any(pid.upper() in ids for pid in id_inline):
                filtered_lines.append(one_id_line)
                mq.remove(line)
            else:
                mq[mq.index(line)] = one_id_line
        else:
            if any(ft in pid.upper() for pid in id_inline for ft in ids):
                filtered_lines.append(one_id_line)
                mq.remove(line)
            else:
                mq[mq.index(line)] = one_id_line
    return mq, filtered_lines

def filter_value(MQfile, header, filtered_prots, filter_value, ncol, opt):
    mq = MQfile
    if ncol and isnumber("int", ncol.replace("c", "")): #"Gene names" in columns:
        index = int(ncol.replace("c", "")) - 1 #columns.index("Gene names")
    else:
        raise ValueError("Please specify the column where "
                         "you would like to apply the filter "
                         "with valid format")
    if header == "true":
        header = mq[0]
        content = mq[1:]
    else:
        header = ""
        content = mq[:]
    if not filtered_prots: # In case there is already some filtered lines from other filters
        filtered_prots = []
        if header != "":
            filtered_prots.append(header)

    for line in content:
        prot = line.replace("\n","")
        filter_value = float(filter_value)
        pep = prot.split("\t")[index].replace('"', "")
        if pep.replace(".", "", 1).isdigit():
            if opt == "<":
                if float(pep) >= filter_value:
                    filtered_prots.append(line)
                    mq.remove(line)
            elif opt == "<=":
                if float(pep) > filter_value:
                    filtered_prots.append(line)
                    mq.remove(line)
            elif opt == ">":
            #print(prot.number_of_prots, filter_value, int(prot.number_of_prots) > filter_value)
                if float(pep) <= filter_value:
                    filtered_prots.append(line)
                    mq.remove(line)
            elif opt == ">=":
                if float(pep) < filter_value:
                    filtered_prots.append(line)
                    mq.remove(line)
            else:
                if float(pep) != filter_value:
                    filtered_prots.append(line)
                    mq.remove(line)
    return mq, filtered_prots #output, trash_file

if __name__ == "__main__":
    options()
