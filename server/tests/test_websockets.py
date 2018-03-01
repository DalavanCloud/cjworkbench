# Tests for our websockets (Channels) handling
# Pretty minimal rn, just tests that we can open a connection to a workflow

from channels.testing import WebsocketCommunicator
from server.websockets import *
from server.tests.utils import *
import asynctest


# This is just here to make PyCharm understand that this file should be run within the standard UnitTest framework
class FakeTasts(TestCase):
    pass

class ChannelTests(asynctest.TestCase):
    def setUp(self):
#        super(ChannelTests, self).setUp() # log in
        self.workflow = add_new_workflow('Workflow 1')
        self.wf_id = self.workflow.id
        self.module = add_new_module_version('Module')
        self.wf_module = add_new_wf_module(self.workflow, self.module)

    async def test_websockets(self):
        wf_path = '/workflow/' + str(self.wf_id)

        communicator = WebsocketCommunicator(WebsocketsHandler, wf_path)
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # client = HttpClient()
        #
        # # cannot connect to an invalid workflow ID
        # with self.assertRaises(AssertionError):
        #     client.send_and_consume('websocket.connect', path='/workflow/999999')
        # self.assertIsNone(client.receive())
        #
        # # can connect to valid workflow ID
        # client.send_and_consume('websocket.connect', path=wf_path)
        # self.assertIsNone(client.receive())
        #
        # # send message
        # ws_send_workflow_update(self.workflow, {'foo':42})
        # self.assertEqual(client.receive(), {'foo' : 42})
        #
        # # add another client to same workflow, test receive
        # client2 = HttpClient()
        # client2.send_and_consume('websocket.connect', path=wf_path)
        # self.assertIsNone(client2.receive())
        #
        # ws_send_workflow_update(self.workflow, {'bar': 42})
        # self.assertEqual(client.receive(), {'bar': 42})
        # self.assertEqual(client2.receive(), {'bar': 42})
        #
        # # remove client from workflow, test no longer receives
        # client2.send_and_consume('websocket.disconnect', path=wf_path)
        # self.assertIsNone(client2.receive())
        # ws_send_workflow_update(self.workflow, {'baz': 42})
        # self.assertEqual(client.receive(), {'baz': 42})
        # self.assertIsNone(client2.receive())
        #
        # # test that utility functions send the right messages
        # ws_client_rerender_workflow(self.workflow)
        # self.assertEqual(client.receive(), {'type':'reload-workflow'})
        #
        # ws_client_wf_module_status(self.wf_module, 'busy')
        # self.assertEqual(client.receive(), {'type':'wfmodule-status', 'id':self.wf_module.id, 'status':'busy'})
        #
