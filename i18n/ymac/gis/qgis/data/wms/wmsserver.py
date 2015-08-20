from datetime import datetime


class WMSLayerSummary():

    def __init__(self, title="", name=""):
        self.name = name
        self.title = title
        self.layers = []
        self.referenceSystems = []

    @staticmethod
    def fromElement(element):
        wmsls = WMSLayerSummary()
        for child in element:
            tag = child.tag.lower()
            if tag == "name":
                wmsls.name = child.text
            elif tag == "title":
                wmsls.title = child.text
            elif tag == "srs":
                wmsls.referenceSystems.append(child.text)
            elif tag == "layer":
                wmsls.layers.append(WMSLayerSummary.fromElement(child))
        return wmsls


class WMSServerSummary(WMSLayerSummary):

    def __init__(self, title="", name=""):
        WMSLayerSummary.__init__(self, title, name)
        self.timestamp = datetime.now(None)

    @staticmethod
    def fromElement(element):
        wmsss = WMSServerSummary()
        for child in element:
            tag = child.tag.lower()
            if tag == "name":
                wmsss.name = child.text
            elif tag == "title":
                wmsss.title = child.text
            elif tag == "layer":
                wmsss.layers.append(WMSLayerSummary.fromElement(child))
        return wmsss
