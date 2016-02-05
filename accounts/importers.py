from kb.groups.models import Group, Membership
from xml.dom.minidom import parse as xml_parse

class AccountsImporter(object):
    group_references = None

    def __init__(self, institute, *args, **kwargs):
        self.institute = institute
        self.group_references = {}

    def add_group(self, group_name, local_reference=None):
        group, _ = Group.objects.get_or_create(title=group_name,
                                               institute=self.institute)
        if local_reference is not None:
            self.group_references[local_reference] = group.pk


class ParnassysImporter(AccountsImporter):

    def _nodes_to_dict(self, nodes):
        attr = {}
        for node in nodes:
            if node.nodeName == "#text":
                continue
            elif node.hasAttribute("key"):
                attr[node.nodeName] = node.getAttribute("key")
            elif len(node.childNodes) == 1 and \
                    node.childNodes[0].nodeName == "#text":
                attr[node.nodeName] = node.childNodes[0].nodeValue
            else:
                values = []
                for child_node in node.childNodes:
                    if child_node.hasAttribute("key"):
                        values.append(child_node.getAttribute("key"))
                attr[node.nodeName] = values
        return attr

    def parse(self, xml_file):
        self.dom = xml_parse(xml_file)
        for node in self.dom.firstChild.childNodes:
            self.parse_info_block(node)

    def parse_info_block(self, node):
        if node.nodeName == "#text":
            pass
        elif node.nodeName == "school":
            pass
        elif node.nodeName == "groepen":
            for group in node.childNodes:
                if group.nodeName != "groep":
                    continue
                self.parse_group(group)
        elif node.nodeName == "leerlingen":
            for student in node.childNodes:
                if student.nodeName != "leerling":
                    continue
                self.parse_student(student)

    def parse_group(self, node):
        key = node.getAttribute('key')
        attributes = self._nodes_to_dict(node.childNodes)
        self.add_group(attributes['naam'], key)

    def parse_student(self, node):
        attributes = self._nodes_to_dict(node.childNodes)
        pass
