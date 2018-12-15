import re
import sys
import nltk

########### check_for_Date #######################################
months = {"January", "Jan", "February", "Feb", "March", "Mar", "April",
          "Apr", "May", "June", "Jun", "July", "Jul", "August", "Aug",
          "September", "Sept", "Sep", "October", "Oct", "November", "Nov",
          "December", "Dec"}
date_pattern = ' ((\d{1,2})/(\d{1,2})) [^UP]'

date_reg = re.compile(date_pattern, re.IGNORECASE)


def check_for_Date(patient, note, chunk, output_handle):

    # define offset based on the length of patient and note
    offset = 25 + len(patient) + len(note)

    for match in date_reg.finditer(chunk):
        month = match.groups()[1]
        day = match.groups()[2]

        # constrains on month and dat value
        if not 1 <= int(month) <= 12:
            continue
        if not 1 <= int(day) <= 31:
            continue
        print(patient, note, end=' ')
        print((match.span(1)[0] - offset), (match.span(1)[1] - offset), match.group().strip())
        result = str(match.span(1)[0] - offset) + ' ' + str(match.span(1)[0] - offset) + ' ' + str(
            match.span(1)[1] - offset)
        output_handle.write(result + '\n')
########### end of check_for_Date ################################


########### check_for_PTName #######################################
PT_indicatos_pre = ['Mr', 'Mr\.', 'Mrs', 'Mrs\.']
PT_regs = []
for indicator in PT_indicatos_pre:
    pattern = "%s[ ]+([A-z]{2,})" % (indicator)
    reg = re.compile(pattern, re.IGNORECASE)
    PT_regs.append(reg)

def check_for_PTName(patient, note, chunk, output_handle):

    # define offset based on the length of patient and note
    offset = 25 + len(patient) + len(note)

    # use all regs to find PHI
    for reg in PT_regs:
        for match in reg.finditer(chunk):
            print(patient, note, end=' ')
            print((match.span(1)[0] - offset), (match.span(1)[1] - offset), match.group().strip())
            result = str(match.span(1)[0] - offset) + ' ' + str(match.span(1)[1] - offset) + ' ' + str(
                match.span(1)[1] - offset)
            output_handle.write(result + '\n')
########### end of check_for_PTName ################################


########### check_for_HCPName #######################################
HCP_indicatos_pre = ['Dr\.', 'dr', 'doctor', 'DR\'S', '[\s]+Q\.']
HCP_regs = []
for indicator in HCP_indicatos_pre:
    pattern = "%s[\s]+([A-z\-']+)" % (indicator)
    reg = re.compile(pattern, re.IGNORECASE)
    HCP_regs.append(reg)

    pattern = "%s[\s]+[A-z\-']+[\s]+AND[\s]+([A-z\-']+)" % (indicator)
    reg = re.compile(pattern, re.IGNORECASE)
    HCP_regs.append(reg)


def check_for_HCPName(patient, note, chunk, output_handle):
    offset = 25 + len(patient) + len(note)
    for reg in HCP_regs:
        for match in reg.finditer(chunk):
            print(patient, note, end=' ')
            print((match.span(1)[0] - offset), (match.span(1)[1] - offset), match.group().strip())
            result = str(match.span(1)[0] - offset) + ' ' + str(match.span(1)[1] - offset) + ' ' + str(
                match.span(1)[1] - offset)
            output_handle.write(result + '\n')
########### end of check_for_HCPName ################################


########### check_for_age ###########################################
age_indicators_pre = ["age", "he is", "she is", "patient is"]
age_indicators_suff = ["year old", "y\. o\.", "y\.o\.", "yo",
                       "years old", "year-old", "-year-old", "years-old",
                       "-years-old", "years of age", "yrs of age", 's/p']
age_regs = []
for indicator in age_indicators_pre:
    age_pattern = "%s[\s]?(\d{2,3}$)" % (indicator)
    reg = re.compile(age_pattern, re.IGNORECASE)
    age_regs.append(reg)

for indicator in age_indicators_suff:
    age_pattern = "(\d{2,3})[\s]%s" % (indicator)
    reg = re.compile(age_pattern, re.IGNORECASE)
    age_regs.append(reg)


