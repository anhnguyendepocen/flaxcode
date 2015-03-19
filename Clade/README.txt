***
Clade has now been moved to https://github.com/flaxsearch/clade
***


==============
Flax Clade PoC
==============

26.Oct.12

Flax Clade PoC is a proof-of-concept open source taxonomy management and
document classification system, based on Apache Solr. In its current state it
should be considered pre-alpha. As open-source software you are welcome to try,
use, copy and modify Clade as you like. We would love to hear any constructive
suggestions you might have.

- Tom Mortimer <tom@flax.co.uk>
- Charlie Hull <charlie@flax.co.uk>

--------------------------------------
Taxonomies and document classification
--------------------------------------

Clade taxonomies have a tree structure, with a single top-level category (e.g.
in the example data, "Social Psychology"). There is no distinction between 
parent and child nodes (except that the former has children) and the hierachical
structure of the taxonomy is completely orthogonal from the node data. The
structure may be freely edited.

Each node represents a category, which is represented by a set of "keywords"
(words or phrases) which should be present in a document belonging to that 
category. Not all the keywords have to be present - they are joined with 
Boolean OR rather than AND. A document may belong to multiple categories, 
which are ranked according to standard Solr (TF-IDF) scoring. It is
also possible to exclude certain keywords from categories.

Clade will also suggest keywords to add to a category, based on the content of
the documents already in the category. This feature is currently slow as it 
uses the standard Solr MoreLikeThis component to analyse a large number of
documents. We plan to improve this for a future release by writing a custom
Solr plugin.

Documents are stored in a standard Solr index and are categorised dynamically
as taxonomy nodes are selected. As this is just a proof of concept, there is 
currently no way of writing the categorisation results to the documents, or
anywhere else.


--------------------------
Installation prerequisites
--------------------------

- Java 6 or 7

- Python 2.6 or 2.7

- Solr 3.6
    http://www.apache.org/dyn/closer.cgi/lucene/solr/3.6.0
    Other versions may also work, but we have not tested them with Clade.

- Python modules
    lxml:       http://pypi.python.org/pypi/lxml/
    httplib2:   http://code.google.com/p/httplib2/downloads/list
	
	On Windows you can download binaries of httplib2 from http://www.lfd.uci.edu/~gohlke/pythonlibs/

---------------
Getting started
---------------

Download the latest versions from these sites and follow the installation
instructions. The system has been developed on Linux and the following instructions
assume a Linux environment, but Windows alternative syntax is included where necessary.

**NEW** - Three batch files are provided (go1, go2 and go3.bat) that can be used to quickly start a 
demonstration version of Clade on Windows: each must be run in a separate command line window. 
You will need to provide the path to your Solr installation, Python and Java in setpaths.bat - 
also provided is cleandata.bat which will remove any previously indexed data. Read the rest of this
batch file to find out what the batch files are doing!

The Clade distribution includes an example taxonomy and documents derived 
from Wikipedia and on the topic of Social Psychology. The taxonomy is 
provided as a CSV file to illustrate how to import existing taxonomies.

To import the taxonomy, run on the command line:

    $ python classify.py import data/socpsy.csv
	
	on Windows:
	
	C:\> python classify.py import data\socpsy.csv

This will create a Python data structure, and pickle it as data/tax.

To import the documents, first copy the Clade Solr configuration files into your
Solr home, e.g.:

    $ cp -f clade/solr-conf/* apache-solr-3.6.0/example/solr/conf
	
	on Windows:
	
	C:\> copy clade\solr-conf\*.* apache-solr-3.6.0\example\solr\conf

Then [re]start Solr, e.g.:

    $ cd apache-solr-3.6.0/example
    $ java -jar start.jar &
	
	on Windows:

    C:\> cd apache-solr-3.6.0\example
    C:\> java -jar start.jar &

Now start the Stanford Named Entity Recognition server, which is used to pull
names, places etc. out of the source data:
 
    $ cd stanford-ner-2011-09-14
    $ ./server.sh &
	
	or on Windows:
	
	C:\ cd stanford-ner-2011-09-14
	C:\ server.bat

Finally, add the example documents (which are provided as plaintext files):

    $ python classify.py textdir data/socpsy-pages
	
	on Windows:
	
	C:\> python classify.py textdir data\socpsy-pages
	
This will output the name of each file as it is processed, and will take a 
few minutes to complete. 


--------------
Running the UI
--------------

The Clade UI is implemented as a web application. To start it, run:
 
    $ python server.py
	
	on Windows:
	
	C:\> python server.py

Then point a browser at 

    http://localhost:8080/
 
 
-----------
UI Controls
-----------

The Clade UI has two modes: Taxonomy and Document. It starts up in the former.

Taxonomy mode
-------------

The page is divided into two halves: the taxonomy tree on the left, and 
information about the current selected category on the right. Clade can support
multiple taxonomies, which can be selected from the drop-down in the upper left.
Selecting a taxonomy will load it into the tree view, where nodes can be
expanded or collapsed, selected and manipulated.

The taxonomy tree display has three small icons in the upper right. The + 
icon causes a new category to be added as a child of the currently selected 
node. The "pen" icon allows the current node name to be edited, and the X
icon deletes the current node (with no warning!)

Nodes and sub-trees may be dragged and dropped onto other nodes, allowing the
taxonomy structure to be rapidly edited.

On the right: the currently selected category name is listed, along with the
number of documents which fit the category. Under this is two keyword lists.

The list on the left contains the keywords which are active for this category.
This list has icons to (from left to right):

    - add a new keyword
    - edit the selected keyword
    - toggle the sense of the selected keyword from positive to negative
    - delete the selected keyword

Negative (NOT) keywords are displayed with a strikethrough. On the right, there
is a list of automatically-generated suggested keywords for this category. To
add one to the active keywords, select it and click the "left arrow" icon.

Below the two keyword lists is a list of the documents which match the current
category, showing the document ID, the title, the current rank and the previous
rank (before changing the active keywords). To view a document, click the title,
which will switch the UI into document mode.

To add a new taxonomy, make sure the taxonomy drop-down has no taxonomy 
selected, then click the Create button. Enter a name for the new taxonomy
and click OK. You can then create the taxonomy by adding nodes to the root
node. All changes will be immediately saved to the data/tax file.

To rename the current taxonomy, click the Rename button, edit the name in
the dialog box, and click OK.

To delete the current taxonomy, click the Delete button and then OK in the
confirm dialog.


Document mode
-------------

Again, in document mode the page has a left section and a right section. On the
left is a list of taxonomy categories which match the document, ranked in 
decreasing score order. The document ID and full text are displayed on the 
right, together with a list of keywords from the selected category. The document
text is highlighted for matching keywords.

To go back to the taxonomy display, click the Back button in the upper right.
Don't use your browser back button - it won't work, as the UI is implemented 
in Javascript/AJAX.

