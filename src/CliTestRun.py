'''
Created on Dec 04, 2015

@author: xhe@redhat.com
'''

import datetime
from pylarion.test_run import TestRun
from pylarion.plan import Plan


class CliTestRun:
    '''An object to manage the general commands

    Attributes:
        project_id: string (e.g. RedHatEnterpriseLinux7 or RHEL6)
    '''
    def __init__(self, default_project):
        """CliTestRun constructor.

        Args:
            default_project: the project where the module is located
        """

        self.project_id = default_project

    def get_input(self, description):
        '''Get input and format input

        Args:
            description: the string you want to display

        Returns:
            raw_input
        '''

        return raw_input("%s:" % description)

    def list_runs(self, is_template, query):
        '''Get input and format input

        Args:
            is_template (bool): True is template, False is run
            query: the Polarion query used to find test runs

        Returns:
            None
        '''
        query_ful = "project.id:%s AND %s" % (self.project_id, query)
        fields = ["query", "created", "test_run_id", "select_test_cases_by",
                  "status", "plannedin", "assignee", "author"]

        st = TestRun.search(query_ful, fields, "created", -1, is_template)

        Object = "Run"
        if is_template is True:
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

    def list_cases_from_run(self, project_id, test_run_id):
        '''list test cases from one run
        Args:
            project_id (string): project to create module in
            test_run_id (string): the unique identifier for the test run

        Returns:
            None
        '''

        tr = TestRun(test_run_id, None, self.project_id)
        print("List cases for: %s\n" % test_run_id)
        ttstr = ("Created Time %8sStatus %1sExecutedBy %2sCaseID" % ('',
                                                                     '',
                                                                     ''))
        lnstr = ("------------%9s------%2s----------%3s------" % ('', '', ''))
        print ttstr
        print lnstr
        for rec in tr.records:
            time = str(rec.executed).split(".")[0]
            print("%-21s%-9s%-12s%s" % (time, rec.result,
                                        rec.executed_by, rec.test_case_id))

    def list_plannedin(self, test_run_id):
        '''list plannedin from one run properties
        Args:
            test_run_id (string): the unique identifier for the test run

        Returns:
            None
        '''

        tr = TestRun(test_run_id, None, self.project_id)
        print "%-30s Planned In: %s" % (test_run_id, tr.plannedin)

    def list_assignee(self, test_run_id):
        '''list assignee from one run properties
        Args:
            test_run_id (string): the unique identifier for the test run

        Returns:
            None
        '''
        tr = TestRun(test_run_id, None, self.project_id)
        print("%-30s Assignee: %s" % (test_run_id, tr.assignee))

    def create_run(self, project_id, test_run_id, template=None,
                   plan_id=None, ass=None):
        '''list assignee from one run properties

        Args:
            project_id (str): project to create module in
            test_run_id (str): the unique identifier for the test run
            template (str): the id of the template to base the test run on
            plan_id (str): the planned_in filed value
            ass (str): the person of assignee to add

        Returns:
            TestRun
        '''
        tr = TestRun.create(project_id, test_run_id, template,
                            plannedin=plan_id, assignee=ass)
        print("Create Test Run : %s\nDone!" % test_run_id)
        return tr

    def set_all_result(self, user, test_run_id, result, comment=None):
        '''set all result

        Args:
            user (str): the person who execute the run
            test_run_id (str): the unique identifier for the test run
            result (str): the test case result in run, it can be set to
                          pass/fail/block
            comment: the test case result verdict in run

        Returns:
            None
        '''
        print "In process ..."
        tr = TestRun(test_run_id, None, self.project_id)

        print "Total records: %d" % len(tr.records)
        print "Updated Date Time    Result  CaseID"
        print "-------------------  ------  -----------"

        for rec in tr.records:
            rec.executed = datetime.datetime.now()
            rec.executed_by = user
            executed_str = str(rec.executed).split('.')[0]
            rec.result = result
            rec.comment = comment
            print "%-20s %-7s %s" % (executed_str, result, rec.test_case_id)
            tr.update_test_record_by_object(rec.test_case_id, rec)

        print "All results of %s is set to \"%s\" by %s\
            \nDone!" % (test_run_id, result, user)

    def set_one_result(self, user, test_run_id, test_case_id,
                       result, command=None):
        '''set result for specified test case in run

        Args:
            user (str): the person who execute the run
            test_run_id (str): the unique identifier for the test run
            test_case_id (str): the test case ID
            result (str): the test case result in run, it can be set to
                          pass/fail/block
            comment: the test case result verdict in run

        Returns:
            None
        '''
        tr = TestRun(test_run_id, None, self.project_id)

        for rec in tr.records:
            rec.executed = datetime.datetime.now()
            rec.executed_by = user
            rec.result = result
            rec.command = command
            if rec.test_case_id == test_case_id:
                print "%s is updating %s case result..." % (user, test_run_id)
                tr.update_test_record_by_object(rec.test_case_id, rec)
        print "%s is updated to \"%s\" Done!" % (test_case_id, result)

    def set_status(self, test_run_id, status):
        '''set status for run

        Args:
            test_run_id (str): the unique identifier for the test run
            status: the status of run

        Returns:
            None
        '''

        tr = TestRun(test_run_id, None, self.project_id)
        print "Current %s : %s" % (test_run_id, tr.status)
        tr.status = status
        tr.update()
        print "Updated %s : %s" % (test_run_id, status)

    def get_plans(self, query):
        '''get plan ids by query

        Args:
            query: the Polarion query used to find plans

        Returns:
            None
        '''
        pls = Plan.search(query, sort="due_date", limit=-1,
                          fields=['due_date', 'name', 'plan_id'])
        ttstr = ("Due Date%-5sPlan ID%-24sPlan Name" % ('', ''))
        lnstr = ("-----------  ---------- %-20s---------" % '')
        print ttstr
        print lnstr
        for pl in pls:
            print "%-12s %-30s %s" % (pl.due_date, pl.plan_id, pl.name)

    def set_plannedin(self, test_run_ids, plan_id, assignee):
        '''set plannedin for the specified run

        Args:
            test_run_id (str): the unique identifier for the test run
            plan_id (str): the plan id
            assignee: the person who will execute the test run

        Returns:
            None
        '''
        for test_run_id in test_run_ids.split(','):
            tr = TestRun(test_run_id, None, self.project_id)
            tr.plannedin = plan_id
            tr.assignee = assignee
            print "%-30s -> Planned In: %s" % (test_run_id, plan_id)
            print "%-30s -> Assignee: %s" % (test_run_id, tr.assignee)
            tr.update()
        print("Done!")

    def set_assignee(self, test_run_ids, assignee):
        '''set assignee for the specified run

        Args:
            test_run_id (str): the unique identifier for the test run
            assignee: the person who will execute the test run

        Returns:
            None
        '''
        for test_run_id in test_run_ids.split(','):
            tr = TestRun(test_run_id, None, self.project_id)
            if not tr.plannedin:
                print "Exit - Please ensure the PlannedIn is set\
                    when you set Assignee"
                print "Please set '-n' firstly OR set both '-n'\
                    and '-a' together"
                exit(0)
            else:
                tr.assignee = assignee
                print "%-30s -> Assignee: %s" % (test_run_id, assignee)
                tr.update()
                print("Done!")
