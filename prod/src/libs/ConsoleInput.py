import argparse


class ConsoleInput(object):

    def __init__(self):
        parser = argparse.ArgumentParser(add_help=False)
        group = parser.add_argument_group("Options")
        group.add_argument("-h", "--help", action="help", help="To run the tool use -tp path and -tableName \n""Options:\n")
        group.add_argument("-tp", "--testprogram", required=True, help="Add the TP path, Example: -tp <path tp TP>")
        group.add_argument("-table_scoreCard", "--tableName", required=False,default="null", help="Add the desired name for output scorecard Table, Example: -table <tableName>")
        group.add_argument("-die", "--die",required=False,default="null", help="Select die (cdie,iodie,imh,cbb), Example: -die imh")
        group.add_argument("-product", "--product", required=True, help="Select Product (gnr,dmr), Example: -product dmr")
        group.add_argument("-step", "--step",required=True, help="Add the step for the product. Example: -step <>")
        #group.add_argument("-cf", "--config_file", help="File with specific path for mtpl and flows to generate table (either this or tp)")
        #group.add_argument("-patmod", "--patmod", help="Patmod location")
        group.add_argument("-c", "--chop",  required=True, help="Add the chop UCC,XCC,HCC,LCC. Example: -c <chop>")
        group.add_argument("-op", "--operation", required=True, help="Operation (HOT, COLD).Example: -op hot")
        group.add_argument("-s", "--socket", required=True, help="Flow SORT or CLASS, Example: -s sort")
        #group.add_argument("-format", "--format",required=True, help="Audit output txt or excel, Example: -format txt")
        #group.add_argument("-separete", "--separate", action='store_true', help="Differentiates between atpg and tatpg")
        #group.add_argument("-iodie", "--iodie", action='store_true', help="For IOdie")
        #group.add_argument("-fused", "--fused", action="store_true", help="IOdie fused unit, not fused by default.")
        self.args = parser.parse_args()

    def parseArguments(self):
        return self.args


