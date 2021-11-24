import requests 
import lxml.html
import rdflib
import urllib
import sys


WIKI_PREFIX = "http://en.wikipedia.org"
EXAMPLE_PREFIX = "http://example.org/"
UNITED_NATIONS_URL = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"

CNAME_INDEX = 6
EXAMPLE_ORG_LEN = 19

example_org_uri = lambda route: f'{EXAMPLE_PREFIX}{route}'
get_content = lambda entity: entity[0][EXAMPLE_ORG_LEN:]

president_r = rdflib.URIRef(example_org_uri('president'))
prime_minister_r = rdflib.URIRef(example_org_uri("prime_minister"))
population_r = rdflib.URIRef(example_org_uri("population"))
area_r = rdflib.URIRef(example_org_uri("area"))
capital_r = rdflib.URIRef(example_org_uri("capital"))
born_r = rdflib.URIRef(example_org_uri("born"))
government_r = rdflib.URIRef(example_org_uri("government"))

TOTAL_PRESIDENTS = set()
TOTAM_PRIME_MINISTERS = set()


def update_ontology(ontology, cname, capital, president, pt_bdate, prime_minister, pm_bdate, government, population, area):
	"""
	Adds all relevnt data about the given country!
	"""
	if capital != "":
		ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+cname), capital_r, rdflib.URIRef(EXAMPLE_PREFIX+capital)))
	if president != "":
		if president not in TOTAL_PRESIDENTS: # some presidents are actually presidents of more than one country!
			TOTAL_PRESIDENTS.add(president)
			ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+cname), president_r, rdflib.URIRef(EXAMPLE_PREFIX+president)))
	if prime_minister != "":
		if prime_minister not in TOTAM_PRIME_MINISTERS: # some presidents are actually presidents of more than one country!
			TOTAM_PRIME_MINISTERS.add(prime_minister)
			ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+cname), prime_minister_r, rdflib.URIRef(EXAMPLE_PREFIX+prime_minister)))
	if pt_bdate != "":
		ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+president), born_r, rdflib.URIRef(EXAMPLE_PREFIX+pt_bdate)))
	if pm_bdate != "":
		ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+prime_minister), born_r, rdflib.URIRef(EXAMPLE_PREFIX+pm_bdate)))
	if government != "":
		ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+cname), government_r, rdflib.URIRef(EXAMPLE_PREFIX+government)))
	if population != "":
		ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+cname), population_r, rdflib.URIRef(EXAMPLE_PREFIX+population)))
	if area != "":
		ontology.add((rdflib.URIRef(EXAMPLE_PREFIX+cname), area_r, rdflib.URIRef(EXAMPLE_PREFIX+area)))
	TOTAL_PRESIDENTS.add(president)


def get_countries_info(url, ontology_path="ontology.nt"):
    """
    Accepts a url of all countries in the world.
    It creates an onology for those countries.
    """

    president = prime_minister = population = area = government = capital = ""
    pt_bdate = pm_bdate = ""
    knowledge_graph = rdflib.Graph()
    res = requests.get(url) 
    doc = lxml.html.fromstring(res.content)

    table = doc.xpath("//table[1]")[0]
    countries = table.xpath(".//td//span[1]//a/@href")
    italic_written_countries = table.xpath(".//td/i//a[1]/@href")
    countries += italic_written_countries
    
    for index, c in enumerate(countries):
        # some of these fields are empty in some of the countries. Thus, we need to initialize them in each iteration
        president = prime_minister = population = area = government = capital = ""
        pt_bdate = pm_bdate = ""
        
        page = requests.get(WIKI_PREFIX + c)
        page_doc = lxml.html.fromstring(page.content)
        infobox = page_doc.xpath("//table[contains(@class, 'infobox')]")#[0]
        if not infobox:
            continue
        infobox = infobox[0]
        cname = c[CNAME_INDEX:]
        cname = urllib.parse.unquote(cname)

        president, pt_bdate = get_president_info(infobox)
        prime_minister, pm_bdate = get_prime_minister_info(infobox)
        capital = get_capital(infobox)
        government = get_government(infobox)
        population = get_population(infobox)
        area = get_area(infobox)
        
        update_ontology(
            knowledge_graph,
            cname, capital,
            president, pt_bdate,
            prime_minister, pm_bdate,
            government,
            population,
            area
        )
    knowledge_graph.serialize(ontology_path, format="nt")


