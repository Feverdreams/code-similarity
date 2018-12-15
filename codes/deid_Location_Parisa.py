# -*- coding: utf-8 -*-
'''
This code tries to find "Location" PHI:
To run the code run the command : python deid.py id.text location.phi
It read the file id.text to find the date type phi in the text.
It provides the output file: location.phi
To run the stats.py, run the command: python stats.py id.deid id-phi.phrase location.phi

This code is modified by Parisa Sarikhani as a part of homework for BMI500 course,
lecture 9.

'''
import re
import sys



##############################################################################
#open the following lists and dictionaries into a list
#path to dict and lists folders
dic_path='../dict'
list_path='../lists'

#locations_unambig.txt into a list
fo_locations_unambig=open(list_path+'/locations_unambig.txt','r')
locations_unambig_lst=fo_locations_unambig.readlines()
     
#locations_ambig.txt
fo_locations_ambig=open(list_path+'/locations_ambig.txt','r')
locations_ambig_lst=fo_locations_ambig.readlines()    
    
#local_places_unambig.txt: Known PHI
fo_local_places_ambig=open(list_path+'/local_places_ambig.txt','r')
local_places_ambig_lst=fo_local_places_ambig.readlines()    
     
#local_places_unambig.txt: Known PHI
fo_local_places_unambig=open(list_path+'/local_places_unambig.txt','r')
local_places_unambig_lst=fo_local_places_unambig.readlines()    
        
#stripped_hospitals.txt : Known PHI
fo_stripped_hospitals=open(list_path+'/stripped_hospitals.txt','r')
stripped_hospitals_lst=fo_stripped_hospitals.readlines()    
    
#more_us_state_abbreviations.txt
fo_more_us_state_abbreviations=open(list_path+'/more_us_state_abbreviations.txt','r')
more_us_state_abbreviations_lst=fo_more_us_state_abbreviations.readlines()  

#us_states.txt
fo_us_states=open(list_path+'/us_states.txt','r')
us_states_lst=fo_us_states.readlines()        

#us_states_abbre.txt
fo_us_states_abbre=open(list_path+'/us_states_abbre.txt','r')
us_states_abbre_lst=fo_us_states_abbre.readlines()    

##############################################################################
#location suffixes and prefixes:
# Phrases that precede locations
location_indicators = ["lives in", "resident of", "lived in", "lives at", "comes from", "called from", "visited from", "arrived from", "returned to"];

# Location indicators that precede locations
loc_indicators_pre = ["cape", "fort", "lake", "mount", "santa", "los", "east","west","north","south"];





def check_for_location(patient,note,chunk, output_handle):
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
    offset =25+len(patient)+len(note)

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found

    
######################### Known PHI ###########################################
    #If any matches is found, it is a phi:
    for word in local_places_ambig_lst: 
        for m in re.finditer(' '+word[:-1]+' ',chunk):
            print(patient, note,end=' ')
            print(m.start()+1-offset, m.end()-1-offset,m.group())
            # create the string that we want to write to file ('start start end')
            result = str(m.start()+1-offset) + ' ' + str(m.start()+1-offset) +' '+ str(m.end()-1-offset) 
            # write the result to one line of output
            output_handle.write(result+'\n')    
    #If any matches is found, it is a phi:
    for word in local_places_unambig_lst:
        
        for m in re.finditer(' '+word[:-1]+' ',chunk):
            print(patient, note,end=' ')
            print(m.start()+1-offset, m.end()-1-offset,m.group())
            # create the string that we want to write to file ('start start end')
            result = str(m.start()+1-offset) + ' ' + str(m.start()+1-offset) +' '+ str(m.end()-1-offset) 
            # write the result to one line of output
            output_handle.write(result+'\n')
    #If any matches is found, it is a phi:
    for word in stripped_hospitals_lst:
        
        for m in re.finditer(' '+word[:-1]+' ',chunk):
            print(patient, note,end=' ')
            print(m.start()+1-offset, m.end()-1-offset,m.group())
            # create the string that we want to write to file ('start start end')
            result = str(m.start()+1-offset) + ' ' + str(m.start()+1-offset) +' '+ str(m.end()-1-offset) 
            # write the result to one line of output
            output_handle.write(result+'\n')
    
    
    
################## Ambiguous PHI ##############################################
################## Indicator (Prefixes) #######################################
# If any matches found in the following lists, it is an ambiguous phi, then we go through the
# the indicators lists to see if any of the indicators (either prefix or suffix) exists
#If there exist a prefix  before the ambiguous phi, it is considered as phi
#Otehrwise, I ignore it.
    AMB_PHI=[]
    for word in locations_unambig_lst:
        for m in re.finditer(' '+word[:-1]+' ',chunk):
            AMB_PHI.append(m)#creat a list of ambiguous PHIs
            
    for word in locations_ambig_lst:
        for m in re.finditer(' '+word[:-1]+' ',chunk):
            AMB_PHI.append(m)#creat a list of ambiguous PHIs
            
    for indicator in location_indicators:#check gor prefixes in location_indicators
        for amb in AMB_PHI:
            if amb !=[]:
                for i in re.finditer(indicator+amb.group(),chunk):
                    if i.end()==amb.end():
                        print(patient, note,end=' ')
                        print(amb.start()+1-offset-1, amb.end()-1-offset-1,amb.group())
                        # create the string that we want to write to file ('start start end')
                        result = str(amb.start()+1-offset-1) + ' ' + str(amb.start()+1-offset-1) +' '+ str(amb.end()-1-offset-1) 
                        # write the result to one line of output
                        output_handle.write(result+'\n')
    for indicator in loc_indicators_pre:# Check for prefixes in loc_indicators_pre
        for amb in AMB_PHI:
            if amb !=[]:
                for i in re.finditer(indicator+amb.group(),chunk):
                    if i.end()==amb.end():
                        print(patient, note,end=' ')
                        print(amb.start()+1-offset-1, amb.end()-1-offset-1,amb.group())
                        # create the string that we want to write to file ('start start end')
                        result = str(amb.start()+1-offset-1) + ' ' + str(amb.start()+1-offset-1) +' '+ str(amb.end()-1-offset-1) 
                        # write the result to one line of output
                        output_handle.write(result+'\n')

    

            
            
def deid_location(text_path = 'id.text', output_path = 'location.phi'):
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
                    #print(chunk.strip())
                    
                    #print('next')
                    #if patient=='2' and note=='2':
                        #sys.exit()
                    check_for_location(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_location()
    
