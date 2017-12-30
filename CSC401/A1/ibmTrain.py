# ibmTrain.py
#
# This file produces 3 classifiers using the NLClassifier IBM Service
#
# TODO: You must fill out all of the functions in this file following
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#

###IMPORTS###################################
import requests
import csv
import json
import re, sys


###HELPER FUNCTIONS##########################
reload(sys)
sys.setdefaultencoding('utf-8')

def convert_training_csv_to_watson_csv_format(input_csv_name, group_id, output_csv_name):
	# Converts an existing training csv file. The output file should
	# contain only the 11,000 lines of your group's specific training set.
	#
	# Inputs:
	#	input_csv - a string containing the name of the original csv file
	#		ex. "my_file.csv"
	#
	#	output_csv - a string containing the name of the output csv file
	#		ex. "my_output_file.csv"
	#
	# Returns:
	#	None

	#TODO: Fill in this function

	file = open(input_csv_name, "rb")
	data = csv.reader(file)
	data = [row for row in data]      #gathering data from input file
	file.close()

	i = 0
	class0 = (group_id * 5500, (group_id + 1) * 5500 - 1)
	class4 = 800000 + group_id * 5500, 800000 + (group_id + 1) * 5500 - 1
	print class0, class4

	for line in data:
		if (i >= class0[0] and i <= class0[1]) or (i >= class4[0] and i <= class4[1]):
			polarity = line[0]
			tweet = re.sub("\"", "", line[5])
			tweet = tweet.decode('cp1252').encode('utf-8')
			with open(output_csv_name, 'a') as op_file:
				op_file_writer = csv.writer(op_file)
				op_file_writer.writerow([tweet, polarity])
				op_file.close()
		i += 1

	return


def extract_subset_from_csv_file(input_csv_file, n_lines_to_extract, output_file_prefix='ibmTrain'):
	# Extracts n_lines_to_extract lines from a given csv file and writes them to
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs:
	#	input_csv - a string containing the name of the original csv file from which
	#		a subset of lines will be extracted
	#		ex. "my_file.csv"
	#
	#	n_lines_to_extract - the number of lines to extract from the csv_file, as an integer
	#		ex. 500
	#
	#	output_file_prefix - a prefix for the output csv file. If unspecified, output files
	#		are named 'ibmTrain#.csv', where # is the input parameter n_lines_to_extract.
	#		The csv must be in the "watson" 2-column format.
	#
	# Returns:
	#	None

	#TODO: Fill in this function

	file = open(input_csv_file, "rb")
	data = csv.reader(file)
	data = [row for row in data]      #gathering data from input file
	file.close()
	count = 0
	n = str(n_lines_to_extract)

	if output_file_prefix == '':              #name of output file
		op_filename = "ibmTrain" + n + ".csv"
	else:
		op_filename = output_file_prefix + n + ".csv"

	for line in data:
		if count < n_lines_to_extract:
			with open(op_filename, 'a') as op_file:
				op_file_writer = csv.writer(op_file)
				op_file_writer.writerow(line)
				op_file.close()
			count += 1

	return


def create_classifier(username, password, n, input_file_prefix='ibmTrain'):
	# Creates a classifier using the NLClassifier service specified with username and password.
	# Training_data for the classifier provided using an existing csv file named
	# ibmTrain#.csv, where # is the input parameter n.
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	n - identification number for the input_file, as an integer
	#		ex. 500
	#
	#	input_file_prefix - a prefix for the input csv file, as a string.
	#		If unspecified data will be collected from an existing csv file
	#		named 'ibmTrain#.csv', where # is the input parameter n.
	#		The csv must be in the "watson" 2-column format.
	#
	# Returns:
	# 	A dictionary containing the response code of the classifier call, will all the fields
	#	specified at
	#	http://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/natural-language-classifier/api/v1/?curl#create_classifier
	#
	#
	# Error Handling:
	#	This function should throw an exception if the create classifier call fails for any reason
	#	or if the input csv file does not exist or cannot be read.
	#

	#TODO: Fill in this function
	try:
		url = "https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers"
		training_data = {'training_data': open(input_file_prefix+str(n)+".csv", "rb"), 'training_metadata': "{\"language\": \"en\", \"name\" : \"Classifier "+str(n)+"\"}"}
		r = requests.get(url, auth=(username, password))

		r = requests.post(url, files=training_data, auth=(username, password))

		code = r.status_code

		str_code = str(code);
		if str_code[0] == '5':
			print "Error: Internal system error! Please try again later."
		elif str_code[0] == '2':
			print "Success!"
		else:
			print "Error! Something went wrong! Please try again."
	except Exception as err:
		print (err.args)

	return r.text

if __name__ == "__main__":

	### STEP 1: Convert csv file into two-field watson format
	input_csv_name = 'training.1600000.processed.noemoticon.csv'

	#DO NOT CHANGE THE NAME OF THIS FILE
	output_csv_name ='training_11000_watson_style.csv'


	convert_training_csv_to_watson_csv_format(input_csv_name, 125, output_csv_name)


	### STEP 2: Save 3 subsets in the new format into ibmTrain#.csv files

	#TODO: extract all 3 subsets and write the 3 new ibmTrain#.csv files
	#
	# you should make use of the following function call:
	#
	n_lines_to_extract = 500
	#extract_subset_from_csv_file(input_csv,n_lines_to_extract)
	extract_subset_from_csv_file('training_11000_watson_style.csv', n_lines_to_extract)

	n_lines_to_extract = 2500
	extract_subset_from_csv_file('training_11000_watson_style.csv', n_lines_to_extract)

	n_lines_to_extract = 5000
	extract_subset_from_csv_file('training_11000_watson_style.csv', n_lines_to_extract)


	### STEP 3: Create the classifiers using Watson

	#TODO: Create all 3 classifiers using the csv files of the subsets produced in
	# STEP 2
	#
	#
	# you should make use of the following function call
	n = 500
	username = '5b1fd9b7-c042-4884-9368-7077a842df8d'
	password = 'brtgMNbda3tL'
	#create_classifier(username, password, n, input_file_prefix='ibmTrain')

	n = 2500
	create_classifier(username, password, n, input_file_prefix='ibmTrain')

	n = 5000
	create_classifier(username, password, n, input_file_prefix='ibmTrain')
