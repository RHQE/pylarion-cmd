'''
Created on Nov 16, 2015

@author: xhe@redhat.com
'''

import os
from pylarion.work_item import TestCase, Requirement, TestStep
import lxml.html
import ConfigParser


class CliWorkItem:
    '''
    An object to manage the general commands

    Attributes:
    project_id:	string (RedHatEnterpriseLinux7 by default)
    workitem_type: type of work item
    workitem_list: all workitems in document
    '''
    def __init__(self, default_project):
        """CliWorkItem constructor.

        Args:
            default_project: the project where the module is located
        """
        self.project_id = default_project
        self.workitem_type = ""
        self.workitem_list = []

    def _get_input(self, description):
        '''Get document objects from polarion server

        Args:
            description: the string you want to display

        Returns:
            raw_input()
        '''
        return raw_input("%s:" % description)

    def _translate_html_to_text(self, html):
        '''translate html to text

        Args:
            html: the html code

        Returns:
            raw_input()
        '''
        if html is None:
            return None
        return lxml.html.fromstring(html).text_content()

    def _get_testcase_steps(self, case_id):
        '''get test steps from polarion server

        Args:
            case_id: test case ID

        Returns:
            the test steps object
        '''
        tc = TestCase(self.project_id, case_id)
        gsteps = tc.get_test_steps()
        """ type(gsteps) = <class 'pylarion.test_steps.TestSteps'> """
        return gsteps

    def _list_case_steps(self, case_id):
        '''parse test steps and save the steps to dict.

        Args:
            case_id: test case ID

        Returns:
            the dict of test steps
        '''
        print "Getting case steps from server..."
        gsteps = self._get_testcase_steps(case_id)
        steps_num = len(gsteps.steps)
        if steps_num == 0:
            return 1

        sdict = {}
        print "\nTest Steps for %s" % case_id
        for i in range(0, steps_num):
            html_steps = gsteps.steps[i].values[0].content
            html_exp_result = gsteps.steps[i].values[1].content
            ascii_steps = None
            ascii_exp = None
            if html_steps:
                html_st = self._translate_html_to_text(html_steps)
                ascii_steps = html_st.encode('ascii',
                                             'ignore').decode('ascii').strip()
            if html_exp_result:
                html_exp = self._translate_html_to_text(html_exp_result)
                ascii_exp = html_exp.encode('ascii',
                                            'ignore').decode('ascii').strip()
            sdict[i] = [str(ascii_steps), ascii_exp]
            print self._format_output(i, ascii_steps, ascii_exp)
        return sdict

    def _format_output(self, num, str1, str2):
        '''format test steps to output.

        Args:
            num: the step number
            str1: the test step string
            str2: the expect result string

        Returns:
            line: the print line
        '''
        line = '[%d]\nStep=%s\nExpectResult=%s' % (num, str1, str2)
        return line

    def _print_steps_from_file(self, case_id, stepfile):
        '''read config file and print test steps.

        Args:
            case_id: test case ID
            stepfile: the file of test step

        Returns:
            None
        '''
        cfile = ConfigParser.ConfigParser()
        cfile.read(stepfile)
        print "\n%s Steps:\n-------" % case_id
        for i in cfile.sections():
            print "[%s]" % i
            print "Step=%s" % cfile.get(i, 'Step')
            print "ExpectedResult=%s" % cfile.get(i, 'ExpectedResult')

    def _create_example_step_file(self, stepfile):
        '''create example file for test step.

        Args:
            stepfile: the file of test step

        Returns:
            None
        '''
        cfile = ConfigParser.ConfigParser()
        step = 'Example Step'
        exp = 'Example Result'
        cfile.add_section(str('0'))
        cfile.set('0', 'Step', step)
        cfile.set('0', 'ExpectedResult', exp)
        cfile.add_section(str('1'))
        cfile.set('1', 'Step', step)
        cfile.set('1', 'ExpectedResult', exp)
        cfile.write(open(stepfile, 'w+'))

    def _write_local_step_file(self, stepfile, sdict):
        '''write the test steps to local file

        Args:
            case_id: test case ID
            stepfile: the file of test step
            sdict: the dict of test steps

        Returns:
            0: refresh successful in local file
            1: no refresh in local file
        '''
        if sdict == 1:
            print "The step in polarion server is empty!"
            print "\nNeed add your steps to %s with default format!" % stepfile
            self._create_example_step_file(stepfile)
            return 1
        else:
            try:
                cfile = ConfigParser.ConfigParser()
                for n in sdict.keys():
                    step = sdict[n][0]
                    exp = sdict[n][1]
                    cfile.add_section(str(n))
                    cfile.set(str(n), 'Step', step)
                    cfile.set(str(n), 'ExpectedResult', exp)
                cfile.write(open(stepfile, 'w+'))
            except ConfigParser.NoSectionError:
                print "No Section Found in %s" % stepfile
                return 0
        print "Refresh successful! %s" % stepfile
        return 0

