# python .\python\transform_xml\run.py
from lxml import etree

# Load the XML and XSLT files
xml_file = 'source.xml'
xslt_file = 'transform_template.xslt'

xml = etree.parse(xml_file)
xslt = etree.parse(xslt_file)

# Perform the transformation
transform = etree.XSLT(xslt)
result = transform(xml)

# Save the result to an XML file
with open('output.xml', 'wb') as f:
    f.write(etree.tostring(result, pretty_print=True))