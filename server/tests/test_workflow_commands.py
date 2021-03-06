from server.models import WfModule, ModuleVersion, ReorderModulesCommand, \
        ChangeWorkflowTitleCommand
from django.test import TestCase
from server.tests.utils import DbTestCase, create_testdata_workflow, \
        add_new_wf_module


class ReorderModulesCommandTests(DbTestCase):
    def setUp(self):
        # Create a workflow with two modules
        self.workflow = create_testdata_workflow()
        # defined by create_testdata_workflow
        self.module_version = ModuleVersion.objects.first()
        self.module1 = WfModule.objects.first()
        self.module2 = add_new_wf_module(self.workflow, self.module_version,
                                         order=1)

    def assertWfModuleVersions(self, expected_versions):
        result = list(
            self.workflow.wf_modules.values_list('last_relevant_delta_id',
                                                 flat=True)
        )
        self.assertEqual(result, expected_versions)

    # Switch module orders, then undo, redo
    def test_reorder_modules(self):
        v0 = self.workflow.revision()

        # Switch module orders. Note that objects in this array are not in
        # order; we're testing that
        new_order = [
            {'id': self.module1.id, 'order': 1},
            {'id': self.module2.id, 'order': 0},
        ]
        cmd = ReorderModulesCommand.create(self.workflow, new_order)
        self.assertEqual(WfModule.objects.count(), 2)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.assertEqual(self.module2.order, 0)
        self.assertEqual(self.module1.order, 1)

        # workflow revision should have been incremented
        self.workflow.refresh_from_db()
        v1 = self.workflow.revision()
        self.assertGreater(v1, v0)
        self.assertWfModuleVersions([v1, v1])

        # undo
        cmd.backward()
        self.assertEqual(WfModule.objects.count(), 2)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.assertEqual(self.module1.order, 0)
        self.assertEqual(self.module2.order, 1)
        self.assertWfModuleVersions([v0, v0])

        # redo
        cmd.forward()
        self.assertEqual(WfModule.objects.count(), 2)
        self.module1.refresh_from_db()
        self.module2.refresh_from_db()
        self.assertEqual(self.module2.order, 0)
        self.assertEqual(self.module1.order, 1)
        self.assertWfModuleVersions([v1, v1])


    # Check error checking
    def test_invalid_input(self):
        total_crap = { 'problem': 'this isn\'t even an array' }
        bad_id = [ { 'id': 999, 'order': 0 }, { 'id': self.module2.id, 'order': 1 } ]
        bad_order = [ { 'id': self.module1.id, 'order': 5 }, { 'id': self.module2.id, 'order': 6 } ]
        missing_id = [{'order': 0 }, {'id': self.module2.id, 'order': 1}]
        missing_order = [{'id': self.module1.id}, {'id': self.module2.id, 'order': 1}]

        with self.assertRaises(ValueError):
            ReorderModulesCommand.create(self.workflow, total_crap)

        with self.assertRaises(ValueError):
            ReorderModulesCommand.create(self.workflow, bad_id)

        with self.assertRaises(ValueError):
            ReorderModulesCommand.create(self.workflow, bad_order)

        with self.assertRaises(ValueError):
            ReorderModulesCommand.create(self.workflow, missing_id)

        with self.assertRaises(ValueError):
            ReorderModulesCommand.create(self.workflow, missing_order)


class ChangeWorkflowTitleCommandTests(TestCase):
    def setUp(self):
        self.workflow = create_testdata_workflow()

    # Change notes, then undo/redo
    def test_change_title(self):
        firstTitle = 'title1'
        secondTitle = 'title2'

        self.workflow.name = firstTitle

        # Change back to second title, see if it saved
        cmd = ChangeWorkflowTitleCommand.create(self.workflow, secondTitle)
        self.assertEqual(self.workflow.name, secondTitle)

        # undo
        cmd.backward()
        self.assertEqual(self.workflow.name, firstTitle)

        # redo
        cmd.forward()
        self.assertEqual(self.workflow.name, secondTitle)
