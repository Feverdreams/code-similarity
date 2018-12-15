import re
import sys
date_pattern ='(((JAN)(UARY)?|(FEB)(UARY)?|(MAR)(CH)?|(APR)(IL)?|(MAY)|(JUN)E?|(JUL)Y?|(AUG)(UST)?|(SEP)(TEMBER)?|(OCT)(OBER)?|(NOV)(EMBER)?|(DEC)(EMBER)?)\s?[0-9][0-9]?,?\s?[0-9]{2,4}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|\b\d\d-?\d\d-?[12][90]\d\d\b|\b\d\d\/\d\d\/[12][90]\d\d\b) (\s\d\d:\d\d)?([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|[0-9]{1,2}-[0-9]{1,2}-[0-9]{2,4}|\d\d-?\d\d-?[12][90]\d\d|\d\d\/\d\d\/[12][90]\d\d) (\s\d\d:\d\d)?\d\/[0-9]{1,2}\/[0-9]{2,4}|\d-[0-9]{1,2}-[0-9]{2,4}\d\/[0-9]{1,2}\/[0-9]{2,4}\d\d?\/[12][90]\d\d|\d\d?-[12][90]\d\d|\d\d?\/0\d|\d\d?-0\d\d\d?\s\s?\d\d(\d\d)?'
# compiling the reg_ex would save some time!
da_reg=re.compile(date_pattern,re.I)
def check_for_phone(patient,note,chunk, output_handle):
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
        Use the precompiled regular expression to find phones.
    """
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in da_reg.finditer(chunk):
                
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
                    check_for_phone(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
'----------------------------------names-------------------------------'
doc_names=['../lists/pid_patientname.txt']
#doc_names=['../lists/local_places_unambig.txt','../lists/locations_unambig.txt']
names=[]
lines=[]
for each in doc_names:
    with open(each, 'r') as f:
        lines=f.readlines()
        for line in lines:
            line=line.replace("\n", "")
            line=line.replace(' ','')
            line=line.split('||||')
            if line[0]!='':
                names.append(line[0])
            if line[1]!='':
                names.append(line[1])
print('' in names)
'''doc='../lists/us_states_abbre.txt'
with open (doc,'r') as f:
    lines=f.readlines()
    for line in lines:
        line = line.replace("\n", "")
        line = line.replace(' ', '')
        if line in local_names:
            local_names.remove(line)
print('' in local_names)
'''
def check_for_name(patient, note, chunk, output_handle):
    # The perl code handles texts a bit differently,
    # we found that adding this offset to start and end positions would produce the same results
    offset = 0
    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient, note))

    #     age_pattern = "year old"
    #     ageInt_pattern = '[^\n\r\|]\n\d\d?\D'
    #     ageInt_reg = re.compile(ageInt_pattern)
    chunk = chunk.upper()

    for each in names:
        loc_reg = re.compile(each)
        for match in loc_reg.finditer(chunk):
            print(patient, note, end=" ")
            print(match.start() - offset, match.end() - offset, match.group())
            start_loc = match.start() - offset
            end_loc = match.end() - offset
            #             print(sentence)
            # create the string that we want to write to file ('start start end')
            result = str(start_loc) + ' ' + str(start_loc) + ' ' + str(end_loc)
            # write the result to one line of output
            output_handle.write(result + '\n')

def deid_name(text_path='id.text', output_path='name.phi'):
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
    with open(output_path, 'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line, flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line, flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_name(patient, note, chunk.strip(), output_file)

                    # initialize the chunk for the next note to be read
                    chunk = ''

if __name__== "__main__":
    deid_date(sys.argv[1], sys.argv[2])
    