def is_valid_area(s):
	"""
	Returns True iff s represents a vaaid value of area 
	"""
	for i in s:
		if (not (i.isdigit())) and i!=',' and i!='.' :
			return False

	return True


def get_birth_date(charecter_url):
	"""
	Accepts a url of some president.
	Returns his name and his date of birth
	"""
	res = requests.get(charecter_url)
	if res.status_code != 200:
		return ""
	doc = lxml.html.fromstring(res.content)
	infobox_lst = doc.xpath("//table[contains(@class, 'infobox')]")
	if not infobox_lst:
		return ""
	infobox = infobox_lst[0]
	# extract the date of birth
	bdate = ""
	b = infobox.xpath("//table//th[contains(text(), 'Born')]")
	if b != []:
		lst = b[0].xpath("./../td//span[@class='bday']//text()")
		if lst != []:
			if '\n' in lst:
				lst.remove('\n')
			#print(lst)
			bdate = lst[0].replace(" ", "_")
	if bdate == "":
		b = infobox.xpath("//table//th[contains(text(), 'Born')]")
		if b != []:
			lst = b[0].xpath("./../td/text()[1]")
			if lst != []:
				bdate = lst[0].replace(" ", "_")
	if sum([1 for ch in bdate if 0 <= ord(ch)-ord('0') <= 9]) < 1:
		bdate = ""
	return bdate


def get_president_info(infobox):
    president, pt_bdate = "", ""
    president_h = infobox.xpath("//th//div/a[text()='President']")
    if president_h != []:
        president = president_h[0].xpath("../../../td//a/text()")[0].replace(" ", "_")
        president_link = president_h[0].xpath("../../../td//a/@href")[0]
        pt_bdate = get_birth_date(WIKI_PREFIX + president_link)
    return president, pt_bdate


def get_prime_minister_info(infobox):
    prime_minister, pm_name = "", ""
    prime_minister_h = infobox.xpath("//tr//div/a[contains(text(), 'Prime Minister')]")
    if prime_minister_h != []:
        lst = prime_minister_h[0].xpath("../../../td//a/text()")
        if '\n' in lst: # there was a new line charecter at the start of lst in some cases
            lst.remove('\n')
        if lst:
            prime_minister = lst[0].replace(" ", "_")
            prime_minister_link = prime_minister_h[0].xpath("../../../td//a/@href")[0]
            pm_bdate = get_birth_date(WIKI_PREFIX + prime_minister_link)
    return prime_minister, pm_name


def get_capital(infobox):
	capital = ""
	capital_h = infobox.xpath("//table//th[contains(text(), 'Capital')]")
	if capital_h != []:
		capital_lst = capital_h[0].xpath("./../td//text()")
		if '\n' in capital_lst:
			capital_lst.remove('\n')
		if ' ' in capital_lst:
			capital_lst.remove(' ')
		capital = capital_lst[0].replace(" ", "_")
		if 'None' in capital_lst[0].replace(" ", ""):
			capital = ""
	return capital

def get_government(infobox):
	government = ""
	government_h = infobox.xpath("//table//tr/th[.//text()='Government']//text()/..")
	if government_h != []:
		government_words = government_h[0].xpath("./../../td//text()")
		if government_words == []:
			government_words = government_h[0].xpath(".//../td//text()")
		for word in government_words:
			if 'de facto' in word.lower():
				#government_words.remove('\n')
				government_words = government_words[:government_words.index(word)]
				break
		invalid_words = ['[', ':', '\n', ' ']
		government_words = [word for word in government_words if word not in invalid_words and 'de jure' not in word and 'de facto' not in word]
		for word in government_words:
			if '[' in word:
				continue
			if '(' in word:
				break
			if word.endswith(' '):
				word = word.replace(' ', '')
			government += (word.replace(' ', '_') + "_")
		government = government[:-1]
		if ' ' in government:
			government = government.replace(' ', '')
		if '__' in government:
			government = government.replace("__", '_')
		if government.startswith('_'):
			government = government[1:]
		if 'undera' in government:
			government = government.replace("undera", "under_a")
	return government