#    def create_links(self, workitem_id):
#        '''create links for testcases and requirement
#
#        Args:
#            workitem_id: the work item ID
#        Returns:
#            None
#        '''
#        TODO...

    def _load_steps(self, stepfile):
        '''read the local file.

        Args:
            stepfile: the file of test step

        Returns:
            lines: the string of printing
        '''
        lines = []
        try:
            cfile = ConfigParser.ConfigParser()
            cfile.read(stepfile)
            for i in(cfile.sections()):
                lst = [None, None]
                lst[0] = str(cfile.get(str(i), 'Step'))
                lst[1] = str(cfile.get(str(i), 'ExpectedResult'))
                lines.append(lst)
        except ConfigParser.NoSectionError:
            print "No Section Found in %s" % stepfile
        return lines

    def _update_steps(self, caseid, stepfile):
        '''update the steps to polarion server

        Args:
            case_id: test case ID
            stepfile: the file of test step

        Returns:
            None
        '''
        lines = self._load_steps(stepfile)
        tc = TestCase(self.project_id, caseid)
        set_steps = []
        for ln in lines:
            ts = TestStep()
            ts.values = [ln[0], ln[1]]
            set_steps.append(ts)
        # update
        tc.set_test_steps(set_steps)
        print "Done!"

    def _get_case_title(self, case_id):
        '''get test case title

        Args:
            case_id: test case ID

        Returns:
            tc.title
        '''
        tc = TestCase(self.project_id, case_id, fields=["title"])
        return tc.title

    def _get_case_attr(self, case_id):
        '''get test case properties

        Args:
            case_id: test case ID

        Returns:
            dict: get the properties of testcase item
        '''
        tc = TestCase(self.project_id, case_id)
        adict = {}
        adict["status"] = tc.status
        adict["type"] = tc.type
        adict["author"] = tc.author
        adict["created"] = str(tc.created).split('.')[0]
        adict["categories"] = tc.categories
        adict["description"] = self._translate_html_to_text(tc.description)
        adict["linked_work_items"] = tc.linked_work_items
        adict["updated"] = str(tc.updated).split('.')[0]
        adict["assignee"] = tc.assignee
#       adict["level"] = tc.level
#       adict["component"] = tc.component
        adict["subcomponent"] = tc.subcomponent
        adict["project_id"] = tc.project_id
        adict["initial_estimate"] = tc.initial_estimate
        adict["testtype"] = tc.testtype
        adict["subtype1"] = tc.subtype1
