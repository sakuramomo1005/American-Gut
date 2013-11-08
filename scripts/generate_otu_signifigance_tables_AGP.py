#!/usr/bin/env python

from argparse import ArgumentParser
from os import mkdir
from numpy import array, delete
from biom.parse import parse_biom_table
from os.path import isfile, exists, join as pjoin
from americangut.generate_otu_signifigance_tables import (calculate_abundance,
                                                          calculate_tax_rank_1,
									                      convert_taxa,
									                      convert_taxa_to_list,
									                      generate_latex_macro)
from americangut.taxtree import build_tree_from_taxontable, sample_rare_unique

<<<<<<< HEAD
def main(taxa, table, sample_ids, output_dir, samples_to_analyze = None):
=======

def main(taxa_table, output_dir, samples_to_analyze = None):
>>>>>>> otu_table_improvements
    """Creates LaTeX formatted significant OTU lists

    INPUTS:
        taxa -- a numpy vector with greengenes taxonomy strings

        tax_table -- a numpy array with the relative frequencies of taxonomies
            (rows) for each give sample (column)

        samples_to_analyze -- a numpy vector of sample ids associated with the 
            tax_table values

        output_dir -- a directory where the final files should be saved.

        samples_to_analyze -- a list of samples_to_analyze which should be used 
                    to generate data. If this is left empty, all the samples in 
                    the table will be used.

    OUTPUTS:
        Generates text files containing LaTex encoded strings which creates a 
        LaTeX macro dictionary with the information for creating a table of most
        abundant taxa, most enriched taxa, and rare and unique taxa. Rare 
        defined as present in less than 10% of the total population. The unique 
        taxa are bolded in the lists. 
    """
    # Sets table constants
    RARE_THRESHHOLD = 0.1
    RENDERING = "LATEX"
    FORMAT_SIGNIFIGANCE = ["VAL_100", "VAL_100", "VAL_INT", "SKIP"]
    FORMAT_ABUNDANCE = ["VAL_100"]    
    MACRO_CATS_SIGNIFICANCE = ['enrichTaxon','enrichSampl', 'enrichPopul', 
        'enrichFoldd']
    MACRO_CATS_ABUNDANCE = ['abundTaxon', 'abundSampl']

    FILE_PRECURSER = 'macros_'
    FILE_EXTENSION = '.tex'

    # Number of taxa shown is an indexing value, it is one less than what is 
    # actually shown.
    NUMBER_OF_TAXA_SHOWN = 5

    # Builds the the taxomnomy tree for the table and identifies the 
    # rare/unique taxa in each sample
    tree, all_taxa = build_tree_from_taxontable(taxa_table)

    # Sets up samples for which tables are being generated    
    if not samples_to_analyze == None:
        samples_to_test = samples_to_analyze
    else:
        samples_to_test = all_taxa.keys()

    if samples_to_test:
        samples_to_test = set(samples_to_test)
        tmp = {k:v for k,v in all_taxa.items() if k in samples_to_test}
        all_taxa = tmp
        if not samples_to_test:
            raise ValueError, "No samples!"

    for samp, filtered_table, rare, unique in sample_rare_unique(tree, \
        taxa_table, all_taxa, RARE_THRESHHOLD):
        filtered_table = filtered_table.filterObservations(lambda v,i,md:\
        v.sum() > 0)

        # Gets sample information for other samples
        taxa = filtered_table.ObservationIds       
        population = array([filtered_table.observationData(i) for i in \
            filtered_table.ObservationIds])
        
        sample_position = filtered_table.getSampleIndex(samp)
        sample = filtered_table.sampleData(samp)
        print samp, sum(sample > 0)
                
        population = delete(population, sample_position, 1)
        
        # Converts the lists into greengenes strings for later processing
        greengenes_rare = []
        greengenes_unique = []
        for taxon in rare:
            greengenes_rare.append('; '.join(taxon))
        for taxon in unique:
            greengenes_unique.append('; '.join(taxon))

        # Formats the rare and unique lists          
        rare_format = []
        rare_combined = []
        for taxon in greengenes_unique:
            rare_combined.append(taxon)
            rare_format.append('COLOR')
        for taxon in greengenes_rare:
            rare_combined.append(taxon)
            rare_format.append('REG')

        number_rare_tax = len(rare_combined)

        if number_rare_tax > NUMBER_OF_TAXA_SHOWN + 1 and len(unique) == 0:
            rare_formatted = ["Your sample contained %i rare "\
            "taxa, including the following: " % number_rare_tax]
            rare_formatted.append(convert_taxa_to_list(\
                rare_combined[:NUMBER_OF_TAXA_SHOWN ], 
                tax_format = rare_format,
                render_mode = RENDERING, 
                comma = True))
            rare_formatted = ''.join(rare_formatted)              

        elif number_rare_tax > NUMBER_OF_TAXA_SHOWN + 1:
            rare_formatted = ["This sample contained %i rare and " \
                 "\\textcolor{red}{%i unique} taxa, including "\
                 "the following: " % (len(rare), len(unique))]
            rare_formatted.append(convert_taxa_to_list(\
                rare_combined[:NUMBER_OF_TAXA_SHOWN ], 
                tax_format = rare_format,
                render_mode = RENDERING, 
                comma = True))
            rare_formatted = ''.join(rare_formatted)

        elif number_rare_tax > 0 and len(unique) == 0:
            rare_formatted = ['This sample included the follow rare taxa: ']
            rare_formatted.append(convert_taxa_to_list(rare_combined, 
                                                tax_format = rare_format,
                                                render_mode = RENDERING, 
                                                comma = True))
            rare_formatted = ''.join(rare_formatted)

        elif number_rare_tax > 0 and len(unique) > 0:
            rare_formatted = ['This sample included the follow rare or'
            ' \\textcolor{red}{unique} taxa: ']
            rare_formatted.append(convert_taxa_to_list(rare_combined, 
                                                tax_format = rare_format,
                                                render_mode = RENDERING, 
                                                comma = True))
            rare_formatted = ''.join(rare_formatted)
    
        else:
            rare_formatted = "There were no rare or unique taxa found"\
                         " in this sample."

        # Calculates abundance rank
        (abundance) = calculate_abundance(sample, taxa)

        (low, high) = calculate_tax_rank_1(sample = sample, 
                                           population = population, 
                                           taxa = taxa)

        #print high
        # Generates formatted enriched table
        formatted_high = convert_taxa(high[0:NUMBER_OF_TAXA_SHOWN],
                                      render_mode = RENDERING, 
                                      formatting_keys = FORMAT_SIGNIFIGANCE)
        #print formatted_high 

        high_formatted = generate_latex_macro(formatted_high, \
            categories = MACRO_CATS_SIGNIFICANCE)

        # Generates formatted abundance table
        formatted_abundance = convert_taxa(abundance[0:NUMBER_OF_TAXA_SHOWN],
                                        render_mode = RENDERING,
                                        formatting_keys = FORMAT_ABUNDANCE)
        abundance_formatted = generate_latex_macro(formatted_abundance, \
            categories = MACRO_CATS_ABUNDANCE)
    


        # Saves the file
        file_name = pjoin(output_dir, '%s%s%s' % (FILE_PRECURSER, samp, 
            FILE_EXTENSION))

