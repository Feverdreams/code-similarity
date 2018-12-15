import re
import sys
#'(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'
#date_pattern ='(\d{1}[/]\d{2}|\d{2}[/]\d{2}|\d{1}[/]\d{2}[/]\d{2}|\d{2}[/]\d{1}[/]\d{2}|\d{2}[/]\d{2}[/]\d{2})'

"""
-------------------------------------------------------------------------------
VERSION 2.0 - Code edited by Andre Holder.
Changes made to original code: 
    (1) Changing the regex to recognize dates and not phone numbers using date_pattern
    (2) check_for_phone & deid_phone functions rewritten as check_for_date & deid_date, respectively
-------------------------------------------------------------------------------
"""

date_pattern ='([1-9][/][1-9] | [1-9][/][1-3][0-9] | 1[0-2][/][1-9] | 1[0-2]/[1-3][0-9] | [1-9][/][1-9][/]\d{2} [1-9][/][1-3][0-9][/]\d{2} | 1[0-2][/][1-9][/]\d{2} | 1[0-2][/][1-3][0-9][/]\d{2})'
#date_pattern ='([1-9][/][1-3][0-9] | 1[0-2]/[1-3][0-9] | [1-9][/][1-3][0-9][/]\d{2} | 1[0-2][/][1-3][0-9][/]\d{2})'
# compiling the reg_ex would save sime time!
date_reg = re.compile(date_pattern)


def check_for_date(patient,note,chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.

    Logic:
        Search the entire chunk for date occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find dates.
    """
    
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in date_reg.finditer(chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
            print((match.start()-offset),match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')

            
def deid_date(text_path= 'id.text', output_path = 'date.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each date found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected date string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no date detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each date detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end date
        where `start` is the start position of the detected date string, and `end` is the detected end position of the string
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
                    # Now we have a full patient note stored in `chunk`, along with patient number and note number
                    # pass all to check_for_date to find any dates in note.
                    check_for_date(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_date(sys.argv[1], sys.argv[2])
    