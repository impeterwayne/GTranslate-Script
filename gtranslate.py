#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This python skript extracts string resources, calls Google translate
# and reassambles a new strings.xml as fitted for Android projects.

# run via

# PYTHONIOENCODING=utf8 python3 gtranslate.py  OR using pythong launcher
# follow instructions

# output format: values-XX folders with strings.xml inside

# edited by alexVinrskis, March 2020

### LANGUAGE CODES FOR REFERENCE

#   af          Afrikaans
#   ak          Akan
#   sq          Albanian
#   am          Amharic
#   ar          Arabic
#   hy          Armenian
#   az          Azerbaijani
#   eu          Basque
#   be          Belarusian
#   bem         Bemba
#   bn          Bengali
#   bh          Bihari
#   xx-bork     Bork, bork, bork!
#   bs          Bosnian
#   br          Breton
#   bg          Bulgarian
#   km          Cambodian
#   ca          Catalan
#   chr         Cherokee
#   ny          Chichewa
#   zh-CN       Chinese (Simplified)
#   zh-TW       Chinese (Traditional)
#   co          Corsican
#   hr          Croatian
#   cs          Czech
#   da          Danish
#   nl          Dutch
#   xx-elmer    Elmer Fudd
#   en          English
#   eo          Esperanto
#   et          Estonian
#   ee          Ewe
#   fo          Faroese
#   tl          Filipino
#   fi          Finnish
#   fr          French
#   fy          Frisian
#   gaa         Ga
#   gl          Galician
#   ka          Georgian
#   de          German
#   el          Greek
#   gn          Guarani
#   gu          Gujarati
#   xx-hacker   Hacker
#   ht          Haitian Creole
#   ha          Hausa
#   haw         Hawaiian
#   iw          Hebrew
#   hi          Hindi
#   hu          Hungarian
#   is          Icelandic
#   ig          Igbo
#   id          Indonesian
#   ia          Interlingua
#   ga          Irish
#   it          Italian
#   ja          Japanese
#   jw          Javanese
#   kn          Kannada
#   kk          Kazakh
#   rw          Kinyarwanda
#   rn          Kirundi
#   xx-klingon  Klingon
#   kg          Kongo
#   ko          Korean
#   kri         Krio (Sierra Leone)
#   ku          Kurdish
#   ckb         Kurdish (Soranî)
#   ky          Kyrgyz
#   lo          Laothian
#   la          Latin
#   lv          Latvian
#   ln          Lingala
#   lt          Lithuanian
#   loz         Lozi
#   lg          Luganda
#   ach         Luo
#   mk          Macedonian
#   mg          Malagasy
#   ms          Malay
#   ml          Malayalam
#   mt          Maltese
#   mi          Maori
#   mr          Marathi
#   mfe         Mauritian Creole
#   mo          Moldavian
#   mn          Mongolian
#   sr-ME       Montenegrin
#   ne          Nepali
#   pcm         Nigerian Pidgin
#   nso         Northern Sotho
#   no          Norwegian
#   nn          Norwegian (Nynorsk)
#   oc          Occitan
#   or          Oriya
#   om          Oromo
#   ps          Pashto
#   fa          Persian
#   xx-pirate   Pirate
#   pl          Polish
#   pt-BR       Portuguese (Brazil)
#   pt-PT       Portuguese (Portugal)
#   pa          Punjabi
#   qu          Quechua
#   ro          Romanian
#   rm          Romansh
#   nyn         Runyakitara
#   ru          Russian
#   gd          Scots Gaelic
#   sr          Serbian
#   sh          Serbo-Croatian
#   st          Sesotho
#   tn          Setswanadef findall_content(xml_string, tag):

#   crs         Seychellois Creole
#   sn          Shona
#   sd          Sindhi
#   si          Sinhalese
#   sk          Slovak
#   sl          Slovenian
#   so          Somali
#   es          Spanish
#   es-419      Spanish (Latin American)
#   su          Sundanese
#   sw          Swahili
#   sv          Swedish
#   tg          Tajik
#   ta          Tamil
#   tt          Tatar
#   te          Telugu
#   th          Thai
#   ti          Tigrinya
#   to          Tonga
#   lua         Tshiluba
#   tum         Tumbuka
#   tr          Turkish
#   tk          Turkmen
#   tw          Twi
#   ug          Uighur
#   uk          Ukrainian
#   ur          Urdu
#   uz          Uzbek
#   vi          Vietnamese
#   cy          Welsh
#   wo          Wolof
#   xh          Xhosa
#   yi          Yiddish
#   yo          Yoruba
#   zu          Zulu

#
#   SUBROUTINES
#

# This subroutine calls Google translate and extracts the translation from
# the html request


