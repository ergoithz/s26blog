Raw xHTML Parser
===============
it's a pure JavaScript SAX-like HTML/XHTML parser  licensed under Mozilla Public License.

Introduction
------------
It's based both on [http://ejohn.org/blog/pure-javascript-html-parser John Resig Pure javascript HTML Parser] and [http://erik.eae.net/archives/2004/11/20/12.18.31/ Erik Arvidsson Simple HTML Parser].

Usage
-----
This parser will be available as an object named rhp, on window scope. It's fairly error proofed, so it can be used to check and fix XHTML and HTML errors like unclosed tags and malformed attributes.

Methods
-------
  * `HTMLParser( string html, hashtable handler )`
    SAX-like parser, receives an HTML string, and a hashtable of callbacks for every type of node.
  * `escapeXHTML( string html )` -> string
    Return escaped string (string without reserved words).
  * `unescapeXHTML( string html )` -> string
    Translate between escaped html code to real string.
  * `HTMLtoXML( string html )` -> string
    Translates HTML to XML (XHTML). Remember XHTML is valid HTML, so an XMLtoHTML converter is unnecessary.
  * `HTMLtoNODE( string html , DOMElement node )` 
    Writes given HTML to DOM, under given node.
  * `HTMLtoDOM( string html [, DOMDocument doc ] )`
    Writes given HTML code on top of DOM's structure.
    