def check_for_age(patient, note, chunk, output_handle):
    offset = 25 + len(patient) + len(note)
    for reg in age_regs:
        for match in reg.finditer(chunk):
            age = match.groups()[0]
            if 90 <= int(age) <= 125:
                print(patient, note, end=' ')
                print((match.span(1)[0] - offset), (match.span(1)[1] - offset), match.group())
                result = str(match.span(1)[0] - offset) + ' ' + str(match.span(1)[1] - offset) + ' ' + str(
                    match.span(1)[1] - offset)
                output_handle.write(result + '\n')
########### end of check_for_age ####################################


########### check_for_phone #########################################
phone_pattern = '(\d{3}[-\.\s/]??\d{3}[-\.\s/]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s/]??\d{4}|\d{5} |\d{5}$)'
ph_reg = re.compile(phone_pattern)


def check_for_phone(patient, note, chunk, output_handle):
    offset = 25 + len(patient) + len(note)
    for match in ph_reg.finditer(chunk):
        print(patient, note, end=' ')
        print((match.start() - offset), match.end() - offset, match.group())
        result = str(match.start() - offset) + ' ' + str(match.start() - offset) + ' ' + str(match.end() - offset)
        output_handle.write(result + '\n')
########### end of check_for_phone ####################################


########## check_for_RelativeProxyName ###############################
proxyname_indicators = ["daughter", "daughters", "dtr", "son", "brother",
                        "sister", "mother", "mom", "father", "dad", "wife",
                        "husband", "neice", "nephew", "spouse", "partner",
                        "cousin", "aunt", "uncle", "granddaughter", "grandson",
                        "grandmother", "grandmom", "grandfather", "granddad", "relative",
                        "friend", "neighbor", "visitor", "family member", "lawyer",
                        "priest", "rabbi", "coworker", "co-worker", "boyfriend",
                        "girlfriend", "friends", "sons", "brothers", "sisters",
                        "sister-in-law", "brother-in-law", "mother-in-law", "father-in-law",
                        "son-in-law", "daughter-in-law", "dtr-in-law"]
proxyname_regs = []
exclude_phrases = ['on', 'and', 'from', 'is', 'did', 'for', 'she', 'he',
                   'called', 'who']
exclude = ''
for phrase in exclude_phrases:
    exclude += ('(?!%s)' % phrase)

for indicator in proxyname_indicators:
    pattern = '%s\s*%s([a-zA-Z]{4,})' % (indicator, exclude)
    reg = re.compile(pattern, re.IGNORECASE)
    proxyname_regs.append(reg)


def check_for_RelativeProxyName(patient, note, chunk, output_handle):
    offset = 25 + len(patient) + len(note)
    for reg in proxyname_regs:
        for match in reg.finditer(chunk):
            p_name = match.groups()[0]

            # using NLTK to remove other types of words
            tokens = nltk.word_tokenize(p_name)
            pos_tags = nltk.pos_tag(tokens)
            if pos_tags[0][1] in ['IN', 'PRP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'MD', 'DT', 'RB', 'JJ', 'NNS']:
                continue
            print(pos_tags)
            print(patient, note, end=' ')
            print(match.span(1)[0] - offset, match.span(1)[1] - offset, match.groups()[0])
            result = str(match.span(1)[0] - offset) + ' ' + str(match.span(1)[1] - offset) + ' ' + str(
                match.span(1)[1] - offset)
            output_handle.write(result + '\n')
########## end of check_for_RelativeProxyName #########################


def deid(text_path='id.text', output_path='phone.phi'):
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
                record_start = re.findall(start_of_record_pattern, line, flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line, flags=re.IGNORECASE)

                if len(record_end):
                    output_file.write('Patient {}\tNote {}\n'.format(patient, note))
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number

                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_phone(patient, note, chunk.strip(), output_file)
                    # check_for_Date(patient, note, chunk.strip(), output_file)
                    # check_for_PTName(patient, note, chunk.strip(), output_file)
                    # check_for_age(patient, note, chunk.strip(), output_file)
                    # check_for_HCPName(patient, note, chunk.strip(), output_file)
                    # check_for_RelativeProxyName(patient, note, chunk.strip(), output_file)

                # initialize the chunk for the next note to be read
                chunk = ''


if __name__ == "__main__":
    deid(sys.argv[1], sys.argv[2])