def get_population(infobox):
	population = ""
	population = infobox.xpath(".//tr[./th//text()='Population'][1]/following-sibling::tr[1]/td[1]//text()")
	if population == []:
		return ""
	if '\n' in population:
		population.remove('\n')
	if 'km' in population[0]:
		population = infobox.xpath(".//tr[./th//text()='Population'][1]/td[1]//text()")
	population = ''.join(population[0].split())
	if population.endswith('\n'):
		population = population[:-1]
	if '(' in population:
		population = population[:population.index('(')]
	return population

def get_area(infobox):
	area = ""
	km_found = False
	area_h = infobox.xpath("//table//tr[contains(./th/a/text(), 'Area')]/th/a/text()") #following-sibling::td[1]/text()")
	if area_h:
		area = infobox.xpath("//table//tr[contains(./th/a/text(), 'Area')]/following::td[1]//text()")
	else:
		area_h = infobox.xpath("//table//tr[contains(./th/a/text(), 'Area')]/td[1]/text()")
		if area_h:
			area = area_h[:-1]
		else:
			#area_h = infobox.xpath(".//tr[contains(.//th/text(), 'Area')]//th//text()")
			area = infobox.xpath(".//tr[contains(.//th/text(), 'Area')]/following::td[1]//text()")
	for val in area:
		if 'km' in val:
			km_found = True
			break
	if not km_found:
		area = infobox.xpath(".//tr[./th[contains(text(), 'Area')]]/td[1]//text()")
	return filter_area(area)


def filter_area(lst):
	lst = [word for word in lst if '[' not in word]
	val = lst[0]
	area = []
	if val.endswith('km'):
		if 'mi' in val:
			val = val.split()[-2]
		if '(' in val:
			val = val[1:]
		for ch in val:
			if ord(ch)<=127:
				area.append(ch)
			else:
				break
		return ''.join(area)+'_km2'
	elif is_valid_area(val.strip()) and 'km' in lst[1]:
		return val.strip()+'_km2'
	return ""


###############################
# Natural Language Processing
###############################

def extract_entity(question, word1, word2):
	"""
	extracts the entity whcih is actually the substring between the two given words
	"""
	ind1 = question.lower().index(word1.lower()) + len(word1)
	ind2 = question.lower().index(word2.lower())
	return question[ind1:ind2]



def parse_question(question):
	"""
	parses the question returns the relevant entity and relation
	"""
	entity = relation = ""
	if 'born' in question.lower(): # the pattern of when was <entitiy> born
		entity = extract_entity(question, 'of ', ' born')
		r = extract_entity(question, 'the ', ' of ')
		relation = 'born' + '_%s' % (r)
	elif 'who' in question.lower():
		if 'president' in question.lower() or 'prime minister' in question.lower():
			relation = extract_entity(question, 'is the ', ' of ')
			entity = extract_entity(question, ' of ', '?')
		else:
			relation = 'president_prime_minister'
			entity = question[7:-1]
	else:
		relation = extract_entity(question, 'is the ', ' of ')
		entity = extract_entity(question, ' of ', '?')
	if entity == "" or relation == "":
		return None
	entity, relation = entity.replace(" ", "_"), relation.replace(" ", "_")
	if entity.endswith('_'):
		entity = entity[:-1]
	if relation.endswith('_'):
		relation = relation[:-1]
	return entity, relation



