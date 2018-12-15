#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 14:55:23 2018

de-id-date.py is for finding phi date 
input is a text file including medical notes
Command for running the code: python de-id-date.py id.text date.phi
results will be saved in date.phi
command for checking code performance: python stats.py id.deid id-phi.phrase date.phi 


This code is modified by Nasim Katebi(nkatebi@emory.edu)
"""

import re
import sys
############## Check for Date ################
# Date patterns (a/b/c or a-b-c or a/b or a-b)
date_pattern='(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(\d{1,2}[-/]\d{1,2})'
# compiling the reg_ex would save sime time!
ph_reg = re.compile(date_pattern)
def check_for_date(patient,note,chunk, output_handle):
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
        Search the entire chunk for date occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # There are some words which are followed by set of numbers similar to date patterns (example: rr 10-20)
    #by detecting these indecators we can remove unwanted values.
    med_exp=['PA','PAP','resp','LS','rr','RR','drop','PAD','HR']
    # In some cases the pattren is not date and it is number of occurence (ex: 2-3 times)
    time_words=['times','minutes','hours']
    for match in ph_reg.finditer(chunk):

        #print(patient, note,end=' ')
      
        # previous part of the date pattern to check if it is a value of med_exp or not 
        # we can also use index of word too find previous and next word.
        #previous_part=chunk[match.start()-5:match.end()-6]
        #list_of_words = chunk.split()
        #previous_part = list_of_words[list_of_words.index(match.group())-1]

        result=""
        flag=0
        for i in range(len(med_exp)):
        # previous part of the date pattern to check if it is a value of med_exp or not 
        # we can also use index of word too find previous and next word.
        
            previous_part=chunk[match.start()-len(med_exp[i])-2:match.start()]

            if med_exp[i] in previous_part:
                flag=1
        for i in range(len(time_words)):
            # next part of the date pattern to  check if it includes time words or not.

            next_part=chunk[match.end():match.end()+len(time_words[i])+1]

            if time_words[i] in next_part:
                flag=1
        if flag==0: # after checking previous and next part of the pattern we can save it as a date
            result=str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            #print(match.group())
        
            # write the result to one line of output
            output_handle.write(result+'\n')
#






def deid_phi(text_path= 'id.text', output_path = 'date.phi'):
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
                    check_for_date(patient,note,chunk.strip(), output_file)
                    #check_for_age(patient,note,chunk.strip(), output_file)
                    #check_for_location(patient,note,chunk.strip(), output_file)

                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_phi(sys.argv[1], sys.argv[2])
    