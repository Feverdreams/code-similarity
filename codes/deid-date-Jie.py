import re
import sys
date_pattern ='(((JAN)(UARY)?|(FEB)(UARY)?|(MAR)(CH)?|(APR)(IL)?|(MAY)|(JUN)E?|(JUL)Y?|(AUG)(UST)?|(SEP)(TEMBER)?|(OCT)(OBER)?|(NOV)(EMBER)?|(DEC)(EMBER)?)-?\s?[0-9][0-9]?,?-?\s?[0-9]{2,4}|[1-2]?[0-9]\s?-?\s?[0-3]?[0-9]\s?-?\s?[0-9]{0-4}|[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|\b\d\d-?\d\d-?[12][90]\d\d\b|\b\d\d\/\d\d\/[12][90]\d\d\b) (\s\d\d:\d\d)?([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2,4}|[0-9]{1,2}-[0-9]{1,2}-[0-9]{2,4}|\d\d-?\d\d-?[12][90]\d\d|\d\d\/\d\d\/[12][90]\d\d) (\s\d\d:\d\d)?\d\/[0-9]{1,2}\/[0-9]{2,4}|\d-[0-9]{1,2}-[0-9]{2,4}\d\/[0-9]{1,2}\/[0-9]{2,4}\d\d?\/[12][90]\d\d|\d\d?-[12][90]\d\d|\d\d?\/0\d|\d\d?-0\d\d\d?\s((JAN)(UARY)?|(FEB)(UARY)?|(MAR)(CH)?|(APR)(IL)?|(MAY)|(JUN)E?|(JUL)Y?|(AUG)(UST)?|(SEP)(TEMBER)?|(OCT)(TOBER)?|(NOV)(EMBER)?|(DEC)(EMBER)?)\s?\d\d(\d\d)?'

# compiling the reg_ex would save sime time!
ph_reg = re.compile(date_pattern)


def check_for_date(patient,note,chunk, output_handle):
    
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

            
            
def deid_date(text_path= 'id.text', output_path = 'date.phi'):
    
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
                    
                    check_for_date(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
        
    
    
    deid_date(sys.argv[1], sys.argv[2])
    