#       adict["importance"] = tc.importance
#       adict["automation"] = tc.automation
        adict["upstream"] = tc.upstream
        adict["tags"] = tc.tags
        adict["title"] = tc.title
        return adict

    def _get_req_attr(self, req_id):
        '''get requirement properties

        Args:
            req_id: requirement ID

        Returns:
            dict: get the properties of requirement item
        '''
        req = Requirement(self.project_id, req_id)
        adict = {}
        adict["status"] = req.status
        adict["type"] = req.type
        adict["author"] = req.author
        adict["created"] = str(req.created).split('.')[0]
        adict["categories"] = req.categories
        adict["description"] = self._translate_html_to_text(req.description)
        adict["linked_work_items"] = req.linked_work_items_derived
        adict["updated"] = str(req.updated).split('.')[0]
        adict["assignee"] = req.assignee
        adict["project_id"] = req.project_id
        adict["severity"] = req.severity
        adict["priority"] = req.priority
        adict["planed_in"] = req.planned_in
        adict["title"] = req.title
        return adict

    def get_steps_from_server(self, caseid, stepfile):
        '''get test steps from polarion server

        Args:
            case_id: test case ID
            stepfile: the file of test step

        Returns:
            None
        '''
        sdict = self._list_case_steps(caseid)
        print "\r"
        if os.path.exists(stepfile):
            question = "Need to re-write local file: %s? (N/Y)" % stepfile
            is_yes = self._get_input(question)
        else:
            print "Local file %s is created" % stepfile
            is_yes = "Y"
        if is_yes in ["Y", "y"]:
            self._write_local_step_file(stepfile, sdict)

    def sync_steps(self, case_id, stepfile):
        '''push the local file steps to polarion server.

        Args:
            case_id: test case ID
            stepfile: the file of test step

        Returns:
            None
        '''
        self._print_steps_from_file(case_id, stepfile)
        question = "\nUpdate above steps to polarion server? (Y/N)"
        is_yes = self._get_input(question)
        if is_yes in ['Y', 'y']:
            print "Updating..."
            self._update_steps(case_id, stepfile)
        else:
            print "Continue to edit %s by manual" % stepfile

    def get_linked_wis_for_case(self, case_id):
        '''get linked requirement id for the specified test case
        Args:
            case_id: test case ID

        Returns:
            lst: list of requirement IDs
        '''
        tc = TestCase(self.project_id, case_id,
                      fields=["linked_work_items"])
        lwis = tc.linked_work_items
        lst = []
        if isinstance(lwis, list):
            for lwi in lwis:
                if lwi.role == "verifies":
                    req_id = lwi.work_item_id
                    lst.append(req_id)
        else:
            lst = lwis
        return lst

    def get_linked_wis_for_req(self, req_id):
        '''get linked requirement id for the specified requirement
        Args:
            req_id: requirement ID

        Returns:
            lst: the list of test case IDs
        '''
        req = Requirement(self.project_id, req_id,
                          fields=["linked_work_items_derived"])
        lwis = req.linked_work_items_derived
        lst = []
        if isinstance(lwis, list):
            for lwi in lwis:
                if lwi.role == "verifies":
                    case_id = lwi.work_item_id
                    lst.append(case_id)
        else:
            lst = lwis
        return lst

    def list_linked_wis_for_case(self, case_id):
        '''list the linked testcase id
        Args:
            case_id: test case ID

        Returns:
            lwi.work_item_id: requirement IDs
        '''
        lwi = self.get_linked_wis_for_case(case_id)
        print "TestCase %s verifies the following items:" % case_id
        print "Rquirement ID"
        print "-------------"
        if isinstance(lwi, list):
            for wi in lwi:
                print wi
        else:
            print lwi.work_item_id

    def list_linked_wis_for_req(self, req_id):
        '''list the linked requirement id
        Args:
            req_id: requirement ID

        Returns:
            wi.work_item_id: testcase IDs
        '''
        lwi = self.get_linked_wis_for_req(req_id)
        print "Requirement %s is verified by the following items:" % req_id
        print "Case ID    "
        print "---------- "
        if isinstance(lwi, list):
            for wi in lwi:
                print wi
        else:
            print wi.work_item_id
