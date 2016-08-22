# -*- coding: utf8 -*-
import datetime
import ConfigParser
from pylarion.document import Document
from pylarion.work_item import TestCase
from pylarion.work_item import Requirement
from pylarion.test_run import TestRun
from pylarion.plan import Plan


class Repo(object):
    '''Attributes includes the all options of command line'''
    def __init__(self,
                 assignee=None,
                 comment=None,
                 document=None,
                 query=None,
                 debug=None,
                 is_document=None,
                 testcase=None,
                 links=None,
                 template=None,
                 plannedin=None,
                 result=None,
                 plan_ids=None,
                 requirement=None,
                 run=None,
                 steps=None,
                 workitem=None,
                 status=None):
        self.assignee = assignee
        self.comment = comment
        self.document = document
        self.query = query
        self.debug = debug
        self.is_document = is_document
        self.testcase = testcase
        self.links = links
        self.template = template
        self.plannedin = plannedin
        self.result = result
        self.plan_ids = plan_ids
        self.requirement = requirement
        self.run = run
        self.steps = steps
        self.workitem = workitem
        self.status = status


class Config(object):
    '''Attributes includes the usesful parameters in config'''
    def __init__(self,
                 space=None,
                 plannedin=None,
                 assignee=None):
        self.conf_space = space
        self.conf_plannedin = plannedin

    def getconf(self, confile):
        condict = {}
        cfile = ConfigParser.SafeConfigParser()

        cfile.read(confile)
        condict['con_space'] = cfile.get('cmd', 'space')
        condict['con_plannedin'] = cfile.get('cmd', 'plannedin')
        condict['assignee'] = cfile.get('cmd', 'assignee')
        condict['output'] = cfile.get('cmd', 'output')
        return condict


class CmdList(object):
    ''' An object to manage the command of update

    Attributes:
        space (string)
    '''

    def __init__(self, space=None):
        ''' constructor for the Module object. Provide the methods of
            command update based on parameters passed in.

        Args:
            space: specific space of the repository

        Returns:
            None
        '''

        self.space = space

    def list_all_documents_under_space(self, fields=None):
        fields = ['document_id',
                  'document_name',
                  'author',
                  'created',
                  'updated',
                  'updated_by']
        doc_list = Document.get_documents(Document.default_project,
                                          self.space,
                                          fields)
        return doc_list

    def list_documents_by_query(self,
                                query,
                                is_sql=False,
                                fields=None):
        fields = ['document_id',
                  'document_name',
                  'author',
                  'created',
                  'updated',
                  'updated_by']
        doc_list = Document.query(query, is_sql, fields)

        return doc_list

    def print_documents(self, docs, fields):
        print 'Created%7sAuthor%7sDocument' % ('', '')
        print '-------%7s------%7s--------' % ('', '')

        for doc in docs:
            print '%-14s %-11s %s' % (doc.created.strftime('%Y-%m-%d'),
                                      doc.author,
                                      doc.document_id)

    def list_workitems_in_doc(self, doc_name_with_space):
        doc = Document(Document.default_project, doc_name_with_space)
        fields = ['work_item_id',
                  'author',
                  'title',
                  'type',
                  'status',
                  'assignee',
                  'categories',
                  'comments',
                  'created',
                  'approvals',
                  'updated']
        self.workitem_list = doc.get_work_items(None, True, fields)
        return self.workitem_list

    def print_workitems(self, workitems):
        print 'Type%10sID%12sDescription' % ('', '')
        print '-------%7s-----%9s--------' % ('', '')

        for wi in workitems:
            print '%-13s %-13s %s' % (wi.type, wi.work_item_id, wi.title)

    def print_steps_for_testcase(self, case_id):
        tc = TestCase(TestCase.default_project, case_id)
        steps = tc.get_test_steps()

        for step in steps.steps:
            stp = step.values[0].content
            exp = step.values[1].content
            print 'TestStep       = %s' % stp
            print 'ExpectedResult = %s\n' % exp

        if steps.steps is None:
            print 'No step for this tesecase!'

    def print_links_for_requirement(self, req_id):
        req = Requirement(Requirement.default_project, req_id)
        print 'ID%-12sRole' % ('')
        print '-------%7s------' % ('')

        for linked in req.linked_work_items_derived:
            print '%-13s %-13s' % (linked.work_item_id,
                                   linked.role)

    def print_links_for_testcase(self, case_id):
        tc = TestCase(TestCase.default_project, case_id)
        print 'ID%-12sRole' % ('')
        print '-------%7s------' % ('')

        for linked in tc.linked_work_items:
            print '%-13s %-13s' % (linked.work_item_id,
                                   linked.role)

    def print_runs_by_query(self, query, is_template=False):
        query_ful = 'project.id:%s AND %s' % (TestRun.default_project, query)
        fields = ['query',
                  'created',
                  'test_run_id',
                  'select_test_cases_by',
                  'status',
                  'plannedin',
                  'assignee',
                  'author']

        st = TestRun.search(query_ful,
                            fields,
                            'created',
                            -1,
                            is_template)
        Object = ''
        if is_template:
            Object = 'Template'

        prestr = 'Created Time %8sAuthor %3sAssignee' % ('', '')
        latstr = '%sStatus %3sPlanID%10s%s' % ('', '', '', Object)
        preln = '------------%9s------%4s------' % ('', '')
        latln = '%2s--------%2s-------%9s--------' % ('', '', '')

        print '%s %s' % (prestr, latstr)
        print '%s %s' % (preln, latln)

        for tp in st:
            created_time = str(tp.created).split('.')[0]
            print '%-20s %-9s %-8s %-10s%-15s %s' % (created_time,
                                                     tp.author,
                                                     tp.assignee,
                                                     tp.status,
                                                     tp.plannedin,
                                                     tp.test_run_id)

    def print_templates_by_query(self, query):
        self.print_runs_by_query(query, True)

    def print_testcases_from_run(self, run):
        tr = TestRun(run, None, TestRun.default_project)
        print '(Only CaseID can be displayed when --run=$template)'
        print('List cases for: %s\n' % run)
        ttstr = ('Created Time %8sStatus %1sExecutedBy %2sCaseID' % ('',
                                                                     '',
                                                                     ''))
        lnstr = ('------------%9s------%2s----------%3s------' % ('', '', ''))
        print ttstr
        print lnstr

        for rec in tr.records:
            time = str(rec.executed).split('.')[0]
            print('%-21s%-9s%-12s%-10s' % (time,
                                           rec.result,
                                           rec.executed_by,
                                           rec.test_case_id))

    def print_plan_ids(self, query):
        pls = Plan.search(query,
                          sort='due_date',
                          limit=-1,
                          fields=['due_date',
                                  'name',
                                  'plan_id'])

        ttstr = ('Due Date%-5sPlan ID%-24sPlan Name' % ('', ''))
        lnstr = ('-----------  ---------- %-20s---------' % '')
        print ttstr
        print lnstr

        for pl in pls:
            print '%-12s %-30s %s' % (pl.due_date, pl.plan_id, pl.name)


