# -*- coding: utf-8 -*-
'''
This code tries to find "Age" PHI:
To run the code run the command : python deid.py id.text age.phi
It read the file id.text to find the date type phi in the text.
It provides the output file: age.phi
To run the stats.py, run the command: python stats.py id.deid id-phi.phrase age.phi

This code is modified by Parisa Sarikhani as a part of homework for BMI500 course,
lecture 9.

'''

import re
import sys


# compiling the reg_ex would save sime time!]

# Age indicators that follow ages
age_indicators_suff = ["year old", "y\. o\.", "y\.o\.", "yo", "y", "years old", "year-old", "-year-old", "years-old", "-years-old", "years of age", "yrs of age", "s/p"];

# Age indicators that precede ages
age_indicators_pre = ["age", "he is", "she is", "patient is"];

#Regular expression for age: we are interested in 89< age < 125 (2 or 3 digits)
#regualr expression to find any pattern a space, followed by a 2 or 3 digit number, followed by a whitespace or . or ,
age_pattern='[\s]\d{2,3}[\s,.]' 
age_reg = re.compile(age_pattern)



def check_for_age(patient,note,chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function. 
    Logic:
        Search the entire chunk for phone number occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find phones.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 25+len(patient)+len(note)

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in age_reg.finditer(chunk):
        #Check if the found digit is in the range 89<age<125
        if int(match.group()[:-1])<125 and int(match.group()[:-1])>89:
            #Check the prefixe : if one of the defined suffixes exists after the nominated digit yhen the digit is a PHI 
            for suff in age_indicators_suff:
                for i in re.finditer(match.group()[1:-1]+' '+suff+' ',chunk):#match.group()[1:-1] ignores the space before age and after age
                    if i.start()==match.start()+1:
                        # debug print, 'end=" "' stops print() from adding a new line
                        print(patient, note,end=' ')
                        print((match.start()+1-offset),match.end()-1-offset, match.group())

                        # create the string that we want to write to file ('start start end')    
                        result = str(match.start()+1-offset) + ' ' + str(match.start()+1-offset) +' '+ str(match.end()-1-offset) 
            
                        # write the result to one line of output
                        output_handle.write(result+'\n')
                        
            #Check the prefixe : if one of the defined prefixes exists before the nominated digit yhen the digit is a PHI            
            for pref in age_indicators_suff:
                for i in re.finditer(pref+match.group()[1:-1],chunk):#match.group()[1:-1] ignores the space before age and after age
                    if i.end()==match.end()-1:
                        # debug print, 'end=" "' stops print() from adding a new line
                        print(patient, note,end=' ')
                        print((match.start()+1-offset),match.end()-1-offset, match.group())

                        # create the string that we want to write to file ('start start end')    
                        result = str(match.start()+1-offset) + ' ' + str(match.start()+1-offset) +' '+ str(match.end()-1-offset) 
            
                        # write the result to one line of output
                        output_handle.write(result+'\n')
                        
            
    

        
        
        
        
        
        
        
        
        
        
            
def deid_age(text_path= 'id.text', output_path = 'age.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each phone number found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected phone number string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no phone number detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each phone number detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end phone_number
        where `start` is the start position of the detected phone number string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    
    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # open the output file just once to save time on the time intensive IO
    with open(output_path,'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_age(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_age(sys.argv[1], sys.argv[2])
    