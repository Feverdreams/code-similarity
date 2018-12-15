import re
import sys
phone_pattern ='(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4})'

# compiling the reg_ex would save sime time!
ph_reg = re.compile(phone_pattern)

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
        Search the entire chunk for phone number occurances. Find the location of these occurances 
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
    for match in ph_reg.finditer(chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            print(patient, note,end=' ')
            print((match.start()-offset),match.end()-offset, match.group())
                
            # create the string that we want to write to file ('start start end')    
            result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
            # write the result to one line of output
            output_handle.write(result+'\n')
            
def deid_phone(text_path= 'id.text', output_path = 'phone.phi'):
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

############Define deid_age()###############################

def check_for_age(patient, note, chunk, output_handle, age_indicators_suff):
    
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))
    
#     age_pattern = "year old"
    ageInt_pattern = '[^\n\r\|]\n\d\d?\D'
    ageInt_reg = re.compile(ageInt_pattern)
    
    for age_pattern in age_indicators_suff:
        age_reg = re.compile(age_pattern)

        for match in age_reg.finditer(chunk):
            
            pre_length = 5

            # debug print, 'end=" "' stops print() from adding a new line
            sentence = chunk[max(0, (match.start()-pre_length)):match.end()]

            matchInt = ageInt_reg.search(sentence)

            if (matchInt):
                print(patient, note,end=' ')
                
                start_loc = (match.start() -pre_length + matchInt.start() + 1-offset - 1)
                print(start_loc,(match.start() -pre_length + matchInt.end() - 1-offset - 2), matchInt.group()[1:-1])  
                print(sentence)

                # create the string that we want to write to file ('start start end')    
                result = str(start_loc) + ' ' + str(start_loc) +' '+ str(match.start() -pre_length + matchInt.end() - 1-offset - 2) 

                # write the result to one line of output
                output_handle.write(result+'\n')    

def deid_age(text_path= 'id.text', output_path = 'phone.phi'):

    # Age indicators that follow ages
    # age_indicators_suff = ["year old", "y\. o\.", "y\.o\.", "yo", "years old", "year-old", "-year-old", "years-old", "-years-old", "years of age", "yrs of age"]
    age_indicators_suff = [ "yo"]
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
#                 print(line)
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                
                if len(record_start):
#                     print(record_start[0])
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
#                     print(chunk)
#                     check_for_phone(patient,note,chunk.strip(), output_file)
                    check_for_age(patient,note,chunk.strip(), output_file, age_indicators_suff)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''

############Define deid_ptname()###############################

def check_for_ptname(patient, note, chunk, output_handle, name_set):
    
    # The perl code handles texts a bit differently, 
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))
    
#     age_pattern = "year old"
#     ageInt_pattern = '[^\n\r\|]\n\d\d?\D'
#     ageInt_reg = re.compile(ageInt_pattern)
    chunk = chunk.upper()
    
    for age_pattern in name_set:
        age_reg = re.compile(r'\s' + age_pattern +'\s')

        for match in age_reg.finditer(chunk):

            print(patient, note,end=' ')

            start_loc = match.start() - offset
            end_loc = match.end() - offset
            print(start_loc, end_loc, match.group()) 
            print(chunk[max(0, start_loc -10 + offset):(end_loc + 10 + offset)])
#             print(sentence)

            # create the string that we want to write to file ('start start end')    
            result = str(start_loc) + ' ' + str(start_loc) +' '+ str(end_loc) 

            # write the result to one line of output
            output_handle.write(result+'\n')    

def deid_ptname(text_path= 'id.text', output_path = 'phone.phi'):

    ## generate nameset
    ptname_path = '../lists/pid_patientname.txt'

    name_set = set()
    with open(ptname_path, 'r') as fi:
        line = fi.readline()
        
        while line:
    #         print(line)
            split_line = line.split('||||')
            if (len(split_line[1].strip()) > 4): 
                name_set.add(split_line[1].strip() )
                
            if (len(split_line[2].strip()) > 4): 
                name_set.add(split_line[2].strip() )
            line = fi.readline()
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
#                 print(line)
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                
                if len(record_start):
#                     print(record_start[0])
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
#                     print(chunk)
#                     check_for_phone(patient,note,chunk.strip(), output_file)
                    check_for_ptname(patient,note,chunk.strip(), output_file, name_set)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''

############Define deid_hcpname()###############################
def deid_hcpname(text_path= 'id.text', output_path = 'phone.phi'):

    ## generate nameset
    ptname_path = '../lists/doctor_last_names.txt'

    name_set = set()
    with open(ptname_path, 'r') as fi:
        line = fi.readline()
        
        while line:

            doc_name = line.strip()
            if (len(doc_name) > 4): 
                name_set.add(doc_name )

            line = fi.readline()

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
#                 print(line)
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                
                if len(record_start):
#                     print(record_start[0])
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
#                     print(chunk)
#                     check_for_phone(patient,note,chunk.strip(), output_file)
                    check_for_ptname(patient,note,chunk.strip(), output_file, name_set)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''

############Define deid_location()###############################
def deid_location(text_path= 'id.text', output_path = 'phone.phi'):

    ## generate name_set
    ptname_path = '../lists/stripped_hospitals.txt'

    name_set = set()
    with open(ptname_path, 'r') as fi:
        line = fi.readline()
            
        while line:

            doc_name = line.strip()
            if (len(doc_name) > 4): 
                name_set.add(doc_name.upper())

            line = fi.readline()

    name_set.add('CROSS')
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
#                 print(line)
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                
                if len(record_start):
#                     print(record_start[0])
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
#                     print(chunk)
#                     check_for_phone(patient,note,chunk.strip(), output_file)
                    check_for_ptname(patient,note,chunk.strip(), output_file, name_set)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''

############Define deid_relativeName()###############################

def deid_relativeName(text_path= 'id.text', output_path = 'phone.phi'):
    ## generate nameset
    ptname_path = '../lists/pid_patientname.txt'
    name_set = set()
    with open(ptname_path, 'r') as fi:
        line = fi.readline()
        
        while line:
    #         print(line)
            split_line = line.split('||||')
            if (len(split_line[1].strip()) > 3): 
                name_set.add(split_line[1].strip() )
                
            if (len(split_line[2].strip()) > 3): 
                name_set.add(split_line[2].strip() )
            line = fi.readline()
    name_set.remove('WILL')
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
#                 print(line)
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                
                if len(record_start):
#                     print(record_start[0])
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
#                     print(chunk)
#                     check_for_phone(patient,note,chunk.strip(), output_file)
                    check_for_ptname(patient,note,chunk.strip(), output_file, name_set)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''

if __name__== "__main__":
    deid_age(sys.argv[1], sys.argv[2])
    # deid_ptname(sys.argv[1], sys.argv[2])
    # deid_relativeName(sys.argv[1], sys.argv[2])
    # deid_location(sys.argv[1], sys.argv[2])
    # deid_hcpname(sys.argv[1], sys.argv[2])
    # deid_phone(sys.argv[1], sys.argv[2])
    