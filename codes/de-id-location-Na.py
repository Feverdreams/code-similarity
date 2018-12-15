#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 15:08:03 2018
de-id-location.py code is for finding phi location
input is a text file including medical notes
Command for running the code: python de-id-location.py id.text location.phi
results will be saved in location.phi
command for checking code performance: python stats.py id.deid id-phi.phrase location.phi 


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

####################################### check for location ##################
def check_for_location(patient,note,chunk, output_handle):
    #text files including location names in "lists" folder will be saved in list data structure  
    offset=27
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))
    #print(patient, note,end=' ')
    with open('../lists/stripped_hospitals.txt','r') as text:
        location=[]
        for line in text:
            location.append(line)
    with open('../lists/local_places_ambig.txt','r') as text:
        for line in text:
            location.append(line)
    with open('../lists/local_places_unambig.txt','r') as text:
        for line in text:
            location.append(line)
    ## we need to check the location indicators to make the results better
    location_indicators = ("lives in", "resident of", "lived in", "lives at", "comes from", "called from", "visited from", "arrived from", "returned to");
    employment_indicators_pre = ("employee of", "employed by", "employed at", "CEO of", "manager at", "manager for", "manager of", "works at", "business");       
    # Hospital indicators that follow hospital names
    hospital_indicators = ("Hospital", "General Hospital", "Gen Hospital", "gen hosp", "hosp", "Medical Center", "Med Center", "Med Ctr", "Rehab", "Clinic", "Rehabilitation", "Campus", "health center", "cancer center", "development center", "community health center", "health and rehabilitation", "Medical", "transferred to", "transferred from", "transfered to", "transfered from");
    # Location indicators that follow locations
    loc_indicators_suff = ("city", "town", "beach", "valley","county", "harbor", "ville", "creek", "springs", "mountain", "island", "lake", "lakes", "shore", "garden", "haven", "village", "grove", "hills", "hill", "shire", "cove", "coast", "alley", "street", "terrace", "boulevard", "parkway", "highway", "university", "college", "tower");
    # Location indicators that are most likely preceded by locations
    loc_ind_suff_c = ("town", "ville", "harbor", "tower");
    # Location indicators that precede locations
    loc_indicators_pre = ("cape", "fort", "lake", "mount", "santa", "los", "east","west","north","south");
    apt_indicators = ("apt", "suite"); #only check these after the street address is found
    street_add_suff = ("park", "drive", "street", "road", "lane", "boulevard", "blvd", "avenue", "highway", "circle","ave", "place", "rd", "st");
    #Strict street address suffix: case-sensitive match on the following, 
    #and will be marked as PHI regardless of ambiguity (common words)
    #strict_street_add_suff = ("Park", "Drive", "Street", "Road", "Lane", "Boulevard", "Blvd", "Avenue", "Highway","Ave",,"Rd", "PARK", "DRIVE", "STREET", "ROAD", "LANE", "BOULEVARD", "BLVD", "AVENUE", "HIGHWAY","AVE", "RD")
    #print(patient, note,end=' ')
    
    
    # check if patiant note includes any location names
    for i in range(len(location)):
        for match in re.finditer(''+location[i][:-1]+'',chunk):
            result=str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            output_handle.write(result+'\n')
            

            

#    for i in range(len(hospital_indicators)):
#        flag=0
#        for match in re.finditer(hospital_indicators[i],chunk):
#            flag=0
#            previous_word = list_of_words[list_of_words.index(hospital_indicators[i])-1]
#            if previous_word in location:
#                flag=0
#            else:
#                flag=1
#        if flag==1:
#            start=match.start()-(len(previous_word)+1)
#            end=match.start()-1
#            result=str(start-offset) + ' ' + str(start) +' '+ str(end-offset) 
#            output_handle.write(result+'\n')
#            print(previous_word)

            
        

            
        
    
    
    ###############################################################################33       










def deid_phi(text_path= 'id.text', output_path = 'location.phi'):
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
                    #check_for_age(patient,note,chunk.strip(), output_file)
                    check_for_location(patient,note,chunk.strip(), output_file)

                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_phi(sys.argv[1], sys.argv[2])
    