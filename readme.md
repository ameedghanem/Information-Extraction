# Information Extraction Project

This is a system that answers a natural language questions about the world countries. It is part of the **Web Data Management course** taught at **Tel aviv university.**</br>
## First - The offline part
In this part once create a knowledge graph of all countries in the world listed in [this link](https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)).</br>
- An entity in our knowledge graph is an existence who has a wikipedia page.
- A relation is actually a field in the infobox of the entitty it belongs to.
![logo](https://github.com/ameedghanem/Information-Extraction/blob/main/logos/Screenshot%20from%202021-11-24%2014-31-55.png)
## Second -  The online part
This is where the user can ask a question about a specific country of his choice or even can ask about presidents and prime ministers.
The question asked by the user has to be one these following format:</br>
`
    1. Who is the president of <country>?</br>
    2. Who is the prime minister of <country>?</br>
    3. What is the population of <country>?</br>
    4. What is the area of <country>?</br>
    5. What is the government of <country>?</br>
    6. What is the capital of <country>?</br>
    7. When was the president of <country> born?</br>
    8. When was the prime minister of <country> born?</br>
    9. Who is <entity>?
`
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
