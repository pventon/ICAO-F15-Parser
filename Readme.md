<h1>ICAO Field 15 Parser</h1>
<h2>General</h2>
This repository contains an ICAO Field 15 Parser implemented using Python version 3.10.7. A more recent version of Python must be used in order to support <b>match</b> statements used in the source code (switch statements in  other languages).
<p>The project has been built using the PyCharm 2022.2.2 (Professional Edition) IDE.
<p>An acronym list is provided at the end of this readme for readers unfamiliar with ATC acronyms.
<h2>Future Projects</h2>
<p>As of 4th October 2022 implementation is ongoing on a Python project for a complete ICAO message parser that will parse all ICAO ATS and OLDI messages in the ICAO format. The ICAO message parser should be uploaded within a few weeks, say end of October 2022. The list of supported message titles will be:
<ul>
<li>ICAO ATS -> ACH, ACP, AFP, APL, ARR, CDN, CHG, CNL, CPL, DEP, DLA, EST, FPL, FNM, MFS, RQP, RQS, SPL</li>
<li>OLDI -> ABI, ACP, ACT, AMA, CDN, COD, CPL, INF, LAM, MAC, OCM, PAC, RAP, REJ, REV, RJC, ROC, RRV, SBY</li>
</ul>
<p>Eventually there will be a fully data driven ADEXP parser also; no work in progress at the moment. I have a complete Java implementation of this and need to translate it to Python. It will come, but this will take time. The upcoming ICAO message parser has already been implemented to recognise ADEXP messages and the stub is in place to call a dedicated ADEXP parser. The initial release will be for the ICAO format only.
<h1>ICAO Field 15 Parser Technical Description</h1>
<p>ICAO Field 15 is a string containing an arbitrary number of tokens that together describe a route filed by a pilot describing the route to be flown. 
Individual token syntax is described in ICAO DOC 4444; this parser implements these descriptions in order to identify tokens based on their syntax.
ICAO Field 15 can be treated as a simple language comprised of three basic token types:
<ul>
<li><b>Points</b> - These can be AIP <b>PRPs</b>, <b>Latitude / Longitude</b>, <b>Point / Bearing / Distance</b> or <b>Aerodrome</b> tokens;</li>
<li><b>Connectors</b> - These can be AIP published <b>ATS routes</b>, <b>SID</b>, <b>STAR</b>, <b>DCT</b> and / or special connectors indicating non-IFR routing, (e.g. VFR sections);</li>
<li><b>Modifiers</b> - These consist of <b>Speed</b> and <b>Level</b> tokens that have to be applied at a point where they are specified;</li>
</ul>
ICAO Field 15 grammar / semantics analysis consists of parsing the field for correct token syntax and sequences of tokens that basically follow a 'point -> connector -> point -> connector -> point -> connector... etc. concept. 
<p>The parser starts by tokenizing the string representing ICAO Field 15; whitespace is removed and all tokens placed into a list with two identifiers, one identifying a tokens base type (e.g. point, connector or modifier) and a subtype that identifies a token in more detail, (e.g. a Latitude longitude point). The token type and subtype are derived from a tokens syntax.
<p>In addition, the zero based start and end index of a tokens location in the ICAO Field 15 string are stored; this can be used to highlight tokens in a GUI to identify erroneous tokens to users.
Once the token list is established, a class instance representing an empty ERS is created and both the token list (input) and ERS (output) are passed as arguments to the parser.
<p>The parser iterates through the tokens checking for correct semantics (and some limited syntax checking not picked up during tokenization) populating the ERS with an ERS record for each token processed.
<p>The ERS contains the speed and altitude at all points in both imperial units as extracted from field 15 and SI units.
SI altitudes are in meters and SI speed in meters / second. Flight rules are applied at each ERS item. Latitude and Longitude values are converted to decimal values and stored in the ERS. The azimuth and distance from one point to another are derived and stored; this can only be done where the latitude and longitude are known. The azimuth and distance between points are calculated using an oblate spheroid Earth model (geographicslib Python library).
<p>This parser performs no lookup into an AIP database to obtain latitude and longitude values for PRPs, although this could be done as a separate 'pass' over the ERS. All the methods for assigning coordinates and calculating azimuth / distance values are available in the F15Parse class.
<p>Flight rule changes accepted by the parser are:
<ul>
<li><b>IFR / VFR</b> - Flight plan Field 15 descriptions can change the flight rules between IFR -> VFR and VFR -> IFR at any point along a route;</li>
<li><b>OAT / GAT</b> - Flight plan Field 15 descriptions can change the flight rules between OAT -> GAT and GAT -> OAT at any point along a route;</li>
<li><b>IFPSTOP / IFPSTART</b> - These are CFMU IFPS specials to 'stop' IFR handling / processing between these designators. They are included in this implementation for completeness and may not be seen outside the CFMU IFPS.</li>
</ul>
Once parsing is complete and no errors exist, the ERS will contain a sequence of points connected by a connector of a given type with all speed and altitude data applied. The ERS is ready for 'full' population using AIP data after which ETO at points can be calculated if required.
The first and last points are always the ADEP and ADES; these are 'dummy' placeholders that must ultimately be populated from ATS messages, typically an FPL message when initially creating a flight plan.
<h1>Parser Usage</h1>
<p>Example usage of the ICAO field 15 parser.</p>
<pre><code>
# A sample Field 15 string...
token_string = "N0450M0825 00N000E B9 00N001E VFR IFR 00N001W/N0350F100 01N001W 01S001W 02S001W180060"
</code></pre>
<pre><code>
# Instantiate the tokenizer; the 'Tokenize()' class stores a copy of the field 15 string.
# If parallel processing is required using multiple threads, a new instance is
# required for each thread / field 15 string; individual field 15 strings must be 
# assigned to each instance of the Tokenize class.
tokenize = Tokenize()
</code></pre>
<pre><code>
# Set the string to be tokenized...
tokenize.set_string_to_tokenize(token_string)
</code></pre>
<pre><code>
# Set the white space to tokenize the ICAO field 15, these are a space (ASCII 20),
# a newline (\n), a tab (\t), a carriage return (\r) and the forward slash (/).
# The forward slash is always saved as a token, the remaining whitespace characters
# are discarded.
tokenize.set_whitespace(" \n\t\r/")
</code></pre>
<pre><code>
# Tokenize the Field 15 string
tokenize.tokenize()
</code></pre>
<pre><code>
# The tokenized list of tokens is stored in a list of Token class instances which can be
# retrieved as follows:
tokens = tokenize.get_tokens()
</code></pre>
<pre><code>
# Instantiate an Extracted Route Record instance, the parser 'output' will be stored
# in this class. Multi-threaded applications should also instantiate this class for each thread.
ers = ExtractedRouteSequence()
</code></pre>
<pre><code>
# Pass the input tokens and output ERS storage as parameters to the parser.
# If the parser return value is greater than zero then errors exist.
# It is a callers responsibility to retrieve the erroneous tokens with
# ers.get_all_errors() which returns a list of tokens (Token classes) containing all
# erroneous tokens along with their respective error messages.
# The erroneous tokens have their zero based start and end index describing
# their location in field 15; the zero based indices can be
# used to highlight erroneous tokens in a GUI.
# The Parse15 class is stateless and therefore only has to be instantiated once
# for multi-threaded applications.
num_errors = ParseF15().parse_f15(ers, tokens)
</code></pre>
<pre><code>
# An ERS can be examined with the following print command...
ers.print_ers()
</code></pre>

