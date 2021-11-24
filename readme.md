# Information Extraction Project

This is a system that answers a natural language questions about the world countries. It is part of the **Web Data Management course** taught at **Tel aviv university.**</br>
First, in the offline once need to create the knowledge graph of all countries in the world listed in [this link](https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)).</br>
An entity in our knowledge graph is an existence who has a wikipedia page.
A relation is actually a field in the infobox of the entitty that is belongs to.
![logo]()
Second, the online part. This is where the user can ask a question about a specific country of his choice or even can ask about presidents and prime ministers.  

## The system answers questions of the following format:
    1. Who is the president of <country>?
    2. Who is the prime minister of <country>?
    3. What is the population of <country>?
    4. What is the area of <country>?
    5. What is the government of <country>?
    6. What is the capital of <country>?
    7. When was the president of <country> born?
    8. When was the prime minister of <country> born?
    9. Who is <entity>?  
---
## Installation
    $ git clone https://github.com/ameedghanem/Information-Extraction.git 
      ... 
    $ cd Information-Extraction/

## Prerequesties
#### run the following command to install all prerequesties
    $ ./scripts/prerequesties.sh
# Usage
- The offline phase (creating the knowledge graph):
    `$ python geo_qa.py create ontology.nt`
    This part may takes 7 minutes.
- the online phases (natural language question answering)
    `$ python geo_qa.py question "<the user's question>"`
