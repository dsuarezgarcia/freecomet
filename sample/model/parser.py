# -*- encoding: utf-8 -*-

'''
    The parser module.
'''

# General imports
import statistics
import ntpath
import pickle
import numpy
import xlwt
import os

# Custom imports
from sample.model.canvas_model import CanvasModel
import sample.model.utils as utils
import sample.model.constants as constants
 

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #
#                                                                             #
# 	Parser                                                                    #
#                                                                             #
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ #

class Parser(object):

    '''
        The Parser static class.
    '''

    FILE_EXTENSION = ".xls"
    OUTPUT_STR = "_out"

    ''' Write data in given path. '''
    def write(data, path):

        out_file = open(path, 'wb') 
        pickle.dump(data, out_file)
        out_file.close()

    ''' Read data from given path. '''
    def read(path):
    
        in_file = open(path, 'rb')      
        data = pickle.load(in_file)
        in_file.close()
        return data

    ''' Generates the output of current project. '''
    def generate_output(sample_list, path):
        
        # Create spreadsheet
        workbook = Parser.generate_spreadsheet(sample_list)
        # Create dir folder
        (final_path, dir_name) = Parser.create_dir(path)

        # Save spreadsheet file on output dir
        workbook.save(os.path.join(final_path, dir_name+Parser.FILE_EXTENSION))
        # Save segmented images on output dir
        Parser.save_segmented_images(sample_list, final_path)

    ''' Saves the segmented images on given path. '''
    def save_segmented_images(sample_list, path):

        # Numpy wants BGR and not RGB
        tail_color = (
            CanvasModel.get_instance().get_tail_color().blue * constants.MAX_VALUE,          
            CanvasModel.get_instance().get_tail_color().green * constants.MAX_VALUE,
            CanvasModel.get_instance().get_tail_color().red * constants.MAX_VALUE           
        )
                     
        head_color = (
            CanvasModel.get_instance().get_head_color().blue * constants.MAX_VALUE,
            CanvasModel.get_instance().get_head_color().green * constants.MAX_VALUE,           
            CanvasModel.get_instance().get_head_color().red * constants.MAX_VALUE
        )

        for sample in sample_list:
        
            image_copy = numpy.copy(sample.get_image())
            n = 1
            for comet in sample.get_comet_list():
            
                if comet.get_tail_contour() is not None:
                    utils.draw_contours(image_copy, [comet.get_tail_contour()],
                        tail_color, 1)
                utils.draw_contours(image_copy, [comet.get_head_contour()],
                    head_color, 1)
                    
                n += 1

            utils.save_image(image_copy, os.path.join(
                path, Parser.get_image_output_name(sample.get_name())))

    ''' Creates a directory to save the output. '''
    def create_dir(path):
        
        original_dir_name = ntpath.basename(path)
        dir_name = original_dir_name
        local_path = path[:-len(dir_name)]
            
        n = 1
        created = False
        while not created:
    
            try:
                os.mkdir(local_path + dir_name)
                created = True
                
            except OSError as error:
                dir_name = original_dir_name + "(" + str(n) + ")"
                n += 1
                
                
        return (local_path+dir_name, dir_name)

    ''' Creates a spreadsheet with the model statistics. '''
    def generate_spreadsheet(sample_list):

        # Workbook is created 
        workbook = xlwt.Workbook()  
        # add_sheet is used to create the spreadsheet. 
        sheet = workbook.add_sheet('Sheet')

        # Columns creation 
        style = xlwt.easyxf('font: bold 1') 
        sheet.write(0, 0, "FileName", style)
        sheet.write(0, 1, "CometNumber", style)
        sheet.write(0, 2, "CometArea", style)
        sheet.write(0, 3, "CometIntensity", style)
        sheet.write(0, 4, "CometLength", style)
        sheet.write(0, 5, "CometDNA", style)
        sheet.write(0, 6, "HeadArea", style)
        sheet.write(0, 7, "HeadIntensity", style)
        sheet.write(0, 8, "HeadLength", style)
        sheet.write(0, 9, "HeadDNA", style)
        sheet.write(0, 10, "HeadDNA%", style)
        sheet.write(0, 11, "TailArea", style)
        sheet.write(0, 12, "TailIntensity", style)
        sheet.write(0, 13, "TailLength", style)
        sheet.write(0, 14, "TailDNA", style)
        sheet.write(0, 15, "TailDNA%", style)
        sheet.write(0, 16, "TailMoment", style)
        sheet.write(0, 17, "OliveMoment", style)
         
        # Parameters list
        comet_area_list = []
        comet_average_intensity_list = []
        comet_length_list = []
        comet_dna_content_list = []
        head_area_list = []
        head_average_intensity_list = []
        head_length_list = []
        head_dna_content_list = []
        head_dna_percentage_list = []
        tail_area_list = []
        tail_average_intensity_list = []
        tail_length_list = []
        tail_dna_content_list = []
        tail_dna_percentage_list = []
        tail_moment_list = []
        olive_moment_list = []

        parameters_list = [comet_area_list, comet_average_intensity_list, comet_length_list,
                comet_dna_content_list, head_area_list, head_average_intensity_list,
                head_length_list, head_dna_content_list, head_dna_percentage_list,
                tail_area_list, tail_average_intensity_list, tail_length_list,
                tail_dna_content_list, tail_dna_percentage_list, tail_moment_list,
                olive_moment_list]
        

        # Sample statistics
        row = 1
        for sample in sample_list:
        
        
            sample_output_name = Parser.get_image_output_name(sample.get_name())
            comet_number = 1                
            for comet in sample.get_comet_list():

                parameters = comet.get_parameters()

                sheet.write(row, 0, sample_output_name)
                sheet.write(row, 1, comet_number)
                sheet.write(row, 2, parameters.get_comet_area())
                comet_area_list.append(parameters.get_comet_area())
                sheet.write(row, 3, parameters.get_comet_average_intensity())
                comet_average_intensity_list.append(parameters.get_comet_average_intensity())
                sheet.write(row, 4, parameters.get_comet_length())
                comet_length_list.append(parameters.get_comet_length())
                sheet.write(row, 5, parameters.get_comet_dna_content())
                comet_dna_content_list.append(parameters.get_comet_dna_content())
                sheet.write(row, 6, parameters.get_head_area())
                head_area_list.append(parameters.get_head_area())
                sheet.write(row, 7, parameters.get_head_average_intensity())
                head_average_intensity_list.append(parameters.get_head_average_intensity())
                sheet.write(row, 8, parameters.get_head_length())
                head_length_list.append(parameters.get_head_length())
                sheet.write(row, 9, parameters.get_head_dna_content())
                head_dna_content_list.append(parameters.get_head_dna_content())
                sheet.write(row, 10, parameters.get_head_dna_percentage()*100)
                head_dna_percentage_list.append(parameters.get_head_dna_percentage())
                sheet.write(row, 11, parameters.get_tail_area())
                tail_area_list.append(parameters.get_tail_area())
                sheet.write(row, 12, parameters.get_tail_average_intensity())
                tail_average_intensity_list.append(parameters.get_tail_average_intensity())
                sheet.write(row, 13, parameters.get_tail_length())
                tail_length_list.append(parameters.get_tail_length())
                sheet.write(row, 14, parameters.get_tail_dna_content())
                tail_dna_content_list.append(parameters.get_tail_dna_content())
                sheet.write(row, 15, parameters.get_tail_dna_percentage()*100)
                tail_dna_percentage_list.append(parameters.get_tail_dna_percentage())
                sheet.write(row, 16, parameters.get_tail_moment())
                tail_moment_list.append(parameters.get_tail_moment())
                sheet.write(row, 17, parameters.get_olive_moment())
                olive_moment_list.append(parameters.get_olive_moment())
                comet_number += 1
                row += 1

        row += 1

        if len(parameters_list[0]) > 0:

            # Population statistics
            sheet.write(row, 0, "Population statistics", style)       
            row += 1
            Parser.write_statistics(sheet, row, statistics.mean, "Mean", parameters_list)
            row += 1
            Parser.write_statistics(sheet, row, statistics.median, "Median", parameters_list)
            row += 1
            Parser.write_statistics(sheet, row, statistics.stdev, "Stddev", parameters_list)
            row += 1
            Parser.write_statistics(sheet, row, min, "Min", parameters_list)
            row += 1
            Parser.write_statistics(sheet, row, max, "Max", parameters_list)
            
        return workbook    
       
    ''' Writes the statistics from given function. '''
    def write_statistics(sheet, row, fun, fun_name, list): 

        sheet.write(row, 0, fun_name)
        sheet.write(row, 2, fun(list[0]))    
        sheet.write(row, 3, fun(list[1]))
        sheet.write(row, 4, fun(list[2]))
        sheet.write(row, 5, fun(list[3]))
        sheet.write(row, 6, fun(list[4]))
        sheet.write(row, 7, fun(list[5]))
        sheet.write(row, 8, fun(list[6]))
        sheet.write(row, 9, fun(list[7]))
        sheet.write(row, 10, fun(list[8]))
        sheet.write(row, 11, fun(list[9]))
        sheet.write(row, 12, fun(list[10]))
        sheet.write(row, 13, fun(list[11])) 
        sheet.write(row, 14, fun(list[12])) 
        sheet.write(row, 15, fun(list[13])) 
        sheet.write(row, 16, fun(list[14])) 
        sheet.write(row, 17, fun(list[15]))
    
    ''' Returns the output name of an image. '''
    def get_image_output_name(image_name): 
        name, extension = os.path.splitext(image_name)
        return (name + Parser.OUTPUT_STR + extension)
    
    