def get_sparql_query(entity, relation):
	"""
	accepts an entity and a relation and bulids a proper sparql query
	"""
	query = None
	if relation != 'president_prime_minister' and 'born_' not in relation:
		query = ["select ?f where { <http://example.org/%s> <http://example.org/%s> ?f } " % (entity, relation)]
	elif relation.startswith('born'):
		relation = relation.split('_', 1)[1]
		query = ["select ?bdate where { <http://example.org/%s> <http://example.org/%s> ?p. ?p <http://example.org/born> ?bdate }" % (entity, relation)]
	else:
		q1 = "select ?c where { ?c <http://example.org/president> <http://example.org/%s> }" % entity
		q2 = "select ?c where { ?c <http://example.org/prime_minister> <http://example.org/%s> }" % entity
		query = [q1, q2]
	return query



def evaluate_query(query):
	"""
	Accepts a sparql query
	Returns the query's answer according to the ontology we've created before
	"""
	lst = []
	answer = ""
	geo_ontology = rdflib.Graph()
	geo_ontology.parse("ontology.nt", format="nt")
	if query:
		if len(query) > 1:
			res1 = geo_ontology.query(query[0])
			if res1:
				lst = list(res1) + ['president']
			res2 = geo_ontology.query(query[1])
			if res2 and not res1:
				lst = list(res2) + ['prime_minister']
		else:
			lst = list(geo_ontology.query(query[0]))
	if lst:
		answer = [get_content(ans).replace("_", " ") for ans in lst if type(ans) != str] + [t for t in lst if type(t) == str]
	return answer



def answer_the_question(question):
	"""
	accepts aquestion in natural language (ENG)
	prints the proper answer
	"""
	entity, relation = parse_question(question)
	query = get_sparql_query(entity, relation)
	answer = evaluate_query(query)
	if answer:
		if 'who is' not in question.lower():
			answer = ', '.join(answer) if len(answer) > 1 else answer[0]
			print(answer)
		else:
			if relation == 'prime_minister' or relation == 'president':
				answer = ', '.join(answer) if len(answer) > 1 else answer[0]
				print(answer)
			elif relation == 'president_prime_minister':
				print("%s of %s" % (answer[1].title().replace('_', ' '), answer[0]))
			else:
				sys.exit()


def run_quesries():
	"""
	We've bulit this function in order to evaluate the quesries that we were asked to, in part a of the assignment
	"""
	get_string = lambda entity:	entity[0][19:].replace('_', ' ') if 'http' in entity[0] else entity[0]
	q1 = "select distinct ?pCount (COUNT(?p) as ?pCount) WHERE { ?p <http://example.org/government> ?g . FILTER (regex(lcase(str(?g)), 'monarchy'))}" # monarchy government
	q2 = "select distinct ?pCount (COUNT(?p) as ?pCount) WHERE { ?p <http://example.org/government> ?g . FILTER (regex(lcase(str(?g)), 'republic'))}" # republic government
	q3 = "select distinct ?pCount (COUNT(?p) as ?pCount) WHERE { ?p <http://example.org/prime_minister> ?c . }" # prime minister count
	q4 = "select distinct ?pCount (COUNT(?a) as ?pCount) WHERE { ?p <http://example.org/area> ?a . }" # countries count
	queries = [q1, q2, q3, q4]

	g = rdflib.Graph()
	g.parse("ontology.nt", format="nt")
	t = [list(g.query(q))[0] for q in queries]
	for r in t:
		print(get_string(r))



###############
# M  A  I  N
###############

def run_qa(argv):
	if len(argv) == 1:
		sys.exit(f'Usage: argv[0] create ontology.nt OR argv[0] question <natural language question>')
	cmd = argv[1]
	if cmd == 'create' and argv[2].endswith(".nt"):
		get_countries_info(UNITED_NATIONS_URL, argv[2])
	elif cmd == 'question':
		answer_the_question(argv[2])
	else:
		print("Invalid Command")
		return


if __name__ == '__main__':
	#run_quesries() # this was for runnign the 4 queries that we have been asked to run in part A
	run_qa(sys.argv)