<<<<<<< HEAD
            # Generates formatted abundance table
            formatted_abundance = convert_taxa(abundance[0:NUMBER_OF_TAXA_SHOWN],
                                            render_mode = RENDERING,
                                            formatting_keys = FORMAT_ABUNDANCE)
            abundance_formatted = generate_latex_macro(formatted_abundance, \
                categories = MACRO_CATS_ABUNDANCE)
        
            # Generates formatted list
            rare_format = []
            rare_combined = []
            for taxon in unique:
                rare_combined.append(taxon)
                rare_format.append('COLOR')
            for taxon in rare:
                rare_combined.append(taxon)
                rare_format.append('REG')

            number_rare_tax = len(rare_combined)

            if number_rare_tax > NUMBER_OF_TAXA_SHOWN + 1 and len(unique) == 0:
                rare_formatted = ["Your sample contained %i rare "\
                "taxa, including the following: " % number_rare_tax]
                rare_formatted.append(convert_taxa_to_list(\
                    rare_combined[:NUMBER_OF_TAXA_SHOWN ], 
                    tax_format = rare_format,
                    render_mode = RENDERING, 
                    comma = True))
                rare_formatted = ''.join(rare_formatted)                

            elif number_rare_tax > NUMBER_OF_TAXA_SHOWN + 1:
                rare_formatted = ["This sample contained %i rare and " \
                     "\\textcolor{red}{%i unique} taxa, including "\
                     "the following: " % (len(rare), len(unique))]
                rare_formatted.append(convert_taxa_to_list(\
                    rare_combined[:NUMBER_OF_TAXA_SHOWN ], 
                    tax_format = rare_format,
                    render_mode = RENDERING, 
                    comma = True))
                rare_formatted = ''.join(rare_formatted)

            elif number_rare_tax > 0 and len(unique) == 0:
                rare_formatted = ['This sample included the following rare taxa: ']
                rare_formatted.append(convert_taxa_to_list(rare_combined, 
                                                    tax_format = rare_format,
                                                    render_mode = RENDERING, 
                                                    comma = True))
                rare_formatted = ''.join(rare_formatted)
    
            elif number_rare_tax > 0 and len(unique) > 0:
                rare_formatted = ['This sample included the following rare or'
                ' \\textcolor{red}{unique} taxa: ']
                rare_formatted.append(convert_taxa_to_list(rare_combined, 
                                                    tax_format = rare_format,
                                                    render_mode = RENDERING, 
                                                    comma = True))
                rare_formatted = ''.join(rare_formatted)
            
            else:
                rare_formatted = "There were no rare or unique taxa found"\
                             " in this sample."

            # Saves the file
            file_name = pjoin(output_dir, '%s%s%s' % (FILE_PRECURSER, sample_id, 
                FILE_EXTENSION))

            file_for_editing = open(file_name, 'w')
            # file_for_editing.write('% Participant Name\n\\def\\yourname'\
            #     '{Michael Pollan or longer name}\n\n')
            file_for_editing.write('%% Abundance Table\n%s\n\n\n' \
                % abundance_formatted)
            file_for_editing.write('%% Enrichment Table\n%s\n\n\n' \
                % high_formatted)
            file_for_editing.write('%% Rare List\n\\def\\rareList{%s}\n' \
                % rare_formatted)
            file_for_editing.close()
