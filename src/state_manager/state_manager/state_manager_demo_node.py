#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class DetachScenarioPublisher(Node):
    def __init__(self):
        super().__init__('state_manager_demo_node')

        self.declare_parameter('topic_qr', '/qr_decoded')
        self.declare_parameter('topic_manual', '/manual_command')
        self.declare_parameter('topic_status', '/uav_status')
        self.declare_parameter('manual_detach_cmd', 'detach')
        self.declare_parameter('manual_form_cmd', 'form_formation')
        self.declare_parameter('qr_detach_keyword', 'detach')
        self.declare_parameter('detach_target', 'uav2')
        self.declare_parameter('trigger_mode', 'manual')
        self.declare_parameter('start_delay', 2.0)
        self.declare_parameter('detach_confirm_delay', 4.0)
        self.declare_parameter('form_delay', 6.0)

        self.topic_qr = self.get_parameter('topic_qr').value
        self.topic_manual = self.get_parameter('topic_manual').value
        self.topic_status = self.get_parameter('topic_status').value
        self.manual_detach_cmd = self.get_parameter('manual_detach_cmd').value
        self.manual_form_cmd = self.get_parameter('manual_form_cmd').value
        self.qr_detach_keyword = self.get_parameter('qr_detach_keyword').value
        self.detach_target = self.get_parameter('detach_target').value
        self.trigger_mode = self.get_parameter('trigger_mode').value
        self.start_delay = float(self.get_parameter('start_delay').value)
        self.detach_confirm_delay = float(self.get_parameter('detach_confirm_delay').value)
        self.form_delay = float(self.get_parameter('form_delay').value)

        self.manual_pub = self.create_publisher(String, self.topic_manual, 10)
        self.qr_pub = self.create_publisher(String, self.topic_qr, 10)
        self.status_pub = self.create_publisher(String, self.topic_status, 10)
        self.detach_client = self.create_client(Trigger, '/swarm/request_detach')

        self.start_time = self.get_clock().now()
        self.step = 0
        self.timer = self.create_timer(0.2, self.tick)

    def tick(self):
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        if self.step == 0 and elapsed >= self.start_delay:
            self.trigger_detach()
            self.step = 1
        elif self.step == 1 and elapsed >= self.detach_confirm_delay:
            self.publish_detached_status()
            self.step = 2
        elif self.step == 2 and elapsed >= self.form_delay:
            self.publish_form_command()
            self.step = 3

    def trigger_detach(self):
        if self.trigger_mode == 'qr':
            self.qr_pub.publish(String(data=self.qr_detach_keyword))
            self.get_logger().info('Sent QR detach trigger: %s', self.qr_detach_keyword)
        elif self.trigger_mode == 'service':
            if not self.detach_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().warn('Detach service not available, falling back to manual command.')
                self.manual_pub.publish(String(data=self.manual_detach_cmd))
                return
            request = Trigger.Request()
            future = self.detach_client.call_async(request)
            future.add_done_callback(self.handle_detach_response)
        else:
            self.manual_pub.publish(String(data=self.manual_detach_cmd))
            self.get_logger().info('Sent manual detach command: %s', self.manual_detach_cmd)

    def handle_detach_response(self, future):
        try:
            response = future.result()
            self.get_logger().info('Detach service response: %s', response.message)
        except Exception as exc:
            self.get_logger().warn('Detach service call failed: %s', exc)

    def publish_detached_status(self):
        status = f'detached:{self.detach_target}'
        self.status_pub.publish(String(data=status))
        self.get_logger().info('Published status: %s', status)

    def publish_form_command(self):
        self.manual_pub.publish(String(data=self.manual_form_cmd))
        self.get_logger().info('Sent manual formation command: %s', self.manual_form_cmd)


def main(args=None):
    rclpy.init(args=args)
    node = DetachScenarioPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