<h1>Acronyms</h1>
<ul>
<li>ADEP    Aerodrome of Departure (Given as an ICAO Location Indicator)</li>
<li>ADES    Aerodrome of Destination (Given as an ICAO Location Indicator)</li>
<li>AIP     Aeronautical Information Publication</li>
<li>ATC     Air Traffic Control</li>
<li>ATS     Air Traffic Service</li>
<li>CFMU    Central Flow Management Unit</li>
<li>DCT     Direct (used to specify direct routing between points)</li>
<li>ERS     Extracted Route Sequence</li>
<li>ETO     Estimated Time Over</li>
<li>GAT     General Air Traffic</li>
<li>ICAO    International Civil Aviation Organisation</li>
<li>IFR     Instrument Flight Rules</li>
<li>IFPS    Initial Flight Planing System</li>
<li>IFPSTOP Indicates end of IFR routing (used by the CFMU IFPS)</li>
<li>IFPSTART Indicates start of IFR routing (used by the CFMU IFPS)</li>
<li>OAT     Operational Air Traffic (typically military)</li>
<li>PRP     Published Route Points</li>
<li>SI      Metric measurement system</li>
<li>SID     Standard Instrument Departure</li>
<li>STAR    Standard Arrival Route</li>
<li>VFR     Visual Flight Rules</li>
</ul>