async def translate(to_translate, to_language="auto", language="auto"):
    excepted=False
    while True:
        try:
            result = await translate_internal(to_translate, to_language, language)
            if excepted:
                print("FUCK: Success")
            return result
        except:
            if excepted:
                print("FUCK: Exception Again")
            else:
                print("FUCK: Exception")
            excepted = True

async def translate_internal(to_translate, to_language="auto", language="auto"):
    to_translate=serialize_text(to_translate, language)
    # send request
    session_timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(trust_env=True, timeout=session_timeout) as session:
        translate_url = "https://translate.google.com/m?sl=%s&tl=%s&q=%s&op=translate"% (language, to_language, to_translate.replace(" ", "+"))
        async with session.get(translate_url) as r:
            # r = requests.get("https://translate.google.com/m?sl=%s&tl=%s&q=%s&op=translate"% (language, to_language, to_translate.replace(" ", "+")))
            # set markers that enclose the charset identifier
            beforecharset='charset='
            aftercharset='" http-equiv'
            # extract charset
            text = await r.text()
            text_encoding = r.get_encoding()
            parsed1=text[text.find(beforecharset)+len(beforecharset):]
            parsed2=parsed1[:parsed1.find(aftercharset)]
            # Display warning when encoding mismatch
            if(parsed2!=text_encoding):
                pass
                print('\x1b[1;31;40m' + 'Warning: Potential Charset conflict' )
                print(" Encoding as extracted by SELF    : "+parsed2)
                print(" Encoding as detected by REQUESTS : "+text_encoding+ '\x1b[0m')

            # Work around an AGE OLD Python bug in case of windows-874 encoding
            # https://bugs.python.org/issue854511
            if(text_encoding=='windows-874' and os.name=='posix'):
                print('\x1b[1;31;40m' + "Alert: Working around age old Python bug (https://bugs.python.org/issue854511)\nOn Linux, charset windows-874 must be labeled as charset cp874"+'\x1b[0m')
                text_encoding='cp874'

            # convert html tags
            # text=html.unescape(r.text)
            # set markers that enclose the wanted translation
            before_trans = 'class="result-container">'
            after_trans='</div>'
            # extract translation and return it
            parsed1=text[text.find(before_trans)+len(before_trans):]
            parsed2=parsed1[:parsed1.find(after_trans)]
            # fix parameter strings
            parsed3 = re.sub('% ([ds])', r' %\1', parsed2)
            parsed4 = re.sub('% ([\d]) \$ ([ds])', r' %\1$\2', parsed3).strip()
            return deserialize_text(html.unescape(parsed4).replace("'", r"\'"))



# MAIN PROGRAM

# import libraries
import html
import requests
import os
import xml.etree.ElementTree as ET
import sys
from io import BytesIO
import re
import time
import shutil
from pathlib import Path
import asyncio
import urllib.parse
import aiohttp
from lxml import etree
# ask user for paramters, apply defaults
# Set default values
default_infile = "strings.xml"
default_inputlanguage = "en"
default_outputlangs = ["hi", "es", "fr","pt", "ko", "ru", "tr"]

# Read command-line arguments
args = sys.argv[1:]

# Apply defaults if necessary
INFILE = args[0] if len(args) > 0 else default_infile
INPUTLANGUAGE = args[1] if len(args) > 1 else default_inputlanguage
OUTPUTlangs = args[2:] if len(args) > 2 else default_outputlangs

# Remove the input language from the output languages list, if present
if INPUTLANGUAGE in OUTPUTlangs:
    OUTPUTlangs.remove(INPUTLANGUAGE)

specialChars = {
    "%s": "❤️", "%1$s": "🥕", "%2$s": "🍇", "%3$s": "🍐", "%4$s": "🍋",
    "%d": "🍖", "%1$d": "🍊", "%2$d": "🍎", "%3$d": "🍓", "%4$d": "🍅"
}

docTypevariableLists = {}


print("=================================================\n\n")

OUTDIRECTORY = Path('out')
if OUTDIRECTORY.exists():
    shutil.rmtree("out")
os.makedirs("out")

def serialize_text(text, language):

    for key, val in specialChars.items():
        text = text.replace(key, val)
    
    tag_match_regex = re.compile('<.*?>')
    text = re.sub(tag_match_regex, '', text)  # Remove all html tags from text (although there should be none, but still ensuring)

    # text = text.replace("&", "and")
    text = text.replace("\\n", "\n")    # Replace "\" "n" with next line character
    text = text.replace("\\'", "'")     # Replace \' with '
    text = text.replace("\\@", "@")     # Replace \@ with @
    text = text.replace("\\?", "?")     # Replace \? with ?
    text = text.replace("\\\"", "\"")   # Replace \" with "
    
    # text=text.lower()
    text = urllib.parse.quote_plus(text) # Encode final string

    return text

