#!/usr/bin/env python3

import rclpy
from enum import Enum
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class SwarmState(str, Enum):
    IDLE = 'IDLE'
    FORMATION = 'FORMATION'
    DETACHING = 'DETACHING'
    RECONFIGURING = 'RECONFIGURING'
    WAITING = 'WAITING'


class StateManagerNode(Node):
    def __init__(self):
        super().__init__('state_manager_node')

        self.declare_parameter('uav_ids', ['uav1', 'uav2', 'uav3'])
        self.declare_parameter('detach_target', '')
        self.declare_parameter('formation_name', 'triangle')
        self.declare_parameter('use_qr_trigger', True)
        self.declare_parameter('qr_detach_keyword', 'detach')
        self.declare_parameter('manual_detach_cmd', 'detach')
        self.declare_parameter('manual_form_cmd', 'form_formation')
        self.declare_parameter('state_publish_period', 0.5)
        self.declare_parameter('reconfig_delay', 2.0)
        self.declare_parameter('log_transitions', True)
        self.declare_parameter('topic_qr', '/qr_decoded')
        self.declare_parameter('topic_manual', '/manual_command')
        self.declare_parameter('topic_status', '/uav_status')
        self.declare_parameter('topic_state', '/swarm/state_change')
        self.declare_parameter('topic_detach', '/swarm/detach_command')
        self.declare_parameter('topic_formation', '/swarm/formation_command')

        self.uav_ids = list(self.get_parameter('uav_ids').value)
        self.detach_target = self.get_parameter('detach_target').value
        if not self.detach_target and self.uav_ids:
            self.detach_target = self.uav_ids[1] if len(self.uav_ids) > 1 else self.uav_ids[0]

        self.formation_name = self.get_parameter('formation_name').value
        self.use_qr_trigger = self.get_parameter('use_qr_trigger').value
        self.qr_detach_keyword = self.get_parameter('qr_detach_keyword').value
        self.manual_detach_cmd = self.get_parameter('manual_detach_cmd').value
        self.manual_form_cmd = self.get_parameter('manual_form_cmd').value
        self.state_publish_period = float(self.get_parameter('state_publish_period').value)
        self.reconfig_delay = float(self.get_parameter('reconfig_delay').value)
        self.log_transitions = self.get_parameter('log_transitions').value

        self.topic_qr = self.get_parameter('topic_qr').value
        self.topic_manual = self.get_parameter('topic_manual').value
        self.topic_status = self.get_parameter('topic_status').value
        self.topic_state = self.get_parameter('topic_state').value
        self.topic_detach = self.get_parameter('topic_detach').value
        self.topic_formation = self.get_parameter('topic_formation').value

        self.state = SwarmState.IDLE
        self.reconfig_timer = None

        self.create_subscription(String, self.topic_qr, self.qr_callback, 10)
        self.create_subscription(String, self.topic_manual, self.manual_callback, 10)
        self.create_subscription(String, self.topic_status, self.status_callback, 10)
        self.state_pub = self.create_publisher(String, self.topic_state, 10)
        self.detach_pub = self.create_publisher(String, self.topic_detach, 10)
        self.formation_pub = self.create_publisher(String, self.topic_formation, 10)

        self.create_service(Trigger, '/swarm/request_detach', self.handle_detach_request)
        self.state_timer = self.create_timer(self.state_publish_period, self.publish_state)

        self.publish_state()
        self.get_logger().info('State manager ready (target: %s).', self.detach_target)

    def publish_state(self):
        self.state_pub.publish(String(data=self.state.value))

    def transition_to(self, new_state: SwarmState, reason: str):
        if self.state == new_state:
            return
        if self.log_transitions:
            self.get_logger().info('State %s -> %s (%s)', self.state.value, new_state.value, reason)
        self.state = new_state
        self.publish_state()

        if new_state == SwarmState.DETACHING:
            self.publish_detach_command()
        elif new_state == SwarmState.RECONFIGURING:
            self.start_reconfig_timer()
            self.publish_formation_command()
        elif new_state == SwarmState.FORMATION:
            self.publish_formation_command()

    def publish_detach_command(self):
        if not self.detach_target:
            self.get_logger().warn('Detach requested but no detach_target configured.')
            return
        self.detach_pub.publish(String(data=self.detach_target))

    def publish_formation_command(self):
        self.formation_pub.publish(String(data=self.formation_name))

    def start_reconfig_timer(self):
        if self.reconfig_timer is not None:
            self.reconfig_timer.cancel()
        self.reconfig_timer = self.create_timer(self.reconfig_delay, self.finish_reconfigure)

    def finish_reconfigure(self):
        if self.reconfig_timer is not None:
            self.reconfig_timer.cancel()
            self.reconfig_timer = None
        self.transition_to(SwarmState.FORMATION, 'reconfig complete')

    def qr_callback(self, msg):
        if not self.use_qr_trigger:
            return
        if self.qr_detach_keyword in msg.data:
            self.transition_to(SwarmState.DETACHING, 'qr trigger')

    def manual_callback(self, msg):
        if msg.data == self.manual_detach_cmd:
            self.transition_to(SwarmState.DETACHING, 'manual command')
        elif msg.data == self.manual_form_cmd:
            self.transition_to(SwarmState.FORMATION, 'manual command')

    def status_callback(self, msg):
        if self.state != SwarmState.DETACHING:
            return
        status = msg.data.lower()
        if 'detached' in status and self.detach_target.lower() in status:
            self.transition_to(SwarmState.RECONFIGURING, 'detach confirmed')

    def handle_detach_request(self, request, response):
        self.transition_to(SwarmState.DETACHING, 'service request')
        response.success = True
        response.message = f'detach command sent to {self.detach_target}'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = StateManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
