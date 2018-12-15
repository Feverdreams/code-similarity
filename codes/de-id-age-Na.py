#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 15:02:53 2018
de-id-age.py is for finding phi age 
input is a text file including medical notes
Command for running the code:python de-id-age.py id.text age.phi
results will be saved in age.phi
command for checking code performance: python stats.py id.deid id-phi.phrase age.phi 


This code is modified by Nasim Katebi(nkatebi@emory.edu)
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 18:03:37 2018

@author: nkatebi
"""
import re
import sys

###################################check for age#########################################
def check_for_age(patient,note,chunk, output_handle):
    # phi Ages are above 90 so first we can find the numbers in this range 
    # then we should look for the indicators of age before and after that number.
    offset=27
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    age_pattern='(\s\d{2,3})'
    age_reg = re.compile(age_pattern)
    # Age indicators that follow ages(last one is added based on a sample note)
    age_indicators_suff = ("year old", "y\. o\.", "y\.o\.", " yo ", " y ", "years old", "year-old", "-year-old", "years-old", "-years-old", "years of age", "yrs of age","s/p")

    # Age indicators that precede ages
    age_indicators_pre = ("age", "he is", "she is", "patient is")
    for match in age_reg.finditer(chunk):
    #print(patient, note,end=' ')

        flag=0
        if 90<=int(match.group())<=125:
            for i in range(len(age_indicators_suff)):
                if age_indicators_suff[i] in chunk[match.end():match.end()+len(age_indicators_suff[i])+2]:
                    flag=1
            for i in range(len(age_indicators_pre)):
                if age_indicators_pre[i] in chunk[match.start()-(len(age_indicators_pre[i])+2):match.start()]:
                    flag=1
            

            if flag==1: # after checking previous and next part of the pattern we can save it as an age
                result=str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
                #print(match.group())
        
                # write the result to one line of output
                output_handle.write(result+'\n')      
        
        
  
    ####################################################################################          







def deid_phi(text_path= 'id.text', output_path = 'age.phi'):
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
                   # print(chunk.strip())
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    #check_for_date(patient,note,chunk.strip(), output_file)
                    check_for_age(patient,note,chunk.strip(), output_file)
                    #check_for_location(patient,note,chunk.strip(), output_file)

                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_phi(sys.argv[1], sys.argv[2])
    