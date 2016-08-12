'''
Created on Nov 16, 2015

@author: xhe@redhat.com
'''

import sys
from pylarion.document import Document


class CliDoc:
    '''
    An object to manage the general commands

    Attributes:
    project_id		:	string (RedHatEnterpriseLinux7 by default)
    space		:	space name (KernelStorageQE by default)
    document_no_name    :       no is only for selecting
    document_name       :       document name
    workitem_type       :       type of work item
    workitem_list       :       all workitems in document
    document_list       :       all document in one space
    '''
    def __init__(self, default_project, space):
        """Document constructor.

        Args:
            default_project: the project where the module is located
            space: document space location with one component or None for
                   default space
        """

        self.project_id = default_project
        self.space = space
        self.document_name = ""
        self.document_list = ""
        self.workitem_type = ""
        self.workitem_list = []

    def _get_docs_in_server(self):
        '''Get document objects from polarion server

        Args:
            None

        Returns:
            None
        '''
        print "Getting latest documents from server..."
        fields = ["document_id", "document_name", "author",
                  "created", "updated", "updated_by"]
        self.document_list = Document.get_documents(self.project_id,
                                                    self.space, fields)

    def _get_workitems_in_doc(self, doc_name_with_space):
        ''' Get work items from the document.
        Args:
            doc_name_with_space: specific space/doc_name of the repository,
                                 required if project_id is given
            item_type: the item type are one of these items:
                       testcase
                       requirement
        Returns:
            None
        '''
        doc = Document(self.project_id, doc_name_with_space)
        # Note: doc.get_work_items() without fields will return workitem uri
        fields = ["work_item_id", "author", "title", "type",
                  "status", "assignee", "categories", "comments",
                  "created", "approvals", "updated"]
        self.workitem_list = doc.get_work_items(None, True, fields)

    def _columnar_display(self, list, pagewidth=170):
        ''' Format the list content looks more beautiful
        Args:
            list: the content you expected be more beautiful

        Returns:
             None
        '''
        maxlen = 0
        for item in list:
            lt = len(str(item))
            if lt > maxlen:
                maxlen = lt
        maxlen += 2  # space it out a little more
        numcol = int(pagewidth / maxlen)

        i = 0
        for item in list:
            print "{0:{1}}".format(item, maxlen),
            i += 1
            if i % numcol == 0:
                print "\n",

    def _list_docs(self):
        '''Print the document list

        Args:
            None

        Returns:
            None
        '''
        self._get_docs_in_server()
        lst_doc = self.document_list
        num_doc = len(lst_doc)

        print "Totally Document: %d|loanding ...\n" % num_doc
        if num_doc < 1:
            print "No documents exist in space: %s" % self.space
            return 0

        for i in range(0, len(lst_doc)):
            print "%d: %s" % (i, lst_doc[i].document_name)
        return 0

    def get_input(self, description):
        '''Get input and format input

        Args:
            description: the string you want to display

        Returns:
            raw_input(instring)
        '''
        instring = "Please enter one %s to search e.g.RHEL7-2822\
            \n>>" % description
        return raw_input(instring)

    def check_doc_in_space(self, document_name=None):
        '''Check one document exists in the space

        Args:
            document_name (string): the document you checked

        Returns:
            None
        '''
        is_exists = False
        # It supports to get the document id from input
        if not document_name:
            # list all document under this space
            self._list_docs()
            # input the document name e.g. IB Test
            input_id = self.get_input("document name")

        print "Search ..."
        document_name = input_id
        field = ['author', 'updated', 'created']
        lst_doc = Document.get_documents(self.project_id, self.space, field)

        for i in range(0, len(lst_doc)):
            c_doc = lst_doc[i].document_name
            print c_doc
            if document_name in c_doc or c_doc in document_name:
                if is_exists is True:
                    print "\nIt's successfully to search the document!\n"
                    return 0
        return 1

    def list_workitems_in_doc(self, document_name, workitem_type):
        '''Get document from polarion server

        Args:
            document_name (string): the document includes work items
            workitem_type (string): the type of workitems (requirement
                                    or testcase)

        Returns:
            None
        '''
        if workitem_type not in ["requirement", "testcase"]:
            print '''Please choose "requirement" or "testcase"'''
            sys.exit(1)

        self._get_workitems_in_doc(document_name)
        print "\nList %s from document: %s" % (workitem_type, document_name)
        print "%sID   Title" % workitem_type
        print "----------%3s----------" % ('')
        for i in range(0, len(self.workitem_list)):
            if self.workitem_list[i].type == workitem_type:
                print "%s   %s" % (self.workitem_list[i].work_item_id,
                                   self.workitem_list[i].title)

    def get_docs(self, dpath):
        '''write document names into one local file and obtain the
        document list from the file in the future due to it's slow
        to get documents from polarion server

        Args:
            dpath (string): document path to write down

        Returns:
            None
        '''
        fh = open(dpath, "a+")
        try:
            if len(fh.readlines()) == 0:  # empty file
                self._get_docs_in_server()
                for i in range(0, len(self.document_list)):
                    fh.write(self.document_list[i].document_name)
                    fh.write('\n')
            else:
                inputs = raw_input("Refresh documents from server?(Y\N)")
                if inputs == 'Y' or inputs == 'y':
                    fh.truncate(0)
                    self._get_docs_in_server()
                    for i in range(0, len(self.document_list)):
                        fh.write(self.document_list[i].document_name)
                        fh.write('\n')

            # print the documents
            fh.seek(0)
            lines = fh.readlines()
            for line in lines:
                print line.strip()

        finally:
            fh.close()

    def list_headings_in_doc(self, document_name):
        ''' Get the headings for the document from polarion server

        Args:
            document_name: the document which includes headings

        Return:
            None
        '''
        self._get_workitems_in_doc(document_name)
        print "List headings from document %s" % document_name
        print "Heading ID        Title"
        print "--------------    -----"
        for i in range(0, len(self.workitem_list)):
            print "%s   d%s" % (self.workitem_list[i].work_item_id,
                                self.workitem_list[i].title)