=======
        file_for_editing = open(file_name, 'w')
        # file_for_editing.write('% Participant Name\n\\def\\yourname'\
        #     '{Michael Pollan or longer name}\n\n')
        file_for_editing.write('%% Abundance Table\n%s\n\n\n' \
            % abundance_formatted)
        file_for_editing.write('%% Enrichment Table\n%s\n\n\n' \
            % high_formatted)
        file_for_editing.write('%% Rare List\n\\def\\rareList{%s}\n' \
            % rare_formatted)
        file_for_editing.close()
>>>>>>> otu_table_improvements

# Sets up command line parsing
parser = ArgumentParser(description = "Creates lists and tables of enriched, abundance and rare taxa")

parser.add_argument('-i', '--input', help = 'Path to taxonomy table [REQUIRED]')
parser.add_argument('-o', '--output', \
                    help = 'Path to the output directory [REQUIRED]')
parser.add_argument('-s', '--samples', default = None, \
                    help = 'Sample IDs to be analyzed. If no value is '\
                    'specified, all samples in the taxonomy file will be'\
                    ' analyzed.')

if __name__ == '__main__':

    args = parser.parse_args()

    # Checks the tax table file path is sane and loads it.
    if not args.input:
        parser.error('An input taxonomy table is required')
    elif not isfile(args.input):
        parser.error("The supplied taxonomy file does not exist in the path.")        
    else:
        tax_table = parse_biom_table(open(args.input))

    # Checks the output directory is sane.
    if not args.output:
        parser.error('An output directory must be supplied.')
    elif not exists(args.output):
        mkdir(args.output)        

    output_dir = args.output
    

    # Parses the sample IDs as a list
    if args.samples:
        samples_to_analyze = []
        for sample in args.samples.split(','): 
            samples_to_analyze.append(sample)
    else:
        samples_to_analyze = None

    main(taxa_table = tax_table, output_dir = output_dir, \
        samples_to_analyze = samples_to_analyze)
