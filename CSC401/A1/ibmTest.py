import requests
import csv
import json
import re, sys
# ibmTest.py
#
# This file tests all 3 classifiers using the NLClassifier IBM Service
# previously created using ibmTrain.py
#
# TODO: You must fill out all of the functions in this file following
# 		the specifications exactly. DO NOT modify the headers of any
#		functions. Doing so will cause your program to fail the autotester.
#
#		You may use whatever libraries you like (as long as they are available
#		on CDF). You may find json, request, or pycurl helpful.
#		You may also find it helpful to reuse some of your functions from ibmTrain.py.
#
reload(sys)
sys.setdefaultencoding('utf-8')
def get_classifier_ids(username,password):
	# Retrieves a list of classifier ids from a NLClassifier service
	# an outputfile named ibmTrain#.csv (where # is n_lines_to_extract).
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#
	# Returns:
	#	a list of classifier ids as strings
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason
	#

	#TODO: Fill in this function
	try:
		r = requests.get('https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers', auth=(username, password))
		classids = json.loads(r.text)
	except Exception as err:
		print('error:', err.args)

	return [str(classids['classifiers'][0]['classifier_id']), str(classids['classifiers'][1]['classifier_id']), str(classids['classifiers'][2]['classifier_id'])]


def assert_all_classifiers_are_available(username, password, classifier_id_list):
	# Asserts all classifiers in the classifier_id_list are 'Available'
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id_list - a list of classifier ids as strings
	#
	# Returns:
	#	None
	#
	# Error Handling:
	#	This function should throw an exception if the classifiers call fails for any reason AND
	#	It should throw an error if any classifier is NOT 'Available'

	#TODO: Fill in this function
	for classid in classifier_id_list:
		try:
			r = requests.get('https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'+classid, auth=(username, password))
			classifierdata = json.loads(r.text)
			if classifierdata['status'] != 'Available':
				raise Exception('Error: not all classifiers available')
		except Exception as err:
			print('error:', err.args)

	return

def classify_single_text(username,password,classifier_id,text):
	# Classifies a given text using a single classifier from an NLClassifier
	# service
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	classifier_id - a classifier id, as a string
	#
	#	text - a string of text to be classified, not UTF-8 encoded
	#		ex. "Oh, look a tweet!"
	#
	# Returns:
	#	A "classification". Aka:
	#	a dictionary containing the top_class and the confidences of all the possible classes
	#	Format example:
	#		{'top_class': 'class_name',
	#		 'classes': [
	#					  {'class_name': 'myclass', 'confidence': 0.999} ,
	#					  {'class_name': 'myclass2', 'confidence': 0.001}
	#					]
	#		}
	#
	# Error Handling:
	#	This function should throw an exception if the classify call fails for any reason
	#

	#TODO: Fill in this function
	classdict = {}
	try:
		text = text.strip("#")
		text = text.decode('cp1252').encode('utf-8')
		r = requests.get('https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'+classifier_id+'/classify?text='+text, auth=(username, password))
		textinfo = json.loads(r.text)
		classes = textinfo['classes']
		classeslist = list()
		for i in range(len(classes)):
			classeslist.append({'class_name': str(classes[i]['class_name']), 'confidence': classes[i]['confidence']})

		classdict = {'top_class': str(textinfo['top_class']), 'classes': classeslist}
	except Exception as err:
		print('error', err.args)
		return

	return classdict

def classify_all_texts(username,password,input_csv_name):
	# Classifies all texts in an input csv file using all classifiers for a given NLClassifier
	# service.
	#
	# Inputs:
	# 	username - username for the NLClassifier to be used, as a string
	#
	# 	password - password for the NLClassifier to be used, as a string
	#
	#	input_csv_name - full path and name of an input csv file in the
	#		6 column format of the input test/training files
	#
	# Returns:
	#	A list of "classifications". Aka:

	#TODO: Fill in this function
	file = open(input_csv_name, "rb")
	data = csv.reader(file)
	data = [row for row in data]      #gathering data from input file
	file.close()

	finaldict = {}

	for classifier_id in get_classifier_ids(username, password):
		r = requests.get('https://gateway.watsonplatform.net/natural-language-classifier/api/v1/classifiers/'+classifier_id, auth=(username, password))
		classifierdata = json.loads(r.text)
		dictname = str(classifierdata['name'])
		dictlist = list()

		for line in data:
			count = 0
			for element in line:
				count += 1
				if count == 6:
					dictlist.append(classify_single_text(username, password, classifier_id, element))
		finaldict[dictname] = dictlist

	return finaldict