def deserialize_text(text):
    

    
    text = text.replace('\\ ', '\\').replace('\\ n ', '\\n').replace('\\n ', '\\n').replace('/ ', '/')

    text = text.replace("\n", "\\n")    # Replace next line with \n
    # text = text.replace("'", "\\'")     # Replace ' with \'
    text = text.replace("@", "\\@")     # Replace @ with \@
    text = text.replace("?", "\\?")     # Replace ? with \?
    text = text.replace("\"", "\\\"")   # Replace " with \"

    for key, val in specialChars.items():
        text = text.replace(val, key)
        
    
    return text
    

from xml.dom.minidom import parse, parseString
# repeat proccess for each of the lang
async def perform_translate(OUTPUTLANGUAGE):
    os.makedirs("out/values-{OUTPUTLANGUAGE}".format(OUTPUTLANGUAGE = OUTPUTLANGUAGE))
    OUTFILE= "out/values-{OUTPUTLANGUAGE}/strings.xml".format(OUTPUTLANGUAGE = OUTPUTLANGUAGE)
    # read xml structure
    tree = etree.parse(INFILE)
    root = tree.getroot()
    dtd = parse(INFILE).doctype
    for i in range(len(dtd.entities._seq)):
        docTypevariableLists[dtd.entities._seq[i].nodeName]=dtd.entities._seq[i].childNodes[0].nodeValue
    
    print("doctype Values:",docTypevariableLists)
    
    #tree = etree.parse(INFILE)
    #docinfo = tree.docinfo
    #print(docinfo.doctype)

    
    # print(OUTPUTLANGUAGE + "...\n")

    i=-1
    # cycle through elements
    while i  < len(root):
        i=i+1
        #if i>3 :
        #    break
    #	for each translatable string call the translation subroutine
    #   and replace the string by its translation,
    #   descend into each string array
    #     time.sleep(1)
        if i>=len(root):
            break
        isTranslatable=root[i].get('translatable')
        if isTranslatable:
            root.remove(root[i])
            i=i-1
            continue
        if(root[i].tag=='string') & (isTranslatable!='false'):
            # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
            totranslate=root[i].text
            if(totranslate!=None):
                root[i].text=await translate(totranslate,OUTPUTLANGUAGE,INPUTLANGUAGE)

            # if string was broken down due to HTML tags, reassemble it
            if len(root[i]) != 0:
                for element in range(len(root[i])):
                    root[i][element].text = " " + await translate(root[i][element].text, OUTPUTLANGUAGE, INPUTLANGUAGE)
                    root[i][element].tail = " " + await translate(root[i][element].tail, OUTPUTLANGUAGE, INPUTLANGUAGE)

        if(root[i].tag=='string-array' or root[i].tag=='plurals'):
            isParentTranslatable=root[i].get('translatable')
            for j in range(len(root[i])):
    #	for each translatable string call the translation subroutine
    #   and replace the string by its translation,
                isTranslatable=root[i][j].get('translatable')
                if(root[i][j].tag=='item') & ((isTranslatable!='false')&(isParentTranslatable!='false')):
                    # trasnalte text and fix any possible issues traslotor creates: messing up HTML tags, adding spaces between string formatting elements
                    totranslate=root[i][j].text
                    if(totranslate!=None):
                        root[i][j].text=await translate(totranslate,OUTPUTLANGUAGE,INPUTLANGUAGE)

                    # if string was broken down due to HTML tags, reassemble it
                    if len(root[i][j]) != 0:
                        for element in range(len(root[i][j])):
                            root[i][j][element].text = " " + await translate(root[i][j][element].text, OUTPUTLANGUAGE, INPUTLANGUAGE)
                            root[i][j][element].tail = " " + await translate(root[i][j][element].tail, OUTPUTLANGUAGE, INPUTLANGUAGE)
    # write new xml file
    tree.write(OUTFILE, encoding='utf-8')
    # Read in the file
    with open(OUTFILE, 'r',encoding='utf-8') as file :
        filedata = file.read()
        filedataSp=filedata.split("<resources>", 1)
    for key, val in docTypevariableLists.items():
        filedataSp[1] = filedataSp[1].replace(val, "&"+key+";")
        
    # Write the file out again
    with open(OUTFILE, 'w',encoding='utf-8') as file:
        file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"+filedataSp[0]+"<resources>"+filedataSp[1])
        
async def start_translate():
    coroutines = []
    for OUTPUTLANGUAGE in OUTPUTlangs:
        coroutines.append(perform_translate(OUTPUTLANGUAGE))
    await asyncio.gather(*coroutines)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(start_translate())
print("done")