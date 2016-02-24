/*
 * Raw xHTML parser
 * A pure JavaScript SAX-like HTML/XHTML parser.
 *
 * Felipe A. Hernández - http://spayder26.blogspot.com
 * John Resig - http://ejohn.org/blog/pure-javascript-html-parser/
 * Erik Arvidsson - http://erik.eae.net/archives/2004/11/20/12.18.31/
 * Licensed under Mozilla Public License
 */
window.rhp = (function() {
  /* Raw xHTML parser */
  var $def = function(a, b) {
      return typeof((b || window)[a]) != "undefined";
    },
    makeMap = function(a) {
      var r = {};
      for (var i = 0, b = a.split(','), o; o = b[i++];) {
        r[o] = 1;
      }
      return r;
    },
    startTag =
    /^<(\w+)((?:\s+\w+(?:\s*=\s*(?:(?:"[^"]*")|(?:'[^']*')|[^>\s]+))?)*)\s*(\/?)>/,
    endTag = /^<\/(\w+)[^>]*>/,
    attr =
    /(\w+)(?:\s*=\s*(?:(?:"((?:\\.|[^"])*)")|(?:'((?:\\.|[^'])*)')|([^>\s]+)))?/g,
    me = {},
    esc = [
      ["&", "&amp;"],
      [">", "&gt;"],
      ["<", "&lt;"],
      ["\"", "&quot;"],
      ["'", "&apos;"]
    ],
    esr = [],
    unesr = [],
    esl,
    getDoc = function(node) {
      if (node.nodeType == 9) {
        return node;
      }
      return (node.ownerDocument || (node.getOwnerDocument && node.getOwnerDocument()) ||
        document);
    };
  esl = esc.length;
  for (var i = 0; i < esl; i++) {
    esr[i] = new RegExp(esc[i][0], "g");
    unesr[i] = new RegExp(esc[i][1], "g");
  }
  var empty = makeMap(
      "area,base,basefont,br,col,frame,hr,img,input,isindex,link,meta,param,embed"
    ),
    block = makeMap(
      "address,applet,blockquote,button,center,dd,del,dir,div,dl,dt,fieldset,form,frameset,hr,iframe,ins,isindex,li,map,menu,noframes,noscript,object,ol,p,pre,script,table,tbody,td,tfoot,th,thead,tr,ul"
    ),
    inline = makeMap(
      "a,abbr,acronym,applet,b,basefont,bdo,big,br,button,cite,code,del,dfn,em,font,i,iframe,img,input,ins,kbd,label,map,object,q,s,samp,script,select,small,span,strike,strong,sub,sup,textarea,tt,u,var"
    ),
    closeSelf = makeMap("colgroup,dd,dt,li,options,p,td,tfoot,th,thead,tr"),
    fillAttrs = makeMap(
      "checked,compact,declare,defer,disabled,ismap,multiple,nohref,noresize,noshade,nowrap,readonly,selected"
    ),
    special = makeMap("script,style");
  me.HTMLParser = function(html, handler) {
    // SAX-like HTML parser
    var stack = [],
      parseEndTag = function(tag, tagName) {
        var pos, i;
        if (!tagName) {
          pos = 0;
        } else {
          for (pos = stack.length - 1; pos > -1; pos--) {
            if (stack[pos] == tagName) {
              break;
            }
          }
        }
        if (pos >= 0) {
          for (i = stack.length - 1; i >= pos; i--) {
            if (handler.end) {
              handler.end(stack[i]);
            }
          }
          stack.length = pos;
        }
      },
      parseStartTag = function(tag, tagName, rest, unary) {
        if (block[tagName]) {
          while (stack.last() && $def(stack.last(), inline)) {
            parseEndTag("", stack.last());
          }
        }
        if (closeSelf[tagName] && stack.last() == tagName) {
          parseEndTag("", tagName);
        }
        unary = (empty[tagName] || !!unary);
        if (!unary) {
          stack.push(tagName);
        }
        if (handler.start) {
          var attrs = [];
          rest.replace(attr,
            function(match, name) {
              var value = arguments[2] ? arguments[2] : (arguments[3] ?
                arguments[3] : (arguments[4] ? arguments[4] : (
                  fillAttrs[name] ? name : "")));
              attrs.push({
                name: name,
                value: value,
                escaped: value.replace(/(^|[^\\])"/g, '$1\\\"')
              });
            });
          if (handler.start) {
            handler.start(tagName, attrs, unary);
          }
        }
      },
      last = html,
      index, chars, match;
    stack.last = function() {
      return (this.length) ? this[this.length - 1] : null;
    };
    while (html) {
      chars = true;
      if (!stack.last() || !special[stack.last()]) {
        if (html.indexOf("<!--") === 0) {
          index = html.indexOf("-->");
          if (index >= 0) {
            if (handler.comment) {
              handler.comment(html.substring(4, index));
            }
            html = html.substring(index + 3);
            chars = false;
          }
        } else if (html.indexOf("</") === 0) {
          match = html.match(endTag);
          if (match) {
            html = html.substring(match[0].length);
            match[0].replace(endTag, parseEndTag);
            chars = false;
          }
        } else if (html.indexOf("<") === 0) {
          match = html.match(startTag);
          if (match) {
            html = html.substring(match[0].length);
            match[0].replace(startTag, parseStartTag);
            chars = false;
          }
        }
        if (chars) {
          index = html.indexOf("<");
          var text = (index < 0) ? html : html.substring(0, index);
          html = (index < 0) ? "" : html.substring(index);
          if (handler.chars) {
            handler.chars(text);
          }
        }
      } else {
        html = html.replace(new RegExp("(.*)<\/" + stack.last() +
          "[^>]*>"), (function() {
          return function(all, text) {
            text = text.replace(/<!--(.*?)-->/g, "$1").replace(
              /<!\[CDATA\[(.*?)\]\]>/g, "$1");
            if (handler.chars) {
              handler.chars(text);
            }
            return "";
          };
        })());
        parseEndTag("", stack.last());
      }
      if (html == last) {
        throw "Parse Error: " + html;
      }
      last = html;
    }
    parseEndTag();
  };
  me.escapeXHTML = function(html) {
    // Escape XHTML characters
    for (var i = 0; i < esl; i++) {
      html = html.replace(esr[i], esc[i][1]);
    }
    return html;
  };
  me.unescapeXHTML = function(html) {
    // Unescape XHTML characters
    for (var i = esl - 1; i > -1; i--) {
      html = html.replace(unesr[i], esc[i][0]);
    }
    return html;
  };
  me.HTMLtoXML = function(html) {
    // Parses HTML string to XML string (XHTML)
    var results = "";
    me.HTMLParser(html, {
      start: function(tag, attrs, unary) {
        results += "<" + tag.toLowerCase();
        for (var i = 0, il = attrs.length; i < il; i++) {
          results += " " + attrs[i].name.toLowerCase() + '="' +
            attrs[i].escaped + '"';
        }
        results += (unary ? "/" : "") + ">";
      },
      end: function(tag) {
        results += "</" + tag.toLowerCase() + ">";
      },
      chars: function(text) {
        results += text;
      },
      comment: function(text) {
        results += "<!--" + text + "-->";
      }
    });
    return results;
  };
  me.HTMLtoNODE = function(html, node) {
    // Writes an HTML string to DOM's node
    var elems = [node],
      doc = getDoc(node),
      cur = node;
    me.HTMLParser(html, {
      start: function(tagName, attrs, unary) {
        var elem = doc.createElement(tagName);
        for (var i = 0, il = attrs.length; i < il; i++) {
          elem.setAttribute(attrs[i].name, me.unescapeXHTML(attrs[i]
            .value));
        }
        if (cur && cur.appendChild) {
          cur.appendChild(elem);
        }
        if (!unary) {
          elems.push(elem);
          cur = elem;
        }
      },
      end: function(tag) {
        elems.length -= 1;
        cur = elems[elems.length - 1];
      },
      chars: function(text) {
        cur.appendChild(doc.createTextNode(me.unescapeXHTML(text)));
      },
      comment: function(text) {
        if (doc.createComment) {
          cur.appendChild(doc.createComment(text));
        }
      }
    });
  };
  me.HTMLtoDOM = function(html, doc) {
    // HTML string to DOM's document node
    if (!doc) {
      doc = document;
    } else {
      doc = getDoc(doc);
    }
    var n = doc.createElement("div");
    me.HTMLtoNODE(html, n);
    return n.childNodes;
  };
  return me;
}());