def compute_accuracy_of_single_classifier(classifier_dict, input_csv_file_name, classifier_id):
	# Given a list of "classifications" for a given classifier, compute the accuracy of this
	# classifier according to the input csv file
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text)
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The accuracy of the classifier, as a fraction between [0.0-1.0] (ie percentage/100). \
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the
	#	inputs.
	#

	#TODO: fill in this function
	try:
		file = open(input_csv_file_name, "rb")
		data = csv.reader(file)
		data = [row for row in data]      #gathering data from input file
		file.close()
	except Exception as err:
		print(err.args)

	numbercorrect = 0
	ind = 0
	for line in data:
		count = 0
		for element in line:
			if count == 0:
				polarity = element #it's the first one
				break
			count += 1
		if polarity == classifier_dict[ind]['top_class']:
			numbercorrect += 1
		ind += 1

	return numbercorrect/float(ind)

def compute_average_confidence_of_single_classifier(classifier_dict, input_csv_file_name, classname):
	# Given a list of "classifications" for a given classifier, compute the average
	# confidence of this classifier wrt the selected class, according to the input
	# csv file.
	#
	# Inputs:
	# 	classifier_dict - A list of "classifications". Aka:
	#		A list of dictionaries, one for each text, in order of lines in the
	#		input file. Each element is a dictionary containing the top_class
	#		and the confidences of all the possible classes (ie the same
	#		format as returned by classify_single_text)
	# 		Format example:
	#			[
	#				{'top_class': 'class_name',
	#			 	 'classes': [
	#						  	{'class_name': 'myclass', 'confidence': 0.999} ,
	#						  	{'class_name': 'myclass2', 'confidence': 0.001}
	#							]
	#				},
	#				{'top_class': 'class_name',
	#				...
	#				}
	#			]
	#
	#	input_csv_name - full path and name of an input csv file in the
	#		6 column format of the input test/training files
	#
	# Returns:
	#	The average confidence of the classifier, as a number between [0.0-1.0]
	#	See the handout for more info.
	#
	# Error Handling:
	# 	This function should throw an error if there is an issue with the
	#	inputs.
	#

	#TODO: fill in this function
	totalconfidence = 0
	actualconfidence = 0

	for tweetindex in range(len(classifier_dict)):
		for classindex in range(len(classifier_dict[tweetindex]['classes'])):
			if classifier_dict[tweetindex]['classes'][classindex]['class_name'] == classname:
				actualconfidence += classifier_dict[tweetindex]['classes'][classindex]['confidence']
				totalconfidence += 1

	if totalconfidence != 0:
		return actualconfidence/float(totalconfidence)


if __name__ == "__main__":

	input_test_data = 'testdata.manual.2009.06.14.csv'
	username = '5b1fd9b7-c042-4884-9368-7077a842df8d'
	password = 'brtgMNbda3tL'

	classidlist = get_classifier_ids(username, password)

	#STEP 1: Ensure all 3 classifiers are ready for testing
	assert_all_classifiers_are_available(username, password, classidlist)

	#STEP 2: Test the test data on all classifiers
	classdict = classify_all_texts(username, password, input_test_data)
	#print classify_single_text(username, password, classidlist[0], 'lebron best athlete of our generation, if not all time (basketball related) I don\'t want to get into inter-sport debates about   __1/2')

	#STEP 3: Compute the accuracy for each classifier
	print(compute_accuracy_of_single_classifier(classdict['Classifier 500'], input_test_data, classidlist[0]))
	print compute_accuracy_of_single_classifier(classdict['Classifier 2500'], input_test_data, classidlist[1])
	print compute_accuracy_of_single_classifier(classdict['Classifier 5000'], input_test_data, classidlist[2])

	#STEP 4: Compute the confidence of each class for each classifier
	conf500_0 = compute_average_confidence_of_single_classifier(classdict['Classifier 500'], input_test_data, '0')
	conf500_4 = compute_average_confidence_of_single_classifier(classdict['Classifier 500'], input_test_data, '4')
	conf2500_0 = compute_average_confidence_of_single_classifier(classdict['Classifier 2500'], input_test_data, '0')
	conf2500_4 = compute_average_confidence_of_single_classifier(classdict['Classifier 2500'], input_test_data, '4')
	conf5000_0 = compute_average_confidence_of_single_classifier(classdict['Classifier 5000'], input_test_data, '0')
	conf5000_4 = compute_average_confidence_of_single_classifier(classdict['Classifier 5000'], input_test_data, '4')

	print conf500_0
	print conf500_4
	print conf2500_0
	print conf2500_4
	print conf5000_0
	print conf5000_4
