#!/usr/bin/env python

import os
import sys
import commands
import getopt
import ConfigParser
import shutil
from pylarion.document import Document
from pylarion.work_item import TestCase 
from pylarion.work_item import Requirement
from pylarion.work_item import *
from pylarion.test_run import TestRun

class Repo(object):
    """Attributes includes the all options of command line"""
    def __init__(self,
                 assignee=None,
                 comment=None,
                 document=None,
                 query=None,
                 debug=None,
                 testcase=None,
                 links=None,
                 template=None,
                 plannedin=None,
                 result=None,
                 plan_ids=None,
                 requirement=None,
                 run=None,
                 steps=None,
                 workitem_type=None,
                 status=None):
        self.assignee = assignee
        self.comment = comment
        self.document = document
        self.query = query
        self.debug = debug
        self.testcase = testcase
        self.links = links
        self.template = template
        self.plannedin = plannedin
        self.result = result
        self.plan_ids = plan_ids
        self.requirement = requirement
        self.run = run
        self.steps = steps
        self.workitem_type = workitem_type
        self.status = status

class Config(object):
    """Attributes includes the usesful parameters in config"""
    def __init__(self,
                 user=None,
                 space=None,
                 plannedin=None,
                 assignee=None):
        self.user = user
        self.conf_space = space
        self.conf_plannedin = plannedin

    def getconf(self, confile):
        condict = {}
        cfile = ConfigParser.SafeConfigParser()

        cfile.read(confile)
        condict["con_space"] = cfile.get('cmd', 'space')
        condict["project"] = cfile.get('webservice', 'default_project')
        condict["output"] = cfile.get('cmd', 'output')
        condict["user"] = cfile.get('webservice', 'user')
        condict["con_plannedin"] = cfile.get('cmd', 'plannedin')
        condict["assignee"] = cfile.get('cmd', 'assignee')

        return condict


class CmdList(object):

    def __init__(self, project=None, space=None):
        self.project = project
        self.space = space
        pass

    def list_all_documents_under_space(self, fields=None):
        fields=["document_id",
                "document_name",
                "author",
                "created",
                "updated",
                "updated_by"]
        doc_list = Document.get_documents(self.project,
                                          self.space,
                                          fields)
        return doc_list

    def list_documents_by_query(self,
                                query,
                                is_sql=False,
                                fields=None):
        fields=["document_id",
                "document_name",
                "author",
                "created",
                "updated",
                "updated_by"]
        doc_list = Document.query(query, is_sql, fields)

        return doc_list

    def print_documents(self, docs, fields):
        print "Created%7sAuthor%7sDocument" % ('', '')
        print "-------%7s------%7s--------" % ('', '')

        for doc in docs:
            print "%-14s %-11s %s" % (doc.created.strftime('%Y-%m-%d'),
                                      doc.author,
                                      doc.document_id)

    def list_workitems_in_document(self, doc_name_with_space):
        doc = Document(self.project, doc_name_with_space)
        fields = ["work_item_id",
                  "author",
                  "title",
                  "type",
                  "status",
                  "assignee",
                  "categories",
                  "comments",
                  "created",
                  "approvals",
                  "updated"]
        self.workitem_list = doc.get_work_items(None, True, fields)
        return self.workitem_list

    def print_workitems(self, workitems):
        print "Type%10sID%12sDescription" % ('', '')
        print "-------%7s-----%9s--------" % ('', '')

        for wi in workitems:
            print "%-13s %-13s %s" % (wi.type, wi.work_item_id, wi.title)

    def print_steps_for_testcase(self, case_id):
        tc = TestCase(self.project, case_id)
        steps = tc.get_test_steps()
      
        for step in steps.steps:
            stp = step.values[0].content
            exp = step.values[1].content
            print "TestStep       = %s" % stp
            print "ExpectedResult = %s\n" % exp

    def print_links_for_requirement(self, req_id):
        req = Requirement(self.project, req_id)
        print "ID%-12sRole" % ('')
        print "-------%7s------" % ('')

        for linked in req.linked_work_items_derived:
            print "%-13s %-13s" % (linked.work_item_id,
                                   linked.role)

    def print_links_for_testcase(self, case_id):
        tc = TestCase(self.project, case_id)
        print "ID%-12sRole" % ('')
        print "-------%7s------" % ('')

        for linked in tc.linked_work_items:
            print "%-13s %-13s" % (linked.work_item_id,
                                   linked.role)

    def print_runs_by_query(self, query, is_template=False):
        query_ful = "project.id:%s AND %s" %(self.project, query)
        fields = ["query",
                  "created",
                  "test_run_id",
                  "select_test_cases_by",
                  "status",
                  "plannedin",
                  "assignee",
                  "author"]
        st =TestRun.search(query_ful,
                           fields,
                           "created",
                           -1,
                           is_template)
        Object = "Run"
        if is_template == True:
            Object = "Template"

        prestr = "Created Time %8sAuthor %3sAssignee" % ('', '')
        latstr = "%sStatus %3sPlanID%10s%s" % ('', '', '', Object)
        preln = "------------%9s------%4s------" % ('', '')
        latln = "%2s--------%2s-------%9s--------" % ('', '', '')

        print "%s %s" % (prestr, latstr)
        print "%s %s" % (preln, latln)

        for tp in st:
            created_time = str(tp.created).split(".")[0]
            print "%-20s %-9s %-8s %-10s%-15s %s" % (created_time,
                                                     tp.author,
                                                     tp.assignee,
                                                     tp.status,
                                                     tp.plannedin,
                                                     tp.test_run_id)
 
class CmdUpdate(object):

    def __init__(self, project, space, user):
        self.project = project
        self.space = space

    def update_all_results_for_run(self):

        pass

    def update_result_for_run(self):

        pass

    def update_plannedin_for_run(self):

        pass

    def update_plannedin_for_runs(self):
    
        pass

    def update_assignee_for_run(self):
        pass

    def update_assignee_for_runs(self):
        pass

    def update_status_for_run(self):
        pass


class CmdCreate(object):

    def __init__(self, project, space, user):
        self.project = project
        self.space = space

    def create_run_from_template(self, run, template):
        pass

    def create_runs_from_template(self, runlist, template):
        '''TODO'''
        pass


# CmdList().list_all_documents_under_space('RedHatEnterpriseLinux7','KernelStorageQE')
#wis = CmdList('RedHatEnterpriseLinux7','KernelStorageQE').list_workitems_from_document('KernelStorageQE/KS FCoE Requirement Specification')
#print CmdList('RedHatEnterpriseLinux7','KernelStorageQE').print_workitems(wis)