class CmdUpdate(object):
    ''' An object to manage the command of update

    Attributes:
        None
    '''

    def __init__(self):
        ''' constructor for the Module object. Provide the methods of
            command update based on parameters passed in.

        Args:
            None

        Returns:
            None
        '''

    def update_all_results_for_run(self, run, result, user, comment):

        tr = TestRun(run.strip(), None, TestRun.default_project)
        print 'Update %s:' % run.strip()

        if not comment:
            comment = ''

        print 'Total records: %d' % len(tr.records)
        print 'Updated Date Time    Result  CaseID'
        print '-------------------  ------  -----------'

        if user == 'None':
            user = TestRun.logged_in_user_id

        for rec in tr.records:
            rec.executed = datetime.datetime.now()
            rec.executed_by = user
            executed_str = str(rec.executed).split('.')[0]
            rec.result = result
            rec.comment = comment

            print '%-20s %-7s %s' % (executed_str,
                                     result,
                                     rec.test_case_id)
            tr.update_test_record_by_object(rec.test_case_id,
                                            rec)
        print 'Done!'

    def update_all_results_for_runs(self, runs, result, user, comment):
        if runs.find(','):
            for run in runs.split(','):
                self.update_all_results_for_run(run, result, user, comment)
        else:
            print 'Please use comma \',\' to seperate your runs!'

    def update_1_result_for_run(self,
                                run,
                                testcase,
                                result,
                                user,
                                comment):

        if not comment:
            comment = ''

        tr = TestRun(run.strip(), None, TestRun.default_project)
        print 'Update %s:' % run

        if user == 'None':
            user = TestRun.logged_in_user_id

        for rec in tr.records:
            rec.executed = datetime.datetime.now()
            rec.executed_by = user
            rec.result = result
            rec.comment = comment

            if rec.test_case_id == testcase:
                tr.update_test_record_by_object(testcase, rec)
                print '%4sSet %s to %s (verdict %s)' % ('',
                                                        testcase,
                                                        result,
                                                        comment)
        print 'Done!'

    def update_1_result_for_runs(self,
                                 runs,
                                 testcase,
                                 result,
                                 user,
                                 comment):

        if runs.find(','):
            for run in runs.split(','):
                self.update_1_result_for_run(run,
                                             testcase,
                                             result,
                                             user,
                                             comment)
        else:
            print 'Please use comma \',\' to seperate your runs!'

    def update_status_for_run(self,
                              run,
                              status):

        tr = TestRun(run.strip(), None, TestRun.default_project)
        tr.status = status
        tr.update()
        print 'Updated %s status -> %s' % (run, status)

    def update_status_for_runs(self,
                               runs,
                               status):

        if runs.find(','):
            for run in runs.split(','):
                self.update_status_for_run(run, status)
        else:
            print 'Please use comma \',\' to seperate your runs!'

    def update_run(self,
                   run,
                   template=None,
                   plannedin=None,
                   assignee=None,
                   is_template=False):

        qrun = run.replace('-', '\-')
        query_ful = 'project.id:%s AND id:%s' % (TestRun.default_project,
                                                 qrun.strip())

        fields = ['query',
                  'created',
                  'test_run_id',
                  'select_test_cases_by',
                  'status',
                  'plannedin',
                  'assignee',
                  'author']
        st = TestRun.search(query_ful,
                            fields,
                            'created',
                            -1,
                            is_template)

        # Update run if exists, otherwise create it.
        if st:
            print 'Update the existing run: %s' % run
            tr = TestRun(run.strip(),
                         None,
                         TestRun.default_project)
        else:
            tr = TestRun.create(TestRun.default_project,
                                run.strip(),
                                template)
            print '\nCreated %s:' % run

        # set customer filed of plannedin
        if plannedin:
            tr.plannedin = plannedin
            print '%4sSet Plannedin to %s' % ('', plannedin)

        if assignee == 'None':
            tr.assignee = TestRun.logged_in_user_id
        else:
            tr.assignee = assignee

        print '%4sSet Assignee to %s' % ('', tr.assignee)
        tr.update()

    def update_runs(self,
                    runs,
                    template=None,
                    plannedin=None,
                    assignee=None):

        if runs.find(','):
            for run in runs.split(','):
                self.update_run(run,
                                template,
                                plannedin,
                                assignee)
            print 'Done!'
        else:
            print 'Please use comma \',\' to seperate your runs!'
