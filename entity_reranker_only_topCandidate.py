#!/usr/bin/python

## This script takes a naf file with an entities layer as input 
## For each entity disambiguation candidate, it looks up the dbpedia type (class)
## of each candidate and reranks the candidates based on the dbpedia class ranking 
## for the domain at hand. 
## This version loads the dbpedia resource table in memory
## It also only prints the highest ranking candidate 

## Created by: Marieke van Erp (marieke.van.erp@vu.nl)
## Date: 13 November 2014 

import sys
from KafNafParserPy import *
import codecs
import re
import datetime
from random import randrange

# Resource Types table 
dbpedia_table =  "DBpediaResourceTypeTableOnlyRanked.tsv"

lp = Clp()
lp.set_name('vua-nedtype-reranking')
lp.set_version('1.0')
lp.set_beginTimestamp()

types = {}
with open(dbpedia_table) as f:
	for line in f:
		line = re.sub('\n', '',line)
		fields = line.split('\t')
		types[fields[0]] = fields[1]

# Get the file
input = sys.stdin

# parse the XML
my_parser = KafNafParser(input)

# Get the entities 
for entity in my_parser.get_entities():
	terms = []
	entity_text = "" 
	# Get the span of the references (entities) 
	for reference in entity.get_references():
		for span_obj in reference:
			for item in span_obj.get_span_ids():
				terms.append(item)
	# Also get the text that denote the entities 
	for term in terms:
		entity_text = entity_text + " " + my_parser.get_term(term).get_lemma()
	entity_text = entity_text.rstrip()
	reranked = {}
	# Also get the actual references 
	for external_reference in entity.get_external_references():
		resource_name = external_reference.get_reference().replace('http://dbpedia.org/resource/','')	
		if resource_name in types:
			reranked[external_reference.get_reference()] = int(types[resource_name])
			print external_reference.get_reference(), types[resource_name]
	if len(reranked) > 0:
		max_key = sorted(reranked.items(), key=lambda t: -t[1])[0][0]
		new_reference = CexternalReference()			
		new_reference.set_resource('vua-type-reranker-v1.0')
		new_reference.set_reference(max_key)
		new_reference.set_confidence(str(reranked[max_key]))
		my_parser.add_external_reference_to_entity(entity.get_id(),new_reference)
		
lp.set_endTimestamp()
my_parser.add_linguistic_processor('entities', lp)

my_parser.dump()
		

